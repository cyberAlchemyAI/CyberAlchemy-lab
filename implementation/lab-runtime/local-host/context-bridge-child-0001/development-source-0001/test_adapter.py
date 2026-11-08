"""Ordinary owned subprocess fixtures only. Docker is never invoked by this suite."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
import unittest
from unittest import mock

import adapter as A


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ctx-child-tests-')
        self.root = Path(self.temp.name) / 'run'
        self.child_sha = hashlib.sha256((A.HERE / 'child.py').read_bytes()).hexdigest()
        self.fds = len(os.listdir('/proc/self/fd'))
        self.threads = threading.active_count()

    def tearDown(self):
        # Exact fixture-owned tree only; no reset/reuse by the adapter.
        for base, dirs, _ in os.walk(self.temp.name):
            os.chmod(base, 0o700)
            for name in dirs:
                os.chmod(Path(base) / name, 0o700)
        self.temp.cleanup()
        self.assertEqual(len(os.listdir('/proc/self/fd')), self.fds)
        self.assertEqual(threading.active_count(), self.threads)

    def run_fixture(self, fault='none', seconds=5):
        result = A.run(self.root, self.child_sha, fault=fault, seconds=seconds)
        evidence = json.loads((self.root / 'observation.json').read_bytes())
        self.assertEqual(hashlib.sha256((self.root / 'observation.json').read_bytes()).hexdigest(),
                         result['observation_sha256'])
        self.assertEqual(evidence['status'], 'PROVISIONAL')
        self.assertFalse(result['effect_enabled'])
        self.assertEqual(result['original_Context'], 'NOT_RUN')
        return result, evidence

    def test_complete_separate_child(self):
        result, e = self.run_fixture()
        self.assertEqual(result['result'], 'PASS_SYNTHETIC_ONLY')
        self.assertNotEqual(e['peer'][0], os.getpid())
        self.assertEqual(e['peer'], [e['child_report']['pid'], os.getuid(), os.getgid()])
        self.assertEqual(e['child_exit'], 0)
        self.assertEqual(len(e['child_report']['read_leaves']), 40)
        self.assertEqual(len(e['mediator_trace']), 42)
        self.assertEqual([row[1:3] for row in e['mediator_trace'][-4:]],
                         [['RELEASE_PRIVATE', 38], ['EMIT', 39], ['EMIT', 40], ['FINISH', 41]])
        self.assertFalse((self.root / 'attempt/private').exists())
        self.assertFalse(result['docker_readonly_proved'])
        self.assertFalse(Path('/proc', str(e['peer'][0])).exists())

    def test_child_crash(self):
        result, e = self.run_fixture('crash', 0.4)
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertEqual(e['child_exit'], 23)
        self.assertEqual(e['mediator_trace'], [])

    def test_timeout_reaped(self):
        began = time.monotonic()
        result, e = self.run_fixture('timeout', 0.4)
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertLess(time.monotonic() - began, 4)
        self.assertEqual(e['child_exit'], -9)

    def test_wrong_token_no_leaf(self):
        result, e = self.run_fixture('wrong_token', 0.8)
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertFalse((self.root / 'attempt/package/request.json').exists())

    def test_exit_after_provisional_summary(self):
        result, e = self.run_fixture('exit_after_summary')
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertEqual(e['child_exit'], 19)
        self.assertIn('"result": "PASS"', e['stdout'])
        self.assertEqual(e['status'], 'PROVISIONAL')

    def test_wrong_summary(self):
        result, _ = self.run_fixture('bad_summary')
        self.assertEqual(result['result'], 'UNKNOWN')

    def test_stdout_ceiling(self):
        result, _ = self.run_fixture('stdout_overflow')
        self.assertEqual(result['result'], 'UNKNOWN')

    def test_real_close_then_raise_never_pass(self):
        original_close, original_durable = os.close, A.durable
        target = []
        calls = []
        def durable(fd, name, raw):
            original_durable(fd, name, raw)
            if name == 'observation.json':
                target.append(fd)
        def close(fd):
            original_close(fd)
            if target and fd == target[0] and not calls:
                calls.append(fd)
                raise OSError('inert close uncertainty')
        with mock.patch.object(A, 'durable', durable), mock.patch.object(A.os, 'close', close):
            result, _ = self.run_fixture()
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertEqual(len(calls), 1)

    def test_postclose_readback_refusal(self):
        original = A.selected
        def selected(path, digest):
            if Path(path).name == 'observation.json':
                raise RuntimeError('FIXTURE_READBACK_FAILURE')
            return original(path, digest)
        with mock.patch.object(A, 'selected', selected):
            result, _ = self.run_fixture()
        self.assertEqual(result['result'], 'UNKNOWN')

    def test_existing_attempt_unchanged(self):
        self.root.mkdir()
        (self.root / 'foreign').write_bytes(b'keep')
        result = A.run(self.root, self.child_sha)
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertEqual(list(self.root.iterdir()), [self.root / 'foreign'])

    def test_source_drift_before_attempt(self):
        with self.assertRaisesRegex(RuntimeError, 'SELECTED_DRIFT'):
            A.run(self.root, '0' * 64)
        self.assertFalse(self.root.exists())

    def test_parent_symlink_refuses(self):
        alias = Path(self.temp.name) / 'alias'
        alias.symlink_to(Path(self.temp.name), target_is_directory=True)
        with self.assertRaises(OSError):
            A.run(alias / 'run', self.child_sha)
        self.assertFalse(self.root.exists())

    def test_summary_hidden_until_aggregate(self):
        with mock.patch('sys.stdout') as stdout:
            result, e = self.run_fixture('parent_close')
            stdout.write.assert_not_called()
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertIn('"result": "PASS"', e['stdout'])

    def test_wrong_docker_name_refuses_before_effect(self):
        with mock.patch.object(A, 'docker_call') as call:
            with self.assertRaises(RuntimeError):
                A.run(self.root, self.child_sha, docker_probe=True, container_name='foreign')
            call.assert_not_called()
        self.assertFalse(self.root.exists())

    def test_actual_context_disabled(self):
        self.assertFalse(A.EFFECT_ENABLED)
        with self.assertRaisesRegex(RuntimeError, 'ACTUAL_CONTEXT_EFFECT_DISABLED'):
            A.launch_context()

    def test_parent_identity_after_receive(self):
        real = A.socket.socket
        # The trusted process launch PID, not a frame assertion, selects peer.
        class WrongPeer:
            def __init__(self, sock):
                self.sock = sock
            def __getattr__(self, name):
                return getattr(self.sock, name)
            def accept(self):
                sock, address = self.sock.accept()
                wrapped = WrongPeer(sock)
                wrapped.getsockopt = lambda *args: __import__('struct').pack('3i', os.getpid(), os.getuid(), os.getgid())
                return wrapped, address
        with mock.patch.object(A.socket, 'socket', lambda *a, **k: WrongPeer(real(*a, **k))):
            result, e = self.run_fixture()
        self.assertEqual(result['result'], 'UNKNOWN')
        self.assertEqual(e['mediator_trace'], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
