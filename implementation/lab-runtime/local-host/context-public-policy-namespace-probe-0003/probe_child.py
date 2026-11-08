"""Public-only namespace probe child candidate; never launched by this cut."""
from __future__ import annotations

import errno
import base64
import stat
import hashlib
import json
import os
import socket
import struct
import sys
from pathlib import Path

ROLE = 'probe/public-only'
HERE = Path('/workspace') / ROLE
OUT = HERE / 'packages/0001'
SENTINEL = HERE / '.readonly-sentinel'
MOUNT_TARGETS = ('/workspace','/control','/runner','/cache-disabled',
                 '/attempt/input/lab-context-native-reader','/context-policy')


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
            head,tail = line.split(' - ',1)
            fields = head.split(' ')
            need(len(fields) >= 6 and all(fields[:6]) and len(tail.split(' ')) >= 3,
                 'MOUNTINFO_SHAPE')
            encoded = fields[4]
            decoded = []
            index = 0
            while index < len(encoded):
                if encoded[index] == '\\':
                    digits = encoded[index+1:index+4]
                    need(len(digits) == 3 and all(c in '01234567' for c in digits),
                         'MOUNTINFO_ESCAPE')
                    decoded.append(chr(int(digits,8)))
                    index += 4
                else:
                    decoded.append(encoded[index])
                    index += 1
            path = ''.join(decoded)
            need(path.startswith('/') and all(32 <= ord(c) < 127 for c in path) and
                 (path == '/' or (not path.endswith('/') and
                  all(part not in ('','.','..') for part in path.split('/')[1:]))),
                 'MOUNTINFO_PATH')
            rows.append((path,set(fields[5].split(','))))
    except (UnicodeError,ValueError) as exc:
        raise RuntimeError('MOUNTINFO_SHAPE') from exc
    for target in MOUNT_TARGETS:
        found = [options for path,options in rows if path == target]
        need(len(found) == 1 and 'ro' in found[0] and 'rw' not in found[0],
             'SIX_VFS_READ_ONLY_MOUNTS')
    need(not any(path.startswith(target+'/')
                 for path,_ in rows for target in MOUNT_TARGETS),
         'SIX_TARGETS_NO_NESTED_MOUNT')
    return sha(raw)

def packet(sock,value):
    raw = (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
    need(len(raw) <= 98304,'PACKET_BOUND')
    need(sock.send(raw) == len(raw),'SHORT_PACKET')


def receive(sock):
    raw = sock.recv(98305)
    need(0 < len(raw) <= 98304 and raw.endswith(b'\n'), 'PACKET_BOUND')
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


POLICY_PUBLIC = b'{"schema":"public-policy-visibility-sentinel/v1","authority_effect":"none","public_only":true}\n'
POLICY_PATH = Path('/context-policy/permission.json')

def read_policy():
    fd = os.open(POLICY_PATH,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
    try:
        st = os.fstat(fd)
        body = os.read(fd,4097)
        need(stat.S_ISREG(st.st_mode) and st.st_uid == os.getuid() and
             stat.S_IMODE(st.st_mode) == 0o600 and st.st_nlink == 1 and
             body == POLICY_PUBLIC, 'PUBLIC_POLICY_READBACK')
        return sha(body)
    finally:
        os.close(fd)

def require_policy_erofs(open_fn=os.open, close_fn=os.close):
    # No write/truncate occurs even on a failing writable-mount control.
    try:
        fd = open_fn(POLICY_PATH,os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
    except OSError as exc:
        need(exc.errno == errno.EROFS,'POLICY_EROFS_REQUIRED')
        return errno.EROFS
    close_fn(fd)
    raise RuntimeError('POLICY_MOUNT_WRITABLE')


def main(config):
    need(type(config) is dict and set(config) ==
         {'token','uid','gid'} and
         type(config['token']) is str and len(config['token']) == 32 and
         all(c in '0123456789abcdef' for c in config['token']) and
         type(config['uid']) is int and config['uid'] == os.getuid() and
         type(config['gid']) is int and config['gid'] == os.getgid(),
         'PROBE_SELECTION')
    need(not os.path.lexists(HERE/'packages'),'ORIGINAL_OUTPUT_ABSENT')
    need(not os.path.lexists('/context-policy/permission.json'),'POLICY_INITIAL_ABSENCE')
    with open('/proc/self/mountinfo','rb') as stream:
        raw = stream.read(65537)
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
                     'erofs_errno':errno.EROFS,
                     'policy_absent':True,'mountinfo_b64':base64.b64encode(raw).decode('ascii')})
        go = receive(sock)
        need(go == {'schema':'context-public-probe-go/v1',
                    'token':config['token']},'PROBE_GO')
        ack = receive(sock)
        need(set(ack) == {'schema','token','leaf','sha256','policy_sha256'} and
             ack['schema'] == 'context-public-probe-ack/v1' and
             ack['token'] == config['token'] and ack['leaf'] == 'request.json' and
             type(ack['sha256']) is str and len(ack['sha256']) == 64,
             'PROBE_ACK')
        need(ack['policy_sha256'] == sha(POLICY_PUBLIC),'POLICY_ACK_DIGEST')
        fd = os.open(OUT/'request.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            body = os.read(fd,65537)
            need(0 < len(body) <= 65536 and sha(body) == ack['sha256'],
                 'POST_ACK_READBACK')
        finally:
            os.close(fd)
        policy_sha = read_policy()
        require_policy_erofs()
        packet(sock,{'schema':'context-public-probe-result/v1',
                     'token':config['token'],'child_readback_sha256':sha(body),
                     'mountinfo_sha256':mount_sha,'erofs_errno':errno.EROFS,
                     'policy_sha256':policy_sha,'policy_erofs_errno':errno.EROFS})
    finally:
        sock.close()


if __name__ == '__main__':
    try:
        need(len(sys.argv) == 2,'PROBE_ARGV')
        main(json.loads(sys.argv[1]))
    except BaseException:
        sys.stderr.write('PUBLIC_PROBE_UNKNOWN\n')
        raise SystemExit(1) from None
