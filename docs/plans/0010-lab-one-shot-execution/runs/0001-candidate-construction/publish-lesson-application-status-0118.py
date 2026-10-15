"""Publish original lesson.assess candidate implementation and pending qualification."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v82'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    progress = API / 'receipts/R03-0118.json'
    p = load(progress)
    current = sorted((RUN / 'currentness-receipts').glob('*.json'))[-1]
    c = load(current)
    assert c['result'] == 'PASS' and c['completed_tasks'] == 36 and c['total_tasks'] == 46
    assert any(row['task'] == 'R03' and row['receipt'] == progress.relative_to(ROOT).as_posix() for row in c['active_receipt_checks'])
    for version in [79, 80]:
        assert not (RUN / f'API{version}-machine-lifecycle-full-terminal-0001.json').exists(), 'Publish actual terminal outcome instead of stale running claim.'
    status = RUN / 'OPERATIONAL-FOUNDATION-STATUS-0118.md'
    with status.open('x') as stream:
        stream.write('''# Lab current Machine and guarded read qualification

**36/46 tasks closed. 23/34 handlers authored; 11 remain missing.**
R03 and R06 remain in progress. The complete Lab/API remain unqualified.

Fresh Source5, Reader4, Mapper4 and Context9 component evidence remains valid.
Context9 passed actual construction, all50 cases and43,827 independent checks.
It produced30 carriers retaining23 original bodies and25 exact native joins.

API78 completed all20 original cases:14 Machine failures at a stale mapper
digest,6 termination passes,0 Machine public replies. The original mapper guard
independently refused the stale digest and accepted the current package's cold
native replay. API79 binds the actual current mapper package. Its first original
identity/signature/shared-custody test passed; the complete selection is running.

API80 uses the existing guarded model_read_batch across complete query and
connection calculations. Both original calculation ASTs and all323 test method
ASTs remain unchanged. Exact current/historical prefix selection, original byte
readers and source/schema guards remain. Permission checks, real clocks and the
900-second Session ceiling are unchanged. This candidate scope change requires
actual runtime and original affected branch qualification; no speed claim is made.

Live selections: API79 job35646 and API80 job19391, each with14 original Machine
and6 original termination cases. Observe these same jobs; partial output is not
a restart condition. No current Machine or complete API qualification is inferred.

Original lesson.assess is authored in API81 under a separately selected private
recorded-outcome method. It binds exact current application, evidence and
counterevidence, original prospective target/core validation and causal ceiling.
It returns a candidate ChangeProposal through original guarded calculation and
journal paths. All323 methods remain; only3 exact registry-count expectations
change21to22. Authoring checks passed; runtime qualification remains pending.
The selected signed source contains no Lesson Application records. Positive
qualification requires an actual controlled application and bound evidence.
No application, interpreted truth or broader/causal effectiveness is inferred.

Original lesson.apply is authored in API82 with actual parent operator/Session
custody, exact current Lesson/selection/applicability/instruction, scoped conflict
overrides and original delegated operations. It prepares an attributed application
ChangeProposal through original candidate/core validation and journal paths;
no tool dispatch occurs. All323 methods retained, with3 exact registry-count
expectations22to23. Authoring checks pass; runtime examples remain pending.

The API80 immediate Machine Context query diagnostic passed1 actual case using
original fixture/bridge/real clock. The long seven-operation read case still
errored after actual successful query/inspect replies; complete original suite
results and timing/expiry diagnosis remain. Source/context explanatory copied
anchor/count discrepancies are preserved and corrected in a bound clarification.

Remaining: all11 missing handlers, original affected API selections and reference
refusals, R05 integration journeys, R06 privacy and R07 acceptance. S02 must freeze
the complete package before the sole actual R08 owner response. A01-A04 retain
separately scoped application/acceptance effects. Existing authorization covers
candidate construction and isolated checks; canonical admission, live/existing
stores, activation, external effects, push and deployment remain excluded.
''')
    parent = RUN / 'custody-integration-handoff-0099.json'
    old = load(parent)
    handoff = RUN / 'custody-integration-handoff-0100.json'
    closed = [94242, 42299, 66562]
    emit(handoff, {**old, 'parent_handoff_binding': bind(parent),
                   'current_progress_binding': bind(progress), 'currentness_binding': bind(current),
                   'current_status_binding': bind(status), 'current_API_source_binding': p['source_binding'],
                   'current_API_profile_binding': p['profile_binding'],
                   'same_live_jobs': [
                       {'tool_session_id': 35646, 'API': 79, 'selected_cases': 20,
                        'selection_binding': bind(RUN / 'API79-independent-selection-0001.json')},
                       {'tool_session_id': 19391, 'API': 80, 'selected_cases': 20,
                        'selection_binding': bind(RUN / 'API80-independent-selection-0001.json')}],
                   'closed_jobs_do_not_repoll': sorted(set(old['closed_jobs_do_not_repoll'] + closed)),
                   'next_action': p['remaining_obligations'], 'current_Machine_qualified': False, 'authored_handlers': 23, 'unimplemented_operations': 11,
                   'whole_API_qualified': False, 'goal_complete': False})
    index = RUN / 'R03-CURRENT-PROGRESS-0118.json'
    emit(index, {'schema_version': 'lab-current-progress-index/v1-candidate',
                 'publisher_binding': bind(Path(__file__).resolve()), 'progress_binding': bind(progress),
                 'currentness_binding': bind(current), 'status_binding': bind(status), 'handoff_binding': bind(handoff),
                 'closed_tasks': 36, 'total_tasks': 46, 'authored_handlers': 23, 'unimplemented_operations': 11,
                 'API78_original20_terminal_observed': True, 'API78_original_termination_passes': 6,
                 'API79_first_original_Machine_case_result': 'PASS',
                 'same_live_jobs': [35646, 19391], 'current_Machine_qualified': False,
                 'whole_API_qualified': False, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'PUBLISHED-SCOPED-PROGRESS', 'index': bind(index),
                      'status': bind(status), 'handoff': bind(handoff), 'same_live_jobs': [35646, 19391]}), flush=True)


if __name__ == '__main__':
    main()
