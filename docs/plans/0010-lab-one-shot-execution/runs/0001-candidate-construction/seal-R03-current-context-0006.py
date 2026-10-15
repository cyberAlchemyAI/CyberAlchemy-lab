"""Qualify Context5 only after complete actual checks and independent audit."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
CONTEXT = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v5'

def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def load(path):
    return json.loads(path.read_bytes())

def main():
    output = CONTEXT / 'receipts/qualification-0001.json'
    assert not output.exists()
    terminal_path = RUN / 'current-context-delivery-terminal-0005.json'
    terminal = load(terminal_path)
    assert terminal['selected_exit_codes'] == {'build': 0, 'checks': 0}
    for phase in ['build', 'checks']:
        row = terminal[phase]
        assert row['terminal_observed'] is True and row['exit_code'] == 0
        assert isinstance(row['tool_session_id'], int) and row['chunk_id']
        assert bind(ROOT / row['log_binding']['path']) == row['log_binding']
        assert row['source_binding'] == bind(CONTEXT / 'source-manifest.json')
    audit_terminal_path = RUN / 'current-context-delivery-audit-terminal-0005.json'
    audit_terminal = load(audit_terminal_path)
    assert audit_terminal['terminal_observed'] is True and audit_terminal['exit_code'] == 0
    assert isinstance(audit_terminal['tool_session_id'], int) and audit_terminal['chunk_id']
    assert bind(ROOT / audit_terminal['log_binding']['path']) == audit_terminal['log_binding']
    tests_path = CONTEXT / 'receipts/checks.json'
    tests = load(tests_path)
    assert tests['result'] == 'PASS' and tests['tests_run'] == tests['expected_tests'] == 50
    assert len(tests['cases']) == len({case['test'] for case in tests['cases']}) == 50
    assert all(case['result'] == 'PASS' for case in tests['cases'])
    audit_path = CONTEXT / 'receipts/independent-audit.json'
    audit = load(audit_path)
    assert audit['result'] == 'PASS' and audit['selected_methods'] == 50
    assert audit['actual_generated_carriers'] == 30 and audit['raw_source_bodies'] == 23
    assert audit['exact_native_joins'] == 25 and audit['historical_nonce_signature_independently_verified']
    proof_path = CONTEXT / 'receipts/audit-proof-0001.json'
    proof = load(proof_path)
    assert proof['result'] == 'PASS' and proof['selected_methods'] == 50
    assert proof['independent_audit_binding'] == bind(audit_path)
    rows = {row['path']: row for row in proof['files']}
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    for path in [proof_path, terminal_path, audit_terminal_path, tests_path, audit_path,
                 RUN / 'observe-context-terminal-0005.py', RUN / 'current-context-sealing-failure-0001.json', RUN / 'seal-R03-current-context-0005.py', Path(__file__)]:
        row = bind(path)
        assert rows.get(row['path'], row) == row
        rows[row['path']] = row
    value = {'schema_version': 'lab-original-context-qualified-proof/v1-candidate',
             'result': 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(),
             'selected_methods': 50, 'actual_check_exit_code': 0, 'actual_audit_exit_code': 0,
             'actual_build_exit_code': 0, 'files': [rows[key] for key in sorted(rows)],
             'source_binding': bind(CONTEXT / 'source-manifest.json'),
             'package_binding': bind(CONTEXT / 'packages/0001/manifest.json'),
             'build_and_checks_terminal_binding': bind(terminal_path),
             'audit_terminal_binding': bind(audit_terminal_path),
             'independent_audit_binding': bind(audit_path), 'actual_generated_carriers': 30,
             'exact_native_joins': 25, 'raw_source_bodies': 23,
             'current_Agent_qualified': False, 'public_operations_added': 0,
             'task_complete': False, 'goal_complete': False,
             'authority_effect': 'none', 'actual_owner_outcome': None,
             'claim_ceiling': 'Exact Context producer qualification only. API31, actual Agent lifecycle, remaining 21 APIs and the full plan remain required.'}
    with output.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'qualified_Context': bind(output), 'files': len(rows)}))

if __name__ == '__main__':
    main()
