"""Two exact fresh runs sharing a cache, interruption/resume and owned controls."""
from pathlib import Path
import copy
import json
import os
import sys
import threading
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,check,binding
from v3.p07.api import OwnedQualifier
from v3.p07.cache import CacheAnchor
from v3.p07.runs import inspect_record,execution_state,validate,cleanup_proposal,owner
sys.path.insert(0,str(BASE/'execution'));import support as s
controls=[];runs=[]
def control(name,ok):
    s.require(ok,name);controls.append({'name':name,'result':'pass'})
    s.write(HERE/'repeatability-progress.json',{'complete':False,'controls':controls,'runs':runs})
def save(name,a):
    p=HERE/(name+'.json');s.write(p,a);runs.append(s.binding(p));return a
def rejected(name,call):
    try:call()
    except Exception:control(name,True);return
    raise ValueError('negative control accepted '+name)
req=s.read(BASE/'p01/request-fixture.json');policy=req['resource_policy'];raw=json.dumps(req,ensure_ascii=False).encode()
api=OwnedQualifier(HERE/'runs',policy)
a=save('first-result',api.qualify(raw));control('first-rich-run-fresh-qualified',a['status']=='qualified-candidate')
r=a['qualified_result'];control('first-owned-event-live',api.live_event(r))
first_job=Path(a['supervised_run']['job']);first_snapshot={str(p):s.digest(p) for p in first_job.rglob('*') if p.is_file()}
control('all-final-first-files-private-read-only',all((p.stat().st_mode&0o777)==0o400 for p in first_job.rglob('*') if p.is_file()))
control('all-final-first-directories-private-read-only',(first_job.stat().st_mode&0o777)==0o500 and all((p.stat().st_mode&0o777)==0o500 for p in first_job.rglob('*') if p.is_dir()))
control('first-final-record-current-without-fresh-event',inspect_record(a['owned_run'])['status']=='recorded-current' and not inspect_record(a['owned_run'])['fresh_qualification'])
req_b=copy.deepcopy(req);req_b['proposal']['proposal_id']='rich-repeatability-second-request'
b=save('second-result',api.qualify(json.dumps(req_b,ensure_ascii=False).encode()))
control('second-different-request-fresh-qualified',b['status']=='qualified-candidate' and b['qualified_result']['request_identity']!=r['request_identity'])
control('distinct-owned-job-and-proof-run',a['supervised_run']['job']!=b['supervised_run']['job'] and r['run_id']!=b['qualified_result']['run_id'])
records=[s.read(check(x['owned_run'])) for x in [a,b]]
control('different-requests-share-exact-anchored-cache',records[0]['cache_check']['cache_key']==records[1]['cache_check']['cache_key'])
control('second-run-cannot-rewrite-first-evidence',all(s.digest(Path(p))==sha for p,sha in first_snapshot.items()))
control('first-event-remains-valid-after-second-run',api.live_event(r))
ca=CacheAnchor('staged');cb=CacheAnchor('combined')
control('layout-policy-affects-cache-key',ca.key!=cb.key)
metadata=copy.deepcopy(ca.metadata);metadata['modules'][0]['olean']['sha256']='0'*64
rejected('self-certified-replacement-cache-metadata-refused',lambda:ca.verify_metadata_bytes(json.dumps(metadata).encode()))
rejected('truncated-cache-metadata-refused',lambda:ca.verify_metadata_bytes(b'{}'))
state=execution_state(s.read(s.PLAN));validate('execution-state',state)
control('all-selected-extensions-remain-outstanding-optional',state['remaining_optional']==['E0'+str(i) for i in range(7)] and not state['resolved_optional'])
test_plan=copy.deepcopy(s.read(s.PLAN));next(t for t in test_plan['tasks'] if t['id']=='E00')['selected']=False
test_state=execution_state(test_plan)
control('unselected-optional-resolution-excluded-from-remaining','E00' not in test_state['remaining_optional'] and {'id':'E00','resolution':'not-needed'} in test_state['resolved_optional'])
bad_plan=copy.deepcopy(test_plan);next(t for t in bad_plan['tasks'] if t['id']=='P08')['selected']=False
rejected('required-task-cannot-be-not-needed',lambda:execution_state(bad_plan))
rejected('completed-run-excluded-from-cleanup',lambda:cleanup_proposal(a['owned_run'],first_job))
rejected('cleanup-cannot-target-other-run',lambda:cleanup_proposal(a['owned_run'],Path(b['supervised_run']['job'])))
new_api=OwnedQualifier(HERE/'other-session',policy)
control('saved-owned-record-does-not-create-live-event',not new_api.live_event(r))
cancel=threading.Event();timer=threading.Timer(2,cancel.set);timer.start()
try:interrupted=save('interrupted-result',api.qualify(raw,cancel=cancel))
finally:timer.cancel()
control('interrupted-run-nonqualified-and-finalized',interrupted['status']=='cancelled' and interrupted['qualified_result'] is None and inspect_record(interrupted['owned_run'])['phase']=='cancelled')
source_job=Path(interrupted['supervised_run']['job']);phase=sorted(source_job.glob('phase-*.json'))[-1];phase_ref=s.binding(phase)
control('interrupted-phase-is-byte-bound-and-read-only',(phase.stat().st_mode&0o777)==0o400)
old_snapshot={str(p):s.digest(p) for p in source_job.rglob('*') if p.is_file()}
resumed=save('resumed-result',api.resume(phase_ref,raw))
control('resume-is-a-new-fresh-rich-qualification',resumed['status']=='qualified-candidate' and resumed['qualified_result']['run_id']!=r['run_id'] and api.live_event(resumed['qualified_result']))
resume_job=Path(resumed['supervised_run']['job']);resume_validation=s.read(resume_job/'resume-validation.json')
control('resume-retains-exact-old-phase-provenance',resume_validation['source_phase']==phase_ref and not resume_validation['reused_qualification'])
control('resume-preserves-interrupted-evidence',all(s.digest(Path(p))==sha for p,sha in old_snapshot.items()))
wrong=save('changed-request-resume-result',api.resume(phase_ref,raw+b' '))
control('changed-request-byte-resume-refused',wrong['status']=='invalid' and wrong['qualified_result'] is None and 'request bytes' in wrong['reason'])
policy2=copy.deepcopy(policy);policy2['stage_seconds']=59
wrong=save('changed-policy-resume-result',OwnedQualifier(HERE/'runs',policy2).resume(phase_ref,raw))
control('changed-policy-resume-refused',wrong['status']=='invalid' and 'policy' in wrong['reason'])
fake=HERE/'fixtures/job-transplant';fake.mkdir(parents=True,exist_ok=True);own=owner(fake)
value=copy.deepcopy(records[0]);value['run_id']=fake.name;value['owner']=own
s.write(fake/'owned-run-record.json',value)
rejected('run-output-transplant-refused',lambda:inspect_record(s.binding(fake/'owned-run-record.json')))
control('retained-issuance-recipe-exact',s.read(HERE/'api-recipe-review.json')['roundtrip']=='exact')
report={'result':'pass','controls':controls,'runs':runs,'actual_fresh_qualifications':3,'actual_interrupted_runs':1,
        'accepted_inputs_unchanged':True,'authority_effect':'none'}
s.write(HERE/'repeatability-controls.json',report)
print('P07 repeatability controls passed: '+str(len(controls)),flush=True)
