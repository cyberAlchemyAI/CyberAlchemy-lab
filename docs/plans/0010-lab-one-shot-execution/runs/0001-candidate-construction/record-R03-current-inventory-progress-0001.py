"""Record exact current API coverage and the full queued regression selection."""
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


def main():
    parent = BASE / 'api-v49/receipts/R03-0085.json'
    old = load(parent)
    rows = {row['path']: row for row in old['files']}
    for name in ['api-v50', 'api50-current-checks-v1', 'api50-typed-checks-v1']:
        manifest = BASE / name / 'source-manifest.json'
        for row in load(manifest)['files']:
            rows[row['path']] = row
        row = bind(manifest)
        rows[row['path']] = row
    extras = [parent, Path(__file__).resolve(),
        RUN / 'API50-status-inventory-static-0001.json', RUN / 'context-R03-API50-full-regression-0001.json',
        RUN / 'run-API50-serialized-regression-0001.py']
    for path in extras:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    proof = load(RUN / 'API50-status-inventory-static-0001.json')
    assert proof['result'] == 'PASS' and proof['declared_count'] == 34
    assert proof['authored_count'] == proof['unimplemented_count'] == 17
    assert proof['retained_original_test_methods'] == 293
    context = load(RUN / 'context-R03-API50-full-regression-0001.json')
    assert context['total_selected_cases'] == 452
    api = BASE / 'api-v50'
    value = {**old, 'files': [rows[key] for key in sorted(rows)],
        'parent_progress_binding': bind(parent), 'source_binding': bind(api / 'source-manifest.json'),
        'profile_binding': bind(api / 'contract-profile.json'),
        'change': 'API50 corrects stale status20-missing text:34 original contracts minus17 registered handlers gives17 exact named missing operations. All293 original methods retained. Full452 selected current regression cases frozen, including all original full runners and corrected typed10; serialized queue waits for same API49 actual terminal and process exit.',
        'unimplemented_public_operations': proof['unimplemented_operations'],
        'unimplemented_public_operation_count': 17,
        'current_full_suites': context['selected_public_suites'], 'current_full_suite_selected_cases': 452,
        'selected_cases_include_runner_overlap': True,
        'current_full_public_suite_verdict': None, 'API50_full_public_runtime_qualified': False,
        'current_serialized_public_driver_binding': bind(RUN / 'run-API50-serialized-regression-0001.py'),
        'claim_ceiling': 'Exact authored and missing operation inventory plus frozen full regression selection. Queued execution supplies no result; runtime qualification, assigned Agent support, genuine R05, remaining17 operation implementations, full S02 and R08 remain.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    value['remaining_obligations'] = list(old['remaining_obligations']) + [
        'Complete every one of the17 named unimplemented public handlers under its original contract.',
        'Complete all452 selected current regression cases; overlaps and historical runner metadata must not inflate qualification claims.',
        'Integrate the existing W06 lesson-selection semantics with actual trusted live Session/Assignment and current exact signed source through the original lesson.select public contract.']
    path = api / 'receipts/R03-0086.json'
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
                      'missing_operations': 17, 'selected_regression_cases': 452, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()
