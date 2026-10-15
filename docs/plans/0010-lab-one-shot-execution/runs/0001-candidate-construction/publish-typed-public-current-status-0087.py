"""Publish exact API49 evidence, API50 ongoing regression and lesson obligations."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    progress = BASE / 'api-v50/receipts/R03-0087.json'
    current = RUN / 'currentness-receipts/0151.json'
    checked = load(current)
    assert checked['result'] == 'PASS' and checked['completed_tasks'] == 36 and checked['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in checked['active_receipt_checks'])
    assert load(RUN / 'R03-0087-currentness-terminal-0001.json')['actual_exit_code'] == 0
    assert load(progress)['API49_typed_operator_runtime_qualified']
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0087.md'
    with status.open('x') as stream:
        stream.write('''# Lab operational foundation: current candidate progress

The plan remains active. Existing authorization covers candidate implementation,
full verification and newly owned isolated development fixtures. The sole final
owner admission remains R08 after full S02; no admission outcome exists yet.

## Current state

| Item | State |
| --- | --- |
| Plan | 36 of46 tasks closed; R03/R06 in progress |
| Public inventory | 34 contracts,17 authored handlers,17 named missing operations |
| Earlier qualification | 13 historical scoped qualifications retained |
| API49 typed operator | Full10 cases PASS;0 failures,0 errors; actual exit0 |
| API49 public calls | 12 actual authenticated calls, including exact recorded retry |
| API49 exit | Original reader/source guarded exit and unchanged projection/config checked |
| Pure identity/selection | 6 wire/noncollapse +41 inventory/preclaim checks PASS |
| Current source | API50 frozen with accurate missing-operation status |
| Current regression | 452 selected cases across10 full suites; serialized execution running |
| Lesson integration | Host design and3 closed internal schemas frozen; handler pending |
| Admission | Single final R08 pending full S02 |

## Verified typed preparation

The corrected actual operator flow prepares an exact typed Change Proposal with
the original authenticated Actor, signed policy bytes, independent route, current
source cut, complete schema/core/body/postimage checks and durable operation key.
Its expected out-of-scope admission is refused. Recorded retry returns the same
result without another journal effect. An incomplete core retains pending
uncertainty. Actor spoofing, unsupported operation, changed route, duplicate schema
destination, wrong review, expiry and both inspection identity mismatches are
refused under their original assertions.

All10 cases completed, then original reader and source exit checks completed.
Frozen fixture cleanups close Service, release the ephemeral signer and assert
the owned temporary root absent. This proves the exact API49 operator candidate
scope with synthetic targets. It supplies no genuine semantic owner verdict,
assigned Machine typed permission, operational grant or repository admission.

API48's earlier typed8 actual failure and interrupted controls remain intact.
Seven controls completed in its log; the eighth started, without a final report.
Its unavailable process has no known exit code or proved cleanup. Earlier API47
actual exit143 remains a separate interruption. Old claims and keys were not
reused. Only absent code was recreated; the native reader bytes match the
historical selected executable.

## Exact operation coverage and complete regression

API50 replaces the stale20-missing status text with the exact selected contract
inventory minus registered handlers. It now reports17 missing operation names.
All34 original public schemas and293 original test methods remain unchanged.

The fresh serialized regression waits for the same API49 full report and actual
process exit, then executes typed10, failure18, controls11, full146,
classification16, review11, exports134, metadata86, machine14 and termination6.
These452 cases include overlap between original runners. Every assertion,
original real clock, absolute participation period, source/permission guard and
cleanup check remains. Three separately versioned handler-count assertions retain
the previously declared15-to17 correction. Historical runner metadata is
preserved and does not establish current qualification. No current aggregate
result is claimed before complete actual terminal evidence.

## Lesson selection integration

The original lesson.select contract consumes Context Query and returns Lesson
Selection with selected, omitted and blocked exact revisions. The new internal
routing, applicability and domain profile schemas select actual live Session and
Assignment facts, independent instruction precedence, complete source inventory,
exact review and applicability witnesses. Missing evidence is explicit and blocks
that lesson. Unknown current Lesson carriers cannot become a false empty catalog.

Existing W06 conditions cover expiry, exclusions, source/family identity,
counterevidence, instructions and conflicting influences. Its controlled source
repair is specific: its fixed retention and review assumptions cannot silently
define all Lab lessons. The host design requires explicit generalization,
preserved W06 tests and real empty/nonempty signed-source qualification.

The three schema structure checks passed. These artifacts are internal candidate
runtime contracts, not new canonical Artifact Types or public API contracts. The
lesson handler, assigned Machine composition and general lesson selection remain
implementation and qualification obligations.

## Remaining requirements

1. Finish the452 current selected regressions, preserving failed or incomplete
   outcomes, original clocks and exact source/permission boundaries.
2. Implement all17 missing public operations and their complete original contracts.
   Complete lesson.select, assigned Machine typed participation, governed internal
   endpoint contracts and specialized canonical authority resolvers.
3. Use genuinely reviewed model changes and exact independent authority where
   required. Synthetic fixtures cannot replace actual review or genuine R05 users.
4. Complete R05 participant evidence, R06, R07 and freeze all-member S02 closure.
5. Present the exact complete package and evidence for the sole R08 owner decision.

Currentness151 PASS:38 active receipts,77 original preparation files,887 baseline
sources and no changes. R03-0087 binds15,580 files. The goal remains incomplete.
''')
    handoff = load(RUN / 'custody-integration-handoff-0073.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(current),
        current_status_binding=bind(status), current_API_source_binding=bind(BASE / 'api-v50/source-manifest.json'),
        current_API_profile_binding=bind(BASE / 'api-v50/contract-profile.json'))
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] +
        [44943, 47083, 25601, 34365, 53849, 29409, 44074]))
    handoff['same_live_jobs'] = [{'session_id': 28245, 'initial_chunk_id': 'c3944a',
        'state': 'last-observed-running', 'owned_driver_PID': 21680, 'owned_child_PID': 22387,
        'suite': 'API50 serialized452 regression cases; typed10 currently running',
        'driver_binding': bind(RUN / 'run-API50-serialized-regression-0001.py'),
        'typed_source_binding': bind(BASE / 'api50-typed-checks-v1/source-manifest.json'),
        'strict_source_binding': bind(BASE / 'api50-current-checks-v1/source-manifest.json'),
        'log_path': (RUN / 'API50-typed10-0001.log').relative_to(ROOT).as_posix(),
        'whole_API_qualified': False}]
    handoff['new_scoped_evidence'].update(
        API49_typed_public='Actual PASS10/FAIL0/ERROR0;12 public calls, exact retry, original reader/source exit and fixture cleanup assertions completed. Operator candidate only.',
        current_API50='Exact status count17missing;34 schemas/293 methods preserved;452 selected original current cases executing serially.',
        lesson_select='Complete host design and3 structurally checked closed internal contracts frozen. Public implementation/runtime qualification pending.')
    handoff['next_action'] = [
        'Observe same28245 driver21680; inspect each actual child/report/terminal. Never restart solely on observation timeout.',
        'Bind complete actual API50 typed10/failure18/controls11/full146/classification16/review11/exports134/metadata86/machine14/termination6 results.',
        'Implement and qualify lesson.select through frozen lesson-selection-contract-v1 with actual live transport/Assignment and complete source inventory.',
        'Complete all17 remaining operations, assigned Machine typed support, authority resolvers, genuine R05/R06/R07/S02 and sole R08 decision.',
        'Keep original failed and interrupted evidence. No old private key, short memory, claim or fixture restoration.']
    handoff['terminal_bindings'].extend([bind(RUN / 'API49-typed10-terminal-0001.json'),
                                       bind(RUN / 'R03-0087-currentness-terminal-0001.json')])
    hp = RUN / 'custody-integration-handoff-0074.json'
    put(hp, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0087.json'
    put(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(current), 'status_binding': bind(status), 'handoff_binding': bind(hp),
        'closed_tasks': 36, 'total_tasks': 46, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
                      'status': bind(status), 'handoff': bind(hp), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
