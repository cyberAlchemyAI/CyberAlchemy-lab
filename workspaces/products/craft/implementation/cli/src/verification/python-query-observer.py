"""Independent checked-source/closed-Python Query observer; no target execution."""
import ast
import hashlib
import json
import pathlib
import re
import sys

SUPPORT = {"values.py": "01e2b483f8ab8d56499557430763ff351c08aac6c5a579a7c3d97a30922daa5d", "facts.py": "1d20d280ed71456e1f4cb57afa339df0b1c56c81b74772c0c3a08a2b4b828c8b"}


def require(ok, reason):
    if not ok: raise ValueError("PYTHON_QUERY_OBSERVER:" + reason)


def dump(node): return ast.dump(node, include_attributes=False)


def frozen(node):
    if isinstance(node, ast.Constant) and type(node.value) in (str, int, bool, type(None)): return node.value
    if isinstance(node, ast.Tuple): return [frozen(n) for n in node.elts]
    require(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == '_MappingProxyType' and len(node.args) == 1 and not node.keywords and isinstance(node.args[0], ast.Dict), 'immutable descriptor')
    body = node.args[0]
    keys = [frozen(n) for n in body.keys]
    require(all(type(k) is str for k in keys) and len(set(keys)) == len(keys), 'descriptor keys')
    return dict(zip(keys, [frozen(n) for n in body.values]))


def observe(root, module, contract, model, runtime_dir, provider_override=None):
    provider = (root / module['provider_path']).read_bytes() if provider_override is None else provider_override
    require(hashlib.sha256(provider).hexdigest() == module['descriptor']['provider']['sha256'], 'provider digest')
    require(sorted(e['id'] for e in module['descriptor']['runtime']) == sorted(SUPPORT), 'runtime bindings')
    for entry in module['descriptor']['runtime']:
        require(hashlib.sha256((root / runtime_dir / entry['id']).read_bytes()).hexdigest() == SUPPORT[entry['id']] == entry['sha256'], 'support perimeter')
    tree = ast.parse(provider)
    source = pathlib.PurePosixPath(module['provider_path']).parent.parts
    target = pathlib.PurePosixPath(runtime_dir).parts
    common = 0
    while common < min(len(source), len(target)) and source[common] == target[common]: common += 1
    runtime_import = '.' * (len(source) - common + 1) + '.'.join(target[common:])
    imports = ast.parse('from __future__ import annotations\nfrom typing import Literal as _Literal, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast\nfrom ' + runtime_import + ' import values as _v, facts as _facts\nfrom codecs import lookup as _lookup_codec\n_lookup_codec("utf-16-le")\n_lookup_codec("utf-16-be")').body
    require([dump(n) for n in tree.body[:6]] == [dump(n) for n in imports], 'imports and codec initialization')
    declarations = {d['selector']: d for d in model['declarations']}
    protocols = {}

    def literal(node): return ast.literal_eval(node)
    def ref(node):
        require(isinstance(node, ast.Name) and node.id in protocols, 'protocol dependency')
        return protocols[node.id]
    def protocol(node):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == '_v':
            scalar = {'STRING': 'String', 'BOOL': 'Bool', 'UINT64': 'UInt64'}
            require(node.attr in scalar, 'scalar protocol')
            return {'kind': 'scalar', 'name': scalar[node.attr]}
        require(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == '_facts' and not node.keywords, 'protocol assembly')
        name, args = node.func.attr, node.args
        if name == 'optional_fact':
            require(len(args) == 1, 'optional protocol')
            return {'kind': 'optional', 'element': ref(args[0])}
        if name == 'sequence_fact':
            require(len(args) == 2 and type(literal(args[1])) is bool, 'collection protocol')
            return {'kind': 'set' if literal(args[1]) else 'list', 'element': ref(args[0])}
        if name == 'sum_fact':
            require(len(args) == 1 and isinstance(args[0], ast.Dict), 'sum protocol')
            return {'kind': 'sum', 'variants': {literal(k): None if isinstance(v, ast.Constant) and v.value is None else ref(v) for k, v in zip(args[0].keys, args[0].values)}}
        if name == 'named_sum_fact':
            require(len(args) == 2, 'named sum protocol')
            selector = literal(args[0]); d = declarations[selector]
            expected = {'kind': 'sum', 'variants': {v['name']: semantic(v['payload']) if v['payload'] else None for v in d['contract']['variants']}}
            require(d['kind'] == 'Enum' and ref(args[1]) == expected, 'named sum binding')
            return {'kind': 'named', 'selector': selector}
        require(name == 'record_fact' and len(args) == 4, 'record protocol')
        kind, selector = literal(args[0]), literal(args[1]); d = declarations[selector]
        fields = sorted(d['contract']['properties'], key=lambda f: f['name'])
        require(isinstance(args[2], ast.Tuple), 'record fields')
        actual = [(literal(n.elts[0]), ref(n.elts[1]), literal(n.elts[2])) for n in args[2].elts]
        expected = [(f['name'], semantic(f['type']), f['type']['kind'] == 'optional') for f in fields]
        identity = tuple(f['name'] for f in fields if kind != 'Entity' or f['identity'])
        require(kind == d['kind'] and actual == expected and literal(args[3]) == identity, 'record fields and identity')
        return {'kind': 'named', 'selector': selector}

    def semantic(t):
        if t['kind'] == 'sum': return {'kind': 'sum', 'variants': {v['name']: semantic(v['payload']) if v['payload'] else None for v in t['variants']}}
        if t['kind'] in ('list', 'set', 'optional'): return {'kind': t['kind'], 'element': semantic(t['element'])}
        return t

    # Typing declarations may contain type expressions and stub methods only.
    type_names = {'int', 'str', 'bool', 'object', 'list', 'tuple', '_Literal', '_NotRequired'}
    declared = set()
    def type_expr(node):
        allowed = (ast.Name, ast.Constant, ast.Subscript, ast.BinOp, ast.BitOr, ast.Tuple, ast.Load)
        require(all(isinstance(n, allowed) for n in ast.walk(node)), 'type expression')
        require(all(n.id in type_names for n in ast.walk(node) if isinstance(n, ast.Name)), 'undeclared type read')
    for node in tree.body[6:-1]:
        if isinstance(node, ast.Assign):
            require(len(node.targets) == 1 and isinstance(node.targets[0], ast.Name), 'declaration')
            name = node.targets[0].id
            require(name not in declared, 'duplicate declaration')
            declared.add(name)
            if name.startswith('_fact_type'):
                require(name == '_fact_type' + str(len(protocols)), 'protocol declaration order')
                protocols[name] = protocol(node.value)
            elif isinstance(node.value, ast.Call):
                require(re.fullmatch(r'_Shape[0-9]+(?:Case[0-9]+)?Input|_ReadModelInput|_Parameters', name), 'input type name')
                require(isinstance(node.value.func, ast.Name) and node.value.func.id == '_TypedDict' and len(node.value.args) == 2 and not node.value.keywords and isinstance(node.value.args[1], ast.Dict), 'typed input')
                require(literal(node.value.args[0]) == name, 'type name')
                for k, v in zip(node.value.args[1].keys, node.value.args[1].values): require(type(literal(k)) is str, 'field name'); type_expr(v)
                type_names.add(name)
            else:
                require(name == '_RowsInput', 'unexpected alias')
                type_expr(node.value); type_names.add(name)
        elif isinstance(node, ast.ClassDef):
            require(re.fullmatch(r'_Shape[0-9]+(?:Case[0-9]+)?|_ReadModel', node.name) and node.name not in declared, 'read type name')
            declared.add(node.name); type_names.add(node.name)
            require(len(node.bases) == 1 and isinstance(node.bases[0], ast.Name) and node.bases[0].id == '_Protocol' and not node.keywords and not node.decorator_list and not node.type_params, 'read protocol')
            for method in node.body:
                if isinstance(method, ast.Pass): continue
                require(isinstance(method, ast.FunctionDef) and method.name == '__getitem__' and len(method.body) == 1 and isinstance(method.body[0], ast.Expr) and isinstance(method.body[0].value, ast.Constant) and method.body[0].value.value is Ellipsis, 'protocol stub')
                require(all(isinstance(n, ast.Name) and n.id == '_overload' for n in method.decorator_list), 'protocol decorators')
                require(not method.type_params and [a.arg for a in method.args.args] == ['self', 'key'] and not method.args.posonlyargs and not method.args.kwonlyargs and not method.args.defaults and not method.args.kw_defaults and not method.args.vararg and not method.args.kwarg, 'protocol arguments')
                for a in method.args.args:
                    if a.annotation: type_expr(a.annotation)
                type_expr(method.returns)
        else: require(False, 'unexpected prelude effect')
    def protocol_name(t):
        matches = [name for name, value in protocols.items() if value == semantic(t)]
        require(len(matches) == 1, 'exact value protocol')
        return matches[0]
    source_fields = {f['name']: f['type'] for f in declarations[contract['source']]['contract']['properties']}
    def value(v):
        if v['kind'] == 'field': return source_fields[v['name']], 'row[' + repr(v['name']) + ']'
        if v['kind'] == 'parameter':
            i = next(i for i, p in enumerate(contract['inputs']) if p['name'] == v['name'])
            return contract['inputs'][i]['type'], 'p' + str(i)
        t = {'kind': 'scalar', 'name': v['type']}
        return t, '_v.STRING.normalize(' + repr(v['value']) + ')' if v['type'] == 'String' else repr(v['value'])
    def order(code, t):
        require(t['kind'] == 'scalar', 'scalar ordering')
        return code + '.encode("utf-16-be", "surrogatepass")' if t['name'] == 'String' else code
    def predicate(e):
        if e['op'] in ('all', 'any'): return '(' + (' and ' if e['op'] == 'all' else ' or ').join(predicate(t) for t in e['terms']) + ')'
        if e['op'] == 'not': return '(not ' + predicate(e['term']) + ')'
        lt, left = value(e['left']); rt, right = value(e['right']); require(lt == rt, 'operand types')
        if e['op'] == 'eq': return '(' + protocol_name(lt) + '.key(' + left + ') == ' + protocol_name(rt) + '.key(' + right + '))'
        return '(' + order(left, lt) + ' ' + {'lt': '<', 'lte': '<=', 'gt': '>', 'gte': '>='}[e['op']] + ' ' + order(right, rt) + ')'
    names = [p['name'] for p in contract['inputs']]
    expected = 'def query(rows: _RowsInput, parameters: _Parameters) -> tuple[_ReadModel, ...]:\n    try:\n'
    expected += '        if type(parameters) is not dict or len(parameters) != ' + str(len(names)) + ' or any(type(key) is not str for key in parameters):\n            raise TypeError("QUERY_INPUT")\n'
    expected += '        if any(key not in ' + repr(tuple(names)) + ' for key in parameters):\n            raise TypeError("QUERY_INPUT")\n'
    for i, p in enumerate(contract['inputs']): expected += '        p' + str(i) + ' = ' + protocol_name(p['type']) + '.normalize(parameters[' + repr(p['name']) + '])\n'
    expected += '        snapshots = ' + protocol_name({'kind': 'list', 'element': {'kind': 'named', 'selector': contract['source']}}) + '.normalize(rows)\n'
    expected += '        selected = [row for row in snapshots if ' + (predicate(contract['filter']) if contract['filter'] else 'True') + ']\n'
    if contract['order_by']:
        ordering = contract['order_by']; expected += '        selected.sort(key=lambda row: ' + order('row[' + repr(ordering['field']) + ']', source_fields[ordering['field']]) + ', reverse=' + str(ordering['direction'] == 'desc') + ')\n'
    if contract['limit'] is not None: expected += '        selected = selected[:' + str(contract['limit']) + ']\n'
    expected += '        return tuple(_cast(_ReadModel, _facts._Fact((' + ''.join('(' + repr(n) + ', row[' + repr(n) + ']),' for n in contract['projection']) + '))) for row in selected)\n'
    expected += '    except (TypeError, ValueError, KeyError):\n        raise TypeError("QUERY_INPUT") from None\n'
    require(dump(tree.body[-1]) == dump(ast.parse(expected).body[0]), 'query semantics or effects')
    descriptor = module['descriptor']
    require(descriptor['read_targets'] == [{'selector': contract['source'], 'fields': sorted(source_fields)}] and descriptor['result_fields'] == [{'name': n, 'type': source_fields[n]} for n in contract['projection']] and descriptor['inputs'] == contract['inputs'] and descriptor['filter'] == contract['filter'] and descriptor['order_by'] == contract['order_by'] and descriptor['limit'] == contract['limit'], 'source binding')
    wrapper = ast.parse((root / module['relative_path']).read_bytes())
    require(len(wrapper.body) == 8 and isinstance(wrapper.body[4], ast.Assign) and frozen(wrapper.body[4].value) == descriptor, 'descriptor binding')
    wrapper.body[4].value = ast.Constant(None)
    expected = '''from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from PROVIDER import query as _query, _RowsInput, _Parameters, _ReadModel
_DESCRIPTOR = None
@_dataclass(frozen=True, slots=True)
class _BoundQuery:
    @property
    def descriptor(self): return _DESCRIPTOR
    def __call__(self, rows: _RowsInput, parameters: _Parameters) -> tuple[_ReadModel, ...]: return _query(rows, parameters)
CALLABLE = _BoundQuery()
__all__ = ["CALLABLE"]
'''.replace('PROVIDER', module['provider_import']).replace('CALLABLE', module['callable'])
    require(dump(wrapper) == dump(ast.parse(expected)), 'frozen provider binding')


if __name__ == '__main__':
    data = json.load(sys.stdin)
    for module in data['modules']: observe(pathlib.Path(data['root']), module, data['contracts'][module['selector']], data['model'], data['runtime_dir'])
    print(json.dumps({'observed': len(data['modules'])}))
