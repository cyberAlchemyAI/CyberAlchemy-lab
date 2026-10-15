"""Publish verified component progress and preserve the actual live API selection."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v78'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    progress = API / 'receipts/R03-0114.json'
    p = load(progress)
    current = sorted((RUN / 'currentness-receipts').glob('*.json'))[-1]
    c = load(current)
    assert c['result'] == 'PASS' and c['completed_tasks'] == 36 and c['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix() for row in c['active_receipt_checks'])
    assert p['fresh_Context_component_qualified'] and p['API77_Machine_lifecycle_outcome']['actual_cases'] == 0
    terminal = RUN / 'API78-machine-lifecycle-full-terminal-0001.json'
    assert not terminal.exists(), 'Publish actual terminal outcome instead of a stale running claim.'
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0114.md'
    text = '''# Lab fresh source and Context integration

**36/46 tasks closed. 21/34 public handlers authored; 13 remain missing.**
R03 and R06 remain in progress. The complete Lab and API remain unqualified.

## Completed component work

- Fresh signed Source5: 20 tests and 94 independent audit checks passed.
- Reader4: 20 tests and 137 independent audit checks passed.
- Mapper4: all 29 predecessor methods and 251 independent checks passed.
- Context9: actual build, all 50 cases and 43,827 independent audit checks passed.

The source retains all 23 original artifact bodies and independently fixed
periods. The native projection has 15 nodes and 10 edges. Context construction
produced 30 artifact carriers. Disposable source stores, signers and host keys
were removed; no saved Session or Agent memory was restored. Current permissions,
real clocks, revocation checks and the 900-second Session ceiling remain.

## Current API work

API77's original 20-case Machine/termination selection failed during schema setup:
zero cases, zero public replies, two errors. Its repository-only profile reader
received an absolute native-executable path. That failed observation is retained.

API78 separates repository profile rows from the explicit external native
dependency. The complete source and Context guards still bind that executable.
Every prospective repository row passed the original repository reader, and all
323 API77 test method ASTs remain unchanged. The original 14 Machine and six
termination cases are running as job 33812. No outcome is inferred from startup.

## Remaining work and decision boundary

Observe the same job and record its actual outcome. Qualify the affected inherited
API selections and remaining typed reference refusal cases. Implement the 13
missing operations listed in the linked progress receipt, then complete original
R05 journeys, R06 privacy and R07 acceptance.

S02 freezes the complete review package. R08 remains the sole owner admission
checkpoint, with independent member scopes retained in one exact review.
Existing authorization covers candidate construction and isolated validation.
Canonical admission before R08, existing/live stores, activation, external
effects, push and deployment remain excluded. A01-A04 retain their separately
scoped application and operational acceptance requirements.
'''
    with status.open('x') as stream:
        stream.write(text)
    parent_handoff = RUN / 'custody-integration-handoff-0096.json'
    old = load(parent_handoff)
    closed = [71833, 3150, 54000, 21170, 74671, 44028, 44583, 40276, 14584, 64431,
              41290, 65656, 38356, 61723, 37627, 3624]
    handoff = RUN / 'custody-integration-handoff-0097.json'
    emit(handoff, {'schema_version': 'lab-current-execution-handoff/v1-candidate',
                   'objective': 'complete the plan', 'parent_handoff_binding': bind(parent_handoff),
                   'current_progress_binding': bind(progress), 'currentness_binding': bind(current),
                   'current_status_binding': bind(status), 'current_API_source_binding': p['source_binding'],
                   'current_API_profile_binding': p['profile_binding'],
                   'qualified_fresh_Context_binding': p['fresh_Context_qualification_binding'],
                   'same_live_jobs': [{'tool_session_id': 33812, 'selected_cases': 20,
                                       'selection_binding': p['Machine_lifecycle_selection_binding'],
                                       'instruction': 'Observe same actual process; partial output is not a restart condition.'}],
                   'closed_jobs_do_not_repoll': sorted(set(old['closed_jobs_do_not_repoll'] + closed)),
                   'next_action': p['remaining_obligations'], 'closed_tasks': 36, 'total_tasks': 46,
                   'original_public_operations': 34, 'authored_handlers': 21, 'unimplemented_operations': 13,
                   'current_Machine_qualified': False, 'whole_API_qualified': False,
                   'sole_owner_checkpoint': 'S02 complete exact package, then R08 actual owner response',
                   'authorization_binding': bind(RUN / 'authorization.json'),
                   'authority_effect': 'none', 'actual_owner_outcome': None, 'goal_complete': False})
    index = RUN / 'R03-CURRENT-PROGRESS-0114.json'
    emit(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
                 'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
                 'currentness_binding': bind(current), 'status_binding': bind(status), 'handoff_binding': bind(handoff),
                 'closed_tasks': 36, 'total_tasks': 46, 'authored_handlers': 21, 'unimplemented_operations': 13,
                 'fresh_Context_component_qualified': True, 'current_Machine_qualified': False,
                 'same_live_job': 33812, 'whole_API_qualified': False,
                 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
                      'status': bind(status), 'handoff': bind(handoff), 'same_live_job': 33812}), flush=True)


if __name__ == '__main__':
    main()
