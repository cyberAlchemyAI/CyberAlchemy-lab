"""Owned synthetic IPC only; never imports or executes an original Context module."""
import ast
import array
import contextlib
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import tempfile
import threading
import time
import types
import unittest
from unittest import mock

import bridge as B

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
ORIGINAL = REPO / 'implementation/lab-runtime/local-host/context-integration-0002/adapted-build-inert.py'
ORIGINAL_SHA = 'ae925dfd721372fe0744ae1b2ef0c00810c57bb1459ceccc63736aa5f572ee6a'
ENCODER = REPO / 'implementation/lab-runtime/local-host/source-only-docker-0002/generated/product/lab/release-candidates/v1/interface/docker-source-20261020-0001/base.py'
ENCODER_SHA = 'bc5eb6c60db7a911a28bbcac4deca901c213cdce54e203dd2db5749377b42a6f'
TOKEN = 'a' * 32


def selected_ast():
    raw = ORIGINAL.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise RuntimeError('PREIMAGE_DRIFT')
    return ast.parse(raw)


class Fixture:
    def __init__(self, seconds=5):
        self.temp = tempfile.TemporaryDirectory(prefix='context-bridge-0002-')
        self.here = Path(self.temp.name)
        (self.here / 'source-manifest.json').write_bytes(b'{"synthetic":true}')
        self.source = self.binding(self.here / 'source-manifest.json')
        self.deadline = time.monotonic() + seconds
        self.writer = B.Writer(self.here / 'packages', self.source, self.deadline)
        self.client_sock, self.server_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.client = B.Client(self.client_sock, B.credentials(), TOKEN, self.writer.out,
                               self.source, self.deadline)
        self.server = B.Mediator(self.server_sock, B.credentials(), TOKEN, self.writer)
        self.thread = None
        self.printed = []
        self.output = B.ProvisionalOutput()
        tree = selected_ast()
        emit = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'emit')
        self.build = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'build')
        encoder_raw = ENCODER.read_bytes()
        if B.sha(encoder_raw) != ENCODER_SHA:
            raise RuntimeError('ENCODER_PREIMAGE_DRIFT')
        encoder = next(n for n in ast.parse(encoder_raw).body
                       if isinstance(n, ast.FunctionDef) and n.name == 'encoded')
        enc_namespace = {'json': json}
        exec(compile(ast.Module(body=[encoder], type_ignores=[]), str(ENCODER), 'exec'), enc_namespace)
        namespace = {'HERE': self.here, 'require': B.need, 'encoded': enc_namespace['encoded'],
                     '_ctx_emit': self.client.emit}
        exec(compile(ast.Module(body=[emit], type_ignores=[]), str(ORIGINAL), 'exec'), namespace)
        self.emit = namespace['emit']
        self.namespace = {'HERE': self.here, 'out': self.writer.out,
                          'root': self.writer.private, 'started': 0,
                          'time': types.SimpleNamespace(monotonic=lambda: 1),
                          'source_pin': self.source['sha256'], 'mapped_pin': 'b' * 64,
                          'emit': self.emit, 'binding': self.binding, 'json': json,
                          'print': self.output.capture}

    def binding(self, path):
        raw = path.read_bytes()
        return {'path': str(path), 'sha256': B.sha(raw)}

    def start(self):
        self.thread = self.server.start()

    def prefix(self, count=38):
        for i, name in enumerate(B.LEAVES[:count]):
            raw = B.encode({'synthetic': i})
            self.emit(self.writer.out / name, None, raw=raw)
            # Actual bytes are visible after ACK; no emulated read or binding map.
            if (self.writer.out / name).read_bytes() != raw:
                raise RuntimeError('POST_ACK_VISIBILITY')
            if stat.S_IMODE((self.writer.out / name).stat().st_mode) != 0o444:
                raise RuntimeError('READ_ONLY_MODE')

    def tail(self):
        # Selected original result assignment, result emit, manifest assignment,
        # manifest emit and print. No full build, imports, source read, key or native.
        exec(compile(ast.Module(body=self.build.body[-5:], type_ignores=[]),
                     str(ORIGINAL), 'exec'), self.namespace)

    def complete(self):
        self.prefix()
        self.client.release_private()
        self.tail()
        if not self.server.join(2):
            raise RuntimeError('THREAD_NOT_FINISHED')
        status = B.final_verdict(self.client, self.server)
        self.printed.append(self.output.release(self.client, self.server))
        return status

    def close(self):
        with contextlib.suppress(BaseException):
            self.client.close_once()
        if self.thread:
            self.thread.join(6)
            if self.thread.is_alive():
                raise RuntimeError('REVIEW_FIXTURE_THREAD_REMAINS')
        else:
            self.server_sock.close()
        self.writer.abort()
        # Fixture-only exact tree; retained originals remain until assertions end.
        if self.writer.out.exists():
            self.writer.out.chmod(0o700)
            (self.writer.out / 'artifacts').chmod(0o700)
        self.temp.cleanup()


class Tests(unittest.TestCase):
    def setUp(self):
        baseline = len(os.listdir('/proc/self/fd'))
        thread_ids = {t.ident for t in threading.enumerate()}
        def all_owned_fixtures_released():
            self.assertEqual(len(os.listdir('/proc/self/fd')), baseline)
            self.assertEqual({t.ident for t in threading.enumerate()}, thread_ids)
        self.addCleanup(all_owned_fixtures_released)

    def fixture(self, **kwargs):
        f = Fixture(**kwargs)
        self.addCleanup(f.close)
        return f

    def test_original_tail_real_ipc_complete(self):
        f = self.fixture()
        f.start()
        self.assertEqual(f.complete(), 'PASS_SYNTHETIC_ONLY')
        self.assertEqual(len(f.printed), 1)
        self.assertEqual(len(f.writer.rows), 40)
        self.assertEqual(f.client.seq, 42)  # 40 EMIT + RELEASE_PRIVATE + FINISH
        self.assertEqual([e[2] for e in f.client.trace if e[:2] == ('SENT', 'FINISH')], [41])
        self.assertEqual(f.client.trace[-1], ('CLIENT_CLOSED', 1))
        self.assertEqual(f.writer.trace[-2][0], 'WRITER_CLOSED')
        self.assertEqual(f.writer.trace[-1], ('POSTCLOSE_READBACK', 40))
        self.assertFalse(f.writer.private.exists())
        manifest = json.loads((f.writer.out / 'manifest.json').read_bytes())
        manifest_raw = (f.writer.out / 'manifest.json').read_bytes()
        self.assertTrue(manifest_raw.endswith(b'\n'))
        self.assertIn(b'\n  ', manifest_raw)
        self.assertNotEqual(manifest_raw, B.encode(manifest))
        self.assertEqual(len(manifest), 8)
        self.assertEqual(len(manifest['files']), 39)
        self.assertEqual(manifest['schema_version'], 'lab-actual-context-delivery-package/v1-candidate')
        for name in B.LEAVES:
            trace = f.writer.trace
            self.assertLess(trace.index(('FILE_FSYNC', name)), trace.index(('NAME_FSYNC_READBACK', name)))
        print(json.dumps({'case': 'original_tail_real_ipc_complete', 'effect': 'synthetic_only',
                          'preimage_sha256': ORIGINAL_SHA, 'leaves': 40, 'manifest_rows': 39,
                          'wire_requests': 42, 'client_trace': f.client.trace,
                          'writer_trace': f.writer.trace, 'server_state': f.server.state,
                          'printed_summary_count': len(f.printed)}, sort_keys=True))

    def test_guard_keeps_real_context_disabled(self):
        self.assertFalse(B.EFFECT_ENABLED)
        with self.assertRaisesRegex(B.Unknown, 'ACTUAL_CONTEXT_EFFECT_DISABLED'):
            B.launch_context()

    def test_drift_before_AST_compile(self):
        with mock.patch.object(Path, 'read_bytes', return_value=b'print("unselected")'):
            with self.assertRaisesRegex(RuntimeError, 'PREIMAGE_DRIFT'):
                selected_ast()

    def test_private_release_exact_order_and_single_use(self):
        for count in (0, 37):
            with self.subTest(count=count):
                f = self.fixture()
                f.start()
                f.prefix(count)
                with self.assertRaises(B.Unknown):
                    f.client.release_private()
                self.assertEqual(f.client.state, 'UNKNOWN')
                self.assertFalse(f.printed)
        f = self.fixture()
        f.start()
        f.prefix()
        f.client.release_private()
        with self.assertRaises(B.Unknown):
            f.client.release_private()

    def test_result_requires_release(self):
        f = self.fixture()
        f.start()
        f.prefix()
        with self.assertRaisesRegex(B.Unknown, 'CLIENT_PRIVATE'):
            f.tail()
        self.assertFalse((f.writer.out / 'build-result.json').exists())
        self.assertFalse(f.printed)

    def test_changed_duplicate_and_extra_leaf_refuse(self):
        f = self.fixture()
        f.start()
        f.prefix(1)
        before = (f.writer.out / B.LEAVES[0]).read_bytes()
        with self.assertRaises(B.Unknown):
            f.client.emit(f.writer.out / B.LEAVES[0], b'changed')
        self.assertEqual((f.writer.out / B.LEAVES[0]).read_bytes(), before)
        with self.assertRaises(B.Unknown):
            f.client.emit(f.writer.out / 'extra.json', b'extra')
        self.assertFalse((f.writer.out / 'extra.json').exists())

    def test_manifest_exact_profile_bindings_and_rows(self):
        for mutation in ('extra', 'source', 'rows', 'profile', 'delivery'):
            with self.subTest(mutation=mutation):
                f = self.fixture()
                f.start()
                f.prefix()
                f.client.release_private()
                exec(compile(ast.Module(body=f.build.body[-5:-2], type_ignores=[]),
                             str(ORIGINAL), 'exec'), f.namespace)
                m = f.namespace['manifest']
                if mutation == 'extra':
                    m['extra'] = True
                elif mutation == 'source':
                    m['source_manifest_binding']['sha256'] = 'c' * 64
                elif mutation == 'rows':
                    m['files'] = m['files'][::-1]
                elif mutation == 'profile':
                    m['schema_version'] = 'lab-context-scratch-package/v1-inert'
                else:
                    m['delivery_binding'] = m['provenance_binding']
                with self.assertRaises(Exception):
                    f.emit(f.writer.out / 'manifest.json', m)
                self.assertFalse(f.printed)
                self.assertFalse((f.writer.out / 'manifest.json').exists())

    def test_lost_or_changed_ack_suppresses_summary(self):
        for op, ordinal, mode in (('EMIT', 40, 'lost'), ('FINISH', 41, 'lost'),
                                  ('EMIT', 1, 'hash'), ('FINISH', 41, 'ordinal')):
            with self.subTest(op=op, mode=mode):
                f = self.fixture()
                real = B.send
                def faulty(sock, raw, deadline):
                    value = json.loads(raw)
                    if sock is f.server_sock and value['op'] == op and value['ordinal'] == ordinal:
                        if mode == 'lost':
                            raise OSError('synthetic send fault')
                        value['request_sha256' if mode == 'hash' else 'ordinal'] = '0' * 64
                        raw = B.encode(value)
                    return real(sock, raw, deadline)
                with mock.patch.object(B, 'send', side_effect=faulty):
                    f.start()
                    with self.assertRaises(Exception):
                        f.complete()
                    f.thread.join(2)
                self.assertFalse(f.printed)
                self.assertEqual(f.client.state, 'UNKNOWN')
                # A server can see clean EOF after the client rejected its
                # corrupted last ACK. EOF cannot authenticate client success.
                self.assertIn(f.server.state, ('UNKNOWN', 'PEER_EOF'))
                with self.assertRaises(B.Unknown):
                    B.final_verdict(f.client, f.server)
                with self.assertRaises(B.Unknown):
                    f.client.emit(f.writer.out / B.LEAVES[0], b'retry')

    def test_writer_close_fault_no_finish_ack(self):
        f = self.fixture()
        original = B.close_all
        hit = []
        def fail(fds):
            is_finish = f.writer.package_fd in fds and len(f.writer.rows) == 40
            original(fds)
            if is_finish and not hit:
                hit.append(True)
                raise B.Unknown('CLOSE_UNCERTAIN')
        with mock.patch.object(B, 'close_all', side_effect=fail):
            f.start()
            with self.assertRaises(Exception):
                f.complete()
            f.thread.join(2)
        self.assertTrue(hit)
        self.assertFalse(any(e[:2] == ('ACK_PREPARED', 'FINISH') for e in f.server.trace))
        self.assertFalse(f.printed)
        self.assertEqual(f.writer.fds, [])

    def test_client_close_interrupt_no_summary(self):
        f = self.fixture()
        real = f.client.close_once
        def fail():
            real()
            raise KeyboardInterrupt()
        with mock.patch.object(f.client, 'close_once', side_effect=fail):
            f.start()
            with self.assertRaises(KeyboardInterrupt):
                f.complete()
            f.thread.join(2)
        self.assertFalse(f.printed)
        self.assertEqual(f.client.state, 'UNKNOWN')
        with self.assertRaises(B.Unknown):
            B.final_verdict(f.client, f.server)

    def test_parent_close_failure_keeps_provisional_summary_private(self):
        f = self.fixture()
        class CloseFault:
            def __getattr__(self, name):
                return getattr(f.server_sock, name)
            def close(self):
                f.server_sock.close()
                raise OSError('synthetic close uncertainty')
        f.server.sock = CloseFault()
        f.start()
        with self.assertRaisesRegex(B.Unknown, 'FINAL_UNKNOWN'):
            f.complete()
        self.assertEqual(len(f.printed), 0)
        self.assertEqual(f.output.state, 'BUFFERED')
        self.assertEqual(f.server.state, 'UNKNOWN')
        self.assertFalse(f.server.socket_closed)
        with self.assertRaisesRegex(B.Unknown, 'FINAL_UNKNOWN'):
            f.output.release(f.client, f.server)
        self.assertEqual(f.output.state, 'UNKNOWN')

    def test_detach_while_receive_blocks_prevents_write(self):
        f = self.fixture()
        f.start()
        moved = f.writer.path.with_name('moved')
        f.writer.path.rename(moved)
        f.writer.path.mkdir()
        try:
            with self.assertRaises(Exception):
                f.prefix(1)
            f.thread.join(2)
            self.assertFalse((moved / 'package/request.json').exists())
        finally:
            f.writer.path.rmdir()
            moved.rename(f.writer.path)

    def test_postclose_detach_prevents_finish_ack(self):
        f = self.fixture()
        real = f.writer.postclose
        def detach():
            moved = f.writer.path.with_name('moved')
            f.writer.path.rename(moved)
            f.writer.path.mkdir()
            try:
                real()
            finally:
                f.writer.path.rmdir()
                moved.rename(f.writer.path)
        with mock.patch.object(f.writer, 'postclose', side_effect=detach):
            f.start()
            with self.assertRaises(Exception):
                f.complete()
            f.thread.join(2)
        self.assertFalse(f.printed)
        self.assertFalse(any(e[:2] == ('ACK_PREPARED', 'FINISH') for e in f.server.trace))

    def test_fsync_failure_never_ack_or_retry(self):
        f = self.fixture()
        real = B.os.fsync
        hit = []
        def fail(fd):
            if stat.S_ISREG(os.fstat(fd).st_mode):
                hit.append(True)
                raise OSError('synthetic fsync')
            return real(fd)
        with mock.patch.object(B.os, 'fsync', side_effect=fail):
            f.start()
            with self.assertRaises(Exception):
                f.prefix(1)
            f.thread.join(2)
        self.assertTrue(hit)
        self.assertFalse(f.server.trace)
        self.assertEqual(f.writer.state, 'UNKNOWN')
        with self.assertRaises(FileExistsError):
            B.Writer(f.writer.path, f.source, time.monotonic() + 3)

    def test_oversize_bool_ordinal_wrong_peer_and_duplicate_fields(self):
        for fault in ('oversize', 'bool', 'peer', 'duplicate'):
            with self.subTest(fault=fault):
                f = self.fixture()
                if fault == 'peer':
                    f.server.peer = (os.getpid() + 100000, os.getuid(), os.getgid())
                f.start()
                raw = B.encode({'v': 'context-fixture-ipc/v1', 'attempt': TOKEN, 'seq': 1,
                                'op': 'EMIT', 'ordinal': True if fault == 'bool' else 1,
                                'leaf': B.LEAVES[0], 'sha256': B.sha(b'x'),
                                'payload': 'eA=='})
                if fault == 'oversize':
                    raw = b'x' * (B.MAX_PACKET + 1)
                elif fault == 'duplicate':
                    raw = raw[:-1] + b',"seq":1}'
                f.client_sock.send(raw)
                f.thread.join(2)
                self.assertEqual(f.server.state, 'UNKNOWN')
                self.assertFalse((f.writer.out / B.LEAVES[0]).exists())

    def test_deadline_before_request_is_unknown(self):
        f = self.fixture(seconds=0.1)
        f.start()
        time.sleep(0.15)
        with self.assertRaises(Exception):
            f.prefix(1)
        f.thread.join(2)
        self.assertEqual(f.server.state, 'UNKNOWN')
        self.assertFalse((f.writer.out / B.LEAVES[0]).exists())

    def test_symlink_fifo_and_extra_inventory_refuse(self):
        for fault in ('symlink', 'fifo', 'extra'):
            with self.subTest(fault=fault):
                f = self.fixture()
                f.start()
                f.prefix()
                f.client.release_private()
                if fault == 'extra':
                    (f.writer.out / 'extra.json').write_bytes(b'owned extra')
                else:
                    leaf = f.writer.out / B.LEAVES[0]
                    leaf.unlink()
                    if fault == 'fifo':
                        os.mkfifo(leaf)
                    else:
                        leaf.symlink_to(f.here / 'source-manifest.json')
                with self.assertRaises(Exception):
                    f.tail()
                f.thread.join(2)
                self.assertFalse(f.printed)

    def test_close_all_attempts_every_fd_once(self):
        read1, write1 = os.pipe()
        read2, write2 = os.pipe()
        owned = [read1, write1, read2, write2]
        real = os.close
        calls = []
        def fail(fd):
            calls.append(fd)
            real(fd)
            if len(calls) == 1:
                raise OSError('after release')
        with mock.patch.object(B.os, 'close', side_effect=fail):
            with self.assertRaisesRegex(B.Unknown, 'CLOSE_UNCERTAIN'):
                B.close_all(owned)
        self.assertEqual(calls, owned[::-1])
        for fd in owned:
            with self.assertRaises(OSError):
                os.fstat(fd)

    def test_directory_fsync_failure_no_ack(self):
        f = self.fixture()
        real = B.os.fsync
        def fail(fd):
            if fd == f.writer.package_fd:
                raise OSError('synthetic directory fsync')
            return real(fd)
        with mock.patch.object(B.os, 'fsync', side_effect=fail):
            f.start()
            with self.assertRaises(Exception):
                f.prefix(1)
            f.thread.join(2)
        self.assertFalse(f.server.trace)
        self.assertEqual(f.writer.state, 'UNKNOWN')

    def test_unexplained_private_file_is_retained(self):
        f = self.fixture()
        f.start()
        f.prefix()
        extra = f.writer.private / 'not-owned-by-cleanup'
        extra.write_bytes(b'synthetic')
        with self.assertRaises(Exception):
            f.client.release_private()
        f.thread.join(2)
        self.assertEqual(extra.read_bytes(), b'synthetic')
        self.assertTrue(f.writer.private.exists())
        self.assertFalse(f.printed)

    def test_extra_frame_after_finish_blocks_final(self):
        f = self.fixture()
        f.start()
        f.prefix()
        f.client.release_private()
        # Execute result and manifest assignment; emit manifest manually, then
        # send a second FINISH instead of the fixed Client close.
        exec(compile(ast.Module(body=f.build.body[-5:-2], type_ignores=[]),
                     str(ORIGINAL), 'exec'), f.namespace)
        f.client.rows = f.client.exchange('EMIT', 40, 'manifest.json', B.encode(f.namespace['manifest']))
        f.client.exchange('FINISH', 41)
        with self.assertRaises(Exception):
            f.client.exchange('FINISH', 41)
        f.thread.join(2)
        self.assertEqual(f.server.state, 'UNKNOWN')
        self.assertFalse(f.printed)

    def test_lost_finish_send_blocks_summary(self):
        f = self.fixture()
        real = B.send
        def fail(sock, raw, deadline):
            if sock is f.client_sock and json.loads(raw)['op'] == 'FINISH':
                raise OSError('send lost')
            return real(sock, raw, deadline)
        with mock.patch.object(B, 'send', side_effect=fail):
            f.start()
            with self.assertRaises(Exception):
                f.complete()
            f.thread.join(2)
        self.assertFalse(f.printed)
        self.assertFalse(any(e[:2] == ('ACK_PREPARED', 'FINISH') for e in f.server.trace))

    def test_rights_are_closed_and_refused(self):
        left, right = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.addCleanup(left.close)
        self.addCleanup(right.close)
        B.configure(right)
        read_fd, write_fd = os.pipe()
        self.addCleanup(os.close, read_fd)
        self.addCleanup(os.close, write_fd)
        left.sendmsg([b'{}'], [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                               array.array('i', [read_fd, write_fd]))])
        closed = []
        real = B.close_all
        def capture(fds):
            closed.extend(fds)
            real(fds)
        with mock.patch.object(B, 'close_all', side_effect=capture):
            with self.assertRaisesRegex(B.Unknown, 'ANCILLARY'):
                B.receive(right, B.credentials(), time.monotonic() + 1)
        self.assertEqual(len(closed), 2)
        for fd in closed:
            with self.assertRaises(OSError):
                os.fstat(fd)

    def test_selected_token_peer_and_deadline_shapes(self):
        for peer, token, deadline in ((B.credentials(), 'bad', time.monotonic() + 1),
                                      ((True, 1000, 1000), TOKEN, time.monotonic() + 1),
                                      (B.credentials(), TOKEN, float('nan'))):
            with self.assertRaises(B.Unknown):
                B.transport_selection(peer, token, deadline)

    def test_postcompletion_retry_poisoned(self):
        f = self.fixture()
        f.start()
        self.assertEqual(f.complete(), 'PASS_SYNTHETIC_ONLY')
        with self.assertRaises(B.Unknown):
            f.client.exchange('FINISH', 41)
        self.assertEqual(f.client.state, 'UNKNOWN')
        with self.assertRaises(B.Unknown):
            B.final_verdict(f.client, f.server)

    def test_blocked_parent_close_then_failure_cannot_publish(self):
        f = self.fixture()
        entered, release = threading.Event(), threading.Event()
        class BlockedClose:
            def __getattr__(self, name):
                return getattr(f.server_sock, name)
            def close(self):
                entered.set()
                if not release.wait(2):
                    raise RuntimeError('fixture unblock missing')
                f.server_sock.close()
                raise OSError('synthetic late close failure')
        f.server.sock = BlockedClose()
        f.start()
        try:
            f.prefix()
            f.client.release_private()
            f.tail()
            self.assertTrue(entered.wait(1))
            self.assertEqual(f.client.state, 'SUMMARY_PERMITTED')
            self.assertEqual(f.server.state, 'PEER_EOF')
            self.assertFalse(f.server.socket_closed)
            self.assertFalse(f.server.run_completed)
            self.assertFalse(f.server.join(0.01))
            self.assertEqual(f.output.state, 'BUFFERED')
            self.assertEqual(f.printed, [])
            with self.assertRaisesRegex(B.Unknown, 'FINAL_UNKNOWN'):
                B.final_verdict(f.client, f.server)
            with self.assertRaisesRegex(B.Unknown, 'FINAL_UNKNOWN'):
                f.output.release(f.client, f.server)
            self.assertEqual(f.output.state, 'UNKNOWN')
        finally:
            release.set()
            f.server.join(2)
        self.assertTrue(f.server.run_completed)
        self.assertFalse(f.server.socket_closed)
        self.assertEqual(f.server.state, 'UNKNOWN')
        self.assertEqual(f.printed, [])
        with self.assertRaisesRegex(B.Unknown, 'FINAL_UNKNOWN'):
            B.final_verdict(f.client, f.server)

    def test_blocked_successful_close_releases_only_after_join(self):
        f = self.fixture()
        entered, release = threading.Event(), threading.Event()
        class BlockedClose:
            def __getattr__(self, name):
                return getattr(f.server_sock, name)
            def close(self):
                entered.set()
                if not release.wait(2):
                    raise RuntimeError('fixture unblock missing')
                f.server_sock.close()
        f.server.sock = BlockedClose()
        f.start()
        try:
            f.prefix()
            f.client.release_private()
            f.tail()
            self.assertTrue(entered.wait(1))
            self.assertFalse(f.server.socket_closed)
            self.assertFalse(f.server.join(0))
            with self.assertRaisesRegex(B.Unknown, 'FINAL_UNKNOWN'):
                B.final_verdict(f.client, f.server)
            self.assertEqual(f.output.state, 'BUFFERED')
            self.assertEqual(f.printed, [])
        finally:
            release.set()
            f.server.join(2)
        self.assertEqual(B.final_verdict(f.client, f.server), 'PASS_SYNTHETIC_ONLY')
        f.printed.append(f.output.release(f.client, f.server))
        self.assertEqual(len(f.printed), 1)
        self.assertEqual(json.loads(f.printed[0])['result'], 'PASS')
        with self.assertRaisesRegex(B.Unknown, 'PROVISIONAL_STATE'):
            f.output.release(f.client, f.server)

    def test_unjoined_completed_mediator_refuses_final(self):
        f = self.fixture()
        f.start()
        f.prefix()
        f.client.release_private()
        f.tail()
        f.thread.join(2)  # direct external join is not managed completion admission
        self.assertFalse(f.thread.is_alive())
        self.assertTrue(f.server.run_completed and f.server.socket_closed)
        self.assertFalse(f.server._joined)
        with self.assertRaisesRegex(B.Unknown, 'FINAL_UNKNOWN'):
            B.final_verdict(f.client, f.server)
        self.assertEqual(f.printed, [])
        self.assertTrue(f.server.join(0))
        f.printed.append(f.output.release(f.client, f.server))
        self.assertEqual(len(f.printed), 1)

    def test_provisional_capture_is_bounded_and_one_use(self):
        for value in ('x' * 8193, 'é' * 8191, object()):
            output = B.ProvisionalOutput()
            with self.assertRaises(B.Unknown):
                output.capture(value, flush=True)
            self.assertEqual(output.state, 'UNKNOWN')
        output = B.ProvisionalOutput()
        output.capture('{"result":"PASS"}', flush=True)
        with self.assertRaises(B.Unknown):
            output.capture('{"result":"PASS"}', flush=True)
        self.assertEqual(output.state, 'UNKNOWN')

    def test_wrong_provisional_summary_refuses_after_join(self):
        f = self.fixture()
        f.start()
        f.prefix()
        f.client.release_private()
        # Original construction and close finish, but inject wrong output
        # into the separately selected parent capture rather than expose it.
        f.namespace['print'] = lambda text, **kw: f.output.capture(
            json.dumps(dict(json.loads(text), public_API_operations_added=False)), **kw)
        f.tail()
        self.assertTrue(f.server.join(2))
        self.assertEqual(B.final_verdict(f.client, f.server), 'PASS_SYNTHETIC_ONLY')
        with self.assertRaisesRegex(B.Unknown, 'PROVISIONAL_SUMMARY_BINDING'):
            f.output.release(f.client, f.server)
        self.assertEqual(f.output.state, 'UNKNOWN')
        self.assertEqual(f.printed, [])


if __name__ == '__main__':
    unittest.main()
