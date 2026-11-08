"""Bounded native Operation replay using in-memory deferred transaction ports."""
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
    if not ok: raise ValueError('PYTHON_OPERATION_SEMANTICS:' + why)


class Runtime(facts.Runtime):
    def build(self, recipe):
        if recipe['tag'] == 'scalar' and recipe.get('format') == 'number':
            value = float(recipe['value'])
            return int(value) if math.isfinite(value) and value.is_integer() and abs(value) <= 9007199254740991 else value
        return super().build(recipe)


def keys(mapping):
    return sorted(mapping, key=lambda k: k.encode('utf-16-be', 'surrogatepass'))


async def observe_case(call, case, row, Fact):
    runtime = Runtime(row['recipes'])
    recipe = json.loads(case['values'][0])
    input = runtime.build({'tag': 'ref', 'value': str(recipe['input'])})
    rows = [{**r, 'value': runtime.build({'tag': 'ref', 'value': str(r['value'])})} for r in recipe['reads']]
    input_ids = set()
    def collect(v):
        if not isinstance(v, (dict, list)) and type(v) is not tuple: return
        if id(v) in input_ids: return
        input_ids.add(id(v))
        values = dict.values(v) if isinstance(v, dict) else list.__iter__(v) if isinstance(v, list) else iter(v)
        for child in values: collect(child)
    collect(input)
    for r in rows: collect(r['value'])
    def view(root):
        count, active = [0], set()
        def walk(v, depth=0):
            count[0] += 1
            require(count[0] <= 65536 and depth <= 64, 'output capacity')
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
                    require(owned.frozen(v) and type(v.entries) is tuple, 'frozen fact')
                    mapping = dict(v.entries)
                else:
                    require(owned.frozen(v), 'immutable outcome or batch')
                    mapping = {f.name: getattr(v, f.name) for f in dataclasses.fields(v)}
                require(all(type(k) is str for k in mapping), 'record keys')
                return ['record', [[k, walk(mapping[k], depth + 1)] for k in keys(mapping)]]
            finally: active.remove(id(v))
        return walk(root)
    trace, batches, pending, read_requests, clock_calls = [], [], [], [], []
    mode = recipe['mode']
    async def defer(phase, value=None, throws=False):
        future = asyncio.get_running_loop().create_future()
        trace.append(phase); pending.append((phase, future, value, throws))
        return await future
    def receipt():
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
        async def read(self, request):
            read_requests.append(view(request))
            r = next((r for r in rows if r['slot'] == request['slot']), None)
            require(r is not None, 'undeclared read')
            return await defer('read:' + request['slot'], r['value'], r.get('throws', False))
        async def commit(self, batch):
            batches.append(view(batch))
            return await defer('commit', receipt(), mode == 'commit-throw')
        async def rollback(self):
            return await defer('rollback', None, mode == 'rollback-throw')
    transaction = Transaction()
    class Store:
        async def begin(self): return await defer('begin', transaction, mode == 'begin-throw')
    def clock(c):
        def tick():
            clock_calls.append(c['slot'])
            if c.get('mode') == 'throw': raise RuntimeError('fixture-clock')
            return c['value']
        return tick
    dependencies = {'store': Store(), 'clocks': {c['slot']: clock(c) for c in recipe['clocks'] if c.get('mode') != 'missing'}}
    baseline = owned.fingerprint(input)
    read_baselines = [owned.fingerprint(r['value']) for r in rows]
    task = asyncio.create_task(call(input, dependencies))
    # Unlike JS async functions, Python coroutines begin on scheduling. Reach
    # the first suspension before probing capture against caller-owned changes.
    await asyncio.sleep(0)
    synchronous_changed = baseline != owned.fingerprint(input)
    if recipe['capture']:
        for key, value in input.items():
            input[key] = not value if type(value) is bool else value + '-changed' if type(value) is str else value + 1 if type(value) in (int, float) else None
        def late(): raise RuntimeError('late-operation-clock')
        for key in dependencies['clocks']: dependencies['clocks'][key] = late
        baseline = owned.fingerprint(input)
    settled = {k: False for k in ('settled_before_begin', 'settled_before_commit', 'settled_before_rollback', 'settled_before_read')}
    try:
        for _ in range(512):
            for _ in range(8): await asyncio.sleep(0)
            if pending:
                phase, future, value, throws = pending.pop(0)
                key = 'settled_before_read' if phase.startswith('read:') else 'settled_before_' + phase
                settled[key] |= task.done()
                trace.append(phase + ('-rejected' if throws else '-resolved'))
                require(not future.done(), 'transaction port already settled')
                if throws: future.set_exception(asyncio.CancelledError() if recipe.get('cancel') == ('read' if phase.startswith('read:') else phase) else RuntimeError('fixture-' + phase))
                else: future.set_result(value)
                continue
            if task.done(): break
        require(task.done() and not pending, 'stalled Operation')
        outcome = await task
        return {'outcome': view(outcome), 'trace': trace, 'batches': batches, 'read_calls': len(read_requests), **settled,
                'getter_reads': len(runtime.touches), 'input_changed': synchronous_changed or baseline != owned.fingerprint(input),
                'read_requests': read_requests, 'clock_calls': clock_calls,
                'read_changed': any(owned.fingerprint(r['value']) != baseline for r, baseline in zip(rows, read_baselines))}
    finally:
        if not task.done():
            task.cancel()
            for _, future, _, _ in pending:
                if not future.done(): future.cancel()
            try: await task
            except (Exception, asyncio.CancelledError): pass


def run(data, predecessor, observer, event_observer):
    controls, root = data['controls'], pathlib.Path(data['root'])
    selected = lambda r: r['state'] == 'ready' and r.get('adapter') == 'python-operation'
    earlier = {**data, 'controls': {**controls, 'rows': [{**r, 'state': 'not_evaluable'} if selected(r) else r for r in controls['rows']]}}
    result = predecessor(earlier)
    by_selector = {r['selector']: r for r in result['rows']}
    async def execute():
        for row in controls['rows']:
            if not selected(row): continue
            m = row['module']
            payload = {'root': data['root'], 'actions': {row['selector']: row['action']}, 'nodes': row['nodes'],
                       'model': controls['data_model'], 'module_root': str(pathlib.PurePosixPath(controls['runtime_dir']).parent),
                       'rule_modules': controls['rule_modules'], 'event_modules': row['event_modules']}
            # Every transitive Rule and owned factory is observed by preceding
            # stages. Observe Event dependencies even if their own case budgets
            # left a pending Event row; never infer their semantics from a hash.
            for event in row['event_modules']:
                event_observer({'root': data['root'], 'runtime': controls['runtime_dir'] + '/event_values.py',
                                'bodies': {event['selector']: row['nodes'][event['selector']]['body']}, 'nodes': row['nodes']}, event)
            observer(payload, m)
            native = importlib.import_module(m['import_name'])
            require(pathlib.Path(native.__file__).resolve() == (root / m['relative_path']).resolve(), 'Operation module identity')
            call = getattr(native, m['callable'])
            require(owned.frozen(call) and facts.thaw(call.descriptor) == m['descriptor'], 'frozen bound Operation')
            require(inspect.iscoroutinefunction(type(call).__call__) and list(inspect.signature(call).parameters) == ['parameters', 'dependencies'], 'native awaited call shape')
            Fact = importlib.import_module(controls['runtime_dir'].replace('/', '.') + '.facts')._Fact
            for case in row['cases']:
                expected = json.loads(case['expected']['value'])
                observed = facts.thaw(call.descriptor) if case['mode'] == 'operation-descriptor' else await observe_case(call, case, row, Fact)
                require(observed == expected, 'outcome:' + row['selector'] + ':' + case['id'] + ':' + repr(observed)[:900] + ':expected:' + repr(expected)[:900])
            for name in ('__call__', 'descriptor', 'extra'):
                try: setattr(call, name, None)
                except (AttributeError, TypeError): pass
                else: raise ValueError('mutable Operation binding')
            for mutation in ('value', 'effect'):
                tree = ast.parse((root / m['provider_path']).read_bytes())
                if mutation == 'value':
                    returns = [n for n in ast.walk(tree.body[-1]) if isinstance(n, ast.Return)]
                    require(bool(returns), 'Operation return required')
                    returns[0].value = ast.Constant(None)
                else: tree.body.append(ast.Pass())
                ast.fix_missing_locations(tree); mutant = ast.unparse(tree).encode()
                compile(mutant, m['provider_path'], 'exec', dont_inherit=True)
                changed = copy.deepcopy(m); changed['descriptor']['provider']['sha256'] = hashlib.sha256(mutant).hexdigest()
                # Existing pinned observer stays unchanged. Redirect this single
                # owned provider read in memory and restore the method in all cases.
                read_bytes = pathlib.Path.read_bytes
                def read(path): return mutant if path == root / m['provider_path'] else read_bytes(path)
                with patch.object(pathlib.Path, 'read_bytes', read):
                    try: observer(payload, changed)
                    except ValueError as error: require('Operation semantics/types/effects' in str(error), 'nonsemantic substitution rejection')
                    else: raise ValueError('compiling Operation substitution survived')
            by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                           'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2}
    if any(selected(r) for r in controls['rows']): asyncio.run(execute())
    require(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in result['toolchain_files'].items()), 'toolchain changed after Operations')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
