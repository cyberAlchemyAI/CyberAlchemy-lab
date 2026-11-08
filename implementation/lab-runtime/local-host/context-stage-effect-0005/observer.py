"""External OS-exit observer; records one terminal receipt with no rerun."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

CONTROLLER = Path(__file__).with_name('controller.py').resolve()
MAX_OUTPUT = 1024 * 1024


def observe(receipt, argv, *, timeout=180, fixture=False):
    receipt = Path(receipt)
    if not receipt.is_absolute() or receipt.parent.name.startswith('cal-context-stage-fixture-') is False:
        raise ValueError('disposable fixture receipt root required; real observer disabled')
    if len(argv) != 4 or argv[:3] != [sys.executable, '-B', str(CONTROLLER)] or \
            argv[3] not in ('--preflight-public', '--real-stage'):
        raise ValueError('closed controller argv required')
    if argv[3] == '--real-stage':
        raise ValueError('real stage observation disabled pending effect review')
    if receipt.exists():
        raise FileExistsError('terminal receipt already exists')
    start = time.time_ns()
    try:
        run = subprocess.run(argv, capture_output=True, timeout=timeout, check=False)
        status = 'OS_EXIT_OBSERVED'
        exit_code = run.returncode
        stdout = run.stdout; stderr = run.stderr
    except subprocess.TimeoutExpired as exc:
        status = 'TIMEOUT_UNKNOWN_CHILD_EFFECT'
        exit_code = None
        stdout = exc.stdout or b''; stderr = exc.stderr or b''
    end = time.time_ns()
    receipt_data = {
        'schema_version': 'lab-context-stage-external-os-observation/v1-candidate',
        'status': status, 'argv': argv, 'os_exit_code': exit_code,
        'started_ns': start, 'ended_ns': end,
        'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
        'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
        'stdout_size': len(stdout), 'stderr_size': len(stderr),
        'stdout_bounded': len(stdout) <= MAX_OUTPUT,
        'stderr_bounded': len(stderr) <= MAX_OUTPUT,
        'real_effect': 'DISABLED', 'protected_body': 'UNOPENED',
        'context_launch': 'REFUSED',
    }
    raw = (json.dumps(receipt_data, sort_keys=True, separators=(',', ':')) + '\n').encode()
    fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
                 os.O_CLOEXEC, 0o600)
    primary = None
    try:
        view = memoryview(raw)
        while view:
            count = os.write(fd, view)
            if count <= 0:
                raise OSError('terminal receipt write stalled')
            view = view[count:]
        os.fsync(fd)
    except BaseException as exc:
        primary = exc
    try:
        os.close(fd)  # One close attempt; no retry after ambiguous release.
    except BaseException as exc:
        raise RuntimeError('terminal receipt close uncertain') from (primary or exc)
    if primary:
        raise RuntimeError('terminal receipt write uncertain') from primary
    parent = os.open(receipt.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                     os.O_CLOEXEC)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)
    return receipt_data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: observer.py ABSOLUTE_DISPOSABLE_RECEIPT_PATH')
    record = observe(sys.argv[1], [sys.executable, '-B', str(CONTROLLER),
                                   '--preflight-public'])
    print(json.dumps({'status': record['status'], 'exit': record['os_exit_code'],
                      'receipt': sys.argv[1]}, sort_keys=True))
