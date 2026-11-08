"""Fixed inert fd3 peer for disposable transport tests only."""
from __future__ import annotations

import base64
from array import array
import os
import socket
import sys

from . import mapper_package_ipc_model_0004 as model
from . import mapper_package_transport_0001 as transport

ATTEMPT = 'synthetic-transport-0001'
SELECTION = '2' * 64
PINS = dict.fromkeys(('mapper', 'source', 'reader', 'adapter'), '1' * 64)


def _fd_census() -> bool:
    try:
        descriptors = [int(name) for name in os.listdir('/proc/self/fd')]
        for fd in descriptors:
            if fd <= 3:
                continue
            try:
                os.fstat(fd)
            except OSError:
                continue
            return False
        return True
    except OSError:
        return False


def _client(endpoint: socket.socket, scenario: str) -> int:
    endpoint.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
    endpoint.settimeout(transport.TIMEOUT)
    if endpoint.fileno() != 3 or not _fd_census():
        return 20
    parent = os.getppid()
    expected = (parent, transport.process_start(parent), os.geteuid(), os.getegid())
    ordinal = 0

    def exchange(verb, payload):
        nonlocal ordinal
        raw = model.encode(model.envelope(ATTEMPT, SELECTION, ordinal,
                                          verb, payload))
        transport.send_frame(endpoint, raw)
        response = model.decode(transport.recv_frame(endpoint, expected))
        if (type(response) is not dict or set(response) !=
                {'schema_version', 'ordinal', 'request_sha256', 'observation'} or
                response['schema_version'] != 'lab-mapper-transport-response/v1' or
                response['ordinal'] != ordinal or
                response['request_sha256'] != model.sha(raw) or
                response['observation'] not in ('MODEL_ONLY', 'DURABLE_FILE')):
            raise ValueError('response differs')
        ordinal += 1
        return response

    if scenario == 'disconnect':
        return 0
    if scenario == 'rights':
        fd = os.open('/dev/null', os.O_RDONLY | os.O_CLOEXEC)
        try:
            raw = model.encode(model.envelope(ATTEMPT, SELECTION, 0,
                                              'BEGIN', PINS))
            endpoint.sendmsg([raw], [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                                       __import__('struct').pack('i', fd))])
        finally:
            os.close(fd)
        return 0
    if scenario == 'ctrunc':
        fds = [os.open('/dev/null', os.O_RDONLY | os.O_CLOEXEC)
               for _ in range(64)]
        try:
            raw = model.encode(model.envelope(ATTEMPT, SELECTION, 0,
                                              'BEGIN', PINS))
            endpoint.sendmsg([raw], [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                                       array('i', fds).tobytes())])
        finally:
            for fd in fds:
                os.close(fd)
        return 0
    if scenario == 'trunc':
        endpoint.send(b'x' * (model.FRAME_MAX + 1))
        return 0
    if scenario == 'replay':
        raw = model.encode(model.envelope(ATTEMPT, SELECTION, 0,
                                          'BEGIN', PINS))
        transport.send_frame(endpoint, raw)
        transport.recv_frame(endpoint, expected)
        transport.send_frame(endpoint, raw)
        return 0

    exchange('BEGIN', PINS)

    def upload(verb, target, raw):
        blob_id = ordinal
        exchange('BLOB_BEGIN', {'size_bytes': len(raw), 'sha256': model.sha(raw),
                                'purpose': verb, 'target': target})
        exchange('BLOB_CHUNK', {'blob_id': blob_id, 'offset': 0,
                                'data': base64.b64encode(raw).decode()})
        exchange('BLOB_END', {'blob_id': blob_id})
        return blob_id

    for family in ('semantic', 'governance'):
        blob = upload('SEAL', family, b'{"semantic":[],"governance":[]}\n')
        exchange('SEAL', {'blob_id': blob})
    name = 'semantic/00000001.json'
    blob = upload('EMIT', name, b'{"synthetic":"event"}\n')
    response = exchange('EMIT', {'blob_id': blob, 'leaf': name})
    return 0 if response['observation'] == 'DURABLE_FILE' else 23


def main() -> int:
    try:
        if len(sys.argv) != 2 or sys.argv[1] not in (
                'normal', 'replay', 'disconnect', 'rights', 'trunc', 'ctrunc'):
            return 21
        with socket.socket(fileno=3) as endpoint:
            return _client(endpoint, sys.argv[1])
    except BaseException:
        return 22


if __name__ == '__main__':
    raise SystemExit(main())
