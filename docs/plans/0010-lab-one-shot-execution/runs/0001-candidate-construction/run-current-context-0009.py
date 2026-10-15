"""Capture actual successor Context build/check exits without replacing guards."""
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SELECTED = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v9'
SOURCE_PIN = '85f81392b9ae2e4c34d96c0f6696b3b0a34397717f4b11706fa062eba8a20cb3'
OBSERVER_PIN = '0501e20c920c16e8e2378bb6884a37fce7e9ba0f1cebe9f8dd8adb940abe46bb'
MAPPED_PIN = '61eba56461293d8e056b71e2066d1ceec40aab633d8a4caf3ddaa550c57b981e'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source = SELECTED / 'source-manifest.json'
    assert bind(source)['sha256'] == SOURCE_PIN
    assert bind(RUN / 'current-context-code-audit-source-0009.json')['sha256'] == OBSERVER_PIN
    result = {'schema_version': 'lab-child-Context-phase-terminals/v1-candidate',
              'producer_binding': bind(Path(__file__).resolve()), 'source_binding': bind(source),
              'selected_exit_codes': {}, 'authority_effect': 'none', 'actual_owner_outcome': None,
              'current_Agent_qualified': False, 'task_complete': False, 'goal_complete': False}
    for phase in ['build', 'checks']:
        command = [sys.executable, '-B', str(RUN / 'run-context-with-code-audit-0009.py'), phase,
                   '--observer-source-sha256', OBSERVER_PIN, '--source-sha256', SOURCE_PIN,
                   '--mapped-package-sha256', MAPPED_PIN]
        if phase == 'checks':
            command += ['--package-sha256', bind(SELECTED / 'packages/0001/manifest.json')['sha256']]
        log = RUN / f'current-context-{phase}-0009.log'
        started = datetime.now(timezone.utc).isoformat()
        print(json.dumps({'phase': phase, 'status': 'STARTING'}), flush=True)
        with log.open('xb') as stream:
            child = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
        result['selected_exit_codes'][phase] = child.returncode
        result[phase] = {'command': command, 'exit_code': child.returncode,
                         'terminal_observed': True, 'source_binding': bind(source),
                         'log_binding': bind(log), 'started_at': started,
                         'completed_at': datetime.now(timezone.utc).isoformat()}
        print(json.dumps({'phase': phase, 'actual_exit_code': child.returncode, 'log_binding': bind(log)}), flush=True)
        if child.returncode != 0:
            break
    output = RUN / 'current-context-delivery-terminal-0009.json'
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'terminal_binding': bind(output), 'selected_exit_codes': result['selected_exit_codes']}), flush=True)
    return next((value for value in result['selected_exit_codes'].values() if value != 0), 0)


if __name__ == '__main__':
    raise SystemExit(main())
