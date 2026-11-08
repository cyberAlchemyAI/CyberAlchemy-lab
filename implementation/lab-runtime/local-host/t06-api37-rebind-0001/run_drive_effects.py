"""Run one exact prepared T06 API37 composite startup; keep private wire logs external."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
TASK = ROOT / 'implementation/lab-runtime/local-host/t06-api37-rebind-0001'
PRODUCER = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api37-0001/revision-0001'
SDK = ROOT / 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api37-0001/revision-0001'
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v37-current-t06-0001'
CONTROL = Path('/tmp/cal-T06-api37-control-0001')
LOCK = Path('/tmp/cal-T06-api37-lease-sensitive-runtime.lock')
PROVISION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result-v4.json'
PINS = {
    PRODUCER / 'driver-selection.json': '5288edf50277eb85e68907c1c72786cac2e26497b059c8016839a99e1bc9c499',
    SDK / 'source-manifest.json': 'eee265a5fcb78c3a338992c2953314840bb2608f4826314b7aa844778c799f27',
    API / 'source-manifest.json': 'cdcd83d10b24551888d9c4890d923fa55ad763617a8ecbf2f853fe8755fc5e60',
    API / 'contract-profile.json': '782a035f07957db35aac0391e010c7552979da87ee521f952edbf9510bb0fc4f',
    PROVISION: '81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d',
    TASK / 'drive_effects.py': '530541b9bdc6705601615dfb4ea56524ab98a6ffaa1d127ffcd39f86f06abd49',
    ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/source-manifest.json': '574bd9f1fc976755eb0bf075b2ec7c14d8c378e8c6b074fa4df0e50af3951bd7',
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def exact():
    for path, pin in PINS.items():
        if path.is_symlink() or not path.is_file() or sha(path.read_bytes()) != pin:
            raise ValueError('public pin changed: ' + str(path.relative_to(ROOT)))

def main():
    os.umask(0o077)
    exact()
    if stat.S_IMODE(CONTROL.stat().st_mode) != 0o700:
        raise ValueError('private control root mode differs')
    private_root = Path((CONTROL / 'root.txt').read_text().strip())
    selection = private_root / 'private-branch-selection.json'
    if private_root.parent != Path('/tmp') or not private_root.name.startswith('cal-T06-branch-fixtures-') or not selection.is_file():
        raise ValueError('selected external preparation root differs')
    selected_sha = sha(selection.read_bytes())
    if selected_sha != 'd02d6165c00279ede9b680077fb2a7cb2364f2b6c16ec87cdd32f0501e2003f0':
        raise ValueError('independent private branch selection pin differs')
    record = json.loads(selection.read_bytes())
    action = Path(record['branches']['actions']['workspace_root'])
    grant = json.loads((action / 'grant.json').read_bytes())
    remaining = grant['expires_at'] - time.time()
    if remaining < 300:
        raise ValueError('prepared Action grant too near expiry for bounded startup')
    argv = [sys.executable, '-B', str(TASK / 'drive_effects.py'),
            '--branch-selection', str(selection), '--branch-selection-sha256', selected_sha,
            '--sdk-directory', str(SDK), '--sdk-source-sha256', PINS[SDK / 'source-manifest.json'],
            '--provisioning-path', str(PROVISION.relative_to(ROOT)), '--provisioning-sha256', PINS[PROVISION],
            '--lease-lock', str(LOCK)]
    started = time.monotonic()
    stdout_path = CONTROL / 'drive-stdout.bin'; stderr_path = CONTROL / 'drive-stderr.bin'
    with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
        os.chmod(stdout_path, 0o600); os.chmod(stderr_path, 0o600)
        process = subprocess.run(argv, cwd=ROOT, stdout=stdout, stderr=stderr,
                                 env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    exact()
    output = stdout_path.read_bytes(); errors = stderr_path.read_bytes()
    receipt = {'schema_version': 'lab-T06-api37-live-effects/v1', 'process_exit_code': process.returncode,
               'elapsed_seconds': round(time.monotonic() - started, 3), 'source_manifest_sha256': PINS[API / 'source-manifest.json'],
               'profile_sha256': PINS[API / 'contract-profile.json'], 'sdk_manifest_sha256': PINS[SDK / 'source-manifest.json'],
               'private_branch_selection_sha256': selected_sha, 'private_root_locator_sha256': sha(str(private_root).encode()),
               'private_stdout_sha256': sha(output), 'private_stderr_sha256': sha(errors), 'private_stderr_size': len(errors),
               'driver_sha256': PINS[TASK / 'drive_effects.py'], 'authority_effect': 'none'}
    if process.returncode == 0:
        result = json.loads(output)
        events = result.get('events', [])
        if not (result.get('status') == 'PASS' and result.get('process_exit_code') == 0 and
                [item.get('event') for item in events] ==
                ['lab-composite-fresh-session-request/v1-candidate', 'lab-composite-ready/v1-candidate', 'representative-reads', 'action-positive-and-wrong-scope'] and
                events[1].get('catalog_operation_count') == 34 and
                events[1].get('composition') == 'Base28+Action3+Governance3' and
                result.get('dispatch_operations_executed') == 6 and
                events[2].get('count') == 4 and len(result.get('observations', [])) == 6 and events[3].get('count') == 2 and
                result['observations'][4].get('posture') == 'completed' and result['observations'][5].get('code') == 'unauthorized'):
            raise ValueError('public driver result differs from actual PASS')
        receipt['result'] = result
        receipt['status'] = 'PASS'
    else:
        receipt['status'] = 'REFUSED'
        receipt['error_class'] = 'driver-nonzero'
    (TASK / 'RUN-LIVE-EFFECTS-0001.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
