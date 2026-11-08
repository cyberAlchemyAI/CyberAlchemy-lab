"""One-shot, inert Bubblewrap fd3/read-only-bind mediator feasibility probe.

Do not invoke until independent exact-byte preflight review. No generated builder,
native executable, Source8 input, or protected family is used.
"""
import errno
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time


BWRAP = Path('/usr/bin/bwrap')
BWRAP_SHA = '523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6'
TOKEN = b'cal-lcu0205-b03b05-inert-token-v1\n'
PREFLIGHT_SHA = '7d93614c4c9a4ed7251aed783fc7bc4836664e65b242851b7de97a798198cac1'
PREFLIGHT = Path('docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-05/B03-B05-BWRAP-MEDIATOR-PREFLIGHT-0001.md')

CHILD = r'''
import errno,fcntl,json,os,socket,stat
def fd_rows():
    out=[]
    for name in sorted(os.listdir('/proc/self/fd'),key=int):
        fd=int(name)
        try:
            flags=fcntl.fcntl(fd,fcntl.F_GETFL)
            kind=stat.S_IFMT(os.fstat(fd).st_mode)
            out.append({'fd':fd,'access':flags & os.O_ACCMODE,'kind':kind})
        except OSError as e:
            if e.errno != errno.EBADF: raise
    return out
def valid(rows):
    return [r['fd'] for r in rows]==[0,1,2,3] and all(r['access']==(os.O_RDONLY if r['fd']==0 else os.O_WRONLY if r['fd'] in (1,2) else os.O_RDWR) for r in rows)
s=socket.socket(fileno=3)
before=fd_rows()
family=os.stat('/family',follow_symlinks=False)
assert not os.path.lexists('/family/mediated.txt')
s.sendall(b'CREATE mediated.txt')
assert s.recv(64)==b'CREATED'
with open('/family/mediated.txt','rb') as f: content=f.read(128)
assert content==b'cal-lcu0205-b03b05-inert-token-v1\n'
direct_errno=None
try: fd=os.open('/family/direct.txt',os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
except OSError as e: direct_errno=e.errno
else: os.close(fd)
after=fd_rows()
assert direct_errno==errno.EROFS and valid(before) and valid(after)
print(json.dumps({'schema_version':'lab-lcu0205-b03b05-mediator-child/v1','result':'PASS','mount_dev':family.st_dev,'mount_ino':family.st_ino,'fd_before':before,'fd_after':after,'mediated_sha256':'b5af833c7d35d2097ea775e0b6b53d97649f27cb745315774b41d40732db148d','direct_write_errno':direct_errno},sort_keys=True))
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path_or_fd):
    s = os.fstat(path_or_fd) if isinstance(path_or_fd, int) else os.stat(path_or_fd, follow_symlinks=False)
    return {'dev': s.st_dev, 'ino': s.st_ino, 'uid': s.st_uid, 'mode': stat.S_IMODE(s.st_mode), 'nlink': s.st_nlink}


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def pin_preflight():
    require(PREFLIGHT.is_file() and not PREFLIGHT.is_symlink() and sha(PREFLIGHT.read_bytes()) == PREFLIGHT_SHA, 'preflight drift')
    s = BWRAP.stat()
    require(stat.S_ISREG(s.st_mode) and s.st_uid == 0 and stat.S_IMODE(s.st_mode) == 0o755 and s.st_size == 80424, 'bwrap metadata drift')
    require(sha(BWRAP.read_bytes()) == BWRAP_SHA, 'bwrap digest drift')


def child_preexec(fd):
    def setup():
        if fd != 3:
            os.dup2(fd, 3, inheritable=True)
        else:
            os.set_inheritable(3, True)
    return setup


def no_replace_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try: os.fsync(parent)
    finally: os.close(parent)
    return sha(raw)


def run(receipt):
    require(receipt.is_absolute() and receipt.parent.is_dir() and not receipt.exists(), 'fresh receipt required')
    pin_preflight()
    scratch = Path(tempfile.mkdtemp(prefix='lc-u02-05-b03b05-', dir='/tmp'))
    os.chmod(scratch, 0o700)
    family = scratch / 'family'
    family.mkdir(mode=0o700)
    held = os.open(family, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    parent_sock = child_sock = None
    child = None
    created = False
    cleanup = 'UNKNOWN-retained'
    observation = {}
    failure = None
    try:
        pre = {'scratch': identity(scratch), 'family_held': identity(held), 'family_path': identity(family),
               'family_names': os.listdir(family)}
        require(pre['scratch']['uid'] == os.getuid() and pre['scratch']['mode'] == 0o700, 'scratch custody')
        require(pre['family_held'] == pre['family_path'] and not pre['family_names'], 'family prestate')
        parent_sock, child_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        argv = [str(BWRAP), '--die-with-parent', '--unshare-all', '--clearenv', '--preserve-fds', '1',
                '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64',
                '--ro-bind', str(family), '/family', '--proc', '/proc',
                '--chdir', '/', '--', '/usr/bin/python3', '-B', '-S', '-c', CHILD]
        # Only child_sock is passed. preexec remaps it to 3 before bwrap starts.
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 close_fds=True, pass_fds=(child_sock.fileno(),), preexec_fn=child_preexec(child_sock.fileno()),
                                 start_new_session=True, env={})
        child_sock.close()
        child_sock = None
        ready, _, _ = select.select([parent_sock], [], [], 5)
        require(bool(ready), 'mediator request timeout')
        request = parent_sock.recv(64)
        require(request == b'CREATE mediated.txt', 'unexpected mediator request')
        require(identity(held) == identity(family) == pre['family_held'], 'source attachment changed before mediator write')
        require(not os.listdir(family), 'unexpected family prewrite leaf')
        fd = os.open('mediated.txt', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o400, dir_fd=held)
        created = True
        with os.fdopen(fd, 'wb') as f:
            f.write(TOKEN)
            f.flush()
            os.fsync(f.fileno())
        parent_sock.sendall(b'CREATED')
        stdout, stderr = child.communicate(timeout=8)
        require(len(stdout) <= 8192 and len(stderr) <= 8192, 'child output bound')
        require(child.returncode == 0 and not stderr and stdout.count(b'\n') == 1, 'child failed')
        value = json.loads(stdout)
        require(value['result'] == 'PASS' and value['schema_version'] == 'lab-lcu0205-b03b05-mediator-child/v1', 'child contract')
        require((value['mount_dev'], value['mount_ino']) == (pre['family_held']['dev'], pre['family_held']['ino']), 'mount identity')
        require(value['direct_write_errno'] == errno.EROFS, 'direct write not refused')
        require(value['mediated_sha256'] == sha(TOKEN), 'child token digest')
        require(value['fd_before'] == value['fd_after'], 'child fd drift')
        require(identity(held) == identity(family) == pre['family_held'], 'source attachment changed after child')
        require(os.listdir(family) == ['mediated.txt'], 'family poststate')
        leaf = family / 'mediated.txt'
        require(leaf.is_file() and not leaf.is_symlink() and leaf.read_bytes() == TOKEN and
                stat.S_IMODE(leaf.stat().st_mode) == 0o400 and leaf.stat().st_nlink == 1,
                'mediated leaf poststate')
        observation = {'pre': pre, 'child': value, 'child_returncode': child.returncode,
                       'child_stdout_sha256': sha(stdout), 'child_stderr_bytes': len(stderr),
                       'post': {'family_held': identity(held), 'family_path': identity(family),
                                'family_names': os.listdir(family), 'mediated_sha256': sha(TOKEN)}}
        parent_sock.close()
        parent_sock = None
        os.close(held)
        held = -1
        leaf.unlink()
        family.rmdir()
        scratch.rmdir()
        cleanup = 'confirmed-scratch-absent'
    except Exception as exc:
        failure = type(exc).__name__ + ': ' + str(exc)[:160]
        if child is not None and child.poll() is None:
            try: os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            try: child.communicate(timeout=5)
            except subprocess.TimeoutExpired: failure += '; child-reap-uncertain'
    finally:
        if parent_sock is not None: parent_sock.close()
        if child_sock is not None: child_sock.close()
        if held >= 0: os.close(held)
        if child is not None:
            for stream in (child.stdout, child.stderr):
                if stream is not None: stream.close()
    receipt_value = {'schema_version': 'lab-lcu0205-b03b05-mediator-probe/v1',
                     'result': 'PASS' if failure is None else 'UNKNOWN',
                     'claim_ceiling': 'One inert Bubblewrap fd3 and read-only-bind mediator feasibility observation; no writer isolation, protected source, historical builder, Mapper, Context, host qualification, or LC-U02-05 acceptance.',
                     'bwrap_sha256': BWRAP_SHA, 'preflight_sha256': PREFLIGHT_SHA,
                     'source_sha256': sha(Path(__file__).read_bytes()), 'scratch_path': str(scratch),
                     'cleanup': cleanup, 'observation': observation, 'failure': failure,
                     'scratch_absent': not scratch.exists()}
    digest = no_replace_json(receipt, receipt_value)
    print(json.dumps({'result': receipt_value['result'], 'receipt': str(receipt), 'sha256': digest,
                      'cleanup': cleanup, 'scratch_path': str(scratch)}, sort_keys=True))
    if failure is not None:
        raise RuntimeError('probe UNKNOWN; scratch retained; inspect receipt')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: mediator_probe_0001.py NEW-ABSOLUTE-RECEIPT.json')
    run(Path(sys.argv[1]))
