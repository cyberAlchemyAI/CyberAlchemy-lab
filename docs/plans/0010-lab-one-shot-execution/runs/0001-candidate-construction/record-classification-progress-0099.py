"""Bind qualified focused classification repair and completed predecessor journeys."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v56'
CHECK = BASE / 'api56-classification-checks-v1'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    predecessor = BASE / 'api-v55/receipts/R03-0098.json'
    old = load(predecessor)
    manifest = load(API / 'source-manifest.json')
    profile = load(API / 'contract-profile.json')
    focused_path = CHECK / 'receipts/focused-0001.json'
    focused = load(focused_path)
    assert focused['result'] == 'PASS' and focused['actual_cases'] == 3
    assert focused['errors'] == focused['failures'] == 0
    assert focused['source_guarded_exit_completed'] and focused['owned_fixture_cleanup_completed']
    assert focused['original_test_file_unchanged'] and focused['original_cases_retained'] == 16
    assert not focused['whole_API_qualified']
    wire = load(CHECK / 'receipts/focused-wire-0001.json')
    assert len(wire) == 4
    assert [row['reply']['kind'] for row in wire] == ['result', 'error', 'error', 'error']
    assert wire[2]['reply']['message']['code'] == 'indeterminate'
    assert wire[3]['reply']['message']['code'] == 'recovery-required'
    session_path = RUN / 'API55-session-affected7-child-terminal-0001.json'
    sessions = load(session_path)
    package_path = RUN / 'API55-package3-child-terminal-0001.json'
    package = load(package_path)
    review_path = RUN / 'API50-review11-terminal-0002.json'
    review = load(review_path)
    for report, expected in [(sessions, 7), (package, 3), (review, 11)]:
        assert report['actual_exit_code'] == 0 and report['actual_cases'] == expected
        assert report['full_selected_suite_completed'] and report['errors'] == report['failures'] == 0
    assert sessions['source_guarded_exit_completed'] and sessions['owned_fixture_cleanup_completed']
    assert package['source_guarded_exit_completed'] and package['owned_fixture_cleanup_completed']
    package_report = load(ROOT / package['report_binding']['path'])
    assert package_report['actual_public_calls'] == 9 and package_report['actual_import_positive_completed']
    assert len(profile['implemented_operations']) == 19 and manifest['unchanged_inherited_method_count'] == 293
    terminal = RUN / 'API56-classification-focused3-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': 55912, 'initial_chunk_id': 'f97412', 'final_chunk_id': '5fff4f',
        'actual_exit_code': 0, 'result': 'PASS', 'actual_cases': 3, 'actual_public_calls': 4,
        'source_guarded_exit_completed': True, 'owned_fixture_cleanup_completed': True,
        'report_binding': bind(focused_path), 'log_binding': bind(CHECK / 'receipts/focused-0001.log'),
        'wire_binding': bind(CHECK / 'receipts/focused-wire-0001.json'),
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    driver_terminal = RUN / 'API55-affected-qualification-terminal-0001.json'
    emit(driver_terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': 81506, 'initial_chunk_id': '56b58a', 'final_chunk_id': '8f1fbe',
        'actual_exit_code': 0, 'result': 'PASS', 'actual_selected_cases': 10,
        'suite_terminal_bindings': [bind(session_path), bind(package_path)],
        'source_guarded_exit_completed': True, 'owned_fixture_cleanup_completed': True,
        'whole_API_qualified': False, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    rows = {r['path']: r for r in old['files']}
    for row in manifest['files'] + focused['files']:
        rows[row['path']] = row
    paths = [predecessor, API / 'source-manifest.json', API / 'contract-profile.json',
        CHECK / 'source-manifest.json', focused_path, terminal, driver_terminal,
        session_path, package_path, review_path, Path(__file__).resolve()]
    for result in [sessions, package, review]:
        paths.extend(ROOT / result[key]['path'] for key in ['report_binding', 'log_binding'])
        report = load(ROOT / result['report_binding']['path'])
        for row in report.get('files', []):
            rows[row['path']] = row
    for path in paths:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    value = {**old, 'files': [rows[k] for k in sorted(rows)], 'parent_progress_binding': bind(predecessor),
        'source_binding': bind(API / 'source-manifest.json'), 'profile_binding': bind(API / 'contract-profile.json'),
        'implemented_operations': profile['implemented_operations'], 'authored_handlers': 19,
        'implemented_public_handlers': 19, 'unimplemented_public_operation_count': 15,
        'change': 'API56 binds classification v8 and passes all three focused cases/four actual public calls. The independently versioned axis case proves nine exact proposal targets with five domain/four typed relations, original signatures/endpoints/qualifiers; the original test source stays unchanged. Both original bad-core tests pass: failed native validation evidence remains after original source exit while the operation is indeterminate/pending, with recovery-required retry and no command/classifier result. API55 affected Session7 and actual import3/9 calls completed PASS/exit0. API50 review11 completed PASS/exit0; all earlier failures remain. Full API56 classification16 is running; fifteen operations and the whole plan remain unfinished.',
        'classification_focused_checks_binding': bind(focused_path),
        'classification_focused_terminal_binding': bind(terminal),
        'classification_focused_actual_cases': 3, 'classification_focused_actual_public_calls': 4,
        'classification_v8_authored_but_unbound': False, 'classification_v8_runtime_qualified': True,
        'classification_v8_runtime_qualification_scope': 'Three focused cases only; full16 result not yet established.',
        'classification_full16_qualified': False, 'current_API56_whole_suite_qualified': False,
        'historical_API55_original_expiry_checks_binding': old['original_expiry_checks_binding'],
        'historical_API55_affected_Session_checks_binding': sessions['report_binding'],
        'historical_API55_package_import_checks_binding': package['report_binding'],
        'historical_API55_affected_qualification_terminal_binding': bind(driver_terminal),
        'historical_API55_same_cut_Work_import_qualified': True,
        'original_expiry_runtime_qualified': False, 'package_import_same_cut_Work_candidate_qualified': False,
        'package_import_actual_cases': 0, 'package_import_actual_public_calls': 0,
        'current_API56_package_import_qualified': False,
        'API50_review11_terminal_binding': bind(review_path),
        'API50_completed_selected_cases': 212, 'API50_passed_selected_cases': 208,
        'API50_failed_selected_cases': 3, 'API50_errored_selected_cases': 1,
        'API50_remaining_selected_cases': 240,
        'remaining_obligations': [
            'Complete the same full16 API56 classification job, then qualify every current inherited journey and package lane; focused classification and historical API55 journeys do not qualify the whole current API.',
            'Complete the same API50 remaining240 scheduler, now exports134; preserve all actual failed scopes and original clocks.',
            'Implement all15 remaining public operations and complete general foreign/admitted-source package authority/carrier coverage and portable public export with complete dependency/privacy proof.',
            'Complete nonempty Lesson/Context/Ontology sources, actual Machine write authority and internal/specialized authority resolution, genuine R05 participant evidence, R06/R07 and all-member S02. Sole actual R08 precedes separately authorized A01-A04.'],
        'claim_ceiling': 'Three focused authenticated classification cases/four calls against exact API56 only. API55 Session7/import3 and API50 review11 are completed predecessor evidence. Full classification16 and the remaining240 original selections are live; no complete API, genuine pilot, owner outcome, admission, activation or complete plan.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = API / 'receipts/R03-0099.json'
    path.parent.mkdir(exist_ok=True)
    emit(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
        'actual_focused_cases': 3, 'actual_public_calls': 4, 'authored_handlers': 19,
        'missing_operations': 15, 'task_complete': False, 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
