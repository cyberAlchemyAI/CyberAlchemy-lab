"""Owned ordinary local sockets/files only. Docker and original roles never run."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import time
import types
import unittest
from unittest import mock

import wire_bridge as B
import runner as R
import project as P
import child as C
import prior_io as IO

HERE = Path(__file__).resolve().parent


def ready(sock, token, deadline, out=None):
    raw = B.encode({'schema': 'context-child-ready/v1', 'attempt': token,
                    'out': str(out or R.CHILD_HERE / 'packages/0001'),
                    'original_guard_sha256': R.GUARD_SHA, 'output_absent': True})
    B.send(sock, raw, deadline)
    B.need(B.receive(sock, B.credentials(), deadline) ==
           B.encode({'schema': 'context-child-go/v1', 'ready_sha256': B.sha(raw)}), 'GO')


def manifest(client):
    return {'schema_version': 'lab-actual-context-delivery-package/v1-candidate',
            'files': sorted(client.rows, key=lambda row: row['path']),
            'source_manifest_binding': client.source, 'authority_effect': 'none',
            'actual_owner_outcome': None, 'delivery_binding': client.rows[35],
            'provenance_binding': client.rows[37], 'claim_ceiling': B.CLAIM}


def send_package(client, physical_out, bad_manifest=False):
    for index, leaf in enumerate(B.LEAVES[:38]):
        raw = B.encode({'synthetic_public_body': index})
        client.emit(client.out / leaf, raw)
        # Host view oracle only; Docker child visibility remains unexecuted.
        B.need((physical_out / leaf).read_bytes() == raw, 'ACK_BEFORE_VISIBLE')
    client.release_private()
    client.emit(client.out / B.LEAVES[38], b'{"fixture":true}')
    value = manifest(client)
    if bad_manifest:
        value['files'][0]['path'] = str(physical_out / B.LEAVES[0])
    raw = B.encode(value)
    client.emit(client.out / B.LEAVES[39], raw)
    return B.encode({'result': 'PASS', 'package_binding':
                     {'path': str(client.out / 'manifest.json'), 'sha256': B.sha(raw)},
                     'generated_carriers': 30, 'posture': 'ready', 'public_API_operations_added': 0})


class Fixture:
    def __init__(self, close_fault=False):
        self.tmp = tempfile.TemporaryDirectory(prefix='context-docker-runner-test-')
        self.here = Path(self.tmp.name) / 'physical-family'
        self.here.mkdir()
        self.source = {'path': str(R.CHILD_HERE / 'source-manifest.json'), 'sha256': 'a' * 64}
        self.deadline = time.monotonic() + 2.0
        self.cs, self.ps = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        B.configure(self.cs)
        if close_fault:
            self.ps = CloseFault(self.ps)
        self.parent = R.Parent(self.ps, B.credentials(), self.here, self.source, 'a' * 32, self.deadline)
        self.client = B.Client(self.cs, B.credentials(), 'a' * 32,
                               R.CHILD_HERE / 'packages/0001', self.source, self.deadline)

    def complete(self):
        self.parent.start()
        if (self.here / 'packages').exists():
            raise RuntimeError('PRECREATED')
        ready(self.cs, 'a' * 32, self.deadline)
        raw = send_package(self.client, self.here / 'packages/0001')
        self.parent.join()
        return raw

    def close(self):
        with contextlib.suppress(BaseException):
            self.client.close_once()
        with contextlib.suppress(BaseException):
            self.ps.shutdown(socket.SHUT_RDWR)
        if self.parent.thread:
            self.parent.thread.join(3)
        if self.parent.mediator:
            self.parent.mediator.join(3)
        if self.parent.writer and self.parent.writer.state != 'CLOSED':
            self.parent.writer.abort()
        with contextlib.suppress(BaseException):
            self.ps.close()
        for directory, _, _ in os.walk(self.tmp.name):
            os.chmod(directory, 0o700)
        self.tmp.cleanup()


class CloseFault:
    def __init__(self, sock):
        self.sock = sock
    def __getattr__(self, name):
        return getattr(self.sock, name)
    def close(self):
        self.sock.close()
        raise OSError('fixture')


class Tests(unittest.TestCase):
    def fixture(self, **kwargs):
        f = Fixture(**kwargs)
        self.addCleanup(f.close)
        return f

    def topology(self):
        return {**{key: '/tmp/selected-' + key for key in
                   ('public', 'control', 'code', 'cache_guard', 'native', 'private')},
                'uid': os.getuid(), 'gid': os.getgid()}

    def test_projection_inverse_exact(self):
        original = HERE.parent / 'context-original-bridge-0001/layout_bridge.py'
        self.assertEqual(P.project(original.read_bytes()), (HERE / 'wire_bridge.py').read_bytes())
        with self.assertRaisesRegex(RuntimeError, 'PREIMAGE'):
            P.project(original.read_bytes() + b'\n')

    def test_views_full40_and_finish41(self):
        f = self.fixture()
        raw = f.complete()
        result = R.aggregate(f.parent, raw, 0, b'', True, True, True)
        self.assertEqual(result['result'], 'PASS_SYNTHETIC_ONLY')
        self.assertEqual(len(f.parent.writer.rows), 40)
        self.assertNotEqual(f.parent.writer.out, f.parent.writer.wire_out)
        self.assertTrue(all(r['path'].startswith('/workspace/') for r in f.parent.writer.rows))
        self.assertEqual(f.parent.mediator.seq, 42)
        self.assertEqual(f.parent.mediator.trace[-1][1:3], ('FINISH', 41))

    def test_host_path_manifest_refuses(self):
        f = self.fixture()
        f.parent.start()
        ready(f.cs, 'a' * 32, f.deadline)
        with self.assertRaises(BaseException):
            send_package(f.client, f.here / 'packages/0001', True)
        self.assertFalse((f.here / 'packages/0001/manifest.json').exists())

    def test_wrong_ready_path_creates_nothing(self):
        f = self.fixture()
        f.parent.start()
        with self.assertRaises(BaseException):
            ready(f.cs, 'a' * 32, f.deadline, f.here / 'packages/0001')
        f.parent.thread.join(2)
        self.assertFalse((f.here / 'packages').exists())

    def test_existing_empty_packages_refuses(self):
        f = self.fixture()
        (f.here / 'packages').mkdir()
        f.parent.start()
        with self.assertRaises(BaseException):
            ready(f.cs, 'a' * 32, f.deadline)
        self.assertEqual(list((f.here / 'packages').iterdir()), [])

    def test_symlink_parent_refuses(self):
        f = self.fixture()
        alias = f.here.parent / 'alias'
        alias.symlink_to(f.here)
        with self.assertRaises(BaseException):
            R.Writer(alias, R.CHILD_HERE, f.source, f.deadline)
        self.assertFalse((f.here / 'packages').exists())

    def test_parent_close_fault_prevents_aggregate(self):
        f = self.fixture(close_fault=True)
        raw = f.complete()
        with self.assertRaisesRegex(B.Unknown, 'AGGREGATE'):
            R.aggregate(f.parent, raw, 0, b'', True, True, True)

    def test_os_cleanup_and_absence_required(self):
        f = self.fixture()
        raw = f.complete()
        for fields in [(1, b'', True, True, True), (0, b'error', True, True, True),
                       (0, b'', False, True, True), (0, b'', True, False, True),
                       (0, b'', True, True, False)]:
            with self.subTest(fields=fields), self.assertRaises(B.Unknown):
                R.aggregate(f.parent, raw, *fields)

    def test_wrong_summary_refuses(self):
        f = self.fixture()
        raw = f.complete()
        value = json.loads(raw)
        value['package_binding']['path'] = str(f.parent.writer.out / 'manifest.json')
        with self.assertRaisesRegex(B.Unknown, 'SUMMARY'):
            R.aggregate(f.parent, B.encode(value), 0, b'', True, True, True)

    def test_final_readback_detects_replacement(self):
        f = self.fixture()
        raw = f.complete()
        out = f.parent.writer.out
        os.chmod(out, 0o700)
        (out / 'request.json').unlink()
        (out / 'request.json').write_bytes(b'changed')
        with self.assertRaises(B.Unknown):
            R.aggregate(f.parent, raw, 0, b'', True, True, True)

    def test_no_go_before_guard(self):
        f = self.fixture()
        f.parent.start()
        self.assertIsNone(f.parent.writer)
        self.assertFalse((f.here / 'packages').exists())
        f.cs.close()
        f.parent.thread.join(2)
        self.assertEqual(f.parent.state, 'UNKNOWN')

    def test_docker_mounts_no_private(self):
        value = self.topology()
        args = R.argv(value, 'a' * 64, {'fixture_only': True})
        mounts = [args[i + 1] for i, a in enumerate(args) if a == '--mount']
        self.assertEqual(len(mounts), 5)
        self.assertTrue(all(m.endswith(',readonly') for m in mounts))
        self.assertFalse(any(value['private'] in m for m in mounts))
        self.assertFalse(any('packages/0001' in m for m in mounts))
        for pair in [('--network', 'none'), ('--cap-drop', 'ALL'), ('--pids-limit', '8'),
                     ('--memory', '128m'), ('--entrypoint', '/usr/local/bin/python3.14')]:
            self.assertEqual(args[args.index(pair[0]) + 1], pair[1])
        self.assertIn(R.IMAGE, args)

    def test_private_alias_refused(self):
        value = self.topology()
        for key in ('public', 'control', 'code'):
            changed = dict(value, private=value[key] + '/private')
            with self.assertRaisesRegex(B.Unknown, 'EXPOSURE'):
                R.topology(changed)

    def test_mount_argv_injection_refused(self):
        for bad in ['/tmp/a,readonly=false', '/tmp/a/../b', '/tmp//a', '/tmp/a\0b']:
            with self.assertRaises(B.Unknown):
                R.argv(dict(self.topology(), public=bad), 'a' * 64, {'fixture_only': True})

    def test_peer_kernel_tuple(self):
        a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        try:
            self.assertEqual(R.peer_join(a, os.getpid(), os.getuid(), os.getgid()), B.credentials())
            for pid in (0, True, os.getpid() + 1):
                with self.assertRaises(B.Unknown):
                    R.peer_join(a, pid, os.getuid(), os.getgid())
        finally:
            a.close()
            b.close()

    def test_exact_absence_grammar(self):
        cid = 'b' * 64
        self.assertTrue(R.absent(1, b'[]\n',
                                f'Error response from daemon: No such container: {cid}\n'.encode(), cid))
        self.assertFalse(R.absent(1, b'[]\n', b'permission denied\n', cid))

    def test_disabled_before_process_or_root(self):
        with mock.patch.object(IO, 'docker_call', side_effect=AssertionError('effect')), \
             mock.patch.object(R.os, 'mkdir', side_effect=AssertionError('effect')):
            with self.assertRaisesRegex(RuntimeError, 'DISABLED'):
                R.execute()
            with self.assertRaisesRegex(B.Unknown, 'DISABLED'):
                R.controller_candidate('/tmp/not-created', {}, {})

    def test_child_wrong_runtime_refuses_before_read(self):
        with mock.patch.object(C, 'selected', side_effect=AssertionError('read')):
            with self.assertRaisesRegex(RuntimeError, 'CHILD_RUNTIME'):
                C.main({})

    def test_child_digest_read_snapshot(self):
        with tempfile.TemporaryDirectory(prefix='ctx-child-read-') as t:
            p = Path(t) / 'x'
            p.write_bytes(b'public')
            self.assertEqual(C.selected(p, B.sha(b'public')), b'public')
            with self.assertRaisesRegex(RuntimeError, 'DRIFT'):
                C.selected(p, 'a' * 64)
            alias = Path(t) / 'alias'
            alias.symlink_to(p)
            with self.assertRaises(OSError):
                C.selected(alias, B.sha(b'public'))

    def test_capture_real_public_child(self):
        p = IO.subprocess.Popen(['/usr/bin/python3.14', '-I', '-B', '-S', '-c',
                                 "import sys;print('PROVISIONAL');sys.stderr.write('bounded')"],
                                stdout=IO.subprocess.PIPE, stderr=IO.subprocess.PIPE,
                                start_new_session=True)
        try:
            result = IO.capture(p, time.monotonic() + 2, 128)
            self.assertEqual(result, {'stdout': b'PROVISIONAL\n', 'stderr': b'bounded'})
            self.assertEqual(p.returncode, 0)
        finally:
            IO.end_group(p)
            p.stdout.close()
            p.stderr.close()

    def test_capture_overflow_is_unknown(self):
        p = IO.subprocess.Popen(['/usr/bin/python3.14', '-I', '-B', '-S', '-c',
                                 "print('x'*1000)"],
                                stdout=IO.subprocess.PIPE, stderr=IO.subprocess.PIPE,
                                start_new_session=True)
        try:
            with self.assertRaises(IO.CaptureUnknown) as caught:
                IO.capture(p, time.monotonic() + 2, 64)
            self.assertLessEqual(sum(map(len, caught.exception.outputs.values())), 64)
        finally:
            IO.end_group(p)
            p.stdout.close()
            p.stderr.close()

    def test_plan_has_external_receipt_gap(self):
        plan = R.launch_plan(self.topology(), 'a' * 64, {'fixture_only': True})
        self.assertFalse(plan['effect_enabled'])
        self.assertIn('external OS observer', plan['open_integration'])

    def controller_fixture(self, fault=None):
        """Mock Docker boundary; real held writer, socket and full controller."""
        temp = tempfile.TemporaryDirectory(prefix='ctx-docker-controller-fixture-')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / 'attempt'
        value = {**{k: str(root / v) for k, v in
                    [('public', 'public'), ('control', 'control'), ('private', 'private-unmounted')]},
                 'code': str(HERE), 'cache_guard': str(Path(temp.name) / 'guard'),
                 'native': str(Path(temp.name) / 'native'), 'uid': os.getuid(), 'gid': os.getgid()}
        bindings = {n: B.sha((HERE / n).read_bytes()) for n in (
            'child.py', 'wire_bridge.py', 'hooks.py', 'projected-build-inert.py', 'encoder-source.py')}
        state = {}
        cid = 'c' * 64

        def docker(args, records):
            if args[0] == 'create':
                state['config'] = json.loads(args[-1])
                response = (0, cid.encode() + b'\n', b'')
            elif args[0] == 'inspect' and state.get('removed'):
                response = (1, b'[]\n', f'Error response from daemon: No such container: {cid}\n'.encode())
            elif args[0] == 'inspect':
                response = (0, json.dumps([{'Id': cid, 'State': {'Pid': os.getpid()}}]).encode(), b'')
            elif args[0] == 'rm':
                state['removed'] = True
                response = (0, cid.encode() + b'\n', b'')
            elif args[0] == 'ps':
                response = (0, b'remaining\n' if fault == 'remaining' and state.get('removed') else b'', b'')
            else:
                raise AssertionError('unexpected Docker verb')
            records.append({'argv': args, 'exit': response[0],
                            'stdout': response[1].decode(), 'stderr': response[2].decode()})
            return response[0], {'stdout': response[1], 'stderr': response[2]}

        class Pipe:
            def close(self):
                if fault == 'pipe_close':
                    raise OSError('fixture-close')

        proc = types.SimpleNamespace(returncode=None, stdout=Pipe(), stderr=Pipe(),
                                     poll=lambda: None, pid=123456789)

        def child():
            config = state['config']
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
            sock.connect(str(root / 'control/ipc'))
            B.configure(sock)
            source = {'path': str(R.CHILD_HERE / 'source-manifest.json'),
                      'sha256': B.sha(b'{"synthetic_public_only":true}\n')}
            client = B.Client(sock, B.credentials(), config['token'],
                              R.CHILD_HERE / 'packages/0001', source, config['deadline'])
            try:
                ready(sock, config['token'], config['deadline'])
                state['stdout'] = send_package(client, root / 'public' / R.ROLE / 'packages/0001')
                proc.returncode = 1 if fault == 'exit' else 0
            except BaseException:
                state['stdout'] = b''
                proc.returncode = 1
            finally:
                client.close_once()

        def popen(*args, **kwargs):
            state['thread'] = threading.Thread(target=child)
            state['thread'].start()
            return proc

        def capture(*args):
            state['thread'].join(5)
            if state['thread'].is_alive():
                raise RuntimeError('FIXTURE_TIMEOUT')
            raw = state.pop('stdout', b'')
            return {'stdout': raw, 'stderr': b''}

        selected = IO.selected
        def selected_fixture(p, digest):
            if Path(p).parent == HERE or Path(p).name == 'observation.json':
                return selected(p, digest)
            return b'fixture selected external bytes; never executed'

        with mock.patch.object(R, 'EFFECT_ENABLED', True), \
             mock.patch.object(IO, 'docker_call', side_effect=docker), \
             mock.patch.object(IO, 'selected', side_effect=selected_fixture), \
             mock.patch.object(R.subprocess, 'Popen', side_effect=popen), \
             mock.patch.object(IO, 'capture', side_effect=capture), \
             mock.patch.object(IO, 'end_group'):
            try:
                result = R.controller_candidate(root, value, bindings)
            finally:
                for directory, _, _ in os.walk(temp.name):
                    os.chmod(directory, 0o700)
        return result, root

    def test_controller_fixed_lifecycle_mock_success(self):
        result, root = self.controller_fixture()
        self.assertEqual(result['result'], 'PASS_SYNTHETIC_ONLY')
        observation = json.loads((root / 'observation.json').read_bytes())
        self.assertEqual(observation['status'], 'PROVISIONAL')
        self.assertTrue(observation['cid_absent'] and observation['name_absent'])
        self.assertEqual(observation['os_exit'], 0)
        self.assertEqual(len(observation['commands']), 6)

    def test_controller_pipe_close_unknown(self):
        with self.assertRaisesRegex(B.Unknown, 'CONTROLLER_UNKNOWN'):
            self.controller_fixture('pipe_close')

    def test_controller_nonzero_exit_unknown(self):
        with self.assertRaisesRegex(B.Unknown, 'CONTROLLER_UNKNOWN'):
            self.controller_fixture('exit')

    def test_controller_remaining_name_unknown(self):
        with self.assertRaisesRegex(B.Unknown, 'CONTROLLER_UNKNOWN'):
            self.controller_fixture('remaining')
