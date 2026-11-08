"""Disposable kernel-credential SOCK_SEQPACKET transport for the pure model.

Only a fixed inert stand-in may be spawned by this module. The server can
durably emit opaque package bytes through the separate scratch-only writer;
SEAL and COLD_READ remain model-only and never invoke native code.
"""
from __future__ import annotations

from array import array
import fcntl
import os
from pathlib import Path
import signal
import socket
import stat
import struct
import sys
import threading
import time

from . import mapper_package_ipc_model_0004 as model

ANCILLARY_MAX = socket.CMSG_SPACE(struct.calcsize('3i')) + socket.CMSG_SPACE(16 * 4)
CHILD_MODULE = 't35_external_v1.phase_scoped_v2.mapper_package_standin_0001'
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT = 5.0


class TransportRefusal(RuntimeError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok:
        raise TransportRefusal(code)


def process_start(pid: int) -> int:
    need(type(pid) is int and pid > 0, 'PID')
    raw = Path(f'/proc/{pid}/stat').read_bytes()
    rest = raw.rsplit(b')', 1)[1].split()
    return int(rest[19])


def socket_pair() -> tuple[socket.socket, socket.socket]:
    pair = socket.socketpair(socket.AF_UNIX,
                             socket.SOCK_SEQPACKET | socket.SOCK_CLOEXEC)
    for endpoint in pair:
        endpoint.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        endpoint.settimeout(TIMEOUT)
    return pair


def _close_rights(ancillary: list[tuple[int, int, bytes]]) -> tuple[tuple[int, int, int] | None,
                                                                int, bool, bool]:
    credentials = []
    rights = False
    unknown = False
    for level, kind, data in ancillary:
        if level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS:
            if len(data) == struct.calcsize('3i'):
                credentials.append(struct.unpack('3i', data))
            else:
                unknown = True
        elif level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
            rights = True
            values = array('i')
            values.frombytes(data[:len(data) // values.itemsize * values.itemsize])
            for fd in values:
                try:
                    os.close(fd)
                except OSError:
                    unknown = True
        else:
            unknown = True
    return (credentials[0] if len(credentials) == 1 else None,
            len(credentials), rights, unknown)


def recv_frame(endpoint: socket.socket, expected: tuple[int, int, int, int]) -> bytes:
    """Receive one whole frame and one genuine kernel credential, no rights."""
    try:
        raw, ancillary, flags, _address = endpoint.recvmsg(
            model.FRAME_MAX, ANCILLARY_MAX,
            getattr(socket, 'MSG_CMSG_CLOEXEC', 0))
    except (OSError, TimeoutError) as error:
        raise TransportRefusal('RECV_FAILED') from error
    credential, count, rights, unknown = _close_rights(ancillary)
    need(bool(raw), 'DISCONNECTED')
    need(not flags & socket.MSG_TRUNC, 'MSG_TRUNC')
    need(not flags & socket.MSG_CTRUNC, 'MSG_CTRUNC')
    need(not rights, 'SCM_RIGHTS')
    need(not unknown and count == 1 and credential is not None,
         'SCM_CREDENTIALS')
    pid, uid, gid = credential
    need((pid, process_start(pid), uid, gid) == expected,
         'PEER_IDENTITY')
    return raw


def send_frame(endpoint: socket.socket, raw: bytes) -> None:
    need(type(raw) is bytes and 0 < len(raw) <= model.FRAME_MAX, 'FRAME_BOUND')
    try:
        count = endpoint.send(raw)
    except OSError as error:
        raise TransportRefusal('SEND_FAILED') from error
    need(count == len(raw), 'SHORT_SEND')


def _inheritable_fds(except_fd: int) -> list[int]:
    result = []
    for name in os.listdir('/proc/self/fd'):
        fd = int(name)
        if fd <= 2 or fd == except_fd:
            continue
        try:
            if os.get_inheritable(fd):
                result.append(fd)
        except OSError:
            pass
    return result


def spawn_standin(child: socket.socket, scenario: str) -> int:
    """Map only the socket to fd3 using posix_spawn file actions."""
    need(scenario in ('normal', 'replay', 'disconnect', 'rights', 'trunc', 'ctrunc'),
         'SCENARIO')
    need(threading.active_count() == 1, 'MULTITHREADED_SPAWN')
    transfer = fcntl.fcntl(child.fileno(), fcntl.F_DUPFD_CLOEXEC, 4)
    try:
        need(not _inheritable_fds(transfer), 'INHERITABLE_FD')
        env = {'PATH': '/usr/bin:/bin', 'PYTHONPATH': str(PACKAGE_ROOT),
               'LC_ALL': 'C.UTF-8'}
        argv = [sys.executable, '-B', '-m', CHILD_MODULE, scenario]
        actions = [(os.POSIX_SPAWN_DUP2, transfer, 3),
                   (os.POSIX_SPAWN_CLOSE, transfer)]
        return os.posix_spawn(sys.executable, argv, env,
                              file_actions=actions, setsid=True)
    finally:
        os.close(transfer)


class ModelServer:
    """Real transport checks; only EMIT may call the disposable writer."""

    def __init__(self, endpoint: socket.socket, peer: tuple[int, int, int, int],
                 protocol: model.ProtocolModel, writer=None):
        need(type(protocol) is model.ProtocolModel and protocol.peer == peer,
             'MODEL_PEER')
        self.endpoint = endpoint
        self.peer = peer
        self.protocol = protocol
        self.writer = writer
        self.failed = False
        self.closed = False
        self.emits = 0

    def receive_one(self) -> dict:
        need(not self.failed and not self.closed, 'SERVER_CLOSED')
        try:
            raw = recv_frame(self.endpoint, self.peer)
            # The pure model consumes its ready upload on an EMIT action.
            ready = self.protocol.ready
            action = self.protocol.receive(raw, peer=self.peer)
            if action.get('schema_version') == 'lab-mapper-model-action/v1':
                if action['verb'] == 'EMIT':
                    need(self.writer is not None and ready is not None and
                         bytes(ready['data']) and
                         model.sha(ready['data']) == action['blob_sha256'],
                         'WRITER_BLOB')
                    receipt = self.writer.emit(action['target'], bytes(ready['data']))
                    need(receipt['durable_observed'] is True and
                         receipt['sha256'] == action['blob_sha256'],
                         'WRITER_ACK')
                    self.emits += 1
                    observed = 'DURABLE_FILE'
                else:
                    observed = 'MODEL_ONLY'
                self.protocol.complete_synthetic(action['action_id'], success=True)
            else:
                observed = 'MODEL_ONLY'
            response = model.encode({
                'schema_version': 'lab-mapper-transport-response/v1',
                'ordinal': action['ordinal'],
                'request_sha256': model.sha(raw),
                'observation': observed,
            })
            send_frame(self.endpoint, response)
            return {'ordinal': action['ordinal'], 'observation': observed,
                    'peer_pid': self.peer[0]}
        except BaseException:
            self.failed = True
            self.protocol.disconnect()
            if self.writer is not None:
                self.writer.unknown = True
            self.close()
            raise

    def close(self) -> None:
        if not self.closed:
            self.closed = True
            self.endpoint.close()


def reap_standin(pid: int, *, timeout: float = TIMEOUT) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        done, status = os.waitpid(pid, os.WNOHANG)
        if done == pid:
            return os.waitstatus_to_exitcode(status)
        time.sleep(0.01)
    # The leader has not been reaped by the polling loop, so its original
    # session/group identity still anchors this numeric PGID if cleanup fires.
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    _, status = os.waitpid(pid, 0)
    return os.waitstatus_to_exitcode(status)
