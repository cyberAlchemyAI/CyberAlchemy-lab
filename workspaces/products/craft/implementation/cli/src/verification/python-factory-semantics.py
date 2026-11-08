"""Source-directed lifecycle execution against independently observed factories.

The injected owned helper is a pinned predecessor; this layer adds lifecycle
requests without changing native products or interpreting Rules itself.
"""
import ast
import dataclasses
import hashlib
import json
import pathlib

require, fingerprint, frozen = owned.require, owned.fingerprint, owned.frozen


class Runtime(owned.Runtime):
    def build(self, recipe):
        if recipe['tag'] == 'fields': return self.fields(recipe)
        if recipe['tag'] == 'bad':
            mode, base = recipe['mode'], recipe['base']
            if base['tag'] == 'fields' and mode in ('frozen', 'null-prototype'):
                # Both JS recipes denote inert own fields. Python accepts exact
                # dictionaries; no immutable/mapping-subclass input is claimed.
                return self.fields(base)
            if base['tag'] == 'fields' and mode == 'missing-field':
                return {k: v for k, v in self.fields(base).items() if k != recipe['field']}
            if mode in ('getter', 'non-enumerable') and base['tag'] in ('fields', 'record'):
                touches = self.touches
                class HostileFields(dict):
                    def get(self, *args): touches.append('get'); raise AssertionError('field accessor evaluated')
                    def __getitem__(self, key): touches.append('getitem'); raise AssertionError('field accessor evaluated')
                return HostileFields(self.fields(base))
        return super().build(recipe)

    def factory(self, chain, foreign=False):
        base = getattr(self.module(self.row['selector'], foreign), self.row['module']['callable'])()
        require(frozen(base) and base.extensions == (), 'immutable base factory')
        factory, tracked = base, [(base, ())]
        for index, name in enumerate(chain):
            previous = factory
            factory = factory.extend(name)
            require(factory is not previous and frozen(factory), 'fresh immutable extension')
            require(type(factory.extensions) is tuple and factory.extensions == tuple(chain[:index + 1]), 'extension chain order')
            tracked.append((factory, factory.extensions))
        return factory, tracked

    def result(self, result):
        require(frozen(result) and type(result.ok) is bool and type(result.failure_codes) is tuple, 'immutable lifecycle result')
        require(frozen(result.trace) and type(result.trace.phases) is tuple and type(result.trace.validators) is tuple, 'immutable lifecycle trace')
        require(all(frozen(v) for v in result.trace.validators), 'immutable validator rows')
        require(result.value is not None if result.ok else result.value is None, 'lifecycle value/failure separation')
        return {'ok': result.ok, 'failure_codes': list(result.failure_codes), 'trace': {'route': result.trace.route,
                'phases': list(result.trace.phases), 'validators': [dataclasses.asdict(v) for v in result.trace.validators]}}


def run(data, predecessor, owned_observer, enum_observer, rule_observer):
    controls, root = data['controls'], pathlib.Path(data['root'])
    selected = lambda row: row.get('adapter') == 'python-factory' and row['state'] == 'ready'
    earlier = {**data, 'controls': {**controls, 'rows': [{**r, 'state': 'not_evaluable'} if selected(r) else r for r in controls['rows']]}}
    result = predecessor(earlier)
    by_selector = {r['selector']: r for r in result['rows']}
    for row in controls['rows']:
        if not selected(row): continue
        runtime, keys, reference_keys = Runtime(data, row), {}, {}
        component = runtime.component(row['selector'])
        baseline = runtime.build(row['baseline'])
        for case in row['cases']:
            runtime.touches.clear()
            request = json.loads(case['values'][0])
            tracked, watched = [], []
            try:
                factory, chain = runtime.factory(request['chain']); tracked.extend(chain)
                require(hasattr(factory, 'transition') == (row['kind'] == 'Entity'), 'lifecycle route surface')
                arg = runtime.build(request['input']); watched.append((arg, fingerprint(arg)))
                previous = runtime.build(request['previous']) if 'previous' in request else None
                watched.append((previous, fingerprint(previous)))
                if request['route'] == 'extend':
                    factory.extend(arg)
                    raise ValueError('invalid extension accepted')
                native = factory.transition(previous, arg) if request['route'] == 'transition' else getattr(factory, request['route'])(arg)
                value = runtime.result(native)
                value.update(extensions=list(factory.extensions), snapshot=None)
                if native.ok:
                    output = native.value
                    require(component.is_owned(output) and frozen(output) and frozen(output.fields), 'owned immutable snapshot')
                    if row['kind'] == 'Entity':
                        identity = tuple(getattr(output.fields, f['native_name']) for f in runtime.factories[row['selector']]['fields'] if f['identity'])
                        require(type(output.identity) is tuple and len(output.identity) == len(identity) and all(a is b for a, b in zip(output.identity, identity)), 'entity identity fields')
                    else: require(not hasattr(output, 'identity'), 'value object has no entity identity')
                    expected = json.loads(case['expected']['value'])['snapshot']
                    require(expected is not None, 'unexpected accepted factory')
                    copy_arg = runtime.build(request['input']); watched.append((copy_arg, fingerprint(copy_arg)))
                    copy = factory.create(copy_arg)
                    require(copy.ok and runtime.result(copy)['trace']['route'] == 'create', 'factory copy witness')
                    require(copy.value is not output and output is not previous, 'fresh lifecycle snapshot')
                    require(output == copy.value and copy.value == output and hash(output) == hash(copy.value), 'equivalent snapshot copy')
                    native_key = component.key(output)
                    require(type(native_key) is str and native_key == component.key(copy.value), 'stable snapshot key')
                    require((output == baseline) == expected['equals_baseline'] and (baseline == output) == expected['equals_baseline'], 'baseline snapshot identity')
                    if native_key in keys: require(keys[native_key] == expected['key'], 'collapsed snapshot identities')
                    keys[native_key] = expected['key']
                    if expected['key'] in reference_keys:
                        prior_key, prior = reference_keys[expected['key']]
                        require(prior_key == native_key and prior == output and output == prior and hash(prior) == hash(output), 'split snapshot identity')
                    reference_keys[expected['key']] = (native_key, output)
                    foreign_factory, foreign_chain = runtime.factory(request['chain'], True); tracked.extend(foreign_chain)
                    foreign_arg = runtime.build(request['input']); watched.append((foreign_arg, fingerprint(foreign_arg)))
                    foreign = foreign_factory.create(foreign_arg)
                    require(foreign.ok, 'foreign factory witness')
                    runtime.result(foreign)
                    for unowned in (runtime.clone(output), foreign.value):
                        require(not component.is_owned(unowned) and not (output == unowned) and not (unowned == output), 'snapshot ownership boundary')
                        owned.reject(lambda: component.key(unowned), 'UNOWNED_SNAPSHOT')
                        owned.reject(lambda: component.normalize(unowned), 'UNOWNED_SNAPSHOT')
                    require(component.normalize(output) is output, 'owned normalization identity')
                    owned.reject(lambda: type(output)(), 'SNAPSHOT_CONSTRUCTION_REQUIRES_FACTORY')
                    try: output.fields = None
                    except (AttributeError, TypeError): pass
                    else: raise ValueError('mutable snapshot fields')
                    value['snapshot'] = {'view': runtime.view(row['shape'], output), 'key': expected['key'], 'equals_baseline': output == baseline}
                observed = {'kind': 'value', 'value': owned.canonical_view(value)}
            except (TypeError, ValueError) as error:
                observed = {'kind': 'error', 'name': type(error).__name__, 'message': str(error)}
            expected = {'kind': 'value', 'value': owned.canonical_view(json.loads(case['expected']['value']))} if case['expected']['kind'] == 'value' else case['expected']
            require(observed == expected, 'factory outcome:' + row['selector'] + ':' + case['id'] + ':' + repr(observed)[:600] + ':expected:' + repr(expected)[:600])
            require(not runtime.touches and all(fingerprint(v) == before for v, before in watched), 'factory input mutation/coercion')
            require(all(frozen(v) and v.extensions == before for v, before in tracked), 'factory chain mutation')
        for name in ('normalize', 'key', 'is_owned'):
            try: setattr(component, name, lambda v: v)
            except (AttributeError, TypeError): pass
            else: raise ValueError('mutable factory component')
        base, _ = runtime.factory([])
        owned.reject(lambda: type(base)(), 'FACTORY_CONSTRUCTION_REQUIRES_PROVIDER')
        owned.reject(lambda: runtime.clone(base).create({}), 'UNOWNED_FACTORY')
        source = (root / row['module']['relative_path']).read_bytes()
        for mutation in ('return', 'effect'):
            tree = ast.parse(source)
            if mutation == 'return': tree.body[-1].value = ast.Constant(value=None)
            else: tree.body.append(ast.Pass())
            ast.fix_missing_locations(tree)
            mutant = ast.unparse(tree).encode()
            compile(mutant, row['module']['relative_path'], 'exec', dont_inherit=True)
            try: owned_observer(data, enum_observer, rule_observer, {row['module']['relative_path']: mutant})
            except ValueError as error: require('owned semantics/effects' in str(error), 'nonsemantic factory mutation rejection')
            else: raise ValueError('compiling factory substitution survived')
        by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                      'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2}
    require(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in result['toolchain_files'].items()), 'toolchain changed after factories')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
