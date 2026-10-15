"""Qualify exact fresh Context only from actual build, full50 and audit exits."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SELECTED = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v9'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def main():
    source = SELECTED / 'source-manifest.json'
    assert bind(source)['sha256'] == '85f81392b9ae2e4c34d96c0f6696b3b0a34397717f4b11706fa062eba8a20cb3'
    phases_path = RUN / 'current-context-delivery-terminal-0009.json'
    phases = load(phases_path)
    assert phases['selected_exit_codes'] == {'build': 0, 'checks': 0}
    audit_terminal_path = RUN / 'current-context-delivery-audit-terminal-0009.json'
    audit_terminal = load(audit_terminal_path)
    assert audit_terminal['actual_exit_code'] == audit_terminal['freeze_actual_exit_code'] == 0
    checks_path = SELECTED / 'receipts/checks.json'
    checks = load(checks_path)
    assert checks['result'] == 'PASS' and checks['tests_run'] == checks['expected_tests'] == 50
    assert len(checks['cases']) == 50 and all(row['result'] == 'PASS' for row in checks['cases'])
    assert checks['source_sha256'] == bind(source)['sha256']
    assert checks['package_sha256'] == bind(SELECTED / 'packages/0001/manifest.json')['sha256']
    audit_path = SELECTED / 'receipts/independent-audit.json'
    audit = load(audit_path)
    assert audit_terminal['report_binding'] == bind(audit_path)
    assert audit['result'] == 'PASS' and audit['selected_methods'] == 50
    assert audit['actual_generated_carriers'] == 30 and audit['raw_source_bodies'] == 23 and audit['exact_native_joins'] == 25
    assert audit['runtime_repository_code_execution_verified'] and audit['execution_dependency_selection_independently_verified']
    proof_path = SELECTED / 'receipts/audit-proof-0001.json'
    proof = load(proof_path)
    assert proof['result'] == 'PASS' and proof['independent_audit_binding'] == bind(audit_path)
    rows = {row['path']: row for row in proof['files']}
    parent = SELECTED.parent / 'current-context-delivery-v8/receipts/qualification-0001.json'
    for row in load(parent)['files']:
        assert rows.get(row['path']) == row
    paths = [proof_path, phases_path, audit_terminal_path, audit_path, checks_path, parent,
             RUN / 'run-current-context-0009.py', RUN / 'run-current-context-audit-0009.py', Path(__file__).resolve()]
    for phase in ['build', 'checks']:
        row = phases[phase]
        assert row['terminal_observed'] and row['exit_code'] == 0 and row['source_binding'] == bind(source)
        paths.append(ROOT / row['log_binding']['path'])
        assert bind(paths[-1]) == row['log_binding']
    for key in ['log_binding', 'freeze_log_binding', 'producer_binding']:
        path = ROOT / audit_terminal[key]['path']
        assert bind(path) == audit_terminal[key]
        paths.append(path)
    for path in paths:
        row = bind(path)
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    value = {'schema_version': 'lab-context-qualified-component/v1-candidate',
             'result': 'PASS', 'files': [rows[key] for key in sorted(rows)],
             'source_binding': bind(source), 'package_binding': bind(SELECTED / 'packages/0001/manifest.json'),
             'independent_audit_binding': bind(audit_path), 'parent_qualification_binding': bind(parent),
             'reader_path_revision_binding': load(source)['reader_path_revision_binding'],
             'selected_methods': 50, 'unchanged_parent_test_methods': 49, 'exact_reader_assertion_rebound': 1,
             'actual_build_exit_code': 0, 'actual_check_exit_code': 0, 'actual_audit_exit_code': 0,
             'audit_checks': audit['checks'], 'actual_generated_carriers': 30,
             'current_Context_successor_qualified': True, 'current_API_qualified': False,
             'current_Agent_qualified': False, 'repository_admissions_applied': 0,
             'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
             'remaining_obligations': ['Qualify original API Machine and lifecycle behavior using exact fresh source and Context bindings.',
                                       'Implement all13 missing handlers and full46-task package before S02/R08; preserve A01-A04 effect scope.'],
             'claim_ceiling': 'Exact Context component qualification. Complete API, current Agent, final package, owner decision and application remain.'}
    output = SELECTED / 'receipts/qualification-0001.json'
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'qualification_binding': bind(output), 'files': len(rows), 'audit_checks': audit['checks']}), flush=True)


if __name__ == '__main__':
    main()
