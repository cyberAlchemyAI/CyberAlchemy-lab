"""Seal actual terminal and complete byte-custody proof, without running checks."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
HERE = ROOT / 'product/lab/release-candidates/v1/interface/byte-custody-v1'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    source = HERE / 'source-manifest.json'
    assert bind(source)['sha256'] == '219e2cd6ed6d723bac8d23df87467ea93a1761f115c25e7529bb446fee736cdd'
    manifest = json.loads(source.read_bytes())
    rows = {row['path']: row for row in manifest['files']}
    assert len(rows) == 11173
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    report_path = HERE / 'receipts/checks-0001.json'
    report = json.loads(report_path.read_bytes())
    assert report['result'] == 'PASS' and report['tests_run'] == report['expected_tests'] == 17
    assert len(report['cases']) == 17 and all(row['result'] == 'PASS' for row in report['cases'])
    assert report['source_sha256'] == bind(source)['sha256']
    measurement = report['actual_full_closure_measurement']
    assert measurement['result'] == 'PASS'
    assert [row['implementation'] for row in measurement['measurements']] == ['original', 'descriptor', 'descriptor', 'original']
    for row in measurement['measurements']:
        assert row['actual_files'] == 11165 and row['actual_bytes'] == 1187416595
        assert row['all_original_file_hashes_matched']
    log = RUN / 'descriptor-byte-custody-checks-0001.log'
    assert re.search(r'Ran 17 tests in [0-9.]+s\n\nOK', log.read_text())
    terminal = RUN / 'descriptor-byte-custody-terminal-0001.json'
    output = HERE / 'receipts/proof-0001.json'
    assert not terminal.exists() and not output.exists()
    put(terminal, {'schema_version': 'lab-actual-terminal-observation/v1-candidate',
                   'checked_at': datetime.now(timezone.utc).isoformat(),
                   'tool_session_id': 2457, 'exit_code': 0, 'chunk_id': 'e26100',
                   'terminal_observed': True, 'source_binding': bind(source),
                   'report_binding': bind(report_path), 'log_binding': bind(log),
                   'authority_effect': 'none', 'actual_owner_outcome': None})
    for path in [source, report_path, log, terminal, Path(__file__)]:
        rows[bind(path)['path']] = bind(path)
    put(output, {'schema_version': 'lab-descriptor-byte-custody-proof/v1-candidate',
                 'result': 'PASS', 'actual_cases': 17, 'actual_terminal_exit_code': 0,
                 'source_binding': bind(source), 'actual_terminal_binding': bind(terminal),
                 'report_binding': bind(report_path), 'log_binding': bind(log),
                 'files': [rows[key] for key in sorted(rows)],
                 'actual_full_closure_measurement': measurement,
                 'Context_or_API_or_Agent_qualified': False,
                 'task_complete': False, 'goal_complete': False,
                 'authority_effect': 'none', 'actual_owner_outcome': None,
                 'claim_ceiling': 'Actual17 filesystem cases and complete11165 dependency-byte ABBA comparison. Modest component gain only; 2419 directory descriptors per pass. No whole Context/API/Agent qualification or deadline fix.'})
    print(json.dumps({'result': 'PASS', 'proof_binding': bind(output), 'files': len(rows),
                      'component_ratio': measurement['component_speed_ratio']}), flush=True)


if __name__ == '__main__':
    main()
