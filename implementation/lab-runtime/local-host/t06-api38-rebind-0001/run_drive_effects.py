"""Run one exact prepared T06 API38 composite startup; keep private wire logs external."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
TASK = ROOT / 'implementation/lab-runtime/local-host/t06-api38-rebind-0001'
PRODUCER = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api38-0001/revision-0001'
SDK = ROOT / 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api38-0001/revision-0001'
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v38-current-t06-0001'
CONTROL = Path('/tmp/cal-T06-api38-control-0001')
LOCK = Path('/tmp/cal-T06-api38-lease-sensitive-runtime.lock')
PROVISION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result-v4.json'
PINS = {
    PRODUCER / 'driver-selection.json': 'bfdc80f119d415ba243ff1fe72c0870f33d3406eb3446a39f86a1bb408a73967',
    SDK / 'source-manifest.json': '4da6dc3db086ffb4d74abaa8f364c3579c7acdbf72afbb7f7e54b4e5c169847b',
    API / 'source-manifest.json': '71f5ba4008ce1955265e949bb5250a5af6d9cc5da046d40c8fa7c6a765f774a7',
    API / 'contract-profile.json': '32e43cbdaf65a81ccd29033d7351f1685e28ca54c640d595e894322749f82869',
    PROVISION: '81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d',
    TASK / 'drive_effects.py': '7fae3f5fc5d7f4c1f983dfef083427efb286fdf2b20b49030bd5074a69bce854',
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
    if selected_sha != '9ac7c7b8fb60d6270003a4c2ff3b24e0d0f2f7077ccb89a285fa6ea9e5718511':
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
    receipt = {'schema_version': 'lab-T06-api38-live-effects/v1', 'process_exit_code': process.returncode,
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
                ['lab-composite-fresh-session-request/v1-candidate', 'lab-composite-ready/v1-candidate', 'base-positive-reads', 'action-positive-inspection-wrong-scope', 'governance-positive-and-inspection'] and
                events[1].get('catalog_operation_count') == 34 and
                events[1].get('composition') == 'Base28+Action3+Governance3' and
                result.get('dispatch_operations_executed') == 7 and
                events[2].get('count') == 2 and len(result.get('observations', [])) == 7 and events[3].get('count') == 3 and events[4].get('count') == 2 and
                result['observations'][2].get('posture') == 'completed' and result['observations'][3].get('posture') == 'completed' and result['observations'][4].get('code') == 'unauthorized' and result['observations'][5].get('reply_kind') == 'result' and result['observations'][6].get('posture') == 'completed'):
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
