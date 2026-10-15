"""Create a distinct signed branch with preserved learning and exact contest closure."""
import base64
import copy
from dataclasses import asdict
from datetime import datetime,timezone
import tempfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from .base import *
from . import records, integration, resolution_plan

OLD=HERE.parent/'current-participation-v5'
LEARNING=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/Machine-policy-custody-lesson-0001'


def authored_bytes(value):return (' \r\n'+json.dumps(value,indent=4,ensure_ascii=True).replace('\n','\r\n')+'\r\n\t').encode()


def archive(store,pins):
    data=store.replay(require_current=True)
    names=['config.json','baseline.json','HEAD.json']+[f'transactions/{index:010d}.json' for index in range(data['head']['sequence']+1)]
    return {'schema_version':'lab-owned-custody-participation-archive/v1-candidate','engine_pins':asdict(pins),
        'config_sha256':sha((store.path/'config.json').read_bytes()),'baseline_snapshot_digest':data['baseline']['snapshot_digest'],
        'expected_head':data['head']['transaction_digest'],
        'files':{name:{'sha256':sha((store.path/name).read_bytes()),'base64_original_bytes':base64.b64encode((store.path/name).read_bytes()).decode()} for name in names},
        'private_keys_exported':False,'Session_memory_rehydrated':False,'authority_effect':'none','actual_owner_outcome':None}


def main(pin,unused=None):
    verify_source(pin);out=HERE/'packages/0001';require(not out.exists(),'preserve prior package attempt')
    out.mkdir(parents=True,mode=0o700);declared=episode();pins=selected_pins()
    require(datetime.fromisoformat(declared['not_before'])<=datetime.now(timezone.utc)<datetime.fromisoformat(declared['expires_at']),
            'independently fixed fresh episode period is not current')
    require(declared['principal_ref']==records.PRINCIPAL and declared['principal_ref']!=load(OLD/'episode-contract.json')['principal_ref'],
            'new participation must use its distinct fixed identity')
    original_old_period=(OLD/'packages/0001/period.json').read_bytes()
    gate_key=Ed25519PrivateKey.generate();gate_public=gate_key.public_key().public_bytes_raw().hex()
    all_rows=[];phase_rows=[]
    with tempfile.TemporaryDirectory(prefix='cal-R03-integrated-source-0006-') as temporary,loader.engine(pins) as handle:
        owned=Path(temporary);store,key=handle.create_owned(owned,'R03-current-participation-0006',selected_project_scope=True,
            correction_domains=['scope:cyberalchemy-lab-first-agent-episode'])
        def commit(name,targets,originals):
            before=store.replay(require_current=True);config=before['config']
            proposal={'schema_version':'lab-runtime-proposal/v1','proposal_id':'R03-Source6-'+name,
                'expected_head':before['head']['transaction_digest'],'source_snapshot_digest':config['source_snapshot_digest'],
                'scope_ref':config['scope_ref'],'policy_ref':config['policy_ref'],'challenge_route':config['challenge_route'],
                'schemas':{},'targets':copy.deepcopy(targets)}
            proposal=handle.custody.with_originals(proposal,originals,{},exact_schema_bytes=True)
            _,cores=handle.operations.prepare(before['projection'],proposal,before['head']['transaction_digest'],config)
            review=store.review(proposal)
            approval=store.authorize(proposal,key);application=store.apply(proposal,approval);retry=store.apply(proposal,approval)
            require(retry['idempotent'] and retry['transaction_digest']==application['transaction_digest'],'same exact transaction retry redispatched')
            for suffix,value in [('proposal',proposal),('review',review),('approval',approval),('application',application),('retry',retry)]:emit(out/(name+'-'+suffix+'.json'),value)
            after=store.replay(require_current=True)
            for target in targets:
                version=target['version_ref'];raw=originals[version];row=after['projection']['subjects'][version]
                require(row['effective_state']=='local-admitted-current' and row['record']==target['record'],'source postimage differs')
                require(handle.custody.original_bytes(store,version,after['head']['transaction_digest'])==raw,'source original bytes lost')
                all_rows.append({'phase':name,'kind':row['kind'],'version_ref':version,'carrier_ref':target['carrier_ref'],
                    'original_byte_sha256':sha(raw),'byte_provenance':'Preserved selected original' if name.startswith('preserved-') else 'Authored by this exact producer'})
            phase_rows.append({'phase':name,'target_count':len(targets),'independent_cores':len(cores),'exact_retry':True})
            return after
        try:
            setup=load(OLD/'packages/0001/project-setup-proposal.json')['targets']
            raw_setup={target['version_ref']:(OLD/('packages/0001/setup-artifacts/'+target['record'].get('kind',
                'project' if target['carrier_ref']=='cal.artifact-type.project-identity/v1' else 'product')+'.json')).read_bytes() for target in setup}
            data=commit('preserved-project-product',setup,raw_setup)
            targets=load(OLD/'packages/0001/proposal.json')['targets'];old_index=load(OLD/'packages/0001/record-index.json')
            preserved={row['version_ref']:original(row['original_binding']) for row in old_index}
            data=commit('preserved-participation',targets,preserved)
            lesson_index=load(LEARNING/'index.json');require(lesson_index['result']=='PASS' and len(lesson_index['records'])==7,'complete original learning index required')
            targets=[];raws={}
            for row in lesson_index['records']:
                raw=original(row['binding']);body=parse(raw);kind=row['kind'];version=row['version_ref']
                carrier='cal.artifact-type.'+kind+('/v3' if kind=='typed-relation' else '/v1')
                targets.append({'category':'typed-relation' if kind=='typed-relation' else 'artifact-instance','operation':'admit',
                    'version_ref':version,'carrier_ref':carrier,'record':body,'predecessor_ref':None,
                    'decision_ref':'decision:Source6:preserved-learning:'+version,'contract':None});raws[version]=raw
            data=commit('preserved-learning',targets,raws)
            fresh=records.targets(data['projection'],data['config']['scope_ref'],data['config'])
            contest=integration.targets(data['projection'],data['config']['scope_ref'],data['config'],gate_public,
                                        datetime.now(timezone.utc).isoformat())
            raws={target['version_ref']:authored_bytes(target['record']) for target in fresh+contest}
            for index,target in enumerate(fresh+contest):emit(out/('artifacts/'+str(index).zfill(2)+'.json'),None,raw=raws[target['version_ref']])
            data=commit('fresh-participation-and-contest',fresh+contest,raws)
            current=[{**row,'original_binding':binding(out/('artifacts/'+str(index).zfill(2)+'.json')),
                      'encoding':handle.custody.ENCODING} for index,row in enumerate(all_rows[-len(fresh+contest):])]
            emit(out/'record-index.json',current[:len(fresh)]);emit(out/'integrated-record-index.json',all_rows)
            for target in fresh+contest:
                if target['category']=='typed-relation':handle.operations.validate_relation(target['record'],data['projection'])
            emit(out/'review.json',load(out/'fresh-participation-and-contest-review.json'))
            plan=resolution_plan.make(store,handle,data,gate_key,out)
            # Independent signature verification against the exact current original Principal.
            selected=module('_cal_Source6_gate_v2',HERE.parent/'challenge-resolution-v2/gate.py')
            payload=plan['gate']['payload']
            selected.verify(plan['gate'],selected_public_key_hex=gate_public,recognized_principal=integration.OWNER,
                selected_gate_ref=integration.ROUTES['resolution_gate_ref'],owner_route=integration.ROUTES['owner_route'],
                scope_ref=data['config']['scope_ref'],source_cut=payload['source_cut'],challenge=payload['challenge'],
                resolution_decision=payload['resolution_decision'],challenge_contract=payload['challenge_contract'],subject=payload['subject'],
                selected_outcome=payload['selected_outcome'],semantic_proposal_binding=payload['semantic_proposal_binding'],
                governance_proposal_binding=payload['governance_proposal_binding'],evidence_bindings=payload['evidence_bindings'],
                consequence_routes=payload['consequence_routes'],response_obligations=payload['response_obligations'],
                principal_record=data['projection']['subjects'][integration.OWNER+'@'+records.VERSION]['record'],
                policy_expires_at=declared['expires_at'],now=datetime.now(timezone.utc))
            expected={'schema_version':'lab-owned-custody-participation-expected-replay/v1-candidate','engine_pins':asdict(pins),
                'projection_sha256':handle.common.digest(data['projection']),
                'transaction_sha256s':[handle.common.digest(value) for value in data['transactions']],
                'config_sha256':sha((store.path/'config.json').read_bytes()),'baseline_snapshot_digest':data['baseline']['snapshot_digest'],
                'expected_head':data['head']['transaction_digest'],'selected_source_record_index':current,
                'current_Project_State_ref':data['projection']['state']['node_id'],'authority_effect':'none','actual_owner_outcome':None}
            emit(out/'expected-replay.json',expected)
            old_period=HERE.parent/'custody-participation-v1/packages/0001/period.json'
            emit(out/'period.json',{'schema_version':'lab-owned-absolute-participation-period/v1-candidate',
                **{name:declared[name] for name in ('period_ref','not_before','expires_at','principal_ref','assignment_version_ref')},
                'episode_contract_binding':binding(HERE/'episode-contract.json'),'original_expired_period_binding':binding(old_period),
                'constructed_at':datetime.now(timezone.utc).isoformat(),'authority_effect':'none','actual_owner_outcome':None,
                'claim_ceiling':'Distinct owned Source6 period only; Source5 and previous Assignments remain unchanged.'})
            require((OLD/'packages/0001/period.json').read_bytes()==original_old_period,'Source5 period changed')
            verify_source(pin)
            result={'result':'PASS','phases':phase_rows,'signed_transactions':len(phase_rows),
                'preserved_original_targets':30,'fresh_participation_targets':21,'contest_targets':22,
                'actual_original_targets':len(all_rows),'independently_recognized_gate_signature_verified':True,
                'public_API_resolution_qualified':False,'learning_context_qualified':False,
                'private_keys_exported':False,'Session_memory_rehydrated':False,'active_Agents_created':0,
                'canonical_effects_applied':0,'source_effects_applied':0,'authority_effect':'none','actual_owner_outcome':None,'owned_root':str(owned)}
        except Exception as error:
            emit(out/'failure.json',{'result':'FAIL','error_class':type(error).__name__,'reason':str(error),'authority_effect':'none','actual_owner_outcome':None});raise
        finally:
            gate_key=None
            emit(out/'branch.snapshot',archive(store,pins))
    require(not owned.exists(),'owned branch or signer remains');result['owned_store_and_key_removed']=True
    emit(out/'build-result.json',result)
    files=[binding(path) for path in sorted(out.rglob('*')) if path.is_file()]
    emit(out/'manifest.json',{'schema_version':'lab-owned-current-participation-package/v1-candidate','files':files,
        'source_manifest_binding':binding(HERE/'source-manifest.json'),'archive_binding':binding(out/'branch.snapshot'),
        'expected_replay_binding':binding(out/'expected-replay.json'),'period_binding':binding(out/'period.json'),
        'episode_contract_binding':binding(HERE/'episode-contract.json'),'visibility':'private-candidate-original-custody',
        'public_package_export_allowed':False,'authority_effect':'none','actual_owner_outcome':None})
    print(json.dumps({'result':'PASS','source_package_binding':binding(out/'manifest.json'),'actual_original_targets':len(all_rows)}),flush=True)
