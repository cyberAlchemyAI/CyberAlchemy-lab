"""Source-case replay for nominal Python State Machines; intents stay data."""
import ast
import copy
import dataclasses
import enum
import hashlib
import importlib
import inspect
import json
import pathlib
import sys
import types


def require(ok, why):
    if not ok: raise ValueError('PYTHON_STATE_MACHINE_SEMANTICS:' + why)


class Runtime:
    def __init__(self, recipes):
        self.recipes, self.touches = recipes, []
        touches = self.touches
        class HostileDict(dict):
            def __getitem__(self, key): touches.append('get'); return None
        class HostileList(list):
            def __iter__(self): touches.append('iter'); return iter(())
        class HostileScalar:
            def __int__(self): touches.append('int'); return 1
            def __str__(self): touches.append('str'); return '1'
        self.dict, self.list, self.scalar = HostileDict, HostileList, HostileScalar

    def build(self, r):
        tag = r['tag']
        if tag == 'ref': return self.build(self.recipes[int(r['value'])])
        if tag == 'null': return None
        if tag == 'scalar': return int(r['value']) if r.get('format') in ('number', 'bigint') else r['value']
        if tag in ('fields', 'record'): return {k: self.build(v) for k, v in r['fields'].items()}
        if tag in ('list', 'set'): return [self.build(v) for v in r['items']]
        if tag == 'named': return self.build(r['input'])
        if tag == 'sum': return {'variant': r['variant'], **({'payload': self.build(r['payload'])} if 'payload' in r else {})}
        require(tag == 'bad', 'unknown fact recipe')
        base, mode, field = self.build(r['base']), r['mode'], r.get('field', 'variant')
        if mode in ('frozen', 'null-prototype'): return base
        constants = {'null': None, 'undefined': object(), 'number': 0, 'boolean': False,
                     'string': 'invalid', 'array': [], 'object': {}, 'negative': '-1',
                     'overflow': '18446744073709551616', 'padded': '01', 'unsafe': 9007199254740992.0,
                     'fraction': 1.5, 'nan': float('nan'), 'infinity': float('inf')}
        if mode in constants: return constants[mode]
        if mode == 'coercion': return self.scalar()
        if mode in ('getter', 'non-enumerable', 'inherited'): return self.dict(base)
        if mode == 'symbol': return {**base, object(): True}
        if mode == 'extra':
            name = 'extra'
            while name in base: name += '_'
            return {**base, name: True}
        if mode == 'missing-field': return {k: v for k, v in base.items() if k != field}
        if mode == 'missing-variant': return {k: v for k, v in base.items() if k != 'variant'}
        if mode == 'unknown-variant': return {**base, 'variant': '__semantic_unknown__'}
        if mode == 'missing-payload': return {k: v for k, v in base.items() if k != 'payload'}
        if mode == 'surplus-payload': return {**base, 'payload': None}
        if mode in ('collection-extra', 'collection-symbol', 'collection-inherited', 'sparse', 'collection-getter', 'collection-hidden'): return self.list(base)
        if mode == 'duplicate': return [*base, base[0]]
        raise ValueError('unknown State Machine fact recipe:' + mode)


def thaw(v):
    if type(v) is types.MappingProxyType: return {k: thaw(x) for k, x in v.items()}
    if type(v) is tuple: return [thaw(x) for x in v]
    require(type(v) in (str, bool, int, type(None)), 'immutable descriptor or intent')
    return v


def run(data, predecessor, observer):
    controls, root = data['controls'], pathlib.Path(data['root'])
    selected = lambda r: r['state'] == 'ready' and r.get('adapter') == 'python-state-machine'
    earlier = {**data, 'controls': {**controls, 'rows': [{**r, 'state': 'not_evaluable'} if selected(r) else r for r in controls['rows']]}}
    result = predecessor(earlier)
    by_selector = {r['selector']: r for r in result['rows']}
    audit_state = {'armed': False, 'effects': []}
    def audit(event, args):
        if audit_state['armed'] and (event in ('open', 'import', 'exec', 'compile') or event.startswith(('os.', 'socket.', 'subprocess.', 'ctypes.'))):
            audit_state['effects'].append(event)
    sys.addaudithook(audit)
    for row in controls['rows']:
        if not selected(row): continue
        m, c = row['module'], row['contract']
        payload = {'root': data['root'], 'contracts': {row['selector']: c}, 'model': controls['data_model'],
                   'module_root': str(pathlib.PurePosixPath(controls['runtime_dir']).parent),
                   'nodes': row['events'], 'rule_modules': controls['rule_modules']}
        # Checked Rule source observation is performed by the predecessor before
        # any reducer can run. Check this reducer's direct receipt bytes too.
        for ref in m['descriptor']['rule_dependencies']:
            require(hashlib.sha256((root / ref['path']).read_bytes()).hexdigest() == ref['sha256'], 'Rule dependency bytes')
        for ref in m['descriptor']['runtime']:
            require(hashlib.sha256((root / controls['runtime_dir'] / ref['id']).read_bytes()).hexdigest() == ref['sha256'], 'runtime bytes')
        observer(payload, m)
        native = importlib.import_module(m['import_name'])
        require(pathlib.Path(native.__file__).resolve() == (root / m['relative_path']).resolve(), 'module identity')
        call, State, Trigger = getattr(native, m['callable']), native.State, native.Trigger
        require(issubclass(State, enum.Enum) and issubclass(Trigger, enum.Enum) and State is not Trigger, 'nominal roles')
        require([s.value for s in State] == sorted(c['states']), 'state coverage')
        require([t.value for t in Trigger] == sorted(set(t['trigger_event_ref'] for t in c['transitions'])), 'trigger coverage')
        require(native.initial_state is State(c['initial']), 'initial state')
        require(owned.frozen(call) and thaw(call.descriptor) == m['descriptor'], 'frozen source binding')
        require(list(inspect.signature(call).parameters) == ['state', 'trigger', 'parameters'] and not inspect.iscoroutinefunction(type(call).__call__), 'native call shape')
        runtime = Runtime(row['recipes'])
        def symbol(recipe, cls):
            value = runtime.build(recipe)
            if type(value) is str:
                try: return cls(value)
                except ValueError: pass
            return value
        def view(output):
            require(owned.frozen(output), 'frozen outcome')
            require(type(output.state) is State and any(output.state is s for s in State), 'nominal output state')
            require(type(output.output_intents) is tuple and all(type(i) is types.MappingProxyType for i in output.output_intents), 'immutable output intents')
            return {f.name: output.state.value if f.name == 'state' else thaw(getattr(output, f.name)) for f in dataclasses.fields(output)}
        for case in row['cases']:
            if case['mode'] == 'initial-state':
                require(case['expected'] == {'kind': 'value', 'value': native.initial_state.value}, 'initial outcome')
                continue
            runtime.touches.clear()
            arg = runtime.build({'tag': 'ref', 'value': case['values'][0]})
            state, trigger = symbol(json.loads(case['values'][1]), State), symbol(json.loads(case['values'][2]), Trigger)
            before = owned.fingerprint(arg)
            expected = dict(case['expected'])
            if expected['kind'] == 'value': expected['value'] = json.loads(expected['value'])
            outputs = []
            for _ in range(2):
                audit_state['effects'].clear()
                audit_state['armed'] = True
                try:
                    try: output = call(state, trigger, arg)
                    except TypeError as error: observed = {'kind': 'error', 'name': 'TypeError', 'message': str(error)}
                    else:
                        observed = {'kind': 'value', 'value': view(output)}
                        require(all(output is not p for p in outputs), 'fresh replay result')
                        outputs.append(output)
                finally: audit_state['armed'] = False
                require(not audit_state['effects'], 'effect during reducer replay')
                require(observed == expected, 'outcome:' + row['selector'] + ':' + case['id'] + ':' + repr(observed)[:450] + ':expected:' + repr(expected)[:450])
                require(not runtime.touches and before == owned.fingerprint(arg), 'input mutation/coercion')
        for name in ('__call__', 'descriptor', 'extra'):
            try: setattr(call, name, None)
            except (AttributeError, TypeError): pass
            else: raise ValueError('mutable State Machine binding')
        baseline = next(k for k in row['cases'] if k['mode'] != 'initial-state' and k['expected']['kind'] == 'value')
        parameters = runtime.build({'tag': 'ref', 'value': baseline['values'][0]})
        state, trigger = next(iter(State)), next(iter(Trigger))
        # Wire strings are translated at the test boundary only. Public calls
        # must reject strings, other roles, foreign enums, and forged members.
        for cls, valid, other, side in ((State, state, trigger, 0), (Trigger, trigger, state, 1)):
            foreign = enum.Enum('Foreign', {x.name: x.value for x in cls})
            forged = object.__new__(cls); forged._name_ = valid.name; forged._value_ = valid.value
            for value in (valid.value, other, foreign(valid.value), forged, None, False, 0):
                try: call(value if side == 0 else state, value if side == 1 else trigger, parameters)
                except TypeError as error: require(str(error) == 'STATE_MACHINE_INPUT', 'nominal rejection boundary')
                else: raise ValueError('foreign or forged nominal input accepted')
        for mutation in ('value', 'effect'):
            tree = ast.parse((root / m['provider_path']).read_bytes())
            if mutation == 'value':
                returns = [n for n in ast.walk(tree.body[-1]) if isinstance(n, ast.Return)]
                require(bool(returns), 'reducer return required')
                returns[0].value = ast.Constant(None)
            else: tree.body.append(ast.Pass())
            ast.fix_missing_locations(tree); mutant = ast.unparse(tree).encode()
            compile(mutant, m['provider_path'], 'exec', dont_inherit=True)
            changed = copy.deepcopy(m); changed['descriptor']['provider']['sha256'] = hashlib.sha256(mutant).hexdigest()
            try: observer(payload, changed, {m['provider_path']: mutant})
            except ValueError as error: require('State Machine semantics/types/effects' in str(error), 'nonsemantic substitution rejection')
            else: raise ValueError('compiling State Machine substitution survived')
        by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                       'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2}
    require(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in result['toolchain_files'].items()), 'toolchain changed after State Machines')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
