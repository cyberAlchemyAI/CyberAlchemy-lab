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
PYTHON = '/usr/bin/python3.14'
PYTHON_SHA = '52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'
DOCKER = '/usr/bin/docker'
DOCKER_SHA = '999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
GUARD = '/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-02/python-bytecode-cache-disabled-0002'
EFFECT_ENABLED = False
# Bootstrap compiles the exact retained bytes whose digest was checked.
BOOTSTRAP = (
    "import hashlib,pathlib,sys;"
    "p=pathlib.Path(sys.argv.pop(1));h=sys.argv.pop(1);r=p.read_bytes();"
    "assert hashlib.sha256(r).hexdigest()==h,'CHILD_PREIMAGE';"
    "exec(compile(r,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})"
)
# No assert-based safety under -O.
BOOTSTRAP = BOOTSTRAP.replace(
    "assert hashlib.sha256(r).hexdigest()==h,'CHILD_PREIMAGE';",
    "exec(\"if hashlib.sha256(r).hexdigest()!=h: raise RuntimeError('CHILD_PREIMAGE')\");")


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
                raise RuntimeError('PIPE_DEADLINE')
            for key, _ in poller.select(min(left, 0.1)):
                raw = os.read(key.fileobj.fileno(), 4096)
                if not raw:
                    poller.unregister(key.fileobj)
                else:
                    outputs[key.data].extend(raw)
                    if sum(map(len, outputs.values())) > ceiling:
                        raise RuntimeError('PIPE_LIMIT')
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
    selected(PYTHON, PYTHON_SHA)
    if docker_probe:
        B.need(fault == 'none' and container_name == 'cal-context-public-child-0001',
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
    try:
        os.mkdir(root.name, 0o700, dir_fd=parent_fds[-1])
        os.fsync(parent_fds[-1])
        root_fd = os.open(root.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                          dir_fd=parent_fds[-1])
        owned.append(root_fd)
        root_identity = B.identity(os.fstat(root_fd))
        os.mkdir('control', 0o700, dir_fd=root_fd)
        os.fsync(root_fd)
        durable(root_fd, 'admission.json', B.encode({'synthetic_only': True, 'docker': docker_probe}))
        deadline = time.monotonic() + float(seconds)
        source = {'path': str(root / 'source-manifest.json'), 'sha256': B.sha(b'{"synthetic":true}')}
        durable(root_fd, 'source-manifest.json', b'{"synthetic":true}')
        writer = B.Writer(root / 'attempt', source, deadline)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        listener.bind(str(root / 'control/ipc'))
        listener.listen(1)
        listener.settimeout(max(0.01, deadline - time.monotonic()))
        config = {'bridge': str(BRIDGE), 'out': str(writer.out), 'source': source,
                  'socket': str(root / 'control/ipc'), 'token': os.urandom(16).hex(),
                  'deadline': deadline, 'docker': docker_probe, 'fault': fault,
                  'parent_peer': [0 if docker_probe else os.getpid(), os.getuid(), os.getgid()]}
        child_args = ['-B', '-S', '-X', 'pycache_prefix=' + GUARD]
        if sys.flags.optimize:
            child_args.append('-O')
        child_args += ['-c', BOOTSTRAP, str(HERE / 'child.py'), child_sha, json.dumps(config)]
        if docker_probe:
            code, pre = docker_call(['ps', '-a', '--no-trunc', '--filter',
                                    'name=^' + container_name + '$', '--format', '{{.ID}}'], commands)
            B.need(code == 0 and pre['stdout'] == b'' and pre['stderr'] == b'', 'CONTAINER_EXISTS')
            mounts = []
            for path in (HERE, BRIDGE.parent, Path(GUARD), root / 'control', writer.out):
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
        listener.close()
        listener = None
        mediator = B.Mediator(accepted, peer, config['token'], writer)
        accepted = None  # ownership transferred exactly once
        mediator.start()
        output = capture(process, deadline)
        commands.append({'argv': argv, 'exit': process.returncode})
        B.need(process.returncode == 0 and output['stderr'] == b'', 'CHILD_EXIT')
        B.need(mediator.join(max(0, deadline - time.monotonic())), 'MEDIATOR_JOIN')
        B.need(mediator.state == 'PEER_EOF' and mediator.socket_closed and
               writer.state == 'CLOSED', 'PARENT_COMPLETION')
        summary = B.parse(output['stdout'], canonical=False)
        expected_summary = {'result': 'PASS',
                            'package_binding': {'path': str(writer.out / 'manifest.json'),
                                                'sha256': writer.digests['manifest.json']},
                            'generated_carriers': 30, 'posture': 'ready', 'public_API_operations_added': 0}
        B.need(set(summary) == {'schema', 'summary', 'pid', 'uid', 'gid', 'closed', 'state',
                                'read_leaves', 'readonly_errno', 'parent_peer'} and
               summary['schema'] == 'context-synthetic-child/v1' and
               B.encode(summary['summary']) == B.encode(expected_summary) and
               summary['closed'] is True and summary['state'] == 'SUMMARY_PERMITTED' and
               summary['read_leaves'] == list(B.LEAVES) and
               summary['parent_peer'] == config['parent_peer'] and
               (summary['pid'], summary['uid'], summary['gid']) ==
               (1 if docker_probe else expected_pid, os.getuid(), os.getgid()) and
               summary['readonly_errno'] == ([30, 30] if docker_probe else []), 'CHILD_SUMMARY')
        writer.postclose()
    except BaseException:
        unknown = True
    finally:
        # All already-owned resources are attempted independently once.
        if process is not None:
            try:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=3)
            except BaseException:
                cleanup_unknown = True
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
                    B.need(code == 0 and inspected['stdout'] == b'0\\n'.replace(b'\\n', b'\n'),
                           'DOCKER_EXIT')
                code, _ = docker_call(['rm', '-f', cid], commands)
                B.need(code == 0, 'DOCKER_REMOVE')
                code, absent = docker_call(['inspect', '--type', 'container', cid], commands)
                B.need(code == 1 and absent['stdout'] == b'[]\n' and
                       absent['stderr'] == f'Error response from daemon: No such container: {cid}\n'.encode(),
                       'DOCKER_ABSENCE')
            except BaseException:
                cleanup_unknown = True
        evidence = {'schema': 'context-child-evidence/v1', 'status': 'PROVISIONAL',
                    'unknown': unknown, 'cleanup_unknown': cleanup_unknown,
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
