"""Publish corrected candidate status and actual unavailable-process evidence."""
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
    progress = BASE / 'api-v49/receipts/R03-0085.json'
    current = RUN / 'currentness-receipts/0150.json'
    value, checked = load(progress), load(current)
    assert value['result'] == checked['result'] == 'PASS' and not value['task_complete']
    assert checked['completed_tasks'] == 36 and checked['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in checked['active_receipt_checks'])
    assert load(RUN / 'R03-0085-currentness-terminal-0001.json')['actual_exit_code'] == 0
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0085.md'
    text = '''# Lab operational foundation: current candidate progress

Existing authorization covers candidate implementation and verification. The
single final owner checkpoint remains R08 after complete S02.

## Current state

| Item | State |
| --- | --- |
| Plan | 36 of 46 tasks closed; R03 and R06 in progress |
| Public model | 34 contracts; 17 handlers authored |
| Qualification | 13 historical scoped qualifications; 21 original qualifications remain |
| Current candidate | API49 frozen; original34 schemas and293 test methods retained |
| Identity repair | Exact proposal and successor identities joined independently |
| Pure verification | 6 complete wire/noncollapse checks and41 selection/preclaim checks PASS |
| Previous typed suite | API48: 8 cases,7 PASS,1 FAIL,0 errors; actual exit1 |
| Previous controls | 7 completed log cases; eighth started; process unavailable; exit unknown |
| Restored code | Exact selected dependencies; native reader hash matches original |
| Current public verification | Fresh API49 typed10 started; full result pending |
| Admission | Sole R08 pending complete S02 |

## What changed

The original typed fixture supplied different proposal names and successor
revisions to its proposal and inspector. The corrected fixture selects the exact
same identities before rebuilding byte bindings. All eight original public test
methods remain unchanged; two additional cases require identity mismatches to be
refused before a durable operation claim.

The candidate host now checks the independently selected inspection against the
exact proposal, relation target, predecessor, semantic question, axis, noncollapse
report and complete ordered qualifier domains during preflight. Full original
wire/noncollapse, body/schema/core/postimage checks remain. Pure checks establish
these structural properties; public runtime qualification is still pending.

## Actual verification and interruption

API48 typed8 completed with an actual failure, original guarded reader exit and
zero errors. Its seven passing cases do not qualify the corrected runtime: some
downstream negative expectations could have passed at an earlier identity refusal.
The failed report, wire observations and actual exit1 remain intact.

The old API48 driver and its tool session are unavailable. Controls completed
seven log cases and started case8, with no final report or terminal. Its exit
status and cause are unknown. No complete suite, guarded exit, cleanup or disposal
is inferred. Previous API47 actual exit143 remains separately preserved.

The earlier temporary Python environment and native executable were absent.
Selected dependency wheels were checked and installed offline into a new code
environment. The native reader was rebuilt from frozen inputs and resolved locks;
its bytes match the original hash. No old Agent, key, short memory, operation
claim or fixture was restored. A new context selects fresh isolated verification
after the interruption while retaining all incomplete predecessor obligations.

## Remaining work and decision

1. Finish corrected public typed10 and every original current suite, preserving
   real clocks, absolute participation periods, uncertainty and cleanup checks.
2. Complete assigned Machine Agent composition, governed internal endpoint
   contracts and specialized canonical authority resolvers.
3. Complete genuinely reviewed model changes and independently scoped authority;
   synthetic test fixtures provide no genuine owner verdict or operational grant.
4. Complete actual R05 participant evidence, R06, R07 and full S02.
5. Present the exact package and evidence for the sole final R08 admission.

Currentness150 PASS:38 active receipts,77 preserved preparation files and887
baseline sources; no changes. R03-0085 binds15,456 files. Candidate preparation
provides no admission, activation or complete plan outcome.
'''
    with status.open('x') as stream:
        stream.write(text)
    handoff = load(RUN / 'custody-integration-handoff-0072.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(current),
                   current_status_binding=bind(status), current_API_source_binding=bind(BASE / 'api-v49/source-manifest.json'),
                   current_API_profile_binding=bind(BASE / 'api-v49/contract-profile.json'))
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] +
        [25516, 33645, 33188, 18521, 10849, 89106, 45119]))
    handoff['same_live_jobs'] = [{'session_id': 44943, 'initial_chunk_id': '35e9ba',
        'state': 'last-observed-running', 'owned_driver_PID': 9233, 'owned_child_PID': 9268,
        'suite': 'API49 fresh authenticated typed10',
        'driver_binding': bind(RUN / 'run-API49-recovery-qualification-0001.py'),
        'checks_source_binding': bind(BASE / 'api49-typed-checks-v1/source-manifest.json'),
        'log_path': (RUN / 'API49-typed10-0001.log').relative_to(ROOT).as_posix(),
        'whole_API_qualified': False}]
    handoff['new_scoped_evidence'].update(
        typed_operator_host='API49 authored17 handlers; exact preclaim identity joins; actual public result pending.',
        typed_identity='6 full original wire/noncollapse and41 pure selection/preclaim checks PASS.',
        prior_API48='Typed8 completed actual FAIL1/PASS7/ERROR0. Controls process unavailable after7 completed cases; exit unknown.',
        restored_code='Offline selected wheels and exact native reader bytes restored; no old state or Agent restored.')
    handoff['next_action'] = [
        'Observe same44943 driver/PID9233 and child9268; bind actual terminal and complete report before qualification.',
        'Do not restart on observation timeout or declare interrupted suites complete.',
        'Finish every original current suite, assigned Machine support, authority resolvers and genuine R05/R06/R07/S02.',
        'Preserve unavailable predecessor logs and unknown exit; no old private keys, memory or claims may be reused.',
        'Keep sole final R08 owner checkpoint and full original goal criteria.']
    handoff['terminal_bindings'].extend([bind(RUN / 'API48-typed8-terminal-0001.json'),
        bind(RUN / 'API48-unavailable-driver-observation-0001.json'),
        bind(RUN / 'native-code-restoration-0003.json'), bind(RUN / 'R03-0085-currentness-terminal-0001.json')])
    handoff_path = RUN / 'custody-integration-handoff-0073.json'
    put(handoff_path, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0085.json'
    put(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(current), 'status_binding': bind(status), 'handoff_binding': bind(handoff_path),
        'closed_tasks': 36, 'total_tasks': 46, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index), 'status': bind(status),
                      'handoff': bind(handoff_path), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
