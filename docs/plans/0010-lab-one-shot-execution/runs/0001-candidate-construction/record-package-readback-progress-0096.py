"""Bind completed managed readback evidence without claiming public integration."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PACKAGE = BASE / 'package-publication-v2'


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
    parent_path = BASE / 'api-v52/receipts/R03-0095.json'
    parent = load(parent_path)
    report_path = PACKAGE / 'receipts/checks-0001.json'
    report, manifest = load(report_path), load(PACKAGE / 'source-manifest.json')
    assert report['result'] == 'PASS' and report['real_filesystem_fixture_cases'] == 53
    assert report['failures'] == report['errors'] == 0
    assert report['full_selected_suite_completed'] and report['source_guarded_exit_completed']
    assert report['owned_temporary_fixture_cleanup_completed']
    assert report['actual_public_calls'] == report['public_handlers_added'] == 0
    assert not report['actual_authenticated_host_used'] and not report['whole_API_qualified']
    assert manifest['retained_predecessor_cases'] == 33 and manifest['added_readback_cases'] == 20
    assert report['source_sha256'] == manifest['source_sha256'] == '75518f6554dab3625eab49c760643d641377a63d375fede5e7ee47353997a2ec'
    terminal = RUN / 'package-readback53-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': 14367, 'initial_chunk_id': '78d3ad', 'final_chunk_id': 'c90856',
        'actual_exit_code': 0, 'result': 'PASS', 'actual_cases': 53, 'failures': 0, 'errors': 0,
        'source_guarded_exit_completed': True, 'report_binding': bind(report_path),
        'log_binding': bind(PACKAGE / 'receipts/actual-0001.log'),
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    rows = {row['path']: row for row in parent['files']}
    for row in manifest['files'] + manifest['input_bindings'] + report['files']:
        rows[row['path']] = row
    for path in (parent_path, report_path, terminal, PACKAGE / 'source-manifest.json', Path(__file__).resolve()):
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    value = {**parent, 'files': [rows[k] for k in sorted(rows)],
        'parent_progress_binding': bind(parent_path),
        'change': 'Managed package publication v2 implements independently selected read-only package retrieval. It verifies exact archive, manifest, receipt and durable marker under shared locks, current host callbacks, root and generation identity; absence, pending writes, tampering and unsafe files require reconciliation without repair. All 33 predecessor filesystem test methods are retained; 20 new readback tests passed. No public package handler or authenticated-host qualification is added.',
        'package_publication_v2_source_binding': bind(PACKAGE / 'source-manifest.json'),
        'package_publication_v2_actual_checks_binding': bind(report_path),
        'package_publication_v2_terminal_binding': bind(terminal),
        'package_publication_v2_filesystem_cases': 53,
        'package_publication_v2_retained_predecessor_cases': 33,
        'package_publication_v2_added_readback_cases': 20,
        'package_publication_v2_managed_readback_qualified': True,
        'package_publication_v2_actual_authenticated_host_qualified': False,
        'package_publication_v2_public_handlers_added': 0,
        'claim_ceiling': 'Complete bounded managed filesystem component with synthetic source/permission callbacks only. Current original API52 remains 18 authored handlers and 16 missing; source closure/privacy and public package transport/model qualification remain pending. No canonical admission, genuine participant evidence, whole API or completed plan.',
        'remaining_obligations': [
            'Integrate the verified package publication v2 readback with actual authenticated package host controls; callers cannot supply arbitrary paths. Verify original signed source, complete portable dependencies/provenance/privacy, mapping/disposition, target model and current permission/deadline before claiming public export/import.',
            *parent['remaining_obligations']],
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = BASE / 'api-v52/receipts/R03-0096.json'
    emit(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
        'readback_filesystem_cases': 53, 'handlers': 18, 'missing': 16,
        'task_complete': False, 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
