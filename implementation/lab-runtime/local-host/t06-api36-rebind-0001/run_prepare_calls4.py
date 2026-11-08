"""One fresh API36 T06 preparation under the sealed installed environment."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
TASK = ROOT / 'implementation/lab-runtime/local-host/t06-api36-rebind-0001'
PRODUCER = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api36-0001/revision-0001'
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v36-current-t06-0001'
SDK = ROOT / 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api36-0001/revision-0001'
INSTALL = ROOT / 'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001'
INSTALLED_PYTHON = [str(INSTALL / 'lib/abi/ld-linux-x86-64.so.2'), '--inhibit-cache',
                    '--library-path', str(INSTALL / 'lib/abi'), str(INSTALL / 'bin/python'),
                    '-X', 'utf8', '-B', '-S']
CONTROL = Path('/tmp/cal-T06-api36-calls4-control-0001')
LOCK = Path('/tmp/cal-T06-api36-calls4-lease-sensitive-runtime.lock')
PINS = {
    PRODUCER / 'driver-selection.json': 'c4cd19bc3bd498e809baaa8b8cb308cc8b09552544d432e9f534806c6fcb2c9d',
    API / 'source-manifest.json': '5990d980ae1df2fe59c90eabfc9de806ea8ab7abbf90bb123063f5ad83ff592f',
    API / 'contract-profile.json': 'c5bc36e213979199fdd947bdb7309a4e32534305fd93eca6366aff9e19f01e78',
    API / 'integration-members.json': '1caa8e6dc18e7f34a5ec7d86a37c4673566fb3ed2ead267b2256adb939ddf527',
    SDK / 'source-manifest.json': '09075e54f49cef4176d6244b2ef8d56baacd3ebfdd67210c8f5f6e89d64d328a',
    ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v34-current-t06-0001/source-manifest.json': '4a47f51f9b93e7a51ed3fe4b59c340ac0c8f0dabc19eb851392dbd64b608b9bd',
    ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v34-current-t06-0001/contract-profile.json': '371e305e053cfcb88aa318149b8c47298af38f2d567599c6d935808a1be7d835',
    ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/source-manifest.json': '574bd9f1fc976755eb0bf075b2ec7c14d8c378e8c6b074fa4df0e50af3951bd7',
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def exact():
    for path, expected in PINS.items():
        if not path.is_file() or path.is_symlink() or sha(path.read_bytes()) != expected:
            raise ValueError('selected public input differs: ' + str(path.relative_to(ROOT)))

def private_file(name, raw):
    path = CONTROL / name
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return path

def child(args, name, timeout):
    before = time.monotonic()
    outcome = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=timeout,
                             env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'PYTHONNOUSERSITE': '1',
                                  'PYTHONPATH': str(ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay') + ':' + str(INSTALL / 'deps'), 'PYTHONDONTWRITEBYTECODE': '1'})
    private_file(name + '-stdout.bin', outcome.stdout)
    private_file(name + '-stderr.bin', outcome.stderr)
    return outcome, round(time.monotonic() - before, 3)

def main():
    os.umask(0o077)
    exact()
    CONTROL.mkdir(mode=0o700)
    if stat.S_IMODE(CONTROL.stat().st_mode) != 0o700:
        raise ValueError('private control directory mode differs')
    result = {'schema_version': 'lab-T06-api36-preparation/v1', 'source_manifest_sha256': PINS[API / 'source-manifest.json'],
              'profile_sha256': PINS[API / 'contract-profile.json'], 'driver_selection_sha256': PINS[PRODUCER / 'driver-selection.json'],
              'sdk_manifest_sha256': PINS[SDK / 'source-manifest.json'], 'authority_effect': 'none',
              'composite_child_started': False, 'load_before': list(os.getloadavg())}
    started = time.monotonic()
    try:
        stage, stage_seconds = child([*INSTALLED_PYTHON, str(PRODUCER / 'prepare_branches.py'), 'stage-keys',
                                      '--selection', str(PRODUCER / 'driver-selection.json'),
                                      '--selection-sha256', PINS[PRODUCER / 'driver-selection.json']], 'stage', 120)
        result['stage_exit_code'] = stage.returncode; result['stage_seconds'] = stage_seconds
        if stage.returncode != 0:
            raise ValueError('fresh private key staging refused')
        private_root = Path(stage.stdout.decode().strip())
        if private_root.parent != Path('/tmp') or not private_root.name.startswith('cal-T06-branch-fixtures-'):
            raise ValueError('unexpected private root locator')
        identity = private_root.lstat()
        if not stat.S_ISDIR(identity.st_mode) or identity.st_uid != os.getuid() or stat.S_IMODE(identity.st_mode) != 0o700:
            raise ValueError('private root custody differs')
        private_file('root.txt', (str(private_root) + '\n').encode())
        result['private_root_locator_sha256'] = sha(str(private_root).encode())
        prepare, prepare_seconds = child([*INSTALLED_PYTHON, str(PRODUCER / 'prepare_branches.py'), 'prepare',
                                          '--selection', str(PRODUCER / 'driver-selection.json'),
                                          '--selection-sha256', PINS[PRODUCER / 'driver-selection.json'],
                                          '--root', str(private_root), '--source-sha256', PINS[API / 'source-manifest.json'],
                                          '--profile-sha256', PINS[API / 'contract-profile.json'],
                                          '--lease-lock', str(LOCK)], 'prepare', 900)
        result['prepare_exit_code'] = prepare.returncode; result['prepare_seconds'] = prepare_seconds
        if prepare.returncode != 0:
            raise ValueError('isolated three-branch preparation refused')
        selection = private_root / 'private-branch-selection.json'
        if not selection.is_file() or selection.is_symlink() or stat.S_IMODE(selection.stat().st_mode) != 0o600:
            raise ValueError('private branch selection absent or unsafe')
        result['private_branch_selection_sha256'] = sha(selection.read_bytes())
        result['status'] = 'PASS-PREPARED'
    except Exception as error:
        result['status'] = 'REFUSED'
        result['error_class'] = type(error).__name__
        result['error_message_sha256'] = sha(str(error).encode())
    finally:
        exact()
        result['elapsed_seconds'] = round(time.monotonic() - started, 3)
        result['load_after'] = list(os.getloadavg())
        result['private_logs'] = {name: sha((CONTROL / name).read_bytes()) for name in
                                  ('stage-stdout.bin', 'stage-stderr.bin', 'prepare-stdout.bin', 'prepare-stderr.bin')
                                  if (CONTROL / name).is_file()}
        (TASK / 'RUN-PREPARE-CALLS-0004.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))
    return 0 if result['status'] == 'PASS-PREPARED' else 1

if __name__ == '__main__':
    raise SystemExit(main())
