"""Publish scoped current state without converting authored handlers into proof."""
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
    progress = BASE / 'api-v48/receipts/R03-0084.json'
    current = RUN / 'currentness-receipts/0149.json'
    value, checked = load(progress), load(current)
    assert value['result'] == checked['result'] == 'PASS' and not value['task_complete']
    assert checked['completed_tasks'] == 36 and checked['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in checked['active_receipt_checks'])
    assert load(RUN / 'R03-0084-currentness-terminal-0001.json')['actual_exit_code'] == 0
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0084.md'
    text = '''# Lab operational foundation: current candidate progress

The existing development authorization covers continued candidate implementation
and verification. The sole owner admission checkpoint remains R08 after complete
S02. There is no owner admission outcome for this package.

## Current state

| Item | State |
| --- | --- |
| Plan | 36 of 46 tasks closed; R03 and R06 in progress |
| Public model | 34 contracts; 17 handlers authored |
| Qualification | 13 historical scoped qualifications; 21 original qualifications remain |
| Typed helper | Frozen v11: 144 pure checks PASS |
| Typed operator host | Authored in API48; public execution qualification running |
| Typed selection and shape | 42 checks PASS, including 25 complete inventory checks |
| Original core/schema checks | API46 cases14/15: 2 PASS, 0 failures, 0 errors; guarded exit complete |
| Earlier full failure suite | API45: 16 PASS, 2 FAIL, 0 errors; original failed assertions retained |
| Interrupted successor | API47: actual exit143 after 3 completed cases; no full verdict |
| Current verification | API48 typed8, controls11, original failure18 and full146 serialized |
| Admission | R08 pending complete S02 |

## What was added

API48 registers `typed.extension.prepare` through a declared closed successor
policy and the original authenticated operator dispatcher. All nine earlier
authentication variants, 34 public contract schemas and 293 original test methods
remain. The new composition binds the actual authenticated Actor, current cut,
outer durable key, exact owned route and independently selected target metadata.

The complete original catalog, helper source and 144-case proof are selected by
fixed byte bindings. Endpoint and affected-carrier successor closure is derived
independently. Original wire/noncollapse and coupled body/schema/core/postimage
checks run over the actual signed source selection. Candidate material cannot
shadow the captured canonical catalog. Schema destinations must be unique,
canonical relative paths and exactly cover the proposal's schema inventory.
The original 64-target and 1,000-element frame array bounds remain distinct.

The original bounded pure scope stages evidence. Original producer, source and
actual policy/expiry checks complete before publication; journal completion and
recorded retry remain in the existing dispatcher. Optional scope hypotheses
retain the actual refusal and unprovisioned copied configuration. They grant no
operational authority. Assigned Machine Agent support remains unqualified.

## Verification and preserved failures

Forty-two pure selection and offline policy/routing shape checks passed. They
include the complete schema inventory and declared external migration-source
pins. These fixtures supply no actual transport, permission or owner verdict.

The initial freeze attempt failed because its final verifier tried to convert
an already declared absolute migration path to a repository-relative path. The
attempt and frozen v2 composition remain intact. V3 preserves those exact paths
with original file, symlink and hash checks. API48's final freeze completed.

The first shape-check run passed all25 inventory methods but failed its synthetic
authorization placeholder: the unchanged original policy requires the exact
development authorization binding. A successor fixture supplies that exact
binding and passes42 checks. The actual policy contract was preserved.

API46's two original focused cases completed with source/custody entry and exit
guards. Incomplete cores retain pending uncertainty; exact invalid-schema
refusals retain their validation evidence. This is scoped evidence, not full
runtime qualification.

The API47 full failure run ended with actual exit143 after three completed cases
and the fourth case started. Its cause, full verdict and guarded exit/cleanup
are not established. Its observations are preserved. Existing temporary failure
roots have insufficient attribution and remain untouched; private keys were not
inspected and old claims were not cleared or redispatched.

The new API48 run uses fresh owned fixtures and actual ReaderChannel signatures,
policy bytes, source replay and durable journal. All8 new typed cases, all11
original controls, all18 original failure cases and all146 original source cases
are selected serially. Separate strict test successors change only the three
obsolete exact handler-count assertions from15 to17; every other AST is retained.
Their runtime outcomes are not established by this status.

## Remaining work and final decision

1. Complete the live serialized verification and every other original current
   suite. Preserve real clocks, absolute participation periods, uncertainty,
   retry/recovery and cleanup assertions.
2. Complete assigned Machine Agent typed composition, governed internal endpoint
   contracts and specialized canonical authority resolvers.
3. Replace synthetic model fixtures with genuinely reviewed complete changes and
   their exact independently scoped operational authority. Reconcile attribution
   of the interrupted predecessor's incomplete state without clearing old claims.
4. Complete genuine R05 participant evidence, R06, R07 and freeze full S02.
5. Present the exact package and evidence for the sole R08 owner admission.

The plan remains active and incomplete. Candidate preparation creates no genuine
semantic owner verdict, admitted relation, operational scope grant or activation.

Currentness149 PASS: 38 active receipts, 77 preserved preparation files and
887 baseline sources; no changes. R03-0084 binds 15,313 files and retains all
incomplete criteria.
'''
    with status.open('x') as stream:
        stream.write(text)
    handoff = load(RUN / 'custody-integration-handoff-0071.json')
    handoff['current_progress_binding'] = bind(progress)
    handoff['currentness_binding'] = bind(current)
    handoff['current_status_binding'] = bind(status)
    handoff['current_API_source_binding'] = bind(BASE / 'api-v48/source-manifest.json')
    handoff['current_API_profile_binding'] = bind(BASE / 'api-v48/contract-profile.json')
    handoff['implemented_public_handlers'] = 17
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] +
        [37740, 21283, 59768, 62391, 84003, 82388, 39693, 22931, 26483, 97539]))
    handoff['same_live_jobs'] = [{'session_id': 25516, 'initial_chunk_id': '99e51c',
        'state': 'last-observed-running', 'owned_driver_PID': 365370, 'owned_typed_child_PID': 365371,
        'suite': 'API48 serial typed8 -> controls11 -> original failure18 -> strict full146',
        'driver_binding': bind(RUN / 'run-API48-serialized-public-qualification-0001.py'),
        'typed_checks_source_binding': bind(BASE / 'api48-typed-checks-v1/source-manifest.json'),
        'strict_checks_source_binding': bind(BASE / 'api48-current-checks-v1/source-manifest.json'),
        'log_path': (RUN / 'API48-serialized-public-qualification-0001.log').relative_to(ROOT).as_posix(),
        'typed_log_path': (RUN / 'API48-typed8-0001.log').relative_to(ROOT).as_posix(),
        'whole_API_qualified': False}]
    handoff['new_scoped_evidence'].update(
        typed_operator_host='API48 authored17 handlers; operator typed composition and closed policy. Actual public qualification running.',
        typed_selection='PASS42 pure selection/offline shape checks; no public transport or grant in that evidence.',
        original_core_schema='API46 original cases14/15 PASS2 with source/custody exit guards.',
        interrupted_API47='Actual143 after3 completed cases; no full verdict, cause or guarded exit/cleanup inferred.')
    handoff['next_action'] = [
        'Continue same25516 driver and actual child365371. Read logs/terminal before assuming any result. Do not restart on observation timeout.',
        'Bind actual typed8/controls11/failure18/full146 terminal and complete reports. Keep original assertions, real clocks and source/cleanup guards.',
        'Preserve API47 interrupted observations and unknown-attribution temporary roots. Do not inspect private keys or clear old claims.',
        'Complete remaining original qualifications, assigned Agent support, authority resolvers, genuine R05/R06/R07/S02 and sole R08 decision.']
    handoff['terminal_bindings'].extend(bind(RUN / name) for name in [
        'API46-core-schema-focused-terminal-0001.json', 'API47-failure18-interrupted-terminal-0001.json',
        'API48-freeze-attempt-0001-terminal.json', 'API48-freeze-terminal-0001.json',
        'API48-selection-attempt-0001-terminal.json', 'API48-selection-terminal-0002.json',
        'API48-public-qualification-freeze-terminal-0001.json', 'R03-0084-currentness-terminal-0001.json'])
    handoff_path = RUN / 'custody-integration-handoff-0072.json'
    put(handoff_path, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0084.json'
    put(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(current), 'status_binding': bind(status), 'handoff_binding': bind(handoff_path),
        'closed_tasks': 36, 'total_tasks': 46, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index), 'status': bind(status),
                      'handoff': bind(handoff_path), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
