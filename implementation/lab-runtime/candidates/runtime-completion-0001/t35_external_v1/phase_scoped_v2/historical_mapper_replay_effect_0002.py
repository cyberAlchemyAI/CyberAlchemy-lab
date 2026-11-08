"""Inactive import; one-shot historical Mapper native replay effect candidate.

run_and_publish can execute native code. It requires separate exact-byte review
and effect preflight; import, code_bindings and source_preflight are read-only.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
import hashlib
import json
import os
from pathlib import Path
import secrets
import selectors
import shutil
import signal
import stat
import subprocess
import time

from . import historical_mapper_replay_0001 as plan
from . import native_seal_smoke_0005 as custody
from ..held_paths import HeldCanonicalDirectory, fd_mount_id

ROOT = plan.REPO
EVIDENCE = ROOT / ('docs/plans/0011-lab-runtime-completion/runs/'
                   '0001-execution/runtime-completion-0001/LC-U02-05')
ATTEMPT = 'historical-mapper-replay-attempt-0002.json'
RESULT = 'historical-mapper-replay-result-0002.json'
TEMP_PREFIX = f'.{RESULT}.tmp-'
TEST = ROOT / ('implementation/lab-runtime/candidates/runtime-completion-0001/'
               'tests/LC-U02-05/test_historical_mapper_replay_effect_0002.py')
EXPECTED_CUSTODY_SHA = 'a67e26b0794f17d91774182ac3ec0b4adabca72d37fbe6dd8919ff8a4fc3103c'
EXPECTED_HELD_PATHS_SHA = 'cf09b24ac5cbdc2d3deeda026fbe37564cddbb4c598aff79f55863af800a7bb1'


class Refusal(RuntimeError):
    pass


def require(ok: bool, code: str) -> None:
    if not ok:
        raise Refusal(code)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def code_bindings() -> dict[str, str]:
    from .. import held_paths
    values = {'controller': Path(__file__), 'plan': Path(plan.__file__),
              'custody': Path(custody.__file__),
              'held_paths': Path(held_paths.__file__), 'test': TEST}
    result = {name: sha(path.read_bytes()) for name, path in values.items()}
    require(result['custody'] == EXPECTED_CUSTODY_SHA and
            result['held_paths'] == EXPECTED_HELD_PATHS_SHA,
            'reviewed_custody_dependency_changed')
    return result


def package_rows() -> dict[str, tuple[int, str]]:
    """Bind exact selected names and bytes before any scratch copy."""
    plan.static_preflight()
    rows = {}
    for name in sorted(plan.expected_names()):
        raw = (plan.PACKAGE / name).read_bytes()
        rows[name] = (len(raw), sha(raw))
    inventory = (json.dumps([[name, size, digest]
                             for name, (size, digest) in rows.items()],
                            separators=(',', ':'), ensure_ascii=True) + '\n').encode()
    require(sha(inventory) == plan.PACKAGE_INVENTORY_SHA256,
            'package_selection_changed')
    return rows


def capture(root: Path, rows: dict[str, tuple[int, str]],
            state: dict) -> tuple[Path, dict[Path, tuple[int, int, str]]]:
    """Nofollow copy all 55 package and five runtime leaves into private scratch."""
    for directory in (root / 'selected', root / 'selected/abi',
                      root / 'package', root / 'package/semantic',
                      root / 'package/governance'):
        directory.mkdir(mode=0o700)
    specs = {}
    runtime_targets = {
        plan.BWRAP: root / 'selected/bwrap',
        plan.INSTALL / 'bin/lab-context-native-reader': root / 'selected/native',
    }
    for source in plan.SELECTED_RUNTIME:
        if source not in runtime_targets:
            runtime_targets[source] = root / 'selected/abi' / source.name
    require(len(runtime_targets) == 5 and len(set(runtime_targets.values())) == 5,
            'runtime_copy_mapping')
    for source, target in runtime_targets.items():
        size, original_mode, digest = plan.SELECTED_RUNTIME[source]
        raw = custody.held_selected(source, (size, original_mode, digest))
        mode = (0o500 if source in (plan.BWRAP,
                plan.INSTALL / 'bin/lab-context-native-reader') or
                source.name == 'ld-linux-x86-64.so.2' else 0o400)
        custody.write_exact(target, raw, mode)
        specs[target] = (size, mode, digest)
    for name, (size, digest) in rows.items():
        source, target = plan.PACKAGE / name, root / 'package' / name
        raw = custody.held_selected(source, (size, 0o600, digest))
        custody.write_exact(target, raw, 0o400)
        specs[target] = (size, 0o400, digest)
    require(len(specs) == 60, 'copy_closure')
    for directory in (root / 'package/semantic', root / 'package/governance',
                      root / 'package'):
        directory.chmod(0o500)
    require(package_rows() == rows, 'source_package_changed_after_capture')
    state['copy_inventory_sha256'] = plan.PACKAGE_INVENTORY_SHA256
    state['runtime_copy_sha256'] = {str(path.relative_to(root)): spec[2]
                                    for path, spec in specs.items()
                                    if path.is_relative_to(root / 'selected')}
    return root / 'selected/bwrap', specs


@contextmanager
def watchdog():
    require(signal.SIGALRM not in signal.pthread_sigmask(signal.SIG_BLOCK, set())
            and signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0),
            'watchdog_state')
    previous = signal.getsignal(signal.SIGALRM)
    def expired(_signum, _frame):
        raise TimeoutError('aggregate_watchdog')
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, plan.AGGREGATE_CAP_SECONDS)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def run_child(argv: list[str], *, timeout: int, stdout_cap: int,
              observation: dict) -> tuple[int, bytes, bytes]:
    """Observe fresh leader and original group with two bounded streams."""
    require(type(argv) is list and all(type(item) is str for item in argv) and
            type(timeout) is int and 0 < timeout <= plan.CHILD_TIMEOUT_SECONDS and
            type(stdout_cap) is int and 0 < stdout_cap <= plan.STDOUT_CAP_BYTES,
            'child_selection')
    observation.update(launch_attempted=True, leader_started=False,
                       reaped_observed=False, group_absent_observed=False,
                       forced_cleanup=False, forced_timeout=False,
                       forced_output_limit=False, timeout_seconds=timeout,
                       argv_sha256=sha(json.dumps(argv, separators=(',', ':')).encode()),
                       argv_count=len(argv), exit_code=None,
                       stdout_bytes=None, stderr_bytes=None,
                       stdout_sha256=None, stderr_sha256=None,
                       elapsed_milliseconds=None)
    started = time.monotonic()
    deadline = started + timeout
    process = None
    selector = None
    output = {}
    forced = None
    rc = None
    failure: BaseException | None = None

    def remember(error: BaseException) -> None:
        nonlocal failure, forced
        if failure is None:
            failure = error
        if process is not None and forced is None:
            forced = 'observation_error'

    try:
        mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            process = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       start_new_session=True, env={'LC_ALL': 'C'})
            custody._UNCLOSED_CHILDREN[process.pid] = process
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
                stream = event.fileobj
                limit = stdout_cap if stream is process.stdout else plan.STDERR_CAP_BYTES
                chunk = os.read(stream.fileno(), min(65536, limit + 1 -
                                                    len(output[stream])))
                if not chunk:
                    selector.unregister(stream)
                    continue
                if len(output[stream]) + len(chunk) > limit:
                    forced = 'output_limit'
                    break
                output[stream].extend(chunk)
            if forced is not None:
                break
    except BaseException as error:
        remember(error)
    finally:
        try:
            if selector is not None:
                try:
                    selector.close()
                except BaseException as error:
                    remember(error)
            if process is not None:
                try:
                    stdout = bytes(output.get(process.stdout, b''))
                    stderr = bytes(output.get(process.stderr, b''))
                    observation.update(stdout_bytes=len(stdout), stderr_bytes=len(stderr),
                                       stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))
                except BaseException as error:
                    remember(error)
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        try:
                            stream.close()
                        except BaseException as error:
                            remember(error)
                try:
                    rc = custody.close_group(process, forced, observation, deadline)
                except BaseException as error:
                    remember(error)
        finally:
            observation['elapsed_milliseconds'] = round(
                (time.monotonic() - started) * 1000)
    if failure is not None:
        raise failure
    require(observation['reaped_observed'] and
            observation['group_absent_observed'], 'child_closure')
    observation['exit_code'] = rc
    return rc, bytes(output.get(process.stdout, b'')), bytes(output.get(process.stderr, b''))


def invoke(root: Path, bwrap: Path, specs: dict, rows: dict,
           held: HeldCanonicalDirectory, state: dict) -> None:
    with custody.held_copies(root, specs) as copies:
        def check() -> None:
            require(held.attached(), 'scratch_detached')
            seen = custody.verify_copies(copies)
            require(len(seen) == 60 and package_rows() == rows,
                    'selected_inputs_changed')
        check()
        version = [str(bwrap), '--version']
        state['stage'] = 'bwrap_version'
        row = state['children']['bwrap_version'] = {}
        try:
            rc, out, err = run_child(version, timeout=5, stdout_cap=256,
                                     observation=row)
        finally:
            check()
        require(rc == 0 and out == plan.EXPECTED_BWRAP_VERSION and
                err == b'' and not row['forced_cleanup'], 'bwrap_version')
        argv = list(plan.replay_argv(root))
        plan.validate_replay_argv(root, argv)
        state['argv_sha256'] = sha(json.dumps(argv, separators=(',', ':')).encode())
        outputs = []
        for name in ('replay_1', 'replay_2'):
            state['stage'] = name
            check()
            row = state['children'][name] = {}
            try:
                observed = run_child(argv, timeout=plan.CHILD_TIMEOUT_SECONDS,
                                     stdout_cap=plan.STDOUT_CAP_BYTES,
                                     observation=row)
            finally:
                check()
            require(not row['forced_cleanup'], 'forced_child_cleanup')
            outputs.append(observed)
        plan.validate_replays(outputs[0][1], outputs[1][1],
                              outputs[0][2], outputs[1][2],
                              outputs[0][0], outputs[1][0],
                              first_closed=(state['children']['replay_1']['reaped_observed']
                                            and state['children']['replay_1']['group_absent_observed']),
                              second_closed=(state['children']['replay_2']['reaped_observed']
                                             and state['children']['replay_2']['group_absent_observed']),
                              first_forced=state['children']['replay_1']['forced_cleanup'],
                              second_forced=state['children']['replay_2']['forced_cleanup'])
        check()


def prepare_scratch_cleanup(root: Path, held: HeldCanonicalDirectory) -> None:
    """Restore owner write only after all observed children are closed."""
    require(held.attached(), 'scratch_detached')
    for path in (root / 'package/semantic', root / 'package/governance',
                 root / 'package'):
        if not os.path.lexists(path):
            continue
        with HeldCanonicalDirectory(str(path)) as directory:
            info = os.fstat(directory.fd)
            mount_id = fd_mount_id(directory.fd)
            require(directory.attached() and stat.S_ISDIR(info.st_mode) and
                    info.st_uid == os.getuid() and
                    stat.S_IMODE(info.st_mode) in (0o500, 0o700),
                    'scratch_cleanup_directory')
            os.fchmod(directory.fd, 0o700)
            with HeldCanonicalDirectory(str(path)) as renewed:
                current = os.fstat(directory.fd)
                observed = os.fstat(renewed.fd)
                require(renewed.attached() and
                        (current.st_dev, current.st_ino, current.st_uid,
                         current.st_gid) ==
                        (info.st_dev, info.st_ino, info.st_uid, info.st_gid) ==
                        (observed.st_dev, observed.st_ino, observed.st_uid,
                         observed.st_gid) and
                        stat.S_IMODE(current.st_mode) ==
                        stat.S_IMODE(observed.st_mode) == 0o700 and
                        fd_mount_id(renewed.fd) == mount_id,
                        'scratch_cleanup_directory_detached')
    require(held.attached(), 'scratch_detached')


def effect(state: dict, rows: dict, root: Path) -> None:
    state['stage'] = 'scratch'
    require(root.parent == Path('/tmp') and
            root.name.startswith('lc-u02-05-historical-mapper-replay-') and
            not os.path.lexists(root), 'scratch_preexists')
    root.mkdir(mode=0o700)
    state['scratch_root'] = root
    state['scratch_retained_unknown'] = True
    held = None
    try:
        held = HeldCanonicalDirectory(str(root))
        info = root.lstat()
        require(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700
                and info.st_uid == os.getuid() and held.attached(),
                'scratch_ownership')
        state['stage'] = 'capture'
        bwrap, specs = capture(root, rows, state)
        invoke(root, bwrap, specs, rows, held, state)
        state['stage'] = 'cleanup'
    finally:
        try:
            attached = held is not None and held.attached()
        except BaseException:
            attached = False
        try:
            if attached and custody.scratch_closed(state):
                prepare_scratch_cleanup(root, held)
                shutil.rmtree(root)
                state['scratch_cleanup_observed'] = not os.path.lexists(root)
                if state['scratch_cleanup_observed']:
                    state['scratch_retained_unknown'] = False
        finally:
            if held is not None:
                held.close()
    require(state['scratch_cleanup_observed'] and
            not state['scratch_retained_unknown'], 'scratch_cleanup')
    state['status'] = 'PASS'
    state['stage'] = 'complete'


def validate_pass(state: dict) -> None:
    root = state.get('scratch_root')
    expected_runtime = {
        'selected/bwrap': plan.SELECTED_RUNTIME[plan.BWRAP][2],
        'selected/native': plan.SELECTED_RUNTIME[
            plan.INSTALL / 'bin/lab-context-native-reader'][2],
    }
    for source in plan.SELECTED_RUNTIME:
        if source not in (plan.BWRAP,
                          plan.INSTALL / 'bin/lab-context-native-reader'):
            expected_runtime['selected/abi/' + source.name] = (
                plan.SELECTED_RUNTIME[source][2])
    require(state['status'] == 'PASS' and state['stage'] == 'complete' and
            isinstance(root, Path) and not os.path.lexists(root) and
            state['scratch_cleanup_observed'] and
            not state['scratch_retained_unknown'] and
            state['copy_inventory_sha256'] == plan.PACKAGE_INVENTORY_SHA256 and
            state['runtime_copy_sha256'] == expected_runtime and
            set(state['children']) == {'bwrap_version', 'replay_1', 'replay_2'},
            'pass_state')
    argv = list(plan.replay_argv(root))
    expected_argv_sha = sha(json.dumps(argv, separators=(',', ':')).encode())
    require(state['argv_sha256'] == expected_argv_sha, 'pass_argv')
    for name, timeout, out_size, out_sha in (
            ('bwrap_version', 5, len(plan.EXPECTED_BWRAP_VERSION),
             sha(plan.EXPECTED_BWRAP_VERSION)),
            ('replay_1', plan.CHILD_TIMEOUT_SECONDS,
             plan.EXPECTED_STDOUT_BYTES, plan.EXPECTED_STDOUT_SHA256),
            ('replay_2', plan.CHILD_TIMEOUT_SECONDS,
             plan.EXPECTED_STDOUT_BYTES, plan.EXPECTED_STDOUT_SHA256)):
        row = state['children'][name]
        require(all(row.get(key) is True for key in
                    ('launch_attempted', 'leader_started', 'reaped_observed',
                     'group_absent_observed')) and
                all(row.get(key) is False for key in
                    ('forced_cleanup', 'forced_timeout', 'forced_output_limit')) and
                row.get('timeout_seconds') == timeout and
                row.get('exit_code') == 0 and
                row.get('stdout_bytes') == out_size and
                row.get('stdout_sha256') == out_sha and
                row.get('stderr_bytes') == 0 and
                row.get('stderr_sha256') == sha(b'') and
                row.get('argv_sha256') == (expected_argv_sha if name !=
                    'bwrap_version' else sha(json.dumps(
                        [str(root / 'selected/bwrap'), '--version'],
                        separators=(',', ':')).encode())),
                'pass_child_observation')


def _exists(held: HeldCanonicalDirectory, name: str) -> bool:
    try:
        os.stat(name, dir_fd=held.fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return True


def refuse_temp(held: HeldCanonicalDirectory) -> None:
    require(held.attached(), 'evidence_root_detached')
    with os.scandir(held.fd) as entries:
        require(not any(entry.name.startswith(TEMP_PREFIX) for entry in entries),
                'retained_receipt_temp')
    require(held.attached(), 'evidence_root_detached')


def _json_bytes(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       allow_nan=False) + '\n').encode()


def _write_exclusive(held: HeldCanonicalDirectory, name: str,
                     raw: bytes) -> tuple[int, int]:
    require(0 < len(raw) <= 65536 and held.attached(), 'publication_size_or_root')
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=held.fd)
    try:
        os.fchmod(fd, 0o600)
        offset = 0
        while offset < len(raw):
            written = os.write(fd, raw[offset:])
            require(written > 0, 'publication_write')
            offset += written
        os.fsync(fd)
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                info.st_size == len(raw) and stat.S_IMODE(info.st_mode) == 0o600,
                'publication_identity')
    finally:
        os.close(fd)
    identity = (info.st_dev, info.st_ino)
    custody._readback_leaf(held, name, raw, identity, 1)
    os.fsync(held.fd)
    custody._readback_leaf(held, name, raw, identity, 1)
    return identity


def attempt_bytes(bindings: dict, selected: dict, root: Path) -> bytes:
    argv = list(plan.replay_argv(root))
    version = [str(root / 'selected/bwrap'), '--version']
    return _json_bytes({
        'schema_version': 'lab-historical-mapper-replay-attempt/v1',
        'result_name': RESULT,
        'code_bindings': bindings,
        'selected': selected,
        'argv_contract': 'two_identical_replay_argv_fresh_processes',
        'native_argv_sha256': sha(json.dumps(argv, separators=(',', ':')).encode()),
        'version_argv_sha256': sha(json.dumps(version, separators=(',', ':')).encode()),
        'scratch_name_sha256': sha(root.name.encode()),
        'stdout_cap_bytes': plan.STDOUT_CAP_BYTES,
        'stderr_cap_bytes': plan.STDERR_CAP_BYTES,
        'child_timeout_seconds': plan.CHILD_TIMEOUT_SECONDS,
        'aggregate_cap_seconds': plan.AGGREGATE_CAP_SECONDS,
        'claim_ceiling': 'historical_checked_in_25_event_native_read_only_diagnostic',
    })


def publish_result(held: HeldCanonicalDirectory, result: dict) -> None:
    raw = _json_bytes(result)
    temp = TEMP_PREFIX + secrets.token_hex(16)
    identity = _write_exclusive(held, temp, raw)
    fd = os.open(temp, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                 dir_fd=held.fd)
    try:
        require((os.fstat(fd).st_dev, os.fstat(fd).st_ino) == identity and
                held.attached(), 'receipt_temp_detached')
        os.link(temp, RESULT, src_dir_fd=held.fd, dst_dir_fd=held.fd,
                follow_symlinks=False)
        os.fsync(held.fd)
        custody._readback_leaf(held, RESULT, raw, identity, 2)
    finally:
        os.close(fd)
    os.unlink(temp, dir_fd=held.fd)


def receipt(state: dict) -> dict:
    return {
        'schema_version': 'lab-historical-mapper-replay-result/v1-candidate',
        'status': state['status'],
        'failure_stage': None if state['status'] == 'PASS' else state['stage'],
        'failure_code': state['failure_code'],
        'code_bindings': state.get('code_bindings'),
        'code_bindings_after': state.get('code_bindings_after'),
        'attempt_marker': state.get('attempt_marker'),
        'package_inventory_sha256': state.get('copy_inventory_sha256'),
        'runtime_copy_sha256': state.get('runtime_copy_sha256'),
        'native_argv_sha256': state.get('argv_sha256'),
        'expected_native_stdout_bytes': plan.EXPECTED_STDOUT_BYTES,
        'expected_native_stdout_sha256': plan.EXPECTED_STDOUT_SHA256,
        'children': {name: {key: row.get(key) for key in (
            'launch_attempted', 'leader_started', 'reaped_observed',
            'group_absent_observed', 'forced_cleanup', 'forced_timeout',
            'forced_output_limit', 'timeout_seconds', 'exit_code',
            'elapsed_milliseconds', 'stdout_bytes', 'stderr_bytes',
            'stdout_sha256', 'stderr_sha256', 'argv_sha256', 'argv_count')}
            for name, row in state['children'].items()},
        'aggregate_elapsed_milliseconds': state.get('aggregate_elapsed_milliseconds'),
        'scratch_cleanup_observed': state['scratch_cleanup_observed'],
        'scratch_retained_unknown': state['scratch_retained_unknown'],
        'retained_scratch': (state['scratch_root'].name
                             if state['scratch_retained_unknown'] and
                             state['scratch_root'] else None),
        'raw_diagnostics_published': False,
        'containment_scope': 'observed_process_groups_only',
        'escaped_session_absence_proven': False,
        'authority_effect': 'none',
        'claim_ceiling': 'historical_checked_in_25_event_native_read_only_diagnostic',
        'fresh_same_scratch_mapper_qualified': False,
        'protected_source8_qualified': False,
        'lc_u02_05_accepted': False,
    }


def run_and_publish(destination: Path = EVIDENCE / RESULT) -> dict:
    """Effect entry point: NEVER call without independent review and preflight."""
    require(destination == EVIDENCE / RESULT, 'receipt_destination')
    state = {'status': 'FAIL', 'stage': 'preflight', 'failure_code': None,
             'children': {}, 'scratch_root': None,
             'scratch_cleanup_observed': False,
             'scratch_retained_unknown': False}
    with custody.controller_scope() as held:
        require(held.path == EVIDENCE and held.attached() and
                not _exists(held, ATTEMPT) and not _exists(held, RESULT),
                'attempt_or_result_preexists')
        refuse_temp(held)
        bindings = code_bindings()
        selected = plan.static_preflight()
        rows = package_rows()
        state['code_bindings'] = bindings
        root = Path('/tmp/lc-u02-05-historical-mapper-replay-' +
                    secrets.token_hex(16))
        require(not os.path.lexists(root), 'scratch_preexists')
        marker_raw = attempt_bytes(bindings, selected, root)
        marker_identity = _write_exclusive(held, ATTEMPT, marker_raw)
        state['attempt_marker'] = {'name': ATTEMPT, 'sha256': sha(marker_raw),
                                   'size_bytes': len(marker_raw)}
        started = time.monotonic()
        try:
            with watchdog():
                effect(state, rows, root)
            require(code_bindings() == bindings, 'controller_bytes_changed')
            validate_pass(state)
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
        if state['code_bindings_after'] != bindings:
            state['status'] = 'FAIL'
            state['failure_code'] = 'controller_bytes_changed'
        state['aggregate_elapsed_milliseconds'] = round(
            (time.monotonic() - started) * 1000)
        require(held.attached(), 'evidence_root_detached')
        custody._readback_leaf(held, ATTEMPT, marker_raw, marker_identity, 1)
        refuse_temp(held)
        result = receipt(state)
        publish_result(held, result)
        return result


def main() -> int:
    return 0 if run_and_publish()['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
