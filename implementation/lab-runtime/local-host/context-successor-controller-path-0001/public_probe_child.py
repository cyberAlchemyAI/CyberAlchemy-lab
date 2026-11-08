"""Public-only namespace probe child candidate; never launched by this cut."""
from __future__ import annotations

import errno
import hashlib
import json
import os
import socket
import struct
import sys
from pathlib import Path

ROLE = 'product/lab/release-candidates/v1/interface/docker-context-20261020-0002'
HERE = Path('/workspace') / ROLE
OUT = HERE / 'packages/0001'
SENTINEL = HERE / '.readonly-sentinel'


def need(ok, code):
    if not ok:
        raise RuntimeError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def mountinfo_ro(raw):
    need(type(raw) is bytes and 0 < len(raw) <= 65536, 'MOUNTINFO_BOUND')
    rows = []
    try:
        for line in raw.decode('ascii').splitlines():
            head,_tail = line.split(' - ',1)
            fields = head.split(' ')
            need(len(fields) >= 6,'MOUNTINFO_SHAPE')
            rows.append((fields[4],set(fields[5].split(','))))
    except (UnicodeError,ValueError) as exc:
        raise RuntimeError('MOUNTINFO_SHAPE') from exc
    workspace = [options for path,options in rows if path == '/workspace']
    need(len(workspace) == 1 and 'ro' in workspace[0] and
         'rw' not in workspace[0] and
         not any(path.startswith('/workspace/') for path,_ in rows),
         'WORKSPACE_RO_NO_NESTED_MOUNT')
    return sha(raw)


def packet(sock,value):
    raw = (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
    need(len(raw) <= 4096,'PACKET_BOUND')
    sock.sendall(raw)


def receive(sock):
    raw = sock.recv(4097)
    need(0 < len(raw) <= 4096 and raw.endswith(b'\n'), 'PACKET_BOUND')
    value = json.loads(raw)
    need(type(value) is dict,'PACKET_OBJECT')
    return value


def require_erofs(open_fn=os.open, exists_fn=os.path.lexists,
                  close_fn=os.close):
    try:
        fd = open_fn(SENTINEL,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,
                     0o600)
    except OSError as exc:
        need(exc.errno == errno.EROFS and not exists_fn(SENTINEL),
             'EROFS_SENTINEL')
        return errno.EROFS
    close_fn(fd)
    raise RuntimeError('WRITABLE_CHILD_WORKSPACE')


def main(config):
    need(type(config) is dict and set(config) ==
         {'token','uid','gid'} and
         type(config['token']) is str and len(config['token']) == 32 and
         all(c in '0123456789abcdef' for c in config['token']) and
         type(config['uid']) is int and config['uid'] == os.getuid() and
         type(config['gid']) is int and config['gid'] == os.getgid(),
         'PROBE_SELECTION')
    need(not os.path.lexists(HERE/'packages'),'ORIGINAL_OUTPUT_ABSENT')
    raw = Path('/proc/self/mountinfo').read_bytes()
    mount_sha = mountinfo_ro(raw)
    require_erofs()
    sock = socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET)
    try:
        sock.settimeout(5)
        sock.connect('/control/ipc')
        peer = struct.unpack('3i',sock.getsockopt(socket.SOL_SOCKET,
                                                  socket.SO_PEERCRED,12))
        need(peer == (0,config['uid'],config['gid']),
             'PARENT_PEER_IDENTITY')
        packet(sock,{'schema':'context-public-probe-ready/v1',
                     'token':config['token'],'out':str(OUT),
                     'output_absent':True,'mountinfo_sha256':mount_sha,
                     'erofs_errno':errno.EROFS})
        go = receive(sock)
        need(go == {'schema':'context-public-probe-go/v1',
                    'token':config['token']},'PROBE_GO')
        ack = receive(sock)
        need(set(ack) == {'schema','token','leaf','sha256'} and
             ack['schema'] == 'context-public-probe-ack/v1' and
             ack['token'] == config['token'] and ack['leaf'] == 'request.json' and
             type(ack['sha256']) is str and len(ack['sha256']) == 64,
             'PROBE_ACK')
        fd = os.open(OUT/'request.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            body = os.read(fd,65537)
            need(0 < len(body) <= 65536 and sha(body) == ack['sha256'],
                 'POST_ACK_READBACK')
        finally:
            os.close(fd)
        packet(sock,{'schema':'context-public-probe-result/v1',
                     'token':config['token'],'child_readback_sha256':sha(body),
                     'mountinfo_sha256':mount_sha,'erofs_errno':errno.EROFS})
    finally:
        sock.close()


if __name__ == '__main__':
    try:
        need(len(sys.argv) == 2,'PROBE_ARGV')
        main(json.loads(sys.argv[1]))
    except BaseException:
        sys.stderr.write('PUBLIC_PROBE_UNKNOWN\n')
        raise SystemExit(1) from None
