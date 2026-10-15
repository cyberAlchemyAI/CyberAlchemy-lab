"""Publish actual bounded composition proof and the remaining original plan."""
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
    progress=API/'receipts/R03-0120.json'
    p=load(progress)
    current=sorted((RUN/'currentness-receipts').glob('*.json'))[-1]
    checked=load(current)
    assert checked['result']=='PASS' and checked['completed_tasks']==36 and checked['total_tasks']==46
    assert any(row['task']=='R03' and row['receipt']==progress.relative_to(ROOT).as_posix() for row in checked['active_receipt_checks'])
    actual=RUN/'API83-live-application-composition-0002.json'
    a=load(actual)
    assert a['result']=='PASS' and a['cases_run']==1 and len(a['phases'])==5
    jobs=[]
    for job,report,version,purpose in [
            (19391,'API80-machine-lifecycle-full-0001.json',80,'original20-case-Machine-and-termination-selection'),
            (60417,'API83-Machine-seven-read-observation-0001.json',83,'original-seven-read-method-with-parent-owned-test-observation')]:
        if not (RUN/report).exists():jobs.append({'tool_session_id':job,'API':version,'purpose':purpose})
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0120.md'
    with status.open('x') as stream:stream.write('''# Lab current Session composition result

**36/46 tasks closed. 23/34 handlers authored; 11 remain missing.**
R03 and R06 remain in progress. The complete Lab/API remain unqualified.

## Actual repaired prerequisite

API82's application policy required Session control to be absent while its
application method required that same host's actual live Session. API83 and
Lesson Application/v2 now declare a separate current participation policy with
the original source period, actual operator, source eligibility and Session
control. One pair of private future identifiers permits prospective bytes to
be prepared. Declaring identifiers creates no live resource or memory.

Actual opening through original eligibility reserves both identities outside
the pure fact scope before RAM allocation. Durable reservation and Session
history refuse reuse after disposal or uncertain opening. The original real
clock,900-second ceiling, scoped source, current permission, RAM disposal and
Machine seven-read allowlist remain. All323 inherited test method ASTs remain
unchanged. Seven structural/source checks passed.

The actual isolated composition episode passed1case with5observed phases:

1. Authenticate the new private policy and refuse malformed/extra identity
   fields and absent Session control under the original schema machinery.
2. Obtain actual same-cut Context and open a real Session with the selected
   identities, original participation eligibility and900-second ceiling.
3. Retry the exact opening through the original journal and retain the same
   actual live resource.
4. Close the actual Session and observe original RAM disposal.
5. Refuse a new-key opening that attempts to reuse the closed identity pair.

This qualifies policy/Session composition only. Positive lesson.apply and
lesson.assess require an actual controlled lesson/application/evidence episode;
the selected source has no current Lesson Application records. No tool dispatch,
interpreted outcome, causal effectiveness or canonical admission is inferred.

## Original Machine qualification

API79 completed all20original cases:19passes,1observation-helper error and
0assertion failures. The observer attempted to use the Machine service after
the call, when its pointer was unavailable; the returned transport outcome was
not retained. The underlying closure/expiry cause remains unproven.

The same API80 original20case job remains observed until its actual terminal.
The API83 original seven-read method also runs with an explicitly declared
parent-owned test observer, which survives peer disposal and records the actual
returned transport/schema outcome and elapsed time. Runtime clocks, source,
permission and lifecycle callbacks are unchanged. Neither partial output nor
the prior positive immediate Context query probe establishes full qualification.

## Admission boundary and remaining original work

Existing authorization covers candidate implementation and isolated validation.
The sole actual owner admission checkpoint remains R08 after S02 freezes the
complete exact package. No new intermediate owner decision is required for
this candidate repair. Live/existing stores, canonical admission, activation,
tool/external effects, publication and A01-A04 application retain their scopes.

Implement all11 remaining original operations: checkpoint.resolve,
admission.apply,action.evaluate,action.dispatch,action.reconcile,
workflow.transition,challenge.resolve,ontology.project,installation.execute,
capability.adoption.prepare,release.prepare. Finish real lesson/application
qualification, original R03 affected selections,R05 journeys,R06 privacy and
R07 acceptance before S02/R08. A01-A04 still remain after the owner checkpoint.
''')
    parent=RUN/'custody-integration-handoff-0101.json'
    old=load(parent)
    handoff=RUN/'custody-integration-handoff-0102.json'
    emit(handoff,{**old,'parent_handoff_binding':bind(parent),'current_progress_binding':bind(progress),
                  'currentness_binding':bind(current),'current_status_binding':bind(status),
                  'current_API_source_binding':p['source_binding'],'current_API_profile_binding':p['profile_binding'],
                  'actual_application_policy_Session_composition_binding':bind(actual),
                  'same_live_jobs':jobs,'closed_jobs_do_not_repoll':sorted(set(old['closed_jobs_do_not_repoll']+[51955,26953,28936])),
                  'next_action':p['remaining_obligations'],'current_Machine_qualified':False,
                  'whole_API_qualified':False,'goal_complete':False})
    index=RUN/'R03-CURRENT-PROGRESS-0120.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate',
                'publisher_binding':bind(Path(__file__).resolve()),'progress_binding':bind(progress),
                'currentness_binding':bind(current),'status_binding':bind(status),'handoff_binding':bind(handoff),
                'closed_tasks':36,'total_tasks':46,'authored_handlers':23,'unimplemented_operations':11,
                'actual_application_policy_Session_composition_binding':bind(actual),
                'actual_application_composition_cases':1,'actual_application_composition_phases':5,
                'same_live_jobs':[row['tool_session_id'] for row in jobs],'current_Machine_qualified':False,
                'whole_API_qualified':False,'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),
                      'handoff':bind(handoff),'live_jobs':jobs}),flush=True)


if __name__=='__main__':main()
