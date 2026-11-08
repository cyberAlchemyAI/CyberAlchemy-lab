"""Run one private, current API43 Base/Action/Governance composite fixture."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
TASK = ROOT / 'implementation/lab-runtime/local-host/t22-api-selector-recut-0001'
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v43-r03-0005-composite-0001'
SDK = ROOT / 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api43-t22-0001/revision-0001'
BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api43-t22-0001/revision-0001'
INSTALL = ROOT / 'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001'
OVERLAY = ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay'
PROVISION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result-v4.json'
PINS = {
    API / 'source-manifest.json': '22cd380b7544721c6519c869e430a99cbb6b84c3e863a425125f3d9944981560',
    API / 'contract-profile.json': 'bc660fbd0ac6055dc49b008c9c46c4b09925e1e3cd8795940a0563348b04a2e6',
    SDK / 'source-manifest.json': '39f3593f496dea3e86fb6c152a4853568c39b0bc4b46648bd80cadac965e194a',
    BRANCH / 'driver-selection.json': '50572a2db800eb605f4b6f7d6704f55a32838850f157b4c2135da0da79a2d9a4',
    PROVISION: '81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def exact(path, expected):
    state = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(state.st_mode) or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('selected origin differs')
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError('selected byte differs')
    return raw


def verify_selection():
    for path, expected in PINS.items():
        exact(path, expected)
    source = json.loads((API / 'source-manifest.json').read_bytes())
    profile = json.loads((API / 'contract-profile.json').read_bytes())
    if source['profile_binding'] != {
        'path': (API / 'contract-profile.json').relative_to(ROOT).as_posix(),
        'sha256': PINS[API / 'contract-profile.json'],
    }:
        raise ValueError('API43 profile binding differs')
    for rows, count in ((source['files'], 207), (profile['files'], 33434)):
        if len(rows) != count or len({row['path'] for row in rows}) != count:
            raise ValueError('selected source inventory differs')
        for row in rows:
            path = Path(row['path'])
            exact(path if path.is_absolute() else ROOT / path, row['sha256'])


def private_file(folder, name, raw):
    path = folder / name
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return path


def child(argv, folder, name, timeout, env):
    started = time.monotonic()
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout, env=env)
    private_file(folder, name + '-stdout.bin', result.stdout)
    private_file(folder, name + '-stderr.bin', result.stderr)
    return result, round(time.monotonic() - started, 3)


def run(control):
    loader = INSTALL / 'lib/abi/ld-linux-x86-64.so.2'
    installed = [str(loader), '--inhibit-cache', '--library-path', str(INSTALL / 'lib/abi'),
                 str(INSTALL / 'bin/python'), '-X', 'utf8', '-B', '-S']
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'PYTHONNOUSERSITE': '1',
           'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(OVERLAY) + ':' + str(INSTALL / 'deps')}
    selection_path = BRANCH / 'driver-selection.json'
    stage, stage_seconds = child([*installed, str(BRANCH / 'prepare_branches.py'), 'stage-keys',
                                  '--selection', str(selection_path), '--selection-sha256', PINS[selection_path]],
                                 control, 'stage', 120, env)
    if stage.returncode:
        raise ValueError('fresh private key staging refused')
    root = Path(stage.stdout.decode().strip())
    state = root.lstat()
    if (root.parent != Path('/tmp') or not root.name.startswith('cal-T06-branch-fixtures-') or
            not stat.S_ISDIR(state.st_mode) or state.st_uid != os.getuid() or stat.S_IMODE(state.st_mode) != 0o700):
        raise ValueError('private root differs')
    lock = control / 'lease.lock'
    prepare, prepare_seconds = child([*installed, str(BRANCH / 'prepare_branches.py'), 'prepare',
                                      '--selection', str(selection_path), '--selection-sha256', PINS[selection_path],
                                      '--root', str(root), '--source-sha256', PINS[API / 'source-manifest.json'],
                                      '--profile-sha256', PINS[API / 'contract-profile.json'], '--lease-lock', str(lock)],
                                     control, 'prepare', 900, env)
    if prepare.returncode:
        raise ValueError('actual three-branch preparation refused')
    selected = root / 'private-branch-selection.json'
    selected_state = selected.lstat()
    if (not stat.S_ISREG(selected_state.st_mode) or selected_state.st_uid != os.getuid() or
            stat.S_IMODE(selected_state.st_mode) != 0o600):
        raise ValueError('private branch selection differs')
    selected_sha = sha(selected.read_bytes())
    driver = BRANCH / 'drive_operator.py'
    live, live_seconds = child([sys.executable, '-B', str(driver),
                                '--branch-selection', str(selected), '--branch-selection-sha256', selected_sha,
                                '--sdk-directory', str(SDK), '--sdk-source-sha256', PINS[SDK / 'source-manifest.json'],
                                '--provisioning-path', PROVISION.relative_to(ROOT).as_posix(),
                                '--provisioning-sha256', PINS[PROVISION], '--lease-lock', str(lock)],
                               control, 'drive', 1200, {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    if live.returncode:
        raise ValueError('actual composite driver refused')
    public = json.loads(live.stdout)
    observations = public.get('observations', [])
    if not (public.get('status') == 'PASS' and public.get('process_exit_code') == 0 and
            public.get('dispatch_operations_executed') == 7 and len(observations) == 7 and
            [row.get('branch') for row in observations] ==
            ['base', 'base', 'actions', 'actions', 'actions', 'governance', 'governance'] and
            [row.get('operation') for row in observations] ==
            ['lab.status', 'catalog.get', 'action.dispatch', 'operation.inspect',
             'action.dispatch', 'capability.adoption.prepare', 'operation.inspect'] and
            observations[4].get('code') == 'unauthorized'):
        raise ValueError('seven-call public result differs')
    return {
        'stage_seconds': stage_seconds, 'prepare_seconds': prepare_seconds, 'live_seconds': live_seconds,
        'private_root_locator_sha256': sha(str(root).encode()),
        'private_branch_selection_sha256': selected_sha,
        'private_logs_sha256': {name: sha((control / name).read_bytes()) for name in
                                ('stage-stdout.bin', 'stage-stderr.bin', 'prepare-stdout.bin',
                                 'prepare-stderr.bin', 'drive-stdout.bin', 'drive-stderr.bin')},
        'public_driver_result': public,
    }


def main():
    os.umask(0o077)
    own = Path(__file__)
    own_sha = sha(exact(own, sha(own.read_bytes())))
    control = Path(tempfile.mkdtemp(prefix='cal-T06-api43-product-', dir='/tmp'))
    started = time.monotonic()
    result = {
        'schema_version': 'lab-T06-api43-local-product/v1-candidate', 'status': 'REFUSED',
        'entrypoint_sha256': own_sha,
        'api_source_sha256': PINS[API / 'source-manifest.json'],
        'api_profile_sha256': PINS[API / 'contract-profile.json'],
        'sdk_manifest_sha256': PINS[SDK / 'source-manifest.json'],
        'branch_selection_sha256': PINS[BRANCH / 'driver-selection.json'],
        'control_locator_sha256': sha(str(control).encode()),
        'authority_effect': 'none', 'whole_api_qualified': False,
        'craft_native_dispatch_integration': False,
        'started_at': datetime.now(timezone.utc).isoformat(),
    }
    try:
        verify_selection()
        result.update(run(control))
        result['status'] = 'PASS'
    except Exception as error:
        result['error_class'] = type(error).__name__
        result['error_message_sha256'] = sha(str(error).encode())
    finally:
        verify_selection()
        if sha(own.read_bytes()) != own_sha:
            raise ValueError('entrypoint changed during run')
        result['elapsed_seconds'] = round(time.monotonic() - started, 3)
        result['finished_at'] = datetime.now(timezone.utc).isoformat()
        result['claim_ceiling'] = ('One fresh local API43 Base/Action/Governance composite technical fixture and seven '
                                   'public dispatch calls; no authority effect, full 34-operation qualification, '
                                   'or native Craft dispatch claim.')
        receipt = TASK / 'RUN-API43-PRODUCT-0001.json'
        fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write((json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
            stream.flush()
            os.fsync(stream.fileno())
    print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds'],
                      'receipt': str(receipt), 'entrypoint_sha256': own_sha}, sort_keys=True))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
