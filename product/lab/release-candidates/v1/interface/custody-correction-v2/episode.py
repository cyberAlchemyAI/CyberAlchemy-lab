"""Exact reviewed correction revisions in a fresh explicitly owned signed store."""
from dataclasses import asdict
import base64
import copy
import re
import time
from loader import *

EXAMPLES=ROOT/'product/lab/release-candidates/v1/examples/operator-journeys/corrections'
DOMAIN='scope:cyberalchemy-lab-first-agent-episode'


def emit(path,value):
    with Path(path).open('xb') as stream:stream.write(encoded(value))


def base_proposal(data,name,targets):
    c=data['config']
    return {'schema_version':'lab-runtime-proposal/v1','proposal_id':name,'expected_head':data['head']['transaction_digest'],
        'source_snapshot_digest':c['source_snapshot_digest'],'scope_ref':c['scope_ref'],'policy_ref':c['policy_ref'],
        'challenge_route':c['challenge_route'],'schemas':{},'targets':targets}


def project_setup(handle,store,key):
    data=store.replay(require_current=True);old=data['projection']['subjects']['project:cyberalchemy-v2-to-lab-migration@foundation.1']
    target={'category':'artifact-instance','operation':'revise','version_ref':old['identity']+'@1.0.0-candidate.1',
        'predecessor_ref':old['version_ref'],'carrier_ref':old['carrier_ref'],'record':copy.deepcopy(old['record']),
        'decision_ref':'decision:R03-reference-correction:project-setup','contract':None}
    proposal=base_proposal(data,'R03-correction-project-setup',[target]);approval=store.authorize(proposal,key);applied=store.apply(proposal,approval)
    return {'proposal':proposal,'approval':approval,'application':applied}


def correction_proposal(handle,data,name='R03-reviewed-reference-corrections'):
    targets=[]
    for b in handle.corrections.profile()['member_bindings']:
        member=handle.corrections.exact_document(data['projection'],b)
        predecessor=data['projection']['subjects'][member['predecessor_version_ref']]
        targets.append({'category':'typed-relation','operation':'revise','version_ref':member['version_ref'],
            'carrier_ref':predecessor['carrier_ref'],'record':copy.deepcopy(handle.corrections.exact_document(data['projection'],member['record_binding'])),
            'predecessor_ref':member['predecessor_version_ref'],'decision_ref':'decision:R03-reference-correction:'+member['identity_ref'].rsplit(':',1)[-1],
            'contract':None,'reference_correction_binding':copy.deepcopy(b)})
    proposal=base_proposal(data,name,targets)
    proposal.update(schema_version='lab-runtime-proposal/v2-candidate',correction_profile_binding=handle.corrections.binding())
    return proposal


def archive(store,pins):
    data=store.replay(require_current=True)
    names=['config.json','baseline.json','HEAD.json']+[f'transactions/{i:010d}.json' for i in range(data['head']['sequence']+1)]
    files={name:{'sha256':sha((store.path/name).read_bytes()),'base64_original_bytes':base64.b64encode((store.path/name).read_bytes()).decode()} for name in names}
    return {'schema_version':'lab-reference-correction-archive/v1-candidate','engine_pins':asdict(pins),
        'config_sha256':files['config.json']['sha256'],'baseline_snapshot_digest':data['baseline']['snapshot_digest'],
        'expected_head':data['head']['transaction_digest'],'files':files,'private_keys_exported':False,'authority_effect':'none','actual_owner_outcome':None}


def restore(path,expected_sha,destination,pins):
    path=Path(path);require(sha(path.read_bytes())==expected_sha,'independent correction archive digest differs')
    value=parse(path.read_bytes());require(value['engine_pins']==asdict(pins),'independent correction archive engine differs')
    destination=Path(destination);require(not destination.exists() and destination.is_relative_to(Path('/tmp')) and not destination.is_relative_to(ROOT),'fresh owned cold destination required')
    destination.mkdir();(destination/'transactions').mkdir()
    for name,b in value['files'].items():
        require(name in ['config.json','baseline.json','HEAD.json'] or re.fullmatch(r'transactions/[0-9]{10}\.json',name),'unsafe archive entry')
        raw=base64.b64decode(b['base64_original_bytes'],validate=True);require(sha(raw)==b['sha256'],'original archive bytes differ')
        with (destination/name).open('xb') as stream:stream.write(raw)
    with engine(pins) as handle:data=handle.replay_owned(destination,value['config_sha256'],value['baseline_snapshot_digest'],value['expected_head'])
    return data


def verify_result(handle,before,after,proposal):
    rows=[]
    for target in proposal['targets']:
        subject=after['projection']['subjects'][target['version_ref']];prior=after['projection']['subjects'][target['predecessor_ref']]
        require(subject['record']==target['record'] and subject['effective_state']=='local-admitted-current'
            and prior['record']==before['projection']['subjects'][target['predecessor_ref']]['record']
            and prior['effective_state']=='local-admitted-historical','correction/original effective postimages differ')
        handle.operations.validate_relation(subject['record'],after['projection'],allow_historical=True)
        proof=subject['reference_correction_proof'];require(proof['domain_scope_ref']==DOMAIN,'correction domain scope collapsed')
        cores=after['transactions'][-1]['decision_cores'];core=next(c for c in cores if c['version_ref']==subject['version_ref'])
        require(all(core[k]==v for k,v in proof.items()),'independent correction core omitted declared scope/profile/witness')
        decision=next(s for s in after['projection']['subjects'].values() if s['identity']==target['decision_ref'])
        scope=next(r for r in after['transactions'][-1]['consequences']['governance_records'] if r['kind']=='decision-scope'
            and r['payload']['subject_refs']==[target['version_ref']])
        require(decision['record']['scope_ref']==scope['scope_ref']==DOMAIN,'independent correction Decision scope differs')
        rows.append({'version_ref':subject['version_ref'],'predecessor_ref':prior['version_ref'],'source_binding':subject['source'],
            'effective_state':subject['effective_state'],'original_effective_state':prior['effective_state'],'correction_proof':proof,
            'record_structural_sha256':handle.common.digest(subject['record']),'decision_ref':core['decision_ref']})
    require(len(rows)==10 and len({r['decision_ref'] for r in rows})==10,'ten independent applied corrections required')
    return rows


def run(destination,pins):
    destination=Path(destination).resolve();require(destination.is_relative_to(EXAMPLES) and not destination.exists(),'fresh selected correction example root required')
    destination.mkdir(parents=True);start=time.perf_counter();outcome=None
    with tempfile.TemporaryDirectory(prefix='cal-R03-correction-owned-') as temporary,engine(pins) as handle:
        owned=Path(temporary);store,key=handle.create_owned(owned,'R03-reference-corrections',selected_project_scope=True,correction_domains=[DOMAIN])
        try:
            setup=project_setup(handle,store,key);emit(destination/'project-setup.json',setup)
            before=store.replay(require_current=True);proposal=correction_proposal(handle,before)
            emit(destination/'proposal.json',proposal)
            post,cores=handle.operations.prepare(before['projection'],proposal,before['head']['transaction_digest'],before['config'])
            emit(destination/'review.json',store.review(proposal))
            approval=store.authorize(proposal,key);emit(destination/'approval.json',approval)
            applied=store.apply(proposal,approval);emit(destination/'application.json',applied)
            retry=store.apply(proposal,approval);require(retry['idempotent'] and retry['transaction_digest']==applied['transaction_digest'],'exact correction retry differs')
            emit(destination/'retry.json',retry);after=store.replay(require_current=True);rows=verify_result(handle,before,after,proposal)
            expected={'projection_sha256':handle.common.digest(after['projection']),'transaction_sha256s':[handle.common.digest(t) for t in after['transactions']],
                'applied_corrections':rows,'config_sha256':sha((store.path/'config.json').read_bytes()),'expected_head':after['head']['transaction_digest'],
                'baseline_snapshot_digest':after['baseline']['snapshot_digest'],'engine_pins':asdict(pins)}
            emit(destination/'expected-replay.json',expected)
            outcome={'result':'PASS','applied_corrections':10,'independent_correction_decisions':10,'signed_transactions':2,
                'project_setup_transactions':1,'correction_transactions':1,'idempotent_retry':True,
                'proposal_scope_ref':after['config']['scope_ref'],'record_domain_scope_refs':[DOMAIN],
                'config_scope_grants_bound_in_signature':True,'source_effects_applied':0,'canonical_effects_applied':0,
                'private_keys_exported':False,'Session_memory_exported':False,'human_pilot':False,'authority_effect':'none','actual_owner_outcome':None,
                'signature_basis':'Independent freshly provisioned controlled signer for this owned candidate store; no human/canonical owner response.',
                'original_source_records_preserved':True,'duration_seconds':time.perf_counter()-start}
        except Exception as error:
            emit(destination/'failure.json',{'result':'FAIL','error_class':type(error).__name__,'reason':str(error),
                'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0})
            raise
        finally:emit(destination/'branch.snapshot',archive(store,pins))
    require(not owned.exists(),'owned correction store/key remain');outcome['owned_store_and_key_removed']=True
    emit(destination/'result.json',outcome);print(json.dumps(outcome,sort_keys=True))
    return outcome


if __name__=='__main__':
    require(len(sys.argv)==3,'usage: episode.py fresh-selected-output pins-json');run(sys.argv[1],EnginePins(**parse(Path(sys.argv[2]).read_bytes())))
