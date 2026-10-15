"""Freeze and capture the independent successor audit after actual full50 checks."""
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SELECTED = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v9'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    terminal_path = RUN / 'current-context-delivery-terminal-0009.json'
    terminal = load(terminal_path)
    assert terminal['selected_exit_codes'] == {'build': 0, 'checks': 0}
    report = load(SELECTED / 'receipts/checks.json')
    assert report['result'] == 'PASS' and report['tests_run'] == 50
    context_path = RUN / 'context-R03-current-context-audit-0009.json'
    paths = [SELECTED / 'source-manifest.json', SELECTED / 'packages/0001/manifest.json',
             SELECTED / 'receipts/checks.json', terminal_path,
             RUN / 'current-context-code-audit-source-0009.json',
             RUN / 'current-context-code-execution-build-0009.json',
             RUN / 'current-context-code-execution-checks-0009.json',
             RUN / 'authorization.json', Path(__file__).resolve()]
    for phase in ['build', 'checks']:
        row = terminal[phase]
        assert row['terminal_observed'] and row['exit_code'] == 0
        assert bind(ROOT / row['log_binding']['path']) == row['log_binding']
        paths.append(ROOT / row['log_binding']['path'])
    emit(context_path, {'schema_version': 'lab-bounded-context/v1-candidate',
                        'task': 'R03 independent fresh Context audit', 'strict_coverage': 'PASS',
                        'source_bindings': [bind(path) for path in paths],
                        'blockers': [], 'runtime_qualified': False, 'authority_effect': 'none',
                        'actual_owner_outcome': None,
                        'constraints': ['Verify exact fresh source/reader/native bytes and all50 methods.',
                                        'Retain every historical parent proof and immutable period.',
                                        'Verify actual disposable host/key closure; no Session or permission restoration.',
                                        'No API, owner, admission or complete plan claim.']})
    freeze_log = RUN / 'current-context-audit-freeze-0009.log'
    with freeze_log.open('xb') as stream:
        frozen = subprocess.run([sys.executable, '-B', str(RUN / 'freeze-R03-current-context-audit-0009.py')],
                                stdout=stream, stderr=subprocess.STDOUT)
    assert frozen.returncode == 0, freeze_log
    source = RUN / 'current-context-audit-source-0009.json'
    command = [sys.executable, '-B', str(RUN / 'audit-R03-current-context-0009.py'),
               '--source-sha256', bind(source)['sha256']]
    started = datetime.now(timezone.utc).isoformat()
    log = RUN / 'current-context-independent-audit-0009.log'
    print(json.dumps({'phase': 'independent-audit', 'status': 'STARTING', 'source_binding': bind(source)}), flush=True)
    with log.open('xb') as stream:
        audit = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
    output = RUN / 'current-context-delivery-audit-terminal-0009.json'
    result = {'schema_version': 'lab-child-process-terminal/v1-candidate',
              'command': command, 'actual_exit_code': audit.returncode,
              'source_binding': bind(source), 'Context_source_binding': bind(SELECTED / 'source-manifest.json'),
              'producer_binding': bind(Path(__file__).resolve()), 'log_binding': bind(log),
              'started_at': started, 'completed_at': datetime.now(timezone.utc).isoformat(),
              'freeze_actual_exit_code': frozen.returncode, 'freeze_log_binding': bind(freeze_log),
              'authority_effect': 'none', 'actual_owner_outcome': None,
              'current_Agent_qualified': False, 'task_complete': False, 'goal_complete': False}
    report_path = SELECTED / 'receipts/independent-audit.json'
    if report_path.exists():
        result['report_binding'] = bind(report_path)
        result['result'] = load(report_path)['result']
    emit(output, result)
    print(json.dumps({'actual_exit_code': audit.returncode, 'terminal_binding': bind(output)}), flush=True)
    return audit.returncode


if __name__ == '__main__':
    raise SystemExit(main())
