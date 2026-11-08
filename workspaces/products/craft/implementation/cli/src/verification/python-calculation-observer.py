"""Independent closed-grammar observer; does not import or execute target code."""
import ast
import hashlib
import json
import pathlib
import sys

SUPPORT_SHA256 = "64fb6af38ef6c3d7629d946fe499e35ea3ecea2fe46ca7944e10a508e8090f86"


def require(condition, reason):
    if not condition:
        raise ValueError("PYTHON_CALCULATION_OBSERVER:" + reason)


def dump(node):
    return ast.dump(node, include_attributes=False)


def frozen(node):
    if isinstance(node, ast.Constant) and type(node.value) in (str, int, bool, type(None)):
        return node.value
    if isinstance(node, ast.Tuple):
        return [frozen(n) for n in node.elts]
    require(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_MappingProxyType" and len(node.args) == 1 and not node.keywords, "immutable descriptor")
    value = node.args[0]
    require(isinstance(value, ast.Dict), "descriptor map")
    keys = [frozen(n) for n in value.keys]
    require(all(type(k) is str for k in keys) and len(set(keys)) == len(keys), "descriptor keys")
    return dict(zip(keys, [frozen(n) for n in value.values]))


def observe(root, module, contract, support_path, provider_override=None):
    provider = (root / module["provider_path"]).read_bytes() if provider_override is None else provider_override
    support = (root / support_path).read_bytes()
    descriptor = module["descriptor"]
    require(hashlib.sha256(provider).hexdigest() == descriptor["provider"]["sha256"], "provider digest")
    require(hashlib.sha256(support).hexdigest() == SUPPORT_SHA256 == descriptor["runtime"]["sha256"], "support perimeter")
    require(descriptor["inputs"] == contract["inputs"] and descriptor["result"] == contract["result"] and descriptor["ontology_calculation"] == contract["ontology_calculation"] and descriptor["source_version"] == contract["schema_version"], "source binding")
    tree = ast.parse(provider)
    require(len(tree.body) == 5, "provider grammar")
    # Expected imports are caller-bound paths, not paths advertised by target code.
    source_parts = pathlib.PurePosixPath(module["provider_path"]).parent.parts
    target_parts = pathlib.PurePosixPath(support_path).with_suffix("").parts
    common = 0
    while common < min(len(source_parts), len(target_parts)) and source_parts[common] == target_parts[common]:
        common += 1
    runtime_import = "." * (len(source_parts) - common + 1) + ".".join(target_parts[common:])
    expected_imports = ast.parse("from __future__ import annotations\nfrom typing import TypedDict as _TypedDict\nfrom " + runtime_import + " import _normalize, _inputs, _checked, _divide").body
    require([dump(n) for n in tree.body[:3]] == [dump(n) for n in expected_imports], "imports")
    names = [p["name"] for p in contract["inputs"]]
    typed = ast.parse('_Inputs = _TypedDict("_Inputs", {' + ','.join(repr(n) + ': int | str' for n in names) + '})').body[0]
    require(dump(tree.body[3]) == dump(typed), "typed inputs")
    fn = tree.body[4]
    header = ast.parse('def calculate(input: _Inputs) -> int:\n    pass').body[0]
    require(isinstance(fn, ast.FunctionDef) and fn.name == "calculate" and dump(fn.args) == dump(header.args) and dump(fn.returns) == dump(header.returns) and not fn.decorator_list and not fn.type_params, "callable shape")
    prefix = ast.parse('d = _inputs(input, ' + repr(tuple(names)) + ')\n' + ''.join('p' + str(i) + ' = _normalize(d[' + repr(n) + '])\n' for i, n in enumerate(names))).body
    require([dump(n) for n in fn.body[:len(prefix)]] == [dump(n) for n in prefix], "input normalization")
    env = {'p' + str(i): {"op": "input", "name": n} for i, n in enumerate(names)}
    observed = []

    def operand(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return {"op": "literal", "value": str(node.value)}
        require(isinstance(node, ast.Name) and node.id in env, "operand")
        return env[node.id]

    instructions = fn.body[len(prefix):-1]
    for index, statement in enumerate(instructions):
        require(isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name) and statement.targets[0].id == 'v' + str(index), "instruction order")
        call = statement.value
        require(isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and not call.keywords, "arithmetic call")
        if call.func.id == '_checked':
            require(len(call.args) == 1 and isinstance(call.args[0], ast.BinOp), "checked arithmetic")
            expr = call.args[0]
            ops = {ast.Add: 'add', ast.Sub: 'subtract', ast.Mult: 'multiply'}
            require(type(expr.op) in ops, "operator")
            value = {"op": ops[type(expr.op)], "left": operand(expr.left), "right": operand(expr.right)}
        else:
            require(call.func.id == '_divide' and len(call.args) == 3 and isinstance(call.args[2], ast.Constant) and call.args[2].value == contract['division_rounding'], "division rounding")
            value = {"op": "divide", "left": operand(call.args[0]), "right": operand(call.args[1])}
        observed.append(value)
        env['v' + str(index)] = value
    expected = []

    def authored(expr):
        if expr['op'] == 'literal':
            return {"op": "literal", "value": str(expr['value'])}
        if expr['op'] == 'input':
            return expr
        value = {"op": expr['op'], "left": authored(expr['left']), "right": authored(expr['right'])}
        expected.append(value)
        return value

    expression = authored(contract['expression'])
    require(observed == expected, "authored arithmetic and occurrence order")
    require(isinstance(fn.body[-1], ast.Return) and operand(fn.body[-1].value) == expression, "complete value return")
    wrapper = ast.parse((root / module['relative_path']).read_bytes())
    require(len(wrapper.body) == 8, "binding grammar")
    assignment = wrapper.body[4]
    require(isinstance(assignment, ast.Assign) and len(assignment.targets) == 1 and isinstance(assignment.targets[0], ast.Name) and assignment.targets[0].id == '_DESCRIPTOR' and frozen(assignment.value) == descriptor, "descriptor binding")
    # Erase the separately checked immutable literal and compare the complete facade.
    assignment.value = ast.Constant(None)
    expected_wrapper = ast.parse('''from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from PROVIDER import calculate as _calculate, _Inputs
_DESCRIPTOR = None
@_dataclass(frozen=True, slots=True)
class _BoundCalculation:
    @property
    def descriptor(self):
        return _DESCRIPTOR
    def __call__(self, input: _Inputs) -> int:
        return _calculate(input)
CALLABLE = _BoundCalculation()
__all__ = ["CALLABLE"]
'''.replace('PROVIDER', module['provider_import']).replace('CALLABLE', module['callable']))
    require(dump(wrapper) == dump(expected_wrapper), "frozen provider binding")


if __name__ == '__main__':
    data = json.load(sys.stdin)
    for module in data['modules']:
        observe(pathlib.Path(data['root']), module, data['contracts'][module['selector']], data['support_path'])
    print(json.dumps({"observed": len(data['modules'])}))
