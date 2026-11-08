"""Run one private API45 Base/Action/Governance same-child coverage fixture."""
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
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v45-r03-0005-coverage-0001'
SDK = ROOT / 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api45-t17-0001/revision-0001'
BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api45-t17-0001/revision-0001'
INSTALL = ROOT / 'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001'
OVERLAY = ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay'
ACTION = ROOT / 'product/lab/release-candidates/v1/interface/api-action-integration-v8-current-t17-0001/source-manifest.json'
PROVISION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result-v4.json'
PINS = {
    API / 'source-manifest.json': 'd5a57418f84729a085a5a4b335ddcf08ec65de912132a9e2327e66c65dae395d',
    API / 'contract-profile.json': '5635f3d3b5f65852aae01cbd85268802aa42d92b3037fbc70a7694116ed4f205',
    SDK / 'source-manifest.json': '39fd71bade1f31c74150f585bae368334b1cd775c2a6bd401c2ac3852bd79077',
    BRANCH / 'driver-selection.json': 'd8fcbecb0697bf768b9c0a9380e3121496147f9ddd2409b0ae2ffa028de94d15',
    PROVISION: '81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d',
    ACTION: '3b20c6bf6039c5ebf4e2ea056ac5651b465913b13bc133277e039ed60bc37d53',
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
        raise ValueError('API45 profile binding differs')
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
    expected = [
        ('base', 'lab.status', 'positive', 'result'),
        ('base', 'catalog.get', 'positive', 'result'),
        ('base', 'artifact.query', 'positive', 'result'),
        ('base', 'artifact.inspect', 'positive', 'result'),
        ('base', 'lab.status', 'wrong-scope', 'error'),
        ('base', 'catalog.get', 'wrong-context', 'error'),
        ('base', 'artifact.query', 'wrong-scope', 'error'),
        ('base', 'artifact.inspect', 'wrong-context', 'error'),
        ('actions', 'action.dispatch', 'positive-owned-counter', 'result'),
        ('actions', 'operation.inspect', 'positive-owned-counter-inspection', 'result'),
        ('actions', 'operation.inspect', 'wrong-context-refusal', 'error'),
        ('actions', 'action.dispatch', 'wrong-scope-refusal', 'error'),
        ('governance', 'capability.adoption.prepare', 'positive-owned-candidate', 'result'),
        ('governance', 'operation.inspect', 'positive-owned-candidate-inspection', 'result'),
        ('governance', 'capability.adoption.prepare', 'wrong-context-refusal', 'error'),
    ]
    observed = [(row.get('branch'), row.get('operation'), row.get('case'), row.get('reply_kind'))
                for row in observations]
    if not (public.get('status') == 'PASS' and public.get('process_exit_code') == 0 and
            public.get('dispatch_operations_executed') == 15 and observed == expected and
            public.get('authority_effect') == 'none' and public.get('whole_API_qualified') is False and
            all(row.get('authority_effect') == 'none' for row in observations) and
            all(row.get('code') == 'unauthorized' for row in observations if row.get('reply_kind') == 'error') and
            observations[8].get('counter_after') == observations[10].get('counter_after') ==
            observations[11].get('counter_after') == 1):
        raise ValueError('fifteen-call same-child public result differs')
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
    control = Path(tempfile.mkdtemp(prefix='cal-T17-api45-pairs-', dir='/tmp'))
    started = time.monotonic()
    result = {
        'schema_version': 'lab-T17-api45-same-child-coverage/v1-candidate', 'status': 'REFUSED',
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
        result['claim_ceiling'] = ('One fresh local API45 Base/Action/Governance composite technical fixture with '
                                   'fifteen same-child calls across seven distinct operations if PASS; no authority '
                                   'effect, full 34-operation qualification, or native Craft dispatch claim.')
        receipt = TASK / 'RUN-API45-PAIRS-0001.json'
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
