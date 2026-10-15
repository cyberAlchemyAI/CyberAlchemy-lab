"""Publish exact current scope repair, learning candidates and full remaining scope."""
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
    progress=API/'receipts/R03-0124.json';p=load(progress)
    current=sorted((RUN/'currentness-receipts').glob('*.json'))[-1];c=load(current)
    assert c['result']=='PASS' and c['completed_tasks']==36 and c['total_tasks']==46
    assert any(row['task']=='R03' and row['receipt']==progress.relative_to(ROOT).as_posix() for row in c['active_receipt_checks'])
    learning=RUN/'Machine-policy-custody-lesson-0001/index.json'
    diagnosis=RUN/'API83-original-Machine-generation-diagnosis-0001.json'
    actual=RUN/'API85-Machine-seven-read-observation-0001.json'
    posture=load(actual)['result'] if actual.exists() else 'running'
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0124.md'
    with status.open('x') as stream:stream.write('''# Lab Machine policy custody and real learning candidate

**36/46 tasks closed. 23/34 public handlers authored; 11 remain missing.**
R03 and R06 remain in progress; full Lab/API qualification remains open.

## Confirmed current failure

The actual original Machine generator refuses its parent policy channel because
the original fact-copy scope registers the Machine as its sole policy host.
The known refusal is `fact scope selects another host channel`. The diagnostic
confirmed peer disposal while the parent Session stayed live and unexpired.
This is a current controlled diagnosis; it does not establish every historical
failure cause or excuse the preserved original API79/API80 suite failures.

## Candidate repair and qualification

API84 explicitly composes the actual peer's parent ReaderChannel as the policy
custodian, while the original generator still uses the actual Machine Actor and
permission bridge. The original sealed-copy class, source callbacks, real
clock, expiry limits, transport/auth/vault/protocol bytes and all323 inherited
test methods remain. API85 changes one exact fixture connection reference;
322ASTs remain unchanged and all original assertions remain. No role, operation,
grant or lifetime is added. Seven exact
structural/source checks passed.

API84 actual Machine context.get returned a domain result with the peer and
Session live. Its next session.inspect call correctly rejected the fixture
parent opaque context reference. API85 supplies that exact Machine context
reference in one fixture line; original production auth/clock/permission/
dispatch bytes remain identical to84.

The corrected actual API85 seven-read case posture is: '''+posture+'''. Its selection
asserts the exact API84 path/source/profile hashes. Initial API84-labeled0001
actually selectedAPI83 through a copied lowercase path; that failure is
preserved as predecessor evidence and supplies no API84 qualification.
After the repaired case passes, run all original14Machine and6termination
cases, then qualify wrong-parent/source/resource and private scope refusals.

## Materialized learning records

Machine-policy-custody-lesson-0001 contains four schema-valid candidate bodies:
an Agent Action, Operational Observation, Agent Reflection and Operational
Lesson. Three explicit Typed Relations connect action-to-observation,
reflection-to-observation and lesson-to-reflection under current admitted
endpoint signatures and qualifier contracts. Actual actor/Session audit
identifiers and accountability come from the controlled opening metadata;
no Session RAM, notes or private keys were copied.

The lesson states a scoped falsifiable prediction: this exact private custody
repair should allow the original seven-read Machine case to return all seven
domain results without losing a live unexpired peer at this mismatch. It has
explicit exclusions, retention and expiry. The operator Context success is
retained as counterevidence against broader failure/causal claims.

These records are unadmitted and not in the current signed source. They are not
an actual selected/applied lesson or assessed outcome. Import exact candidates
with explicit applicability and mapped relation closure into a new owned signed
source; original Context9 intentionally refuses current lessons without that
closure. A fresh Agent must consume that Project State before the later
controlled application/outcome can be qualified. Prior code repair remains
independent counterevidence and must not be counted as lesson application.

## Remaining full plan and checkpoint

Implement all11 missing original operations: checkpoint.resolve,admission.apply,
action.evaluate,action.dispatch,action.reconcile,workflow.transition,
challenge.resolve,ontology.project,installation.execute,
capability.adoption.prepare,release.prepare. Complete original R03 affected
selections,R05 journeys,R06 privacy,R07 acceptance and S02 full exact package
before the sole actual R08 owner response. Preserve separately scoped A01-A04.

Existing authorization covers candidate construction and isolated checks;
canonical admission, existing/live stores, activation, external/tool effects
and publication remain outside it. No new intermediate owner decision is
introduced by this repair or unadmitted learning materialization.
''')
    parent=RUN/'custody-integration-handoff-0104.json';old=load(parent)
    jobs=[] if actual.exists() else [{'tool_session_id':78380,'API':85,'purpose':'original-seven-read-method-exact-API84-selection'}]
    handoff=RUN/'custody-integration-handoff-0105.json'
    emit(handoff,{**old,'parent_handoff_binding':bind(parent),'current_progress_binding':bind(progress),
                  'current_status_binding':bind(status),'currentness_binding':bind(current),
                  'current_API_source_binding':p['source_binding'],'current_API_profile_binding':p['profile_binding'],
                  'current_original_Machine_failure_diagnosis_binding':bind(diagnosis),
                  'actual_failure_learning_candidate_binding':bind(learning),
                  'same_live_jobs':jobs,'closed_jobs_do_not_repoll':sorted(set(old['closed_jobs_do_not_repoll']+[60417,3462,17289,54097,77677,6773,92280,65228,52098,5302])),
                  'next_action':p['remaining_obligations'],'current_Machine_qualified':False,
                  'whole_API_qualified':False,'goal_complete':False})
    index=RUN/'R03-CURRENT-PROGRESS-0124.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate','publisher_binding':bind(Path(__file__).resolve()),
                'progress_binding':bind(progress),'currentness_binding':bind(current),'status_binding':bind(status),
                'handoff_binding':bind(handoff),'closed_tasks':36,'total_tasks':46,'authored_handlers':23,
                'unimplemented_operations':11,'actual_failure_learning_candidate_binding':bind(learning),
                'actual_learning_candidate_bodies':4,'actual_learning_candidate_relations':3,
                'actual_Machine_repair_case_posture':posture,'same_live_jobs':[row['tool_session_id'] for row in jobs],
                'current_Machine_qualified':False,'whole_API_qualified':False,'authority_effect':'none',
                'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),
                      'handoff':bind(handoff),'live_jobs':jobs}),flush=True)


if __name__=='__main__':main()
