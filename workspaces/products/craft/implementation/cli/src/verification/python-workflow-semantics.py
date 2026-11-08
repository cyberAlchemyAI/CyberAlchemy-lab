"""Native Workflow replay against source-derived outcomes and deferred effects."""
import ast
import asyncio
import copy
import dataclasses
import hashlib
import importlib
import inspect
import json
import math
import pathlib
import types
from unittest.mock import patch


def require(ok, why):
    if not ok: raise ValueError('PYTHON_WORKFLOW_SEMANTICS:' + why)


def first_difference(observed, expected, location='$'):
    if observed == expected: return None
    if type(observed) is not type(expected):
        return location + ':type:' + type(observed).__name__ + '!=' + type(expected).__name__
    if isinstance(expected, dict):
        observed_keys, expected_keys = set(observed), set(expected)
        if observed_keys != expected_keys:
            return location + ':keys:' + repr(sorted(observed_keys - expected_keys)) + ':' + repr(sorted(expected_keys - observed_keys))
        for key in sorted(expected):
            difference = first_difference(observed[key], expected[key], location + '.' + key)
            if difference is not None: return difference
        return None
    if isinstance(expected, list):
        if len(observed) != len(expected): return location + ':length:' + str(len(observed)) + '!=' + str(len(expected))
        for index, value in enumerate(expected):
            difference = first_difference(observed[index], value, location + '[' + str(index) + ']')
            if difference is not None: return difference
        return None
    return location + ':value:' + repr(observed)[:256] + '!=' + repr(expected)[:256]


async def observe_case(call, case, row, Fact):
    runtime = operations.Runtime(row['recipes'])
    selected = json.loads(case['values'][0])
    input = runtime.build({'tag': 'ref', 'value': str(selected['input'])})
    rows = [{**s, 'operation_ref': row['workflow']['steps'][i]['operation_ref'],
             'reads': [{**r, 'value': runtime.build({'tag': 'ref', 'value': str(r['value'])})} for r in s['reads']]}
            for i, s in enumerate(selected['steps'])]
    input_ids = set()
    def collect(v):
        if not isinstance(v, (dict, list)) and type(v) is not tuple: return
        if id(v) in input_ids: return
        input_ids.add(id(v))
        values = dict.values(v) if isinstance(v, dict) else list.__iter__(v) if isinstance(v, list) else iter(v)
        for child in values: collect(child)
    collect(input)
    for s in rows:
        for r in s['reads']: collect(r['value'])
    def view(root):
        count, active = [0], set()
        def walk(v, depth=0):
            count[0] += 1
            require(count[0] <= 65536 and depth <= 128, 'output capacity')
            if v is None: return ['null']
            if type(v) is bool: return ['boolean', v]
            if type(v) is int: return ['bigint', str(v)]
            if type(v) is str: return ['string', v]
            if type(v) is float:
                require(math.isfinite(v), 'finite output'); return ['number', v]
            require(id(v) not in input_ids and id(v) not in active, 'detached acyclic output')
            active.add(id(v))
            try:
                if type(v) is tuple: return ['array', [walk(x, depth + 1) for x in v]]
                if type(v) is types.MappingProxyType: mapping = v
                elif type(v) is Fact:
                    require(owned.frozen(v) and type(v.entries) is tuple, 'frozen fact'); mapping = dict(v.entries)
                else:
                    require(owned.frozen(v), 'immutable outcome or batch')
                    mapping = {f.name: getattr(v, f.name) for f in dataclasses.fields(v)}
                require(all(type(k) is str for k in mapping), 'record keys')
                return ['record', [[k, walk(mapping[k], depth + 1)] for k in operations.keys(mapping)]]
            finally: active.remove(id(v))
        return walk(root)
    port_trace, batches, read_requests, clock_calls, pending = [], [], [], [], []
    active, position, overlapping_ports = {}, 0, False
    async def defer(row, phase, value=None, throws=False):
        nonlocal overlapping_ports
        overlapping_ports |= bool(pending)
        future = asyncio.get_running_loop().create_future()
        port_trace.append(row['step_id'] + ':' + phase)
        pending.append((row['step_id'], phase, future, value, throws))
        return await future
    def receipt(mode):
        if mode == 'receipt-empty': return {}
        if mode == 'receipt-unknown': return {'status': 'unknown'}
        if mode == 'receipt-extra': return {'status': 'committed', 'extra': True}
        if mode == 'receipt-null': return None
        if mode == 'receipt-undefined': return object()
        if mode == 'receipt-array': return ['committed']
        if mode == 'receipt-symbol': return {'status': 'committed', object(): True}
        if mode in ('receipt-getter', 'receipt-inherited', 'receipt-hidden'): return runtime.dict(status='committed')
        return {'status': mode if mode in ('rejected', 'indeterminate') else 'committed'}
    class Transaction:
        def __init__(self, row): self.row = row
        async def read(self, request):
            read_requests.append({'step_id': self.row['step_id'], 'value': view(request)})
            r = next((r for r in self.row['reads'] if r['slot'] == request['slot']), None)
            require(r is not None, 'undeclared read')
            return await defer(self.row, 'read:' + request['slot'], r['value'], r.get('throws', False))
        async def commit(self, batch):
            batches.append({'step_id': self.row['step_id'], 'value': view(batch)})
            return await defer(self.row, 'commit', receipt(self.row['mode']), self.row['mode'] == 'commit-throw')
        async def rollback(self): return await defer(self.row, 'rollback', None, self.row['mode'] == 'rollback-throw')
    class Store:
        def __init__(self, selector): self.selector = selector
        async def begin(self):
            nonlocal position
            require(position < len(rows), 'extra forward occurrence')
            row = rows[position]; position += 1
            require(row['operation_ref'] == self.selector, 'forward Operation order')
            active[self.selector] = row
            return await defer(row, 'begin', Transaction(row), row['mode'] == 'begin-throw')
    def clock(selector, slot):
        def tick():
            row = active[selector]; c = next(c for c in row['clocks'] if c['slot'] == slot)
            clock_calls.append(row['step_id'] + ':' + slot)
            if c.get('mode') == 'throw': raise RuntimeError('fixture-clock')
            return c['value']
        return tick
    dependencies = {}
    for row_ in rows:
        selector = row_['operation_ref']
        if selector not in dependencies:
            dependencies[selector] = {'store': Store(selector), 'clocks': {c['slot']: clock(selector, c['slot']) for c in row_['clocks'] if c.get('mode') != 'missing'}}
    ids = dict(selected['identity'])
    baseline = owned.fingerprint(input)
    read_baselines = [owned.fingerprint(r['value']) for s in rows for r in s['reads']]
    task = asyncio.create_task(call(input, ids, dependencies))
    await asyncio.sleep(0)
    synchronous_changed = baseline != owned.fingerprint(input)
    if selected['capture']:
        for key, value in input.items():
            input[key] = not value if type(value) is bool else value + '-changed' if type(value) is str else value + 1 if type(value) in (int, float) else None
        dependencies.clear(); ids['workflow_execution_id'] = 'changed-identity'
        baseline = owned.fingerprint(input)
    settled_while_pending = False
    try:
        for _ in range((len(rows) + 1) * 1024):
            for _ in range(8): await asyncio.sleep(0)
            if pending:
                step, phase, future, value, throws = pending.pop(0)
                settled_while_pending |= task.done()
                port_trace.append(step + ':' + phase + ('-rejected' if throws else '-resolved'))
                require(not future.done(), 'port already settled')
                if throws:
                    cancel = selected.get('cancel') == {'step_id': step, 'phase': 'read' if phase.startswith('read:') else phase}
                    future.set_exception(asyncio.CancelledError() if cancel else RuntimeError('fixture-' + phase))
                else: future.set_result(value)
                continue
            if task.done(): break
        require(task.done() and not pending, 'stalled Workflow')
        rejected, outcome = False, None
        try: outcome = await task
        except (Exception, asyncio.CancelledError): rejected = True
        return {'rejected': rejected, 'outcome': None if rejected else view(outcome), 'port_trace': port_trace,
                'batches': batches, 'read_requests': read_requests, 'clock_calls': clock_calls,
                'settled_while_pending': settled_while_pending, 'overlapping_ports': overlapping_ports,
                'getter_reads': len(runtime.touches), 'input_changed': synchronous_changed or baseline != owned.fingerprint(input),
                'read_changed': [owned.fingerprint(r['value']) for s in rows for r in s['reads']] != read_baselines}
    finally:
        if not task.done():
            task.cancel()
            for _, _, future, _, _ in pending:
                if not future.done(): future.cancel()
            try: await task
            except (Exception, asyncio.CancelledError): pass


def run(data, predecessor, observer, event_observer):
    controls, root = data['controls'], pathlib.Path(data['root'])
    selected = lambda r: r['state'] == 'ready' and r.get('adapter') == 'python-workflow'
    earlier = {**data, 'controls': {**controls, 'rows': [{**r, 'state': 'not_evaluable'} if selected(r) else r for r in controls['rows']]}}
    result = predecessor(earlier)
    by_selector = {r['selector']: r for r in result['rows']}
    async def execute():
        for row in controls['rows']:
            if not selected(row): continue
            m = row['module']
            payload = {'root': data['root'], 'workflow': row['workflow'], 'model': controls['data_model'], 'nodes': row['nodes'],
                       'rule_modules': controls['rule_modules'], 'event_modules': row['event_modules'],
                       'plan': {'modules': [m], 'selection': {'policy': row['policy']}, 'materialization': row['materialization'],
                                'operation_plan': {'modules': row['operation_modules'], 'selection': {'actions': row['actions']}, 'plan_sha256': row['operation_plan_sha256']}}}
            for event in row['event_modules']:
                event_observer({'root': data['root'], 'runtime': controls['runtime_dir'] + '/event_values.py',
                                'bodies': {event['selector']: row['nodes'][event['selector']]['body']}, 'nodes': row['nodes']}, event)
            observer(payload)
            native = importlib.import_module(m['import_name'])
            require(pathlib.Path(native.__file__).resolve() == (root / m['relative_path']).resolve(), 'Workflow module identity')
            call = getattr(native, m['callable'])
            require(owned.frozen(call) and facts.thaw(call.descriptor) == m['descriptor'], 'frozen bound Workflow')
            require(inspect.iscoroutinefunction(type(call).__call__) and list(inspect.signature(call).parameters) == ['parameters', 'execution_identity', 'dependencies'], 'native awaited call shape')
            Fact = importlib.import_module(controls['runtime_dir'].replace('/', '.') + '.facts')._Fact
            for case in row['cases']:
                expected = json.loads(case['expected']['value'])
                observed = facts.thaw(call.descriptor) if case['mode'] == 'workflow-descriptor' else await observe_case(call, case, row, Fact)
                require(observed == expected, 'outcome:' + row['selector'] + ':' + case['id'] + ':' + str(first_difference(observed, expected)))
            for name in ('__call__', 'descriptor', 'extra'):
                try: setattr(call, name, None)
                except (AttributeError, TypeError): pass
                else: raise ValueError('mutable Workflow binding')
            for mutation in ('orchestration', 'materialization'):
                file = m['provider_path'] if mutation == 'orchestration' else m['material_path']
                tree = ast.parse((root / file).read_bytes())
                target = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == ('execute' if mutation == 'orchestration' else 'result'))
                returns = [n for n in ast.walk(target) if isinstance(n, ast.Return)]
                require(bool(returns), 'native return required'); returns[-1].value = ast.Constant(None)
                ast.fix_missing_locations(tree); mutant = ast.unparse(tree).encode()
                compile(mutant, file, 'exec', dont_inherit=True)
                changed = copy.deepcopy(payload)
                if mutation == 'orchestration': changed['plan']['modules'][0]['descriptor']['provider_sha256'] = hashlib.sha256(mutant).hexdigest()
                # Material AST must reject before its trailing custody check.
                read_bytes = pathlib.Path.read_bytes
                def read(path): return mutant if path == root / file else read_bytes(path)
                with patch.object(pathlib.Path, 'read_bytes', read):
                    try: observer(changed)
                    except ValueError as error: require('AST' in str(error), 'nonsemantic substitution rejection:' + str(error))
                    else: raise ValueError('compiling Workflow substitution survived')
            by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                           'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2}
    if any(selected(r) for r in controls['rows']): asyncio.run(execute())
    require(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in result['toolchain_files'].items()), 'toolchain changed after Workflows')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
