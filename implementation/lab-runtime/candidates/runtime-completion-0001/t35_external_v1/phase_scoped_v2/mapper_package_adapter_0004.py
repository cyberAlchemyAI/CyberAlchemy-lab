"""Pure exact-preimage Mapper AST adapter. No filesystem/process/custody API.

The output requires a future independently selected bridge. Never execute it
merely because this projection succeeds. The supplied preimage SHA is an
external selection, not an authority or an internally derived default.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import re

MAX_SOURCE = 256 * 1024
BRIDGE = '_t35_external_runtime_capture'
IMPORT = ('from _t35_external_runtime_capture import package_begin, package_emit, '
          'package_seal, package_cold_read, package_finish')


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(node):
    return ast.dump(node, annotate_fields=True, include_attributes=False)


def function(tree, name):
    rows = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    need(len(rows) == 1, 'FUNCTION_SHAPE')
    return rows[0]


def calls(node, name):
    return [n for n in ast.walk(node) if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name) and n.func.id == name]


def parse(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE, 'SOURCE_BOUND')
    try:
        return ast.parse(raw.decode('utf-8'))
    except (SyntaxError, UnicodeError, ValueError, RecursionError):
        raise Refusal('SOURCE_SYNTAX') from None


def pinned(raw, expected_sha256):
    need(type(expected_sha256) is str and re.fullmatch('[0-9a-f]{64}', expected_sha256)
         and type(raw) is bytes and digest(raw) == expected_sha256, 'PREIMAGE_DRIFT')
    return parse(raw)


def projection_contract(tree):
    """Inspect original count/cursor predicates, not an invented projection."""
    build = function(tree, 'build')
    counts = {}
    for node in calls(build, 'require'):
        if not node.args:
            continue
        c = node.args[0]
        if (isinstance(c, ast.Compare) and len(c.ops) == 1 and isinstance(c.ops[0], ast.Eq)
                and isinstance(c.left, ast.Call) and isinstance(c.left.func, ast.Name)
                and c.left.func.id == 'len' and len(c.left.args) == 1
                and isinstance(c.left.args[0], ast.Name) and len(c.comparators) == 1
                and isinstance(c.comparators[0], ast.Constant)):
            name = c.left.args[0].id
            if name in ('current', 'selected_relation_refs', 'relations'):
                need(name not in counts, 'COUNT_DUPLICATE')
                counts[name] = c.comparators[0].value
    need(counts == {'current': 15, 'selected_relation_refs': 10, 'relations': 10},
         'PROJECTION_COUNTS')
    request = [n.value for n in ast.walk(build) if isinstance(n, ast.Assign)
               and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
               and n.targets[0].id == 'request']
    need(len(request) == 1 and isinstance(request[0], ast.Dict), 'REQUEST_SHAPE')
    cursors = []
    for node in ast.walk(request[0]):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value in ('semantic_cursor', 'governance_cursor'):
                    need(isinstance(value, ast.Constant) and type(value.value) is int,
                         'CURSOR_SHAPE')
                    cursors.append((key.value, value.value))
    need(sorted(cursors) == [('governance_cursor', 25), ('semantic_cursor', 25)],
         'PROJECTION_CURSORS')
    return {'nodes': 15, 'relations': 10, 'events_per_family': 25,
            'leaves': 55, 'manifest_rows': 54}


def sites(tree):
    result = []
    for name, labels in [('build', ('B1',)), ('emit', ('E1', 'E2')),
                         ('seal', ('S1', 'S2'))]:
        found = calls(function(tree, name), '_t35_effect_refused')
        need(len(found) == len(labels), 'REFUSAL_TOPOLOGY')
        # ast.iter_fields preserves source structure, so each path is exact.
        def visit(node, path):
            if any(node is x for x in found):
                yield path, node
            for field, value in ast.iter_fields(node):
                if isinstance(value, ast.AST):
                    yield from visit(value, path + '.' + field)
                elif isinstance(value, list):
                    for i, child in enumerate(value):
                        if isinstance(child, ast.AST):
                            yield from visit(child, path + '.' + field + '[' + str(i) + ']')
        paths = list(visit(function(tree, name), name))
        for label, (path, node) in zip(labels, paths):
            result.append({'id': label, 'selector': path, 'old_ast': dump(node)})
    need(len(calls(tree, '_t35_effect_refused')) == 5, 'EXTRA_REFUSAL')
    call = function(tree, 'call')
    need(len(calls(call, 'run_native')) == 1, 'CALL_BRIDGE')
    result.append({'id': 'C1', 'selector': 'call.body', 'old_ast': dump(call)})
    return result


def _project(tree):
    original = copy.deepcopy(tree)
    selected_sites = sites(tree)
    projection = projection_contract(tree)
    build = function(tree, 'build')
    need([ast.unparse(x) for x in build.body[:5]] == [
        'guard(pin)', 'started = time.monotonic()', "out = HERE / 'packages/0001'",
        "require(not out.exists(), 'mapped package already exists')", '_t35_effect_refused()'],
        'BUILD_PREIMAGE')
    need([len(calls(build, n)) for n in ('guard', 'seal', 'call', 'emit')] == [2, 2, 2, 6],
         'BUILD_TOPOLOGY')
    spans = [{'id': 'B1', 'old_ast': [dump(x) for x in build.body[3:5]]}]
    build.body[3:5] = ast.parse('package_begin(pin, out)').body
    bodies = {
        'emit': '''def emit(p, value, raw=None):
    require(p.is_relative_to(HERE / 'packages/0001'), 'mapped package leaf outside boundary')
    return package_emit(p.relative_to(HERE / 'packages/0001').as_posix(), encoded(value) if raw is None else raw)
''',
        'seal': '''def seal(body):
    return json.loads(package_seal(encoded(body)))
''',
    }
    for name, text in bodies.items():
        f = function(tree, name)
        need(dump(f.args) == dump(function(ast.parse(text), name).args), 'FUNCTION_ARGUMENTS')
        spans.append({'id': name, 'old_ast': [dump(n) for n in f.body]})
        f.body = function(ast.parse(text), name).body
    call = function(tree, 'call')
    need(len(call.body) == 6 and len(calls(call.body[0], 'require')) == 1
         and len(calls(call.body[4], 'require')) == 1
         and isinstance(call.body[-1], ast.Return), 'CALL_PREIMAGE')
    need(ast.unparse(call.body[0]) == "require(sha(EXE.read_bytes()) == EXE_SHA, 'native executable changed before invocation')"
         and ast.unparse(call.body[4]) == "require(sha(EXE.read_bytes()) == EXE_SHA, 'native executable changed after invocation')",
         'CALL_GUARDS')
    spans.append({'id': 'call', 'old_ast': [dump(n) for n in call.body]})
    before, after = call.body[0], call.body[4]
    call.body = [before, *ast.parse("raw = package_cold_read(list(map(str, args)))").body,
                 after, ast.Return(value=ast.Name(id='raw', ctx=ast.Load()))]
    positions = [i for i, n in enumerate(build.body) if ast.unparse(n) == "emit(out / 'manifest.json', manifest)"]
    need(len(positions) == 1 and positions[0] == len(build.body) - 2
         and len(calls(build.body[-1], 'print')) == 1, 'FINISH_PREIMAGE')
    finish_index = positions[0] + 1
    build.body[finish_index:finish_index] = ast.parse("package_finish(binding(out / 'manifest.json'))").body
    imported = ast.parse(IMPORT).body[0]
    need(not any(isinstance(n, ast.ImportFrom) and n.module == BRIDGE for n in tree.body),
         'EXTRA_BRIDGE_IMPORT')
    index = 1 if isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) else 0
    while index < len(tree.body) and isinstance(tree.body[index], ast.ImportFrom) and tree.body[index].module == '__future__':
        index += 1
    tree.body.insert(index, imported)
    ast.fix_missing_locations(tree)
    # Restore exactly the four allowed replacement spans and two insertions.
    inverse = copy.deepcopy(tree)
    del inverse.body[index]
    ib = function(inverse, 'build')
    del ib.body[finish_index]
    ib.body[3:4] = copy.deepcopy(function(original, 'build').body[3:5])
    for name in ('emit', 'seal', 'call'):
        function(inverse, name).body = copy.deepcopy(function(original, name).body)
    need(dump(inverse) == dump(original), 'NONSELECTED_AST_CHANGED')
    need(not calls(tree, '_t35_effect_refused') and not calls(tree, 'run_native'), 'EFFECT_REMAINS')
    need(projection_contract(tree) == projection, 'PROJECTION_DRIFT')
    spans[0]['new_ast'] = [dump(build.body[3])]
    for span in spans[1:]:
        span['new_ast'] = [dump(n) for n in function(tree, span['id']).body]
    return tree, {'sites': selected_sites, 'grouped_replacements': spans,
                  'insertions': [{'id': 'F1', 'selector': 'build.body[' + str(finish_index) + ']',
                                  'new_ast': dump(build.body[finish_index])},
                                 {'id': 'I1', 'selector': 'module.body[' + str(index) + ']',
                                  'new_ast': dump(imported)}], 'projection': projection}


def adapt(raw, *, expected_preimage_sha256):
    tree = pinned(raw, expected_preimage_sha256)
    old_ast = dump(tree)
    post, record = _project(tree)
    output = (ast.unparse(post) + '\n').encode('utf-8')
    need(len(output) <= MAX_SOURCE, 'POSTIMAGE_BOUND')
    compile(output, '<selected-mapper-projection>', 'exec')  # No code is executed.
    record.update(schema_version='lab-mapper-ast-projection/v1', authority_effect='none',
                  effect_ready=False, preimage_sha256=expected_preimage_sha256,
                  preimage_ast_sha256=digest(old_ast.encode()), postimage_sha256=digest(output),
                  postimage_ast_sha256=digest(dump(parse(output)).encode()))
    return output, record


def verify_postimage(preimage, postimage, *, expected_preimage_sha256):
    expected, record = adapt(preimage, expected_preimage_sha256=expected_preimage_sha256)
    need(type(postimage) is bytes and postimage == expected, 'POSTIMAGE_DRIFT')
    return record
