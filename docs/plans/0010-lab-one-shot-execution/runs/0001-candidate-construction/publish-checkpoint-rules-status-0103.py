"""Publish completed selected proofs without upgrading their authority."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
def load(p): return json.loads(p.read_bytes())
def bind(p): return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as f: json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    progress=BASE/'api-v59/receipts/R03-0103.json'
    proof=load(progress)
    currentness=RUN/'currentness-receipts/0166.json'
    current=load(currentness)
    assert current['result']=='PASS' and current['completed_tasks']==36 and current['total_tasks']==46
    assert any(r['task']=='R03' and r['receipt']==bind(progress)['path'] for r in current['active_receipt_checks'])
    assert proof['package_export_full14_qualified'] and proof['checkpoint_resolution_rule_cases']==47
    assert not proof['checkpoint_resolution_public_handler_qualified']
    for pid in (73615,98143): assert Path('/proc',str(pid),'stat').exists()
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0103.md'
    with status.open('x') as f: f.write('''# Current Lab candidate progress

**36/46 tasks closed. R03/R06 remain in progress.** API59 has twenty authored
handlers and fourteen missing public operations. Candidate construction and
isolated verification remain authorized. All-member S02 precedes the sole actual
R08 owner checkpoint. Admission and activation remain pending.

## Completed verification

API59's full selected export suite passed fourteen cases and eighteen actual
authenticated public calls, with source exit checks and owned fixture cleanup.
This covers JSON Work-root candidate/current-source exports, permission, privacy,
dependency closure, read-only retries and lock/generation recovery. The two API58
failures are preserved. API59's repair prevents lookup from creating a lock file
and refuses a durable journal whose lock is missing without recreating it.

The pure checkpoint resolution kernel passed forty-seven synthetic cases. It
checks exact original package, target, core and owner-voice coupling, selected-key
Ed25519 signatures, time windows, revocation, channel shape and ordered outcomes.
Reject and defer remain explicit. It retains the package's semantic and operational
gaps. It makes no owner recognition, admission or live authority claim.

The first kernel run stopped forty-four fixtures on duplicate schema identity.
Its failed evidence is preserved. Version 2 accepts duplicate identities only
for byte-identical originals; all forty-five original test bodies remain unchanged
and two added cases check identical copies and conflicting bytes.

`checkpoint.resolve` still needs authenticated owner/channel and live Role/Scope
adapters, durable recording, exact retries/recovery and Validation Reports.
The pure kernel is not a public API handler or an actual R08 owner outcome.

Historical API50 metadata86 passed. Its closed selected scopes now total 432
selections: 428 PASS, three FAIL and one ERROR. These selections overlap and are
not unique tests. The same original scheduler continues Machine14 then termination6;
twenty selections remain. Original clocks and failed evidence are retained.

## Remaining work and decision boundary

Complete all fourteen missing public operations and inherited current API journeys;
general carrier/reference/foreign-authority import and export; non-JSON privacy and
encoding; nonempty Lesson/Context/Ontology sources; actual Machine write authority;
genuine R05 participant evidence; R06/R07; and all-member S02 verification.
The final R08 response must bind the exact completed package and evidence.
A01-A04 retain separate authorization requirements.

Currentness166 passed: 38 active receipts, 77 original preparation files and 887
original bound sources, with no mismatches. No complete API, genuine pilot, actual
owner outcome, canonical admission, activation or completed plan is claimed.
''')
    handoff=load(RUN/'custody-integration-handoff-0088.json')
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(currentness),
        current_status_binding=bind(status),current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[23170,28856,93460,31630]))
    handoff['same_live_jobs']=[{'session_id':67314,'initial_chunk_id':'c83434','owned_driver_PID':73615,
        'owned_child_PID':98143,'state':'last-observed-running','suite':'API50 Machine14 then termination6',
        'driver_binding':bind(RUN/'run-API50-remaining-regression-0002.py'),'whole_API_qualified':False}]
    for key in ('package_export_full14_terminal_binding','checkpoint_resolution_rule_terminal_binding',
                'checkpoint_resolution_rule_failed_terminal_binding','historical_API50_metadata86_terminal_binding'):
        handoff['terminal_bindings'].append(proof[key])
    handoff['new_scoped_evidence']['API59_full14']='14 cases/18 actual calls PASS; selected Work-root JSON export only.'
    handoff['new_scoped_evidence']['checkpoint_pure47']='47 synthetic cases PASS; no public checkpoint handler or actual owner recognition.'
    handoff['new_scoped_evidence']['API50_metadata86']='86 cases PASS on exact historical source; 20 selected cases remain live.'
    handoff['next_action']=proof['remaining_obligations']
    hp=RUN/'custody-integration-handoff-0089.json';emit(hp,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0103.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate','publisher_binding':bind(Path(__file__).resolve()),
        'progress_binding':bind(progress),'currentness_binding':bind(currentness),'status_binding':bind(status),
        'handoff_binding':bind(hp),'closed_tasks':36,'total_tasks':46,'authored_handlers':20,
        'unimplemented_operations':14,'current_export_full14_qualified':True,'export_actual_public_calls':18,
        'checkpoint_pure_cases_passed':47,'checkpoint_public_handler_qualified':False,
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(hp)}),flush=True)
if __name__=='__main__': main()
