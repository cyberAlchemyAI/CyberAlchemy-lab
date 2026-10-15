"""Bind completed original expiry evidence without closing the full task."""
import argparse
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v55'
CHECK = BASE / 'api55-session-checks-v1'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    if path.name=='API55-expiry2-terminal-0001.json' and path.exists():
        assert load(path)==value, 'preserve the actual completed expiry terminal'
        return
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--session-id', type=int, required=True)
    parser.add_argument('--initial-chunk-id', required=True)
    parser.add_argument('--final-chunk-id', required=True)
    args = parser.parse_args()
    predecessor = BASE / 'api-v53/receipts/R03-0097-0002.json'
    old = load(predecessor)
    manifest = load(API / 'source-manifest.json')
    profile = load(API / 'contract-profile.json')
    report_path = CHECK / 'receipts/checks-0001.json'
    report = load(report_path)
    assert report['result'] == 'PASS' and report['actual_cases'] == 2
    assert report['errors'] == report['failures'] == 0
    assert report['source_guarded_exit_completed'] and report['owned_fixture_cleanup_completed']
    assert report['original_70_second_deadlines_unchanged'] and report['original_90_second_waits_unchanged']
    assert report['original_test_methods_unchanged'] and report['original_source_callbacks_unchanged']
    assert not report['whole_API_qualified'] and not report['full_regression_qualified']
    assert len(profile['implemented_operations']) == 19 and manifest['unchanged_inherited_method_count'] == 293
    measurement_path = RUN / 'API53-original-expiry-profile-0001.json'
    measurement = load(measurement_path)
    assert measurement['test_result'] == 'FAIL' and measurement['measurement_completed']
    assert measurement['profiling_adds_runtime_overhead']
    classification_path = RUN / 'API50-classification16-terminal-0002.json'
    classification = load(classification_path)
    assert classification['actual_exit_code'] == 1 and classification['actual_cases'] == 16
    assert classification['failures'] == 2 and classification['errors'] == 0
    assert classification['full_selected_suite_completed']
    terminal = RUN / 'API55-expiry2-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': args.session_id, 'initial_chunk_id': args.initial_chunk_id, 'final_chunk_id': args.final_chunk_id,
        'actual_exit_code': 0, 'result': 'PASS', 'actual_cases': 2,
        'source_guarded_exit_completed': True, 'owned_fixture_cleanup_completed': True,
        'report_binding': bind(report_path), 'log_binding': bind(CHECK / 'receipts/actual-0001.log'),
        'wire_binding': bind(CHECK / 'receipts/wire-0001.json'),
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    rows = {r['path']: r for r in old['files']}
    for r in manifest['files'] + report['files'] + measurement['files']:
        rows[r['path']] = r
    for path in (predecessor, API / 'source-manifest.json', API / 'contract-profile.json', report_path,
                 terminal, measurement_path, classification_path,
                 RUN / 'record-session-scope-progress-0098.py',
                 RUN / 'R03-0098-producer-failed-attempt-terminal-0001.json',
                 RUN / 'API54-expiry2-failed-terminal-0001.json',
                 ROOT / classification['report_binding']['path'], ROOT / classification['log_binding']['path'],
                 Path(__file__).resolve()):
        r = bind(path)
        rows[r['path']] = r
    for path in [RUN / 'CLASSIFICATION-GAPS-0001.md', *(BASE / 'classification-preparation-v8').glob('*')]:
        if path.is_file():
            r=bind(path);rows[r['path']]=r
    for r in rows.values():
        assert hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'], r['path']
    value = {**old, 'files': [rows[k] for k in sorted(rows)], 'parent_progress_binding': bind(predecessor),
        'source_binding': bind(API / 'source-manifest.json'), 'profile_binding': bind(API / 'contract-profile.json'),
        'implemented_operations': profile['implemented_operations'], 'authored_handlers': 19,
        'implemented_public_handlers': 19, 'unimplemented_public_operation_count': 15,
        'change': 'API55 groups post-claim Session eligibility, exact delivered proof and pure opening metadata into one original sealed source scope. Its full source/policy exit precedes actual LiveReader creation and journal writes. Original callbacks, registry, policy rereads, real clocks and disposal remain. The original Context producer is selected and fully verified once per synchronous policy call; its module handle is reused only within that invocation. Original preflight and reader selection remain, and no source bytes, policy or permission are cached between calls. The failed API54 note-expiry report stays bound. Reply delivery also rechecks the effective deadline after its final verification. Both original 70-second expiry tests passed unchanged, without profiling or extended waits. API53 failed profiling evidence and all failed API50 regression evidence are preserved. Other API55 journeys remain to qualify; no task is closed.',
        'original_expiry_checks_binding': bind(report_path), 'original_expiry_terminal_binding': bind(terminal),
        'original_expiry_actual_cases': 2, 'original_expiry_runtime_qualified': True,
        'API53_failed_profile_binding': bind(measurement_path),
        'historical_API53_same_cut_Work_import_qualified': True,
        'historical_API53_package_import_checks_binding': old['package_import_actual_checks_binding'],
        'historical_API53_package_import_terminal_binding': old['package_import_actual_terminal_binding'],
        'package_import_actual_cases': 0, 'package_import_actual_public_calls': 0,
        'package_import_same_cut_Work_candidate_qualified': False,
        'current_API55_package_import_qualified': False, 'current_API55_whole_suite_qualified': False,
        'API50_classification16_terminal_binding': bind(classification_path),
        'classification_gap_analysis_binding': bind(RUN / 'CLASSIFICATION-GAPS-0001.md'),
        'classification_v8_authored_but_unbound': True,
        'classification_v8_runtime_qualified': False,
        'API50_completed_selected_cases': 201, 'API50_passed_selected_cases': 197,
        'API50_failed_selected_cases': 3, 'API50_errored_selected_cases': 1,
        'API50_remaining_selected_cases': 251,
        'remaining_obligations': [
            'Qualify current API55 affected Session source-corruption/revocation/close/private-memory/retry journeys, actual package import and every inherited public journey. Two expiry cases do not qualify the whole API.',
            'Finish the same API50 remaining-suite scheduler and preserve/classify every actual failure; completed historical scopes do not qualify current API55.',
            'Complete all15 missing operations, general foreign/admitted package authority and carrier coverage, public export with full dependency/privacy closure, nonempty Lesson/Context/Ontology and actual Machine write/internal authority resolution.',
            'Complete genuine R05 participant evidence, R06/R07 and all-member S02, then sole actual R08 before independently authorized A01-A04.'],
        'claim_ceiling': 'Two unchanged original real-clock expiry tests passed against exact API55 only. Original failed profiling/API50 evidence remains. No complete regression, general package import/export, owner outcome, admission, activation, genuine pilot or completed plan.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = API / 'receipts/R03-0098.json'
    path.parent.mkdir(exist_ok=True)
    emit(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
        'actual_expiry_cases': 2, 'authored_handlers': 19, 'missing': 15,
        'task_complete': False, 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
