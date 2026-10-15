"""Publish exact owner adapter progress without closing the full API or plan."""
import hashlib
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as stream:json.dump(v,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    progress=BASE/'api-v59/receipts/R03-0104.json';proof=load(progress)
    currentness=RUN/'currentness-receipts/0167.json';current=load(currentness)
    assert current['result']=='PASS' and current['completed_tasks']==36 and current['total_tasks']==46
    assert any(r['task']=='R03' and r['receipt']==bind(progress)['path'] for r in current['active_receipt_checks'])
    assert proof['checkpoint_owner_join_cases_passed']==49 and not proof['checkpoint_owner_live_authority_qualified']
    for pid in (73615,98143):assert Path('/proc',str(pid),'stat').exists()
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0104.md'
    with status.open('x') as stream:stream.write('''# Current Lab candidate progress

**36/46 tasks closed; R03/R06 remain in progress.** API59 still has twenty
authored handlers and fourteen missing public operations. Candidate construction
and isolated verification are authorized. All-member S02 precedes the sole
actual R08 owner checkpoint. Admission and activation remain pending.

## Completed evidence

API59's selected JSON Work-root export suite passed fourteen cases and eighteen
authenticated calls, with original source exit checks and owned fixture cleanup.
The pure checkpoint rule kernel passed forty-seven synthetic cases. Its exact
package/core/target/ordered-voice and signature checks remain separate from
actual owner recognition and live authority.

The new owner adapter has independent private-file owner/key selection, a source
resolver requiring the actual frozen API59 Service/ReaderChannel/Vault, and
original-schema joins of Principal, Role Assignment, Authority Claim, Authority
Boundary and Decision Scope. It rechecks source bytes, signed cut, authenticated
operator, scope, exact current artifact headers, original bodies and real clocks.
Selections are read through no-follow directory descriptors with private modes,
owner, link count and file/directory identity checks. Caller key claims fail.

The current version separates the storage scope in an artifact header from its
body's semantic domain. Each independent owner selection names the storage scope
and the assignment's domain. A Role Assignment cannot cover another target domain
merely because both artifacts share the same store.

Forty-nine synthetic original-schema join and actual private-file custody cases
passed. All forty-three prior test bodies remain unchanged in the final version;
six domain checks were added. Initial v1 evidence remains: 38 cases, five errors,
no failed assertions. The corrected v2 passed 43 after preserving mandatory
limitations/exclusions and resolving Source Cut through its original storage
schema. Negative cases check that they reach the intended semantic refusal.

The join retains limitations, assignment basis and claim basis references.
It explicitly returns authority_basis_verified=false and live_authority_verified=false.
Those original Decisions and limitations require independent provenance and
semantic resolution. No successful native owner-source journey, actual human
identity, public checkpoint handler or actual R08 response is qualified.

## Remaining work and decision boundary

Compose owner selection with the complete checkpoint kernel; resolve original
basis Decisions and limitations; complete actual owner/channel provenance,
public host policy integration, durable recording, exact retry/recovery and
Validation Reports. Then verify actual authenticated checkpoint journeys.
Conversation and existing-authority channels require their own provenance adapters.

The original API50 scheduler is still running Machine14 then termination6.
Its closed selections total 432: 428 PASS, 3 FAIL, 1 ERROR; twenty selections remain
without a terminal verdict. The live Machine log has an additional error in its
second case; its cause and full result remain unestablished. Original clocks and
failure evidence are preserved. No historical proof qualifies all current API59.

All fourteen missing operations, general carrier/reference/foreign-authority
adapters, non-JSON privacy/encoding, nonempty Lesson/Context/Ontology sources,
actual Machine write authority, genuine R05 participants, R06/R07 and all-member
S02 remain required. The final R08 response must bind the exact completed package
and evidence. A01-A04 retain separate authorization requirements.

Currentness167 passed with 38 active receipts, 77 preserved preparation files
and 887 original bound sources; no mismatches. No complete API, genuine pilot,
live authority, canonical admission, activation or completed plan is claimed.
''')
    handoff=load(RUN/'custody-integration-handoff-0089.json')
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(currentness),
        current_status_binding=bind(status),current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'],next_action=proof['remaining_obligations'])
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[59455,41499,5887]))
    handoff['terminal_bindings'].extend(proof['checkpoint_owner_join_terminal_bindings'])
    handoff['new_scoped_evidence']['checkpoint_owner_adapter49']='49 selected synthetic original-schema join/private-file cases PASS. Storage and assignment domains separate. Basis/limitations unresolved; no live authority, native positive journey or public handler qualified.'
    handoff['new_scoped_evidence']['API50_live_machine_error']='Second Machine case has ERROR in live log; no terminal cause/verdict yet. Preserve same original job67314/driver73615/child98143.'
    hp=RUN/'custody-integration-handoff-0090.json';emit(hp,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0104.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate','publisher_binding':bind(Path(__file__).resolve()),
        'progress_binding':bind(progress),'currentness_binding':bind(currentness),'status_binding':bind(status),
        'handoff_binding':bind(hp),'closed_tasks':36,'total_tasks':46,'authored_handlers':20,'unimplemented_operations':14,
        'owner_join_selected_cases_passed':49,'owner_native_positive_journey_qualified':False,
        'checkpoint_public_handler_qualified':False,'live_authority_verified':False,
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(hp)}),flush=True)
if __name__=='__main__':main()
