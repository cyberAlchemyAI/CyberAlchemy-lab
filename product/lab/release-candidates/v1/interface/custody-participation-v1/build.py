"""Author new actual bytes and independently sign a newly owned source cut."""
import base64,copy,tempfile,time
from dataclasses import asdict
from datetime import datetime,timezone
from .base import *
from . import records
DOMAIN='scope:cyberalchemy-lab-first-agent-episode'
PRIOR_PERIOD=HERE.parent/'session-participation-v2/packages/0001/period.json'
def raw_json(value):return (' \r\n'+json.dumps(value,indent=4,ensure_ascii=True,allow_nan=False).replace('\n','\r\n')+'\r\n\t').encode()
def proposal(data,identity,targets,handle,raws):
    c=data['config'];p={'schema_version':'lab-runtime-proposal/v1','proposal_id':identity,
        'expected_head':data['head']['transaction_digest'],'source_snapshot_digest':c['source_snapshot_digest'],
        'scope_ref':c['scope_ref'],'policy_ref':c['policy_ref'],'challenge_route':c['challenge_route'],'schemas':{},'targets':targets}
    return handle.custody.with_originals(p,raws,{},exact_schema_bytes=True)
def archive(store,pins):
    data=store.replay(require_current=True)
    names=['config.json','baseline.json','HEAD.json']+[f'transactions/{i:010d}.json' for i in range(data['head']['sequence']+1)]
    files={n:{'sha256':sha((store.path/n).read_bytes()),'base64_original_bytes':base64.b64encode((store.path/n).read_bytes()).decode()} for n in names}
    return {'schema_version':'lab-owned-custody-participation-archive/v1-candidate','engine_pins':asdict(pins),
        'config_sha256':files['config.json']['sha256'],'baseline_snapshot_digest':data['baseline']['snapshot_digest'],
        'expected_head':data['head']['transaction_digest'],'files':files,'private_keys_exported':False,
        'historical_provenance_protection':'private-original-custody-not-public-package','Session_memory_rehydrated':False,
        'authority_effect':'none','actual_owner_outcome':None}
def main(pin,unused=None):
    verify_source(pin);out=HERE/'packages/0001';require(not out.exists(),'refuse source package overwrite')
    out.mkdir(parents=True,mode=0o700);start=time.monotonic();pins=selected_pins();prior=load(PRIOR_PERIOD)
    now=datetime.now(timezone.utc);require(datetime.fromisoformat(prior['not_before'])<=now<datetime.fromisoformat(prior['expires_at']),'original absolute source validity ended')
    with tempfile.TemporaryDirectory(prefix='cal-R03-original-participation-') as temporary,loader.engine(pins) as handle:
        owned=Path(temporary);store,key=handle.create_owned(owned,'R03-original-participation-0001',selected_project_scope=True,correction_domains=[DOMAIN])
        try:
            before=store.replay(require_current=True);scope=before['config']['scope_ref'];setup=[];setup_originals={}
            for identity in [scope,'product:cyberalchemy-lab']:
                rows=[s for s in before['projection']['subjects'].values() if s['identity']==identity and s['effective_state']=='admitted-current']
                require(len(rows)==1,'unique original Project/Product source absent');old=rows[0];body=copy.deepcopy(old['record'])
                version=identity+('@'+body['version'] if identity==scope else '@original-reader.candidate.1')
                require(version!=old['version_ref'],'setup requires explicit new immutable revision')
                t={'category':'artifact-instance','operation':'revise','version_ref':version,'carrier_ref':old['carrier_ref'],
                    'record':body,'predecessor_ref':old['version_ref'],'decision_ref':'decision:R03-original-participation:setup:'+old['kind'],'contract':None}
                setup.append(t);raw=raw_json(body);setup_originals[version]=raw
                emit(out/('setup-artifacts/'+old['kind']+'.json'),None,raw=raw)
            setup_proposal=proposal(before,'R03-original-project-product-source-setup',setup,handle,setup_originals)
            emit(out/'project-setup-proposal.json',setup_proposal);setup_approval=store.authorize(setup_proposal,key)
            emit(out/'project-setup-approval.json',setup_approval);emit(out/'project-setup-application.json',store.apply(setup_proposal,setup_approval))
            before=store.replay(require_current=True);items=records.targets(before['projection'],scope,before['config'])
            require(len(items)==21,'all eleven sources and ten Typed Relations required');raws={};index=[]
            for i,t in enumerate(items):
                raw=raw_json(t['record']);path=out/('artifacts/'+str(i).zfill(2)+'.json');emit(path,None,raw=raw);raws[t['version_ref']]=raw
                require(raw!=handle.common.encoded(t['record']),'actual authored originals must exercise distinct encoding')
                index.append({'kind':t['record'].get('kind',before['projection']['contracts'][t['carrier_ref']]['semantic_kind']),
                    'version_ref':t['version_ref'],'carrier_ref':t['carrier_ref'],'original_binding':binding(path),
                    'encoding':handle.custody.ENCODING,'byte_provenance':'New candidate file authored by this frozen producer from exact fixture and declared replacements; no prior original-byte claim.'})
            emit(out/'record-index.json',index);p=proposal(before,'R03-original-reader-participation',items,handle,raws);emit(out/'proposal.json',p)
            post,cores=handle.operations.prepare(before['projection'],p,before['head']['transaction_digest'],before['config'])
            require(len(cores)==21 and post!=before['projection'],'twenty-one independent prospective cores required')
            emit(out/'review.json',store.review(p));approval=store.authorize(p,key);emit(out/'approval.json',approval)
            applied=store.apply(p,approval);emit(out/'application.json',applied);retry=store.apply(p,approval);emit(out/'retry.json',retry)
            require(retry['idempotent'] and retry['transaction_digest']==applied['transaction_digest'],'exact retry must not redispatch')
            after=store.replay(require_current=True)
            for t,row in zip(items,index):
                subject=after['projection']['subjects'][t['version_ref']]
                require(subject['effective_state']=='local-admitted-current' and subject['record']==t['record'],'actual source postimage differs')
                require(subject['source']['sha256']==row['original_binding']['sha256'],'original header bytes lost')
                require(handle.custody.original_bytes(store,t['version_ref'],after['head']['transaction_digest'])==raws[t['version_ref']],'actual original retrieval differs')
                if t['category']=='typed-relation':handle.operations.validate_relation(subject['record'],after['projection'])
            assignment=after['projection']['subjects'][records.ASSIGNMENT+'@'+records.VERSION]['record']['payload']
            require(assignment['eligible_agent_ref']==records.PROFILE+'@'+records.VERSION,'Assignment reused old Agent')
            state=after['projection']['state'];require(state['payload']['project_ref']==scope,'generated state scope differs')
            expected={'schema_version':'lab-owned-custody-participation-expected-replay/v1-candidate','engine_pins':asdict(pins),
                'projection_sha256':handle.common.digest(after['projection']),'transaction_sha256s':[handle.common.digest(t) for t in after['transactions']],
                'config_sha256':sha((store.path/'config.json').read_bytes()),'baseline_snapshot_digest':after['baseline']['snapshot_digest'],
                'expected_head':after['head']['transaction_digest'],'selected_source_record_index':index,'current_Project_State_ref':state['node_id'],
                'authority_effect':'none','actual_owner_outcome':None}
            emit(out/'expected-replay.json',expected)
            emit(out/'period.json',{'schema_version':'lab-owned-absolute-participation-period/v1-candidate','period_ref':records.PERIOD,
                'not_before':prior['not_before'],'expires_at':prior['expires_at'],'principal_ref':records.PRINCIPAL,
                'assignment_version_ref':records.ASSIGNMENT+'@'+records.VERSION,'inherited_validity_binding':binding(PRIOR_PERIOD),
                'constructed_at':datetime.now(timezone.utc).isoformat(),'authority_effect':'none','actual_owner_outcome':None,
                'claim_ceiling':'New owned candidate period declaration bounded to the exact retained absolute interval. No reset, extension or current host permission.'})
            verify_source(pin);outcome={'result':'PASS','authored_current_artifacts':11,'authored_current_typed_relations':10,
                'independent_participation_decision_cores':21,'setup_independent_cores':2,'signed_transactions':2,
                'fresh_Profile_eligible_Assignment':True,'original_target_byte_custody':True,'private_keys_exported':False,
                'Session_memory_rehydrated':False,'active_Agents_created':0,'public_API_operations_added':0,
                'canonical_effects_applied':0,'source_effects_applied':0,'authority_effect':'none','actual_owner_outcome':None,
                'human_pilot_outcome':None,'signature_basis':'New controlled development signer in the newly owned store; no actual owner outcome.',
                'owned_root':str(owned),'duration_seconds':time.monotonic()-start}
        except Exception as error:
            emit(out/'failure.json',{'result':'FAIL','error_class':type(error).__name__,'reason':str(error),'authority_effect':'none','actual_owner_outcome':None});raise
        finally:emit(out/'branch.snapshot',archive(store,pins))
    require(not owned.exists(),'owned store or signer remains');outcome['owned_store_and_key_removed']=True;emit(out/'build-result.json',outcome)
    files=[binding(path) for path in sorted(out.rglob('*')) if path.is_file()]
    manifest={'schema_version':'lab-owned-custody-participation-package/v1-candidate','files':files,'source_manifest_binding':binding(HERE/'source-manifest.json'),
        'archive_binding':binding(out/'branch.snapshot'),'expected_replay_binding':binding(out/'expected-replay.json'),'period_binding':binding(out/'period.json'),
        'visibility':'private-candidate-original-custody','public_package_export_allowed':False,'authority_effect':'none','actual_owner_outcome':None}
    emit(out/'manifest.json',manifest);print(json.dumps({'result':'PASS','package_binding':binding(out/'manifest.json'),'actual_original_targets':23,'records':21}),flush=True)
