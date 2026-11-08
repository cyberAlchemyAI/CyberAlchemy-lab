"""One exact AST projection: wire row paths only; physical custody unchanged."""
import ast
import copy
import hashlib

BASE_SHA = 'b0780752a5cd18ad58adb2a735a69ca482479be1974f8a18a6bf805713409816'


def project(raw):
    if type(raw) is not bytes or hashlib.sha256(raw).hexdigest() != BASE_SHA:
        raise RuntimeError('WRITER_PREIMAGE')
    tree = ast.parse(raw)
    original = ast.dump(tree, include_attributes=False)
    writer = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Writer')
    emit = next(n for n in writer.body if isinstance(n, ast.FunctionDef) and n.name == 'emit')
    targets = [n for n in ast.walk(emit) if isinstance(n, ast.Attribute) and
               isinstance(n.value, ast.Name) and n.value.id == 'self' and n.attr == 'out']
    if len(targets) != 1:
        raise RuntimeError('WRITER_ROW_SITE')
    targets[0].attr = 'wire_out'
    inverse = copy.deepcopy(tree)
    restored = [n for n in ast.walk(inverse) if isinstance(n, ast.Attribute) and
                isinstance(n.value, ast.Name) and n.value.id == 'self' and n.attr == 'wire_out']
    if len(restored) != 1:
        raise RuntimeError('WRITER_INVERSE_SITE')
    restored[0].attr = 'out'
    if ast.dump(inverse, include_attributes=False) != original:
        raise RuntimeError('WRITER_INVERSE')
    return (ast.unparse(tree) + '\n').encode()
