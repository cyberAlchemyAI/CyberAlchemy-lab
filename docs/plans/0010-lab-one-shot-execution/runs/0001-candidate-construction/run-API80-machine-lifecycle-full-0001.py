"""Capture the actual20-case child exit and exact independent API selection."""
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v80'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    selection_path = RUN / 'API80-independent-selection-0001.json'
    driver = RUN / 'qualify-API80-machine-lifecycle-full-0001.py'
    source, profile = API / 'source-manifest.json', API / 'contract-profile.json'
    assert source.exists() and profile.exists()
    emit(selection_path, {'schema_version': 'lab-exact-API-test-selection/v1-candidate',
                          'source_binding': bind(source), 'profile_binding': bind(profile),
                          'driver_binding': bind(driver), 'producer_binding': bind(Path(__file__).resolve()),
                          'authorization_binding': bind(RUN / 'authorization.json'),
                          'original_Machine_cases': 14, 'original_termination_cases': 6,
                          'original_clocks_and_callbacks': True, 'maximum_Session_seconds': 900,
                          'runtime_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    command = [sys.executable, '-B', str(driver), '--selection-sha256', bind(selection_path)['sha256']]
    log = RUN / 'API80-machine-lifecycle-full-driver-0001.log'
    started = datetime.now(timezone.utc).isoformat()
    print(json.dumps({'phase': 'STARTING', 'selection_binding': bind(selection_path), 'original_cases': 20}), flush=True)
    with log.open('xb') as stream:
        completed = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
    terminal = {'schema_version': 'lab-child-process-terminal/v1-candidate',
                'actual_exit_code': completed.returncode, 'command': command,
                'source_binding': bind(source), 'profile_binding': bind(profile),
                'selection_binding': bind(selection_path), 'producer_binding': bind(Path(__file__).resolve()),
                'log_binding': bind(log), 'started_at': started,
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'whole_API_qualified': False, 'task_complete': False, 'goal_complete': False}
    report = RUN / 'API80-machine-lifecycle-full-0001.json'
    if report.exists():
        terminal['report_binding'] = bind(report)
        terminal['result'] = json.loads(report.read_bytes())['result']
    out = RUN / 'API80-machine-lifecycle-full-terminal-0001.json'
    emit(out, terminal)
    print(json.dumps({'actual_exit_code': completed.returncode, 'terminal_binding': bind(out)}), flush=True)
    return completed.returncode


if __name__ == '__main__':
    raise SystemExit(main())
