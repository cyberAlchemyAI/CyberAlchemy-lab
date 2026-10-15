"""Independent owner core reconstruction with unchanged original source bytes."""
import argparse,base64,hashlib,importlib.util,json,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-v20';OWNER=API.parent/'owner-routing-v2';TARGET=API.parent/'owner-core-preparation-v1';SOURCE=HERE/'owner-core-audit-source-0001.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes())}
def load(p):return json.loads(p.read_bytes())
def bytes_json(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
def put(p,v):p.open('xb').write(bytes_json(v))
def main():
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();assert bind(SOURCE)['sha256']==a.source_sha256;source=load(SOURCE);checks=[]
    def need(value,label):
        if not value:raise AssertionError(label)
        checks.append(label)
    for row in source['files']:need(bind(ROOT/row['path'])==row,'unchanged frozen owner core input '+row['path'])
    spec=importlib.util.spec_from_file_location('_cal_owner_core_independent_api',API/'__init__.py',submodule_search_locations=[str(API)]);module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);P=__import__(spec.name+'.protocol',fromlist=['*']);G=__import__(spec.name+'.guard',fromlist=['*']);G.verify('297369965e3269d3ae63ff527f98eba1cd7133da0ca1ee487088c6813aeaf342')
    manifest=load(TARGET/'artifacts/manifest.json');old=load(OWNER/'artifacts/proposal.json');originals={r['identity_ref']:r for r in old['exact_targets']};members={r['version_ref']:r for r in manifest['members']}
    need(len(members)==len(manifest['members'])==len(originals)==42,'all42 independent members unique');need(len(manifest['scope_proposals'])==21,'all21 scopes retained');observations=[];seen=set()
    with P.source.replay_source('custody-participation') as view:
        before=digest(view.data['projection']);need(len(view.subjects)==582,'same original582source subjects')
        for group in manifest['scope_proposals']:
            need(group['configuration_status']=='hypothetical-unprovisioned' and not group['actual_runtime_authority_verified'],'scope configuration is explicitly hypothetical')
            config=load(ROOT/group['configuration_hypothesis_binding']['path']);proposal=load(ROOT/group['runtime_proposal_binding']['path']);scope=group['scope_ref'];expected_config=dict(view.data['config']);expected_config['scope_ref']=scope
            need(config==expected_config and scope!=view.data['config']['scope_ref'],'only declared hypothesis scope changes; actual source scope is retained separately')
            need(proposal['scope_ref']==config['scope_ref']==scope and len(proposal['targets'])==2,'exact two members in independently scoped proposal')
            expected=[]
            for target in proposal['targets']:
                version=target['version_ref'];member=members[version];original=originals[target['record']['node_id']];raw=(OWNER/'artifacts'/original['filename']).read_bytes();content=base64.b64decode(target['content']['data'],validate=True)
                need(raw==content and json.loads(raw)==target['record'],'exact original body bytes and parsed value '+version)
                need(sha(raw)==member['original_body_sha256']==target['content']['byte_sha256']==original['byte_sha256'],'four original byte witnesses agree '+version)
                need(target['record']['scope_ref']==member['scope_ref']==scope and target['carrier_ref']==original['carrier_ref']==member['carrier_ref'],'original domain scope/carrier unchanged '+version)
                need(target['decision_ref']==member['decision_ref'] and version not in seen and version not in view.subjects,'independent Decision/version absent from original source '+version);seen.add(version)
                core={'decision_ref':target['decision_ref'],'category':target['category'],'operation':target['operation'],'version_ref':version,'target_digest':digest(target)};core_raw=(ROOT/member['independent_core_binding']['path']).read_bytes()
                need(core_raw==bytes_json(core) and sha(core_raw)==member['independent_core_binding']['sha256'],'complete stable core original byte identity '+version)
                need(sha(bytes_json(target))==member['complete_target_sha256'],'complete target JSON byte SHA is independently verified '+version)
                need(core['target_digest']!=member['complete_target_sha256'],'semantic compact digest remains distinct from complete target JSON byte SHA '+version)
                expected.append(core);observations.append({'version_ref':version,'scope_ref':scope,'original_body_sha256':sha(raw),'target_json_byte_sha256':member['complete_target_sha256'],'core_target_digest':core['target_digest'],'core_binding':member['independent_core_binding'],'authority_effect':'none'})
            post,actual=view.handle.operations.prepare(view.data['projection'],proposal,view.data['head']['transaction_digest'],config)
            need(actual==expected,'fresh original backend computes exact cores '+scope)
            for target in proposal['targets']:need(post['subjects'][target['version_ref']]['record']==target['record'],'fresh simulated postimage matches exact body '+target['version_ref'])
            need(digest(view.data['projection'])==before,'original source unchanged after entire group '+scope)
        need(len(seen)==42 and digest(view.data['projection'])==before,'all42 reconstructed once without source mutation');view.custody_signed_sources.guard();checks.append('final original signed source guard')
    G.verify('297369965e3269d3ae63ff527f98eba1cd7133da0ca1ee487088c6813aeaf342')
    for row in source['files']:need(bind(ROOT/row['path'])==row,'unchanged final owner core input '+row['path'])
    output=TARGET/'receipts/independent-audit-0001.json';audit={'schema_version':'lab-owner-core-independent-audit/v1-candidate','result':'PASS','checks':len(checks),'check_names':checks,'source_binding':bind(SOURCE),'observations':observations,'independent_core_count':42,'separate_scope_count':21,'source_projection_unchanged':True,'configuration_status':'hypothetical-unprovisioned','current_runtime_grants':0,'actual_owner_outcome':None,'required_governing_role_coverage_verified':False,'public_review_adapter_implemented':False,'repository_admissions_applied':0,'authority_effect':'none','task_complete':False,'goal_complete':False,'checked_at':datetime.now(timezone.utc).isoformat()};put(output,audit);print(json.dumps({'result':'PASS','checks':len(checks),'cores':42,'scopes':21,'audit_binding':bind(output)}),flush=True)
if __name__=='__main__':main()
