"""Separate-process synthetic transport. Real Context execution is permanently disabled."""
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import socket
import stat
import struct
import subprocess
import sys
import time
import types

HERE = Path(__file__).resolve().parent
BRIDGE = HERE.parent / 'context-bridge-0002/bridge.py'
BRIDGE_SHA = '5bf35088d43f781453ee8f4e9397a033bd2acdd671142a5a7c05adad709bb52a'
OUTPUT_GUARD_SHA = '1d320473ba057e508a1b52176c556cd2f368e3edfc4f8de4d7de076edf831538'
PYTHON = '/usr/bin/python3.14'
PYTHON_SHA = '52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'
DOCKER = '/usr/bin/docker'
DOCKER_SHA = '999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
GUARD = '/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-02/python-bytecode-cache-disabled-0002'
EFFECT_ENABLED = False
# Bootstrap compiles the exact retained bytes whose digest was checked.
BOOTSTRAP = """import hashlib,pathlib,sys
p=pathlib.Path(sys.argv.pop(1));h=sys.argv.pop(1);r=p.read_bytes()
if hashlib.sha256(r).hexdigest()!=h: raise RuntimeError('CHILD_PREIMAGE')
exec(compile(r,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
"""


class CaptureUnknown(RuntimeError):
    def __init__(self, code, outputs):
        super().__init__(code)
        self.outputs = {key: bytes(value) for key, value in outputs.items()}


def selected(path, digest):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        first = os.fstat(fd)
        if not stat.S_ISREG(first.st_mode) or first.st_size > 128 * 1024 * 1024:
            raise RuntimeError('SELECTED_FILE')
        chunks, count = [], 0
        while count <= first.st_size:
            raw = os.read(fd, min(1024 * 1024, first.st_size + 1 - count))
            if not raw:
                break
            chunks.append(raw)
            count += len(raw)
        raw = b''.join(chunks)
        after = os.fstat(fd)
        fields = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if fields(first) != fields(after) or count != first.st_size or hashlib.sha256(raw).hexdigest() != digest:
            raise RuntimeError('SELECTED_DRIFT')
        return raw
    finally:
        os.close(fd)


def bridge():
    raw = selected(BRIDGE, BRIDGE_SHA)
    module = types.ModuleType('_reviewed_bridge')
    module.__file__ = str(BRIDGE)
    exec(compile(raw, str(BRIDGE), 'exec'), module.__dict__)
    return module


def capture(process, deadline, ceiling=16384):
    """Drain both pipes concurrently to EOF; no blocking communicate allocation."""
    outputs = {'stdout': bytearray(), 'stderr': bytearray()}
    with selectors.DefaultSelector() as poller:
        for name in outputs:
            pipe = getattr(process, name)
            os.set_blocking(pipe.fileno(), False)
            poller.register(pipe, selectors.EVENT_READ, name)
        while poller.get_map():
            left = deadline - time.monotonic()
            if left <= 0:
                raise CaptureUnknown('PIPE_DEADLINE', outputs)
            for key, _ in poller.select(min(left, 0.1)):
                raw = os.read(key.fileobj.fileno(), 4096)
                if not raw:
                    poller.unregister(key.fileobj)
                else:
                    outputs[key.data].extend(raw)
                    if sum(map(len, outputs.values())) > ceiling:
                        # Bound the retained prefix as well as the next allocation.
                        outputs[key.data] = outputs[key.data][:max(0, ceiling - len(outputs['stderr' if key.data == 'stdout' else 'stdout']))]
                        raise CaptureUnknown('PIPE_LIMIT', outputs)
        process.wait(timeout=max(0.001, deadline - time.monotonic()))
    return {name: bytes(value) for name, value in outputs.items()}


def docker_call(args, records, timeout=5):
    process = subprocess.Popen([DOCKER, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True, close_fds=True,
                               env={'PATH': '/usr/bin:/bin'})
    try:
        output = capture(process, time.monotonic() + timeout, 32768)
        records.append({'argv': [DOCKER, *args], 'exit': process.returncode,
                        **{k: v.decode('utf-8', 'replace') for k, v in output.items()}})
        return process.returncode, output
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=3)
        for pipe in (process.stdout, process.stderr):
            pipe.close()


def durable(root_fd, name, raw):
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o400, dir_fd=root_fd)
    try:
        view = memoryview(raw)
        while view:
            size = os.write(fd, view)
            if size <= 0:
                raise RuntimeError('EVIDENCE_WRITE')
            view = view[size:]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.fsync(root_fd)


def end_group(process):
    """Only the session/group created by this adapter; no PID rediscovery."""
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGKILL)
    process.wait(timeout=3)
    try:
        os.killpg(process.pid, 0)
    except ProcessLookupError:
        return
    os.killpg(process.pid, signal.SIGKILL)
    until = time.monotonic() + 1
    while time.monotonic() < until:
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.01)
    raise RuntimeError('OWNED_GROUP_REMAINS')


def sentinel(root_fd, root, B):
    public = os.open('public', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
    try:
        raw = b'public synthetic writable sentinel; never a Context input\n'
        durable(public, 'writable-sentinel', raw)
        fd = os.open('writable-sentinel', os.O_RDONLY | os.O_NOFOLLOW, dir_fd=public)
        try:
            os.fchmod(fd, 0o644)
            os.fsync(fd)
            info = os.fstat(fd)
        finally:
            os.close(fd)
        # Open after chmod, with this process's ordinary UID, and never write.
        writable = os.open('writable-sentinel', os.O_WRONLY | os.O_NOFOLLOW, dir_fd=public)
        os.close(writable)
        os.fsync(public)
        return {'path': str(root / 'public/writable-sentinel'), 'sha256': B.sha(raw),
                'identity': [info.st_dev, info.st_ino, info.st_uid, info.st_gid,
                             stat.S_IMODE(info.st_mode), info.st_size],
                'parent_write_open_succeeded': True}
    finally:
        os.close(public)


def run(root, child_sha, *, seconds=8, fault='none', docker_probe=False,
        container_name=None):
    """Owned disposable fixture only. Caller retains every consumed attempt."""
    B = bridge()
    root = Path(root)
    B.need(root.is_absolute() and type(seconds) in (int, float) and
           not isinstance(seconds, bool) and 0.1 <= seconds <= 25, 'FIXTURE_SELECTION')
    B.need(fault in {'none', 'crash', 'timeout', 'wrong_token', 'bad_summary',
                    'exit_after_summary', 'stdout_overflow', 'parent_close'}, 'FAULT')
    selected(HERE / 'child.py', child_sha)
    selected(HERE / 'output_guard.py', OUTPUT_GUARD_SHA)
    selected(PYTHON, PYTHON_SHA)
    if docker_probe:
        B.need(fault == 'none' and container_name == 'cal-context-public-child-0002',
               'DOCKER_PROBE_ONLY')
        selected(DOCKER, DOCKER_SHA)
    # Root creation is exclusive. No reset/retry path is implemented.
    parent_fds = B.chain(root.parent)
    root_fd = None
    owned = []
    writer = listener = accepted = process = mediator = None
    cid = None
    commands = []
    output = {'stdout': b'', 'stderr': b''}
    unknown = False
    cleanup_unknown = False
    summary = None
    peer = None
    ready = None
    stage = 'admission'
    output_complete = False
    process_observation = None
    try:
        os.mkdir(root.name, 0o700, dir_fd=parent_fds[-1])
        os.fsync(parent_fds[-1])
        root_fd = os.open(root.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                          dir_fd=parent_fds[-1])
        owned.append(root_fd)
        root_identity = B.identity(os.fstat(root_fd))
        os.mkdir('control', 0o700, dir_fd=root_fd)
        os.mkdir('public', 0o700, dir_fd=root_fd)
        os.fsync(root_fd)
        selected_sentinel = sentinel(root_fd, root, B) if docker_probe else None
        durable(root_fd, 'admission.json', B.encode({'synthetic_only': True, 'docker': docker_probe}))
        deadline = time.monotonic() + float(seconds)
        source = {'path': str(root / 'source-manifest.json'), 'sha256': B.sha(b'{"synthetic":true}')}
        durable(root_fd, 'source-manifest.json', b'{"synthetic":true}')
        output_path = root / 'public/attempt/package'
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        listener.bind(str(root / 'control/ipc'))
        listener.listen(1)
        listener.settimeout(max(0.01, deadline - time.monotonic()))
        config = {'bridge': str(BRIDGE), 'out': str(output_path), 'source': source,
                  'socket': str(root / 'control/ipc'), 'token': os.urandom(16).hex(),
                  'deadline': deadline, 'docker': docker_probe, 'fault': fault,
                  'public_root': str(root / 'public'), 'sentinel': selected_sentinel,
                  'guard_sha256': OUTPUT_GUARD_SHA,
                  'parent_peer': [0 if docker_probe else os.getpid(), os.getuid(), os.getgid()]}
        child_args = ['-I', '-B', '-S', '-X', 'pycache_prefix=' + GUARD]
        if sys.flags.optimize:
            child_args.append('-O')
        child_args += ['-c', BOOTSTRAP, str(HERE / 'child.py'), child_sha, json.dumps(config)]
        if docker_probe:
            code, pre = docker_call(['ps', '-a', '--no-trunc', '--filter',
                                    'name=^' + container_name + '$', '--format', '{{.ID}}'], commands)
            B.need(code == 0 and pre['stdout'] == b'' and pre['stderr'] == b'', 'CONTAINER_EXISTS')
            mounts = []
            for path in (HERE, BRIDGE.parent, Path(GUARD), root / 'control', root / 'public'):
                mounts += ['--mount', 'type=bind,src=' + str(path) + ',dst=' + str(path) + ',readonly']
            args = ['create', '--name', container_name, '--network', 'none', '--read-only',
                    '--user', f'{os.getuid()}:{os.getgid()}', '--userns', 'host',
                    '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                    '--pids-limit', '8', '--memory', '128m', '--cpus', '1',
                    '--ipc', 'none', '--entrypoint', '/usr/local/bin/python3.14',
                    *mounts, IMAGE, *child_args]
            code, created = docker_call(args, commands)
            B.need(code == 0, 'DOCKER_CREATE')
            cid = created['stdout'].decode().strip()
            B.need(len(cid) == 64 and all(c in '0123456789abcdef' for c in cid), 'DOCKER_ID')
            argv = [DOCKER, 'start', '-a', cid]
        else:
            argv = [PYTHON, *child_args]
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True, close_fds=True,
                                   env={'PATH': '/usr/bin:/bin'})
        expected_pid = process.pid
        stage = 'peer'
        if docker_probe:
            expected_pid = 0
            while time.monotonic() < deadline:
                code, inspected = docker_call(['inspect', '--format', '{{.State.Pid}}', cid], commands)
                if code == 0 and inspected['stdout'].strip().isdigit():
                    expected_pid = int(inspected['stdout'])
                    if expected_pid > 0:
                        break
                time.sleep(0.02)
            B.need(expected_pid > 0, 'DOCKER_INIT_PID')
        accepted, _ = listener.accept()
        peer = struct.unpack('3i', accepted.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
        B.need(peer == (expected_pid, os.getuid(), os.getgid()), 'CHILD_PEER')
        proc = Path('/proc') / str(expected_pid)
        stat_raw = (proc / 'stat').read_bytes()
        B.need(0 < len(stat_raw) <= 8192, 'PROC_BOUND')
        process_observation = {'host_pid': expected_pid,
                               'start_ticks': int(stat_raw.rsplit(b') ', 1)[1].split()[19]),
                               'exe': os.readlink(proc / 'exe'),
                               'pid_namespace': os.readlink(proc / 'ns/pid'),
                               'mount_namespace': os.readlink(proc / 'ns/mnt'),
                               'stat_sha256': B.sha(stat_raw)}
        B.configure(accepted)
        ready_raw = B.receive(accepted, peer, deadline)
        ready = {'schema': 'context-child-ready/v1', 'attempt': config['token'],
                 'out': str(output_path), 'original_guard_sha256': config['guard_sha256'],
                 'output_absent': True}
        B.need(ready_raw == B.encode(ready) and not output_path.exists(), 'ORIGINAL_OUTPUT_GUARD')
        writer = B.Writer(root / 'public/attempt', source, deadline)
        B.send(accepted, B.encode({'schema': 'context-child-go/v1',
                                  'ready_sha256': B.sha(ready_raw)}), deadline)
        listener.close()
        listener = None
        mediator = B.Mediator(accepted, peer, config['token'], writer)
        accepted = None  # ownership transferred exactly once
        mediator.start()
        stage = 'capture'
        output = capture(process, deadline)
        output_complete = True
        commands.append({'argv': argv, 'exit': process.returncode})
        B.need(process.returncode == 0 and output['stderr'] == b'', 'CHILD_EXIT')
        B.need(mediator.join(max(0, deadline - time.monotonic())), 'MEDIATOR_JOIN')
        B.need(mediator.state == 'PEER_EOF' and mediator.socket_closed and
               writer.state == 'CLOSED', 'PARENT_COMPLETION')
        stage = 'summary'
        summary = B.parse(output['stdout'], canonical=False)
        expected_summary = {'result': 'PASS',
                            'package_binding': {'path': str(writer.out / 'manifest.json'),
                                                'sha256': writer.digests['manifest.json']},
                            'generated_carriers': 30, 'posture': 'ready', 'public_API_operations_added': 0}
        B.need(set(summary) == {'schema', 'summary', 'pid', 'uid', 'gid', 'closed', 'state',
                                'read_leaves', 'readonly_errno', 'parent_peer', 'runtime',
                                'original_output_guard', 'readonly_mount', 'sentinel'} and
               summary['schema'] == 'context-synthetic-child/v1' and
               B.encode(summary['summary']) == B.encode(expected_summary) and
               summary['closed'] is True and summary['state'] == 'SUMMARY_PERMITTED' and
               summary['read_leaves'] == list(B.LEAVES) and
               summary['parent_peer'] == config['parent_peer'] and
               summary['original_output_guard'] == ready and
               (summary['pid'], summary['uid'], summary['gid']) ==
               (1 if docker_probe else expected_pid, os.getuid(), os.getgid()) and
               (summary['readonly_errno'] in ([13, 30], [30, 30]) if docker_probe else
                summary['readonly_errno'] == []), 'CHILD_SUMMARY')
        if docker_probe:
            mount = summary['readonly_mount']
            B.need(type(mount) is dict and set(mount) ==
                   {'selected_path', 'selected_line', 'mountinfo_sha256', 'mountinfo_size'} and
                   type(mount['selected_line']) is str and len(mount['selected_line']) <= 8192 and
                   B.hex64(mount['mountinfo_sha256']) and type(mount['mountinfo_size']) is int and
                   0 < mount['mountinfo_size'] <= 1024 * 1024, 'MOUNT_REPORT')
            fields = mount['selected_line'].split()
            B.need(summary['sentinel'] == selected_sentinel and
                   mount['selected_path'] == str(root / 'public') and len(fields) >= 10 and
                   fields[4] == str(root / 'public') and 'ro' in fields[5].split(',') and
                   'rw' not in fields[5].split(','), 'CHILD_RO_OBSERVATION')
            selected(selected_sentinel['path'], selected_sentinel['sha256'])
            info = Path(selected_sentinel['path']).stat(follow_symlinks=False)
            B.need([info.st_dev, info.st_ino, info.st_uid, info.st_gid,
                    stat.S_IMODE(info.st_mode), info.st_size] == selected_sentinel['identity'],
                   'SENTINEL_POSTIMAGE')
        else:
            B.need(summary['sentinel'] is None and summary['readonly_mount'] is None,
                   'NO_LOCAL_RO_CLAIM')
        B.need(summary['runtime']['isolated'] == 1 and summary['runtime']['no_site'] == 1 and
               summary['runtime']['bytecode_disabled'] is True and
               summary['runtime']['cache_prefix_regular_file'] is True, 'CHILD_RUNTIME')
        writer.postclose()
        stage = 'postclose'
    except BaseException as error:
        if type(error) is CaptureUnknown:
            output = error.outputs
        unknown = True
    finally:
        # All already-owned resources are attempted independently once.
        if process is not None:
            try:
                end_group(process)
            except BaseException:
                cleanup_unknown = True
            if not output_complete and not any(output.values()):
                try:
                    output = capture(process, time.monotonic() + 0.5)
                    output_complete = True
                except BaseException as error:
                    if type(error) is CaptureUnknown:
                        output = error.outputs
            for pipe in (process.stdout, process.stderr):
                try:
                    pipe.close()
                except BaseException:
                    cleanup_unknown = True
        if mediator is not None:
            try:
                if not mediator.join(1):
                    mediator.sock.shutdown(socket.SHUT_RDWR)
                    if not mediator.join(2):
                        cleanup_unknown = True
            except BaseException:
                cleanup_unknown = True
        for sock in (accepted, listener):
            if sock is not None:
                try:
                    sock.close()
                except BaseException:
                    cleanup_unknown = True
        if writer is not None and writer.state != 'CLOSED':
            writer.abort()
        if cid is not None:
            try:
                code, inspected = docker_call(['inspect', '--format', '{{.State.ExitCode}}', cid], commands)
                if not unknown:
                    B.need(code == 0 and inspected['stdout'] == b'0\n',
                           'DOCKER_EXIT')
            except BaseException:
                cleanup_unknown = True
            try:
                code, _ = docker_call(['rm', '-f', cid], commands)
                B.need(code == 0, 'DOCKER_REMOVE')
                code, absent = docker_call(['inspect', '--type', 'container', cid], commands)
                B.need(code == 1 and absent['stdout'] == b'[]\n' and
                       absent['stderr'] == f'Error response from daemon: No such container: {cid}\n'.encode(),
                       'DOCKER_ABSENCE')
                code, absent_name = docker_call(['ps', '-a', '--no-trunc', '--filter',
                                                'name=^' + container_name + '$',
                                                '--format', '{{.ID}}'], commands)
                B.need(code == 0 and absent_name['stdout'] == b'' and
                       absent_name['stderr'] == b'', 'DOCKER_NAME_ABSENCE')
            except BaseException:
                cleanup_unknown = True
        evidence = {'schema': 'context-child-evidence/v1', 'status': 'PROVISIONAL',
                    'unknown': unknown, 'cleanup_unknown': cleanup_unknown,
                    'last_stage': stage, 'process_observation': process_observation,
                    'original_guard_ready': ready,
                    'output_complete': output_complete,
                    'child_exit': None if process is None else process.returncode,
                    'peer': peer, 'stdout': output['stdout'].decode('utf-8', 'replace'),
                    'stderr': output['stderr'].decode('utf-8', 'replace'),
                    'commands': commands, 'docker_id': cid, 'child_report': summary,
                    'writer_trace': [] if writer is None else writer.trace,
                    'mediator_trace': [] if mediator is None else mediator.trace}
        raw = B.encode(evidence)
        try:
            B.need(root_fd is not None and B.identity(root.stat(follow_symlinks=False)) ==
                   root_identity, 'ROOT_ATTACHMENT')
            durable(root_fd, 'observation.json', raw)
        except BaseException:
            cleanup_unknown = True
        for fd in reversed(owned + parent_fds):
            try:
                os.close(fd)
            except BaseException:
                cleanup_unknown = True
        if fault == 'parent_close':
            cleanup_unknown = True
        try:
            B.need(B.identity(root.stat(follow_symlinks=False)) == root_identity, 'POSTCLOSE_ROOT')
            B.need(selected(root / 'observation.json', B.sha(raw)) == raw, 'POSTCLOSE_EVIDENCE')
            if writer is not None and writer.state == 'CLOSED':
                writer.postclose()
        except BaseException:
            cleanup_unknown = True
    return {'result': 'UNKNOWN' if unknown or cleanup_unknown else 'PASS_SYNTHETIC_ONLY',
            'observation_sha256': B.sha(raw), 'root': str(root),
            'docker_readonly_proved': bool(docker_probe and not unknown and not cleanup_unknown),
            'original_Context': 'NOT_RUN', 'effect_enabled': False}


def launch_context(*args, **kwargs):
    raise RuntimeError('ACTUAL_CONTEXT_EFFECT_DISABLED')
