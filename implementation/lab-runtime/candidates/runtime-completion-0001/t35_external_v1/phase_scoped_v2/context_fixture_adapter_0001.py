"""Pure seven-site fixture projection. Never imports or runs generated code.

The completion contract selects a future fixed bridge; no ACK, filesystem or
transport action is implemented here. Compilation does not establish execution.
"""
import ast
import copy
import hashlib
import json
import re
from pathlib import PurePosixPath

MAX_SOURCE = 256 * 1024
NORMALIZED_PREIMAGE = 'b2fa72f10b1d58b0909255e1ef3678997e43b563b45fc8f820e2a85dab76909a'
CEILING = 'Owned scratch stand-in only; no actual Context delivery or host authority.'
COMPLETION_JSON = '''{"schema_version":"lab-context-fixture-completion-selection/v1-inert","bridge_module":"_t35_context_bridge_0001","entrypoint":"_ctx_emit","leaf":"manifest.json","exact_selected_package_path_required":true,"sequence":["RELEASE_PRIVATE_ACK_AND_ABSENCE","BUILD_RESULT_EMIT_ACK","MANIFEST_EMIT_ACK","FINISH_SENT_ONCE","FINISH_ACK","CHECKED_CLIENT_CLOSE","EMIT_RETURN","SUMMARY"],"steps":[43,44,45,46],"missing_manifest_ack_finish_count":0,"finish_send_count":1,"retry":false,"unknown_is_sticky":true,"parent_writer_close_before_finish_ack":true,"late_parent_teardown_invalidates_run":true,"bridge_implemented":false,"effect_ready":false}'''


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(node):
    return ast.dump(node, include_attributes=False)


def completion_contract():
    return json.loads(COMPLETION_JSON)


def completion_digest():
    return sha(COMPLETION_JSON.encode())


def _hex(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def _parse(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE, 'SOURCE_BOUND')
    try:
        return ast.parse(raw.decode('utf-8'))
    except (SyntaxError, ValueError, UnicodeError, RecursionError):
        raise Refusal('SOURCE_SYNTAX') from None


def _function(tree, name):
    found = [(i,n) for i,n in enumerate(tree.body)
             if isinstance(n,ast.FunctionDef) and n.name == name]
    need(len(found) == 1, 'FUNCTION_SHAPE')
    return found[0]


def _normalized(tree):
    tree = copy.deepcopy(tree)
    pins = []
    for node in tree.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('SOURCE_PIN','SOURCE_PACKAGE'):
            need(isinstance(node.value,ast.Constant) and _hex(node.value.value), 'SOURCE_PIN_SHAPE')
            pins.append(node.targets[0].id)
            node.value = ast.Constant('SELECTED_PIN')
    need(sorted(pins) == ['SOURCE_PACKAGE','SOURCE_PIN'], 'SOURCE_PIN_COUNT')
    _, helper = _function(tree, '_t35_binding_path')
    paths = {}
    for node in helper.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('family','snapshot'):
            call = node.value
            need(isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='PurePosixPath' and len(call.args)==1 and not call.keywords and isinstance(call.args[0],ast.Constant), 'LAYOUT_SHAPE')
            value = call.args[0].value
            need(type(value) is str and len(value)<=4096 and value.startswith('/tmp/') and PurePosixPath(value).as_posix()==value and all(x not in ('','.','..') for x in value.split('/')[1:]), 'FIXTURE_LAYOUT')
            paths[node.targets[0].id] = PurePosixPath(value)
            call.args[0] = ast.Constant('SELECTED_PATH')
    need(set(paths)=={'family','snapshot'} and paths['family']!=paths['snapshot'] and paths['family'] not in paths['snapshot'].parents and paths['snapshot'] not in paths['family'].parents, 'FIXTURE_LAYOUT_DISJOINT')
    return tree


def _get(tree, path):
    for item in path:
        tree = getattr(tree,item) if type(item) is str else tree[item]
    return tree


def _set(tree, path, value):
    parent = _get(tree,path[:-1])
    if type(path[-1]) is str:
        setattr(parent,path[-1],value)
    else:
        parent[path[-1]] = value


def _statement(text):
    rows = ast.parse(text).body
    need(len(rows)==1,'REPLACEMENT_SHAPE')
    return rows[0]


def _plan(tree):
    qi,_ = _function(tree,'query')
    pi,_ = _function(tree,'provision')
    bi,build = _function(tree,'build')
    imports = [i for i,n in enumerate(tree.body) if isinstance(n,ast.ImportFrom) and n.module=='generation' and n.level==1]
    need(len(imports)==1,'PROVIDER_IMPORT')
    positions = {}
    for i,n in enumerate(build.body):
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('result','manifest'):
            positions[n.targets[0].id] = i
    need(set(positions)=={'result','manifest'},'OUTPUT_SHAPE')
    m = build.body[positions['manifest']].value
    fields = {k.value:i for i,k in enumerate(m.keys)}
    root = ('body',bi,'body')
    result = """result = {'schema_version':'lab-context-orchestration-result/v1-inert', 'result':'PASS', 'fixture_only':True, 'emitted_artifact_count':30, 'original_generation_executed':False, 'actual_carrier_validation':False, 'native_processes':0, 'authentic_permission':False, 'private_root_removed':True, 'owned_host_root':str(root), 'duration_seconds':time.monotonic()-started, 'source_sha256':source_pin, 'mapped_package_sha256':mapped_pin, 'authority_effect':'none', 'actual_owner_outcome':None, 'task_complete':False}"""
    return [
        ('module_docstring',[(('body',0),_statement(repr('Fixture-only Context builder orchestration; no original generation, native qualification or authentic permission.')))]),
        ('provider_import',[(('body',imports[0]),_statement('from .context_fixture_provider_0001 import *'))]),
        ('query',[(('body',qi),_statement('def query(source, channel):\n    return fixture_query(source, channel)'))]),
        ('provision_docstring',[(('body',pi,'body',0),_statement(repr('Ephemeral fixture key and non-authorizing public policy only.')))]),
        ('result',[(root+(positions['result'],),_statement(result))]),
        ('manifest_values',[(root+(positions['manifest'],'value','values',fields['schema_version']),ast.Constant('lab-context-scratch-package/v1-inert')),
                            (root+(positions['manifest'],'value','values',fields['claim_ceiling']),ast.Constant(CEILING))]),
        ('summary',[(root+(len(build.body)-1,),_statement("print(json.dumps({'result':'PASS','fixture_only':True,'package_binding':binding(out/'manifest.json'),'emitted_artifact_count':30,'authority_effect':'none','task_complete':False}),flush=True)"))]),
    ]


def adapt(raw, *, expected_preimage_sha256, expected_completion_sha256):
    need(_hex(expected_preimage_sha256) and type(raw) is bytes and sha(raw)==expected_preimage_sha256, 'PREIMAGE_DRIFT')
    need(_hex(expected_completion_sha256) and expected_completion_sha256==completion_digest(), 'COMPLETION_SELECTION')
    tree = _parse(raw)
    need(sha(dump(_normalized(tree)).encode())==NORMALIZED_PREIMAGE,'PREIMAGE_SKELETON')
    original = copy.deepcopy(tree)
    plan = _plan(tree)
    changes = []
    originals = []
    for group, entries in plan:
        record = {'group':group,'sites':[]}
        for path,replacement in entries:
            before = copy.deepcopy(_get(tree,path))
            originals.append((path,before))
            record['sites'].append({'path':list(path),'old_ast_sha256':sha(dump(before).encode()),'new_ast_sha256':sha(dump(replacement).encode())})
            _set(tree,path,copy.deepcopy(replacement))
        changes.append(record)
    ast.fix_missing_locations(tree)
    inverse = copy.deepcopy(tree)
    for path,before in originals:
        _set(inverse,path,copy.deepcopy(before))
    need(dump(inverse)==dump(original),'INVERSE_DIFF')
    # The final emit and emit wrapper are unchanged; only the selected future
    # bridge can implement completion. This verifies a call route, not an ACK.
    _, before_build = _function(original,'build')
    _, after_build = _function(tree,'build')
    _, before_emit = _function(original,'emit')
    _, after_emit = _function(tree,'emit')
    need(dump(before_emit)==dump(after_emit) and dump(before_build.body[-2])==dump(after_build.body[-2]),'COMPLETION_ROUTE_DRIFT')
    need(ast.unparse(after_build.body[-2])=="emit(out / 'manifest.json', manifest)",'FINAL_MANIFEST_CALL')
    need(ast.unparse(after_emit.body[-1])=='_ctx_emit(p, encoded(value) if raw is None else raw)','FIXED_BRIDGE_CALL')
    output = (ast.unparse(tree)+'\n').encode()
    need(len(output)<=MAX_SOURCE and dump(_parse(output))==dump(tree),'POSTIMAGE_SHAPE')
    for optimization in (0,2):
        compile(output,'<context-fixture-inert>','exec',optimize=optimization)
    return output, {'schema_version':'lab-context-fixture-ast-projection/v1-inert',
                    'preimage_sha256':expected_preimage_sha256,'postimage_sha256':sha(output),
                    'preimage_ast_sha256':sha(dump(original).encode()),
                    'postimage_ast_sha256':sha(dump(tree).encode()),
                    'groups':changes,'inverse_ast_equal':True,
                    'completion_contract_sha256':expected_completion_sha256,
                    'completion_route_ast_sha256':sha(dump(after_build.body[-2]).encode()),
                    'bridge_implemented':False,'runtime_provider_complete':False,
                    'generated_role_executed':False,'effect_ready':False}


def verify_postimage(preimage, postimage, *, expected_preimage_sha256, expected_completion_sha256):
    expected, record = adapt(preimage,expected_preimage_sha256=expected_preimage_sha256,
                             expected_completion_sha256=expected_completion_sha256)
    need(type(postimage) is bytes and postimage==expected,'POSTIMAGE_DRIFT')
    return record
