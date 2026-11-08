"""Effect-disabled Context transport prototype. Only explicitly owned synthetic attempts."""
import array
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import stat
import struct
import threading
import time

EFFECT_ENABLED = False
CLAIM = 'Actual historical construction delivery at its recorded expiry; later use must revalidate current source, host permission and expiry.'
LEAVES = ('request.json', 'authentication-proof.json', 'trusted-context.json',
          'host-permission-public.json', *(f'artifacts/{i:02d}.json' for i in range(30)),
          'artifact-index.json', 'delivery.json', 'lesson-selection.json',
          'delivery-provenance.json', 'build-result.json', 'manifest.json')
MAX_LEAF = 65536
MAX_PACKET = 100000
MAX_TOTAL = 2 * 1024 * 1024


class Unknown(RuntimeError):
    """A fixed-code terminal refusal. The attempt is never reusable."""


def need(ok, code):
    if not ok:
        raise Unknown(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def parse(raw, canonical=True):
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'DUPLICATE_KEY')
            result[key] = value
        return result
    try:
        def constant(_):
            raise Unknown('NONFINITE_JSON')
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
        if canonical:
            need(encode(value) == raw, 'NONCANONICAL_JSON')
        return value
    except (ValueError, TypeError, UnicodeError):
        raise Unknown('JSON') from None


def hex64(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def close_all(fds):
    """One attempt per owned descriptor; never retry an ambiguous numeric FD."""
    failed = False
    for fd in reversed(fds):
        try:
            os.close(fd)
        except BaseException:
            failed = True
    need(not failed, 'CLOSE_UNCERTAIN')


def identity(info):
    return info.st_dev, info.st_ino, info.st_uid, info.st_gid


def file_identity(info):
    return identity(info) + (info.st_mode, info.st_nlink, info.st_size,
                             info.st_mtime_ns, info.st_ctime_ns)


def chain(path):
    need(type(path) is Path or isinstance(path, Path), 'PATH')
    need(path.is_absolute() and str(path) == os.path.normpath(str(path)), 'PATH')
    fds = []
    try:
        fds.append(os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC))
        for part in path.parts[1:]:
            fds.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                               os.O_CLOEXEC, dir_fd=fds[-1]))
        return fds
    except BaseException:
        try:
            close_all(fds)
        except BaseException:
            pass
        raise


def read_leaf(directory_fd, leaf, expected):
    fd = os.open(leaf, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                 dir_fd=directory_fd)
    error = None
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.geteuid() and before.st_gid == os.getegid() and
             stat.S_IMODE(before.st_mode) == 0o444 and before.st_size <= MAX_LEAF,
             'LEAF_CUSTODY')
        raw = bytearray()
        while len(raw) <= before.st_size:
            part = os.read(fd, before.st_size + 1 - len(raw))
            if not part:
                break
            raw.extend(part)
        after = os.fstat(fd)
        need(file_identity(before) == file_identity(after) and
             len(raw) == before.st_size and sha(raw) == expected,
             'READBACK')
        result = bytes(raw)
    except BaseException as exc:
        error = exc
    try:
        close_all([fd])
    except BaseException as exc:
        error = error or exc
    if error is not None:
        raise error
    return result


def inventory_fd(fd, expected):
    # Incremental bounded enumeration, no recursion or adoption.
    names = set()
    with os.scandir(fd) as entries:
        for entry in entries:
            names.add(entry.name)
            need(len(names) <= len(expected), 'EXTRA_ENTRY')
    need(names == set(expected), 'INVENTORY')


class Writer:
    """Owns one no-replace attempt and its synthetic private directory.

    No actual policy/key is provisioned. The future policy adapter is not installed.
    Read-only file modes are observations, not protection against this same UID.
    """
    def __init__(self, attempt, source_binding, deadline):
        self.path = Path(attempt)
        self.out = self.path / 'package'
        self.private = self.path / 'private'
        self.deadline = deadline
        self.state = 'OPEN'
        self.rows = []
        self.digests = {}
        self.total = 0
        self.released = False
        self.trace = []
        self.fds = []
        need(type(source_binding) is dict and set(source_binding) == {'path', 'sha256'} and
             type(source_binding['path']) is str and 0 < len(source_binding['path']) <= 4096 and
             hex64(source_binding['sha256']), 'SOURCE_BINDING')
        self.source = dict(source_binding)
        need(type(deadline) is float and math.isfinite(deadline) and
             0 < deadline - time.monotonic() <= 30, 'DEADLINE')
        need(os.getuid() == os.geteuid() and os.getgid() == os.getegid(), 'IDENTITY')
        try:
            self.fds = chain(self.path.parent)
            parent = self.fds[-1]
            os.mkdir(self.path.name, 0o700, dir_fd=parent)  # consumes attempt forever
            self.fds.append(os.open(self.path.name, os.O_RDONLY | os.O_DIRECTORY |
                                    os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent))
            self.attempt_fd = self.fds[-1]
            os.fchmod(self.attempt_fd, 0o700)
            os.fsync(self.attempt_fd)
            os.fsync(parent)
            self.attempt_id = identity(os.fstat(self.attempt_fd))
            for name in ('package', 'private'):
                os.mkdir(name, 0o700, dir_fd=self.attempt_fd)
                fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                             os.O_CLOEXEC, dir_fd=self.attempt_fd)
                self.fds.append(fd)
                os.fchmod(fd, 0o700)
                os.fsync(fd)
                if name == 'package':
                    self.package_fd = fd
                    self.package_id = identity(os.fstat(fd))
                else:
                    self.private_fd = fd
                    self.private_id = identity(os.fstat(fd))
            os.fsync(self.attempt_fd)
            os.mkdir('artifacts', 0o700, dir_fd=self.package_fd)
            fd = os.open('artifacts', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                         os.O_CLOEXEC, dir_fd=self.package_fd)
            self.fds.append(fd)
            self.artifacts_fd = fd
            self.artifacts_id = identity(os.fstat(fd))
            os.fchmod(fd, 0o700)
            os.fsync(fd)
            os.fsync(self.package_fd)
            self.check()
        except BaseException:
            self.abort()
            raise

    def check(self):
        need(self.state == 'OPEN' and time.monotonic() < self.deadline, 'WRITER_DEADLINE_STATE')
        current = chain(self.path)
        try:
            need(identity(os.fstat(current[-1])) == self.attempt_id, 'ATTACHMENT')
            need(identity(os.stat('package', dir_fd=current[-1], follow_symlinks=False)) ==
                 self.package_id, 'PACKAGE_ATTACHMENT')
            need(identity(os.stat('artifacts', dir_fd=self.package_fd, follow_symlinks=False)) ==
                 self.artifacts_id, 'ARTIFACT_ATTACHMENT')
        finally:
            close_all(current)

    def slot(self, name):
        return (self.artifacts_fd, name.split('/')[1]) if '/' in name else (self.package_fd, name)

    def emit(self, name, raw):
        try:
            self.check()
            index = len(self.rows)
            need(index < 40 and name == LEAVES[index] and type(raw) is bytes and
                 len(raw) <= MAX_LEAF and self.total + len(raw) <= MAX_TOTAL, 'LEAF_ORDER_BUDGET')
            need(index < 38 or self.released, 'PRIVATE_NOT_RELEASED')
            if index == 39:
                self.validate_manifest(raw)
            directory, leaf = self.slot(name)
            fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
                         os.O_CLOEXEC, 0o600, dir_fd=directory)
            error = None
            try:
                need(stat.S_ISREG(os.fstat(fd).st_mode) and os.fstat(fd).st_nlink == 1,
                     'CREATED_LEAF')
                offset = 0
                while offset < len(raw):
                    self.check()
                    count = os.write(fd, raw[offset:])
                    need(count > 0, 'WRITE_ZERO')
                    offset += count
                os.fchmod(fd, 0o444)
                os.fsync(fd)
                self.trace.append(('FILE_FSYNC', name))
            except BaseException as exc:
                error = exc
            try:
                close_all([fd])
            except BaseException as exc:
                error = error or exc
            if error:
                raise error
            digest = sha(raw)
            need(read_leaf(directory, leaf, digest) == raw, 'WRITE_READBACK')
            os.fsync(directory)
            self.check()
            self.trace.append(('NAME_FSYNC_READBACK', name))
            self.rows.append({'path': str(self.out / name), 'sha256': digest})
            self.digests[name] = digest
            self.total += len(raw)
        except BaseException:
            self.abort()
            raise

    def release_private(self):
        try:
            self.check()
            need(len(self.rows) == 38 and not self.released, 'RELEASE_ORDER')
            need(identity(os.stat('private', dir_fd=self.attempt_fd, follow_symlinks=False)) ==
                 self.private_id, 'PRIVATE_ATTACHMENT')
            inventory_fd(self.private_fd, ())
            fd = self.private_fd
            self.fds.remove(fd)  # consume ownership before ambiguous close
            close_all([fd])
            os.rmdir('private', dir_fd=self.attempt_fd)
            os.fsync(self.attempt_fd)
            need(not os.path.lexists(self.private), 'PRIVATE_REMAINS')
            self.released = True
            self.trace.append(('PRIVATE_RELEASED', 38))
        except BaseException:
            self.abort()
            raise

    def validate_manifest(self, raw):
        value = parse(raw, canonical=False)  # retain original encoded() bytes unchanged
        expected = {'schema_version': 'lab-actual-context-delivery-package/v1-candidate',
                    'files': sorted(self.rows[:39], key=lambda row: row['path']),
                    'source_manifest_binding': self.source, 'authority_effect': 'none',
                    'actual_owner_outcome': None,
                    'delivery_binding': self.rows[LEAVES.index('delivery.json')],
                    'provenance_binding': self.rows[LEAVES.index('delivery-provenance.json')],
                    'claim_ceiling': CLAIM}
        need(len(self.rows) >= 39 and value == expected, 'MANIFEST')

    def validate_inventory(self):
        self.check()
        need(len(self.rows) == 40 and self.released and not os.path.lexists(self.private),
             'FINISH_STATE')
        inventory_fd(self.attempt_fd, ('package',))
        inventory_fd(self.package_fd, [n for n in LEAVES if '/' not in n] + ['artifacts'])
        inventory_fd(self.artifacts_fd, [f'{i:02d}.json' for i in range(30)])
        for name in LEAVES:
            directory, leaf = self.slot(name)
            raw = read_leaf(directory, leaf, self.digests[name])
            if name == 'manifest.json':
                self.validate_manifest(raw)
        self.check()
        return sha(encode(self.rows))

    def postclose(self):
        """Reopen named originals read-only; all audit handles close before ACK."""
        audit = []
        error = None
        try:
            audit = chain(self.path)
            need(identity(os.fstat(audit[-1])) == self.attempt_id, 'POSTCLOSE_ATTACHMENT')
            need(not os.path.lexists(self.private), 'POSTCLOSE_PRIVATE')
            inventory_fd(audit[-1], ('package',))
            p = os.open('package', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                        os.O_CLOEXEC, dir_fd=audit[-1])
            audit.append(p)
            need(identity(os.fstat(p)) == self.package_id, 'POSTCLOSE_PACKAGE')
            a = os.open('artifacts', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                        os.O_CLOEXEC, dir_fd=p)
            audit.append(a)
            need(identity(os.fstat(a)) == self.artifacts_id, 'POSTCLOSE_ARTIFACTS')
            inventory_fd(p, [n for n in LEAVES if '/' not in n] + ['artifacts'])
            inventory_fd(a, [f'{i:02d}.json' for i in range(30)])
            for name in LEAVES:
                need(time.monotonic() < self.deadline, 'POSTCLOSE_DEADLINE')
                read_leaf(a if '/' in name else p, name.split('/')[-1], self.digests[name])
        except BaseException as exc:
            error = exc
        try:
            close_all(audit)
        except BaseException as exc:
            error = error or exc
        if error:
            raise error
        # Bounded final name observation; no exclusion of a later same-UID race.
        need(identity(os.stat(self.path, follow_symlinks=False)) == self.attempt_id and
             identity(os.stat(self.out, follow_symlinks=False)) == self.package_id and
             not os.path.lexists(self.private),
             'POSTCLOSE_FINAL_ATTACHMENT')
        self.trace.append(('POSTCLOSE_READBACK', len(self.rows)))

    def finish(self):
        try:
            digest = self.validate_inventory()
            os.fchmod(self.artifacts_fd, 0o500)
            os.fchmod(self.package_fd, 0o500)
            os.fsync(self.artifacts_fd)
            os.fsync(self.package_fd)
            owned, self.fds = self.fds, []
            close_all(owned)
            self.state = 'CLOSED'
            self.trace.append(('WRITER_CLOSED', digest))
            self.postclose()
            need(time.monotonic() < self.deadline, 'FINISH_DEADLINE')
            return digest
        except BaseException:
            self.abort()
            raise

    def abort(self):
        self.state = 'UNKNOWN'
        owned, self.fds = self.fds, []
        try:
            close_all(owned)
        except BaseException:
            self.trace.append(('CLOSE_UNCERTAIN', len(owned)))
        # Original bytes/directories stay retained, never reset/deleted.


def credentials():
    return os.getpid(), os.getuid(), os.getgid()


def configure(sock):
    need(sock.family == socket.AF_UNIX and sock.type == socket.SOCK_SEQPACKET, 'SOCKET')
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)


def transport_selection(peer, token, deadline):
    need(type(peer) is tuple and len(peer) == 3 and
         all(type(v) is int for v in peer) and peer[0] > 0 and
         all(0 <= v < 2**32 - 1 for v in peer[1:]), 'PEER_SELECTION')
    need(type(token) is str and len(token) == 32 and
         all(c in '0123456789abcdef' for c in token), 'ATTEMPT_TOKEN')
    need(type(deadline) is float and math.isfinite(deadline) and
         0 < deadline - time.monotonic() <= 30, 'TRANSPORT_SELECTION_DEADLINE')


def remaining(sock, deadline):
    left = deadline - time.monotonic()
    need(left > 0, 'TRANSPORT_DEADLINE')
    sock.settimeout(left)


def receive(sock, peer, deadline, eof=False):
    remaining(sock, deadline)
    data, ancillary, flags, _ = sock.recvmsg(MAX_PACKET + 1, socket.CMSG_SPACE(64),
                                            socket.MSG_CMSG_CLOEXEC)
    rights = []
    observed = []
    bad = False
    for level, kind, raw in ancillary:
        if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
            values = array.array('i')
            values.frombytes(raw[:len(raw) - len(raw) % values.itemsize])
            rights.extend(values)
            bad = True
        elif level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS and len(raw) == 12:
            observed.append(struct.unpack('3i', raw))
        else:
            bad = True
    close_all(rights)
    need(not bad and not flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC), 'ANCILLARY_OR_TRUNCATION')
    if eof and not data and not ancillary:
        return None
    need(0 < len(data) <= MAX_PACKET and observed == [peer], 'FRAME_PEER_SIZE')
    return data


def send(sock, raw, deadline):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_PACKET, 'SEND_SIZE')
    remaining(sock, deadline)
    need(sock.send(raw) == len(raw), 'SEND_PARTIAL')


REQUEST_KEYS = {'v', 'attempt', 'seq', 'op', 'ordinal', 'leaf', 'sha256', 'payload'}


class Mediator:
    def __init__(self, sock, peer, token, writer):
        transport_selection(peer, token, writer.deadline)
        configure(sock)
        self.sock, self.peer, self.token, self.writer = sock, peer, token, writer
        self.seq = 0
        self.state = 'OPEN'
        self.trace = []
        self.socket_closed = False
        self.run_completed = False
        self._thread = None
        self._joined = False

    def start(self):
        need(self._thread is None and self.state == 'OPEN', 'MEDIATOR_ALREADY_STARTED')
        self._thread = threading.Thread(target=self.run)
        self._thread.start()
        return self._thread

    def join(self, timeout):
        need(type(timeout) in (int, float) and not isinstance(timeout, bool) and
             math.isfinite(timeout) and 0 <= timeout <= 30 and
             self._thread is not None and threading.current_thread() is not self._thread,
             'MEDIATOR_JOIN')
        self._thread.join(timeout)
        self._joined = not self._thread.is_alive() and self.run_completed
        return self._joined

    def run(self):
        try:
            need(threading.current_thread() is self._thread, 'MEDIATOR_THREAD')
            while self.state == 'OPEN':
                raw = receive(self.sock, self.peer, self.writer.deadline)
                value = parse(raw)
                need(type(value) is dict and set(value) == REQUEST_KEYS and
                     value['v'] == 'context-fixture-ipc/v1' and value['attempt'] == self.token and
                     type(value['seq']) is int and value['seq'] == self.seq + 1 and
                     type(value['ordinal']) is int and type(value['leaf']) is str and
                     type(value['payload']) is str and hex64(value['sha256']), 'REQUEST')
                self.writer.check()  # after blocking receive, before each effect
                payload = base64.b64decode(value['payload'], validate=True)
                need(sha(payload) == value['sha256'], 'PAYLOAD_DIGEST')
                op = value['op']
                if op == 'EMIT':
                    need(value['ordinal'] == len(self.writer.rows) + 1, 'ORDINAL')
                    self.writer.emit(value['leaf'], payload)
                elif op == 'RELEASE_PRIVATE':
                    need(value['ordinal'] == 38 and value['leaf'] == '' and payload == b'',
                         'RELEASE_SHAPE')
                    self.writer.release_private()
                elif op == 'FINISH':
                    need(value['ordinal'] == 41 and value['leaf'] == '' and payload == b'',
                         'FINISH_SHAPE')
                    inventory = self.writer.finish()
                    self.state = 'AWAIT_EOF'
                else:
                    raise Unknown('OP')
                if op != 'FINISH':
                    self.writer.check()
                self.seq += 1
                ack = {'v': 'context-fixture-ack/v1', 'attempt': self.token, 'seq': self.seq,
                       'op': op, 'ordinal': value['ordinal'], 'request_sha256': sha(raw),
                       'leaf_sha256': sha(payload),
                       'inventory_sha256': inventory if op == 'FINISH' else sha(encode(self.writer.rows)),
                       'writer_closed': op == 'FINISH', 'private_absent': self.writer.released}
                self.trace.append(('ACK_PREPARED', op, value['ordinal'], sha(encode(ack))))
                send(self.sock, encode(ack), self.writer.deadline)
            # No extra frame or second FINISH accepted. EOF is only corroboration:
            # it cannot tell whether the client's close syscall reported success.
            need(receive(self.sock, self.peer, self.writer.deadline, eof=True) is None,
                 'POST_FINISH_FRAME')
            self.state = 'PEER_EOF'
        except BaseException:
            self.state = 'UNKNOWN'
            self.writer.abort()
        finally:
            try:
                self.sock.close()
            except BaseException:
                self.state = 'UNKNOWN'
            else:
                self.socket_closed = True
            self.run_completed = True
        return self.state


class Client:
    """Fixed bridge endpoint; the caller supplies only synthetic selection."""
    def __init__(self, sock, peer, token, out, source_binding, deadline):
        transport_selection(peer, token, deadline)
        configure(sock)
        self.sock, self.peer, self.token = sock, peer, token
        self.out, self.source, self.deadline = Path(out), source_binding, deadline
        self.seq = 0
        self.rows = []
        self.state = 'OPEN'
        self.released = False
        self.closed = False
        self.trace = []

    def close_once(self):
        if self.closed:
            return
        self.closed = True
        self.sock.close()

    def exchange(self, op, ordinal, leaf='', payload=b''):
        try:
            need(self.state == 'OPEN', 'CLIENT_POISONED')
            need(type(payload) is bytes and len(payload) <= MAX_LEAF, 'CLIENT_BYTES')
            request = {'v': 'context-fixture-ipc/v1', 'attempt': self.token,
                       'seq': self.seq + 1, 'op': op, 'ordinal': ordinal, 'leaf': leaf,
                       'sha256': sha(payload), 'payload': base64.b64encode(payload).decode()}
            raw = encode(request)
            send(self.sock, raw, self.deadline)
            self.trace.append(('SENT', op, ordinal, sha(raw)))
            ack_raw = receive(self.sock, self.peer, self.deadline)
            ack = parse(ack_raw)
            expected_rows = self.rows + ([{'path': str(self.out / leaf), 'sha256': sha(payload)}]
                                         if op == 'EMIT' else [])
            expected = {'v': 'context-fixture-ack/v1', 'attempt': self.token,
                        'seq': self.seq + 1, 'op': op, 'ordinal': ordinal,
                        'request_sha256': sha(raw), 'leaf_sha256': sha(payload),
                        'inventory_sha256': sha(encode(expected_rows)),
                        'writer_closed': op == 'FINISH',
                        'private_absent': self.released or op == 'RELEASE_PRIVATE'}
            need(ack_raw == encode(expected), 'ACK_BINDING')
            self.seq += 1
            self.trace.append(('ACK', op, ordinal, sha(ack_raw)))
            return expected_rows
        except BaseException:
            self.state = 'UNKNOWN'
            try:
                self.close_once()
            except BaseException:
                pass
            raise

    def emit(self, path, raw):
        try:
            need(self.state == 'OPEN' and len(self.rows) < 40 and
                 Path(path) == self.out / LEAVES[len(self.rows)], 'CLIENT_ORDER')
            need(len(self.rows) < 38 or self.released, 'CLIENT_PRIVATE_NOT_RELEASED')
            self.rows = self.exchange('EMIT', len(self.rows) + 1, LEAVES[len(self.rows)], raw)
            if len(self.rows) == 40:
                self.exchange('FINISH', 41)
                self.close_once()
                self.trace.append(('CLIENT_CLOSED', 1))
                self.state = 'SUMMARY_PERMITTED'
        except BaseException:
            self.state = 'UNKNOWN'
            try:
                self.close_once()
            except BaseException:
                pass
            raise

    def release_private(self):
        try:
            need(len(self.rows) == 38 and not self.released, 'CLIENT_RELEASE_ORDER')
            self.exchange('RELEASE_PRIVATE', 38)
            self.released = True
        except BaseException:
            self.state = 'UNKNOWN'
            try:
                self.close_once()
            except BaseException:
                pass
            raise


def final_verdict(client, mediator):
    # This check enforces managed completion; it is not a caller assertion.
    need(client.state == 'SUMMARY_PERMITTED' and client.closed and
         mediator._thread is not None and mediator._joined and
         mediator.run_completed and not mediator._thread.is_alive() and
         mediator.state == 'PEER_EOF' and mediator.socket_closed and
         mediator.writer.state == 'CLOSED', 'FINAL_UNKNOWN')
    return 'PASS_SYNTHETIC_ONLY'


class ProvisionalOutput:
    """Parent-owned bounded sink for the selected original print statement.

    No bytes are sent to stdout here. A real child-process controller must
    separately implement equivalent bounded pipe capture and OS-exit joining.
    This implementation serves the same-process selected AST fixture only.
    """
    def __init__(self):
        self._raw = None
        self.state = 'EMPTY'

    def capture(self, text, *, flush=False):
        try:
            need(self.state == 'EMPTY' and type(text) is str and
                 type(flush) is bool and len(text) <= 8192, 'PROVISIONAL_PRINT')
            raw = (text + '\n').encode('utf-8')
            need(len(raw) <= 8192, 'PROVISIONAL_PRINT_SIZE')
            self._raw = raw
            self.state = 'BUFFERED'
        except BaseException:
            self.state = 'UNKNOWN'
            raise

    def release(self, client, mediator):
        """One publication decision after successful aggregate completion."""
        try:
            need(self.state == 'BUFFERED', 'PROVISIONAL_STATE')
            final_verdict(client, mediator)
            value = parse(self._raw, canonical=False)
            expected = {
                'result': 'PASS',
                'package_binding': {'path': str(mediator.writer.out / 'manifest.json'),
                                    'sha256': mediator.writer.digests['manifest.json']},
                'generated_carriers': 30, 'posture': 'ready',
                'public_API_operations_added': 0,
            }
            # Exact canonical representation avoids bool/int equality aliasing.
            need(encode(value) == encode(expected), 'PROVISIONAL_SUMMARY_BINDING')
            self.state = 'RELEASED'
            return self._raw
        except BaseException:
            self.state = 'UNKNOWN'
            raise


def launch_context(*args, **kwargs):
    raise Unknown('ACTUAL_CONTEXT_EFFECT_DISABLED')
