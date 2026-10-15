"""Bind actual authenticated import evidence and preserve failed regression scope."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v53'
CHECK = BASE / 'api53-package-checks-v1'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    predecessor = BASE / 'api-v52/receipts/R03-0096.json'
    old = load(predecessor)
    manifest = load(API / 'source-manifest.json')
    profile = load(API / 'contract-profile.json')
    report_path = CHECK / 'receipts/checks-0001.json'
    report = load(report_path)
    assert report['result'] == 'PASS' and report['actual_cases'] == 3 and report['actual_public_calls'] == 9
    assert report['errors'] == report['failures'] == 0
    assert report['source_guarded_exit_completed'] and report['owned_fixture_cleanup_completed']
    assert report['actual_authenticated_host_used'] and report['actual_import_positive_completed']
    assert not report['whole_API_qualified'] and not report['general_foreign_source_import_qualified']
    assert len(profile['implemented_operations']) == 19 and manifest['unchanged_inherited_method_count'] == 293
    wire = load(CHECK / 'receipts/wire-0001.json')
    assert len(wire) == 9
    positives = [row for row in wire if row['original_call']['operation'] == 'package.import'
                 and row['reply'].get('kind') == 'result']
    assert len(positives) == 2 and positives[0]['reply']['message'] == positives[1]['reply']['message']
    assert all(row['reply']['handler_binding'] == {'ref': str((API / 'package_import.py').relative_to(ROOT)),
        'sha256': bind(API / 'package_import.py')['sha256']} for row in positives)
    full_path = RUN / 'API50-full146-terminal-0001.json'
    full = load(full_path)
    assert full['actual_exit_code'] == 1 and full['actual_cases'] == 146
    assert full['failures'] == full['errors'] == 1 and full['full_selected_suite_completed']
    terminal = RUN / 'API53-package3-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': 28664, 'initial_chunk_id': 'df5662', 'final_chunk_id': 'ee3eab',
        'actual_exit_code': 0, 'result': 'PASS', 'actual_cases': 3, 'actual_public_calls': 9,
        'source_guarded_exit_completed': True, 'owned_fixture_cleanup_completed': True,
        'report_binding': bind(report_path), 'log_binding': bind(CHECK / 'receipts/actual-0001.log'),
        'wire_binding': bind(CHECK / 'receipts/wire-0001.json'),
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    rows = {r['path']: r for r in old['files']}
    for r in manifest['files'] + report['files']:
        rows[r['path']] = r
    for path in (predecessor, API / 'source-manifest.json', API / 'contract-profile.json', report_path,
                 terminal, full_path, ROOT / full['report_binding']['path'],
                 ROOT / full['log_binding']['path'], RUN / 'API50-driver-failed-attempt-terminal-0001.json',
                 RUN / 'run-API50-remaining-regression-0002.py', Path(__file__).resolve()):
        r = bind(path)
        rows[r['path']] = r
    for r in rows.values():
        assert hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'], r['path']
    value = {**old, 'files': [rows[k] for k in sorted(rows)], 'parent_progress_binding': bind(predecessor),
        'source_binding': bind(API / 'source-manifest.json'), 'profile_binding': bind(API / 'contract-profile.json'),
        'implemented_operations': profile['implemented_operations'], 'authored_handlers': 19,
        'missing_operations': sorted(set(load(ROOT / 'docs/proposals/0008-lab-api-contracts/api-contracts.json')['operations'][i]['operation']
            for i in range(34)) - set(profile['implemented_operations'])),
        'change': 'API53 adds actual authenticated same-cut candidate Work import with independently selected managed generation, source/target proposals, mapping/disposition and exact source provenance. Native model checks and declared Work-reference/original schema dependency accounting run before claim in a discarded buffer and after claim with evidence committed only after original source exit. Nine actual public calls across three complete cases passed, including pure retry and tampering recovery. All 34 original contracts and 293 inherited methods remain. API50 full146 finished with one real-clock deadline failure and one already-disposed Session error; original driver stopped. A new scheduler resumes only the six unexecuted suites after the import job exited, preserving all original failures and clocks.',
        'package_import_actual_checks_binding': bind(report_path), 'package_import_actual_terminal_binding': bind(terminal),
        'package_import_actual_cases': 3, 'package_import_actual_public_calls': 9,
        'package_import_same_cut_Work_candidate_qualified': True,
        'package_general_foreign_or_admitted_source_import_qualified': False,
        'public_package_export_qualified': False, 'current_API53_whole_suite_qualified': False,
        'API50_full146_terminal_binding': bind(full_path),
        'API50_completed_selected_cases': 185, 'API50_passed_selected_cases': 183,
        'API50_failed_selected_cases': 1, 'API50_errored_selected_cases': 1,
        'API50_remaining_selected_cases': 267,
        'remaining_obligations': [
            'Complete general foreign/admitted-source import authority/provenance and carrier coverage, and actual public export with complete portable dependency/privacy proof. The verified same-cut Work lane does not replace the original full package contracts.',
            'Complete the remaining267 original API50 selected cases through the new owned scheduler and repair/qualify the two failed expiry cases in a reviewed implementation successor without extending deadlines or weakening original assertions. Preserve failed API50 evidence.',
            'Qualify every current API53 inherited journey and all15 missing public operations; the three package cases do not qualify the whole current API or lesson/machine journeys.',
            *old['remaining_obligations']],
        'claim_ceiling': 'Actual three-case/nine-call authenticated same-cut candidate Work import only. Source publication grant is fixture-only; no public export, general source authority, new canonical admission, whole API, genuine pilot or completed plan. API50 full146 completed but failed two expiry checks; six suites remain active under an exclusive continuation scheduler.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = API / 'receipts/R03-0097.json'
    path.parent.mkdir(exist_ok=False)
    emit(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
        'actual_public_calls': 9, 'authored_handlers': 19, 'missing': 15,
        'task_complete': False, 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
