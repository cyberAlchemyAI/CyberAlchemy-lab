"""Publish current progress and the exact continuing jobs without success claims."""
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


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    progress = BASE / 'api-v52/receipts/R03-0091.json'
    currentness = RUN / 'currentness-receipts/0155.json'
    current = load(currentness)
    assert current['result'] == 'PASS' and current['completed_tasks'] == 36 and current['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in current['active_receipt_checks'])
    terminal = RUN / 'R03-0091-currentness-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': 4847, 'initial_chunk_id': '7e2756', 'final_chunk_id': '5eda2d',
        'actual_exit_code': 0, 'result': 'PASS', 'currentness_binding': bind(currentness),
        'closed_tasks': 36, 'total_tasks': 46, 'authority_effect': 'none', 'goal_complete': False})
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0091.md'
    with status.open('x') as stream:
        stream.write('''# Current Lab candidate progress

36/46 plan tasks closed; R03 and R06 in progress. The plan remains incomplete.
Current candidate API52: 34 original contracts, 18 authored handlers, 16 missing.

## Changes and observed verification

- API51 lesson transport: complete three-case suite FAIL, three errors, actual exit 1; full source exit guard completed. Failure and wire evidence preserved.
- API52: exclusive repair selects the actual live Session's parent ReaderChannel for the unchanged fact scope. The Machine peer remains guarded inside the scope. Disposed/revoked channels return the original unauthenticated transport error; a cleared context cannot produce a trusted reply.
- Static construction passed; all 293 inherited methods and three lesson regression assertions retained. No original fact kernel, callback, clock, expiry or permission widened.
- API52 three actual lesson cases are running under session 29782/PID 39122. No successful runtime or nonempty Lesson qualification is claimed.
- API50 original serialized regression remains session 28245/PID 21680, full146 child 32885. Typed10, failure18 and controls11 are complete PASS39. The other 413 selected cases remain pending complete suite results; qualification applies to API50 only.
- Lesson rules: 61 pure successor cases and all 53 original W06 cases passed. These do not qualify actual nonempty public use.
- Currentness155 PASS: 38 active receipts, 77 preparation files and 887 baseline sources; no changes.

## Approval and remaining requirements

Continue existing authorized candidate construction and full suites. One final
R08 checkpoint follows complete S02. It must bind exact independent members,
accountable owner roles, evidence and separately scoped local instructions.
No actual owner outcome, admission, activation, push or deployment exists.

Next: close actual API52 transport defects from its exact results; qualify a
nonempty signed Lesson source and declared Context/Ontology successor; qualify
all inherited API52 scopes; implement 16 remaining operations and actual assigned
Machine typed support; complete genuine R05 pilot, R06/R07/S02 and final R08.

Governance review: [Boundary review](GOVERNANCE-BOUNDARY-REVIEW-0091.md).
R03-0091 binds 15,845 files. No complete API or full plan result is claimed.
''')
    handoff = load(RUN / 'custody-integration-handoff-0077.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(currentness),
        current_status_binding=bind(status), current_API_source_binding=bind(BASE / 'api-v52/source-manifest.json'),
        current_API_profile_binding=bind(BASE / 'api-v52/contract-profile.json'))
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] + [18103, 75031, 35025, 46673, 4847]))
    handoff['same_live_jobs'] = [
        {'session_id': 28245, 'initial_chunk_id': 'c3944a', 'state': 'last-observed-running',
         'owned_driver_PID': 21680, 'owned_child_PID': 32885,
         'suite': 'API50 same452-case regression: complete39; full146 running',
         'driver_binding': bind(RUN / 'run-API50-serialized-regression-0001.py'), 'whole_API_qualified': False},
        {'session_id': 29782, 'initial_chunk_id': 'cf7cb3', 'state': 'last-observed-running',
         'owned_driver_PID': 39122, 'suite': 'API52 three actual lesson cases; terminal result pending',
         'driver_binding': bind(BASE / 'api52-lesson-checks-v1/checks.py'), 'whole_API_qualified': False}]
    handoff['new_scoped_evidence'].update(
        failed_API51='Complete three-case suite FAIL with three errors and actual exit1. No runtime qualification.',
        current_API52='Exclusive parent-reader scope and closed-peer transport repair frozen;18 handlers/16 missing. All293 inherited methods and three lesson assertions retained. Runtime qualification pending.',
        governance='Existing candidate authorization applies; one final R08 after complete S02 with exact independent member and local operation scopes.')
    handoff['next_action'] = [
        'Observe same29782/PID39122; preserve its actual report and terminal. No restarts on observation timeout and no successful qualification before actual PASS.',
        'Observe same28245/PID21680/full146child32885; complete all original selected API50 suites without changing frozen sources.',
        'Qualify actual nonempty signed Lesson source and governed Context/Ontology successor; never fabricate Session objects or relax original zero-catalog/source guards.',
        'Complete all inherited API52 qualification and16 missing operations, actual Machine typed grant and authority resolvers.',
        'Complete genuine pilot evidence and R06/R07/S02; collect sole actual final R08 before A01-A04.']
    handoff['terminal_bindings'].extend([bind(RUN / 'API51-lesson3-terminal-0001.json'),
        bind(RUN / 'API52-construction-terminal-0001.json'), bind(terminal)])
    path = RUN / 'custody-integration-handoff-0078.json'
    emit(path, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0091.json'
    emit(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(currentness), 'status_binding': bind(status), 'handoff_binding': bind(path),
        'governance_review_binding': bind(RUN / 'GOVERNANCE-BOUNDARY-REVIEW-0091.md'),
        'closed_tasks': 36, 'total_tasks': 46, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
        'status': bind(status), 'handoff': bind(path), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
