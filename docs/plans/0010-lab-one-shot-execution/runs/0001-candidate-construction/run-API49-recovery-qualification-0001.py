"""Start fresh isolated qualification after an unavailable interrupted driver.

No old claim, key, workspace, frozen source, deadline or test assertion is changed.
The prior selected suites remain outstanding until their own complete evidence.
"""
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
CHECKS = BASE / 'api49-typed-checks-v1'
CHECK_SHA = 'ef633bb1ad40b3bdd913980392d4ead510f7d9b44c173658622e2012de065ccf'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    observation = RUN / 'API48-unavailable-driver-observation-0001.json'
    prior = json.loads(observation.read_bytes())
    assert prior['actual_exit_code'] is None and not prior['full_suite_verdict_established']
    assert prior['prior_PID_absent'] and not Path('/proc/365370').exists()
    # Identify executable arguments only. Never inspect an old process's memory,
    # environment, private key, temporary fixture or durable operation claim.
    for path in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            argv = path.read_bytes().split(b'\0')
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        assert not any(arg.endswith(b'/run-API48-serialized-public-qualification-0001.py')
                       or arg.endswith(b'/api48-current-checks-v1/checks.py') for arg in argv), 'prior suite still live'
    selected = ROOT / 'product/lab/release-candidates/v1/packaging/R02/packages/0003/selection.json'
    environment = json.loads(selected.read_bytes())
    for name, version in environment['versions'].items():
        assert importlib.metadata.version(name) == version, 'selected dependency version differs'
    assert sys.version.split()[0] == environment['environment']['python_version']
    manifest = CHECKS / 'source-manifest.json'
    assert bind(manifest)['sha256'] == CHECK_SHA
    for row in json.loads(manifest.read_bytes())['files']:
        path = ROOT / row['path']
        assert path.is_file() and not path.is_symlink()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], row['path']
    report_path = CHECKS / 'receipts/checks-0001.json'
    assert not report_path.exists(), 'preserve any existing result'
    command = [sys.executable, '-B', str(CHECKS / 'checks.py'), '--check-source-sha256', CHECK_SHA]
    started = datetime.now(timezone.utc).isoformat()
    print(json.dumps({'phase': 'STARTING-FRESH-API49-TYPED10', 'started_at': started,
                      'prior_selected_suites_still_outstanding': True}), flush=True)
    log = RUN / 'API49-typed10-0001.log'
    with log.open('xb') as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
    terminal = {'schema_version': 'lab-child-process-terminal/v1-candidate', 'suite': 'API49-typed10',
        'command': command, 'actual_exit_code': result.returncode, 'started_at': started,
        'completed_at': datetime.now(timezone.utc).isoformat(), 'log_binding': bind(log),
        'prior_interruption_binding': bind(observation), 'selected_environment_binding': bind(selected),
        'check_source_binding': bind(manifest), 'result': 'PASS' if result.returncode == 0 else 'FAIL',
        'full_selected_suite_completed': False, 'whole_API_qualified': False,
        'authority_effect': 'none', 'task_complete': False}
    if report_path.exists():
        report = json.loads(report_path.read_bytes())
        terminal.update(report_binding=bind(report_path), actual_cases=report['actual_cases'],
                        failures=report['failures'], errors=report['errors'],
                        full_selected_suite_completed=report['actual_cases'] == 10,
                        original_reader_guarded_exit_completed=report['original_reader_guarded_exit_completed'])
    put(RUN / 'API49-typed10-terminal-0001.json', terminal)
    print(json.dumps(terminal), flush=True)
    return result.returncode if result.returncode >= 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
