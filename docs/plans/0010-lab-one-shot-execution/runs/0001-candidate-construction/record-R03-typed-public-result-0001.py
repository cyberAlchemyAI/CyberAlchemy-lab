"""Bind complete API49 public qualification and the pending lesson composition."""
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
    parent = BASE / 'api-v50/receipts/R03-0086.json'
    old = load(parent)
    report_path = BASE / 'api49-typed-checks-v1/receipts/checks-0001.json'
    report = load(report_path)
    terminal_path = RUN / 'API49-typed10-terminal-0001.json'
    terminal = load(terminal_path)
    assert terminal['actual_exit_code'] == 0 and terminal['actual_cases'] == 10
    assert terminal['full_selected_suite_completed'] and terminal['original_reader_guarded_exit_completed']
    assert report['result'] == 'PASS' and report['actual_cases'] == 10
    assert report['failures'] == report['errors'] == 0 and report['original_reader_guarded_exit_completed']
    assert report['source_sha256'] == '70a59c0f1c5cd96bedd523a024827a41e2b8f54f3ca0f6a685599ff4d6fe14aa'
    for key in ['report_binding', 'log_binding', 'check_source_binding']:
        row = terminal[key]
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    rows = {row['path']: row for row in old['files']}
    lesson = BASE / 'lesson-selection-contract-v1/source-manifest.json'
    selected = load(lesson)
    assert selected['structural_schema_checks'] == 3 and not selected['public_handler_integrated']
    for row in selected['files'] + selected['input_bindings']:
        rows[row['path']] = row
    for path in [parent, Path(__file__).resolve(), report_path, terminal_path,
        BASE / 'api49-typed-checks-v1/receipts/wire-0001.json', RUN / 'API49-typed10-0001.log', lesson]:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    value = {**old, 'files': [rows[key] for key in sorted(rows)], 'parent_progress_binding': bind(parent),
        'change': 'API49 full authenticated typed10 completed PASS10/FAIL0/ERROR0 with actual exit0 and original reader guarded exit. API50 exact status correction and452 selected full regression cases remain running. Closed lesson routing/applicability/domain contracts and complete host design materialized;3 schema structure checks pass, actual lesson handler still pending.',
        'API49_typed_operator_runtime_qualified': True,
        'API49_typed_qualification_source_sha256': report['source_sha256'],
        'API49_typed_qualification_profile_sha256': report['profile_sha256'],
        'API49_typed_public_report_binding': bind(report_path), 'API49_typed_public_terminal_binding': bind(terminal_path),
        'API49_typed_public_counts': {'PASS': 10, 'FAIL': 0, 'ERROR': 0},
        'API49_actual_public_calls': report['actual_public_calls'],
        'API49_original_reader_guarded_exit_completed': True,
        'API49_owned_fixture_cleanup_basis': 'All10 tests and their registered Context Manager cleanups completed with0 failures/errors; original frozen fixture closes Service, drops signer and asserts the owned temporary root absent. Original class projection/config and reader/source exit guards completed.',
        'API49_genuine_semantic_review_provided': False, 'API49_assigned_Agent_qualified': False,
        'current_typed_operator_runtime_qualified': False, 'API50_full_public_runtime_qualified': False,
        'lesson_selection_contract_binding': bind(lesson), 'lesson_selection_public_handler_integrated': False,
        'current_full_public_suite_verdict': None,
        'claim_ceiling': 'Complete public typed qualification for exact API49 operator source and synthetic targets only. API50 qualification and lesson public implementation remain incomplete. No assigned Agent typed permission, genuine semantic review, operational scope grant, admission, full API or full plan completion.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    value['remaining_obligations'] = list(old['remaining_obligations']) + [
        'Implement and qualify the lesson.select host composition against the frozen three internal contracts and original public Context Query/Lesson Selection.',
        'Retain the original W06 controlled profile and tests; general Lab applicability cannot silently reuse its fixed retention/family or review assumptions.',
        'Use complete current lesson inventory, actual trusted live Session/Assignment and independent policy-selected review/applicability evidence. Empty current catalog alone cannot qualify nonempty selection.']
    path = BASE / 'api-v50/receipts/R03-0087.json'
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
                      'API49_typed_cases': 10, 'API50_qualified': False, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()
