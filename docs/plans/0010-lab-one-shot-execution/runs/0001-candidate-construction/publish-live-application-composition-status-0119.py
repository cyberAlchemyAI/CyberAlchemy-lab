"""Publish exact scoped implementation, original terminal and pending jobs."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v83'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def main():
    progress=API/'receipts/R03-0119.json'
    p=load(progress)
    current=sorted((RUN/'currentness-receipts').glob('*.json'))[-1]
    checked=load(current)
    assert checked['result']=='PASS' and checked['completed_tasks']==36 and checked['total_tasks']==46
    assert any(row['task']=='R03' and row['receipt']==progress.relative_to(ROOT).as_posix() for row in checked['active_receipt_checks'])
    terminal79=RUN/'API79-machine-lifecycle-full-terminal-0001.json'
    report79=RUN/'API79-machine-lifecycle-full-0001.json'
    actual79=load(report79)
    assert load(terminal79)['actual_exit_code']==1 and actual79['actual_cases']==20
    assert actual79['errors']==1 and actual79['failures']==0
    jobs=[]
    terminal80=RUN/'API80-machine-lifecycle-full-terminal-0001.json'
    if not terminal80.exists():jobs.append({'tool_session_id':19391,'API':80,'selected_cases':20,'selection_binding':bind(RUN/'API80-independent-selection-0001.json')})
    composition=RUN/'API83-live-application-composition-0002.json'
    if not composition.exists():jobs.append({'tool_session_id':51955,'API':83,'selected_cases':1,'purpose':'actual-policy-and-Session-composition-only','driver_binding':bind(RUN/'qualify-API83-live-application-composition-0002.py')})
    composition_posture=load(composition)['result'] if composition.exists() else 'running'
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0119.md'
    text='''# Lab application and current Session composition

**36/46 tasks closed. 23/34 handlers authored; 11 remain missing.**
R03 and R06 remain in progress. The complete Lab/API remain unqualified.

## Repaired prerequisite

API82's application authentication required Session control to be absent, while
the application method required the same host's actual live Session. API83
adds a separate current-participation/application policy that requires Session
control and preserves the original source period and actual operator guards.

The private policy binds one future Session/Agent identity pair so prospective
application bytes can be prepared before opening. Declaring identifiers creates
no resource. Original participation eligibility and exact delivered Context
precede opening. Both identifiers are durably reserved outside the pure fact
scope before RAM allocation. Reuse after disposal or uncertain opening is
refused. Original real clocks, 900-second ceiling, RAM disposal and the Machine
peer's seven-operation read allowlist remain.

Seven source/structural checks passed. All323 inherited test ASTs, original
permission/opening eligibility/disposal/history methods and guarded readers
remain unchanged. This is an implementation repair, not a new public handler.
The actual scoped opening/closing diagnostic posture is: '''+composition_posture+'''.
Its first attempt preserved a0case framework error for missing exact test
profile configuration; successor0002 supplies the selected original profile.
Neither example establishes positive Lesson Application or interpreted outcome.

## Original suite observation

API79 completed all20 original Machine/termination cases with actual exit1:
19passed,0assertion failures,1error. The seven-read case errored in the test
observation helper while trying to access the Machine service's Vault after the
call. Only3 Machine public replies were retained. The returned transport result
was not recorded; the exact underlying closure/expiry cause is not yet proven.
Preserve this failure, repair observation custody in a successor, and rerun the
original affected case. Current Machine qualification remains open.

API80's same original20case job is observed separately. Its partial successful
query/inspect replies do not qualify the whole selection. The API80 immediate
Machine Context query construction diagnostic passed1 actual case previously.

## Governance and remaining work

Candidate construction and isolated validation remain authorized. S02 must
freeze the complete reviewed package before the sole actual R08 owner response.
Canonical admission, existing/live stores, service activation, tool/external
effects and publication remain outside this construction authorization. A01-A04
retain their separately scoped application and acceptance effects.

The current signed source has no Lesson Application records. Create a real
controlled lesson/application/evidence episode, qualify lesson.apply/assess and
refusals, implement all11 missing operations, then finish original R05 journeys,
R06 privacy and R07 acceptance. No task closure or whole Lab realization is
inferred from this prerequisite repair.
'''
    with status.open('x') as stream:stream.write(text)
    parent=RUN/'custody-integration-handoff-0100.json'
    old=load(parent)
    handoff=RUN/'custody-integration-handoff-0101.json'
    emit(handoff,{**old,'parent_handoff_binding':bind(parent),'current_progress_binding':bind(progress),
                  'currentness_binding':bind(current),'current_status_binding':bind(status),
                  'current_API_source_binding':p['source_binding'],'current_API_profile_binding':p['profile_binding'],
                  'API79_original_terminal_binding':bind(terminal79),'API79_original_report_binding':bind(report79),
                  'same_live_jobs':jobs,'closed_jobs_do_not_repoll':sorted(set(old['closed_jobs_do_not_repoll']+[35646,65290,49470,99164,17026,24963,13715])),
                  'next_action':[
                      'Observe API83 composition job51955 and bind its exact actual result; no positive application qualification inferred.',
                      'Observe API80 same original20case job19391. API79 has completed19passes1observation-helper error; preserve failure and repair exact observer custody in a successor before affected original-case qualification.',
                      *p['remaining_obligations'][2:]],
                  'current_Machine_qualified':False,'whole_API_qualified':False,'goal_complete':False})
    index=RUN/'R03-CURRENT-PROGRESS-0119.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate',
                'publisher_binding':bind(Path(__file__).resolve()),'progress_binding':bind(progress),
                'currentness_binding':bind(current),'status_binding':bind(status),'handoff_binding':bind(handoff),
                'closed_tasks':36,'total_tasks':46,'authored_handlers':23,'unimplemented_operations':11,
                'API79_original_terminal_binding':bind(terminal79),'API79_actual_cases':20,'API79_actual_errors':1,
                'same_live_jobs':[row['tool_session_id'] for row in jobs],
                'actual_application_composition_posture':composition_posture,'current_Machine_qualified':False,
                'whole_API_qualified':False,'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(handoff),'live_jobs':jobs}),flush=True)


if __name__=='__main__':main()
