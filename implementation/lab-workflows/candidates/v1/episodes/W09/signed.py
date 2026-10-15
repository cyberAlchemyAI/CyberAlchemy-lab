"""Exact fresh W09 relation/endpoints in owned signed coupling witness stores."""
from control import *
from dataclasses import asdict
import tempfile
sys.path.insert(0,str(ROOT/'product/lab/release-candidates/v1/interface/coupling'))
coupling=module('_W09_signed_coupling',ROOT/'product/lab/release-candidates/v1/interface/coupling/episode.py')
PARENT=ROOT/'implementation/lab-workflows/candidates/v1/tests/signed_integration/selection.json'
PARENT_SHA='6e5d8e24325e45c6801d64161b23539190c78befb2bf9d8f1a9d0f2819ffb1db'

def engine_pins():
    require(sha(PARENT.read_bytes())==PARENT_SHA,'exact reviewed coupling selection changed')
    v=load(PARENT);require(v['engine_manifest_binding']==bind(coupling.HERE/'engine-manifest.json'),'exact engine manifest differs')
    pins=coupling.EnginePins(**v['engine_pins']);coupling.verify_engine(pins);return pins

def targets_for(handle,store,case):
    suffix=':engineering-evidence-membership@candidate.1' if case['domain']=='engineering' else ':experiment-project@candidate.1'
    rows=[r for r in case['records'] if r['version_ref'].endswith(suffix)];require(len(rows)==1,'exact new represented Project relation required')
    rr=rows[0];relation=load(ROOT/rr['path']);original({k:rr[k] for k in ['path','sha256']})
    projection=store.replay()['projection'];targets=[];witnesses=[]
    for endpoint in [relation['payload']['source'],relation['payload']['target']]:
        rows=[r for r in case['records'] if r['version_ref']==endpoint['version_ref']];require(len(rows)==1,'unique exact endpoint required')
        row=rows[0];binding={k:row[k] for k in ['path','sha256']};record=load(ROOT/row['path']);original(binding)
        current=[s for s in projection['subjects'].values() if s['identity']==endpoint['ref'] and s['effective_state'] in ['admitted-current','local-admitted-current']]
        require(len(current)<=1 and endpoint['version_ref'] not in projection['subjects'],'ambiguous or reused endpoint revision')
        predecessor=current[0]['version_ref'] if current else None
        decision='decision:W09:'+case['case_id']+':endpoint:'+str(len(targets))
        targets.append(coupling.target(endpoint['version_ref'],coupling.carrier_for(projection,row['kind']),record,decision,predecessor=predecessor))
        witnesses.append({'version_ref':endpoint['version_ref'],'kind':row['kind'],'source_binding':binding,'record_rewritten':False,
            'original_structural_sha256':handle.common.digest(record),'predecessor_ref':predecessor})
    targets.append(coupling.target(rr['version_ref'],coupling.carrier_for(projection,'typed-relation'),relation,'decision:W09:'+case['case_id']+':relation',category='typed-relation'))
    witnesses.append({'version_ref':rr['version_ref'],'kind':'typed-relation','source_binding':{k:rr[k] for k in ['path','sha256']},
        'original_structural_sha256':handle.common.digest(relation),'record_rewritten':False,'predecessor_ref':None})
    return targets,witnesses,rr['version_ref']

def run(case_path,dest):
    case_path=Path(case_path).resolve();dest=Path(dest).resolve()
    require(case_path.is_relative_to(HERE/'runs') and dest.is_relative_to(HERE/'runs') and not dest.exists(),'new owned W09 case/destination required')
    case_binding=bind(case_path);case=load(case_path);require(case['domain'] in ['engineering','research'],'closed W09 coupling domain')
    pins=engine_pins();selection();dest.mkdir(parents=True);started=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='cal-W09-coupling-') as temp,coupling.engine(pins) as handle:
        owned=Path(temp);store,key=handle.create_owned(owned,'W09-'+case['domain']+'-'+selection()['run_namespace'],selected_project_scope=True)
        targets,witnesses,relation_ref=targets_for(handle,store,case)
        proposal=coupling.proposal_for(store,'W09-'+case['domain']+'-'+selection()['run_namespace'],targets)
        before=store.replay();post,cores=handle.operations.prepare(before['projection'],proposal,before['head']['transaction_digest'],before['config'])
        require(len(cores)==3 and len({r['decision_ref'] for r in cores})==3,'independent Decision cores missing')
        relation=next(t['record'] for t in targets if t['version_ref']==relation_ref)
        frozen_rejection=coupling.frozen_kind_rejection(handle,post,relation)
        review=store.review(proposal);require(review['target_count']==3,'exact review incomplete')
        approval=store.authorize(proposal,key);require(key.stat().st_mode&0o777==0o600,'owned private key mode differs')
        outcome=store.apply(proposal,approval);retry=store.apply(proposal,approval)
        require(retry['idempotent'] and retry['transaction_digest']==outcome['transaction_digest'],'retry changed signed result')
        after=store.replay(require_current=True);p=after['projection'];handle.operations.validate_relation(p['subjects'][relation_ref]['record'],p)
        require(all(p['subjects'][t['version_ref']]['record']==t['record'] for t in targets),'committed postimages differ from exact selected originals')
        views=[handle.mapping.explain(p['subjects'][e['version_ref']],p) for e in [relation['payload']['source'],relation['payload']['target']]]
        archive=coupling.archive(store,pins);emit(dest/'branch.snapshot',archive)
        for name,v in [('proposal',proposal),('review',review),('approval',approval),('application',outcome),('retry',retry)]:emit(dest/(name+'.json'),v)
        emit(dest/'original-source-witnesses.json',{'case_binding':case_binding,'selected_records':witnesses,'raw_source_records_rewritten':False,'original_domain_cases_reexecuted':0,'actual_owner_outcome':None})
        expected={'engine_pins':asdict(pins),'projection_sha256':handle.common.digest(p),'transaction_sha256s':[handle.common.digest(t) for t in after['transactions']],
            'relation_ref':relation_ref,'archive_binding':bind(dest/'branch.snapshot'),'endpoint_views':views,'case_binding':case_binding,
            'config_sha256':archive['config_sha256'],'baseline_snapshot_digest':archive['baseline_snapshot_digest'],'expected_head':archive['expected_head']}
        emit(dest/'expected-replay.json',expected)
    require(not owned.exists(),'owned witness store/private key remains')
    result={'result':'PASS','domain':case['domain'],'source_case_binding':case_binding,'exact_targets':3,'distinct_Decision_cores':3,'signed_transactions':1,
        'fixture_signature_verified':True,'idempotent_retry':True,'owned_store_and_key_removed':True,'frozen_rejection':frozen_rejection,
        'endpoint_views':views,'expected_binding':bind(dest/'expected-replay.json'),'canonical_effects_applied':0,'actual_owner_outcome':None,
        'authority_effect':'none','runtime_activation':False,'private_key_exported':False,'Session_memory_exported':False,'duration_seconds':time.perf_counter()-started}
    emit(dest/'result.json',result);print(encoded(result).decode(),end='')
if __name__=='__main__':
    require(len(sys.argv)==3,'usage: signed.py exact-case fresh-output');run(sys.argv[1],sys.argv[2])
