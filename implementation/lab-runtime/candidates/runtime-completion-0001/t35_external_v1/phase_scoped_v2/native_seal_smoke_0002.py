"""Inert import; versioned disposable empty-input native smoke candidate.

run_and_publish is effect-capable and requires separate exact-byte review.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import stat
import subprocess
import tempfile
import time

from . import native_seal_smoke_0001 as plan
from ..held_paths import HeldCanonicalDirectory

RECEIPT_NAME = 'native-seal-smoke-result-0002.json'
RECEIPT_DIR = plan.REPO / ('docs/plans/0011-lab-runtime-completion/runs/'
                          '0001-execution/runtime-completion-0001/LC-U02-05')
EXPECTED_BWRAP_VERSION = b'bubblewrap 0.11.1\n'
_UNCLOSED_CHILDREN: dict[int, subprocess.Popen] = {}


class Refusal(RuntimeError):
    pass


def require(value: bool, code: str) -> None:
    if not value:
        raise Refusal(code)


def stat_key(info: os.stat_result) -> tuple:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def held_selected(path: Path, expected: tuple[int, int, str]) -> bytes:
    """Capture exact selected bytes through held nofollow regular-file fd."""
    size, mode, digest = expected
    require(path.is_absolute(), 'selected_path_alias')
    with HeldCanonicalDirectory(str(path.parent)) as parent:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW |
                     os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent.fd)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                    before.st_size == size and stat.S_IMODE(before.st_mode) == mode,
                    'selected_metadata')
            raw = bytearray()
            while len(raw) < size:
                chunk = os.read(fd, min(1024 * 1024, size - len(raw)))
                require(bool(chunk), 'selected_truncated')
                raw.extend(chunk)
            after = os.fstat(fd)
            attached = os.stat(path.name, dir_fd=parent.fd, follow_symlinks=False)
            require(stat_key(before) == stat_key(after) == stat_key(attached) and
                    parent.attached() and
                    hashlib.sha256(raw).hexdigest() == digest, 'selected_changed')
            return bytes(raw)
        finally:
            os.close(fd)


def write_exact(path: Path, raw: bytes, mode: int) -> None:
    require(type(raw) is bytes and stat.S_IMODE(mode) == mode, 'scratch_input')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, mode)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, 'wb', closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(fd)
        before = os.fstat(fd)
        attached = path.stat(follow_symlinks=False)
        require(stat_key(before) == stat_key(attached) and
                stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                before.st_size == len(raw) and stat.S_IMODE(before.st_mode) == mode,
                'scratch_detached')
    finally:
        os.close(fd)
    require(held_selected(path, (len(raw), mode, hashlib.sha256(raw).hexdigest())) == raw,
            'scratch_copy_differs')


def capture(root: Path) -> Path:
    require(len(plan.SYNTHETIC_INPUT) == 32 and
            plan.SYNTHETIC_INPUT == b'{"semantic":[],"governance":[]}\n',
            'synthetic_input_selection')
    selected, abi, input_dir = root / 'selected', root / 'selected/abi', root / 'input'
    for directory in (selected, abi, input_dir):
        directory.mkdir(mode=0o700)
    copies = {
        plan.BWRAP: selected / 'bwrap',
        plan.INSTALL / 'bin/lab-context-native-reader': selected / 'native',
    }
    for source in plan.SELECTED:
        if source not in copies:
            copies[source] = abi / source.name
    require(len(copies) == 5 and len(set(copies.values())) == 5,
            'selected_copy_mapping')
    for source, target in copies.items():
        raw = held_selected(source, plan.SELECTED[source])
        mode = 0o500 if source in (plan.BWRAP,
                  plan.INSTALL / 'bin/lab-context-native-reader') else 0o400
        write_exact(target, raw, mode)
    write_exact(input_dir / 'events.json', plan.SYNTHETIC_INPUT, 0o400)
    return selected / 'bwrap'


def held_leader_exited(pid: int) -> bool:
    status = os.waitid(os.P_PID, pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
    return status is not None and status.si_pid == pid


def live_group_members(pgid: int) -> bool:
    with os.scandir('/proc') as entries:
        for entry in entries:
            if not entry.name.isdecimal():
                continue
            try:
                raw = Path('/proc', entry.name, 'stat').read_text()
            except (FileNotFoundError, ProcessLookupError):
                continue
            fields = raw.rsplit(')', 1)[1].split()
            require(len(fields) >= 3, 'group_observation')
            if int(fields[2]) == pgid and fields[0] not in ('Z', 'X', 'x'):
                return True
    return False


def signal_held_group(pid: int) -> None:
    held_leader_exited(pid)
    require(os.getpgid(pid) == pid, 'group_identity')
    os.killpg(pid, signal.SIGKILL)


def wait_held_leader(pid: int, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while not held_leader_exited(pid):
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)
    return True


def wait_group_absent(pid: int) -> bool:
    deadline = time.monotonic() + 2
    while True:
        try:
            os.killpg(pid, 0)  # Observation only; never signal after leader reap.
        except ProcessLookupError:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)


def close_group(process: subprocess.Popen, forced: str | None,
                observed: dict, deadline: float) -> int:
    """Keep leader unreaped until original group has no live members."""
    pid = process.pid
    observed['forced_timeout'] = forced == 'timeout'
    observed['forced_output_limit'] = forced == 'output_limit'
    try:
        if forced is not None:
            observed['forced_cleanup'] = True
            signal_held_group(pid)
        while forced is None and not held_leader_exited(pid):
            if time.monotonic() >= deadline:
                forced = 'timeout'
                observed['forced_cleanup'] = True
                observed['forced_timeout'] = True
                signal_held_group(pid)
                break
            time.sleep(min(0.05, max(0, deadline - time.monotonic())))
        if not wait_held_leader(pid, 2):
            observed['forced_cleanup'] = True
            signal_held_group(pid)
            require(wait_held_leader(pid, 2), 'leader_cleanup')
        if forced is None:
            grace = min(time.monotonic() + 0.5, deadline)
            while live_group_members(pid) and time.monotonic() < grace:
                time.sleep(0.05)
        if live_group_members(pid):
            observed['forced_cleanup'] = True
            signal_held_group(pid)
        drain = time.monotonic() + 2
        while live_group_members(pid) and time.monotonic() < drain:
            time.sleep(0.05)
        require(not live_group_members(pid), 'group_cleanup')
    except BaseException:
        observed['forced_cleanup'] = True
        for _ in range(2):
            try:
                signal_held_group(pid)
            except BaseException:
                pass
            try:
                if not wait_held_leader(pid, 2):
                    continue
                try:
                    live = live_group_members(pid)
                except BaseException:
                    live = True
                if live:
                    continue
                process.wait(timeout=1)
                observed['reaped_observed'] = True
                try:
                    observed['group_absent_observed'] = wait_group_absent(pid)
                except BaseException:
                    pass
                break
            except BaseException:
                if observed['reaped_observed']:
                    break
        if not observed['reaped_observed']:
            _UNCLOSED_CHILDREN[pid] = process
        else:
            _UNCLOSED_CHILDREN.pop(pid, None)
        raise
    rc = process.wait(timeout=1)
    observed['reaped_observed'] = True
    observed['group_absent_observed'] = wait_group_absent(pid)
    require(observed['group_absent_observed'], 'group_not_absent')
    _UNCLOSED_CHILDREN.pop(pid, None)
    return rc


def run_child(argv: list[str], *, timeout: int, observation: dict) -> tuple[int, bytes, bytes]:
    require(type(timeout) is int and 0 < timeout <= plan.CHILD_TIMEOUT_SECONDS and
            type(argv) is list and all(type(arg) is str for arg in argv),
            'child_selection')
    observation.update(launch_attempted=True, leader_started=False,
                       reaped_observed=False, group_absent_observed=False,
                       forced_cleanup=False, forced_timeout=False,
                       forced_output_limit=False)
    deadline = time.monotonic() + timeout
    process = None
    selector = None
    output: dict = {}
    forced = None
    try:
        mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            process = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       start_new_session=True, env={'LC_ALL': 'C'})
            _UNCLOSED_CHILDREN[process.pid] = process
            observation['leader_started'] = True
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, mask)
        output = {process.stdout: bytearray(), process.stderr: bytearray()}
        selector = selectors.DefaultSelector()
        for stream in output:
            selector.register(stream, selectors.EVENT_READ)
        while selector.get_map():
            if time.monotonic() >= deadline:
                forced = 'timeout'
                break
            for event, _ in selector.select(timeout=min(
                    0.1, max(0, deadline - time.monotonic()))):
                chunk = os.read(event.fileobj.fileno(), 257)
                if not chunk:
                    selector.unregister(event.fileobj)
                    continue
                target = output[event.fileobj]
                if len(target) + len(chunk) > 256:
                    forced = 'output_limit'
                    break
                target.extend(chunk)
            if forced is not None:
                break
    finally:
        try:
            if selector is not None:
                selector.close()
        finally:
            if process is not None:
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        try:
                            stream.close()
                        except Exception:
                            pass
                rc = close_group(process, forced, observation, deadline)
    require(observation['reaped_observed'] and observation['group_absent_observed'],
            'child_closure')
    return rc, bytes(output.get(process.stdout, b'')), bytes(output.get(process.stderr, b''))


def scratch_closed(state: dict) -> bool:
    return all(not row.get('launch_attempted') or
               (row.get('reaped_observed') and row.get('group_absent_observed'))
               for row in state['children'].values())


def validate_sandbox_argv(root: Path, argv: list[str]) -> None:
    """Check the only five host paths admitted to the read-only sandbox."""
    expected = {
        (str(root / 'selected/native'), '/work/native'),
        (str(root / 'selected/abi/ld-linux-x86-64.so.2'),
         '/work/abi/ld-linux-x86-64.so.2'),
        (str(root / 'selected/abi/libgcc_s.so.1'),
         '/work/abi/libgcc_s.so.1'),
        (str(root / 'selected/abi/libc.so.6'),
         '/work/abi/libc.so.6'),
        (str(root / 'input/events.json'), '/work/input/events.json'),
    }
    require(type(argv) is list and argv[0] == str(plan.BWRAP) and
            argv.count('--ro-bind') == 5 and '--bind' not in argv and
            '--dev-bind' not in argv and '--unshare-all' in argv and
            '--clearenv' in argv and '--die-with-parent' in argv and
            argv.count('--') == 1, 'sandbox_argv')
    mounts = []
    for index, item in enumerate(argv):
        if item == '--ro-bind':
            require(index + 2 < len(argv), 'sandbox_mount_arity')
            mounts.append((argv[index + 1], argv[index + 2]))
    require(set(mounts) == expected and len(set(mounts)) == 5 and
            not any(part.startswith(('/home/', '/var/lib/', '/run/'))
                    for part in argv), 'sandbox_mount_selection')


def effect(state: dict) -> None:
    state['stage'] = 'scratch'
    root = Path(tempfile.mkdtemp(prefix='lc-u02-05-native-seal-', dir='/tmp'))
    state['scratch_root'] = root
    held = None
    try:
        held = HeldCanonicalDirectory(str(root))
        info = root.stat(follow_symlinks=False)
        require(stat.S_IMODE(info.st_mode) == 0o700 and
                info.st_uid == os.getuid() and stat.S_ISDIR(info.st_mode) and
                held.attached(),
                'scratch_ownership')
        state['stage'] = 'capture'
        bwrap = capture(root)
        require(held.attached(), 'scratch_detached')
        state['stage'] = 'bwrap_version'
        version_obs: dict = {}
        state['children']['bwrap_version'] = version_obs
        rc, out, err = run_child([str(bwrap), '--version'], timeout=5,
                                  observation=version_obs)
        require(held.attached(), 'scratch_detached')
        require(rc == 0 and out == EXPECTED_BWRAP_VERSION and err == b'' and
                not version_obs['forced_cleanup'], 'bwrap_version')
        state['stage'] = 'native_smoke'
        argv = plan.render_argv(root)
        validate_sandbox_argv(root, argv)
        argv[0] = str(bwrap)
        require(held.attached(), 'scratch_detached')
        smoke_obs: dict = {}
        state['children']['native_smoke'] = smoke_obs
        rc, out, err = run_child(argv, timeout=15, observation=smoke_obs)
        require(held.attached(), 'scratch_detached')
        require(plan.check_observation(
            rc, out, err, child_closed=(smoke_obs['reaped_observed'] and
                                        smoke_obs['group_absent_observed']),
            forced_cleanup=smoke_obs['forced_cleanup']), 'native_observation')
        state['stage'] = 'cleanup'
    finally:
        try:
            attached = held is not None and held.attached()
            if attached and scratch_closed(state):
                try:
                    shutil.rmtree(root)
                    state['scratch_cleanup_observed'] = True
                except BaseException:
                    state['scratch_retained_unknown'] = True
                    raise
            else:
                state['scratch_retained_unknown'] = True
        finally:
            if held is not None:
                held.close()
    require(state['scratch_cleanup_observed'] and
            not state['scratch_retained_unknown'], 'scratch_cleanup')
    state['status'] = 'PASS'
    state['stage'] = 'complete'


def receipt(state: dict) -> dict:
    return {
        'schema_version': 'lab-native-seal-smoke-result/v2-candidate',
        'status': state['status'],
        'failure_stage': None if state['status'] == 'PASS' else state['stage'],
        'failure_code': state['failure_code'],
        'selected_leaf_sha256': {str(path): row[2]
                                 for path, row in plan.SELECTED.items()},
        'synthetic_input_sha256': hashlib.sha256(plan.SYNTHETIC_INPUT).hexdigest(),
        'synthetic_input_bytes': 32,
        'bwrap_version_expected': EXPECTED_BWRAP_VERSION.decode().strip(),
        'child_observations': {name: {
            key: bool(row.get(key)) for key in
            ('launch_attempted', 'leader_started', 'reaped_observed',
             'group_absent_observed', 'forced_cleanup', 'forced_timeout',
             'forced_output_limit')} for name, row in state['children'].items()},
        'scratch_cleanup_observed': state['scratch_cleanup_observed'],
        'scratch_retained_unknown': state['scratch_retained_unknown'],
        'retained_scratch': (state['scratch_root'].name
                             if state['scratch_retained_unknown'] else None),
        'raw_diagnostics_published': False,
        'containment_scope': 'observed_process_groups_only',
        'escaped_session_absence_proven': False,
        'authority_effect': 'none',
        'claim_ceiling': 'disposable_empty_native_serialization_only',
        'protected_source8_qualified': False,
        'mapper_package_qualified': False,
        'context_qualified': False,
        'lc_u02_05_accepted': False,
    }


def publish_no_replace(result: dict, destination: Path) -> None:
    require(destination.is_absolute() and destination.name == RECEIPT_NAME and
            destination.parent == RECEIPT_DIR, 'receipt_destination')
    raw = (json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n').encode()
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(fd)
    finally:
        os.close(fd)


def run_and_publish(destination: Path = RECEIPT_DIR / RECEIPT_NAME) -> dict:
    """Effect entry point; do not invoke until independent review clears it."""
    state = {'status': 'FAIL', 'stage': 'preflight', 'failure_code': None,
             'children': {}, 'scratch_root': None,
             'scratch_cleanup_observed': False,
             'scratch_retained_unknown': False}
    try:
        require(destination == RECEIPT_DIR / RECEIPT_NAME and
                not os.path.lexists(destination), 'receipt_preexists')
        effect(state)
    except BaseException as error:
        state['status'] = 'FAIL'
        state['failure_code'] = (str(error) if type(error) is Refusal
                                 else type(error).__name__)
    result = receipt(state)
    publish_no_replace(result, destination)
    return result


def main() -> int:
    return 0 if run_and_publish()['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

