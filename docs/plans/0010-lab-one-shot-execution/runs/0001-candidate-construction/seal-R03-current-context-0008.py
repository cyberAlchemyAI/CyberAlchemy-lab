"""Qualify only the exact successfully built, checked and audited Context."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SELECTED = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v8'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def main():
    output = SELECTED / 'receipts/qualification-0001.json'
    assert not output.exists()
    source = SELECTED / 'source-manifest.json'
    assert bind(source)['sha256'] == 'de6957eb09db5bd052ae494f808f6d02aaeba0641316d62753c13a7d9a0d0bf6'
    terminal_path = RUN / 'current-context-delivery-terminal-0008.json'
    terminal = load(terminal_path)
    assert terminal['selected_exit_codes'] == {'build': 0, 'checks': 0}
    for phase in ['build', 'checks']:
        row = terminal[phase]
        assert row['terminal_observed'] and row['exit_code'] == 0
        assert isinstance(row['tool_session_id'], int) and row['chunk_id']
        assert row['source_binding'] == bind(source)
        assert bind(ROOT / row['log_binding']['path']) == row['log_binding']
    audit_terminal_path = RUN / 'current-context-delivery-audit-terminal-0008.json'
    audit_terminal = load(audit_terminal_path)
    assert audit_terminal['terminal_observed'] and audit_terminal['exit_code'] == 0
    assert isinstance(audit_terminal['tool_session_id'], int) and audit_terminal['chunk_id']
    assert audit_terminal['source_binding'] == bind(source)
    tests = load(SELECTED / 'receipts/checks.json')
    assert tests['result'] == 'PASS' and tests['tests_run'] == tests['expected_tests'] == 50
    assert len(tests['cases']) == 50 and all(row['result'] == 'PASS' for row in tests['cases'])
    audit_path = SELECTED / 'receipts/independent-audit.json'
    audit = load(audit_path)
    assert audit['result'] == 'PASS' and audit['selected_methods'] == 50
    assert audit['actual_generated_carriers'] == 30 and audit['raw_source_bodies'] == 23 and audit['exact_native_joins'] == 25
    assert audit['runtime_repository_code_execution_verified'] and audit['execution_dependency_selection_independently_verified']
    proof_path = SELECTED / 'receipts/audit-proof-0001.json'
    proof = load(proof_path)
    assert proof['result'] == 'PASS' and proof['independent_audit_binding'] == bind(audit_path)
    rows = {row['path']: row for row in proof['files']}
    parent_path = SELECTED.parent / 'current-context-delivery-v6/receipts/qualification-0001.json'
    parent = load(parent_path)
    for row in parent['files']:
        assert rows.get(row['path']) == row
    selected_source = load(source)
    assert selected_source['original49assertion_ASTs_preserved']
    assert selected_source['original50assertions_preserved_except_declared_reader_path']
    assert not selected_source['original50assertion_ASTs_preserved']
    for path in [proof_path, terminal_path, audit_terminal_path, audit_path,
                 RUN / 'observe-context-terminal-0008.py', Path(__file__)]:
        row = bind(path)
        assert rows.get(row['path'], row) == row
        rows[row['path']] = row
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    value = {'schema_version': 'lab-context-qualified-component/v1-candidate',
             'result': 'PASS', 'files': sorted(rows.values(), key=lambda row: row['path']),
             'recorded_at': datetime.now(timezone.utc).isoformat(),
             'source_binding': bind(source), 'package_binding': bind(SELECTED / 'packages/0001/manifest.json'),
             'independent_audit_binding': bind(audit_path), 'parent_qualification_binding': bind(parent_path),
             'reader_path_revision_binding': selected_source['reader_path_revision_binding'],
             'selected_methods': 50, 'unchanged_parent_test_methods': 49, 'exact_reader_assertion_rebound': 1,
             'actual_build_exit_code': 0, 'actual_check_exit_code': 0, 'actual_audit_exit_code': 0,
             'audit_checks': audit['checks'], 'actual_generated_carriers': 30,
             'current_Context_successor_qualified': True, 'current_API_qualified': False,
             'current_Agent_qualified': False, 'repository_admissions_applied': 0,
             'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False,
             'remaining_obligations': proof['remaining_obligations'],
             'claim_ceiling': 'Exact Context component qualification. API, Machine transport, remaining21 operations and complete S02/R08 remain.'}
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'qualification_binding': bind(output), 'files': len(rows), 'checks': audit['checks']}), flush=True)


if __name__ == '__main__':
    main()
