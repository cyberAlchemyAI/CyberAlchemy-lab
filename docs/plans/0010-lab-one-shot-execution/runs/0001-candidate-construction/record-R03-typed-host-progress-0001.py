"""Synchronize authored authenticated typed host and actual scoped evidence."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v48'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parent = BASE / 'api-v47/receipts/R03-0083.json'
    old = load(parent)
    assert old['result'] == 'PASS' and not old['task_complete']
    assert bind(API / 'source-manifest.json')['sha256'] == 'a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6'
    selected = load(RUN / 'API48-typed-host-selection-checks-0002.json')
    assert selected['result'] == 'PASS' and selected['actual_cases'] == 42 and selected['actual_public_calls'] == 0
    assert load(RUN / 'API48-selection-terminal-0002.json')['actual_exit_code'] == 0
    focused = load(RUN / 'API46-core-schema-focused-0001.json')
    assert focused['result'] == 'PASS' and focused['actual_tests'] == 2 and focused['errors'] == 0
    assert focused['original_reader_entry_exit_and_source_guards_completed']
    interruption = load(RUN / 'API47-failure18-interrupted-terminal-0001.json')
    assert interruption['actual_exit_code'] == 143 and not interruption['full_suite_verdict_established']
    rows = {r['path']: r for r in old['files']}
    for row in load(API / 'source-manifest.json')['files']:
        rows[row['path']] = row
    for package in [BASE / 'api48-typed-checks-v1', BASE / 'api48-current-checks-v1']:
        for row in load(package / 'source-manifest.json')['files']:
            rows[row['path']] = row
    extras = [parent, API / 'source-manifest.json', API / 'contract-profile.json',
        BASE / 'api48-typed-checks-v1/source-manifest.json', BASE / 'api48-current-checks-v1/source-manifest.json',
        RUN / 'API46-core-schema-focused-0001.json', RUN / 'API46-core-schema-focused-terminal-0001.json',
        RUN / 'API46-core-schema-focused-0001.log', RUN / 'API48-typed-host-selection-checks-0001.log',
        RUN / 'API48-typed-host-selection-checks-0002.json', RUN / 'API48-typed-host-selection-checks-0002.log',
        RUN / 'API48-selection-attempt-0001-terminal.json', RUN / 'API48-selection-terminal-0002.json',
        RUN / 'verify-API48-typed-host-selection-0001.py', RUN / 'verify-API48-typed-host-selection-0002.py',
        RUN / 'API48-freeze-terminal-0001.json', RUN / 'API48-public-qualification-freeze-terminal-0001.json',
        RUN / 'API47-failure18-interrupted-terminal-0001.json', RUN / 'current-API47-failure18-0001.log',
        RUN / 'run-API48-serialized-public-qualification-0001.py', Path(__file__).resolve()]
    for path in extras:
        row = bind(path)
        rows[row['path']] = row
    # Preserve the completed observations of the interrupted predecessor; do
    # not bind any new live log or evolving result as completed evidence.
    for path in (BASE / 'api-v47/receipts/per-call-observations').glob('*.json'):
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    value = {**old, 'source_binding': bind(API / 'source-manifest.json'),
        'profile_binding': bind(API / 'contract-profile.json'), 'parent_progress_binding': bind(parent),
        'files': [rows[k] for k in sorted(rows)],
        'change': 'API46 original core/schema cases14/15 completed PASS2. API47 full failure18 interrupted with actual exit143 after3 completed cases; no full verdict or guarded exit/cleanup inferred. API48 freezes authenticated operator typed host, exact closed policy and original journal integration;42 pure selection/shape checks PASS. Eight public typed and strict original146/11 successors are frozen and serialized execution started.',
        'implemented_public_handlers': 17, 'typed_host_routing_registered_public_handler': True,
        'typed_operator_host_composition_authored': True, 'typed_operator_public_qualified': False,
        'typed_assigned_Agent_qualified': False, 'API48_full_public_runtime_qualified': False,
        'typed_selection_checks_binding': bind(RUN / 'API48-typed-host-selection-checks-0002.json'),
        'typed_selection_actual_cases': 42, 'API46_focused_checks_binding': bind(RUN / 'API46-core-schema-focused-0001.json'),
        'successor_original_case_result_established': True, 'successor_original_case_actual_counts': {'PASS': 2, 'FAIL': 0, 'ERROR': 0},
        'API47_interrupted_terminal_binding': bind(RUN / 'API47-failure18-interrupted-terminal-0001.json'),
        'API47_full_suite_verdict_established': False, 'API47_cleanup_proven': False,
        'API47_runtime_verification_result_established': False,
        'current_full_suites': ['API48 actual public typed8', 'API48 strict current controls11',
                              'API48 original failure18', 'API48 strict full original146'],
        'current_full_public_suite_verdict': None,
        'current_serialized_public_driver_binding': bind(RUN / 'run-API48-serialized-public-qualification-0001.py'),
        'remaining_obligations': [
            'Qualify all21 original outstanding operations;17 authored handlers do not establish runtime qualification.',
            'Finish the actual API48 serialized public suites with original real clocks,900-second bounds, all source/policy predicates and cleanup assertions.',
            'Preserve interrupted API47 exit143 and its old incomplete claims/workspaces. Complete attribution and reconciliation without private-key inspection or replacing an old outcome.',
            'Complete assigned Machine Agent typed policy/host composition and its actual participation qualifications.',
            'Complete all other original current suites and full source/permission/refusal/retry/recovery/uncertainty criteria.',
            'Replace synthetic extension fixture with genuinely reviewed complete model change and exact independently selected operational authority.',
            'Implement governed internal endpoint and specialized canonical authority resolvers.',
            'Complete genuine R05 participant evidence, R06, R07 and S02 before the sole actual R08 owner decision.',
            'Actual owner outcomes and independently scoped authorization remain required before A01-A04 effects.'],
        'claim_ceiling': 'Scoped candidate implementation and actual pure checks only. Authenticated operator typed handler is authored, runtime qualification is running. Preserve143 interruption without a full verdict. Original34 contracts/293 methods retained; no genuine semantic owner verdict, assigned Agent qualification, operational scope grant or admission.',
        'whole_API_qualified': False, 'current_Agent_qualified': False,
        'normal_runtime_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = API / 'receipts/R03-0084.json'
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
                      'authored_handlers': 17, 'public_typed_qualified': False, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()
