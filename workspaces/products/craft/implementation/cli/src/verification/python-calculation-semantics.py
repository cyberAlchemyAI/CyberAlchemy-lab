"""Bounded source-driven Calculation execution; appended to the pinned observer."""
import copy
import dataclasses
import importlib


def run_semantics(data):
    root = pathlib.Path(data['root']).resolve(strict=True)
    controls = data['controls']
    tool_files = {str(pathlib.Path(m.__file__).resolve()): hashlib.sha256(pathlib.Path(m.__file__).read_bytes()).hexdigest()
                  for m in list(sys.modules.values()) if getattr(m, '__file__', None)
                  and pathlib.Path(m.__file__).is_file()}
    sys.path.insert(0, str(root))
    rows = []
    touches = []

    class ActiveInt(int):
        def __int__(self):
            touches.append('int')
            return 1

    class ActiveStr(str):
        def __eq__(self, other):
            touches.append('eq')
            return True
        __hash__ = str.__hash__

    class ActiveDict(dict):
        def __getitem__(self, key):
            touches.append('get')
            return 1

    bad = {'negative': -1, 'overflow': 18446744073709551616, 'padded': '01',
           'decimal': '1.0', 'signed': '+1', 'empty': '', 'nan': float('nan'),
           'infinity': float('inf'), 'float': 1.0, 'fraction': 1.5, 'null': None,
           'boolean': True, 'int-subclass': ActiveInt(1), 'str-subclass': ActiveStr('1'),
           'unicode': '١', 'newline': '1\n', 'mapping': {}, 'array': []}
    for row in controls['rows']:
        if row['state'] != 'ready':
            rows.append({'selector': row['selector'], 'kind': row['kind'], 'result': 'not_evaluable', 'executed': False})
            continue
        module, contract = row['module'], row['contract']
        observe(root, module, contract, controls['support_path'])
        loaded = importlib.import_module(module['import_name'])
        require(pathlib.Path(loaded.__file__).resolve() == root / module['relative_path'], 'semantic module identity')
        call = getattr(loaded, module['callable'])
        require(dataclasses.is_dataclass(call), 'native bound Calculation')
        for action in [lambda: setattr(call, 'descriptor', {}), lambda: setattr(call, 'replacement', 1), lambda: call.descriptor.__setitem__('selector', 'changed')]:
            try:
                action()
            except (AttributeError, TypeError):
                pass
            else:
                raise ValueError('mutable Calculation binding')
        for case in row['cases']:
            values = [int(v) if case['format'] == 'int' else v for v in case['values']]
            if 'bad' in case:
                values[case['bad']['index']] = bad[case['bad']['kind']]
            names = [p['name'] for p in contract['inputs']]
            arg = dict(zip(names, values))
            mode = case['mode']
            if mode == 'null': arg = None
            elif mode == 'array': arg = values
            elif mode == 'extra':
                extra = '__unselected__'
                while extra in arg: extra += '_'
                arg[extra] = 0
            elif mode == 'missing': del arg[names[0]]
            elif mode == 'subclass': arg = ActiveDict(arg)
            elif mode == 'key-subclass': arg = {ActiveStr(k): v for k, v in arg.items()}
            touches.clear()
            try:
                result = call(arg)
                require(type(result) is int, 'native result is not exact int')
                observed = {'kind': 'value', 'value': str(result)}
            except (TypeError, ValueError) as error:
                observed = {'kind': 'error', 'name': type(error).__name__, 'message': str(error)}
            expected = dict(case['expected'])
            if expected.get('name') == 'RangeError': expected['name'] = 'ValueError'
            require(observed == expected, 'semantic outcome:' + row['selector'] + ':' + case['id'])
            require(not touches, 'hostile coercion executed')
        original = ast.parse((root / module['provider_path']).read_bytes())
        for mutation in ['boolean-return', 'extra-statement']:
            tree = copy.deepcopy(original)
            fn = tree.body[-1]
            if mutation == 'boolean-return': fn.body[-1] = ast.Return(value=ast.Constant(value=True))
            else: fn.body.insert(-1, ast.Pass())
            ast.fix_missing_locations(tree)
            mutant = ast.unparse(tree).encode()
            compile(mutant, module['provider_path'], 'exec', dont_inherit=True)
            changed = copy.deepcopy(module)
            changed['descriptor']['provider']['sha256'] = hashlib.sha256(mutant).hexdigest()
            try:
                observe(root, changed, contract, controls['support_path'], mutant)
            except ValueError as error:
                require(str(error).startswith(('PYTHON_CALCULATION_OBSERVER:operand', 'PYTHON_CALCULATION_OBSERVER:instruction order')), 'mutant rejected for nonsemantic reason')
            else:
                raise ValueError('compiling substitution survived')
        rows.append({'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                     'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2})
    require(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in tool_files.items()), 'semantic toolchain changed')
    return {'schema_version': 'domainspec.python-semantic-observation/v1-candidate',
            'controls_sha256': controls['controls_sha256'], 'rows': rows, 'toolchain_files': tool_files}


if __name__ == '__main__':
    print(json.dumps(run_semantics(json.load(sys.stdin)), sort_keys=True, separators=(',', ':')))
