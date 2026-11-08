"""Exact inert AST probe of the reviewed Context build.emit seam."""
from __future__ import annotations

import ast
import copy
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/context-construction-0003/rendered/build.py')
SOURCE_SHA = 'f465f1f1f8b9c8269935d9590f4a6006633d8c335416e3b46703a6c190e0711b'
OLD_SPAN_SHA = 'c2f71d902f1dde0ae68262cebc9d3c091b6e675c829df3d3dc2fb1b793dc4cb6'
NEW_SPAN_SHA = '80547ec6827c12247a4c828db22caa70a95b321f11e9faafb1694809a8a69ef7'


class Refused(ValueError):
    pass


def require(ok, why):
    if not ok:
        raise Refused(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def span_hash(body):
    return sha(ast.dump(ast.Module(body=body, type_ignores=[]), include_attributes=False).encode())


def function(tree, name):
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    require(len(nodes) == 1, f'exact {name} function required')
    return nodes[0]


def effect_calls(tree):
    return sum(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and
               node.func.id == '_t35_effect_refused' for node in ast.walk(tree))


def adapt():
    raw = SOURCE.read_bytes()
    require(sha(raw) == SOURCE_SHA, 'reviewed Context emitted build changed')
    original = ast.parse(raw)
    emitted = function(original, 'emit')
    build = function(original, 'build')
    require(len(emitted.args.args) == 3 and [n.arg for n in emitted.args.args] == ['p', 'value', 'raw'] and
            len(emitted.args.defaults) == 1 and len(emitted.body) == 4 and
            span_hash(emitted.body[1:]) == OLD_SPAN_SHA and
            effect_calls(original) == 6, 'exact original emit span or refusal count differs')
    require(len(build.body) >= 2 and
            isinstance(build.body[-2], ast.Expr) and isinstance(build.body[-2].value, ast.Call) and
            isinstance(build.body[-2].value.func, ast.Name) and build.body[-2].value.func.id == 'emit' and
            isinstance(build.body[-1], ast.Expr) and isinstance(build.body[-1].value, ast.Call) and
            isinstance(build.body[-1].value.func, ast.Name) and build.body[-1].value.func.id == 'print',
            'original manifest emit and summary adjacency differs')
    new_body = ast.parse('_ctx_emit(p, encoded(value) if raw is None else raw)').body
    require(span_hash(new_body) == NEW_SPAN_SHA, 'selected inert bridge span differs')
    changed = copy.deepcopy(original)
    target = function(changed, 'emit')
    guard = copy.deepcopy(target.body[0])
    target.body[1:] = new_body
    ast.fix_missing_locations(changed)
    require(ast.dump(guard, include_attributes=False) ==
            ast.dump(target.body[0], include_attributes=False) and
            effect_calls(changed) == 4, 'boundary guard or unselected refusal changed')
    inverse = copy.deepcopy(changed)
    function(inverse, 'emit').body[1:] = copy.deepcopy(emitted.body[1:])
    require(ast.dump(inverse, include_attributes=False) ==
            ast.dump(original, include_attributes=False), 'full emitted AST inverse differs')
    out = (ast.unparse(changed) + '\n').encode()
    compile(out, '<inert-context-emitted-build>', 'exec', optimize=0)
    compile(out, '<inert-context-emitted-build>', 'exec', optimize=2)
    proof = {
        'schema_version': 'lab-context-inert-emit-ast-proof/v1',
        'original_rendered_sha256': SOURCE_SHA, 'old_span_sha256': OLD_SPAN_SHA,
        'new_span_sha256': NEW_SPAN_SHA, 'adapted_sha256': sha(out),
        'original_effect_refusals': 6, 'adapted_effect_refusals': 4,
        'unchanged_manifest_emit_then_summary': True,
        'full_ast_inverse_equal': True, 'effect': 'NOT_RUN',
    }
    return out, proof
