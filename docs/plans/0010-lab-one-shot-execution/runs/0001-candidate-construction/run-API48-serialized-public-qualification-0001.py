"""Run current public successor suites serially, preserving every actual verdict.

The terminated API47 job is retained as interrupted, never as a full verdict.
This run selects fresh API48 fixtures and does not reuse or alter its old keys,
workspaces or incomplete operation claims.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v48'
SOURCE = 'a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6'
PROFILE = '080eaba1d670b1f660073a0554a601b3ee4eabd3be60d47dbe427df4ea4229f9'
TYPED = '6b1198c03909390be68f35b6cbbdc39a73084ff31f6b0ca9e448ffe28adcd03c'
STRICT = 'af95798f9bc136c479414c3bb10a38951fc941aae6311df08ba17e657227c7c5'


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    original_terminal = RUN / 'API47-failure18-interrupted-terminal-0001.json'
    previous = json.loads(original_terminal.read_bytes())
    assert previous['actual_exit_code'] == 143 and not previous['full_suite_verdict_established']
    assert not Path('/proc/355024').exists(), 'same old API47 driver is still live; do not overlap it'
    steps = [
        ('typed8', BASE / 'api48-typed-checks-v1/checks.py',
         ['--check-source-sha256', TYPED], BASE / 'api48-typed-checks-v1/receipts/checks-0001.json', 8),
        ('controls11', BASE / 'api48-current-checks-v1/checks.py',
         ['--check-source-sha256', STRICT, '--suite', 'controls'], BASE / 'api48-current-checks-v1/receipts/controls-0001.json', 11),
        ('failure18', API / 'checks_failure.py',
         ['--source-sha256', SOURCE, '--profile-sha256', PROFILE], API / 'receipts/failure-checks.json', 18),
        ('full146', BASE / 'api48-current-checks-v1/checks.py',
         ['--check-source-sha256', STRICT, '--suite', 'full'], BASE / 'api48-current-checks-v1/receipts/full-0001.json', 146),
    ]
    verdicts = []
    for label, script, arguments, report_path, expected in steps:
        assert not report_path.exists(), 'existing result must not be overwritten'
        print(json.dumps({'phase': 'STARTING-CURRENT-SUITE', 'suite': label,
            'new_owned_fixtures': True, 'prior_interruption_preserved': True}), flush=True)
        command = [sys.executable, '-B', str(script), *arguments]
        log = RUN / ('API48-' + label + '-0001.log')
        with log.open('xb') as stream:
            result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
        terminal = {'schema_version': 'lab-child-process-terminal/v1-candidate', 'suite': label,
            'actual_exit_code': result.returncode, 'command': command, 'log_binding': binding(log),
            'result': 'PASS' if result.returncode == 0 else 'FAIL', 'task_complete': False, 'authority_effect': 'none'}
        if report_path.exists():
            report = json.loads(report_path.read_bytes())
            actual = report.get('actual_cases', report.get('tests_run', report.get('actual_tests')))
            terminal['report_binding'] = binding(report_path)
            terminal['actual_cases'] = actual
            terminal['full_selected_suite_completed'] = actual == expected
        emit(RUN / ('API48-' + label + '-terminal-0001.json'), terminal)
        verdicts.append(terminal)
        print(json.dumps({'phase': 'CURRENT-SUITE-TERMINAL', 'suite': label,
            'actual_exit_code': result.returncode, 'actual_cases': terminal.get('actual_cases')}), flush=True)
        assert report_path.exists() and terminal['full_selected_suite_completed'], 'inspect incomplete successor before advancing'
        assert result.returncode in (0, 1) and report.get('errors', 0) == 0, 'inspect anomalous successor or source/cleanup error before advancing'
    success = all(row['actual_exit_code'] == 0 for row in verdicts)
    emit(RUN / 'API48-serialized-public-qualification-terminal-0001.json', {
        'schema_version': 'lab-serialized-public-qualification-terminal/v1-candidate',
        'result': 'PASS' if success else 'FAIL', 'suite_terminals': verdicts,
        'current_API_source_binding': binding(API / 'source-manifest.json'),
        'old_interruption_binding': binding(original_terminal), 'whole_API_qualified': False,
        'all_other_original_suites_outstanding': True, 'task_complete': False, 'authority_effect': 'none'})
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
