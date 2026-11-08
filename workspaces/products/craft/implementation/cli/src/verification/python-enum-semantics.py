"""Execute source-predicted native nominal Enums after whole-module observation."""
import ast
import copy
import enum
import hashlib
import importlib
import json
import pathlib
import sys
import types


def require(ok, why):
    if not ok:
        raise ValueError('PYTHON_ENUM_SEMANTICS:' + why)


def run(data, predecessor, observer):
    controls, root = data['controls'], pathlib.Path(data['root']).resolve(strict=True)
    # A view, not a second workspace or interpreter; every predecessor row and
    # final source/toolchain/cleanup invalidation remains in the enclosing stage.
    earlier = {**data, 'controls': {**controls, 'rows': [r if r['kind'] != 'Enum' else {**r, 'state': 'not_evaluable'} for r in controls['rows']]}}
    result = predecessor(earlier)
    by_selector = {r['selector']: r for r in result['rows']}
    for row in controls['rows']:
        if row['kind'] != 'Enum' or row['state'] != 'ready':
            continue
        require(row['adapter'] == 'python-plain-enum', 'unsupported Enum adapter')
        m = row['module']
        observer(root, m, row['contract'])
        module = importlib.import_module(m['relative_path'][:-3].replace('/', '.'))
        require(pathlib.Path(module.__file__).resolve() == root / m['relative_path'], 'module identity')
        kind = getattr(module, m['symbol'])
        parse, emit, member_id = (getattr(module, name) for name in ('parse_' + m['callable_stem'], 'emit_' + m['callable_stem'], m['callable_stem'] + '_member_id'))
        names = sorted(v['name'] for v in row['contract']['variants'])
        first = parse(names[0])
        source = (root / m['relative_path']).read_bytes()
        foreign_module = types.ModuleType('enum_semantic_foreign')
        exec(compile(source, m['relative_path'], 'exec', dont_inherit=True), foreign_module.__dict__)
        foreign = getattr(foreign_module, 'parse_' + m['callable_stem'])(names[0])
        string_enum = enum.Enum('ForeignString', {'Member': names[0]}, type=str).Member
        touches = []

        class Hostile:
            def __str__(self): touches.append('str'); return names[0]
            def __eq__(self, other): touches.append('eq'); return True
            @property
            def variant(self): touches.append('get'); return names[0]

        class Boxed(str):
            def __eq__(self, other): touches.append('eq'); return True
            __hash__ = str.__hash__

        unknown = '__semantic_unknown__'
        while unknown in names: unknown += '_'
        clone = object.__new__(kind)
        inputs = {'unknown': unknown, 'null': None, 'undefined': object(), 'number': 0, 'boolean': False,
                  'boxed': Boxed(names[0]), 'object': {'variant': names[0]}, 'array': [names[0]], 'symbol': object(),
                  'coercion': Hostile(), 'getter': Hostile(), 'foreign': foreign, 'member': first, 'raw': names[0],
                  'plain': {'variant': names[0]}, 'clone': clone, 'string-enum': string_enum}
        for case in row['cases']:
            touches.clear()
            mode = case['mode']
            if mode == 'definition':
                observed = {'names': [v.value for v in kind], 'wire_values': [emit(v) for v in kind],
                            'enum_id': module.ENUM_ID, 'protocol_id': module.PROTOCOL_ID,
                            'nominal': kind.__bases__ == (enum.Enum,), 'aliases': len(kind.__members__) != len(kind)}
            elif mode == 'member':
                name = case['values'][0]
                value = parse(name)
                foreign_value = getattr(foreign_module, 'parse_' + m['callable_stem'])(name)
                observed = {'wire': emit(value), 'ontology_variant': member_id(value), 'stable': value is parse(name),
                            'copy_stable': copy.copy(value) is value and copy.deepcopy(value) is value,
                            'exact_type': type(value) is kind, 'other_members': [value == parse(n) for n in names],
                            'foreign_equal': value == foreign_value or foreign_value == value, 'string_equal': value == name or name == value}
            else:
                arg = inputs[case['values'][0]]
                before = arg.copy() if type(arg) in (dict, list) else None
                if mode == 'invalid-wire':
                    try: parse(arg)
                    except module._EnumWireError as error:
                        detail = error.as_dict()
                        require(type(error) is module._EnumWireError and type(detail) is dict and set(detail) == {'code', 'enum_id', 'wire_value'}, 'wire error shape')
                        observed = {'name': type(error).__name__, 'code': detail['code'], 'enum_id': detail['enum_id'], 'input_preserved': detail['wire_value'] is arg and error.wire_value is arg}
                    else: raise ValueError('invalid wire accepted')
                else:
                    require(mode == 'unowned', 'unknown control mode')
                    observed = {'input_preserved': True}
                    for key, action in [('emit', emit), ('member_id', member_id)]:
                        try: action(arg)
                        except module._EnumMemberError as error:
                            require(type(error) is module._EnumMemberError and error.enum_id == row['selector'], 'member error shape')
                            observed[key] = error.code
                            observed['input_preserved'] &= error.member is arg
                        else: raise ValueError('unowned member accepted')
                require(before is None or arg == before, 'input mutation')
            require(not touches, 'hostile input evaluated')
            require(observed == json.loads(case['expected']['value']), 'outcome:' + row['selector'] + ':' + case['id'])
        # Native Enum protects declared membership, not arbitrary attributes on
        # member instances. Do not report an invented frozen-component protocol.
        for action in [lambda: setattr(kind, first.name, foreign), lambda: delattr(kind, first.name), lambda: kind.__members__.__setitem__(first.name, foreign)]:
            try: action()
            except (AttributeError, TypeError): pass
            else: raise ValueError('mutable Enum membership')
        for mutation in ('return', 'statement'):
            tree = ast.parse(source)
            fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'emit_' + m['callable_stem'])
            if mutation == 'return':
                next(n for n in ast.walk(fn) if isinstance(n, ast.Return)).value = ast.Constant(value='__wrong__')
            else:
                tree.body.append(ast.Pass())
            ast.fix_missing_locations(tree)
            mutant = ast.unparse(tree).encode()
            compile(mutant, m['relative_path'], 'exec', dont_inherit=True)
            try: observer(root, m, row['contract'], mutant)
            except ValueError as error: require('Enum semantics/effects' in str(error), 'nonsemantic mutant rejection')
            else: raise ValueError('compiling Enum substitution survived')
        by_selector[row['selector']] = {'selector': row['selector'], 'kind': row['kind'], 'result': 'pass', 'executed': True,
                                      'case_count': len(row['cases']), 'native_form': 'pass', 'binding_controls': 3, 'compiling_substitutions': 2}
    require(all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in result['toolchain_files'].items()), 'toolchain changed after Enum execution')
    return {**result, 'rows': [by_selector[r['selector']] for r in controls['rows']]}
