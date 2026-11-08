"""Inert, exact-preimage Context AST projection for reviewed v2 spans.

This emits code referencing an unimplemented Context bridge. It intentionally
leaves private-root effect refusals intact and cannot run a Context build.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import re

MAX_SOURCE = 256 * 1024
BRIDGE = '_t35_context_bridge_0001'
IMPORT_BUILD = ('from _t35_context_bridge_0001 import '
                '_ctx_prepare_package, _ctx_emit, _ctx_provision')
IMPORT_GENERATION = 'from _t35_context_bridge_0001 import _ctx_native_read'
OLD_SPANS = {
    'prepare': '5bd9e120a6afef61ebe5e36704d6a0c70b3c45ab29617cfa5c1d33aba63eb081',
    'emit': 'c2f71d902f1dde0ae68262cebc9d3c091b6e675c829df3d3dc2fb1b793dc4cb6',
    'provision': '35f17e44bbb205c3f24d2b4ce127c0a17c67e5b1d7dfa5e1748dc7ea54b3782f',
    'native': 'd6372f2acf5d09da9aa6bf1e55c893eb155af17756a092c86191102d2b4d67f0',
}
NEW_TEXT = {
    'prepare': '_ctx_prepare_package(out)',
    'emit': '_ctx_emit(p, encoded(value) if raw is None else raw)',
    'provision': '_ctx_provision(path, encoded(policy))',
    'native': "output = _ctx_native_read([p.parent / 'semantic', p.parent / 'governance', p.parent / 'request.json'])",
}
NEW_SPANS = {
    'prepare': '66ac333239256a2993fb0f7faa478be3575dfd46a759ff9c36303c59bcedb29a',
    'emit': '80547ec6827c12247a4c828db22caa70a95b321f11e9faafb1694809a8a69ef7',
    'provision': '9bb14702ec87398d32550108d38e8fa742f792624aa6a2220fe308be627a8dc1',
    'native': 'ef72768d9adb368a46c5568dad67e8f0746f5786ced4ea9e55997b6c40b1d7b0',
}


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(node):
    return ast.dump(node, include_attributes=False)


def span_sha(nodes):
    return sha(dump(ast.Module(body=nodes, type_ignores=[])).encode())


def parse(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE, 'SOURCE_BOUND')
    try:
        return ast.parse(raw.decode('utf-8'))
    except (SyntaxError, UnicodeError, ValueError, RecursionError):
        raise Refusal('SOURCE_SYNTAX') from None


def function(tree, name):
    found = [x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == name]
    need(len(found) == 1, 'FUNCTION_SHAPE')
    return found[0]


def count_calls(tree, name):
    return sum(isinstance(x, ast.Call) and isinstance(x.func, ast.Name)
               and x.func.id == name for x in ast.walk(tree))


def _replacement(name):
    rows = ast.parse(NEW_TEXT[name]).body
    need(len(rows) == 1 and span_sha(rows) == NEW_SPANS[name], 'NEW_SPAN_DRIFT')
    return rows


def _import(tree, text):
    row = ast.parse(text).body[0]
    need(not any(isinstance(x, ast.ImportFrom) and x.module == BRIDGE
                 for x in tree.body), 'BRIDGE_IMPORT_COLLISION')
    index = 1 if (tree.body and isinstance(tree.body[0], ast.Expr)
                  and isinstance(tree.body[0].value, ast.Constant)
                  and type(tree.body[0].value.value) is str) else 0
    while (index < len(tree.body) and isinstance(tree.body[index], ast.ImportFrom)
           and tree.body[index].module == '__future__'):
        index += 1
    tree.body.insert(index, row)
    return index


def _pinned(raw, expected_sha256):
    need(type(expected_sha256) is str and
         re.fullmatch(r'[0-9a-f]{64}', expected_sha256) is not None and
         type(raw) is bytes and sha(raw) == expected_sha256,
         'PREIMAGE_DRIFT')
    return parse(raw)


def _build(tree):
    original = copy.deepcopy(tree)
    build, emit, provision = (function(tree, name)
                              for name in ('build', 'emit', 'provision'))
    need(len(build.body) >= 6 and len(emit.body) == 4 and
         len(provision.body) == 9 and count_calls(tree, '_t35_effect_refused') == 6,
         'BUILD_TOPOLOGY')
    need(ast.unparse(build.body[0]) == 'verify_source(source_pin)' and
         ast.unparse(build.body[1]) == "out = HERE / 'packages/0001'" and
         ast.unparse(build.body[4]) == 'started = time.monotonic()',
         'BUILD_PREFIX')
    need(ast.unparse(emit.body[0]) ==
         "require(p.is_relative_to(HERE / 'packages') or p.is_relative_to(HERE / 'receipts'), 'delivery output boundary escaped')",
         'EMIT_BOUNDARY')
    need(ast.unparse(provision.body[8]) == 'return (key, sha(path.read_bytes()))',
         'PROVISION_READBACK')
    spans = {'prepare': (build.body, 2, 4),
             'emit': (emit.body, 1, 4),
             'provision': (provision.body, 6, 8)}
    record = {}
    for name, (body, first, end) in spans.items():
        need(span_sha(body[first:end]) == OLD_SPANS[name], name.upper() + '_PREIMAGE')
        record[name] = {'function': 'build' if name == 'prepare' else name,
                        'slice': [first, end], 'old_span_sha256': OLD_SPANS[name],
                        'new_span_sha256': NEW_SPANS[name]}
        body[first:end] = _replacement(name)
    import_index = _import(tree, IMPORT_BUILD)
    ast.fix_missing_locations(tree)
    inverse = copy.deepcopy(tree)
    del inverse.body[import_index]
    for name, (fn, first, end) in {
        'prepare': ('build', 2, 4), 'emit': ('emit', 1, 4),
        'provision': ('provision', 6, 8),
    }.items():
        previous = function(original, fn).body[first:end]
        function(inverse, fn).body[first:first + 1] = copy.deepcopy(previous)
    need(dump(inverse) == dump(original), 'INVERSE_DIFF')
    need(count_calls(tree, '_t35_effect_refused') == 2 and
         ast.unparse(function(tree, 'provision').body[-1]) ==
         'return (key, sha(path.read_bytes()))', 'NONSELECTED_GUARD_DRIFT')
    return {'spans': record, 'remaining_refusals': 2,
            'unimplemented_private_root': True}


def _generation(tree):
    original = copy.deepcopy(tree)
    selected = function(tree, 'selected_mapping')
    need(len(selected.body) == 9 and count_calls(tree, '_t35_effect_refused') == 0,
         'GENERATION_TOPOLOGY')
    need(span_sha(selected.body[6:7]) == OLD_SPANS['native'] and
         ast.unparse(selected.body[7]) ==
         "require(output == (p.parent / 'native-output.json').read_bytes(), 'actual cold native projection differs')",
         'NATIVE_PREIMAGE')
    selected.body[6:7] = _replacement('native')
    import_index = _import(tree, IMPORT_GENERATION)
    ast.fix_missing_locations(tree)
    inverse = copy.deepcopy(tree)
    del inverse.body[import_index]
    function(inverse, 'selected_mapping').body[6:7] = copy.deepcopy(
        function(original, 'selected_mapping').body[6:7])
    need(dump(inverse) == dump(original), 'INVERSE_DIFF')
    need(not any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                 and isinstance(x.func.value, ast.Name) and x.func.value.id == 'MAPPED'
                 and x.func.attr == 'call' for x in ast.walk(tree)),
         'NATIVE_CALL_REMAINS')
    return {'spans': {'native': {'function': 'selected_mapping', 'slice': [6, 7],
                                 'old_span_sha256': OLD_SPANS['native'],
                                 'new_span_sha256': NEW_SPANS['native']}},
            'remaining_refusals': 0}


def adapt(raw, *, role, expected_preimage_sha256):
    """Return inert postimage and exact inverse-diff evidence for one role."""
    need(role in ('build', 'generation'), 'ROLE_REFUSED')
    tree = _pinned(raw, expected_preimage_sha256)
    original_ast_sha = sha(dump(tree).encode())
    record = _build(tree) if role == 'build' else _generation(tree)
    output = (ast.unparse(tree) + '\n').encode()
    need(len(output) <= MAX_SOURCE and dump(parse(output)) == dump(tree),
         'POSTIMAGE_DRIFT')
    compile(output, '<context-inert-' + role + '>', 'exec', optimize=0)
    compile(output, '<context-inert-' + role + '>', 'exec', optimize=2)
    record.update(schema_version='lab-context-ast-projection/v1-inert',
                  role=role, authority_effect='none', effect_ready=False,
                  preimage_sha256=expected_preimage_sha256,
                  preimage_ast_sha256=original_ast_sha,
                  postimage_sha256=sha(output),
                  postimage_ast_sha256=sha(dump(parse(output)).encode()))
    return output, record


def verify_postimage(preimage, postimage, *, role, expected_preimage_sha256):
    expected, record = adapt(preimage, role=role,
                             expected_preimage_sha256=expected_preimage_sha256)
    need(type(postimage) is bytes and postimage == expected, 'POSTIMAGE_DRIFT')
    return record
