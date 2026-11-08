"""One-shot image load probe of the exact public native ELF; no Source data."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = REPO / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/bin/lab-context-native-reader'
EXPECTED_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
PROBE = Path('/tmp/cal-mapper-native-load-probe-20261020-0001')
NAME = 'cal-mapper-native-load-probe-20261020-0001'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> dict:
    if os.path.lexists(PROBE):
        raise ValueError('native probe attempt already consumed')
    PROBE.mkdir(mode=0o700)
    folder = PROBE / 'input'
    folder.mkdir(mode=0o700)
    target = folder / 'lab-context-native-reader'
    fd_in = os.open(SOURCE, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    fd_out = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o700)
    hasher = hashlib.sha256()
    try:
        while True:
            chunk = os.read(fd_in, 1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
            os.write(fd_out, chunk)
        os.fchmod(fd_out, 0o755)
        os.fsync(fd_out)
    finally:
        os.close(fd_in)
        os.close(fd_out)
    if hasher.hexdigest() != EXPECTED_SHA or sha(target.read_bytes()) != EXPECTED_SHA:
        raise ValueError('selected native ELF copy changed')
    args = ['docker', 'run', '--rm', '--name', NAME, '--user', '1000:1000',
            '--userns', 'host', '--network', 'none', '--read-only', '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges:true', '--pids-limit', '1',
            '--mount', f'type=bind,src={folder},dst=/attempt/input,readonly',
            '--tmpfs', '/attempt/scratch:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000',
            '-e', 'TMPDIR=/attempt/scratch', '--entrypoint',
            '/attempt/input/lab-context-native-reader', IMAGE, '--help']
    try:
        result = subprocess.run(args, capture_output=True, timeout=20)
        code, stdout, stderr, timeout = result.returncode, result.stdout, result.stderr, False
    except subprocess.TimeoutExpired as error:
        code, stdout, stderr, timeout = None, error.stdout or b'', error.stderr or b'', True
    ps = subprocess.run(['docker', 'ps', '-a', '--filter', f'name=^{NAME}$',
                         '--format', '{{.ID}}'], capture_output=True, timeout=10)
    absent = ps.returncode == 0 and not ps.stdout.strip()
    # The CLI may reject --help; a loaded ELF returns its own usage/refusal.
    combined = (stdout + b'\n' + stderr).lower()
    loaded = (not timeout and code not in (None, 125, 126, 127) and
              b'error while loading shared libraries' not in combined and
              b'exec format error' not in combined and absent)
    receipt = {'schema_version': 'lab-mapper-native-image-load-probe/v1',
               'result': 'PASS_LOAD_ONLY' if loaded else 'UNKNOWN_LOAD',
               'image': IMAGE, 'native_sha256': EXPECTED_SHA,
               'effective_user': '1000:1000', 'userns': 'host',
               'docker_exit': code, 'container_absent': absent, 'timeout': timeout,
               'stdout_sha256': sha(stdout), 'stderr_sha256': sha(stderr),
               'stdout_size': len(stdout), 'stderr_size': len(stderr),
               'private_source_mounted': False, 'mapper_effect': False}
    (PROBE / 'receipt.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))
    return receipt


if __name__ == '__main__':
    value = main()
    raise SystemExit(0 if value['result'] == 'PASS_LOAD_ONLY' else 2)
