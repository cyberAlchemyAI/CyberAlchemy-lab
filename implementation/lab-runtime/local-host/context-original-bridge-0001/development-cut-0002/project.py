"""Exact public-source projections only. Never import or run original Context."""
import ast
import copy
import hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ORIGINAL = BASE / 'context-construction-0003/rendered/build.py'
ORIGINAL_SHA = 'f465f1f1f8b9c8269935d9590f4a6006633d8c335416e3b46703a6c190e0711b'
BRIDGE = BASE / 'context-bridge-0002/bridge.py'
BRIDGE_SHA = '5bf35088d43f781453ee8f4e9397a033bd2acdd671142a5a7c05adad709bb52a'
OLD_EMIT_SHA = 'c2f71d902f1dde0ae68262cebc9d3c091b6e675c829df3d3dc2fb1b793dc4cb6'


def need(ok, code):
    if not ok:
        raise RuntimeError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(node):
    return ast.dump(node, include_attributes=False)


def span(nodes):
    return ast.Module(body=nodes, type_ignores=[])


def function(tree, name):
    found = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    need(len(found) == 1, 'FUNCTION')
    return found[0]


def expression(text):
    return ast.parse(text).body[0]


def count_refusals(tree):
    return sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and
               n.func.id == '_t35_effect_refused' for n in ast.walk(tree))


def project_build(raw):
    need(type(raw) is bytes and sha(raw) == ORIGINAL_SHA, 'ORIGINAL_PREIMAGE')
    old = ast.parse(raw)
    emit = function(old, 'emit')
    build = function(old, 'build')
    need(len(emit.body) == 4 and sha(dump(span(emit.body[1:])).encode()) == OLD_EMIT_SHA,
         'EMIT_PREIMAGE')
    need(dump(build.body[1]) == dump(expression("out = HERE / 'packages/0001'")) and
         dump(build.body[2]) == dump(expression("require(not out.exists(), 'refuse delivery package overwrite')")) and
         dump(build.body[3]) == dump(expression('_t35_effect_refused()')), 'OUTPUT_PREIMAGE')
    cleanup = expression("require(not root.exists(), 'private host permission root remains')")
    indexes = [i for i, n in enumerate(build.body) if dump(n) == dump(cleanup)]
    need(len(indexes) == 1 and indexes[0] == len(build.body) - 6, 'CLEANUP_PREIMAGE')
    need(isinstance(build.body[-1], ast.Expr) and
         isinstance(build.body[-1].value, ast.Call) and
         dump(build.body[-1].value.func) == dump(ast.Name(id='print', ctx=ast.Load())) and
         count_refusals(old) == 6, 'PRINT_PREIMAGE')
    changed = copy.deepcopy(old)
    function(changed, 'emit').body[1:] = [expression('_ctx_emit(p, encoded(value) if raw is None else raw)')]
    target = function(changed, 'build')
    target.body[3] = expression('_ctx_output_ready(out)')
    target.body.insert(indexes[0] + 1, expression('_ctx_release_private(root)'))
    target.body[-1].value.func = ast.Name(id='_ctx_print', ctx=ast.Load())
    ast.fix_missing_locations(changed)
    inverse = copy.deepcopy(changed)
    function(inverse, 'emit').body[1:] = copy.deepcopy(emit.body[1:])
    back = function(inverse, 'build')
    back.body[3] = copy.deepcopy(build.body[3])
    del back.body[indexes[0] + 1]
    back.body[-1].value.func = ast.Name(id='print', ctx=ast.Load())
    need(dump(inverse) == dump(old), 'FULL_BUILD_INVERSE')
    need(count_refusals(changed) == 3, 'REMAINING_REFUSALS')
    result = (ast.unparse(changed) + '\n').encode()
    return result, {'original_sha256': ORIGINAL_SHA, 'projected_sha256': sha(result),
                    'full_AST_inverse_equal': True, 'original_refusals': 6, 'remaining_refusals': 3,
                    'sites': ['emit three sealed statements', 'sealed output mkdir after original guard',
                              'insert RELEASE after original private-absence assertion', 'original print callee'],
                    'output_assignment_unchanged': True, 'manifest_expression_unchanged': True,
                    'cleanup_assertion_precedes_release': True}


def project_writer(raw):
    need(type(raw) is bytes and sha(raw) == BRIDGE_SHA, 'BRIDGE_PREIMAGE')
    old = ast.parse(raw)
    changed = copy.deepcopy(old)
    writers = [n for n in changed.body if isinstance(n, ast.ClassDef) and n.name == 'Writer']
    need(len(writers) == 1, 'WRITER_CLASS')
    expected = {'__init__': 3, 'check': 1, 'validate_inventory': 1, 'postclose': 2}
    actual = {}
    for method in writers[0].body:
        if isinstance(method, ast.FunctionDef):
            for node in ast.walk(method):
                if isinstance(node, ast.Constant) and node.value == 'package':
                    actual[method.name] = actual.get(method.name, 0) + 1
                    node.value = '0001'
    need(actual == expected, 'SEVEN_LAYOUT_SITES')
    inverse = copy.deepcopy(changed)
    back = next(n for n in inverse.body if isinstance(n, ast.ClassDef) and n.name == 'Writer')
    for node in ast.walk(back):
        if isinstance(node, ast.Constant) and node.value == '0001':
            node.value = 'package'
    need(dump(inverse) == dump(old), 'FULL_WRITER_INVERSE')
    result = (ast.unparse(changed) + '\n').encode()
    return result, {'original_sha256': BRIDGE_SHA, 'projected_sha256': sha(result),
                    'full_AST_inverse_equal': True, 'seven_constant_sites': actual,
                    'only_change': 'Writer physical package basename package -> 0001',
                    'attempt_selection': 'HERE/packages', 'output': 'HERE/packages/0001',
                    'protocol_and_Client_and_fsync_and_close_AST_unchanged': True}
