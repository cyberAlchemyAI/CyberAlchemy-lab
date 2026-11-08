"""Native realization of shared source fact recipes, without domain factories."""
import ast
import codecs
import copy
import dataclasses
import hashlib
import importlib
import json
import pathlib
import sys


def require(ok, why):
    if not ok:
        raise ValueError('PYTHON_DATA_SEMANTICS:' + why)


def run(data, calculation, query_observer, mapping_observer, rule_observer, policy_observer):
    root, controls = pathlib.Path(data['root']).resolve(strict=True), data['controls']
    codecs.lookup('utf-16-le')
    codecs.lookup('utf-16-be')
    calculation_input = {**data, 'controls': {**controls, 'rows': [r if r['kind'] == 'Calculation' else {**r, 'state': 'not_evaluable'} for r in controls['rows']]}}
    result = calculation(calculation_input)
    by_selector = {r['selector']: r for r in result['rows']}
    sys.path.insert(0, str(root))
    touches = []
    rule_data = {'root': str(root), 'module_root': str(pathlib.PurePosixPath(controls['runtime_dir']).parent),
                 'rule_model': controls['data_model'], 'rule_modules': controls['rule_modules'],
                 'nodes': {s: {'body': {'typed_contract': c}} for s, c in controls['rule_contracts'].items()}}
    # Observe every transitive Rule before any selected decision can call it.
    for member in controls['rule_modules']:
        rule_observer(rule_data, member)

    class HostileDict(dict):
        def __getitem__(self, key):
            touches.append('get')
            return None

    class HostileList(list):
        def __iter__(self):
            touches.append('iter')
            return iter(())

    class HostileScalar:
        def __int__(self):
            touches.append('int')
            return 1
        def __str__(self):
            touches.append('str')
            return '1'

    def fingerprint(v):
        if type(v) is dict:
            return ('dict', tuple((fingerprint(k), fingerprint(x)) for k, x in v.items()))
        if type(v) in (list, tuple):
            return (type(v).__name__, tuple(fingerprint(x) for x in v))
        if type(v) in (str, bool, int, float, type(None)):
            return (type(v).__name__, repr(v))
        return (type(v).__name__, id(v))

    for row in controls['rows']:
        if row['state'] != 'ready' or row['kind'] == 'Calculation':
            continue
        require(row['kind'] in ('Query', 'Mapping', 'Rule', 'Policy'), 'unimplemented executor')
        module, contract = row['module'], row['contract']
        def observe(module, override=None):
            if row['kind'] == 'Rule':
                return rule_observer(rule_data, module, override)
            if row['kind'] == 'Policy':
                return policy_observer(root, module, contract, controls['data_model'], controls['runtime_dir'], [], controls['rule_modules'], controls['rule_contracts'], override)
            observer = query_observer if row['kind'] == 'Query' else mapping_observer
            return observer(root, module, contract, controls['data_model'], controls['runtime_dir'], override)
        observe(module)
        native = importlib.import_module(module['relative_path'][:-3].replace('/', '.'))
        require(pathlib.Path(native.__file__).resolve() == root / module['relative_path'], 'module identity')
        facts_module = importlib.import_module(controls['runtime_dir'].replace('/', '.') + '.facts')
        Fact = facts_module._Fact
        call = getattr(native, module['callable'])
        binding_controls = 0
        if row['kind'] != 'Rule':
            require(dataclasses.is_dataclass(call), 'native bound callable')
            for action in [lambda: setattr(call, 'descriptor', {}), lambda: setattr(call, 'replacement', 1), lambda: call.descriptor.__setitem__('selector', 'changed')]:
                try: action()
                except (TypeError, AttributeError): pass
                else: raise ValueError('mutable data binding')
                binding_controls += 1

        def build(r):
            tag = r['tag']
            if tag == 'ref': return build(row['recipes'][int(r['value'])])
            if tag == 'null': return None
            if tag == 'scalar': return int(r['value']) if r.get('format') in ('number', 'bigint') else r['value']
            if tag in ('fields', 'record'): return {k: build(v) for k, v in r['fields'].items()}
            if tag in ('list', 'set'): return [build(x) for x in r['items']]
            if tag == 'named': return build(r['input'])
            if tag == 'sum': return {'variant': r['variant'], **({'payload': build(r['payload'])} if 'payload' in r else {})}
            require(tag == 'bad', 'unknown fact recipe')
            base, mode, field = build(r['base']), r['mode'], r.get('field', 'variant')
            if mode in ('frozen', 'null-prototype'): return base
            constants = {'null': None, 'undefined': object(), 'number': 0, 'boolean': False,
                         'string': 'invalid', 'array': [], 'object': {}, 'negative': '-1',
                         'overflow': '18446744073709551616', 'padded': '01', 'unsafe': 9007199254740992.0,
                         'fraction': 1.5, 'nan': float('nan'), 'infinity': float('inf')}
            if mode in constants: return constants[mode]
            if mode == 'coercion': return HostileScalar()
            if mode in ('getter', 'non-enumerable', 'inherited'): return HostileDict(base)
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
            if mode in ('collection-extra', 'collection-symbol', 'collection-inherited', 'sparse', 'collection-getter', 'collection-hidden'): return HostileList(base)
            if mode == 'duplicate': return [*base, base[0]]
            raise ValueError('unknown native invalid recipe:' + mode)

        def view(v):
            if v is None: return ['null']
            if type(v) is bool: return ['boolean', 'true' if v else 'false']
            if type(v) is int: return ['bigint', str(v)]
            if type(v) is str: return ['string', v]
            if type(v) is tuple: return ['array', [view(x) for x in v]]
            require(type(v) is Fact, 'non-native fact result')
            require(type(v.entries) is tuple, 'mutable fact entries')
            return ['record', [[k, view(x)] for k, x in sorted(v.entries, key=lambda p: p[0].encode('utf-16-be', 'surrogatepass'))]]

        for case in row['cases']:
            arg = build({'tag': 'ref', 'value': case['values'][0]})
            before = fingerprint(arg)
            touches.clear()
            try:
                if row['kind'] == 'Query':
                    output = call(arg['rows'], arg['parameters'])
                    require(type(output) is tuple and all(type(r) is Fact for r in output), 'Query native result')
                    observed = {'kind': 'value', 'value': [[[name, view(r[name])] for name in contract['projection']] for r in output]}
                elif row['kind'] == 'Mapping':
                    output = call(arg)
                    require(type(output) is Fact, 'Mapping native result')
                    observed = {'kind': 'value', 'value': [[name, view(value)] for name, value in output.entries]}
                else:
                    output = call(arg)
                    require(type(output) is (bool if row['kind'] == 'Rule' else str), 'decision native result')
                    observed = {'kind': 'value', 'value': ('true' if output else 'false') if row['kind'] == 'Rule' else output}
            except (TypeError, ValueError) as error:
                observed = {'kind': 'error', 'name': type(error).__name__, 'message': str(error)}
                # The accepted Python Rule runtime exposes these finer-grained
                # input errors. Preserve that API; compare only this closed set
                # with the shared language-independent malformed-input outcome.
                if row['kind'] == 'Rule' and type(error) is TypeError and str(error) in ('INVALID_STRING', 'INVALID_BOOL', 'INVALID_UINT64', 'INVALID_COLLECTION', 'DUPLICATE_SET_VALUE'):
                    observed['message'] = 'RULE_INPUT'
            expected = dict(case['expected'])
            if expected['kind'] == 'value' and row['kind'] in ('Query', 'Mapping'): expected['value'] = json.loads(expected['value'])
            require(observed == expected, 'outcome:' + row['selector'] + ':' + case['id'] + ':' + repr(observed)[:512] + ':expected:' + repr(expected)[:512])
            require(not touches and fingerprint(arg) == before, 'input mutation/coercion')
        provider_path = module.get('provider_path', module['relative_path'])
        original = ast.parse((root / provider_path).read_bytes())
        for mutation in ('return', 'statement'):
            tree = copy.deepcopy(original)
            fn = tree.body[-1]
            if mutation == 'return':
                returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
                require(bool(returns), 'provider return required')
                returns[0].value = ast.Constant(value=None)
            else:
                fn.body.insert(0, ast.Pass())
            ast.fix_missing_locations(tree)
            mutant = ast.unparse(tree).encode()
            compile(mutant, provider_path, 'exec', dont_inherit=True)
            changed = copy.deepcopy(module)
            if row['kind'] != 'Rule': changed['descriptor']['provider']['sha256'] = hashlib.sha256(mutant).hexdigest()
            try: observe(changed, mutant)
            except ValueError as error: require(any(s in str(error) for s in ('semantics or effects', 'Rule semantics/effects')), 'nonsemantic mutant rejection')
            else: raise ValueError('compiling data substitution survived')
        by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                      'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': binding_controls, 'compiling_substitutions': 2}
    require(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in result['toolchain_files'].items()), 'toolchain changed after data execution')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
