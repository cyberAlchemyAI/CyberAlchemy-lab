"""Exclusive producer repair; retain exact own emitted receipts and external source paths."""
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


def emit(path, value):
    if path.exists():
        assert load(path) == value, 'existing own derivative differs; no overwrite'
        return
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    predecessor = BASE / 'api-v52/receipts/R03-0093.json'
    old = load(predecessor)
    assert old['implemented_public_handlers'] == 18 and old['unimplemented_public_operation_count'] == 16
    assert old['source_binding'] == bind(BASE / 'api-v52/source-manifest.json')
    rows = {r['path']: r for r in old['files']}
    new_terminals = []
    packages = [
        ('package-transfer-v3', 'pure_cases', 78, 63926, 'c844a1', 'd420d8', 'package-transfer-pure-terminal-0003.json',
         '72375558b7cf9205e559e0320aca2a5bfc6c971c9a89cf1d64b71205b5d2fcb1'),
        ('package-publication-v1', 'real_filesystem_fixture_cases', 33, 73528, '062f34', '2a4189', 'package-publication-terminal-0001.json',
         'f925592eeacb64b74933652fa4223ef62f58e0e2ae7c7b90ceeb620f03b37252')]
    for name, counter, cases, session, initial, final, terminal_name, source_pin in packages:
        package = BASE / name
        source, proof = package / 'source-manifest.json', package / 'receipts/checks-0001.json'
        manifest, report = load(source), load(proof)
        assert report['result'] == 'PASS' and report[counter] == cases
        assert report['failures'] == report['errors'] == 0
        assert report['source_guarded_exit_completed'] and report['full_selected_suite_completed']
        assert report['source_sha256'] == manifest['source_sha256'] == source_pin
        assert report['actual_public_calls'] == report['public_handlers_added'] == 0
        assert not report['actual_authenticated_host_used'] and not report['actual_source_admission_qualified']
        terminal = RUN / terminal_name
        emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate', 'result': 'PASS',
            'session_id': session, 'initial_chunk_id': initial, 'final_chunk_id': final, 'actual_exit_code': 0,
            counter: cases, 'failures': 0, 'errors': 0, 'source_guarded_exit_completed': True,
            'full_selected_suite_completed': True, 'report_binding': bind(proof),
            'log_binding': bind(package / 'receipts/actual-0001.log'), 'actual_public_calls': 0,
            'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
        new_terminals.append(bind(terminal))
        for r in manifest['files'] + manifest['input_bindings'] + report['files']:
            rows[r['path']] = r
        for path in (source, proof, terminal):
            r = bind(path)
            rows[r['path']] = r
    assert load(BASE / 'package-transfer-v3/source-manifest.json')['retained_predecessor_cases'] == 61
    api_source = BASE / 'api-v52/source-manifest.json'
    snapshot = BASE / 'current-participation-v4/packages/0001/branch.snapshot'
    selected = [r for r in load(api_source)['files'] if r['path'] == snapshot.relative_to(ROOT).as_posix()]
    assert len(selected) == 1 and selected[0] == bind(snapshot) and snapshot.stat().st_size == 23542012
    probe = RUN / 'check-package-source-size-0001.py'
    failure = RUN / 'package-public-source-size-failure-0001.json'
    emit(failure, {'schema_version': 'lab-package-public-source-size-probe/v1-candidate', 'result': 'FAIL',
        'actual_exit_code': 1, 'source_snapshot_binding': bind(snapshot), 'source_snapshot_bytes': 23542012,
        'failure_stage': 'recursive-privacy-scan-of-decoded-original-baseline-before-export',
        'actual_exception': 'ValueError: private credential or Session memory',
        'matched_field_metadata': [
            {'source_file': 'baseline.json', 'location': 'documents/authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/agent-session.json/payload/session_memory',
             'value_type': 'object', 'all_reference_and_question_arrays_empty': False, 'expires_with_session': True},
            {'source_file': 'baseline.json', 'location': 'documents/authority/artifact-types/agent-session/v1/schema.json/properties/payload/properties/session_memory',
             'value_type': 'object', 'classification': 'schema-declaration'},
            {'source_file': 'baseline.json', 'location': 'subjects/agent-session:first-governed-agent-episode:2026-10-06@candidate.1/record/payload/session_memory',
             'value_type': 'object', 'all_reference_and_question_arrays_empty': False, 'expires_with_session': True}],
        'original_data_values_exported_to_receipt': False, 'package_constructed': False,
        'filesystem_publication_started': False, 'source_guarded_exit_completed': False,
        'source_snapshot_privacy_classification_required': True,
        'actual_public_calls': 0, 'actual_authenticated_host_used': False, 'actual_signed_source_replay_qualified': False,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'claim_ceiling': 'Actual failed size-probe attempt preserved. The decoded persisted Session descriptor and schema declaration trigger the strict privacy rule. This is neither proof of live-memory disclosure nor permission to exempt/omit source material. Complete original-byte package export remains unqualified.',
        'files': [bind(probe), bind(snapshot), bind(api_source), bind(BASE / 'package-publication-v1/source-manifest.json')]})
    terminal = RUN / 'package-public-source-size-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate', 'result': 'FAIL',
        'session_id': 18533, 'initial_chunk_id': '14fffe', 'final_chunk_id': '41a980', 'actual_exit_code': 1,
        'report_binding': bind(failure), 'source_guarded_exit_completed': False,
        'actual_public_calls': 0, 'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    new_terminals.append(bind(terminal))
    context = RUN / 'context-R03-package-foundation-0094.json'
    emit(context, {'schema_version': 'lab-bounded-candidate-context/v1-candidate', 'task': 'R03',
        'parent_progress_binding': bind(predecessor), 'authorization_binding': bind(RUN / 'authorization.json'),
        'scope': 'Explicit package-transfer schema/budget successor and managed publication filesystem kernel; actual owned fixtures only.',
        'constraint': 'Preserve original public contracts, predecessors, current source and unrelated dirty work; no admission/live stores/keys/activation/external effect.',
        'verification': 'All78 pure cases retaining61 predecessor methods; all33 managed filesystem cases; actual source size probe retained as FAIL.',
        'nonblocking_implementation_choice': 'Separate 1 MiB controls/proposals from32 MiB per material/40 MiB originals/64 MiB archive; exclusively reserved generations with fsync marker and read-only retry.',
        'remaining_source_obligation': 'Review the actual persisted Agent Session descriptor/schema and runtime RAM boundaries before declaring a safe complete source-package privacy contract. No allowlist, deletion, shortened source or silent scan bypass.',
        'owner_checkpoint': 'Sole final actual R08 after full S02; candidate construction remains authorized.',
        'authority_effect': 'none', 'actual_owner_outcome': None})
    for path in (predecessor, probe, failure, terminal, context, Path(__file__).resolve(), RUN / 'record-package-foundation-progress-0094.py'):
        r = bind(path)
        rows[r['path']] = r
    for r in rows.values():
        assert hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'], r['path']
    value = {**old, 'files': [rows[k] for k in sorted(rows)], 'parent_progress_binding': bind(predecessor),
        'change': 'Explicit package-transfer v3 passed78 pure cases retaining61 predecessor assertions. Separate material/source/archive budgets preserve1 MiB public controls and target plans. Strict malformed structured text/binary refusals and source-guarded archive verification added. Managed publication kernel passed33 actual isolated filesystem fixtures. Full23.5 MB source-size probe actually refused persisted Session descriptor/schema during decoded privacy scan; exit1 preserved, no safe complete source export claimed. Public18 handlers/16 missing unchanged.',
        'package_transfer_source_binding': bind(BASE / 'package-transfer-v3/source-manifest.json'),
        'package_transfer_source_sha256': packages[0][-1],
        'package_transfer_report_binding': bind(BASE / 'package-transfer-v3/receipts/checks-0001.json'),
        'package_transfer_current_pure_cases': 78, 'package_transfer_retained_original_cases': 50,
        'package_transfer_retained_predecessor_cases': 61, 'package_transfer_added_pure_cases': 28,
        'package_transfer_added_public_handlers': 0,
        'package_publication_source_binding': bind(BASE / 'package-publication-v1/source-manifest.json'),
        'package_publication_report_binding': bind(BASE / 'package-publication-v1/receipts/checks-0001.json'),
        'package_publication_complete_filesystem_fixture_cases': 33,
        'package_publication_filesystem_fixtures_qualified': True,
        'package_publication_actual_authenticated_host_qualified': False,
        'package_transfer_actual_authenticated_host_qualified': False,
        'package_transfer_managed_generation_qualified': False,
        'package_full_source_size_probe_verdict': 'FAIL', 'package_full_source_size_probe_report_binding': bind(failure),
        'package_full_source_size_probe_terminal_binding': bind(terminal),
        'package_full_source_original_snapshot_bytes': 23542012,
        'package_full_source_privacy_classification_pending': True,
        'package_transfer_terminal_bindings': old['package_transfer_terminal_bindings'] + new_terminals,
        'remaining_obligations': [
            'Resolve complete source-package privacy classification for actual persisted Agent Session descriptor/schema versus actual ephemeral RAM; preserve the full dependency closure and original snapshots. Actual full-source size probe failed and grants no bypass.',
            'Integrate package.export/import into actual authenticated host policies, original signed source replay, exact schema/model/typed/core validation, strict real clocks/budgets, durable claims and verified managed generation recovery. Pure and filesystem fixture PASS does not qualify public handlers.',
            *old['remaining_obligations']],
        'claim_ceiling': 'Complete frozen package-transfer pure78 and managed filesystem33 fixture suites only; source size probe FAIL retained. No public package handler, authenticated permission, safe full-source export, actual source admission, semantic import, new canonical definition, genuine pilot, whole API, admission or complete plan.',
        'progress_producer_failed_attempt': {'producer_binding': bind(RUN / 'record-package-foundation-progress-0094.py'), 'actual_exit_code': 1, 'final_chunk_id': '896ed5', 'reason': 'Path.relative_to rejected an already bound external sibling source. Original source bytes unchanged; exact own derivatives reused without overwrite.'},
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = BASE / 'api-v52/receipts/R03-0094.json'
    emit(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
        'package_pure_cases': 78, 'filesystem_cases': 33, 'full_source_probe': 'FAIL',
        'handlers': 18, 'missing': 16, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()
