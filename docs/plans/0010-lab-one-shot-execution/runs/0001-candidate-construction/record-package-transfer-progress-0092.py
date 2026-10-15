"""Bind complete package calculation evidence without adding unimplemented handlers."""
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
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    predecessor = BASE / 'api-v52/receipts/R03-0091.json'
    old = load(predecessor)
    assert old['implemented_public_handlers'] == 18 and old['unimplemented_public_operation_count'] == 16
    assert old['source_binding'] == bind(BASE / 'api-v52/source-manifest.json')
    rows = {row['path']: row for row in old['files']}
    terminals = []
    for version, cases, session, initial, final, source_pin in [
        (1, 50, 79812, '3e6fd5', 'abdca8', 'ffe7d93e85d8567c8a476a3eb492fa085544fbe95ca27a86015bcc70075344c6'),
        (2, 61, 78747, 'df28d6', '2dc330', '777161eaae374a9f09a20c1744821f3e21304640d9a1da4722db856619986065')]:
        package = BASE / ('package-transfer-v' + str(version))
        source = package / 'source-manifest.json'
        proof = package / 'receipts/checks-0001.json'
        checked = load(proof)
        assert checked['result'] == 'PASS' and checked['pure_cases'] == cases
        assert checked['failures'] == checked['errors'] == 0 and checked['source_sha256'] == source_pin
        assert checked['full_selected_suite_completed'] and checked['source_guarded_exit_completed']
        assert checked['actual_public_calls'] == 0 and not checked['actual_authenticated_host_used']
        assert checked['public_handlers_added'] == 0 and not checked['actual_source_admission_qualified']
        if version == 2:
            assert load(source)['retained_original_cases'] == 50
        terminal = RUN / ('package-transfer-pure-terminal-000' + str(version) + '.json')
        emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate', 'session_id': session,
            'initial_chunk_id': initial, 'final_chunk_id': final, 'actual_exit_code': 0, 'result': 'PASS',
            'pure_cases': cases, 'failures': 0, 'errors': 0, 'full_selected_suite_completed': True,
            'source_guarded_exit_completed': True, 'report_binding': bind(proof),
            'log_binding': bind(package / 'receipts/actual-0001.log'), 'authority_effect': 'none',
            'actual_public_calls': 0, 'task_complete': False, 'goal_complete': False})
        terminals.append(bind(terminal))
        manifest = load(source)
        for row in manifest['files'] + manifest['input_bindings'] + checked['files']:
            rows[row['path']] = row
        for path in (source, proof, terminal):
            row = bind(path)
            rows[row['path']] = row
    for path in (predecessor, Path(__file__).resolve()):
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    value = {**old, 'files': [rows[key] for key in sorted(rows)],
        'parent_progress_binding': bind(predecessor),
        'change': 'Constructed/froze package transfer calculation v1 and explicit v2 archive/privacy successor. Original50 pure cases PASS; successor61 including all50 unchanged assertions PASS. Exact raw original bytes, complete bounded/cyclic dependency closure, complete source import accounting, separate source provenance, encoding/privacy closure and whole-plan output bound implemented. Public export/import integration and full semantic validation remain pending;18 handlers/16 missing unchanged. Same API52/API50 runners continue.',
        'package_transfer_source_binding': bind(BASE / 'package-transfer-v2/source-manifest.json'),
        'package_transfer_source_sha256': '777161eaae374a9f09a20c1744821f3e21304640d9a1da4722db856619986065',
        'package_transfer_report_binding': bind(BASE / 'package-transfer-v2/receipts/checks-0001.json'),
        'package_transfer_terminal_bindings': terminals,
        'package_transfer_current_pure_cases': 61, 'package_transfer_retained_original_cases': 50,
        'package_transfer_added_pure_cases': 11, 'package_transfer_added_public_handlers': 0,
        'package_transfer_actual_authenticated_host_qualified': False,
        'package_transfer_source_admission_qualified': False, 'package_transfer_target_model_qualified': False,
        'package_transfer_managed_generation_qualified': False,
        'package_transfer_host_integration_pending': True,
        'remaining_obligations': [
            'Integrate package.export/import through independently authenticated host policies, actual signed source/provenance replay, complete original carrier/model/typed validation, strict budgets and clocks, durable claims, managed generation and read-only recovery; complete actual public cases before counting these handlers.',
            *old['remaining_obligations']],
        'claim_ceiling': 'Frozen package transfer calculation with61 complete synthetic pure cases, preserving50 original assertions and their separate complete proof. No new public handler, actual source admission verification, semantic target model validation, managed publication, user pilot, admission, complete API or plan.',
        'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    path = BASE / 'api-v52/receipts/R03-0092.json'
    emit(path, value)
    print(json.dumps({'result': 'PASS', 'progress_binding': bind(path), 'bound_files': len(rows),
        'package_pure_cases': 61, 'handlers': 18, 'missing': 16, 'task_complete': False}), flush=True)


if __name__ == '__main__':
    main()
