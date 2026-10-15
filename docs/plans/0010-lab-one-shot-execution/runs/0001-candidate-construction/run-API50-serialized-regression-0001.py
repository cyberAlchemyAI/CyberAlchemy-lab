"""Queue all selected current suites behind the exact live API49 driver."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v50'
SOURCE = '3e46a5bef724a601d3f465841205f8c73a7723637538fd738cdd2ef7a85dcd64'
PROFILE = '6cb5e2461cdc6442384821c4e01df3c117b61166856e3e69731b051ae01b65d5'
STRICT = '9153f572c73c461a132903617637033755088022972b9c1c5c4fd910c6b38983'
TYPED = 'de845541ec86da941c69ad4ed6b8cc0cb12c5cf1a74f5226f5858ea57c3ef3a7'
PREVIOUS_PID = 9233
PREVIOUS_START = '311172'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def await_predecessor():
    terminal = RUN / 'API49-typed10-terminal-0001.json'
    print(json.dumps({'phase': 'WAITING-ON-SAME-API49-DRIVER', 'PID': PREVIOUS_PID,
                      'start_ticks': PREVIOUS_START, 'no_new_fixture_effects': True}), flush=True)
    while not terminal.exists():
        stat = Path('/proc') / str(PREVIOUS_PID) / 'stat'
        assert stat.exists(), 'predecessor disappeared without terminal; inspect before any new fixture'
        assert stat.read_text().rsplit(')', 1)[1].split()[19] == PREVIOUS_START, 'predecessor PID was reused'
        argv = (stat.parent / 'cmdline').read_bytes().split(b'\0')
        assert any(arg.endswith(b'/run-API49-recovery-qualification-0001.py') for arg in argv), 'predecessor identity differs'
        time.sleep(3)
    # Terminal publication may occur just before the parent's final print/exit.
    # Wait for that same parent too; a completed report alone is no overlap permit.
    while (Path('/proc') / str(PREVIOUS_PID) / 'stat').exists():
        stat = Path('/proc') / str(PREVIOUS_PID) / 'stat'
        parts = stat.read_text().rsplit(')', 1)[1].split()
        assert parts[19] == PREVIOUS_START, 'predecessor PID was reused'
        if parts[0] == 'Z':
            break
        time.sleep(3)
    previous = json.loads(terminal.read_bytes())
    assert previous['actual_exit_code'] in (0, 1) and previous['full_selected_suite_completed']
    assert previous['actual_cases'] == 10 and previous['errors'] == 0
    assert previous['original_reader_guarded_exit_completed']
    for key in ['report_binding', 'log_binding', 'check_source_binding']:
        row = previous[key]
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    return terminal


def main():
    previous = await_predecessor()
    for path, expected in [(API / 'source-manifest.json', SOURCE), (API / 'contract-profile.json', PROFILE),
        (BASE / 'api50-current-checks-v1/source-manifest.json', STRICT),
        (BASE / 'api50-typed-checks-v1/source-manifest.json', TYPED)]:
        assert bind(path)['sha256'] == expected
    source_args = ['--source-sha256', SOURCE, '--profile-sha256', PROFILE]
    strict = BASE / 'api50-current-checks-v1'
    typed = BASE / 'api50-typed-checks-v1'
    stages = [
        ('typed10', typed / 'checks.py', ['--check-source-sha256', TYPED], typed / 'receipts/checks-0001.json', 10),
        ('failure18', API / 'checks_failure.py', source_args, API / 'receipts/failure-checks.json', 18),
        ('controls11', strict / 'checks.py', ['--check-source-sha256', STRICT, '--suite', 'controls'], strict / 'receipts/controls-0001.json', 11),
        ('full146', strict / 'checks.py', ['--check-source-sha256', STRICT, '--suite', 'full'], strict / 'receipts/full-0001.json', 146),
        ('classification16', API / 'checks_classification.py', source_args, API / 'receipts/classification-checks.json', 16),
        ('review11', API / 'checks_review.py', source_args, API / 'receipts/review-checks.json', 11),
        ('exports134', API / 'checks_file_exports.py', source_args, API / 'receipts/file-export-checks.json', 134),
        ('metadata86', API / 'checks_metadata_scope.py', source_args, API / 'receipts/metadata-scope-checks.json', 86),
        ('machine14', API / 'checks_machine_transport.py', source_args, API / 'receipts/machine-transport-checks.json', 14),
        ('termination6', API / 'checks_termination_boundaries.py', source_args, API / 'receipts/termination-boundary-checks.json', 6),
    ]
    assert sum(stage[4] for stage in stages) == 452
    outcomes = []
    for label, script, arguments, report_path, expected in stages:
        assert not report_path.exists(), 'preserve any existing suite result'
        command = [sys.executable, '-B', str(script), *arguments]
        started = datetime.now(timezone.utc).isoformat()
        print(json.dumps({'phase': 'STARTING-CURRENT-SUITE', 'suite': label, 'expected_cases': expected,
                          'started_at': started, 'fresh_owned_fixtures': True}), flush=True)
        log = RUN / ('API50-' + label + '-0001.log')
        with log.open('xb') as stream:
            completed = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
        terminal = {'schema_version': 'lab-child-process-terminal/v1-candidate', 'suite': label,
            'command': command, 'actual_exit_code': completed.returncode, 'log_binding': bind(log),
            'started_at': started, 'completed_at': datetime.now(timezone.utc).isoformat(),
            'result': 'PASS' if completed.returncode == 0 else 'FAIL', 'expected_cases': expected,
            'full_selected_suite_completed': False, 'whole_API_qualified': False,
            'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False}
        if report_path.exists():
            report = json.loads(report_path.read_bytes())
            actual = report.get('actual_cases', report.get('tests_run'))
            cases = report['cases']
            errors = sum(row['result'] == 'ERROR' for row in cases)
            failures = sum(row['result'] == 'FAIL' for row in cases)
            terminal.update(report_binding=bind(report_path), actual_cases=actual,
                errors=errors, failures=failures,
                full_selected_suite_completed=actual == expected and len(cases) == expected)
        path = RUN / ('API50-' + label + '-terminal-0001.json')
        put(path, terminal)
        outcomes.append(bind(path))
        print(json.dumps({'phase': 'CURRENT-SUITE-TERMINAL', 'suite': label,
            'actual_exit_code': completed.returncode, 'actual_cases': terminal.get('actual_cases')}), flush=True)
        assert terminal['full_selected_suite_completed'], 'inspect incomplete suite before advancing'
        assert completed.returncode in (0, 1) and terminal['errors'] == 0, 'inspect unexpected error before advancing'
    success = all(json.loads((ROOT / row['path']).read_bytes())['actual_exit_code'] == 0 for row in outcomes)
    result = {'schema_version': 'lab-serialized-public-regression/v1-candidate',
        'result': 'PASS' if success else 'FAIL', 'predecessor_terminal_binding': bind(previous),
        'suite_terminal_bindings': outcomes, 'actual_selected_cases': 452,
        'cases_include_runner_overlap': True, 'source_binding': bind(API / 'source-manifest.json'),
        'profile_binding': bind(API / 'contract-profile.json'), 'remaining_unimplemented_operations': 17,
        'whole_API_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None,
        'task_complete': False, 'goal_complete': False}
    put(RUN / 'API50-serialized-regression-terminal-0001.json', result)
    print(json.dumps(result), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())
