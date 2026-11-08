"""Prove a wrong-branch Ed25519 proof refuses before composite readiness."""

import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
SELECTION_SHA = '7c029bbc7c588ef3cfc29e1466fba7dae80c97e0904dfbb59337c90d277ed48c'
LAUNCHER_SHA = '6dd81ccea7701b7d3adba9be68215924b678b5d05a81bf317a727efffe9559fe'
RUNNER_SHA = '92532aab4ac9641029a750a02bba04bd9702c1a30dc6ee8d6dec6f4ade0720d9'
POSITIVE_SHA = '62775b824645bb1900d02fa66d4d9a0bc853c12c903bf51182745fc35fea65fb'
DRIVER_SHA = 'fe4135724f40d1123b78fa2158c53ff573ccf416b9db3f5f567edc83c6a4848e'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(path, expected):
    path = Path(path)
    if not path.is_absolute() or not path.is_relative_to(ROOT) or any(p.is_symlink() for p in path.parents):
        raise ValueError('selected origin differs')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 16 * 1024 * 1024:
            raise ValueError('selected file differs')
        parts = []
        while block := os.read(fd, 1024 * 1024):
            parts.append(block)
        raw = b''.join(parts)
        after = os.fstat(fd)
        fresh = path.lstat()
        stamp = lambda v: (v.st_dev, v.st_ino, v.st_uid, v.st_mode, v.st_size, v.st_mtime_ns, v.st_ctime_ns)
        if stamp(before) != stamp(after) or stamp(after) != stamp(fresh) or sha(raw) != expected:
            raise ValueError('selected bytes changed')
        return raw
    finally:
        os.close(fd)


def selected():
    launch_path = HERE / 'launch_api45_revision2_pairs.py'
    launch_raw = capture(launch_path, LAUNCHER_SHA)
    launch = {'__name__': '_t18_selected_launcher', '__file__': str(launch_path)}
    exec(compile(launch_raw, str(launch_path), 'exec', dont_inherit=True), launch)
    selection_raw = capture(HERE / 'API45R2-HARNESS-SELECTION-0001.json', SELECTION_SHA)
    selection = json.loads(selection_raw)
    if launch['verify'](selection, launch_path) != RUNNER_SHA:
        raise ValueError('selected runner binding differs')
    runner_path = HERE / 'run_api45_revision2_pairs.py'
    runner_raw = capture(runner_path, RUNNER_SHA)
    runner = {'__name__': '_t18_selected_runner', '__file__': str(runner_path)}
    exec(compile(runner_raw, str(runner_path), 'exec', dont_inherit=True), runner)
    runner['verify_selection']()
    positive = json.loads(capture(HERE / 'RUN-API45R2-PAIRS-0001.json', POSITIVE_SHA))
    if not (positive['status'] == 'PASS' and positive['public_driver_result']['dispatch_operations_executed'] == 15 and
            positive['api_source_sha256'] == runner['PINS'][runner['API'] / 'source-manifest.json'] and
            positive['api_profile_sha256'] == runner['PINS'][runner['API'] / 'contract-profile.json']):
        raise ValueError('same-cut positive binding differs')
    driver_path = runner['BRANCH'] / 'drive_operator.py'
    driver_raw = capture(driver_path, DRIVER_SHA)
    branch = json.loads(capture(runner['BRANCH'] / 'driver-selection.json', runner['PINS'][runner['BRANCH'] / 'driver-selection.json']))
    if {r['path']: r['sha256'] for r in branch['files']}.get(driver_path.relative_to(ROOT).as_posix()) != DRIVER_SHA:
        raise ValueError('wrong-branch driver absent from selection')
    driver = {'__name__': '_t18_selected_driver', '__file__': str(driver_path)}
    exec(compile(driver_raw, str(driver_path), 'exec', dont_inherit=True), driver)
    return runner, driver, positive


def run(runner, driver, control):
    import argparse
    from cryptography.hazmat.primitives import serialization

    loader = runner['INSTALL'] / 'lib/abi/ld-linux-x86-64.so.2'
    installed = [str(loader), '--inhibit-cache', '--library-path', str(runner['INSTALL'] / 'lib/abi'),
                 str(runner['INSTALL'] / 'bin/python'), '-X', 'utf8', '-B', '-S']
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'PYTHONNOUSERSITE': '1',
           'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(runner['OVERLAY']) + ':' + str(runner['INSTALL'] / 'deps')}
    selection = runner['BRANCH'] / 'driver-selection.json'
    stage, stage_seconds = runner['child']([*installed, str(runner['BRANCH'] / 'prepare_branches.py'), 'stage-keys',
        '--selection', str(selection), '--selection-sha256', runner['PINS'][selection]], control, 'stage', 120, env)
    if stage.returncode:
        raise ValueError('fresh private key staging refused')
    root = Path(stage.stdout.decode().strip())
    state = root.lstat()
    if (root.parent != Path('/tmp') or not root.name.startswith('cal-T06-branch-fixtures-') or
            not stat.S_ISDIR(state.st_mode) or state.st_uid != os.getuid() or stat.S_IMODE(state.st_mode) != 0o700):
        raise ValueError('fresh private root differs')
    lock = control / 'lease.lock'
    prepare, prepare_seconds = runner['child']([*installed, str(runner['BRANCH'] / 'prepare_branches.py'), 'prepare',
        '--selection', str(selection), '--selection-sha256', runner['PINS'][selection], '--root', str(root),
        '--source-sha256', runner['PINS'][runner['API'] / 'source-manifest.json'],
        '--profile-sha256', runner['PINS'][runner['API'] / 'contract-profile.json'],
        '--lease-lock', str(lock)], control, 'prepare', 900, env)
    if prepare.returncode:
        raise ValueError('actual three-branch preparation refused')
    private_selection = root / 'private-branch-selection.json'
    record = driver['read_record'](private_selection, sha(private_selection.read_bytes()))
    args = argparse.Namespace(sdk_directory=str(runner['SDK']), sdk_source_sha256=runner['PINS'][runner['SDK'] / 'source-manifest.json'],
                              provisioning_path=runner['PROVISION'].relative_to(ROOT).as_posix(),
                              provisioning_sha256=runner['PINS'][runner['PROVISION']])
    config, config_path, config_sha = driver['configure'](record, args)
    lock_fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    stderr_path = control / 'operator-stderr.bin'
    stderr_fd = os.open(stderr_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    child = None
    try:
        import fcntl
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with os.fdopen(stderr_fd, 'wb') as errors:
            installation = Path(config['dependencies']['installation'])
            child = subprocess.Popen([str(installation / 'lib/abi/ld-linux-x86-64.so.2'), '--inhibit-cache',
                '--library-path', str(installation / 'lib/abi'), str(installation / 'bin/python'),
                '-I', '-X', 'utf8', '-B', '-S', str(runner['SDK'] / 'launch.py'),
                '--launcher-source-sha256', runner['PINS'][runner['SDK'] / 'source-manifest.json'],
                '--config', str(config_path), '--config-sha256', config_sha],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors, pass_fds=(lock_fd,),
                env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
            frames = driver['Frames'](child.stdout)
            deadline = time.monotonic() + 1200
            request = frames.receive(deadline)
            if request.get('schema_version') != 'lab-composite-fresh-session-request/v1-candidate':
                raise ValueError('fresh lease request absent')
            driver['send'](child.stdin, driver['make_handoff'](record, config, config_sha, request))
            challenges = frames.receive(deadline)
            if challenges.get('schema_version') != 'lab-composite-challenges/v1-candidate' or set(challenges['challenges']) != {'base','actions','governance'}:
                raise ValueError('three independent challenges absent')
            base_key = driver['load_key'](record['reader_keys']['base'], record)
            wrong_key = driver['load_key'](record['reader_keys']['actions'], record)
            public_bytes = lambda key: key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
            if public_bytes(base_key) == public_bytes(wrong_key):
                raise ValueError('independent branch keys unexpectedly equal')
            challenge = challenges['challenges']['base']
            proof = {'schema_version': 'lab-local-reader-proof/v1-candidate', 'challenge': challenge,
                     'signature': base64.b64encode(wrong_key.sign(driver['compact'](challenge))).decode()}
            driver['send'](child.stdin, {'schema_version': 'lab-composite-branch-proof/v1-candidate',
                'branch': 'base', 'proof_base64': base64.b64encode(driver['compact'](proof)).decode()})
            refusal = frames.receive(deadline)
            expected = {'schema_version': 'lab-composite-startup-error/v1-candidate',
                        'code': 'startup-or-channel-refused', 'authority_effect': 'none'}
            if refusal != expected:
                raise ValueError('wrong-branch proof did not cause exact startup refusal')
            child.stdin.close()
            exit_code = child.wait(timeout=120)
            if exit_code != 2:
                raise ValueError('wrong-branch child did not refuse with exit code 2')
            return {'stage_seconds': stage_seconds, 'prepare_seconds': prepare_seconds,
                    'private_root_locator_sha256': sha(str(root).encode()),
                    'private_selection_sha256': sha(private_selection.read_bytes()),
                    'config_sha256': config_sha, 'fresh_request_sha256': sha(driver['compact'](request)),
                    'challenge_frame_sha256': sha(driver['compact'](challenges)),
                    'wrong_branch': 'actions-key-on-base-challenge', 'distinct_branch_public_keys': True,
                    'signed_challenge_sha256': sha(driver['compact'](challenge)),
                    'refusal': refusal, 'child_exit_code': exit_code,
                    'dispatch_operations_executed': 0,
                    'private_stderr_sha256': sha(stderr_path.read_bytes())}
    finally:
        if child is not None and child.poll() is None:
            if not child.stdin.closed:
                child.stdin.close()
            child.wait(timeout=120)
        os.close(lock_fd)


def main():
    os.umask(0o077)
    result = {'schema_version': 'lab-T18-api45r2-wrong-branch-handshake/v1-candidate',
              'status': 'REFUSED', 'authority_effect': 'none', 'whole_api_qualified': False,
              'started_at_utc': datetime.now(timezone.utc).isoformat(),
              'positive_same_cut_result_sha256': POSITIVE_SHA,
              'api45r2_harness_selection_sha256': SELECTION_SHA,
              'driver_sha256': DRIVER_SHA}
    started = time.monotonic()
    control = Path(tempfile.mkdtemp(prefix='cal-T18-api45r2-wrong-branch-', dir='/tmp'))
    result['control_locator_sha256'] = sha(str(control).encode())
    try:
        runner, driver, positive = selected()
        result.update(run(runner, driver, control))
        runner['verify_selection']()
        capture(HERE / 'API45R2-HARNESS-SELECTION-0001.json', SELECTION_SHA)
        capture(runner['BRANCH'] / 'drive_operator.py', DRIVER_SHA)
        capture(HERE / 'RUN-API45R2-PAIRS-0001.json', POSITIVE_SHA)
        result['status'] = 'PASS'
    except Exception as error:
        result['error_class'] = type(error).__name__
        result['error_message_sha256'] = sha(str(error).encode())
    finally:
        result['elapsed_seconds'] = round(time.monotonic() - started, 3)
        result['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
        result['claim_ceiling'] = ('One fresh exact-cut composite startup refuses a cryptographically valid '
                                   'Action-key signature submitted as the Base branch proof before readiness; '
                                   'zero dispatch, no authority effect, no all-34 operation claim.')
        receipt = HERE / 'RUN-T18-API45R2-WRONG-BRANCH-0001.json'
        fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            raw = (json.dumps(result, sort_keys=True, indent=2) + '\n').encode()
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds'],
                      'receipt': str(receipt)}, sort_keys=True))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
