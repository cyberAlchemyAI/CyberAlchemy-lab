"""Whole-module plain Enum observation from checked source names and IDs.

This verifier never calls or imports a DomainSpec emitter. Complete AST equality
includes error methods, decorators, annotations, branch order and module effects.
"""
import ast
import json
import keyword
import pathlib


def require(ok, why):
    if not ok:
        raise ValueError('PYTHON_ENUM_OBSERVER:' + why)


def observe(root, module, contract, override=None):
    require(all(v['payload'] is None for v in contract['variants']), 'plain Enum required')
    variants = sorted(contract['variants'], key=lambda v: v['name'])
    node = module['selector'].split(':')[1]
    symbol = ''.join(word.capitalize() for word in node.split('-'))
    if keyword.iskeyword(symbol):
        symbol = 'Concept_' + symbol
    stem = node.replace('-', '_')
    require(module['symbol'] == symbol and module['callable_stem'] == stem, 'native names')
    native = lambda name: 'Variant_' + name if keyword.iskeyword(name) else name
    q = lambda value: json.dumps(value, ensure_ascii=True)
    # Static envelope is independently owned by verification. Dynamic branches
    # below bind only authored variant names and ontology IDs.
    expected = '''from __future__ import annotations
import enum as _enum
ENUM_ID = SELECTOR
PROTOCOL_ID = "python.nominal-enum-explicit-wire/v1"
class _EnumWireError(ValueError):
    code = "DOMAINSPEC_ENUM_UNKNOWN_WIRE"
    def __init__(self, wire_value: object):
        self.enum_id = ENUM_ID
        self.wire_value = wire_value
        super().__init__(self.code + ":" + ENUM_ID)
    def as_dict(self) -> dict[str, object]:
        return {"code": self.code, "enum_id": self.enum_id, "wire_value": self.wire_value}
class _EnumMemberError(TypeError):
    code = "DOMAINSPEC_ENUM_MEMBER_INVALID"
    def __init__(self, member: object):
        self.enum_id = ENUM_ID
        self.member = member
        super().__init__(self.code + ":" + ENUM_ID)
'''.replace('SELECTOR', q(module['selector']))
    expected += '@_enum.unique\nclass ' + symbol + '(_enum.Enum):\n'
    expected += ''.join('    ' + native(v['name']) + ' = ' + q(v['name']) + '\n' for v in variants)
    expected += 'def parse_' + stem + '(wire_value: str) -> ' + symbol + ':\n'
    expected += '    if type(wire_value) is not str:\n        raise _EnumWireError(wire_value)\n'
    for v in variants:
        expected += '    if wire_value == ' + q(v['name']) + ':\n        return ' + symbol + '.' + native(v['name']) + '\n'
    expected += '    raise _EnumWireError(wire_value)\n'
    for function, field in [('emit_' + stem, 'name'), (stem + '_member_id', 'ontology_variant')]:
        expected += 'def ' + function + '(member: ' + symbol + ') -> str:\n'
        for v in variants:
            expected += '    if member is ' + symbol + '.' + native(v['name']) + ':\n        return ' + q(v[field]) + '\n'
        expected += '    raise _EnumMemberError(member)\n'
    source = (pathlib.Path(root) / module['relative_path']).read_bytes() if override is None else override
    require(ast.dump(ast.parse(source), include_attributes=False) == ast.dump(ast.parse(expected), include_attributes=False), 'Enum semantics/effects')


if __name__ == '__main__':
    import sys
    data = json.load(sys.stdin)
    observe(data['root'], data['module'], data['contract'])
    print('plain-enum-observed')
