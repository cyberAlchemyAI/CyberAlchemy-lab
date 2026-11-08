"""Realize shared owned-value recipes; source expectations remain external.

Sum execution includes record construction probes, not full factory lifecycle
qualification. The same recipe runtime is reusable by that later executor.
"""
import ast
import dataclasses
import hashlib
import importlib
import json
import pathlib
import sys
import types


def require(ok, why):
    if not ok:
        raise ValueError('PYTHON_OWNED_SEMANTICS:' + why)


def canonical_view(value):
    if type(value) is list: return [canonical_view(v) for v in value]
    if type(value) is not dict: return value
    result = {k: canonical_view(v) for k, v in value.items()}
    if result.get('kind') == 'named-enum': result.pop('frozen', None)
    # Set order is not cross-language semantic identity. Each backend's key
    # representation may choose a different canonical order of owned members.
    if result.get('kind') == 'set': result['items'].sort(key=lambda v: json.dumps(v, sort_keys=True))
    return result


def fingerprint(value):
    if isinstance(value, dict): return (type(value), tuple((fingerprint(k), fingerprint(v)) for k, v in dict.items(value)))
    if isinstance(value, list): return (type(value), tuple(fingerprint(v) for v in list.__iter__(value)))
    if type(value) is tuple: return ('tuple', tuple(fingerprint(v) for v in value))
    if type(value) in (str, bool, int, float, type(None)): return (type(value).__name__, repr(value))
    if isinstance(value, type): return ('type', id(value))
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return (type(value), tuple((f.name, fingerprint(getattr(value, f.name))) for f in dataclasses.fields(value)))
    try: attributes = object.__getattribute__(value, '__dict__')
    except AttributeError: return (type(value), id(value))
    return (type(value), id(value), fingerprint(attributes))


def frozen(value):
    return dataclasses.is_dataclass(value) and value.__dataclass_params__.frozen and not hasattr(value, '__dict__')


def reject(action, message):
    try: action()
    except TypeError as error: require(type(error) is TypeError and str(error) == message, 'ownership error:' + str(error))
    else: raise ValueError('unowned value accepted')


class Runtime:
    def __init__(self, data, row):
        self.root, self.row = pathlib.Path(data['root']), row
        self.dependencies, self.factories = row['dependencies'], {m['selector']: m for m in data['controls']['factory_modules']}
        self.modules, self.foreign_modules, self.touches = {}, {}, []

    def module(self, selector, foreign=False):
        cache = self.foreign_modules if foreign else self.modules
        if selector not in cache:
            dep = self.dependencies[selector]
            name = dep['relative_path'][:-3].replace('/', '.')
            original = importlib.import_module(name)
            require(pathlib.Path(original.__file__).resolve() == (self.root / dep['relative_path']).resolve(), 'owned module identity')
            if foreign:
                module = types.ModuleType(name + '__semantic_foreign')
                module.__package__, module.__file__ = original.__package__, original.__file__
                sys.modules[module.__name__] = module
                exec(compile(pathlib.Path(original.__file__).read_bytes(), original.__file__, 'exec', dont_inherit=True), module.__dict__)
                cache[selector] = module
            else: cache[selector] = original
        return cache[selector]

    def component(self, selector):
        return getattr(self.module(selector), self.dependencies[selector]['symbol'])

    def fields(self, recipe):
        return {name: self.build(value) for name, value in recipe['fields'].items()}

    def record_result(self, recipe, foreign=False):
        dep = self.dependencies[recipe['selector']]
        arg = self.fields(recipe)
        before = fingerprint(arg)
        result = getattr(self.module(recipe['selector'], foreign), dep['callable'])().create(arg)
        require(fingerprint(arg) == before, 'factory input mutation')
        require(frozen(result) and type(result.ok) is bool and type(result.failure_codes) is tuple and frozen(result.trace), 'native factory result')
        require(type(result.trace.phases) is tuple and type(result.trace.validators) is tuple, 'immutable factory trace')
        metadata = self.factories[recipe['selector']]
        validators = {v['rule']: v for v in metadata['base_validators']}
        for trace in result.trace.validators:
            expected = validators[trace.rule]
            require(frozen(trace) and trace.closure_sha256 == expected['closure_sha256'] and trace.artifact_sha256 == expected['artifact_sha256'], 'validator trace binding')
        require(result.value is not None if result.ok else result.value is None, 'factory value/failure separation')
        observed = {'ok': result.ok, 'failure_codes': list(result.failure_codes), 'trace': {'route': result.trace.route,
                    'phases': list(result.trace.phases), 'validators': [{'rule': v.rule, 'outcome': v.outcome} for v in result.trace.validators]}}
        return result, observed

    def clone(self, value):
        result = object.__new__(type(value))
        for f in dataclasses.fields(value): object.__setattr__(result, f.name, getattr(value, f.name))
        return result

    def foreign(self, recipe):
        dep = self.dependencies[recipe['selector']]
        if dep['kind'] != 'Enum':
            result, _ = self.record_result(recipe, True)
            require(result.ok, 'foreign record witness')
            return result.value
        module = self.module(recipe['selector'], True)
        stem = recipe['selector'].split(':')[1].replace('-', '_')
        if dep['plain']: return getattr(module, 'parse_' + stem)(recipe['variant'])
        arg = self.build(recipe['input'])
        before = fingerprint(arg)
        try: return getattr(module, 'create_' + stem)(arg)
        finally: require(before == fingerprint(arg), 'foreign sum input mutation')

    def build(self, recipe):
        tag = recipe['tag']
        if tag == 'null': return None
        if tag == 'scalar': return int(recipe['value']) if recipe.get('format') in ('number', 'bigint') else recipe['value']
        if tag in ('list', 'set'): return [self.build(r) for r in recipe['items']]
        if tag == 'sum': return {'variant': recipe['variant'], **({'payload': self.build(recipe['payload'])} if 'payload' in recipe else {})}
        if tag == 'enum': return getattr(self.module(recipe['selector']), 'parse_' + recipe['selector'].split(':')[1].replace('-', '_'))(recipe['variant'])
        if tag == 'named':
            arg = self.build(recipe['input'])
            before = fingerprint(arg)
            try: return self.component(recipe['selector']).normalize(arg)
            finally: require(before == fingerprint(arg), 'nested sum input mutation')
        if tag == 'record':
            result, observed = self.record_result(recipe)
            expected = next((p['expected'] for p in self.dependencies[recipe['selector']]['probes'] if p['recipe'] == recipe), None)
            require(expected is not None and observed == expected and result.ok, 'source record witness')
            return result.value
        require(tag == 'bad', 'unknown owned recipe')
        mode, base_recipe = recipe['mode'], recipe['base']
        if mode in ('raw-named', 'clone-named', 'foreign-named'):
            dep = self.dependencies[base_recipe['selector']]
            if mode == 'foreign-named': return self.foreign(base_recipe)
            if mode == 'raw-named':
                return self.fields(base_recipe) if dep['kind'] != 'Enum' else {'variant': base_recipe['variant']} if dep['plain'] else self.build(base_recipe['input'])
            value = self.build(base_recipe)
            return types.SimpleNamespace(variant=base_recipe['variant']) if dep['kind'] == 'Enum' and dep['plain'] else self.clone(value)
        base = self.build(base_recipe)
        constants = {'null': None, 'undefined': object(), 'number': 0, 'string': 'invalid', 'negative': '-1',
                     'overflow': '18446744073709551616', 'padded': '01', 'unsafe': 9007199254740992.0, 'fraction': 1.5, 'array': [], 'object': {}}
        if mode in constants: return constants[mode]
        touches = self.touches
        class HostileScalar:
            def __str__(self): touches.append('str'); return '1'
            def __int__(self): touches.append('int'); return 1
        class HostileDict(dict):
            def get(self, *args): touches.append('get'); return None
            def __getitem__(self, key): touches.append('getitem'); return None
        class HostileList(list):
            def __iter__(self): touches.append('iter'); return iter(())
        if mode == 'coercion': return HostileScalar()
        if mode in ('getter', 'inherited'): return HostileDict(base)
        if mode == 'symbol': return {**base, object(): True}
        if mode == 'extra': return {**base, '__extra__': True}
        if mode == 'missing-variant': return {k: v for k, v in base.items() if k != 'variant'}
        if mode == 'unknown-variant': return {**base, 'variant': '__semantic_unknown__'}
        if mode == 'missing-payload': return {k: v for k, v in base.items() if k != 'payload'}
        if mode == 'surplus-payload': return {**base, 'payload': None}
        if mode in ('collection-extra', 'collection-symbol', 'collection-inherited', 'sparse', 'collection-getter'): return HostileList(base)
        if mode == 'duplicate': return [*base, base[0]]
        raise ValueError('unknown owned negative recipe:' + mode)

    def view(self, t, value):
        kind = t['kind']
        if kind == 'scalar':
            require(type(value) is {'String': str, 'Bool': bool, 'UInt64': int}[t['name']], 'exact scalar type')
            return {'kind': t['name'], 'value': str(value) if t['name'] == 'UInt64' else value}
        if kind == 'optional': return None if value is None else self.view(t['element'], value)
        if kind in ('list', 'set'):
            require(type(value) is tuple, 'immutable native collection')
            return {'kind': kind, 'frozen': True, 'plain': True, 'items': [self.view(t['element'], v) for v in value]}
        if kind == 'sum':
            require(frozen(value), 'frozen native sum')
            variant = next(v for v in t['variants'] if v['name'] == value.variant)
            fields = sorted(f.name for f in dataclasses.fields(value))
            result = {'kind': 'sum', 'variant': value.variant, 'frozen': True, 'keys': fields}
            if variant['payload'] is not None: result['payload'] = self.view(variant['payload'], value.payload)
            return result
        dep = self.dependencies[t['selector']]
        if dep['kind'] == 'Enum' and dep['plain']:
            require(type(value) is getattr(self.module(t['selector']), dep['symbol']), 'nominal Enum type')
            wire = getattr(self.module(t['selector']), 'emit_' + t['selector'].split(':')[1].replace('-', '_'))(value)
            return {'kind': 'named-enum', 'selector': t['selector'], 'owned': True, 'variant': wire}
        require(self.component(t['selector']).is_owned(value), 'nominal owned dependency')
        if dep['kind'] == 'Enum':
            return {'kind': 'named-sum', 'selector': t['selector'], 'owned': True, 'value': self.view({'kind': 'sum', 'variants': dep['contract']['variants']}, value)}
        fields = self.factories[t['selector']]['fields']
        require(frozen(value) and frozen(value.fields), 'immutable native record')
        require([f.name for f in dataclasses.fields(value.fields)] == [f['native_name'] for f in fields], 'native record field coverage')
        return {'kind': 'named-record', 'selector': t['selector'], 'record_kind': dep['kind'], 'owned': True, 'frozen': True, 'fields_frozen': True,
                'fields_keys': [f['name'] for f in fields], 'fields': {f['name']: self.view(f['type'], getattr(value.fields, f['native_name'])) for f in fields}}


def run(data, predecessor, owned_observer, enum_observer, rule_observer):
    controls, root = data['controls'], pathlib.Path(data['root'])
    is_sum = lambda r: r.get('adapter') == 'python-sum' and r['state'] == 'ready'
    earlier = {**data, 'controls': {**controls, 'rows': [{**r, 'state': 'not_evaluable'} if is_sum(r) else r for r in controls['rows']]}}
    result = predecessor(earlier)
    by_selector = {r['selector']: r for r in result['rows']}
    for row in controls['rows']:
        if not is_sum(row): continue
        runtime = Runtime(data, row)
        component = runtime.component(row['selector'])
        call = getattr(runtime.module(row['selector']), row['module']['callable'])
        baseline = call(runtime.build(row['baseline']))
        keys, reference_keys = {}, {}
        for case in row['cases']:
            runtime.touches.clear()
            recipe = json.loads(case['values'][0])
            before, arg = None, None
            try:
                if case['mode'] == 'record-probe':
                    _, value = runtime.record_result(recipe)
                else:
                    arg = runtime.build(recipe)
                    before = fingerprint(arg)
                    output = call(arg)
                    require(component.is_owned(output) and frozen(output), 'owned immutable sum')
                    repeated = call(runtime.build(recipe))
                    require(output is not repeated and output == repeated and repeated == output and hash(output) == hash(repeated), 'fresh equivalent sum')
                    native_key = component.key(output)
                    require(type(native_key) is str and native_key == component.key(repeated), 'stable native key')
                    expected = json.loads(case['expected']['value']) if case['expected']['kind'] == 'value' else None
                    require(expected is not None, 'negative accepted')
                    require((output == baseline) == expected['equals_baseline'] and (baseline == output) == expected['equals_baseline'], 'baseline identity')
                    if native_key in keys: require(keys[native_key] == expected['key'], 'collapsed source identities')
                    keys[native_key] = expected['key']
                    if expected['key'] in reference_keys:
                        prior_key, prior = reference_keys[expected['key']]
                        require(prior_key == native_key and prior == output and output == prior and hash(prior) == hash(output), 'split equivalent source identity')
                    reference_keys[expected['key']] = (native_key, output)
                    clone = runtime.clone(output)
                    foreign = runtime.foreign({'tag': 'named', 'selector': row['selector'], 'input': recipe})
                    for unowned in (clone, foreign):
                        require(not component.is_owned(unowned) and not (output == unowned) and not (unowned == output), 'nominal sum boundary')
                        reject(lambda: component.key(unowned), 'UNOWNED_SUM_CASE')
                    reject(lambda: type(output)(), 'SUM_CONSTRUCTION_REQUIRES_COMPONENT')
                    try: output.variant = '__changed__'
                    except (AttributeError, TypeError): pass
                    else: raise ValueError('mutable sum variant')
                    value = {'view': runtime.view(row['shape'], output), 'key': expected['key'], 'equals_baseline': output == baseline}
                observed = {'kind': 'value', 'value': canonical_view(value)}
            except (TypeError, ValueError) as error:
                observed = {'kind': 'error', 'name': type(error).__name__, 'message': str(error)}
            expected = {'kind': 'value', 'value': canonical_view(json.loads(case['expected']['value']))} if case['expected']['kind'] == 'value' else {'kind': 'error', 'name': 'TypeError', 'message': case['native_error']}
            require(observed == expected, 'outcome:' + row['selector'] + ':' + case['id'] + ':' + repr(observed)[:500] + ':expected:' + repr(expected)[:500])
            require(not runtime.touches and (before is None or before == fingerprint(arg)), 'input mutation/coercion')
        for name in ('normalize', 'key', 'is_owned'):
            try: setattr(component, name, lambda value: value)
            except (AttributeError, TypeError): pass
            else: raise ValueError('mutable owned component')
        source = (root / row['module']['relative_path']).read_bytes()
        for mutation in ('return', 'effect'):
            tree = ast.parse(source)
            if mutation == 'return': tree.body[-1].body[0].value = ast.Constant(value=None)
            else: tree.body.append(ast.Pass())
            ast.fix_missing_locations(tree)
            mutant = ast.unparse(tree).encode()
            compile(mutant, row['module']['relative_path'], 'exec', dont_inherit=True)
            try: owned_observer(data, enum_observer, rule_observer, {row['module']['relative_path']: mutant})
            except ValueError as error: require('owned semantics/effects' in str(error), 'nonsemantic sum mutation rejection')
            else: raise ValueError('compiling sum substitution survived')
        by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                      'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2}
    require(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in result['toolchain_files'].items()), 'toolchain changed after owned execution')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
