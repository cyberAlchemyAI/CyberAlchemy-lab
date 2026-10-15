"""Publish bounded export progress without closing the complete plan."""
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
    progress=BASE/'api-v58/receipts/R03-0101.json';proof=load(progress)
    currentness=RUN/'currentness-receipts/0164.json';current=load(currentness)
    assert current['result']=='PASS' and current['completed_tasks']==36 and current['total_tasks']==46
    assert any(r['task']=='R03' and r['receipt']==bind(progress)['path'] for r in current['active_receipt_checks'])
    assert proof['package_export_runtime_qualified'] and proof['package_export_actual_public_calls']==4
    assert proof['historical_API57_full_classification_qualified'] and not proof['package_export_full12_qualified']
    for pid in (73615,94086):assert Path('/proc',str(pid),'stat').exists()
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0101.md'
    with status.open('x') as f:f.write('''# Current Lab candidate progress

**36/46 tasks closed; R03/R06 remain in progress.** Twenty of 34 public API
handlers are authored. Fourteen operations remain. Candidate construction and
isolated verification are authorized. All-member S02 verification precedes the
sole actual R08 owner checkpoint; admission and activation remain pending.

## Implemented and verified

API58 adds authenticated `package.export`. Its independently selected host plan
binds the exact source cut, roots, original material dependency graph, privacy
review, byte budgets and owned output directory. Native candidate validation and
current signed-source basis verification precede guarded managed publication.
Exact retry reads the recorded generation without publishing again. Source proof
does not grant admission in a receiving repository.

Three selected cases/four authenticated calls passed: a native Work candidate,
a current signed-source Work with its original basis, and exact retry without
file changes. Source exit and owned fixture cleanup passed. Qualification covers
these JSON Work-root journeys. General carriers, foreign authority and non-JSON
material handling remain unfinished. The full 12-case export suite is running.

The initial focused suite failed two cases because its fixture removed required
Work membership. The failed evidence and native validation diagnostic are kept.
A separate bound fixture successor retains that membership; all twelve test
method bodies and the frozen API58 host are unchanged.

API57 separately completed all 17 classification cases/24 authenticated calls,
PASS with exit 0 and owned cleanup. That result belongs to API57. It does not
qualify inherited behavior on API58. All 293 inherited original test methods
remain unchanged.

## Remaining work

The original API50 scheduler continues its remaining selections. Its last closed
scopes retain 212 selections: 208 PASS, three FAIL and one ERROR. Original clocks
and failed evidence remain. Historical results do not qualify the current host.

Complete current export and inherited journeys; implement the remaining fourteen
operations; finish general import, carrier/reference and authority adapters,
non-JSON privacy/encoding, nonempty Lesson/Context/Ontology sources and Machine
write authority. Genuine R05 participant evidence, R06/R07 and final S02/R08
remain. A01-A04 require their separate authorization.

Currentness164 passed: 38 active receipts, 77 preserved preparation files and 887
original bound sources, with no changes detected. No complete API, genuine pilot,
owner outcome, canonical admission, activation or completed plan is claimed.
''')
    handoff=load(RUN/'custody-integration-handoff-0086.json')
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(currentness),
        current_status_binding=bind(status),current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[7381,43272,59531,62194,94484,91431,81443]))
    handoff['same_live_jobs']=[
        {'session_id':67314,'initial_chunk_id':'c83434','owned_driver_PID':73615,
         'state':'last-observed-running','suite':'API50 original remaining scheduler',
         'driver_binding':bind(RUN/'run-API50-remaining-regression-0002.py'),'whole_API_qualified':False},
        {'session_id':42741,'initial_chunk_id':'c5e851','owned_driver_PID':94086,
         'state':'last-observed-running','suite':'API58 package export full12',
         'driver_binding':bind(BASE/'api58-export-checks-v2/checks.py'),'whole_API_qualified':False}]
    handoff['terminal_bindings'].extend([proof['package_export_terminal_binding'],
        proof['historical_API57_full_classification_terminal_binding'],proof['package_export_failed_attempt_terminal_binding']])
    handoff['new_scoped_evidence']['API58_package_export']='3 cases/4 calls PASS; candidate Work, current signed-source Work and read-only exact retry. Full12 live; general carriers and sources incomplete.'
    handoff['new_scoped_evidence']['API57_full_classification']='17 cases/24 authenticated calls PASS/exit0. Exact predecessor only.'
    handoff['next_action']=proof['remaining_obligations']
    hp=RUN/'custody-integration-handoff-0087.json';emit(hp,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0101.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate',
        'publisher_binding':bind(Path(__file__).resolve()),'progress_binding':bind(progress),
        'currentness_binding':bind(currentness),'status_binding':bind(status),'handoff_binding':bind(hp),
        'closed_tasks':36,'total_tasks':46,'authored_handlers':20,'unimplemented_operations':14,
        'export_cases_passed':3,'export_public_calls':4,'current_export_full12_qualified':False,
        'historical_full_classification_cases_passed':17,'current_full_classification_qualified':False,
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(hp),'goal_complete':False}),flush=True)
if __name__=='__main__':main()
