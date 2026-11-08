"""Effect-disabled fixed Docker controller candidate. Synthetic public inputs only."""
import json
import os
from pathlib import Path, PurePosixPath
import socket
import struct
import subprocess
import threading
import time

import wire_bridge as B
import prior_io as IO

EFFECT_ENABLED = False
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
ROLE = 'product/lab/release-candidates/v1/interface/context-runner-synthetic-0001'
CHILD_HERE = Path('/workspace') / ROLE
NAME = 'cal-context-docker-runner-0001'
GUARD_SHA = '1d320473ba057e508a1b52176c556cd2f368e3edfc4f8de4d7de076edf831538'
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'


def path(value):
    B.need(type(value) is str and value.startswith('/') and '\0' not in value and
           ',' not in value and '\\' not in value and
           all(p not in ('', '.', '..') for p in value[1:].split('/')), 'ABSOLUTE_PATH')
    return Path(value)


def topology(value):
    B.need(type(value) is dict and set(value) ==
           {'public', 'control', 'code', 'cache_guard', 'native', 'private', 'uid', 'gid'},
           'TOPOLOGY_FIELDS')
    result = {k: path(value[k]) for k in ('public', 'control', 'code', 'cache_guard',
                                        'native', 'private')}
    for a in result:
        for b in result:
            if a != b:
                B.need(result[a] != result[b] and result[a] not in result[b].parents,
                       'MOUNT_ALIAS_OR_PRIVATE_EXPOSURE')
    B.need(type(value['uid']) is int and type(value['gid']) is int and
           value['uid'] == os.getuid() and value['gid'] == os.getgid(), 'SELECTED_IDENTITY')
    return result


def argv(value, child_sha, config):
    roots = topology(value)
    B.need(B.hex64(child_sha) and type(config) is dict and config.get('fixture_only') is True,
           'CHILD_SELECTION')
    mounts = [('public', '/workspace'), ('control', '/control'), ('code', '/runner'),
              ('cache_guard', '/cache-disabled'), ('native', '/selected-native')]
    command = [IO.DOCKER, 'create', '--name', NAME, '--network', 'none', '--read-only',
               '--user', f"{value['uid']}:{value['gid']}", '--userns', 'host',
               '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
               '--pids-limit', '8', '--memory', '128m', '--cpus', '1', '--ipc', 'none',
               '--entrypoint', '/usr/local/bin/python3.14']
    for source, target in mounts:
        command += ['--mount', f'type=bind,src={roots[source]},dst={target},readonly']
    command += [IMAGE, '-I', '-B', '-S', '-X', 'pycache_prefix=/cache-disabled',
                '-c', IO.BOOTSTRAP, '/runner/child.py', child_sha,
                json.dumps(config, sort_keys=True, separators=(',', ':'))]
    return command


class Writer(B.Writer):
    def __init__(self, physical_here, logical_here, source, deadline):
        physical_here, logical_here = Path(physical_here), Path(logical_here)
        B.need(physical_here.is_absolute() and logical_here == CHILD_HERE, 'WRITER_VIEWS')
        self.wire_out = logical_here / 'packages/0001'
        # All physical opens, attachment checks and post-close checks still use
        # the unchanged base path/out fields. Only emitted row bindings differ.
        super().__init__(physical_here / 'packages', source, deadline)


class Parent:
    def __init__(self, sock, peer, physical_here, source, token, deadline):
        B.transport_selection(peer, token, deadline)
        B.configure(sock)
        self.sock, self.peer, self.here = sock, peer, Path(physical_here)
        self.source, self.token, self.deadline = source, token, deadline
        self.writer = self.mediator = self.thread = None
        self.joined = False
        self.state = 'NEW'

    def start(self):
        B.need(self.state == 'NEW', 'PARENT_ONCE')
        self.state = 'WAIT_READY'
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        transferred = False
        try:
            raw = B.receive(self.sock, self.peer, self.deadline)
            expected = {'schema': 'context-child-ready/v1', 'attempt': self.token,
                        'out': str(CHILD_HERE / 'packages/0001'),
                        'original_guard_sha256': GUARD_SHA, 'output_absent': True}
            B.need(raw == B.encode(expected) and not os.path.lexists(self.here / 'packages'),
                   'ORIGINAL_READY_SCOPE')
            self.writer = Writer(self.here, CHILD_HERE, self.source, self.deadline)
            B.send(self.sock, B.encode({'schema': 'context-child-go/v1',
                                       'ready_sha256': B.sha(raw)}), self.deadline)
            self.mediator = B.Mediator(self.sock, self.peer, self.token, self.writer)
            self.mediator.start()
            transferred = True
            self.state = 'MEDIATING'
        except BaseException:
            self.state = 'UNKNOWN'
            if self.writer:
                self.writer.abort()
        finally:
            if not transferred:
                try:
                    self.sock.close()
                except BaseException:
                    self.state = 'UNKNOWN'

    def join(self):
        B.need(self.thread is not None, 'NOT_STARTED')
        self.thread.join(max(0, self.deadline - time.monotonic()))
        B.need(not self.thread.is_alive() and self.state == 'MEDIATING', 'READY_UNKNOWN')
        B.need(self.mediator.join(max(0, self.deadline - time.monotonic())), 'JOIN_UNKNOWN')
        self.joined = True


def peer_join(sock, inspected_pid, selected_uid, selected_gid):
    B.need(type(inspected_pid) is int and inspected_pid > 0, 'INSPECT_PID')
    peer = struct.unpack('3i', sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
    B.need(peer == (inspected_pid, selected_uid, selected_gid), 'DOCKER_SOCKET_PEER')
    return peer


def absent(code, stdout, stderr, cid):
    return (type(code) is int and code == 1 and stdout == b'[]\n' and
            stderr == f'Error response from daemon: No such container: {cid}\n'.encode())


def aggregate(parent, child_raw, os_exit, stderr, cleanup, absent_cid, absent_name):
    """No original child PASS is released; return only aggregate synthetic verdict."""
    B.need(type(os_exit) is int and os_exit == 0 and stderr == b'' and cleanup is True
           and absent_cid is True and absent_name is True, 'OS_CLEANUP_UNKNOWN')
    m, w = parent.mediator, parent.writer
    B.need(parent.joined and m is not None and m._joined and m.run_completed and
           not m._thread.is_alive() and m.socket_closed and m.state == 'PEER_EOF' and
           w.state == 'CLOSED', 'AGGREGATE_UNKNOWN')
    B.need(type(child_raw) is bytes and 0 < len(child_raw) <= 8192, 'CHILD_STDOUT_BOUND')
    value = B.parse(child_raw, canonical=False)
    expected = {'result': 'PASS', 'package_binding':
                {'path': str(w.wire_out / 'manifest.json'), 'sha256': w.digests['manifest.json']},
                'generated_carriers': 30, 'posture': 'ready', 'public_API_operations_added': 0}
    B.need(value == expected, 'CHILD_SUMMARY')
    w.postclose()
    return {'result': 'PASS_SYNTHETIC_ONLY', 'effect': 'synthetic_fixture_only',
            'child_original_summary': 'PROVISIONAL_NOT_PUBLIC_AUTHORITY',
            'physical_output': str(w.out), 'logical_output': str(w.wire_out),
            'manifest_sha256': w.digests['manifest.json'], 'leaves': len(w.rows)}


def execute(*args, **kwargs):
    # No effect-enabled selector exists in this release. This is checked before
    # any admission directory, Docker query or subprocess launch.
    raise RuntimeError('DOCKER_CONTEXT_EFFECT_DISABLED')


def docker_call(args, records):
    code, output = IO.docker_call(args, records)
    return code, output['stdout'], output['stderr']


def controller_candidate(root, value, bindings):
    """Complete synthetic lifecycle body; this revision refuses before any IO.

    Enabling requires a successor with independently selected release/attempt
    and a new static review. This bool is an effect gate, not Python isolation.
    """
    B.need(EFFECT_ENABLED is True, 'DOCKER_CONTEXT_EFFECT_DISABLED')
    root = path(str(root))
    roots = topology(value)
    B.need(roots['public'] == root / 'public' and roots['control'] == root / 'control'
           and roots['private'] == root / 'private-unmounted', 'ATTEMPT_TOPOLOGY')
    B.need(type(bindings) is dict and set(bindings) ==
           {'child.py', 'wire_bridge.py', 'hooks.py', 'projected-build-inert.py', 'encoder-source.py'},
           'CODE_SELECTION')
    for name, digest in bindings.items():
        IO.selected(roots['code'] / name, digest)
    IO.selected(IO.DOCKER, IO.DOCKER_SHA)
    IO.selected(roots['cache_guard'], 'a5712f1655f68e6f8fe7cacbfb454dc0be0cd1ad8f22f1788fbad7b8adafae29')
    IO.selected(roots['native'], NATIVE_SHA)
    commands = []
    code, out, err = docker_call(['ps', '-a', '--no-trunc', '--filter',
                                   f'name=^{NAME}$', '--format', '{{.ID}}'], commands)
    B.need(code == 0 and out == b'' and err == b'' and not os.path.lexists(root),
           'ATTEMPT_ALREADY_PRESENT')
    ancestors = B.chain(root.parent)
    handles, listener, accepted, process, parent, cid = [], None, None, None, None, None
    streams = {'stdout': b'', 'stderr': b''}
    result, failure, cleanup_unknown, gone, named_gone = None, False, False, False, False
    deadline = time.monotonic() + 25.0
    try:
        os.mkdir(root.name, 0o700, dir_fd=ancestors[-1])
        fd = os.open(root.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                     dir_fd=ancestors[-1])
        handles.append(fd)
        root_identity = B.identity(os.fstat(fd))
        os.fsync(fd)
        os.fsync(ancestors[-1])
        for name in ('public', 'control'):
            os.mkdir(name, 0o700, dir_fd=fd)
        os.fsync(fd)
        here = roots['public'] / ROLE
        here.mkdir(parents=True, mode=0o700)
        source_bytes = b'{"synthetic_public_only":true}\n'
        here_fd = os.open(here, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            IO.durable(here_fd, 'source-manifest.json', source_bytes)
        finally:
            os.close(here_fd)
        # Seal all newly named family ancestors before READY can be accepted.
        hierarchy = B.chain(here)
        try:
            for directory in reversed(hierarchy):
                os.fsync(directory)
        finally:
            B.close_all(hierarchy)
        token = os.urandom(16).hex()
        config = {'fixture_only': True, 'token': token, 'deadline': deadline,
                  'wire_sha': bindings['wire_bridge.py'], 'hooks_sha': bindings['hooks.py'],
                  'build_sha': bindings['projected-build-inert.py'],
                  'encoder_sha': bindings['encoder-source.py']}
        command = argv(value, bindings['child.py'], config)
        IO.durable(fd, 'admission.json', B.encode({'schema': 'context-runner-admission/v1',
                   'status': 'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_RETURN', 'argv': command,
                   'bindings': bindings, 'topology': value, 'root_identity': root_identity}))
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        listener.bind(str(roots['control'] / 'ipc'))
        listener.listen(1)
        code, out, err = docker_call(command[1:], commands)
        B.need(code == 0 and err == b'', 'CREATE_FAILED')
        candidate = out.decode('ascii').strip()
        B.need(B.hex64(candidate), 'CID_SHAPE')
        cid = candidate
        process = subprocess.Popen([IO.DOCKER, 'start', '-a', cid], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env={'PATH': '/usr/bin:/bin'},
                                   close_fds=True, start_new_session=True)
        pid = 0
        while not pid:
            B.need(time.monotonic() < deadline and process.poll() is None, 'START_UNKNOWN')
            code, out, err = docker_call(['inspect', '--type', 'container', cid], commands)
            B.need(code == 0 and err == b'', 'INSPECT_UNKNOWN')
            observation = json.loads(out)
            B.need(type(observation) is list and len(observation) == 1 and
                   observation[0]['Id'] == cid, 'CID_IDENTITY')
            pid = observation[0]['State']['Pid']
            if not pid:
                time.sleep(0.01)
        listener.settimeout(max(0.001, deadline - time.monotonic()))
        accepted, _ = listener.accept()
        peer = peer_join(accepted, pid, value['uid'], value['gid'])
        source = {'path': str(CHILD_HERE / 'source-manifest.json'), 'sha256': B.sha(source_bytes)}
        parent = Parent(accepted, peer, here, source, token, deadline)
        parent.start()
        accepted = None  # Parent owns the accepted connection exactly once.
        try:
            streams = IO.capture(process, deadline, 8192)
        except IO.CaptureUnknown as capture_error:
            streams = capture_error.outputs
            raise
        parent.join()
    except BaseException:
        failure = True
    finally:
        # Each already-owned resource gets an independent cleanup attempt.
        if process is not None:
            try:
                IO.end_group(process)
                # Drain after reap as well; never snapshot an undrained stream.
                late = IO.capture(process, time.monotonic() + 1.0, 8192)
                for key in streams:
                    streams[key] += late[key]
                    B.need(len(streams[key]) <= 8192, 'STREAM_TOTAL_BOUND')
            except BaseException:
                cleanup_unknown = True
            for pipe in (process.stdout, process.stderr):
                try:
                    pipe.close()
                except BaseException:
                    cleanup_unknown = True
        for sock in (accepted, listener):
            if sock is not None:
                try:
                    sock.close()
                except BaseException:
                    cleanup_unknown = True
        if parent is not None:
            try:
                if not parent.joined:
                    parent.sock.shutdown(socket.SHUT_RDWR)
                    parent.join()
            except BaseException:
                cleanup_unknown = True
            if parent.writer is not None and parent.writer.state != 'CLOSED':
                parent.writer.abort()
        if cid is not None:
            try:
                code, out, err = docker_call(['rm', '-f', cid], commands)
                B.need(code == 0 and err == b'' and out.strip() == cid.encode(), 'REMOVE_UNKNOWN')
                code, out, err = docker_call(['inspect', '--type', 'container', cid], commands)
                gone = absent(code, out, err, cid)
                code, out, err = docker_call(['ps', '-a', '--no-trunc', '--filter',
                                               f'name=^{NAME}$', '--format', '{{.ID}}'], commands)
                named_gone = code == 0 and out == b'' and err == b''
            except BaseException:
                cleanup_unknown = True
        try:
            B.need(not failure and parent is not None, 'CONTROLLER_UNKNOWN')
            result = aggregate(parent, streams['stdout'], process.returncode, streams['stderr'],
                               not cleanup_unknown, gone, named_gone)
        except BaseException:
            failure = True
        try:
            if handles:
                observation = {'status': 'PROVISIONAL', 'candidate_result': result,
                               'unknown': failure or cleanup_unknown, 'commands': commands,
                               'cid': cid, 'cid_absent': gone, 'name_absent': named_gone,
                               'os_exit': None if process is None else process.returncode,
                               'stdout': streams['stdout'].decode('utf-8', 'replace'),
                               'stderr': streams['stderr'].decode('utf-8', 'replace')}
                raw = B.encode(observation)
                IO.durable(handles[0], 'observation.json', raw)
        except BaseException:
            cleanup_unknown = True
        try:
            B.close_all(handles + ancestors)
        except BaseException:
            cleanup_unknown = True
    B.need(not failure and not cleanup_unknown and result is not None, 'CONTROLLER_UNKNOWN')
    B.need(B.identity(root.lstat()) == root_identity, 'POSTCLOSE_ROOT')
    # A finalizer failure cannot leave an authoritative PASS in the evidence.
    IO.selected(root / 'observation.json', B.sha(raw))
    parent.writer.postclose()
    return result


def launch_plan(value, child_sha, config):
    """Fixed lifecycle for the next reviewed release, not an effect dispatcher."""
    command = argv(value, child_sha, config)
    return {'schema': 'context-docker-lifecycle/v1-disabled', 'effect_enabled': False,
            'create_argv': command, 'start_argv': [IO.DOCKER, 'start', '-a', '<exact-created-cid>'],
            'inspect_argv': [IO.DOCKER, 'inspect', '--type', 'container', '<exact-created-cid>'],
            'remove_argv': [IO.DOCKER, 'rm', '-f', '<exact-created-cid>'],
            'name_absence_argv': [IO.DOCKER, 'ps', '-a', '--no-trunc', '--filter',
                                  f'name=^{NAME}$', '--format', '{{.ID}}'],
            'deadline_seconds': 25, 'capture_bytes_per_stream': 16384,
            'release': 'only_after_child_OS_exit_mediator_join_all_closes_readback_and_CID_name_absence',
            'open_integration': 'controller body disabled; release selection and external OS observer remain uninstalled'}
