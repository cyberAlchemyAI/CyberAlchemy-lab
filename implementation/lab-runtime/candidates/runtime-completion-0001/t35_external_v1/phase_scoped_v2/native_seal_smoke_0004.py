"""Inert import; versioned disposable empty-input native smoke candidate.

run_and_publish is effect-capable and requires separate exact-byte review.
"""
from __future__ import annotations

import hashlib
from contextlib import ExitStack, contextmanager
import fcntl
import json
import os
from pathlib import Path
import selectors
import secrets
import shutil
import signal
import stat
import subprocess
import tempfile
import time

from . import native_seal_smoke_0001 as plan
from ..held_paths import HeldCanonicalDirectory

RECEIPT_NAME = 'native-seal-smoke-result-0004.json'
RECEIPT_DIR = plan.REPO / ('docs/plans/0011-lab-runtime-completion/runs/'
                          '0001-execution/runtime-completion-0001/LC-U02-05')
EXPECTED_BWRAP_VERSION = b'bubblewrap 0.11.1\n'
AGGREGATE_CAP_SECONDS = 45
TEST_FILE = (plan.REPO / 'implementation/lab-runtime/candidates/'
             'runtime-completion-0001/tests/LC-U02-05/'
             'test_native_seal_smoke_0004.py')
_UNCLOSED_CHILDREN: dict[int, subprocess.Popen] = {}


class Refusal(RuntimeError):
    pass


def require(value: bool, code: str) -> None:
    if not value:
        raise Refusal(code)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_bindings() -> dict[str, str]:
    return {'controller_sha256': file_sha(Path(__file__)),
            'plan_sha256': file_sha(Path(plan.__file__)),
            'test_sha256': file_sha(TEST_FILE)}


@contextmanager
def wall_watchdog():
    require(signal.SIGALRM not in signal.pthread_sigmask(signal.SIG_BLOCK, set())
            and signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0),
            'watchdog_state')
    previous = signal.getsignal(signal.SIGALRM)
    def expired(_signum, _frame):
        raise TimeoutError('effect watchdog')
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, AGGREGATE_CAP_SECONDS)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


@contextmanager
def controller_scope():
    """Serialize cooperating effects under one held evidence-root identity."""
    with HeldCanonicalDirectory(str(RECEIPT_DIR)) as held:
        require(held.attached(), 'evidence_root_detached')
        try:
            fcntl.flock(held.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Refusal('controller_busy') from error
        try:
            require(held.attached(), 'evidence_root_detached')
            yield held
        finally:
            attached = held.attached()
            fcntl.flock(held.fd, fcntl.LOCK_UN)
            require(attached, 'evidence_root_detached')


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


def capture(root: Path, state: dict | None = None) -> Path:
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
        if state is not None:
            state.setdefault('selected_capture_sha256', {})[str(source)] = (
                hashlib.sha256(raw).hexdigest())
        mode = 0o500 if (source in (plan.BWRAP,
                  plan.INSTALL / 'bin/lab-context-native-reader') or
                  source.name == 'ld-linux-x86-64.so.2') else 0o400
        write_exact(target, raw, mode)
    write_exact(input_dir / 'events.json', plan.SYNTHETIC_INPUT, 0o400)
    return selected / 'bwrap'


def copy_specs(root: Path) -> dict[Path, tuple[int, int, str]]:
    result = {
        root / 'selected/bwrap':
            (plan.SELECTED[plan.BWRAP][0], 0o500,
             plan.SELECTED[plan.BWRAP][2]),
        root / 'selected/native':
            (plan.SELECTED[plan.INSTALL / 'bin/lab-context-native-reader'][0],
             0o500,
             plan.SELECTED[plan.INSTALL / 'bin/lab-context-native-reader'][2]),
        root / 'input/events.json':
            (32, 0o400, hashlib.sha256(plan.SYNTHETIC_INPUT).hexdigest()),
    }
    for source in plan.SELECTED:
        if source in (plan.BWRAP,
                      plan.INSTALL / 'bin/lab-context-native-reader'):
            continue
        result[root / 'selected/abi' / source.name] = (
            plan.SELECTED[source][0],
            0o500 if source.name == 'ld-linux-x86-64.so.2' else 0o400,
            plan.SELECTED[source][2])
    require(len(result) == 6, 'copy_selection')
    return result


@contextmanager
def held_copies(root: Path, specs: dict[Path, tuple[int, int, str]] | None = None):
    """Keep nested directory and leaf identities across both child launches."""
    specs = copy_specs(root) if specs is None else specs
    with ExitStack() as stack:
        parents = {}
        rows = {}
        for path, expected in specs.items():
            if path.parent not in parents:
                parents[path.parent] = stack.enter_context(
                    HeldCanonicalDirectory(str(path.parent)))
            parent = parents[path.parent]
            fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW |
                         os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent.fd)
            stack.callback(os.close, fd)
            rows[path] = (parent, fd, stat_key(os.fstat(fd)), expected)
        verify_copies(rows)
        yield rows


def verify_copies(rows: dict) -> dict[str, str]:
    digests = {}
    for path, (parent, fd, initial, expected) in rows.items():
        size, mode, digest = expected
        before = os.fstat(fd)
        attached = os.stat(path.name, dir_fd=parent.fd, follow_symlinks=False)
        require(parent.attached() and stat_key(before) == initial ==
                stat_key(attached) and stat.S_ISREG(before.st_mode) and
                before.st_nlink == 1 and before.st_size == size and
                stat.S_IMODE(before.st_mode) == mode, 'scratch_copy_identity')
        hashed = hashlib.sha256()
        offset = 0
        while offset < size:
            chunk = os.pread(fd, min(1024 * 1024, size - offset), offset)
            require(bool(chunk), 'scratch_copy_truncated')
            hashed.update(chunk)
            offset += len(chunk)
        require(stat_key(os.fstat(fd)) == initial and parent.attached() and
                hashed.hexdigest() == digest, 'scratch_copy_changed')
        digests[str(path)] = digest
    return digests


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
                       forced_output_limit=False, timeout_seconds=timeout,
                       exit_code=None, elapsed_milliseconds=None,
                       stdout_bytes=None, stderr_bytes=None,
                       stdout_sha256=None, stderr_sha256=None,
                       argv_sha256=hashlib.sha256(
                           json.dumps(argv, separators=(',', ':')).encode()
                       ).hexdigest(), argv_count=len(argv))
    started = time.monotonic()
    deadline = started + timeout
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
            try:
                if selector is not None:
                    selector.close()
            finally:
                if process is not None:
                    stdout = bytes(output.get(process.stdout, b''))
                    stderr = bytes(output.get(process.stderr, b''))
                    observation.update(
                        stdout_bytes=len(stdout), stderr_bytes=len(stderr),
                        stdout_sha256=hashlib.sha256(stdout).hexdigest(),
                        stderr_sha256=hashlib.sha256(stderr).hexdigest())
                    for stream in (process.stdout, process.stderr):
                        if stream is not None:
                            try:
                                stream.close()
                            except Exception:
                                pass
                    rc = close_group(process, forced, observation, deadline)
        finally:
            observation['elapsed_milliseconds'] = round(
                (time.monotonic() - started) * 1000)
    require(observation['reaped_observed'] and observation['group_absent_observed'],
            'child_closure')
    stdout = bytes(output.get(process.stdout, b''))
    stderr = bytes(output.get(process.stderr, b''))
    observation['exit_code'] = rc
    return rc, stdout, stderr


def scratch_closed(state: dict) -> bool:
    return all(not row.get('launch_attempted') or
               (row.get('reaped_observed') and row.get('group_absent_observed'))
               for row in state['children'].values())


def expected_sandbox_argv(root: Path, bwrap: Path) -> list[str]:
    """Independent exact vector; no extra Bubblewrap operation is admissible."""
    return [
        str(bwrap), '--die-with-parent', '--unshare-all', '--clearenv',
        '--setenv', 'LC_ALL', 'C',
        '--dir', '/work', '--dir', '/work/abi', '--dir', '/work/input',
        '--ro-bind', str(root / 'selected/native'), '/work/native',
        '--ro-bind', str(root / 'selected/abi/ld-linux-x86-64.so.2'),
        '/work/abi/ld-linux-x86-64.so.2',
        '--ro-bind', str(root / 'selected/abi/libgcc_s.so.1'),
        '/work/abi/libgcc_s.so.1',
        '--ro-bind', str(root / 'selected/abi/libc.so.6'),
        '/work/abi/libc.so.6',
        '--ro-bind', str(root / 'input/events.json'),
        '/work/input/events.json',
        '--chdir', '/work', '--',
        '/work/abi/ld-linux-x86-64.so.2', '--inhibit-cache',
        '--library-path', '/work/abi', '/work/native',
        'seal-fixture', '/work/input/events.json',
    ]


def validate_sandbox_argv(root: Path, argv: list[str], bwrap: Path) -> None:
    require(type(argv) is list and argv == expected_sandbox_argv(root, bwrap),
            'sandbox_argv')


def invoke_children(root: Path, bwrap: Path, held: HeldCanonicalDirectory,
                    state: dict) -> None:
    with held_copies(root) as copies:
        def check_copies() -> None:
            require(held.attached(), 'scratch_detached')
            seen = verify_copies(copies)
            state['copy_sha256'] = {
                str(Path(path).relative_to(root)): digest
                for path, digest in seen.items()}
        check_copies()
        state['stage'] = 'bwrap_version'
        version_argv = [str(bwrap), '--version']
        state['version_argv'] = version_argv
        version_obs: dict = {}
        state['children']['bwrap_version'] = version_obs
        check_copies()
        try:
            rc, out, err = run_child(version_argv, timeout=5,
                                     observation=version_obs)
        finally:
            check_copies()
        require(rc == 0 and out == EXPECTED_BWRAP_VERSION and err == b'' and
                not version_obs['forced_cleanup'], 'bwrap_version')
        state['stage'] = 'native_smoke'
        argv = plan.render_argv(root)
        require(argv[0] == str(plan.BWRAP), 'plan_argv')
        argv[0] = str(bwrap)
        validate_sandbox_argv(root, argv, bwrap)
        state['native_argv'] = list(argv)
        smoke_obs: dict = {}
        state['children']['native_smoke'] = smoke_obs
        check_copies()
        try:
            rc, out, err = run_child(argv, timeout=15, observation=smoke_obs)
        finally:
            check_copies()
        require(plan.check_observation(
            rc, out, err, child_closed=(smoke_obs['reaped_observed'] and
                                        smoke_obs['group_absent_observed']),
            forced_cleanup=smoke_obs['forced_cleanup']), 'native_observation')


def effect(state: dict) -> None:
    state['stage'] = 'scratch'
    root = Path(tempfile.mkdtemp(prefix='lc-u02-05-native-seal-', dir='/tmp'))
    state['scratch_root'] = root
    state['scratch_retained_unknown'] = True
    held = None
    try:
        held = HeldCanonicalDirectory(str(root))
        info = root.stat(follow_symlinks=False)
        require(stat.S_IMODE(info.st_mode) == 0o700 and
                info.st_uid == os.getuid() and stat.S_ISDIR(info.st_mode) and
                held.attached(),
                'scratch_ownership')
        state['stage'] = 'capture'
        bwrap = capture(root, state)
        require(held.attached(), 'scratch_detached')
        invoke_children(root, bwrap, held, state)
        state['stage'] = 'cleanup'
    finally:
        try:
            try:
                attached = held is not None and held.attached()
            except BaseException:
                attached = False
            if attached and scratch_closed(state):
                try:
                    shutil.rmtree(root)
                    state['scratch_cleanup_observed'] = not os.path.lexists(root)
                    if state['scratch_cleanup_observed']:
                        state['scratch_retained_unknown'] = False
                except BaseException:
                    raise
        finally:
            if held is not None:
                held.close()
    require(state['scratch_cleanup_observed'] and
            not state['scratch_retained_unknown'], 'scratch_cleanup')
    state['status'] = 'PASS'
    state['stage'] = 'complete'


def validate_pass_state(state: dict) -> None:
    """Second, closed check of every field that a PASS receipt will publish."""
    root = state.get('scratch_root')
    require(state.get('status') == 'PASS' and state.get('stage') == 'complete' and
            isinstance(root, Path) and
            state.get('scratch_cleanup_observed') is True and
            state.get('scratch_retained_unknown') is False and
            not os.path.lexists(root), 'pass_cleanup')
    expected_copies = {
        str(path.relative_to(root)): row[2]
        for path, row in copy_specs(root).items()}
    require(state.get('copy_sha256') == expected_copies,
            'pass_copy_bindings')
    require(state.get('selected_capture_sha256') ==
            {str(path): row[2] for path, row in plan.SELECTED.items()},
            'pass_selected_capture')
    bwrap = root / 'selected/bwrap'
    version_argv = [str(bwrap), '--version']
    native_argv = expected_sandbox_argv(root, bwrap)
    require(state.get('version_argv') == version_argv and
            state.get('native_argv') == native_argv and
            set(state.get('children', {})) == {'bwrap_version', 'native_smoke'},
            'pass_argv_bindings')
    empty_sha = hashlib.sha256(b'').hexdigest()
    for name, argv, timeout, stdout in (
            ('bwrap_version', version_argv, 5, EXPECTED_BWRAP_VERSION),
            ('native_smoke', native_argv, 15, plan.EXPECTED_STDOUT)):
        row = state['children'][name]
        require(all(row.get(key) is True for key in
                    ('launch_attempted', 'leader_started',
                     'reaped_observed', 'group_absent_observed')) and
                all(row.get(key) is False for key in
                    ('forced_cleanup', 'forced_timeout',
                     'forced_output_limit')) and
                row.get('timeout_seconds') == timeout and
                type(row.get('exit_code')) is int and row['exit_code'] == 0 and
                type(row.get('elapsed_milliseconds')) is int and
                0 <= row['elapsed_milliseconds'] <= (timeout + 5) * 1000 and
                row.get('stdout_bytes') == len(stdout) and
                row.get('stderr_bytes') == 0 and
                row.get('stdout_sha256') == hashlib.sha256(stdout).hexdigest() and
                row.get('stderr_sha256') == empty_sha and
                row.get('argv_count') == len(argv) and
                row.get('argv_sha256') == hashlib.sha256(
                    json.dumps(argv, separators=(',', ':')).encode()
                ).hexdigest(), 'pass_child_observation')


def receipt(state: dict) -> dict:
    return {
        'schema_version': 'lab-native-seal-smoke-result/v4-candidate',
        'status': state['status'],
        'failure_stage': None if state['status'] == 'PASS' else state['stage'],
        'failure_code': state['failure_code'],
        'code_bindings': state.get('code_bindings'),
        'code_bindings_after': state.get('code_bindings_after'),
        'expected_selected_leaf_sha256': {str(path): row[2]
                                          for path, row in plan.SELECTED.items()},
        'selected_capture_sha256': state.get('selected_capture_sha256'),
        'scratch_copy_sha256': state.get('copy_sha256'),
        'synthetic_input_sha256': hashlib.sha256(plan.SYNTHETIC_INPUT).hexdigest(),
        'synthetic_input_bytes': 32,
        'bwrap_version_expected': EXPECTED_BWRAP_VERSION.decode().strip(),
        'version_argv_actual': state.get('version_argv'),
        'native_argv_actual': state.get('native_argv'),
        'aggregate_cap_seconds': AGGREGATE_CAP_SECONDS,
        'aggregate_elapsed_milliseconds': state.get('aggregate_elapsed_milliseconds'),
        'child_observations': {name: {
            **{key: bool(row.get(key)) for key in
            ('launch_attempted', 'leader_started', 'reaped_observed',
             'group_absent_observed', 'forced_cleanup', 'forced_timeout',
             'forced_output_limit')},
            **{key: row.get(key) for key in
               ('timeout_seconds', 'exit_code', 'elapsed_milliseconds',
                'stdout_bytes', 'stderr_bytes', 'stdout_sha256',
                'stderr_sha256', 'argv_sha256', 'argv_count')}}
            for name, row in state['children'].items()},
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


def _readback_leaf(held: HeldCanonicalDirectory, name: str, raw: bytes,
                   identity: tuple[int, int], links: int) -> None:
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                 dir_fd=held.fd)
    try:
        before = os.fstat(fd)
        attached = os.stat(name, dir_fd=held.fd, follow_symlinks=False)
        require(held.attached() and stat_key(before) == stat_key(attached) and
                stat.S_ISREG(before.st_mode) and before.st_nlink == links and
                stat.S_IMODE(before.st_mode) == 0o600 and
                before.st_size == len(raw) and
                (before.st_dev, before.st_ino) == identity,
                'receipt_leaf_identity')
        readback = bytearray()
        while len(readback) <= len(raw):
            part = os.read(fd, min(4096, len(raw) + 1 - len(readback)))
            if not part:
                break
            readback.extend(part)
        require(bytes(readback) == raw and
                stat_key(os.fstat(fd)) == stat_key(before) and
                held.attached(), 'receipt_readback')
    finally:
        os.close(fd)


def publish_no_replace(result: dict, destination: Path,
                       held: HeldCanonicalDirectory) -> None:
    """Stage fully verified bytes, then atomically link the canonical name."""
    require(destination.is_absolute() and destination.name == RECEIPT_NAME and
            destination.parent == RECEIPT_DIR and
            held.path == RECEIPT_DIR and held.attached(),
            'receipt_destination')
    raw = (json.dumps(result, sort_keys=True, separators=(',', ':'),
                      allow_nan=False) + '\n').encode()
    require(0 < len(raw) <= 64 * 1024, 'receipt_size')
    temp_name = f'.{RECEIPT_NAME}.tmp-{secrets.token_hex(16)}'
    fd = os.open(temp_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=held.fd)
    try:
        written = 0
        while written < len(raw):
            amount = os.write(fd, raw[written:])
            require(amount > 0, 'receipt_write')
            written += amount
        os.fsync(fd)
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                info.st_size == len(raw) and
                stat.S_IMODE(info.st_mode) == 0o600 and held.attached(),
                'receipt_temp_identity')
    finally:
        os.close(fd)
    identity = (info.st_dev, info.st_ino)
    temp_hold = os.open(temp_name, os.O_RDONLY | os.O_NOFOLLOW |
                        os.O_CLOEXEC, dir_fd=held.fd)
    try:
        require(stat_key(os.fstat(temp_hold)) == stat_key(info) and
                held.attached(), 'receipt_temp_detached')
        _readback_leaf(held, temp_name, raw, identity, 1)
        require(stat_key(os.fstat(temp_hold)) == stat_key(info) and
                held.attached(), 'receipt_temp_detached')
        # link(2) fails with EEXIST and never replaces an occupied final leaf.
        os.link(temp_name, RECEIPT_NAME, src_dir_fd=held.fd,
                dst_dir_fd=held.fd, follow_symlinks=False)
        os.fsync(held.fd)
        _readback_leaf(held, RECEIPT_NAME, raw, identity, 2)
    finally:
        os.close(temp_hold)
    # The final link is durable and verified. All fallible close/readback work
    # has finished; unlink only the owned temp name, never the final name.
    os.unlink(temp_name, dir_fd=held.fd)


def run_and_publish(destination: Path = RECEIPT_DIR / RECEIPT_NAME) -> dict:
    """Effect entry point; do not invoke until independent review clears it."""
    state = {'status': 'FAIL', 'stage': 'preflight', 'failure_code': None,
             'children': {}, 'scratch_root': None,
             'scratch_cleanup_observed': False,
             'scratch_retained_unknown': False}
    require(destination == RECEIPT_DIR / RECEIPT_NAME,
            'receipt_destination')
    with controller_scope() as held:
        require(held.attached() and not os.path.lexists(destination),
                'receipt_preexists')
        state['code_bindings'] = code_bindings()
        started = time.monotonic()
        try:
            with wall_watchdog():
                effect(state)
            require(code_bindings() == state['code_bindings'],
                    'controller_bytes_changed')
            validate_pass_state(state)
        except BaseException as error:
            state['status'] = 'FAIL'
            state['failure_code'] = (
                str(error) if type(error) is Refusal else
                'WATCHDOG_EXHAUSTED' if type(error) is TimeoutError else
                'UNEXPECTED_EXCEPTION')
        try:
            state['code_bindings_after'] = code_bindings()
        except BaseException:
            state['code_bindings_after'] = None
        if state['code_bindings_after'] != state['code_bindings']:
            state['status'] = 'FAIL'
            state['failure_code'] = 'controller_bytes_changed'
        state['aggregate_elapsed_milliseconds'] = round(
            (time.monotonic() - started) * 1000)
        require(held.attached(), 'evidence_root_detached')
        result = receipt(state)
        publish_no_replace(result, destination, held)
        return result


def main() -> int:
    return 0 if run_and_publish()['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

