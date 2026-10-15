"""Publish scoped current evidence while keeping the complete plan open."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    progress=BASE/'api-v57/receipts/R03-0100.json';proof=load(progress)
    currentness=RUN/'currentness-receipts/0163.json';current=load(currentness)
    assert current['result']=='PASS' and current['completed_tasks']==36 and current['total_tasks']==46
    assert any(r['task']=='R03' and r['receipt']==progress.relative_to(ROOT).as_posix() for r in current['active_receipt_checks'])
    assert proof['pending_native_evidence_runtime_qualified'] and proof['pending_native_evidence_actual_public_calls']==4
    assert proof['historical_API56_classification_full16_qualified'] and not proof['current_API57_classification_full17_qualified']
    for pid in (73615,84106,89502):assert Path('/proc',str(pid),'stat').exists()
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0100.md'
    with status.open('x') as stream:
        stream.write('''# Current Lab candidate progress

**36/46 tasks closed; R03/R06 remain in progress.** All34 public operations stay
in scope. Nineteen handlers are authored and15 operations are missing. Candidate
construction and isolated verification remain authorized. Complete all-member S02
before the sole actual R08 owner checkpoint; admission and activation stay pending.

## Implemented and verified

API57 makes retained native validation evidence discoverable through authenticated
`operation.inspect`. After original source exit succeeds, it records exact evidence
bindings against the original pending claim hash and principal. The observation
does not complete the operation. Inspection returns the retained failed report's
binding while preserving `indeterminate`, null result, required reconciliation and
`retry_allowed: false`. Exact retry returns `recovery-required`. Corrupted claim
bindings are refused. No admission, classifier result or Agent memory is created.

One added case/four actual authenticated calls passed, exit0, with original source
exit and owned fixture cleanup. The initial test request-budget error and initial
freeze path-representation failure remain preserved. Their successors fix the
construction errors; runtime source guards and original tests are unchanged.

Separately, API56 completed its full16 classification cases/20 authenticated calls,
all PASS/exit0. This includes exact independent-axis proposals with nine targets,
four explicit typed relations, original signatures/endpoints/qualifiers, failed
native verification retention and pending retry refusal. That proof belongs to
API56. The full17 classification run against current API57 is now live; its result
is not yet established. All293 inherited original test methods remain unchanged.

API55's seven affected Session cases, original two expiry cases and three import
cases/nine calls remain exact predecessor evidence. Its import scope is controlled
same-cut Work candidates. General portable import/export remains unfinished.

## Remaining work and live qualification

The original API50 scheduler continues exports134 and then its other remaining
selections. Its completed scopes retain212 selections:208 PASS,three FAIL andone
ERROR. Failures and original clocks remain. Older proof does not qualify API57.

Complete the current17 classification run, all15 missing public operations,
general foreign/admitted package authority and carrier closure, public export
privacy/dependency closure, nonempty Lesson/Context/Ontology sources, Machine write
authority and internal/specialized authority resolvers. Genuine R05 pilot evidence,
R06/R07 and final S02/R08 remain. A01-A04 require their separate authorization.

Currentness163 passed with no linked evidence or original preparation changes.
The paired progress index and handoff bind the exact reports and running jobs.
No complete API, genuine pilot, owner outcome, repository admission, service
activation or completed plan is claimed.
''')
    handoff=load(RUN/'custody-integration-handoff-0085.json')
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(currentness),
        current_status_binding=bind(status),current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[82302,53244,63123,43841,35087,55249,87005]))
    handoff['same_live_jobs']=[
        {'session_id':67314,'initial_chunk_id':'c83434','owned_driver_PID':73615,'owned_child_PID':84106,
         'state':'last-observed-running','suite':'API50 remaining240; exports134 running',
         'driver_binding':bind(RUN/'run-API50-remaining-regression-0002.py'),'whole_API_qualified':False},
        {'session_id':7381,'initial_chunk_id':'8e742c','owned_driver_PID':89502,
         'state':'last-observed-running','suite':'API57 classification full17',
         'driver_binding':bind(BASE/'api57-classification-checks-v2/checks.py'),'whole_API_qualified':False}]
    handoff['terminal_bindings'].extend([proof['pending_native_evidence_terminal_binding'],
        proof['historical_API56_classification_full16_terminal_binding'],proof['failed_pending_test_terminal_binding']])
    handoff['new_scoped_evidence']['API57_pending_native_evidence']='1 case/4 calls PASS. Inspectable failed native report, pending claim, null result, no retry; claim-binding tamper refused. Full17 current qualification live.'
    handoff['new_scoped_evidence']['API56_full_classification']='All16 cases/20 authenticated calls PASS/exit0. Exact predecessor only.'
    handoff['next_action']=proof['remaining_obligations']
    handoff_path=RUN/'custody-integration-handoff-0086.json';emit(handoff_path,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0100.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate',
        'publisher_binding':bind(Path(__file__).resolve()),'progress_binding':bind(progress),
        'currentness_binding':bind(currentness),'status_binding':bind(status),'handoff_binding':bind(handoff_path),
        'closed_tasks':36,'total_tasks':46,'authored_handlers':19,'unimplemented_operations':15,
        'pending_native_evidence_cases_passed':1,'pending_native_evidence_public_calls':4,
        'historical_full_classification_cases_passed':16,'current_full_classification_qualified':False,
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),
        'handoff':bind(handoff_path),'goal_complete':False}),flush=True)

if __name__=='__main__':main()
