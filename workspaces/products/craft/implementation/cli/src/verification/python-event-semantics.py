"""Execute shared source Event cases using existing Python carrier semantics."""
import ast
import copy
import dataclasses
import hashlib
import importlib
import json
import math
import pathlib
import types


def require(ok, why):
    if not ok: raise ValueError('PYTHON_EVENT_SEMANTICS:' + why)


def thaw(value):
    if type(value) is types.MappingProxyType: return {k: thaw(v) for k, v in value.items()}
    if type(value) is tuple: return [thaw(v) for v in value]
    require(type(value) in (str, int, bool, type(None)), 'immutable descriptor')
    return value


def numeric_view(value):
    if type(value) is list: return [numeric_view(v) for v in value]
    if type(value) is not dict: return value
    if set(value) == {'kind', 'value'} and value['kind'] == 'number': return {'kind': 'number', 'value': float(value['value'])}
    return {k: numeric_view(v) for k, v in value.items()}


class Runtime:
    def __init__(self, source, reference_scalars):
        self.source, self.reference_scalars, self.touches = source, reference_scalars, []

    def atom(self, recipe, field=None):
        kind, value = recipe['kind'], recipe['value']
        ref = (field or {}).get('type_ref', {})
        name = ref.get('name') if ref.get('kind') != 'reference' else ('integer' if self.reference_scalars[ref['selector']] == 'UInt64' else 'string')
        if kind == 'string': return value
        if kind == 'boolean': return value == 'true'
        if kind == 'python-int': return int(value)
        if kind == 'python-float': return float(value)
        if kind == 'number':
            number = float(value)
            return int(number) if name == 'integer' and math.isfinite(number) and number.is_integer() and abs(number) <= 9007199254740991 else number
        if kind == 'bigint':
            if name != 'decimal': return int(value)
            # JS BigInt is a distinct disallowed decimal carrier. An exact-type
            # rejecting subclass preserves that negative, while python-int
            # cases separately cover Python's permitted integer decimals.
            class DistinctInteger(int): pass
            return DistinctInteger(value)
        require(kind == 'bad', 'unknown atom')
        if value == 'null': return None
        if value == 'array': return []
        if value == 'object': return {}
        if value == 'function': return lambda: None
        if value in ('undefined', 'symbol'): return object()
        touches = self.touches
        class Hostile:
            def __str__(self): touches.append('str'); return '1'
            def __int__(self): touches.append('int'); return 1
            def __float__(self): touches.append('float'); return 1.0
            def __await__(self): touches.append('await'); return iter(())
        require(value in ('coercion', 'promise'), 'unknown malformed atom')
        return Hostile()

    def input(self, recipe):
        source = self.source
        fields = {f['field_id']: f for f in source['payload']}
        value = recipe['input']
        result = {'occurrence': {k: self.atom(v, source['occurrence_id']) for k, v in value['occurrence'].items()},
                  'payload': {k: self.atom(v, fields[k]) for k, v in value['payload'].items()}}
        if 'occurredAt' in value: result['occurredAt'] = self.atom(value['occurredAt'])
        for change in recipe['changes']:
            target, mode = change['target'], change['mode']
            original = result if target == 'input' else result[target]
            if mode in ('frozen', 'null-prototype'): mutated = original
            elif mode == 'null': mutated = None
            elif mode == 'undefined': mutated = object()
            elif mode == 'array': mutated = []
            elif mode == 'extra': mutated = {**original, '__extra__': True}
            elif mode == 'symbol': mutated = {**original, object(): True}
            elif mode == 'missing': mutated = {k: v for k, v in original.items() if k != change['field']}
            else:
                require(mode in ('getter', 'non-enumerable', 'inherited'), 'unknown field change')
                touches = self.touches
                class HostileFields(dict):
                    def get(self, *args): touches.append('get'); return None
                    def __getitem__(self, key): touches.append('getitem'); return None
                mutated = HostileFields(original)
            if target == 'input': result = mutated
            else: result[target] = mutated
        return result

    def value(self, output):
        source = self.source
        require(owned.frozen(output), 'frozen Event record')
        require(type(output.occurrence) is types.MappingProxyType and type(output.payload) is types.MappingProxyType, 'immutable Event fields')
        require(type(output.type) is str and type(output.version) is str and type(output.occurredAt) is str, 'Event metadata types')
        def atom(field, value):
            ref = field['type_ref']
            name = ref['name'] if ref['kind'] == 'primitive' else ('integer' if self.reference_scalars[ref['selector']] == 'UInt64' else 'string')
            exact = {'integer': int, 'decimal': float, 'boolean': bool}.get(name, str)
            require(type(value) is exact, 'exact Event carrier')
            if name == 'decimal': require(value != 0 or math.copysign(1, value) == 1, 'canonical decimal zero')
            kind = {'integer': 'bigint', 'decimal': 'number', 'boolean': 'boolean'}.get(name, 'string')
            return {'kind': kind, 'value': str(value) if name == 'integer' else ('true' if value else 'false') if name == 'boolean' else value}
        require(set(output.occurrence) == {source['occurrence_id']['field_id']}, 'occurrence field coverage')
        fields = {f['field_id']: f for f in source['payload']}
        require(set(output.payload).issubset(fields), 'payload field coverage')
        return {'type': output.type, 'version': output.version, 'occurredAt': {'kind': 'string', 'value': output.occurredAt},
                'occurrence': {k: atom(source['occurrence_id'], v) for k, v in output.occurrence.items()},
                'payload': {k: atom(fields[k], v) for k, v in output.payload.items()}}


def run(data, predecessor, observer):
    controls, root = data['controls'], pathlib.Path(data['root'])
    selected = lambda row: row.get('adapter') == 'python-event' and row['state'] == 'ready'
    earlier = {**data, 'controls': {**controls, 'rows': [{**r, 'state': 'not_evaluable'} if selected(r) else r for r in controls['rows']]}}
    result = predecessor(earlier)
    by_selector = {r['selector']: r for r in result['rows']}
    for row in controls['rows']:
        if not selected(row): continue
        m, source = row['module'], row['source']
        payload = {'root': data['root'], 'runtime': controls['runtime_dir'] + '/event_values.py', 'bodies': {row['selector']: source}, 'nodes': row['references']}
        observer(payload, m)
        module = importlib.import_module(m['import_name'])
        require(pathlib.Path(module.__file__).resolve() == (root / m['relative_path']).resolve(), 'Event module identity')
        call = getattr(module, m['callable'])
        require(owned.frozen(call) and thaw(call.descriptor) == m['descriptor'], 'bound Event descriptor')
        provider = importlib.import_module(m['provider_path'][:-3].replace('/', '.'))
        for index, ref in enumerate(m['reference_imports']):
            shared = importlib.import_module(ref['relative_path'][:-3].replace('/', '.')).EventRef
            supertype = int if ref['identity']['scalar'] == 'UInt64' else str
            require(getattr(provider, '_Ref' + str(index)) is shared and shared.__supertype__ is supertype and shared.__name__ == ref['selector'], 'shared reference type identity')
        runtime = Runtime(source, {ref['selector']: ref['identity']['scalar'] for ref in m['reference_imports']})
        generated = source['occurred_at_policy'] == 'generated'
        for case in row['cases']:
            expected = numeric_view(json.loads(case['expected']['value']))
            if case['mode'] == 'event-descriptor':
                require(thaw(call.descriptor) == expected, 'descriptor outcome')
                continue
            recipe = json.loads(case['values'][0]); runtime.touches.clear()
            arg = runtime.input(recipe); before = owned.fingerprint(arg)
            calls, outputs = [], []
            sentinel = RuntimeError('EVENT_CLOCK_SENTINEL')
            def clock():
                calls.append('clock')
                if recipe['clock']['kind'] == 'throw': raise sentinel
                return runtime.atom(recipe['clock']['value'])
            clock_arg = clock if recipe['clock']['kind'] in ('return', 'throw') else 0 if recipe['clock']['kind'] == 'number' else None if recipe['clock']['kind'] in ('null', 'absent') else object()
            try:
                for _ in range(2 if recipe['repeat'] else 1):
                    value = call(arg, clock_arg) if generated else call(arg)
                    require(type(value) is module.EventValue, 'exact Event record type')
                    require(value.occurrence is not arg['occurrence'] and value.payload is not arg['payload'], 'detached Event fields')
                    require(all(value is not previous and value.occurrence is not previous.occurrence and value.payload is not previous.payload for previous in outputs), 'fresh Event occurrence')
                    outputs.append(value)
                observed = {'result': {'kind': 'value', 'values': [runtime.value(v) for v in outputs], 'detached': True, 'fresh': True}, 'clock_calls': len(calls)}
            except (TypeError, RuntimeError) as error:
                same = error is sentinel
                observed = {'result': {'kind': 'error', 'name': 'Error' if same else type(error).__name__, 'message': str(error), 'same_clock_error': same}, 'clock_calls': len(calls)}
            require(observed == expected, 'outcome:' + row['selector'] + ':' + case['id'] + ':' + repr(observed)[:450] + ':expected:' + repr(expected)[:450])
            if observed['result']['kind'] == 'value':
                # A mapping proxy can still alias a mutable input dictionary.
                # Probe detachment with a reversible change to our own input.
                snapshots = [runtime.value(v) for v in outputs]
                for target in ('occurrence', 'payload'):
                    fields = arg[target]
                    key = next(iter(fields), '__detachment_probe__')
                    present, previous = key in fields, fields.get(key)
                    fields[key] = object()
                    try: require([runtime.value(v) for v in outputs] == snapshots, 'Event fields alias input')
                    finally:
                        if present: fields[key] = previous
                        else: del fields[key]
            require(not runtime.touches and before == owned.fingerprint(arg), 'Event mutation/coercion/await')
        for name in ('__call__', 'descriptor', 'extra'):
            try: setattr(call, name, None)
            except (AttributeError, TypeError): pass
            else: raise ValueError('mutable Event binding')
        # Native arity is Python's TypeError boundary, not JavaScript's undefined
        # argument. Shared missing-clock recipes transport absence as None.
        try: call()
        except TypeError: pass
        else: raise ValueError('missing Event input accepted')
        if generated:
            try: call({})
            except TypeError: pass
            else: raise ValueError('missing native clock argument accepted')
        for mutation in ('value', 'effect'):
            tree = ast.parse((root / m['provider_path']).read_bytes())
            if mutation == 'value': tree.body[-1].body[-1].value.args[0] = ast.Constant(value='__wrong_event_type__')
            else: tree.body.append(ast.Pass())
            ast.fix_missing_locations(tree); mutant = ast.unparse(tree).encode()
            compile(mutant, m['provider_path'], 'exec', dont_inherit=True)
            changed = copy.deepcopy(m); changed['descriptor']['provider']['sha256'] = hashlib.sha256(mutant).hexdigest()
            try: observer(payload, changed, {m['provider_path']: mutant})
            except ValueError as error: require('Event semantics or effects' in str(error), 'nonsemantic Event substitution rejection')
            else: raise ValueError('compiling Event substitution survived')
        by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                      'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2}
    require(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in result['toolchain_files'].items()), 'toolchain changed after Events')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
