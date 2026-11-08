"""Inactive, pure plan for one disposable native ``seal-fixture`` smoke.

This module never creates scratch, starts Bubblewrap, or executes the native
reader. An effect controller must be independently reviewed before using the
rendered argv. The smoke has no Source8 or production authority.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import stat

REPO = Path(__file__).resolve().parents[6]
INSTALL = (REPO / 'product/lab/release-candidates/v1/interface/'
           'runtime-dependencies-v2-completion-0001/installations/0004')
BWRAP = Path('/usr/bin/bwrap')
SELECTED = {
    BWRAP: (80424, 0o755, '523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6'),
    INSTALL / 'bin/lab-context-native-reader':
        (20243600, 0o755, 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'),
    INSTALL / 'lib/abi/ld-linux-x86-64.so.2':
        (254864, 0o755, 'bda779ea9e9ad234f60315477d7cfd0bdde861cd8ddd9df8cdaf62f18c4cec14'),
    INSTALL / 'lib/abi/libgcc_s.so.1':
        (187120, 0o644, '9d339ecb409578d6a5d587e6c537a8f9589b8a13fefba30d167433a4b5758bee'),
    INSTALL / 'lib/abi/libc.so.6':
        (2190608, 0o644, '85e64f97e348786a8fb4d9f3d52fec289e2fb86bba20f0731dfe61990525e0f7'),
}
SYNTHETIC_INPUT = b'{"semantic":[],"governance":[]}\n'
EXPECTED_STDOUT = SYNTHETIC_INPUT
MAX_INPUT_BYTES = len(SYNTHETIC_INPUT)
MAX_STDOUT_BYTES = 256
MAX_STDERR_BYTES = 256
CHILD_TIMEOUT_SECONDS = 15


def static_preflight() -> dict[str, str]:
    """Read-only byte check; no native invocation or family access."""
    result = {}
    for path, (size, mode, expected_sha) in SELECTED.items():
        info = path.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
                info.st_size != size or stat.S_IMODE(info.st_mode) != mode):
            raise ValueError(f'selected leaf type, link count, size or mode differs: {path}')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected_sha:
            raise ValueError(f'selected leaf digest differs: {path}')
        result[str(path)] = digest
    return result


def render_argv(scratch: Path) -> list[str]:
    """Render only; ``scratch`` is a future owned, absolute, private directory.

    The future effect controller must copy and recheck all selected leaves into
    these exact scratch paths and write SYNTHETIC_INPUT at input/events.json.
    This function intentionally does not claim that preparation happened.
    """
    if (not isinstance(scratch, Path) or not scratch.is_absolute() or
            scratch.parent != Path('/tmp') or
            not scratch.name.startswith('lc-u02-05-native-seal-') or
            '..' in scratch.parts):
        raise ValueError('task-owned /tmp scratch directory required')
    native = scratch / 'selected/native'
    abi = scratch / 'selected/abi'
    events = scratch / 'input/events.json'
    return [
        str(BWRAP), '--die-with-parent', '--unshare-all', '--clearenv',
        '--setenv', 'LC_ALL', 'C',
        '--dir', '/work', '--dir', '/work/abi', '--dir', '/work/input',
        '--ro-bind', str(native), '/work/native',
        '--ro-bind', str(abi / 'ld-linux-x86-64.so.2'), '/work/abi/ld-linux-x86-64.so.2',
        '--ro-bind', str(abi / 'libgcc_s.so.1'), '/work/abi/libgcc_s.so.1',
        '--ro-bind', str(abi / 'libc.so.6'), '/work/abi/libc.so.6',
        '--ro-bind', str(events), '/work/input/events.json',
        '--chdir', '/work', '--',
        '/work/abi/ld-linux-x86-64.so.2', '--inhibit-cache',
        '--library-path', '/work/abi', '/work/native',
        'seal-fixture', '/work/input/events.json',
    ]


def check_observation(returncode: int, stdout: bytes, stderr: bytes,
                      *, child_closed: bool, forced_cleanup: bool) -> bool:
    """A strict candidate-only predicate; it never endorses containment."""
    return (type(returncode) is int and returncode == 0 and
            type(stdout) is bytes and len(stdout) <= MAX_STDOUT_BYTES and
            stdout == EXPECTED_STDOUT and type(stderr) is bytes and
            len(stderr) <= MAX_STDERR_BYTES and stderr == b'' and
            child_closed is True and forced_cleanup is False)
