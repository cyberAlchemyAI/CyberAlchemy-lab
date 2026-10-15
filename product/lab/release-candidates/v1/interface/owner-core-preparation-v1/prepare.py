"""Exact owner Decision cores; scope configurations remain hypothetical."""
import copy,hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
API=HERE.parent/'api-v20';OWNER=HERE.parent/'owner-routing-v2'
API_PIN='297369965e3269d3ae63ff527f98eba1cd7133da0ca1ee487088c6813aeaf342'
OWNER_PROOF_PIN='8349a4909d2d767353a39c96d8d1116c34038749cb7b960efdfb3ce2a72f28e6'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes())}
def require(v,message):
    if not v:raise ValueError(message)
def guard(pin):
    p=HERE/'source-manifest.json';require(sha(p.read_bytes())==pin,'owner core source pin differs');m=json.loads(p.read_bytes())
    for row in m['files']:require(bind(ROOT/row['path'])==row,'frozen source changed '+row['path'])
    require(bind(API/'source-manifest.json')['sha256']==API_PIN,'selected API differs');require(bind(OWNER/'proof-0001.json')['sha256']==OWNER_PROOF_PIN,'selected owner representation differs')
    return m
name='_cal_owner_core_api20'
spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)]);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
def imported(n):return __import__(name+'.'+n,fromlist=['*'])
P=imported('protocol')
def inputs(view):
    plan=json.loads((OWNER/'artifacts/proposal.json').read_bytes());groups={}
    for item in plan['exact_targets']:
        path=OWNER/'artifacts'/item['filename'];raw=path.read_bytes();body=P.source.parse(raw)
        require(sha(raw)==item['byte_sha256'] and body['node_id']==item['identity_ref'],'exact proposed owner target differs')
        version=body['node_id']+'@owner-representation.candidate.1';decision='decision:R03-owner-representation:'+body['node_id']
        target={'category':'artifact-instance','operation':'admit','version_ref':version,'carrier_ref':item['carrier_ref'],'record':body,'predecessor_ref':None,'decision_ref':decision,'contract':None,'content':view.handle.custody.content_entry(raw)}
        groups.setdefault(body['scope_ref'],[]).append({'target':target,'original_body_binding':bind(path),'schema_binding':item['schema_binding'],'original_bytes':raw})
    require(sum(map(len,groups.values()))==42 and len(groups)==21,'expected exact42 targets/21 distinct scopes')
    return groups

def proposal_for(view,scope,members):
    require(all(m['target']['record']['scope_ref']==scope for m in members),'declared owner scope differs')
    config=copy.deepcopy(view.data['config']);config['scope_ref']=scope
    ident='proposal:R03-owner-representation:'+sha(scope.encode())
    proposal={'schema_version':'lab-runtime-proposal/v1','proposal_id':ident,'expected_head':view.data['head']['transaction_digest'],'source_snapshot_digest':config['source_snapshot_digest'],'scope_ref':scope,'policy_ref':config['policy_ref'],'challenge_route':config['challenge_route'],'schemas':{},'targets':[copy.deepcopy(m['target']) for m in members]}
    originals={m['target']['version_ref']:m['original_bytes'] for m in members}
    proposal=view.handle.custody.with_originals(proposal,originals,{},exact_schema_bytes=True)
    require(proposal['targets']==[m['target'] for m in members],'raw codec changed already-bound targets')
    return config,proposal

def prepare_group(view,scope,members):
    before=view.handle.common.digest(view.data['projection']);config,proposal=proposal_for(view,scope,members)
    post,cores=view.handle.operations.prepare(view.data['projection'],proposal,view.data['head']['transaction_digest'],config)
    require(before==view.handle.common.digest(view.data['projection']),'pure owner preparation changed source projection')
    expected=[{'decision_ref':m['target']['decision_ref'],'category':'artifact-instance','operation':'admit','version_ref':m['target']['version_ref'],'target_digest':view.handle.common.digest(m['target'])} for m in members]
    require(cores==expected,'actual backend cores differ from complete exact targets')
    for m in members:
        t=m['target'];subject=post['subjects'][t['version_ref']]
        require(subject['record']==t['record'] and subject['source']['sha256']==sha(m['original_bytes']),'simulation changed proposed original bodies')
        require(view.handle.custody.decode_content(t['content'])==m['original_bytes'],'original owner body codec differs')
    return {'scope_ref':scope,'source_project_scope_ref':view.data['config']['scope_ref'],'configuration_status':'hypothetical-unprovisioned','configuration':config,'original_configuration_binding':{'ref':'captured-original-source-config','sha256':sha(encoded(view.data['config']))},'runtime_proposal':proposal,'cores':cores,'source_projection_unchanged':True,'authority_effect':'none','current_runtime_grant':False,'repository_admissions_applied':0,'actual_owner_outcome':None}
