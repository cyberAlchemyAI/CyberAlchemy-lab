"""Publish actual affected-path success without closing full lifecycle scope."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v85'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def main():
    progress=API/'receipts/R03-0125.json';p=load(progress)
    current=sorted((RUN/'currentness-receipts').glob('*.json'))[-1];c=load(current)
    assert c['result']=='PASS' and c['completed_tasks']==36 and c['total_tasks']==46
    assert any(row['task']=='R03' and row['receipt']==progress.relative_to(ROOT).as_posix() for row in c['active_receipt_checks'])
    actual=RUN/'API85-Machine-seven-read-observation-0001.json';a=load(actual)
    assert a['result']=='PASS' and len(a['actual_calls'])==7
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0125.md'
    with status.open('x') as stream:stream.write('''# Lab current Machine read-path result

**36/46 tasks closed. 23/34 public handlers authored;11remain missing.**
R03 and R06 stay in progress; the complete Lab/API remain unqualified.

## Actual current seven-read path

API85 passed the corrected original seven-read method with seven domain
results:lab.status,catalog.get,artifact.query,artifact.inspect,context.get,
session.inspect andoperation.inspect. Every observed peer/Session stayed live
and unexpired. Original runtime source, Actor, permission and real-clock
callbacks remain. One fixture connection reference was explicitly corrected;
all323 methods and original assertions remain,322testASTs unchanged.

The actual original14Machine+6termination fullselection is running as job21646,
bound to exact API85 source/profile and its independent selection. Retain that
same process through the real expiry case and actual terminal. The focused
path pass does not qualify the complete Machine lifecycle or wholeAPI.

## Actual failure and learning candidates

The original current generator refused its parent policy channel while its
fact scope registered the Machine as sole policy host. Direct safe-chain
diagnosis confirmed this before actual Session expiry. The private candidate
composition binds exactly the actual parent policy custodian while preserving
the Machine Actor, original generator and fact-copy implementation. No roles,
operations or lifetime are added. The subsequent stale-parent opaque context
reference was a fixture error, correctly rejected by unchanged authentication.

Four candidate learning bodies and three declared relations record the real
diagnostic: Agent Action, Operational Observation, Agent Reflection and scoped
Operational Lesson. Schemas, exact endpoint pairs and qualifiers passed. They
remain unadmitted,unapplied and outside current signed source. Prior code repair
is independent counterevidence and must not be counted as lesson application.

## Remaining original scope

Qualify full lifecycle and private scope refusals. Import exact learning records
with applicability/mapping closure into a freshly owned signed source, consume
through a new actual Agent Context, then perform/record the controlled later
application and outcome. Context9 deliberately refuses current lessons without
this closure. Positive lesson.apply andlesson.assess remain unqualified.

Implement all11original missing operations:checkpoint.resolve,admission.apply,
action.evaluate,action.dispatch,action.reconcile,workflow.transition,
challenge.resolve,ontology.project,installation.execute,
capability.adoption.prepare,release.prepare. Complete original R03 affected
selections,R05 journeys,R06 privacy,R07 acceptance and S02 exact whole package
before the sole actual R08 owner response. Preserve separately scoped A01-A04.

Existing candidate construction/isolated validation authorization remains.
Canonical admission, existing/live stores, activation, external/tool effects
and publication are outside it; no new intermediate owner decision is added.
''')
    parent=RUN/'custody-integration-handoff-0105.json';old=load(parent)
    selection=RUN/'API85-independent-selection-0001.json'
    handoff=RUN/'custody-integration-handoff-0106.json'
    emit(handoff,{**old,'parent_handoff_binding':bind(parent),'current_progress_binding':bind(progress),
                  'current_status_binding':bind(status),'currentness_binding':bind(current),
                  'current_API_source_binding':p['source_binding'],'current_API_profile_binding':p['profile_binding'],
                  'actual_current_Machine_seven_read_case_binding':bind(actual),
                  'same_live_jobs':[{'tool_session_id':21646,'API':85,'purpose':'original14Machine+6termination','selection_binding':bind(selection)}],
                  'closed_jobs_do_not_repoll':sorted(set(old['closed_jobs_do_not_repoll']+[78380,69435,82656])),
                  'next_action':p['remaining_obligations'],'current_Machine_qualified':False,'whole_API_qualified':False,'goal_complete':False})
    index=RUN/'R03-CURRENT-PROGRESS-0125.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate','publisher_binding':bind(Path(__file__).resolve()),
                'progress_binding':bind(progress),'currentness_binding':bind(current),'status_binding':bind(status),'handoff_binding':bind(handoff),
                'closed_tasks':36,'total_tasks':46,'authored_handlers':23,'unimplemented_operations':11,
                'actual_current_Machine_seven_read_case_binding':bind(actual),'actual_Machine_read_operations_passed':7,
                'same_live_jobs':[21646],'current_Machine_qualified':False,'whole_API_qualified':False,
                'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),
                      'handoff':bind(handoff),'live_job':21646}),flush=True)


if __name__=='__main__':main()
