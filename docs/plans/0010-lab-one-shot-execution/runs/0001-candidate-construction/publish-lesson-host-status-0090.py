"""Publish exact candidate source, scoped evidence and verified live handles."""
import hashlib
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'


def load(p):return json.loads(p.read_bytes())


def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}


def put(p,v):
    with p.open('x') as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')


def main():
    progress=BASE/'api-v51/receipts/R03-0090.json';proof=load(progress)
    current=RUN/'currentness-receipts/0154.json';checked=load(current)
    assert checked['result']=='PASS' and checked['completed_tasks']==36 and checked['total_tasks']==46
    assert any(row['task']=='R03' and row['receipt']==progress.relative_to(ROOT).as_posix() for row in checked['active_receipt_checks'])
    assert load(RUN/'R03-0090-currentness-terminal-0001.json')['actual_exit_code']==0
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0090.md'
    with status.open('x') as f:f.write('''# Lab operational foundation: current candidate progress

The full plan remains active. Candidate construction and verification are already
authorized. One final R08 owner admission remains after complete S02.

## Current state

| Item | State |
| --- | --- |
| Plan | 36/46 tasks closed; R03/R06 in progress |
| Current candidate | API51 frozen;34 original contracts;18 authored handlers;16 missing |
| Original compatibility | All293 inherited test methods retained; every old policy variant preserved |
| Lesson rules | Successor61 complete synthetic cases PASS; all53 original W06 tests PASS |
| API51 lesson transport | Three real signed-source/live-Session cases running under18103/PID35000 |
| API51 qualification | Pending; no earlier source qualification transferred to this version |
| API50 regression | Same28245/PID21680; typed10/failure18/controls11 PASS39; full146 running |
| API50 remaining selection | 413 cases; runner overlap declared; whole API unqualified |
| Currentness154 | PASS;38 active receipts;77 preparation files;887 baseline sources unchanged |
| Admission | Sole R08 pending full S02; no owner outcome exists |

## Implemented lesson host

The new closed policy variant independently selects a host plan. Every old
policy variant and operation set remains. The legacy Machine read subset keeps
its seven operations; only the explicit new lesson policy delegates an eighth
read. Its Machine action budget remains zero.

The handler requires the actual API51 Service, authenticated MachinePeer, selected
parent host and its real live Session resource. It checks accountable Principal,
Agent identity, Assignment, current source cut, Work, Coordination Context and the
original participation eligibility. A copied Actor or reconstructed Session
cannot replace those objects. Routing joins actual source facts with independently
selected instruction, review, applicability, retention and exclusion witnesses.

The complete current Lesson inventory is calculated from declared carrier
semantics and projected kinds. Unknown current Lessons block closure. Routing
must cover the complete ordered inventory; no zero-only fallback or truncation
is implemented. Explicit query exclusions are applied before conflict pairs.
Original source/evidence/counterevidence bytes and current review state remain
bound. The public result uses the original Lesson Selection schema.

Calculation borrows only sealed source facts and keeps original callbacks and
real permission clocks. Full exit guards precede bounded derived evidence writes
to the owned Vault. No domain admission, operation claim or Application occurs.
Transient routing maps are cleared after the call. The actual Session owns RAM
and peer disposal; durable continuity remains Project State through Context and
Ontology Views.

## Verification boundaries and remaining work

The actual three-case transport runner is confirmed live; no full result or
terminal outcome is inferred. The current signed branch contains no Lessons.
Its original Context/Ontology delivery explicitly refuses nonempty Lesson
catalogs. Full qualification therefore requires a governed source/context/ontology
successor and actual nonempty signed-source evidence. Pure fixtures and an empty
catalog cannot establish that requirement.

API50's complete18-case failure suite and11 controls passed with actual exits0,
adding29 complete cases to typed10. The same serialized driver continues full146,
classification16, review11, exports134, metadata86, machine14 and termination6.
Those source-specific qualifications do not qualify API51.

Next: finish the same actual host checks, preserve any failures, qualify nonempty
source composition and all API51 inherited suites, implement16 missing operations,
assigned Machine typed participation and authority/internal endpoint resolvers.
Complete genuine R05 participant evidence, genuinely reviewed model changes where
required, R06/R07 and all-member S02 before the sole actual R08 decision.

API47/API48 failed and interrupted evidence remains preserved. Unknown exits,
cleanup and old claims are not inferred or restored. Existing live stores, keys,
private Session memory and unrelated work remain outside construction scope.

R03-0090 binds15,726 files. No complete API, stable release or full plan outcome
is claimed.
''')
    handoff=load(RUN/'custody-integration-handoff-0076.json')
    handoff.update(current_progress_binding=bind(progress),currentness_binding=bind(current),current_status_binding=bind(status),
        current_API_source_binding=bind(BASE/'api-v51/source-manifest.json'),current_API_profile_binding=bind(BASE/'api-v51/contract-profile.json'))
    handoff['closed_jobs_do_not_repoll']=sorted(set(handoff['closed_jobs_do_not_repoll']+[17218,90328,91272,61644,87442,95341]))
    handoff['same_live_jobs']=[
        {'session_id':28245,'initial_chunk_id':'c3944a','state':'last-observed-running','owned_driver_PID':21680,
         'owned_child_PID':32885,'suite':'API50 same452-case regression: complete39; full146 running',
         'driver_binding':bind(RUN/'run-API50-serialized-regression-0001.py'),'whole_API_qualified':False},
        {'session_id':18103,'initial_chunk_id':'2ba6a0','state':'last-observed-running','owned_driver_PID':35000,
         'suite':'API51 actual lesson3 on zero-Lesson signed source; no terminal result observed',
         'driver_binding':bind(BASE/'api51-lesson-checks-v1/checks.py'),'whole_API_qualified':False}]
    handoff['new_scoped_evidence'].update(API50='Actual PASS39 in typed10/failure18/controls11; same driver full146 running. API50 scopes only.',
        current_API51='Frozen18 authored handlers/16 missing, original34 contracts/293 methods and old policy sets retained; no current version runtime qualification yet.',
        lesson_select='Host and closed read policy materialized;61 pure successor cases and53 retained W06 tests PASS. Actual lesson3 runner running; nonempty signed source/context/ontology successor still required.')
    handoff['next_action']=[
        'Revalidate same18103/PID35000. Bind actual API51 lesson3 report/terminal; preserve failed outcomes and do not restart on observation timeout.',
        'Revalidate same28245/PID21680 and full146 child32885; continue every selected original API50 suite.',
        'Qualify actual nonempty signed Lesson source and its governed Context/Ontology successor; do not transplant synthetic objects or weaken original zero-catalog guards.',
        'Run all original API51 scopes under its own source/profile; use declared successor handler-count checks18 without altering retained assertions.',
        'Complete16 missing operations, assigned Machine typed support, authority resolvers, genuine R05/R06/R07/S02 and sole R08.'
    ]
    handoff['terminal_bindings'].extend([bind(RUN/'API50-failure18-terminal-0001.json'),bind(RUN/'API50-controls11-terminal-0001.json'),
        bind(RUN/'lesson-query-rules-terminal-0002.json'),bind(RUN/'R03-0090-currentness-terminal-0001.json')])
    hp=RUN/'custody-integration-handoff-0077.json';put(hp,handoff)
    index=RUN/'R03-CURRENT-PROGRESS-0090.json'
    put(index,{'schema_version':'lab-current-progress-index/v1-candidate','publisher_binding':bind(Path(__file__).resolve()),
        'progress_binding':bind(progress),'currentness_binding':bind(current),'status_binding':bind(status),'handoff_binding':bind(hp),
        'closed_tasks':36,'total_tasks':46,'authority_effect':'none','task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(index),'status':bind(status),'handoff':bind(hp),
                      'goal_complete':False}),flush=True)


if __name__=='__main__':main()
