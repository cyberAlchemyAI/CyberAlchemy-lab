"""Publish the actual completed readback scope and retain the full active plan."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    progress = BASE / 'api-v52/receipts/R03-0096.json'
    proof = load(progress)
    currentness = RUN / 'currentness-receipts/0159.json'
    current = load(currentness)
    assert current['result'] == 'PASS' and current['completed_tasks'] == 36 and current['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix()
               for row in current['active_receipt_checks'])
    assert proof['package_publication_v2_filesystem_cases'] == 53
    assert not proof['package_publication_v2_actual_authenticated_host_qualified']
    terminal = RUN / 'R03-0096-currentness-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': 6869, 'initial_chunk_id': '5d2db5', 'final_chunk_id': 'f2b497',
        'actual_exit_code': 0, 'result': 'PASS', 'currentness_binding': bind(currentness),
        'closed_tasks': 36, 'total_tasks': 46, 'authority_effect': 'none', 'goal_complete': False})
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0096.md'
    with status.open('x') as stream:
        stream.write('''# Current Lab candidate progress

The full plan remains active: **36/46 tasks closed**. R03 and R06 are in progress.
API52 retains 18 authored handlers, 16 missing operations, all 34 original API
contracts and all 293 inherited test methods. The sole final actual owner
checkpoint remains R08 after complete S02.

## Completed change

Package publication v2 adds managed readback for import. Independent host controls
select package/request bindings, source cut, output root and generation identity.
The component reads the exact original archive and verifies the manifest, receipt
and durable publication marker under shared locks. It checks current source,
permission, deadline and root/generation identity before returning. It creates no
files or directories. Missing, incomplete, changed or unsafe generations require
reconciliation; they are preserved.

The complete filesystem suite passed: **53 cases, zero failures, zero errors,
actual exit 0**. All 33 predecessor methods were retained, with 20 new tests for
readback, tampering, pending publication, unsafe files, expired/revoked controls,
root/generation replacement and active writer locks. The callbacks are synthetic
fixtures; these tests do not establish authenticated public package permission.
The original publication v1 source and evidence remain unchanged.

## Next implementation

Connect package transfer v3 and publication v2 to actual authenticated public
package.export/import. Select controls independently and prove complete portable
dependencies, original provenance/privacy and source admission basis when claimed.
Import must verify target mapping/disposition and run original full target model
validation before returning a candidate proposal. Preserve actual budgets, clocks,
durable idempotency claims, verified read-only recovery and uncertain generations.
No public package handler has been added or qualified in this scope.

## Preserved evidence and remaining work

The previous actual signed-source audit found five unresolved Work references.
One separately prepared Work candidate passed an actual API52 change.validate call:
four checks, five resolved references, zero gaps. That proof remains limited to the
prospective target. The full source snapshot privacy probe remains failed; readback
does not permit bypassing that refusal or dropping a required dependency.

The same API50 serialized regression remains running: session28245, driver21680,
full146child32885. Typed10/failure18/controls11 completed 39 selected cases; 413
selected cases still await complete suite results. The child has progressed through
custody Session case21 and started case22. Partial log lines are not completed
suite evidence, and historical API50 does not qualify current API52.

The full plan still requires all remaining handlers/current suites, nonempty Lesson
source and governed Context/Ontology successor, actual Machine write authority,
internal/specialized authority resolvers, genuine R05 participant evidence,
R06/R07/S02, one actual R08, then independently authorized A01–A04. Candidate
construction does not admit canonical state, activate live stores or authorize push.

Currentness159 passed: 38 active receipts, 77 preparation files and 887 baseline
sources unchanged. R03-0096 binds 15,942 files. The receipt producer's first path
verification error is preserved; its exclusive successor verifies retained sibling
source bytes without changing their identity. No whole API or complete plan claim.
''')
    handoff = load(RUN / 'custody-integration-handoff-0081.json')
    handoff.update(current_progress_binding=bind(progress), currentness_binding=bind(currentness),
        current_status_binding=bind(status), current_API_source_binding=proof['source_binding'],
        current_API_profile_binding=proof['profile_binding'])
    handoff['closed_jobs_do_not_repoll'] = sorted(set(handoff['closed_jobs_do_not_repoll'] +
        [14367, 30521, 23088, 6869]))
    handoff['same_live_jobs'] = [{'session_id': 28245, 'initial_chunk_id': 'c3944a',
        'state': 'last-observed-running', 'owned_driver_PID': 21680, 'owned_child_PID': 32885,
        'suite': 'API50 same452 selected-case regression: complete39; full146 in custody Session case22',
        'driver_binding': bind(RUN / 'run-API50-serialized-regression-0001.py'),
        'whole_API_qualified': False}]
    handoff['new_scoped_evidence']['package_managed_readback'] = (
        'Publication v2 complete53 filesystem fixture tests PASS/exit0: retained33 plus new20. '
        'Independent managed selection, four verified files, no writes/repair, shared locks, '
        'current source/permission/deadline and root/generation identity. Synthetic callbacks '
        'do not qualify authenticated public package calls.')
    handoff['package_publication_v2_source_binding'] = proof['package_publication_v2_source_binding']
    handoff['package_publication_v2_actual_checks_binding'] = proof['package_publication_v2_actual_checks_binding']
    handoff['terminal_bindings'].extend([proof['package_publication_v2_terminal_binding'], bind(terminal)])
    handoff['next_action'].insert(0,
        'Integrate verified publication v2 managed readback and transfer v3 into actual authenticated package handlers, with independent controls, original complete source/dependency/privacy proof and full target validation. No arbitrary caller paths or automatic admission.')
    path = RUN / 'custody-integration-handoff-0082.json'
    emit(path, handoff)
    index = RUN / 'R03-CURRENT-PROGRESS-0096.json'
    emit(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
        'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
        'currentness_binding': bind(currentness), 'status_binding': bind(status),
        'handoff_binding': bind(path), 'closed_tasks': 36, 'total_tasks': 46,
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
                     'status': bind(status), 'handoff': bind(path), 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
