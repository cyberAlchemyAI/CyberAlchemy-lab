"""Pinned original AST predicates with controlled inert dependencies only.

Not the whole original policy_guard, filesystem custody, JSON schema, signed
source, original period, Service or v2 CompletionBridge oracle.
"""
import ast, copy, hashlib, json, os, types
from pathlib import Path
API=Path('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/api-integration-v30')
PINS={'auth.py':'f667de38d845b59de41679d7cdad4f632ff4b60bc98d419557fb4091d0693bef',
      'protocol.py':'bb30b7b9976b273d75e5ab97d24ce64c0b46dcf408696ca4b9d9294d7deab881',
      'installation_release.py':'5362c747a93ecc12990d56136ece6c0e4501f9b0a31e676e9889bc6eb3345dcc'}
TREES={}
for name,pin in PINS.items():
    raw=(API/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('original compatibility input drift')
    TREES[name]=ast.parse(raw,filename=str(API/name))
def method(name,cls,symbol):
    c=next(n for n in TREES[name].body if isinstance(n,ast.ClassDef)and n.name==cls)
    return next(n for n in c.body if isinstance(n,ast.FunctionDef)and n.name==symbol)
FN=method('auth.py','ReaderChannel','policy_guard')
SHAPE=[n for n in FN.body if n.lineno>=49 and n.end_lineno<=103]
if len(SHAPE)<30 or SHAPE[-1].end_lineno!=103:raise ValueError('original AST selector drift')
CONSTANTS=[n for n in TREES['protocol.py'].body if isinstance(n,ast.Assign)
           and all(isinstance(t,ast.Name)and t.id.endswith('_SUPPORTED')for t in n.targets)]
OPS={};exec(compile(ast.Module(body=copy.deepcopy(CONSTANTS),type_ignores=[]),str(API/'protocol.py'),'exec'),OPS)
LINEAGE={'auth_shape':{'source_sha256':PINS['auth.py'],'method':'ReaderChannel.policy_guard',
                       'ranges':[[n.lineno,n.end_lineno]for n in SHAPE],
                       'ast_sha256':hashlib.sha256(ast.dump(ast.Module(body=SHAPE,type_ignores=[]),include_attributes=True).encode()).hexdigest()},
         'operation_constants':{'source_sha256':PINS['protocol.py'],'ranges':[[n.lineno,n.end_lineno]for n in CONSTANTS]},
         'excluded':['original external policy filesystem and JSON schema validation','actual source/signatures/periods/currentness',
                     'full original Service and v2 CompletionBridge validation']}
def require(value,message):
    if not value:raise ValueError(message)
def checked(policy,uid=None):
    source=types.SimpleNamespace(require=require,CURRENT_SOURCE8_NAME='completion-current-participation:optimized-0005')
    env={**OPS,'source':source,'os':types.SimpleNamespace(getuid=lambda:os.getuid()if uid is None else uid),'value':copy.deepcopy(policy)}
    exec(compile(ast.Module(body=copy.deepcopy(SHAPE),type_ignores=[]),str(API/'auth.py'),'exec'),env)
    return env
# Embed the same original predicates in selected inert fixture module source.
# No AST predicate is rewritten; only function wrapping/location changes.
FIXTURE_SOURCE='\n'.join(ast.unparse(n)for n in CONSTANTS)+'\n'
FIXTURE_SOURCE+='def _original_policy(value):\n'+''.join('    '+line+'\n'for n in SHAPE for line in ast.unparse(n).splitlines())
FIXTURE_SOURCE+='\ndef _original_require(value,message):\n    if not value: raise ValueError(message)\n'
FIXTURE_SOURCE+="source=SimpleNamespace(require=_original_require,CURRENT_SOURCE8_NAME='completion-current-participation:optimized-0005')\n"
def policy(role,family,principal,key,uid=None):
    metadata=role=='installation-metadata'
    p={'schema_version':'lab-local-current-legacy-installation-release-policy/v1-candidate'if metadata else'lab-local-candidate-policy/v4-candidate',
       'principal_ref':principal,'reader_public_key':key,'host_uid':os.getuid()if uid is None else uid,
       'source_name':'completion-current-participation:optimized-0005'if family=='optimized-0005'else'completion-legacy:legacy-source8-20261018-b',
       'scope_refs':['scope:owned-fixture'],'expires_at':'2099-01-01T00:00:00Z','max_request_bytes':4096,'max_response_bytes':4096,'max_calls':1,
       'allowed_operations':list(OPS['INSTALLATION_RELEASE_SUPPORTED'if metadata else'LEGACY_SUPPORTED']),
       'revoked':False,'scope_posture':'isolated-candidate-preparation','authority_effect':'none','actual_owner_outcome':None,
       'workspace':None,'session_control':None if metadata else{},'projection_control':None}
    if family=='optimized-0005':p['source8_control']={}
    if metadata:p.update(installation_release_control={'plan_binding':{'ref':'fixture-plan','sha256':'a'*64}},
       current_legacy_installation_control={'period_binding':{},'source_cut':{}},purpose='durable-metadata-and-exact-installation-release',
       development_authorization_binding={},scope_control=None)
    return p
