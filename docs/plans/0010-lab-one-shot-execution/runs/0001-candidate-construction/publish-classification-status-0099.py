"""Publish completed scoped evidence and unfinished current plan."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')

def main():
    progress=BASE/'api-v56/receipts/R03-0099.json'
    proof=load(progress)
    currentness=RUN/'currentness-receipts/0162.json'
    current=load(currentness)
    assert current['result']=='PASS' and current['completed_tasks']==36 and current['total_tasks']==46
    assert any(row['task']=='R03' and row['receipt']==progress.relative_to(ROOT).as_posix() for row in current['active_receipt_checks'])
    assert proof['classification_focused_actual_cases']==3 and proof['classification_focused_actual_public_calls']==4
    assert proof['implemented_public_handlers']==19 and proof['unimplemented_public_operation_count']==15
    assert not proof['whole_API_qualified'] and not proof['task_complete']
    for pid in (73615,84106,86499):assert Path('/proc',str(pid),'stat').exists()
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0099.md'
    with status.open('x') as stream:
        stream.write('''# Current Lab candidate progress

**36/46 tasks closed. R03 and R06 remain in progress.** All34 public contracts
remain in scope:19 handlers are authored and15 operations are missing. The actual
R08 owner checkpoint follows complete S02. This candidate authorization covers
development and isolated verification; admission and activation remain pending.

## Completed evidence

API56 binds classification preparation v8. Three focused cases/four authenticated
calls passed, with full original source exit and owned fixture cleanup. The separate
independent-axis case proves the exact nine-target proposal (five domain targets,
four declared typed relations), original signatures, endpoint pairs and qualifiers.
Both unchanged original bad-core tests pass. Failed native validation evidence
persists while the operation stays pending: no classifier or command result is
recorded, and exact retry requires reconciliation. The full16 run is still live.

API55 completed seven affected Session cases and three package-import cases/nine
calls, all PASS/exit0. Its two original real-clock expiry cases had already passed.
Those proofs belong to API55. Its import proof covers a controlled same-cut Work
candidate; general portable import/export remains outstanding.

API50 review11 completed PASS. Across completed original selections,212 ran,
208 passed,three failed andone errored. All failed evidence remains. The same
original scheduler continues its remaining240 selections, currently exports134.
Historical API50/API55 proof does not qualify the entire API56 successor.

## Current implementation and remaining work

Inspection currently cannot discover the retained report of an incomplete-core
failure. A separate API57 successor is being prepared to associate those exact
verification bindings with the original pending claim and expose them through
authenticated operation inspection. It remains unqualified until actual checks.
It preserves pending state, null result, reconciliation and refusal to redispatch.

Finish exact successor qualification, all15 missing operations, general package
authority/carrier coverage and export privacy closure, nonempty Lesson/Context/
Ontology sources, actual Machine write authority, internal/specialized authority
resolvers, genuine R05 participant evidence and R06/R07. Complete all-member S02,
then obtain the sole actual R08 outcome before independently authorized A01-A04.

Currentness162 passed with no detected changes to linked candidate or original
preparation evidence. No complete API, genuine pilot, owner outcome, admission,
activation or completed plan is claimed. Exact report and live-job bindings are
in the paired progress index and handoff.
''')
    handoff=load(RUN/'custody-integration-handoff-0084.json')
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(currentness),
        current_status_binding=bind(status),current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[81506,55912,93518]))
    handoff['same_live_jobs']=[
        {'session_id':67314,'initial_chunk_id':'c83434','owned_driver_PID':73615,'owned_child_PID':84106,
         'state':'last-observed-running','suite':'API50 remaining240; exports134 running',
         'driver_binding':bind(RUN/'run-API50-remaining-regression-0002.py'),'whole_API_qualified':False},
        {'session_id':82302,'initial_chunk_id':'552acc','owned_driver_PID':86499,
         'state':'last-observed-running','suite':'API56 classification full16',
         'driver_binding':bind(BASE/'api56-classification-checks-v1/checks.py'),'whole_API_qualified':False}]
    handoff['terminal_bindings'].extend([proof['classification_focused_terminal_binding'],
        proof['historical_API55_affected_qualification_terminal_binding'],proof['API50_review11_terminal_binding']])
    handoff['new_scoped_evidence']['API56_classification_focused']='3 cases/4 calls PASS. Exact nine targets/four relations; unchanged failed-core and pending-retry methods pass. Full16 unfinished.'
    handoff['next_action']=proof['remaining_obligations']+['Qualify API57 pending evidence inspection without changing uncertain operation state or authorizing retries.']
    handoff_path=RUN/'custody-integration-handoff-0085.json';emit(handoff_path,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0099.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate',
        'publisher_binding':bind(Path(__file__).resolve()),'progress_binding':bind(progress),
        'currentness_binding':bind(currentness),'status_binding':bind(status),'handoff_binding':bind(handoff_path),
        'closed_tasks':36,'total_tasks':46,'authored_handlers':19,'unimplemented_operations':15,
        'classification_focused_cases_passed':3,'classification_focused_public_calls':4,
        'full_classification_qualified':False,'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),
        'handoff':bind(handoff_path),'goal_complete':False}),flush=True)

if __name__=='__main__':main()
