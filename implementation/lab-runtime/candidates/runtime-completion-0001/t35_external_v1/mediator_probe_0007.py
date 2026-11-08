"""One-shot inert B03/B05 mediator v7; independent static review required."""
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import select
import selectors
import signal
import socket
import stat
import sys
import tempfile
import time


ROOT = Path(__file__).absolute().parents[5]
EVIDENCE = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-05/b03-b05-mediator-evidence-0007'
PREFLIGHT = EVIDENCE.parent / 'B03-B05-BWRAP-MEDIATOR-PREFLIGHT-0007.md'
PREFLIGHT_SHA = '5afcd146610ca128be107f681e13de5f3cfeaeba34ffad3801a220dd6d73a5bd'
BWRAP = Path('/usr/bin/bwrap')
BWRAP_SHA = '523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6'
TOKEN = b'cal-lcu0205-b03b05-inert-token-v7\n'
MAX_STREAM = 8192
MAX_AGGREGATE = 16384
WALL_SECONDS = 10
GROUP_SECONDS = 3


def stderr_diagnostic(raw):
    """Publish only a bounded, fixed-vocabulary diagnosis, never child text."""
    sample = raw[:MAX_STREAM].lower()
    if b'unknown option' in sample:
        return 'BWRAP_UNKNOWN_OPTION'
    if b'operation not permitted' in sample or b'permission denied' in sample:
        return 'BWRAP_PERMISSION_DENIED'
    if b'traceback' in sample or b'assertionerror' in sample:
        return 'CHILD_ASSERTION'
    return 'OTHER_STDERR' if raw else 'NO_STDERR'


def validated_child_observation(raw, pre_family):
    """Decode an exact child grammar and reconstruct publishable fields only."""
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            need(key not in value, 'CHILD_DUPLICATE_KEY')
            value[key] = item
        return value

    def reject_constant(_value):
        raise ProbeError('CHILD_JSON_CONSTANT')

    try:
        value = json.loads(raw, object_pairs_hook=unique_object,
                           parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProbeError('CHILD_JSON') from None
    keys = {'schema_version', 'result', 'mount_dev', 'mount_ino',
            'fd_before', 'fd_after', 'mediated_sha256', 'direct_write_errno'}
    need(type(value) is dict and set(value) == keys, 'CHILD_SCHEMA_KEYS')
    need(type(value['schema_version']) is str and
         value['schema_version'] == 'lab-lcu0205-b03b05-mediator-child/v7' and
         type(value['result']) is str and value['result'] == 'PASS',
         'CHILD_SCHEMA_VALUES')
    need(type(value['mount_dev']) is int and type(value['mount_ino']) is int and
         (value['mount_dev'], value['mount_ino']) == tuple(pre_family[:2]),
         'MOUNT_SOURCE_IDENTITY')
    need(type(value['direct_write_errno']) is int and
         value['direct_write_errno'] == errno.EROFS and
         type(value['mediated_sha256']) is str and
         value['mediated_sha256'] == digest(TOKEN), 'CHILD_OBSERVATION')
    expected_rows = [[0, os.O_RDONLY, stat.S_IFCHR],
                     [1, os.O_WRONLY, stat.S_IFIFO],
                     [2, os.O_WRONLY, stat.S_IFIFO],
                     [3, os.O_RDWR, stat.S_IFSOCK]]
    for field in ('fd_before', 'fd_after'):
        rows = value[field]
        need(type(rows) is list and len(rows) == len(expected_rows), 'CHILD_FDS')
        for row, expected in zip(rows, expected_rows):
            need(type(row) is list and len(row) == 3 and
                 all(type(item) is int for item in row) and row == expected,
                 'CHILD_FDS')
    # No parsed child object crosses the receipt boundary. Rebuild only
    # validated primitives and exact rows, even if validation evolves.
    return {'schema_version': 'lab-lcu0205-b03b05-mediator-child/v7',
            'result': 'PASS', 'mount_dev': pre_family[0],
            'mount_ino': pre_family[1],
            'fd_before': [row.copy() for row in expected_rows],
            'fd_after': [row.copy() for row in expected_rows],
            'mediated_sha256': digest(TOKEN),
            'direct_write_errno': errno.EROFS}

CHILD = r'''
import errno,fcntl,hashlib,json,os,socket,stat
def fds():
    out=[]
    for item in sorted(os.listdir('/proc/self/fd'),key=int):
        fd=int(item)
        try: out.append([fd,fcntl.fcntl(fd,fcntl.F_GETFL)&os.O_ACCMODE,stat.S_IFMT(os.fstat(fd).st_mode)])
        except OSError as e:
            if e.errno!=errno.EBADF: raise
    return out
def allowed(rows):
    return [r[0] for r in rows]==[0,1,2,3] and [r[1] for r in rows]==[os.O_RDONLY,os.O_WRONLY,os.O_WRONLY,os.O_RDWR]
s=socket.socket(fileno=3)
before=fds()
family=os.stat('/family',follow_symlinks=False)
assert not os.path.lexists('/family/mediated.txt')
s.sendall(b'CREATE mediated.txt')
assert s.recv(64)==b'CREATED'
with open('/family/mediated.txt','rb') as f: content=f.read(128)
assert content==b'cal-lcu0205-b03b05-inert-token-v7\n'
direct_errno=None
try: fd=os.open('/family/direct.txt',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
except OSError as e: direct_errno=e.errno
else: os.close(fd)
after=fds()
assert direct_errno==errno.EROFS and allowed(before) and allowed(after)
print(json.dumps({'schema_version':'lab-lcu0205-b03b05-mediator-child/v7','result':'PASS','mount_dev':family.st_dev,'mount_ino':family.st_ino,'fd_before':before,'fd_after':after,'mediated_sha256':hashlib.sha256(content).hexdigest(),'direct_write_errno':direct_errno},sort_keys=True))
'''


class ProbeError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def need(condition, code):
    if not condition:
        raise ProbeError(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ident(fd):
    s = os.fstat(fd)
    return [s.st_dev, s.st_ino, s.st_uid, stat.S_IMODE(s.st_mode), s.st_size, s.st_nlink, s.st_mtime_ns, s.st_ctime_ns]


def path_ident(path):
    s = os.stat(path, follow_symlinks=False)
    return [s.st_dev, s.st_ino, s.st_uid, stat.S_IMODE(s.st_mode), s.st_size, s.st_nlink, s.st_mtime_ns, s.st_ctime_ns]


def hash_fd(fd, limit):
    before = ident(fd)
    need(before[4] <= limit, 'FILE_SIZE_BOUND')
    h = hashlib.sha256()
    offset = 0
    while offset < before[4]:
        chunk = os.pread(fd, min(65536, before[4] - offset), offset)
        need(bool(chunk), 'FILE_SHORT_READ')
        h.update(chunk)
        offset += len(chunk)
    need(ident(fd) == before, 'FILE_CHANGED_DURING_HASH')
    return h.hexdigest(), before


def fixed_selected(path, expected_sha, maximum, expected_owner=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        s = os.fstat(fd)
        need(stat.S_ISREG(s.st_mode) and s.st_nlink == 1, 'SELECTED_FILE_TYPE')
        if expected_owner is not None:
            need(s.st_uid == expected_owner, 'SELECTED_FILE_OWNER')
        value, selected = hash_fd(fd, maximum)
        need(value == expected_sha and path_ident(path) == selected, 'SELECTED_FILE_DRIFT')
        return fd, selected
    except Exception:
        os.close(fd)
        raise


def fsync_write(dirfd, name, raw):
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=dirfd)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
    finally:
        os.fsync(dirfd)


def evidence_root():
    fd = os.open(EVIDENCE, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        s = os.fstat(fd)
        need(stat.S_ISDIR(s.st_mode) and s.st_uid == os.getuid() and stat.S_IMODE(s.st_mode) == 0o700,
             'EVIDENCE_CUSTODY')
        need(path_ident(EVIDENCE) == ident(fd), 'EVIDENCE_ATTACHMENT')
        return fd
    except Exception:
        os.close(fd)
        raise


def evidence_attached(fd):
    try:
        s = os.fstat(fd)
        return (stat.S_ISDIR(s.st_mode) and s.st_uid == os.getuid() and
                stat.S_IMODE(s.st_mode) == 0o700 and path_ident(EVIDENCE) == ident(fd))
    except (FileNotFoundError, NotADirectoryError):
        return False


def reserve(dirfd):
    need('attempt-0001.pending' not in os.listdir(EVIDENCE) and
         'attempt-0001.json' not in os.listdir(EVIDENCE), 'ATTEMPT_EXISTS')
    fsync_write(dirfd, 'attempt-0001.pending', b'lab-lcu0205-b03b05-attempt/v7\n')


def publish_terminal(dirfd, value):
    """Provisional receipt plus separate attachment witness; marker is retained."""
    before = evidence_attached(dirfd)
    candidate = value['candidate_result']
    value = dict(value, result='PROVISIONAL', evidence_attached_before=before,
                 attachment_witness_required=True)
    raw = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    fsync_write(dirfd, 'attempt-0001.provisional.json', raw)
    after = evidence_attached(dirfd)
    terminal = 'PASS' if candidate == 'PASS' and before and after else 'UNKNOWN'
    witness = {'schema_version': 'lab-lcu0205-b03b05-attachment-witness/v7',
               'result': terminal, 'provisional_sha256': digest(raw),
               'held_evidence_identity': ident(dirfd),
               'attached_before': before, 'attached_after_provisional': after,
               'scratch_retained': True, 'reservation_retained': True}
    witness_raw = (json.dumps(witness, sort_keys=True, indent=2) + '\n').encode()
    fsync_write(dirfd, 'attempt-0001.attachment.json', witness_raw)
    last = evidence_attached(dirfd)
    if not last:
        drift = {'schema_version': 'lab-lcu0205-b03b05-attachment-drift/v7',
                 'result': 'UNKNOWN', 'witness_sha256': digest(witness_raw),
                 'held_evidence_identity': ident(dirfd)}
        fsync_write(dirfd, 'attempt-0001.attachment-drift.json',
                    (json.dumps(drift, sort_keys=True, indent=2) + '\n').encode())
        terminal = 'UNKNOWN'
    return terminal, digest(raw), digest(witness_raw), last


def proc_group_members(pgid):
    rows = []
    for entry in os.scandir('/proc'):
        if not entry.name.isdigit():
            continue
        try:
            raw = (Path('/proc') / entry.name / 'stat').read_text()
            fields = raw[raw.rfind(')') + 2:].split()
            if int(fields[2]) == pgid:
                rows.append((int(entry.name), fields[0], int(fields[19])))
        except (FileNotFoundError, ProcessLookupError):
            continue
    return rows


def leader_exited(pidfd):
    return os.waitid(os.P_PIDFD, pidfd, os.WEXITED | os.WNOHANG | os.WNOWAIT) is not None


def close_group(pid, pidfd, established, terminate, deadline):
    """Retain the direct child zombie until the selected original group is empty."""
    if terminate:
        if established:
            try: os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError: pass
        else:
            signal.pidfd_send_signal(pidfd, signal.SIGKILL)
    while time.monotonic() < deadline:
        exited = leader_exited(pidfd)
        members = proc_group_members(pid) if established else []
        live = [row for row in members if row[0] != pid]
        if exited and not live:
            waited, status = os.waitpid(pid, 0)
            need(waited == pid, 'LEADER_REAP')
            return {'leader_status': status, 'original_group_empty': True,
                    'leader_reaped': True, 'group_members_at_close': members}
        if terminate and established and live:
            try: os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError: pass
        time.sleep(0.02)
    raise ProbeError('GROUP_CLOSURE_UNKNOWN')


def child_launch(argv, exe_fd, child_sock, stdin_fd, stdout_w, stderr_w, ready_w):
    pid = os.fork()
    if pid == 0:
        try:
            os.setsid()
            # The held executable may itself be fd 3 in the parent. Lift it
            # before assigning the mediator socket to fd 3.
            keep = fcntl.fcntl(exe_fd, fcntl.F_DUPFD_CLOEXEC, 10)
            os.dup2(stdin_fd, 0)
            os.dup2(stdout_w, 1)
            os.dup2(stderr_w, 2)
            os.dup2(child_sock, 3)
            os.set_inheritable(3, True)
            os.write(ready_w, b'S')
            max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
            if max_fd == resource.RLIM_INFINITY:
                max_fd = 1048576
            os.closerange(4, keep)
            os.closerange(keep + 1, max_fd)
            os.execve(f'/proc/self/fd/{keep}', argv, {})
        except BaseException:
            os._exit(111)
    return pid


def mediator_commit(family_fd, family, pre_family):
    need(ident(family_fd) == path_ident(family) == pre_family and not os.listdir(family), 'FAMILY_PREWRITE_DRIFT')
    leaf_fd = os.open('mediated.txt', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                      0o400, dir_fd=family_fd)
    with os.fdopen(leaf_fd, 'wb') as out:
        out.write(TOKEN)
        out.flush()
        os.fsync(out.fileno())
    os.fsync(family_fd)


def stable_directory_ident(value):
    """Fields unchanged by creating a regular leaf in the same directory."""
    return (value[0], value[1], value[2], value[3], value[5])


def verified_family_poststate(family_fd, family, pre_family):
    """Accept authorized metadata mutation, while rejecting detach or extras."""
    post_family = ident(family_fd)
    need(post_family == path_ident(family) and
         stable_directory_ident(post_family) == stable_directory_ident(pre_family) and
         sorted(os.listdir(family_fd)) == ['mediated.txt'] and
         sorted(os.listdir(family)) == ['mediated.txt'], 'FAMILY_POSTSTATE')
    named_leaf_pre = os.stat('mediated.txt', dir_fd=family_fd, follow_symlinks=False)
    need(stat.S_ISREG(named_leaf_pre.st_mode), 'MEDIATED_LEAF_TYPE')
    leaf_fd = os.open('mediated.txt', os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                      dir_fd=family_fd)
    try:
        leaf_stat = os.fstat(leaf_fd)
        need(stat.S_ISREG(leaf_stat.st_mode), 'MEDIATED_LEAF_TYPE')
        leaf_ident = ident(leaf_fd)
        content = os.read(leaf_fd, len(TOKEN) + 1)
        need(leaf_ident == path_ident(family / 'mediated.txt') and
             leaf_ident[2] == os.getuid() and leaf_ident[3] == 0o400 and
             leaf_ident[4] == len(TOKEN) and leaf_ident[5] == 1 and
             content == TOKEN, 'MEDIATED_LEAF')
    finally:
        os.close(leaf_fd)
    need(ident(family_fd) == path_ident(family) == post_family and
         sorted(os.listdir(family_fd)) == ['mediated.txt'] and
         sorted(os.listdir(family)) == ['mediated.txt'] and
         path_ident(family / 'mediated.txt') == leaf_ident,
         'FAMILY_POSTREAD_DRIFT')
    return {'post_family': post_family, 'leaf_identity': leaf_ident,
            'leaf_sha256': digest(content)}


def bwrap_argv(family):
    # Bubblewrap 0.11.1 closes --sync-fd before payload exec unless
    # --as-pid-1 is selected; source-level evidence is in the preflight.
    return [str(BWRAP), '--die-with-parent', '--unshare-all', '--clearenv',
            '--as-pid-1', '--sync-fd', '3',
            '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64', '--ro-bind', str(family), '/family',
            '--proc', '/proc', '--chdir', '/', '--',
            '/usr/bin/python3', '-B', '-S', '-c', CHILD]


def streaming(pid, pidfd, ready_r, parent_sock, stdout_r, stderr_r, family_fd, family, pre_family, deadline, state, trace):
    selector = selectors.DefaultSelector()
    buffers = trace
    for fd, name in ((ready_r, 'ready'), (parent_sock.fileno(), 'mediator'),
                     (stdout_r, 'stdout'), (stderr_r, 'stderr')):
        os.set_blocking(fd, False)
        selector.register(fd, selectors.EVENT_READ, name)
    mediator_done = False
    try:
        while time.monotonic() < deadline:
            if leader_exited(pidfd) and 'stdout' not in [k.data for k in selector.get_map().values()] and 'stderr' not in [k.data for k in selector.get_map().values()]:
                if state.get('stream_failure'):
                    raise ProbeError(state['stream_failure'])
                need(mediator_done, 'MEDIATOR_REQUEST')
                return bytes(buffers['stdout']), bytes(buffers['stderr']), mediator_done
            events = selector.select(min(0.05, max(0, deadline - time.monotonic())))
            for key, _ in events:
                name = key.data
                if name == 'ready':
                    data = os.read(ready_r, 2)
                    need(data == b'S' and not state['established'], 'SESSION_HANDSHAKE')
                    state['established'] = True
                    selector.unregister(ready_r)
                elif name == 'mediator':
                    data = parent_sock.recv(64)
                    if data != b'CREATE mediated.txt' or not state['established'] or mediator_done:
                        state['stream_failure'] = 'MEDIATOR_REQUEST'
                    else:
                        mediator_commit(family_fd, family, pre_family)
                        parent_sock.sendall(b'CREATED')
                        mediator_done = True
                    selector.unregister(parent_sock)
                else:
                    fd = stdout_r if name == 'stdout' else stderr_r
                    chunk = os.read(fd, 4096)
                    if not chunk:
                        selector.unregister(fd)
                    else:
                        state[name + '_total'] = state.get(name + '_total', 0) + len(chunk)
                        buffers[name].extend(chunk[:max(0, MAX_STREAM - len(buffers[name]))])
                        need(state[name + '_total'] <= MAX_STREAM and
                             state.get('stdout_total', 0) + state.get('stderr_total', 0) <= MAX_AGGREGATE,
                             'OUTPUT_OVERFLOW')
        raise ProbeError(state.get('stream_failure') or 'ATTEMPT_DEADLINE')
    finally:
        selector.close()


def run(expected_source_sha):
    need(len(expected_source_sha) == 64 and all(c in '0123456789abcdef' for c in expected_source_sha), 'SOURCE_SELECTION')
    preflight_fd = source_fd = bwrap_fd = evidence_fd = family_fd = pidfd = -1
    scratch = None
    pid = None
    state = {'established': False}
    stream_trace = {'stdout': bytearray(), 'stderr': bytearray()}
    group = None
    code = None
    observation = {}
    pipes = []
    parent_sock = child_sock = None
    reserved = False
    reservation_started = False
    try:
        preflight_fd, _ = fixed_selected(PREFLIGHT, PREFLIGHT_SHA, 8192, os.getuid())
        source_fd, source_id = fixed_selected(Path(__file__).absolute(), expected_source_sha, 65536, os.getuid())
        bwrap_fd, bwrap_id = fixed_selected(BWRAP, BWRAP_SHA, 100000, 0)
        need(bwrap_id[3] == 0o755 and bwrap_id[4] == 80424, 'BWRAP_METADATA')
        evidence_fd = evidence_root()
        reservation_started = True
        reserve(evidence_fd)
        reserved = True
        deadline = time.monotonic() + WALL_SECONDS
        scratch = Path(tempfile.mkdtemp(prefix='lc-u02-05-b03b05-v7-', dir='/tmp'))
        os.chmod(scratch, 0o700)
        family = scratch / 'family'
        family.mkdir(mode=0o700)
        family_fd = os.open(family, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        pre_family = ident(family_fd)
        need(pre_family == path_ident(family) and not os.listdir(family), 'FAMILY_PRESTATE')
        need(hash_fd(source_fd, 65536)[0] == expected_source_sha and path_ident(Path(__file__).absolute()) == source_id,
             'SOURCE_PRELAUNCH_DRIFT')
        need(hash_fd(bwrap_fd, 100000)[0] == BWRAP_SHA and path_ident(BWRAP) == bwrap_id,
             'BWRAP_PRELAUNCH_DRIFT')
        parent_sock, child_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        ready_r, ready_w = os.pipe2(os.O_CLOEXEC)
        stdout_r, stdout_w = os.pipe2(os.O_CLOEXEC)
        stderr_r, stderr_w = os.pipe2(os.O_CLOEXEC)
        pipes = [ready_r, ready_w, stdout_r, stdout_w, stderr_r, stderr_w]
        stdin_fd = os.open('/dev/null', os.O_RDONLY | os.O_CLOEXEC)
        pipes.append(stdin_fd)
        argv = bwrap_argv(family)
        pid = child_launch(argv, bwrap_fd, child_sock.fileno(), stdin_fd, stdout_w, stderr_w, ready_w)
        pidfd = os.pidfd_open(pid)
        for fd in (ready_w, stdout_w, stderr_w, stdin_fd):
            os.close(fd)
            pipes.remove(fd)
        child_sock.close()
        child_sock = None
        out, err, mediated = streaming(pid, pidfd, ready_r, parent_sock,
                                      stdout_r, stderr_r, family_fd, family, pre_family, deadline, state, stream_trace)
        need(mediated and not err and out.count(b'\n') == 1, 'CHILD_OUTPUT')
        value = validated_child_observation(out, pre_family)
        group = close_group(pid, pidfd, state['established'], False, min(deadline, time.monotonic() + GROUP_SECONDS))
        pid = None
        need(os.WIFEXITED(group['leader_status']) and os.WEXITSTATUS(group['leader_status']) == 0, 'LEADER_EXIT')
        family_poststate = verified_family_poststate(family_fd, family, pre_family)
        need(hash_fd(source_fd, 65536)[0] == expected_source_sha and path_ident(Path(__file__).absolute()) == source_id,
             'SOURCE_POST_DRIFT')
        need(hash_fd(bwrap_fd, 100000)[0] == BWRAP_SHA and path_ident(BWRAP) == bwrap_id,
             'BWRAP_POST_DRIFT')
        observation = {'pre_family': pre_family, 'family_poststate': family_poststate,
                       'child': value, 'stdout_sha256': digest(out),
                       'stderr_bytes': len(err), 'group': group, 'bwrap_identity': bwrap_id,
                       'source_identity': source_id}
        # Retain the exact owner-only scratch for independent post-effect
        # inspection. A later cleanup transaction may remove it.
    except ProbeError as exc:
        code = exc.code
    except BaseException:
        code = 'INTERNAL_OR_SETUP_UNKNOWN'
    finally:
        if pid is not None and pidfd >= 0:
            try:
                # The child may have reached setsid even if the ready byte was
                # not consumed before a stream error. The unreaped PID holds
                # its original number while this current group check runs.
                try:
                    state['established'] = state['established'] or os.getpgid(pid) == pid
                except ProcessLookupError:
                    pass
                group = close_group(pid, pidfd, state['established'], True, time.monotonic() + GROUP_SECONDS)
            except BaseException:
                code = 'GROUP_CLOSURE_UNKNOWN'
        elif pid is not None:
            # The direct child is still ours and unreaped, so this PID cannot
            # have been reused. We cannot prove group closure without a PIDFD.
            try: os.kill(pid, signal.SIGKILL)
            except ProcessLookupError: pass
            stop = time.monotonic() + GROUP_SECONDS
            while time.monotonic() < stop:
                waited, _ = os.waitpid(pid, os.WNOHANG)
                if waited == pid:
                    break
                time.sleep(0.02)
            code = 'PIDFD_OR_GROUP_UNKNOWN'
        for fd in pipes:
            try: os.close(fd)
            except OSError: pass
        for fd in (preflight_fd, source_fd, bwrap_fd, family_fd, pidfd):
            if fd >= 0:
                try: os.close(fd)
                except OSError: pass
        for sock in (parent_sock, child_sock):
            if sock is not None: sock.close()
    if not reserved:
        if evidence_fd >= 0:
            os.close(evidence_fd)
        if reservation_started:
            raise ProbeError('RESERVATION_UNCERTAIN_NO_RETRY')
        raise ProbeError(code or 'PRE_RESERVATION_REFUSAL')
    result = {'schema_version': 'lab-lcu0205-b03b05-mediator-probe/v7',
              'candidate_result': 'PASS' if code is None and scratch is not None else 'UNKNOWN',
              'failure_code': code, 'source_sha256_selected': expected_source_sha,
              'bwrap_sha256_selected': BWRAP_SHA, 'preflight_sha256': PREFLIGHT_SHA,
              'scratch_path': str(scratch) if scratch is not None else None,
              'scratch_retained': scratch is not None,
              'early_stderr': {'diagnostic': stderr_diagnostic(stream_trace['stderr']),
                               'captured_bytes': len(stream_trace['stderr']),
                               'observed_bytes': state.get('stderr_total', 0),
                               'captured_sha256': digest(stream_trace['stderr'])},
              'claim_ceiling': 'One inert fd3/read-only-bind mediator observation only; group check excludes no escaped session; same-UID bind-source race, protected authority, historical builder, Mapper, Context, host qualification and LC-U02-05 acceptance remain unproved.',
              'observation': observation, 'group_cleanup': group}
    try:
        terminal, provisional_sha, witness_sha, attached = publish_terminal(evidence_fd, result)
    finally:
        os.close(evidence_fd)
    print(json.dumps({'result': terminal, 'provisional_sha256': provisional_sha,
                      'attachment_witness_sha256': witness_sha,
                      'evidence_attached': attached,
                      'evidence_directory': str(EVIDENCE) if attached else None,
                      'scratch_path': result['scratch_path']}, sort_keys=True))
    if terminal != 'PASS':
        raise ProbeError('ATTEMPT_UNKNOWN')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: mediator_probe_0007.py INDEPENDENTLY_SELECTED_SOURCE_SHA256')
    run(sys.argv[1])
