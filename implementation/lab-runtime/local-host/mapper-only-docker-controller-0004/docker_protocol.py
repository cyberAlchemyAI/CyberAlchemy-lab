"""Closed, durable Mapper Docker one-shot protocol; inert until release."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import stat
from contextlib import contextmanager

CID_RE = re.compile(r'[0-9a-f]{64}\Z')
NAME_RE = re.compile(r'cal-mapper-only-[a-z0-9-]+\Z')


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def exact_create_argv(args: list[str], label: str) -> None:
    """Recompute from pinned selection; forbid duplicate/extra switches."""
    import controller
    expected = controller.docker_create_argv(controller.trusted_selection(), label=label)
    require(type(args) is list and
            all(type(token) is str for token in args) and
            args == expected and len(args) > 30 and
            args[:2] == ['/usr/bin/docker', 'create'],
            'Docker create vector differs from exact selected vector')


def bounded_error(error: BaseException) -> dict:
    result = {'type': type(error).__name__, 'message': str(error)[:1000]}
    if isinstance(error, DockerCommandError):
        result.update(command=error.command, returncode=error.returncode,
                      stderr_sha256=hashlib.sha256(error.stderr).hexdigest(),
                      stderr_excerpt=error.stderr[:1000].decode('utf-8', errors='replace'))
    return result


class EvidenceAttachmentUnknown(RuntimeError):
    def __init__(self, path: Path, expected_sha256: str, cause: BaseException):
        self.overall = 'UNKNOWN'
        self.selected_path = str(path)
        self.expected_sha256 = expected_sha256
        self.cause = cause
        super().__init__('UNKNOWN evidence pathname attachment: ' + str(path) +
                         '; cause: ' + str(cause))


def directory_identity(info: os.stat_result) -> tuple[int, int, int, int, int]:
    """Attachment plus custody for each directory in the selected path."""
    require(stat.S_ISDIR(info.st_mode), 'evidence ancestor is not a directory')
    return (info.st_dev, info.st_ino, info.st_uid, info.st_gid,
            stat.S_IMODE(info.st_mode))


def private_evidence_parent(info: os.stat_result) -> None:
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
            info.st_gid == os.getgid() and stat.S_IMODE(info.st_mode) == 0o700,
            'evidence directory owner/group/mode differs')


@contextmanager
def held_evidence_parent(path: Path):
    require(path.is_absolute() and '..' not in path.parts and
            path.name not in ('', '.', '..'), 'evidence path differs')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    opened = [os.open('/', flags)]
    try:
        for component in path.parent.parts[1:]:
            opened.append(os.open(component, flags, dir_fd=opened[-1]))
        before = [directory_identity(os.fstat(fd)) for fd in opened]
        parent_info = os.fstat(opened[-1])
        private_evidence_parent(parent_info)
        yield opened[-1], tuple(before)
        require(before == [directory_identity(os.fstat(fd)) for fd in opened],
                'evidence held ancestor custody changed')
        private_evidence_parent(os.fstat(opened[-1]))
    finally:
        for fd in reversed(opened):
            os.close(fd)


def verify_evidence_path(path: Path,
                         expected_chain: tuple[tuple[int, int, int, int, int], ...],
                         written: os.stat_result, raw: bytes) -> None:
    """Fresh no-follow path rewalk after the held writer has closed."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    opened = [os.open('/', flags)]
    try:
        require(directory_identity(os.fstat(opened[0])) == expected_chain[0],
                'evidence root pathname custody changed')
        for index, component in enumerate(path.parent.parts[1:], 1):
            opened.append(os.open(component, flags, dir_fd=opened[-1]))
            observed_dir = os.fstat(opened[-1])
            require(directory_identity(observed_dir) == expected_chain[index],
                    'evidence ancestor pathname custody changed: ' + component)
        require(len(opened) == len(expected_chain),
                'evidence ancestor count differs')
        parent = opened[-1]
        private_evidence_parent(os.fstat(parent))
        before_leaf = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        required_leaf = (written.st_dev, written.st_ino, written.st_mode,
                         written.st_uid, written.st_gid, written.st_nlink,
                         written.st_size, written.st_mtime_ns, written.st_ctime_ns)
        def identity(info):
            return (info.st_dev, info.st_ino, info.st_mode, info.st_uid,
                    info.st_gid, info.st_nlink, info.st_size,
                    info.st_mtime_ns, info.st_ctime_ns)
        require(stat.S_ISREG(before_leaf.st_mode) and
                identity(before_leaf) == required_leaf,
                'evidence selected leaf pathname detached')
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=parent)
        try:
            require(identity(os.fstat(fd)) == required_leaf,
                    'evidence selected leaf changed on open')
            actual = bytearray()
            while len(actual) < len(raw):
                chunk = os.read(fd, len(raw) - len(actual))
                require(bool(chunk), 'evidence selected leaf shortened')
                actual.extend(chunk)
            require(os.read(fd, 1) == b'' and bytes(actual) == raw and
                    hashlib.sha256(actual).digest() == hashlib.sha256(raw).digest() and
                    identity(os.fstat(fd)) == required_leaf and
                    identity(os.stat(path.name, dir_fd=parent,
                                     follow_symlinks=False)) == required_leaf,
                    'evidence selected leaf readback differs')
            require(tuple(directory_identity(os.fstat(item)) for item in opened) ==
                    expected_chain, 'evidence rewalk custody changed during readback')
            private_evidence_parent(os.fstat(parent))
        finally:
            os.close(fd)
        # A rename during leaf readback can leave all held descriptors valid.
        # Make one last fresh pathname attachment check before returning.
        final_attachment(path, expected_chain, required_leaf)
    finally:
        for fd in reversed(opened):
            os.close(fd)


def final_attachment(path: Path,
                     expected_chain: tuple[tuple[int, int, int, int, int], ...],
                     required_leaf: tuple[int, ...]) -> None:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    opened = [os.open('/', flags)]
    try:
        require(directory_identity(os.fstat(opened[0])) == expected_chain[0],
                'evidence final root custody changed')
        for index, component in enumerate(path.parent.parts[1:], 1):
            opened.append(os.open(component, flags, dir_fd=opened[-1]))
            require(directory_identity(os.fstat(opened[-1])) ==
                    expected_chain[index],
                    'evidence final ancestor custody changed: ' + component)
        require(len(opened) == len(expected_chain),
                'evidence final ancestor count differs')
        private_evidence_parent(os.fstat(opened[-1]))
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                       dir_fd=opened[-1])
        try:
            info = os.fstat(leaf)
            observed = (info.st_dev, info.st_ino, info.st_mode,
                        info.st_uid, info.st_gid, info.st_nlink, info.st_size,
                        info.st_mtime_ns, info.st_ctime_ns)
            require(stat.S_ISREG(info.st_mode) and observed == required_leaf,
                    'evidence final leaf custody changed')
        finally:
            os.close(leaf)
    finally:
        for fd in reversed(opened):
            os.close(fd)


def durable_json(path: Path, value: dict) -> dict:
    raw = (json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode()
    require(len(raw) <= 64 * 1024 and path.is_absolute(),
            'one-shot evidence path or size differs')
    digest = hashlib.sha256(raw).hexdigest()
    try:
        with held_evidence_parent(path) as (parent, chain):
            fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent)
            try:
                os.fchmod(fd, 0o600)
                view = memoryview(raw)
                while view:
                    count = os.write(fd, view)
                    require(count > 0, 'one-shot evidence write stalled')
                    view = view[count:]
                os.fsync(fd)
                written = os.fstat(fd)
                require(stat.S_ISREG(written.st_mode) and
                        written.st_uid == os.getuid() and
                        written.st_gid == os.getgid() and
                        written.st_nlink == 1 and written.st_size == len(raw) and
                        stat.S_IMODE(written.st_mode) == 0o600,
                        'one-shot evidence inode differs')
                readback = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW |
                                   os.O_CLOEXEC, dir_fd=parent)
                try:
                    observed = os.fstat(readback)
                    actual = bytearray()
                    while len(actual) < len(raw):
                        chunk = os.read(readback, len(raw) - len(actual))
                        require(bool(chunk), 'one-shot evidence readback shortened')
                        actual.extend(chunk)
                    require((observed.st_dev, observed.st_ino) ==
                            (written.st_dev, written.st_ino) and
                            bytes(actual) == raw and os.read(readback, 1) == b'',
                            'one-shot evidence readback differs')
                finally:
                    os.close(readback)
                os.fsync(parent)
            finally:
                os.close(fd)
        verify_evidence_path(path, chain, written, raw)
    except Exception as error:
        if isinstance(error, EvidenceAttachmentUnknown):
            raise
        raise EvidenceAttachmentUnknown(path, digest, error) from error
    return {'path': path, 'chain': chain, 'written': written, 'raw': raw,
            'sha256': digest}


def verify_evidence_anchor(anchor: dict) -> None:
    try:
        verify_evidence_path(anchor['path'], anchor['chain'],
                             anchor['written'], anchor['raw'])
    except Exception as error:
        raise EvidenceAttachmentUnknown(anchor['path'], anchor['sha256'],
                                        error) from error


class DockerCommandError(RuntimeError):
    def __init__(self, command: list[str], returncode: int, stderr: bytes):
        self.command = command[:]
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f'Docker command failed: {command[1]} exit={returncode}')


class OneShotUnknown(RuntimeError):
    def __init__(self, evidence: dict, primary: BaseException,
                 cleanup: BaseException | None):
        self.evidence = evidence
        self.primary = primary
        self.cleanup = cleanup
        super().__init__('Mapper one-shot UNKNOWN: ' + str(primary) +
                         ('; cleanup unresolved: ' + str(cleanup) if cleanup else ''))
        if cleanup is not None:
            self.add_note('Secondary cleanup failure retained: ' + repr(cleanup))


def exact_owned(obj: dict, *, cid: str | None, name: str,
                image: str, label: str) -> str:
    require(isinstance(obj, dict) and
            isinstance(obj.get('Id'), str) and CID_RE.fullmatch(obj['Id']) is not None and
            (cid is None or obj['Id'] == cid) and obj.get('Name') == '/' + name and
            obj.get('Image') == image and
            obj.get('Config', {}).get('Image') == image and
            obj.get('Config', {}).get('Labels', {}).get('cal.mapper.attempt') == label,
            'Docker container ID/name/nonce/image ownership differs')
    return obj['Id']


def object_identity(obj: dict) -> dict:
    require(isinstance(obj, dict), 'Docker observed object type differs')
    config = obj.get('Config') if isinstance(obj.get('Config'), dict) else {}
    labels = config.get('Labels') if isinstance(config.get('Labels'), dict) else {}
    def bounded(value):
        return str(value)[:256] if value is not None else None
    return {'id': bounded(obj.get('Id')), 'name': bounded(obj.get('Name')),
            'image': bounded(obj.get('Image')),
            'config_image': bounded(config.get('Image')),
            'nonce': bounded(labels.get('cal.mapper.attempt'))}


def reconcile_once(driver, args: list[str], *,
                   image: str, label: str, name: str, evidence_dir: Path,
                   clock=time.monotonic) -> dict:
    """One create, no retry; recover only an exactly owned ambiguous object."""
    exact_create_argv(args, label)
    require(NAME_RE.fullmatch(name) is not None and
            len(label) == 32 and all(c in '0123456789abcdef' for c in label) and
            args[args.index('--name') + 1] == name and
            args[args.index('--label') + 1] == 'cal.mapper.attempt=' + label and
            args[args.index('--entrypoint') + 2] == image and
            evidence_dir.is_absolute() and evidence_dir.is_dir(),
            'selected one-shot identity/evidence differs')
    started = clock()
    deadline = started + 180
    recovery_deadline = deadline + 30
    base = {'schema_version': 'lab-mapper-docker-one-shot-evidence/v2',
            'name': name, 'nonce': label, 'image': image,
            'create_argv_sha256': hashlib.sha256(('\0'.join(args)).encode()).hexdigest(),
            'deadline_seconds': 180, 'recovery_seconds': 30}
    precreate_anchor = durable_json(evidence_dir / 'precreate.json',
                                    {**base, 'phase': 'BEFORE_CREATE',
                                     'effect': 'NOT_STARTED'})
    cid = None
    primary = None
    cleanup_error = None
    result = None
    create_attempted = False
    exact_ownership = False
    cleanup_attempted = False
    absent_proved = False
    observed_object = None

    def within(end: float) -> float:
        require(end - clock() > 0, 'Mapper one-shot monotonic deadline elapsed')
        return end

    try:
        initial = driver.lookup_name(name, deadline=within(deadline))
        observed_object = [object_identity(item) for item in initial]
        require(initial == [],
                'selected Docker name already occupied')
        create_attempted = True
        candidate = driver.create(args, deadline=within(deadline))
        require(isinstance(candidate, str) and CID_RE.fullmatch(candidate) is not None,
                'Docker create returned malformed CID')
        cid = candidate
        before = driver.inspect(cid, deadline=within(deadline))
        exact_owned(before, cid=cid, name=name, image=image, label=label)
        exact_ownership = True
        require(before['State']['Status'] == 'created',
                'selected container did not start from created state')
        client_exit = driver.start_wait(cid, deadline=within(deadline))
        after = driver.inspect(cid, deadline=within(deadline))
        exact_owned(after, cid=cid, name=name, image=image, label=label)
        require(client_exit == 0 and after['State']['Status'] == 'exited' and
                after['State']['ExitCode'] == 0,
                'Mapper client/daemon result differs')
        result = {'client_exit': 0, 'daemon_exit': 0,
                  'daemon_exit_consistent': True, 'container_id': cid}
    except Exception as error:
        primary = error

    # Create may have reached the daemon even when its client timed out.
    if create_attempted and not exact_ownership:
        try:
            found = driver.lookup_name(name, deadline=within(recovery_deadline))
            observed_object = [object_identity(item) for item in found]
            require(len(found) == 1, 'ambiguous create has no unique named object')
            cid = exact_owned(found[0], cid=cid, name=name,
                              image=image, label=label)
            exact_ownership = True
        except Exception as recovery_error:
            cleanup_error = recovery_error

    if exact_ownership and cid is not None:
        try:
            cleanup_attempted = True
            driver.remove(cid, force=primary is not None,
                          deadline=within(recovery_deadline))
            require(driver.absent(cid, deadline=within(recovery_deadline)),
                    'Docker ID absence unproved')
            require(driver.lookup_name(name, deadline=within(recovery_deadline)) == [],
                    'Docker name absence unproved')
            absent_proved = True
        except Exception as error:
            cleanup_error = error if cleanup_error is None else ExceptionGroup(
                'multiple cleanup failures', [cleanup_error, error])

    def write_terminal(value: dict) -> None:
        try:
            durable_json(evidence_dir / 'terminal.json', value)
            verify_evidence_anchor(precreate_anchor)
        except Exception as evidence_error:
            unknown = {**value, 'overall': 'UNKNOWN',
                       'terminal_attachment': 'UNKNOWN',
                       'precreate_path': str(precreate_anchor['path']),
                       'precreate_sha256': precreate_anchor['sha256'],
                       'evidence_error': bounded_error(evidence_error),
                       'retry_allowed': False}
            original = primary if primary is not None else evidence_error
            secondary = evidence_error if primary is not None else None
            if cleanup_error is not None:
                secondary = cleanup_error if secondary is None else ExceptionGroup(
                    'cleanup and evidence failures', [cleanup_error, secondary])
            raise OneShotUnknown(unknown, original, secondary) from evidence_error

    if primary is None and cleanup_error is None and result is not None and absent_proved:
        terminal = {**base, **result, 'phase': 'TERMINAL', 'overall': 'PASS',
                    'cleanup': 'PASS', 'container_absent': True,
                    'forced_cleanup': False, 'create_attempted': True}
        write_terminal(terminal)
        return terminal
    if primary is None:
        primary = ValueError('Mapper one-shot did not reach PASS')
    terminal = {**base, 'phase': 'TERMINAL', 'overall': 'UNKNOWN',
                'container_id': cid, 'create_attempted': create_attempted,
                'exact_ownership': exact_ownership,
                'cleanup_attempted': cleanup_attempted,
                'container_absent': absent_proved,
                'observed_object': observed_object,
                'primary_error': bounded_error(primary),
                'cleanup_error': bounded_error(cleanup_error) if cleanup_error else None,
                'retry_allowed': False}
    write_terminal(terminal)
    raise OneShotUnknown(terminal, primary, cleanup_error) from primary


class SubprocessDocker:
    """Future release adapter; absent rejects transport and daemon failure."""

    @staticmethod
    def _run(args: list[str], *, deadline: float) -> subprocess.CompletedProcess:
        require(args and args[0] == '/usr/bin/docker', 'Docker executable differs')
        timeout = deadline - time.monotonic()
        require(timeout > 0, 'Docker global deadline elapsed')
        result = subprocess.run(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=timeout, check=False)
        require(len(result.stdout) <= 1024 * 1024 and
                len(result.stderr) <= 1024 * 1024,
                'Docker command output exceeds bound')
        return result

    def _ok(self, args: list[str], *, deadline: float) -> bytes:
        result = self._run(args, deadline=deadline)
        if result.returncode != 0:
            raise DockerCommandError(args, result.returncode, result.stderr)
        return result.stdout

    def create(self, args: list[str], *, deadline: float) -> str:
        return self._ok(args, deadline=deadline).decode('ascii').strip()

    def inspect(self, cid: str, *, deadline: float) -> dict:
        raw = self._ok(['/usr/bin/docker', 'inspect', '--type', 'container', cid],
                       deadline=deadline)
        value = json.loads(raw)
        require(isinstance(value, list) and len(value) == 1,
                'Docker inspect cardinality differs')
        return value[0]

    def lookup_name(self, name: str, *, deadline: float) -> list[dict]:
        require(NAME_RE.fullmatch(name) is not None, 'Docker lookup name differs')
        raw = self._ok(['/usr/bin/docker', 'ps', '-a', '--no-trunc',
                        '--filter', 'name=^' + name + '$', '--format', '{{.ID}}'],
                       deadline=deadline)
        ids = raw.decode('ascii').splitlines()
        require(len(ids) <= 2 and len(ids) == len(set(ids)) and
                all(CID_RE.fullmatch(value) is not None for value in ids),
                'Docker exact name enumeration differs')
        return [value for cid in ids if (value := self.inspect(cid, deadline=deadline))
                .get('Name') == '/' + name]

    def start_wait(self, cid: str, *, deadline: float) -> int:
        self._ok(['/usr/bin/docker', 'start', cid], deadline=deadline)
        raw = self._ok(['/usr/bin/docker', 'wait', cid], deadline=deadline)
        token = raw.decode('ascii').strip()
        require(token.isdecimal(), 'Docker wait result differs')
        return int(token)

    def remove(self, cid: str, *, force: bool, deadline: float) -> None:
        self._ok(['/usr/bin/docker', 'rm', *(['--force'] if force else []), cid],
                 deadline=deadline)

    def absent(self, cid: str, *, deadline: float) -> bool:
        require(CID_RE.fullmatch(cid) is not None, 'Docker absence CID differs')
        args = ['/usr/bin/docker', 'inspect', '--type', 'container', cid]
        result = self._run(args, deadline=deadline)
        if result.returncode == 0:
            return False
        exact = {('Error: No such container: ' + cid + '\n').encode(),
                 ('Error: No such object: ' + cid + '\n').encode()}
        if result.returncode == 1 and result.stdout == b'' and result.stderr in exact:
            return True
        raise DockerCommandError(args, result.returncode, result.stderr)
