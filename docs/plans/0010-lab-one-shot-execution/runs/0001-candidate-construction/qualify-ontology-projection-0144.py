"""Actual authenticated source-to-native projection in a new owned ontology root."""
import copy
from datetime import datetime,timezone,timedelta
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback
import uuid

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v4'
SOURCE='53acafec093f41560714dce48584d0f6856e19e2f67b98ed9942111cf557d197'
PROFILE='20986676504f62638f61abce1e8e8c232fe72e10c64862153264f6cc630cf9ab'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def snapshot(p):return {x.relative_to(p).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in p.rglob('*') if x.is_file()}
def main():
    out=RUN/'Ontology-projection-qualification-0144.json';assert not out.exists()
    name='_cal_ontology_public_0144';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    P=__import__(name+'.protocol',fromlist=['*']);G=__import__(name+'.guard',fromlist=['*'])
    A=__import__(name+'.auth',fromlist=['*']);F=__import__(name+'.fixtures',fromlist=['*'])
    W=__import__(name+'.workspace',fromlist=['*']);S=__import__(name+'.service',fromlist=['*'])
    H=__import__(name+'.handlers',fromlist=['*']);O=__import__(name+'.ontology_projection',fromlist=['*'])
    G.verify(SOURCE);schemas=P.Schemas(PROFILE);checks=[];calls=[];failure=None;owned=None
    try:
        with P.source.replay_source('custody-participation') as view,tempfile.TemporaryDirectory(prefix='cal-ontology-public-0144-') as temp:
            owned=Path(temp);owned.chmod(0o700);principal='principal:owned-ontology-operator:'+uuid.uuid4().hex
            key,policy_path,pin=F.provision(owned,'custody-participation',principal=principal,max_actions=8)
            workspace=owned/'workspace';native_root=workspace/'ontology';native_root.mkdir(mode=0o700)
            policy=P.frame_parse(policy_path.read_bytes());manifest=P.frame_parse((workspace/'workspace.json').read_bytes())
            materials={}
            def material(ref,value):
                raw=P.compact(value);materials[ref]=raw;return P.binding(ref,raw)
            current=datetime.now(timezone.utc);end=current+timedelta(hours=1)
            store='ontology-store:owned:'+uuid.uuid4().hex;branch='branch:'+store
            st=native_root.stat();identity={'device':st.st_dev,'inode':st.st_ino}
            genesis={'schema_version':'lab-owned-ontology-head/v1-candidate','sequence':0,'store_ref':store,'branch_ref':branch,
                'parent_head_sha256':None,'generation':None,'generation_sha256':None}
            W.atomic(native_root/'HEAD.json',P.compact(genesis))
            evidence=material('evidence:actual-owned-ontology-root',{'schema_version':'lab-owned-ontology-root-evidence/v1-candidate',
                'principal_ref':principal,'host_uid':os.getuid(),'root_identity':identity,'root_mode':oct(native_root.stat().st_mode&0o777),
                'scope':'New isolated candidate ontology only; no existing store, canonical owner outcome or Lab admission','authority_effect':'none'})
            grant=material('policy:owned-ontology-representation',{'schema_version':'lab-owned-ontology-representation-grant/v1-candidate',
                'principal_ref':principal,'store_ref':store,'effects':['ontology-representation'],'root_identity':identity,
                'not_before':(current-timedelta(seconds=1)).isoformat(),'expires_at':end.isoformat(),'authority_effect':'none','actual_owner_outcome':None})
            basis={'authority_scope':'operator-local','owner_principal_ref':principal,'evidence_bindings':[evidence],
                'policy_bindings':[grant],'scope_refs':[store],'expires_at':end.isoformat()}
            mapping=P.binding(str((O.MAPPER/'policy.json').relative_to(ROOT)),(O.MAPPER/'policy.json').read_bytes());cut=H.cut(view)
            route={'schema_version':'lab-owned-ontology-routing/v1-candidate','principal_ref':principal,'scope_ref':policy['scope_refs'][0],
                'store_ref':store,'branch_ref':branch,'root_identity':identity,'mapping_binding':mapping,
                'mapped_source_binding':{'ref':str((O.MAPPER/'source-manifest.json').relative_to(ROOT)),'sha256':O.MAPPER_PIN},
                'mapped_package_binding':{'ref':str((O.MAPPER/'packages/0001/manifest.json').relative_to(ROOT)),'sha256':O.PACKAGE_PIN},
                'expected_lab_cut':cut,'authorization_basis':basis,'not_before':(current-timedelta(seconds=1)).isoformat(),
                'expires_at':end.isoformat(),'permitted_effects':['ontology-representation']}
            routing=material('routing:owned-ontology',route)
            for i,(ref,raw) in enumerate(materials.items()):
                path='inputs/ontology-'+str(i)+'.json';W.atomic(workspace/path,raw);manifest['materials'].append({'ref':ref,'path':path,'sha256':P.source.sha(raw)})
            mraw=P.compact(manifest);(workspace/'workspace.json').write_bytes(mraw)
            policy.update(schema_version='lab-local-ontology-projection-policy/v1-candidate',session_control=None,
                purpose='durable-metadata-and-exact-ontology-projection',allowed_operations=list(P.ONTOLOGY_SUPPORTED),
                development_authorization_binding=P.binding(str((RUN/'authorization.json').relative_to(ROOT)),(RUN/'authorization.json').read_bytes()),
                scope_control=None,expires_at=end.isoformat(),max_request_bytes=1048576,
                ontology_control={'routing_binding':routing,'method_binding':P.binding(str((API/'ontology_projection.py').relative_to(ROOT)),(API/'ontology_projection.py').read_bytes())})
            policy['workspace']['manifest_sha256']=P.source.sha(mraw);praw=P.compact(policy);policy_path.write_bytes(praw)
            assert schemas.valid('reader-authentication',policy),'actual private ontology policy schema differs'
            channel=A.ReaderChannel(policy_path,P.source.sha(praw),schemas);context=channel.authenticate(F.proof(key,channel.challenge))['context'];key=None
            service=S.Service(view,channel,schemas)
            try:
                assert service.sessions is None and context['principal_ref']==principal
                checks.append({'check':'actual-nonce-and-separately-provisioned-owned-ontology-scope','result':'PASS'})
                expected={'store_ref':store,'branch_ref':branch,'commit_sequence':0,'commit_sha256':P.source.sha(P.compact(genesis)),
                    'source_profile_sha256':mapping['sha256'],'streams':[]}
                actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')};actor['role_assignment_refs']=context['role_assignment_bindings']
                message={'schema_version':'lab-ontology-project-request/v1-candidate','request_ref':'request:owned-ontology:'+uuid.uuid4().hex,
                    'actor':actor,'lab_source_cut':cut,'ontology_expected_cut':expected,'mapping_binding':mapping,'subject_refs':[],
                    'authorization_basis':basis,'idempotency_key':'ontology:'+uuid.uuid4().hex,'authority_effect':'none'}
                call=F.call(context,'lab.status',cut);call.update(operation='ontology.project',message=message,
                    idempotency_key=message['idempotency_key'],deadline=end.isoformat(),max_response_bytes=1048576)
                assert schemas.valid('api-call',call) and schemas.protocol_valid('urn:cyberalchemy-lab:protocol:ontology-project-request:v1-candidate',message)
                before=snapshot(workspace);bad=copy.deepcopy(call);bad['call_id']='call:ontology-forged';bad['message']['actor']['principal_ref']='principal:foreign'
                reply=service.call(P.compact(bad));calls.append({'call':bad,'reply':reply});assert reply['kind']=='error' and reply['message']['code']=='unauthorized' and snapshot(workspace)==before
                checks.append({'check':'forged-Actor-refused-before-claim','result':'PASS'})
                bad=copy.deepcopy(call);bad['call_id']='call:ontology-stale';bad['message']['ontology_expected_cut']['commit_sha256']='1'*64
                reply=service.call(P.compact(bad));calls.append({'call':bad,'reply':reply});assert reply['kind']=='error' and snapshot(workspace)==before
                checks.append({'check':'independent-stale-ontology-cut-refused-before-claim','result':'PASS'})
                reply=service.call(P.compact(call));calls.append({'call':copy.deepcopy(call),'reply':reply});assert reply['kind']=='result',reply
                result=reply['message'];assert result['posture']=='applied' and result['ontology_applied_cut']['store_ref']==store
                assert result['ontology_applied_cut']['commit_sequence']==1 and result['lab_source_cut']==cut and len(result['represented_refs'])==25
                viewraw=service.vault.object_read({'ref':'workspace-object:'+service.vault.manifest['workspace_ref']+':'+result['ontology_view']['byte_sha256'],'sha256':result['ontology_view']['byte_sha256']})
                viewbody=P.frame_parse(viewraw);assert viewbody['payload']['replay_source'] is False and len(viewbody['payload']['selected_node_refs'])==15 and len(viewbody['payload']['selected_edge_refs'])==10
                head=P.frame_parse((native_root/'HEAD.json').read_bytes());generation=native_root/head['generation']
                actual=P.source.custody_delivery().MAPPED.call([generation/'semantic',generation/'governance',generation/'request.json'])
                assert actual==(O.MAPPER/'packages/0001/native-output.json').read_bytes()
                checks.append({'check':'observed-native-publication-rich-carriers-independent-head-and-cold-replay','result':'PASS'})
                before=snapshot(workspace);again=copy.deepcopy(call);again['call_id']='call:ontology-exact-retry'
                repeated=service.call(P.compact(again));calls.append({'call':again,'reply':repeated});assert repeated['kind']=='result' and repeated['message']==result and snapshot(workspace)==before
                checks.append({'check':'exact-retry-no-redispatch-or-second-ontology-commit','result':'PASS'})
                view.custody_signed_sources.guard();checks.append({'check':'actual-original-signed-Lab-source-preserved','result':'PASS'})
            finally:service.close();channel.close()
    except Exception:failure=traceback.format_exc()
    G.verify(SOURCE)
    value={'schema_version':'lab-actual-public-ontology-qualification/v1-candidate','result':'PASS' if failure is None and len(checks)==6 else 'FAIL',
        'checks':checks,'actual_calls':calls,'failure':failure,'owned_fixture_removed':owned is not None and not owned.exists(),
        'files':[bind(p) for p in [API/'source-manifest.json',API/'contract-profile.json',RUN/'context-R03-ontology-public-integration-0144.json',Path(__file__).resolve()]],
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'One independently scoped exact signed-source/native ontology projection and its selected refusal/retry/source checks only. No other mapping, Lab admission, active Agent, human pilot, complete ontology/API or whole Lab qualification.'}
    with out.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'checks':checks,'failure':failure,'report_binding':bind(out)}),flush=True)
    return 0 if value['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
