"""Preserve the actual full six-case terminal without qualifying the whole API."""
import argparse
import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import re

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v34'


def bind(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--observed-session', type=int, required=True)
    parser.add_argument('--observed-exit', type=int, required=True)
    parser.add_argument('--observed-chunk', required=True)
    args = parser.parse_args()
    assert args.observed_exit == 0
    source = API / 'source-manifest.json'
    assert bind(source)['sha256'] == '4b411975d34babbd275cc60856b259091b360aed4df737226867a563c1a2ac2c'
    report_path = API / 'receipts/termination-boundary-checks-0002.json'
    report = json.loads(report_path.read_bytes())
    assert report['result'] == 'PASS' and report['tests_run'] == report['expected_tests'] == 6
    assert len(report['cases']) == 6 and all(row['result'] == 'PASS' for row in report['cases'])
    assert report['source_sha256'] == bind(source)['sha256']
    log = RUN / 'session-termination-boundary-checks-0002.log'
    text = log.read_text()
    actual = re.findall(r'^(test_\S+) \([^\n]+\) \.\.\. ok$', text, re.M)
    methods = {node.name for node in ast.walk(ast.parse((API / 'test_termination_boundaries.py').read_bytes()))
               if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}
    assert len(actual) == len(set(actual)) == 6 and set(actual) == methods
    assert re.search(r'Ran 6 tests in [0-9.]+s\n\nOK\n', text)
    value = {'schema_version': 'lab-actual-terminal-observation/v1-candidate',
             'checked_at': datetime.now(timezone.utc).isoformat(),
             'session_id': args.observed_session, 'exit_code': args.observed_exit,
             'chunk_id': args.observed_chunk, 'terminal_observed': True,
             'actual_cases': 6, 'source_binding': bind(source),
             'profile_binding': bind(API / 'contract-profile.json'),
             'runner_source_binding': bind(RUN / 'API34-termination-full6-source-0002.json'),
             'report_binding': bind(report_path), 'log_binding': bind(log),
             'prior_interruption_binding': bind(RUN / 'session-termination-boundary-interruption-0001.json'),
             'sealer_binding': bind(Path(__file__)),
             'whole_API_qualified': False, 'current_Agent_qualified': False,
             'task_complete': False, 'actual_owner_outcome': None, 'authority_effect': 'none',
             'claim_ceiling': 'All six original termination cases and actual successful terminal only. Full API regression and actual Agent lifecycle remain required.'}
    output = RUN / 'session-termination-boundary-terminal-0002.json'
    with output.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'actual_cases': 6, 'terminal_binding': bind(output)}))


if __name__ == '__main__':
    main()
