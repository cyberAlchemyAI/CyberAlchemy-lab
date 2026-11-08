"""Build and exercise the exact installed public fixture context in Docker."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
INSTALLER = ROOT / 'implementation/lab-runtime/local-host/t25-runtime-installer-0004/install.py'
INSTALLER_SHA = '1d1ac4f57a97e37be80b982adbefd2e2d91cda7681f7369d2314df68dbef3890'
SELECTION = HERE / 'RUNNER-SELECTION-0002.json'
VERIFY = Path('workspace/implementation/lab-runtime/local-host/verify_package.py')
SELECTED_MANIFEST_SHA = '1495543ce90b774d73a514a02f81e529b3bfd0495259ecf9ac12640b9a2606fc'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def private_empty_root(path: Path) -> None:
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute private result root required')
    current = path
    while True:
        state = current.lstat()
        if not stat.S_ISDIR(state.st_mode) or stat.S_ISLNK(state.st_mode):
            raise ValueError('result-root ancestry is redirected')
        if current == path and (state.st_uid != os.getuid()
                                or stat.S_IMODE(state.st_mode) != 0o700):
            raise ValueError('owned mode-0700 result root required')
        if current == current.parent:
            break
        current = current.parent
    if list(path.iterdir()):
        raise ValueError('empty result root required')


def run(label: str, command: list[str], log: Path, *, env=None, timeout=900) -> dict:
    started = utc()
    with log.open('xb') as output:
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                    stdout=output, stderr=subprocess.STDOUT,
                                    timeout=timeout, check=False)
            code = result.returncode
            timed_out = False
        except subprocess.TimeoutExpired:
            code = None
            timed_out = True
        except OSError as error:
            output.write((type(error).__name__ + ': ' + str(error) + '\n').encode())
            code = None
            timed_out = False
    return {'phase': label, 'started_at_utc': started, 'ended_at_utc': utc(),
            'exit_code': code, 'timed_out': timed_out, 'log_sha256': sha(log.read_bytes()),
            'log': log.relative_to(ROOT).as_posix()}


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit('usage: run_installed_fixture.py SELECTION_SHA256 ABSOLUTE_INSTALL_ROOT ABSOLUTE_EMPTY_RESULT_ROOT')
    selected_sha = sys.argv[1]
    if (not isinstance(selected_sha, str) or len(selected_sha) != 64
            or Path(__file__).is_symlink() or SELECTION.is_symlink()
            or INSTALLER.is_symlink()):
        raise ValueError('selected Docker runner control differs')
    selected_raw = SELECTION.read_bytes()
    if sha(selected_raw) != selected_sha:
        raise ValueError('selected Docker runner manifest differs')
    selected = json.loads(selected_raw)
    if selected != {'schema_version': 'lab-T25-installed-fixture-runner-selection/v1',
                    'runner_sha256': sha(Path(__file__).read_bytes()),
                    'installer_sha256': INSTALLER_SHA,
                    'install_manifest_sha256': SELECTED_MANIFEST_SHA,
                    'authority_effect': 'none'} or sha(INSTALLER.read_bytes()) != INSTALLER_SHA:
        raise ValueError('selected installer or Docker runner differs')
    install_root = Path(sys.argv[2])
    result_root = Path(sys.argv[3])
    if not install_root.is_absolute() or '..' in install_root.parts:
        raise ValueError('absolute selected install root required')
    private_empty_root(result_root)
    manifest = install_root / 'runtime/install-manifest.json'
    if sha(manifest.read_bytes()) != SELECTED_MANIFEST_SHA:
        raise ValueError('installed public candidate selection differs')
    fixture = install_root / 'runtime/candidate/fixture'
    if not fixture.is_dir() or fixture.is_symlink():
        raise ValueError('installed fixture context absent')
    nonce = uuid.uuid4().hex
    tag = 'cyberalchemy-lab-local-host:installed-' + nonce
    env = {**os.environ, 'LAB_LOCAL_IMAGE': tag,
           'COMPOSE_PROJECT_NAME': 'cal-installed-' + nonce[:16],
           'LAB_LOCAL_BUILD_CONTEXT': str(fixture)}
    rows = []
    cleanup = None
    started = utc()
    try:
        checks = [
            ('installed-replay', [sys.executable, '-B', str(INSTALLER), 'replay', str(install_root)], 120),
            ('fixture-context', [sys.executable, '-B', str(fixture / VERIFY),
                                 '--verify-context', str(fixture)], 120),
            ('docker-build', ['docker', 'compose', '-f', str(fixture / 'compose.yaml'),
                              'build', '--no-cache', 'lab-fixture'], 900),
            ('chain-fixture', ['docker', 'compose', '-f', str(fixture / 'compose.yaml'),
                               'run', '--rm', '--no-deps', '--pull', 'never', 'chain-fixture'], 600),
            ('lab-fixture', ['docker', 'compose', '-f', str(fixture / 'compose.yaml'),
                             'run', '--rm', '--no-deps', '--pull', 'never', 'lab-fixture'], 600),
        ]
        for label, command, timeout in checks:
            row = run(label, command, result_root / (label + '.log'), env=env, timeout=timeout)
            rows.append(row)
            if row['exit_code'] != 0 or row['timed_out']:
                break
    finally:
        try:
            image = subprocess.run(['docker', 'image', 'inspect', tag],
                                   cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   timeout=30, check=False)
            if image.returncode == 0:
                cleanup = run('image-cleanup', ['docker', 'image', 'rm', '--', tag],
                              result_root / 'image-cleanup.log', env=env, timeout=120)
            else:
                cleanup = {'phase': 'image-cleanup', 'result': 'NO-OWNED-IMAGE'}
        except (OSError, subprocess.TimeoutExpired) as error:
            cleanup = {'phase': 'image-cleanup', 'result': 'UNKNOWN',
                       'error_type': type(error).__name__}
    passed = (len(rows) == 5 and all(row['exit_code'] == 0 and not row['timed_out'] for row in rows)
              and cleanup is not None and cleanup.get('exit_code') == 0
              and not cleanup.get('timed_out', False))
    receipt = {'schema_version': 'lab-T25-installed-public-fixture-docker/v1',
               'result': 'PASS' if passed else 'FAIL',
               'started_at_utc': started, 'ended_at_utc': utc(),
               'install_manifest_sha256': SELECTED_MANIFEST_SHA,
               'runner_selection_sha256': selected_sha,
               'installer_sha256': INSTALLER_SHA,
               'runner_sha256': sha(Path(__file__).read_bytes()),
               'steps': rows, 'image_cleanup': cleanup,
               'original_service_executed': False,
               'portable_api_closure_complete': False,
               'authority_effect': 'none'}
    target = result_root / 'RESULT.json'
    target.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'result': receipt['result'], 'receipt': str(target),
                      'sha256': sha(target.read_bytes())}, sort_keys=True))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
