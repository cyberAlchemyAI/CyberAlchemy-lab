"""Publish bounded challenge progress and the actual stopped scheduler."""
import hashlib
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v68'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as stream:json.dump(v,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    progress=API/'receipts/R03-0106.json';proof=load(progress)
    currentness=sorted((RUN/'currentness-receipts').glob('*.json'))[-1];current=load(currentness)
    assert current['result']=='PASS' and current['completed_tasks']==36 and current['total_tasks']==46
    assert any(r['task']=='R03' and r['receipt']==bind(progress)['path'] for r in current['active_receipt_checks'])
    focused=load(API/'receipts/challenge-focused-checks-0001.json')
    assert focused['result']=='PASS' and focused['actual_cases']==1 and focused['actual_public_calls']==2
    full=next((o for o in proof['challenge_actual_outcomes'] if o['version']==68 and o['scope']=='full'),None)
    if full is None:verdict='The complete seven-case challenge suite is still running; no full verdict is claimed.'
    else:verdict=f"The complete seven-case challenge suite returned {full['result']}: {full['actual_cases']} cases, {full['actual_public_calls']} public calls, {full['failures']} failures and {full['errors']} errors."
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0106.md'
    text=f'''# Lab candidate progress and final review boundary

**36 of 46 tasks closed; R03 and R06 remain in progress.** The frozen API68
candidate has 21 authored handlers and 13 missing operations from the original
34-operation contract. Authorship does not qualify the complete API.

## Challenge submission

The original `challenge.submit` contract now constructs a closed candidate
proposal containing an Evidence Set, an open Challenge Event and two explicit
Typed Relations: Evidence Set `member-of` its selected Project, and Challenge
Event `challenges` the exact selected Work revision. Existing axes, signatures,
endpoint pairs and qualifiers govern both connections.

The handler checks the authenticated Principal, independently selected finite
routing, exact source cut and revision, current Challenge Contract, declared
ground, all required evidence kinds and independently computed eligibility.
The original challenged subject and history remain intact. Historical document
evidence is validated against one captured exact discriminator/schema; it does
not become current membership, authority or a new owner resolution.

The focused actual check passed: one case and two public calls, including stored
original bytes, both typed connections, unchanged source projection and operation
lookup. Original source exit checks and owned fixture cleanup completed.

{verdict}

Earlier failures remain preserved. They exposed an absent admitted Evidence Set,
required nonempty relation references, Project endpoint mapping, a historical
Decision carrier, the Typed Relation-only correction boundary, a Decision v2/v1
discriminator mismatch and use of the input accessor for generated output objects.
API67 returned a real four-target/two-connection result before its output-reading
test errored. API68 uses the actual output custody accessor and retains all checks.

## Remaining integration and validation

Generated proposals still need an independently selected bridge into generic
candidate validation/review. A returned proposal shape and local native core
preparation do not qualify that complete workflow. Machine challenger authority,
historical endpoint cases and actual owner resolution remain unqualified.

The original API50 Machine suite closed with 13 PASS and one ERROR. Captured
frames identify a TypeError in the public read/error path ending at Service.reply;
no temporal cause is asserted. Its scheduler stopped before six termination
cases. Closed overlapping selections total 446: 441 PASS, three failed assertions
and two errors. Historical evidence does not qualify the current complete API.

The 13 missing operations, general carrier/foreign-source/authority adapters,
non-JSON privacy/encoding, nonempty Context/Lesson/Ontology sources, genuine pilot
participants and R06/R07 remain required. The existing 49 owner-join checks and
47 pure checkpoint-rule checks retain their original scope, with live authority
and a successful native owner journey still unqualified.

## Governance boundary

Existing candidate construction authorization covers this work and isolated
validation. No new intermediate semantic approval is required. Complete all
members and S02 before presenting the sole final R08 owner checkpoint.

R08 must bind the exact completed package and evidence. A01 repository admission
and A02 operational effects retain their applicable exact authorization gates.
No canonical admission, activation, external effect or completed plan is claimed.

Progress receipt: `product/lab/release-candidates/v1/interface/api-v68/receipts/R03-0106.json`.
Currentness receipt: `{currentness.name}`.
'''
    with status.open('x') as stream:stream.write(text)
    handoff=load(RUN/'custody-integration-handoff-0090.json')
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(currentness),
        current_status_binding=bind(status),current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'],next_action=proof['remaining_obligations'])
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[69053,71690,87684,44810,92742,95585,70667,67314,75833,85665,45832]))
    handoff['historical_live_job_observations']=handoff.get('same_live_jobs',[])
    handoff['same_live_jobs']=[]
    handoff['new_scoped_evidence']['challenge_API68_focused']='PASS: one actual case, two public calls; exact original artifact output bytes, two typed connections, preserved source history and durable lookup. Full seven-case result has its separate recorded scope.'
    handoff['new_scoped_evidence']['API50_machine14_and_stopped_driver']='Machine14:13 PASS/1 ERROR. Original driver67314 ended1 and stopped before termination6. Captured TypeError at Service.reply; no temporal cause established. 446 overlapping selections closed:441PASS/3FAIL/2ERROR.'
    handoff['challenge_current_active_job_observation']=proof['challenge_current_active_job_observation']
    handoff['challenge_actual_outcomes']=proof['challenge_actual_outcomes']
    handoff['API50_original_driver_terminal_binding']=bind(RUN/'API50-remaining-driver-failed-terminal-0002.json')
    hp=RUN/'custody-integration-handoff-0091.json';emit(hp,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0106.json'
    emit(index,{'schema_version':'lab-current-progress-index/v1-candidate','publisher_binding':bind(Path(__file__).resolve()),
        'progress_binding':bind(progress),'currentness_binding':bind(currentness),'status_binding':bind(status),'handoff_binding':bind(hp),
        'closed_tasks':36,'total_tasks':46,'authored_handlers':21,'unimplemented_operations':13,
        'challenge_focused_cases_passed':1,'challenge_focused_actual_public_calls':2,
        'challenge_selected_full7_runtime_qualified':proof['challenge_operator_selected_full7_runtime_qualified'],
        'generic_challenge_review_workflow_qualified':False,'Machine_challenge_authority_qualified':False,
        'checkpoint_public_handler_qualified':False,'live_authority_verified':False,'whole_API_qualified':False,
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(hp)}),flush=True)
if __name__=='__main__':main()
