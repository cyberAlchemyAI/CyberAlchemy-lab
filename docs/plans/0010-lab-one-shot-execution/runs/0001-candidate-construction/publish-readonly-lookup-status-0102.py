"""Publish actual repaired lookup evidence and retain remaining plan obligations."""
import argparse
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--full-session',type=int,required=True)
    parser.add_argument('--full-initial-chunk',required=True);parser.add_argument('--full-pid',type=int,required=True)
    args=parser.parse_args()
    progress=BASE/'api-v59/receipts/R03-0102.json';proof=load(progress)
    currentness=RUN/'currentness-receipts/0165.json';current=load(currentness)
    assert current['result']=='PASS' and current['completed_tasks']==36 and current['total_tasks']==46
    assert any(r['task']=='R03' and r['receipt']==bind(progress)['path'] for r in current['active_receipt_checks'])
    assert proof['readonly_lookup_runtime_qualified'] and proof['readonly_lookup_actual_public_calls']==5
    for pid in (73615,args.full_pid):assert Path('/proc',str(pid),'stat').exists()
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0102.md'
    with status.open('x') as f:f.write('''# Current Lab candidate progress

**36/46 tasks closed; R03/R06 remain in progress.** The current frozen host is
API59, with twenty authored handlers and fourteen missing public operations.
Construction and isolated verification remain authorized. All-member S02
verification precedes the sole actual R08 owner checkpoint; admission and
activation remain pending.

## Implemented and verified

The full API58 export run completed twelve cases: ten PASS and two FAIL, with no
errors. Both failures found an empty lock file created during lookup before a
rejected request reached its claim. The actual failures and predecessor bytes are
preserved. The run is not qualified as passing.

API59 repairs this read operation. Empty-journal lookup writes nothing. Existing
journal lookup opens the lock without creating it. A durable journal whose lock
is missing is refused without recreation. An authorized claim still creates the
original exclusive writer lock and rechecks its exact fingerprint before dispatch.
Native source guards, authentication, permissions and real clocks are unchanged.

Four focused cases/five authenticated public calls passed with source exit and
owned fixture cleanup: the two unchanged original refusal cases, unknown-operation
inspection of an empty journal, and retry after removing a published operation's
lock. File bytes remain unchanged on each rejected or read-only request. All 305
inherited test methods and all twelve original export test bodies are unchanged.
The full fourteen-case suite on API59 is running; its result is not yet established.

Historical API58 candidate/current-source export and exact-retry proof and API57's
17 classification cases/24 calls remain exact predecessor evidence. They do not
qualify all inherited behavior on API59.

## Remaining work

The original API50 export selection completed all 134 cases, PASS/exit 0. Across
its closed selected scopes, 346 selections have completed: 342 PASS, three FAIL
and one ERROR. These are overlapping suite selections, not unique tests. The same
scheduler continues metadata86, Machine14 and termination6. Original failure
evidence and clocks remain.

Complete all current export and inherited journeys; implement all fourteen
missing operations; finish general foreign/admitted-source import, carrier,
reference and authority adapters, non-JSON privacy/encoding, nonempty
Lesson/Context/Ontology sources and actual Machine write authority. Genuine R05
participant evidence, R06/R07 and final S02/R08 remain. A01-A04 require their
separate authorization.

Currentness165 passed with 38 active receipts, 77 preserved preparation files and
887 original bound sources; no changes were detected. No complete API, genuine
pilot, actual owner outcome, canonical admission, activation or completed plan is
claimed.
''')
    handoff=load(RUN/'custody-integration-handoff-0087.json')
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(currentness),
        current_status_binding=bind(status),current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[42741,84174,23997]))
    handoff['same_live_jobs']=[
        {'session_id':67314,'initial_chunk_id':'c83434','owned_driver_PID':73615,
         'state':'last-observed-running','suite':'API50 original remaining106 scheduler; metadata86 running',
         'driver_binding':bind(RUN/'run-API50-remaining-regression-0002.py'),'whole_API_qualified':False},
        {'session_id':args.full_session,'initial_chunk_id':args.full_initial_chunk,'owned_driver_PID':args.full_pid,
         'state':'last-observed-running','suite':'API59 package export full14',
         'driver_binding':bind(BASE/'api59-export-checks-v1/checks.py'),'whole_API_qualified':False}]
    handoff['terminal_bindings'].extend([proof['readonly_lookup_terminal_binding'],
        proof['historical_API58_export_full12_terminal_binding'],proof['historical_API50_exports134_terminal_binding']])
    handoff['new_scoped_evidence']['API59_readonly_lookup']='4 cases/5 actual calls PASS; no preclaim/read lock creation, missing durable lock refused without recreation. Full14 live.'
    handoff['new_scoped_evidence']['API58_full_export']='12 cases completed, ten PASS/two FAIL. Original refusal cases exposed lock-file side effect; evidence preserved.'
    handoff['new_scoped_evidence']['API50_exports134']='134 cases PASS/exit0. Exact historical source only; not current API59 qualification.'
    handoff['next_action']=proof['remaining_obligations']
    hp=RUN/'custody-integration-handoff-0088.json';emit(hp,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0102.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate',
        'publisher_binding':bind(Path(__file__).resolve()),'progress_binding':bind(progress),
        'currentness_binding':bind(currentness),'status_binding':bind(status),'handoff_binding':bind(hp),
        'closed_tasks':36,'total_tasks':46,'authored_handlers':20,'unimplemented_operations':14,
        'readonly_lookup_cases_passed':4,'readonly_lookup_public_calls':5,'current_export_full14_qualified':False,
        'historical_full_export_failed_cases':2,'historical_export_regression_cases_passed':134,
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(hp),'goal_complete':False}),flush=True)
if __name__=='__main__':main()
