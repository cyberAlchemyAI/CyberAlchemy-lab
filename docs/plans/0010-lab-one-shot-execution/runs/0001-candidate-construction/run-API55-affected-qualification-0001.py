"""Run affected qualification after the completed original expiry scope."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
SOURCE = 'ded6259462a19cfa8da1c5e6bdb7da0e1c04ff98f137c8a3250add64a41d0674'
PROFILE = 'aa2e047859010af460674b33f124aca5f05b8709ea521bbcd394cead7e7eded8'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    expiry = json.loads((BASE / 'api55-session-checks-v1/receipts/checks-0001.json').read_bytes())
    terminal = json.loads((RUN / 'API55-expiry2-terminal-0001.json').read_bytes())
    assert expiry['result'] == 'PASS' and expiry['actual_cases'] == 2
    assert expiry['source_guarded_exit_completed'] and expiry['owned_fixture_cleanup_completed']
    assert terminal['actual_exit_code'] == 0
    for row in expiry['files']:
        assert bind(ROOT / row['path'])['sha256'] == row['sha256']
    own = bind(Path(__file__).resolve())
    stages = [
        ('session-affected7', RUN / 'check-API55-session-affected-0001.py', [],
         RUN / 'API55-session-affected7-report-0001.json', 7),
        ('package3', BASE / 'api55-package-checks-v1/checks.py',
         ['--source-sha256', SOURCE, '--profile-sha256', PROFILE],
         BASE / 'api55-package-checks-v1/receipts/checks-0001.json', 3)]
    outcomes = []
    for label, script, arguments, report_path, expected in stages:
        assert not report_path.exists(), 'preserve any completed or failed predecessor'
        command = [sys.executable, '-B', str(script), *arguments]
        started = datetime.now(timezone.utc).isoformat()
        print(json.dumps({'phase': 'STARTING', 'suite': label, 'expected_cases': expected, 'started_at': started}), flush=True)
        log = RUN / ('API55-' + label + '-child-0001.log')
        with log.open('xb') as stream:
            completed = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
        result = {'schema_version': 'lab-child-process-terminal/v1-candidate', 'suite': label,
            'command': command, 'actual_exit_code': completed.returncode, 'log_binding': bind(log),
            'started_at': started, 'completed_at': datetime.now(timezone.utc).isoformat(),
            'driver_binding': own, 'expected_cases': expected, 'full_selected_suite_completed': False,
            'result': 'PASS' if completed.returncode == 0 else 'FAIL',
            'whole_API_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None,
            'task_complete': False, 'goal_complete': False}
        if report_path.exists():
            report = json.loads(report_path.read_bytes())
            result.update(report_binding=bind(report_path), actual_cases=report['actual_cases'],
                errors=report['errors'], failures=report['failures'],
                source_guarded_exit_completed=report['source_guarded_exit_completed'],
                owned_fixture_cleanup_completed=report['owned_fixture_cleanup_completed'],
                full_selected_suite_completed=report['actual_cases'] == expected)
        output = RUN / ('API55-' + label + '-child-terminal-0001.json')
        with output.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
        outcomes.append(bind(output))
        assert bind(Path(__file__).resolve()) == own, 'driver changed during execution'
        print(json.dumps({'phase': 'TERMINAL', 'suite': label, 'actual_exit_code': completed.returncode,
                          'actual_cases': result.get('actual_cases'), 'terminal': bind(output)}), flush=True)
        assert completed.returncode == 0 and result['full_selected_suite_completed'], 'inspect failed/incomplete stage before next fixture'
        assert result['source_guarded_exit_completed'] and result['owned_fixture_cleanup_completed']
    print(json.dumps({'result': 'PASS', 'actual_selected_cases': 10, 'suite_terminal_bindings': outcomes,
                      'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}), flush=True)


if __name__ == '__main__':
    main()
