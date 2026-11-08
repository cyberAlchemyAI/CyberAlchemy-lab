"""Second inert Context AST projection: exact private-root lifecycle sites.

Input is the externally selected v1 build postimage. The named bridge does
not exist; this module never imports or executes a generated Context role.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import re

from . import context_package_adapter_0001 as previous

MAX_SOURCE = previous.MAX_SOURCE
BRIDGE = '_t35_context_bridge_0002'
IMPORT = ('from _t35_context_bridge_0002 import _ctx_private_root_context, '
          '_ctx_private_root_guard, _ctx_private_root_absent')
OLD = {
    'context': '407083f1bd4311ebc291d419e670ff223356549d8f7991b473e2c71fe819a4d3',
    'guard': 'ecfccebaa2d7bc7fe64eafe62a5f15a397196355c21f031296c7c7b31b724bf8',
    'absent': '60b1201e1a6f8f8181a2a3c6f4b7ee86a1403d25e07a8ff9fc33d12ecae1b731',
}
NEW_TEXT = {
    'context': '_ctx_private_root_context()',
    'guard': '_ctx_private_root_guard(root)',
    'absent': '_ctx_private_root_absent(root)',
}
NEW = {
    'context': '30249210f78759ad5f8e4926ecfb116036c8d526710b8e3c89fa10a6b36180cb',
    'guard': 'f052f0d08b9c183a4d674c5d809a9f56818d267262ddc9e99e0f6af5cd4bbef5',
    'absent': '1ec1a0e2ee3f2ffcad3b2acbe5cc538751c7c5f7c05336649a4c148afd075853',
}
FINALLY_AST_SHA256 = 'eac3c3c90bb4204e4b362619d3a607376a351eca8cab455a199435392ef5e30f'


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(node):
    return ast.dump(node, include_attributes=False)


def node_sha(node):
    return sha(dump(node).encode())


def _parse(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE, 'SOURCE_BOUND')
    try:
        return ast.parse(raw.decode('utf-8'))
    except (SyntaxError, UnicodeError, ValueError, RecursionError):
        raise Refusal('SOURCE_SYNTAX') from None


def _new(name):
    node = ast.parse(NEW_TEXT[name]).body[0]
    if name == 'context':
        node = node.value
    need(node_sha(node) == NEW[name], 'NEW_SPAN_DRIFT')
    return node


def _site(tree):
    build = previous.function(tree, 'build')
    need(len(build.body) >= 9 and isinstance(build.body[5], ast.With) and
         len(build.body[5].items) == 2 and
         ast.unparse(build.body[5].items[0].context_expr) ==
         'reader.open_signed(SOURCE_PIN, SOURCE_PACKAGE)' and
         isinstance(build.body[5].items[1].optional_vars, ast.Name) and
         build.body[5].items[1].optional_vars.id == 'tmp' and
         ast.unparse(build.body[5].body[0]) == 'root = Path(tmp)' and
         ast.unparse(build.body[5].body[2]) ==
         "policy_path = root / 'permission.json'" and
         ast.unparse(build.body[5].body[3]) ==
         'key, policy_pin = provision(policy_path, source)' and
         isinstance(build.body[5].body[-1], ast.Try) and
         not build.body[5].body[-1].handlers and
         not build.body[5].body[-1].orelse and
         node_sha(ast.Module(body=build.body[5].body[-1].finalbody,
                             type_ignores=[])) == FINALLY_AST_SHA256,
         'PRIVATE_TOPOLOGY')
    return build, build.body[5]


def adapt(raw, *, expected_preimage_sha256):
    """Project three exact private-root AST sites and prove inverse equality."""
    need(type(expected_preimage_sha256) is str and
         re.fullmatch(r'[0-9a-f]{64}', expected_preimage_sha256) is not None and
         type(raw) is bytes and sha(raw) == expected_preimage_sha256,
         'PREIMAGE_DRIFT')
    tree = _parse(raw)
    original = copy.deepcopy(tree)
    need(previous.count_calls(tree, '_t35_effect_refused') == 2 and
         len([x for x in tree.body if isinstance(x, ast.ImportFrom)
              and x.module == previous.BRIDGE]) == 1 and
         not any(isinstance(x, ast.ImportFrom) and x.module == BRIDGE
                 for x in tree.body), 'V1_PREIMAGE')
    build, with_node = _site(tree)
    old_nodes = {'context': with_node.items[1].context_expr,
                 'guard': with_node.body[1], 'absent': build.body[6]}
    need(all(node_sha(old_nodes[name]) == OLD[name] for name in OLD),
         'PRIVATE_PREIMAGE')
    with_node.items[1].context_expr = _new('context')
    with_node.body[1] = _new('guard')
    build.body[6] = _new('absent')
    imported = ast.parse(IMPORT).body[0]
    index = next(i for i, node in enumerate(tree.body)
                 if isinstance(node, ast.ImportFrom) and
                 node.module == previous.BRIDGE) + 1
    tree.body.insert(index, imported)
    ast.fix_missing_locations(tree)
    inverse = copy.deepcopy(tree)
    del inverse.body[index]
    ibuild, iwith = _site(inverse)
    original_build, original_with = _site(original)
    iwith.items[1].context_expr = copy.deepcopy(original_with.items[1].context_expr)
    iwith.body[1] = copy.deepcopy(original_with.body[1])
    ibuild.body[6] = copy.deepcopy(original_build.body[6])
    need(dump(inverse) == dump(original), 'INVERSE_DIFF')
    need(previous.count_calls(tree, '_t35_effect_refused') == 0,
         'EFFECT_REFUSAL_REMAINS')
    output = (ast.unparse(tree) + '\n').encode()
    need(len(output) <= MAX_SOURCE and dump(_parse(output)) == dump(tree),
         'POSTIMAGE_DRIFT')
    compile(output, '<context-private-inert>', 'exec', optimize=0)
    compile(output, '<context-private-inert>', 'exec', optimize=2)
    return output, {
        'schema_version': 'lab-context-private-ast-projection/v2-inert',
        'authority_effect': 'none', 'effect_ready': False,
        'preimage_sha256': expected_preimage_sha256,
        'preimage_ast_sha256': sha(dump(original).encode()),
        'postimage_sha256': sha(output),
        'postimage_ast_sha256': sha(dump(_parse(output)).encode()),
        'spans': {name: {'old_ast_sha256': OLD[name], 'new_ast_sha256': NEW[name]}
                  for name in OLD},
        'unimplemented_bridge': BRIDGE,
        'remaining_direct_effect_refusals': 0,
    }


def verify_postimage(preimage, postimage, *, expected_preimage_sha256):
    expected, record = adapt(preimage,
                             expected_preimage_sha256=expected_preimage_sha256)
    need(type(postimage) is bytes and postimage == expected, 'POSTIMAGE_DRIFT')
    return record
