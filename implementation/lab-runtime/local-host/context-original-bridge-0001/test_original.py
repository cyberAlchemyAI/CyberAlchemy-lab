"""Actual selected original AST sites with synthetic public bodies, never full build."""
import ast
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

import project as P
import hooks as H
import layout_bridge as B

HERE = Path(__file__).resolve().parent
ENCODER = HERE.parent / 'source-only-docker-0002/generated/product/lab/release-candidates/v1/interface/docker-source-20261020-0001/base.py'
ENCODER_SHA = 'bc5eb6c60db7a911a28bbcac4deca901c213cdce54e203dd2db5749377b42a6f'


class CloseFault:
    def __init__(self, sock):
        self.sock = sock
        self.calls = 0
    def __getattr__(self, name):
        return getattr(self.sock, name)
    def close(self):
        self.calls += 1
        self.sock.close()
        raise OSError('synthetic-close-failure')


class Fixture:
    def __init__(self, client_close=False, parent_close=False):
        self.temp = tempfile.TemporaryDirectory(prefix='ctx-original-bridge-')
        self.root = Path(self.temp.name)
        self.here = self.root / 'family'
        self.here.mkdir(mode=0o700)
        self.private = self.root / 'synthetic-original-private'
        self.private.mkdir(mode=0o700)
        (self.here / 'source-manifest.json').write_bytes(b'{"synthetic":true}')
        self.source = self.binding(self.here / 'source-manifest.json')
        deadline = time.monotonic() + 3.0
        self.cs, self.ps = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        if client_close:
            self.cs = CloseFault(self.cs)
        if parent_close:
            self.ps = CloseFault(self.ps)
        self.hooks = H.Hooks(self.cs, B.credentials(), self.here, self.private,
                             self.source, 'a' * 32, deadline)
        self.parent = H.Parent(self.ps, B.credentials(), self.here, self.source, 'a' * 32, deadline)
        raw, _ = P.project_build(P.ORIGINAL.read_bytes())
        if raw != (HERE / 'projected-build-inert.py').read_bytes():
            raise RuntimeError('SELECTED_BUILD_DRIFT')
        self.tree = ast.parse(raw)
        self.build = P.function(self.tree, 'build')
        encoder = ENCODER.read_bytes()
        if B.sha(encoder) != ENCODER_SHA:
            raise RuntimeError('ENCODER_DRIFT')
        encoder_node = P.function(ast.parse(encoder), 'encoded')
        self.namespace = {'HERE': self.here, 'require': B.need, 'json': json,
                          '_ctx_emit': self.hooks.emit, '_ctx_output_ready': self.hooks.output_ready,
                          '_ctx_release_private': self.hooks.release_private,
                          '_ctx_print': self.hooks.provisional_print,
                          'root': self.private, 'started': 0,
                          'time': types.SimpleNamespace(monotonic=lambda: 1),
                          'source_pin': self.source['sha256'], 'mapped_pin': 'b' * 64,
                          'binding': self.binding}
        nodes = [encoder_node, P.function(self.tree, 'emit')]
        exec(compile(P.span(nodes), 'selected-original-emit-encoder', 'exec'), self.namespace)
        self.printed = []

    def binding(self, path):
        return {'path': str(path), 'sha256': B.sha(path.read_bytes())}

    def begin(self):
        self.parent.start()
        # Original output assignment, original overwrite guard, projected READY.
        exec(compile(P.span(self.build.body[1:4]), 'selected-original-output', 'exec'), self.namespace)

    def prefix(self):
        for index, name in enumerate(B.LEAVES[:38]):
            raw = B.encode({'synthetic_public_body': index})
            self.namespace['emit'](self.namespace['out'] / name, None, raw=raw)
            if (self.namespace['out'] / name).read_bytes() != raw:
                raise RuntimeError('POST_ACK_ORIGINAL_READ')

    def cleanup_original(self):
        self.private.rmdir()  # empty owned fixture; never policy/key cleanup

    def tail(self):
        # Exact original cleanup assertion, projected RELEASE, original full result,
        # result emit, manifest comprehension/read/bind, manifest emit and print call.
        exec(compile(P.span(self.build.body[-7:]), 'selected-original-build-tail', 'exec'),
             self.namespace)

    def complete(self):
        self.begin()
        self.prefix()
        self.cleanup_original()
        self.tail()
        self.parent.join()
        self.printed.append(self.hooks.publish(self.parent))

    def close(self):
        with contextlib.suppress(BaseException):
            self.hooks.client.close_once()
        if self.parent.thread is not None:
            self.parent.thread.join(4)
            if self.parent.thread.is_alive():
                raise RuntimeError('READY_THREAD_REMAINS')
        else:
            with contextlib.suppress(BaseException):
                self.ps.close()
        if self.parent.mediator is not None:
            self.parent.mediator.join(4)
            if self.parent.mediator._thread.is_alive():
                raise RuntimeError('MEDIATOR_REMAINS')
        if self.parent.writer is not None:
            self.parent.writer.abort()
        for base, dirs, _ in os.walk(self.root):
            os.chmod(base, 0o700)
            for name in dirs:
                if not (Path(base) / name).is_symlink():
                    os.chmod(Path(base) / name, 0o700)
        self.temp.cleanup()


class Tests(unittest.TestCase):
    def setUp(self):
        fds = len(os.listdir('/proc/self/fd'))
        threads = {t.ident for t in threading.enumerate()}
        def restored():
            self.assertEqual(len(os.listdir('/proc/self/fd')), fds)
            self.assertEqual({t.ident for t in threading.enumerate()}, threads)
        self.addCleanup(restored)

    def fixture(self, **kwargs):
        f = Fixture(**kwargs)
        self.addCleanup(f.close)
        return f

    def test_full_inverse_and_exact_seven_writer_sites(self):
        build, bp = P.project_build(P.ORIGINAL.read_bytes())
        writer, wp = P.project_writer(P.BRIDGE.read_bytes())
        self.assertEqual(build, (HERE / 'projected-build-inert.py').read_bytes())
        self.assertEqual(writer, (HERE / 'layout_bridge.py').read_bytes())
        self.assertTrue(bp['full_AST_inverse_equal'])
        self.assertTrue(wp['full_AST_inverse_equal'])
        self.assertEqual(sum(wp['seven_constant_sites'].values()), 7)
        self.assertEqual(bp['remaining_refusals'], 3)

    def test_preimage_drift_refuses_before_projection(self):
        for fn, path in ((P.project_build, P.ORIGINAL), (P.project_writer, P.BRIDGE)):
            with self.assertRaisesRegex(RuntimeError, 'PREIMAGE'):
                fn(path.read_bytes() + b'\n')

    def test_original_tail_exact_path_manifest_protocol(self):
        f = self.fixture()
        self.assertFalse((f.here / 'packages').exists())
        f.complete()
        out = f.here / 'packages/0001'
        self.assertEqual(f.namespace['out'], out)
        self.assertEqual(f.parent.writer.out, out)
        self.assertFalse(out.is_symlink())
        manifest = json.loads((out / 'manifest.json').read_bytes())
        self.assertEqual(len(manifest), 8)
        self.assertEqual(len(manifest['files']), 39)
        for row in manifest['files']:
            self.assertTrue(Path(row['path']).is_relative_to(out))
            self.assertEqual(row, f.binding(Path(row['path'])))
        self.assertEqual(manifest['source_manifest_binding'], f.source)
        self.assertEqual(manifest['delivery_binding'], f.binding(out / 'delivery.json'))
        self.assertEqual(manifest['provenance_binding'], f.binding(out / 'delivery-provenance.json'))
        self.assertTrue((out / 'manifest.json').read_bytes().endswith(b'\n'))
        self.assertIn(b'\n  ', (out / 'manifest.json').read_bytes())
        self.assertEqual(f.hooks.client.seq, 42)
        self.assertEqual([r[1:3] for r in f.parent.mediator.trace[-4:]],
                         [('RELEASE_PRIVATE', 38), ('EMIT', 39), ('EMIT', 40), ('FINISH', 41)])
        self.assertEqual(f.parent.writer.trace[-2][0], 'WRITER_CLOSED')
        self.assertEqual(f.parent.writer.trace[-1], ('POSTCLOSE_READBACK', 40))
        self.assertEqual(len(f.printed), 1)
        self.assertEqual(json.loads(f.printed[0])['package_binding'], f.binding(out / 'manifest.json'))
        self.assertFalse(f.private.exists())
        self.assertFalse(f.parent.writer.private.exists())

    def test_existing_original_output_refuses_before_ready(self):
        f = self.fixture()
        (f.here / 'packages/0001').mkdir(parents=True)
        with self.assertRaisesRegex(RuntimeError, 'refuse delivery package overwrite'):
            exec(compile(P.span(f.build.body[1:4]), 'selected-original-output', 'exec'), f.namespace)
        self.assertEqual(f.hooks.state, 'NEW')
        self.assertIsNone(f.parent.writer)
        self.assertEqual(f.hooks.client.seq, 0)

    def test_wrong_ready_path_no_write(self):
        f = self.fixture()
        with self.assertRaisesRegex(RuntimeError, 'READY_SCOPE'):
            f.hooks.output_ready(f.here / 'packages/package')
        self.assertFalse((f.here / 'packages').exists())

    def test_original_private_assertion_precedes_release(self):
        f = self.fixture()
        f.begin()
        f.prefix()
        with self.assertRaisesRegex(RuntimeError, 'private host permission root remains'):
            f.tail()
        self.assertEqual(f.hooks.client.seq, 38)
        self.assertFalse(f.parent.writer.released)
        self.assertFalse((f.namespace['out'] / 'build-result.json').exists())

    def test_wrong_absent_private_scope_refuses(self):
        f = self.fixture()
        f.begin()
        f.prefix()
        f.namespace['root'] = f.root / 'foreign-absent'
        with self.assertRaisesRegex(RuntimeError, 'ORIGINAL_PRIVATE_NOT_RELEASED'):
            f.tail()
        self.assertEqual(f.hooks.client.seq, 38)
        self.assertEqual(f.printed, [])

    def test_raw_and_encoded_original_emit(self):
        f = self.fixture()
        f.begin()
        f.namespace['emit'](f.namespace['out'] / B.LEAVES[0], {'fixture': 1})
        first = (f.namespace['out'] / B.LEAVES[0]).read_bytes()
        self.assertEqual(first, f.namespace['encoded']({'fixture': 1}))
        f.namespace['emit'](f.namespace['out'] / B.LEAVES[1], None, raw=b'raw selected fixture')
        self.assertEqual((f.namespace['out'] / B.LEAVES[1]).read_bytes(), b'raw selected fixture')

    def test_original_boundary_and_protocol_slot_both_narrow(self):
        f = self.fixture()
        f.begin()
        with self.assertRaisesRegex(RuntimeError, 'delivery output boundary escaped'):
            f.namespace['emit'](f.root / 'foreign', {})
        with self.assertRaisesRegex(RuntimeError, 'CLIENT_ORDER'):
            f.namespace['emit'](f.here / 'receipts/foreign.json', {})
        self.assertEqual(f.printed, [])

    def ack_fault(self, op, ordinal):
        f = self.fixture()
        f.begin()
        f.prefix()
        f.cleanup_original()
        real = B.send
        def send(sock, raw, deadline):
            value = B.parse(raw)
            if value.get('v') == 'context-fixture-ack/v1' and value['op'] == op and value['ordinal'] == ordinal:
                raise OSError('synthetic lost ACK')
            return real(sock, raw, deadline)
        with mock.patch.object(B, 'send', send):
            with self.assertRaises(Exception):
                f.tail()
        with self.assertRaises(Exception):
            f.hooks.publish(f.parent)
        self.assertEqual(f.printed, [])
        self.assertEqual(f.hooks.state, 'UNKNOWN')

    def test_manifest_ack_loss(self):
        self.ack_fault('EMIT', 40)

    def test_finish_ack_loss(self):
        self.ack_fault('FINISH', 41)

    def test_release_ack_loss(self):
        self.ack_fault('RELEASE_PRIVATE', 38)

    def test_client_close_fault_blocks_original_print(self):
        f = self.fixture(client_close=True)
        f.begin()
        f.prefix()
        f.cleanup_original()
        with self.assertRaises(OSError):
            f.tail()
        self.assertEqual(f.hooks.output.state, 'EMPTY')
        self.assertEqual(f.cs.calls, 1)
        self.assertEqual(f.printed, [])

    def test_parent_close_fault_keeps_original_print_provisional(self):
        f = self.fixture(parent_close=True)
        f.begin()
        f.prefix()
        f.cleanup_original()
        f.tail()
        f.parent.join()
        self.assertEqual(f.hooks.output.state, 'BUFFERED')
        with self.assertRaisesRegex(RuntimeError, 'FINAL_UNKNOWN'):
            f.hooks.publish(f.parent)
        self.assertEqual(f.ps.calls, 1)
        self.assertEqual(f.printed, [])

    def test_writer_real_final_close_fault_blocks_finish_ack(self):
        f = self.fixture()
        f.begin()
        f.prefix()
        f.cleanup_original()
        target = tuple(fd for fd in f.parent.writer.fds if fd != f.parent.writer.private_fd)
        real = B.close_all
        hits = []
        def close_all(fds):
            selected = tuple(fds) == target
            real(fds)
            if selected:
                hits.append(1)
                raise OSError('synthetic writer final close uncertainty')
        with mock.patch.object(B, 'close_all', close_all):
            with self.assertRaises(Exception):
                f.tail()
        self.assertEqual(hits, [1])
        self.assertEqual(f.parent.writer.state, 'UNKNOWN')
        self.assertNotIn(('ACK_PREPARED', 'FINISH', 41),
                         [r[:3] for r in f.parent.mediator.trace])
        self.assertEqual(f.hooks.output.state, 'EMPTY')
        self.assertTrue((f.namespace['out'] / 'manifest.json').exists())

    def test_unjoined_parent_cannot_publish(self):
        f = self.fixture()
        f.begin()
        f.prefix()
        f.cleanup_original()
        f.tail()
        self.assertEqual(f.hooks.output.state, 'BUFFERED')
        with self.assertRaisesRegex(RuntimeError, 'AGGREGATE_STATE'):
            f.hooks.publish(f.parent)
        self.assertEqual(f.printed, [])

    def test_wrong_manifest_binding_no_manifest_write(self):
        f = self.fixture()
        f.begin()
        f.prefix()
        f.cleanup_original()
        original = f.binding
        f.namespace['binding'] = lambda p: ({'path': str(p), 'sha256': '0' * 64}
                                            if p.name == 'source-manifest.json' else original(p))
        with self.assertRaises(Exception):
            f.tail()
        self.assertFalse((f.namespace['out'] / 'manifest.json').exists())
        self.assertEqual(f.printed, [])

    def test_second_summary_or_publish_refuses(self):
        f = self.fixture()
        f.complete()
        with self.assertRaisesRegex(RuntimeError, 'AGGREGATE_STATE'):
            f.hooks.publish(f.parent)
        self.assertEqual(len(f.printed), 1)

    def test_actual_context_permanently_disabled(self):
        self.assertFalse(H.EFFECT_ENABLED)
        with self.assertRaisesRegex(RuntimeError, 'ACTUAL_CONTEXT_EFFECT_DISABLED'):
            H.launch_context()

    def test_namespace_parent_zero_refuses_without_selected_profile(self):
        a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        try:
            for mode in (False, True):
                with self.assertRaises(RuntimeError):
                    H.client_endpoint(a, (0, os.getuid(), os.getgid()), 'a' * 32,
                                      Path('/synthetic/packages/0001'), {},
                                      time.monotonic() + 2.0, mode)
        finally:
            a.close()
            b.close()

    def test_namespace_parent_coordinate_only_under_simulated_pid_one(self):
        a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        try:
            with mock.patch.object(H.os, 'getpid', return_value=1):
                client = H.client_endpoint(a, (0, os.getuid(), os.getgid()), 'a' * 32,
                                          Path('/synthetic/packages/0001'), {},
                                          time.monotonic() + 2.0, True)
                self.assertEqual(client.peer, (0, os.getuid(), os.getgid()))
                self.assertEqual(client.state, 'OPEN')
                self.assertEqual(client.seq, 0)
                with self.assertRaises(RuntimeError):
                    H.client_endpoint(b, (1, os.getuid(), os.getgid()), 'a' * 32,
                                      Path('/synthetic/packages/0001'), {},
                                      time.monotonic() + 2.0, True)
        finally:
            a.close()
            b.close()
