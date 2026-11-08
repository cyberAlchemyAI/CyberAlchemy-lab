"""Fault regressions for the inert v7 mediator controller; never launches bwrap."""
import contextlib
import errno
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import select
import signal
import socket
import stat
import tempfile
import threading
import time
import unittest
from unittest import mock


SOURCE = Path(__file__).absolute().parents[2] / 't35_external_v1' / 'mediator_probe_0007.py'
spec = importlib.util.spec_from_file_location('mediator_probe_0007', SOURCE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbeV7Tests(unittest.TestCase):
    def child_value(self, family_id):
        rows = [[0, os.O_RDONLY, stat.S_IFCHR],
                [1, os.O_WRONLY, stat.S_IFIFO],
                [2, os.O_WRONLY, stat.S_IFIFO],
                [3, os.O_RDWR, stat.S_IFSOCK]]
        return {'schema_version': 'lab-lcu0205-b03b05-mediator-child/v7',
                'result': 'PASS', 'mount_dev': family_id[0],
                'mount_ino': family_id[1], 'fd_before': rows,
                'fd_after': [row.copy() for row in rows],
                'mediated_sha256': probe.digest(probe.TOKEN),
                'direct_write_errno': errno.EROFS}

    def test_closed_child_schema_reconstructs_only_allowlisted_fields(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-json-') as root:
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                family_id = probe.ident(fd)
                raw = json.dumps(self.child_value(family_id)).encode()
                clean = probe.validated_child_observation(raw, family_id)
                self.assertEqual(clean, self.child_value(family_id))
                self.assertIsNot(clean['fd_before'], clean['fd_after'])
                for field, replacement in (('mount_dev', True),
                                           ('direct_write_errno', True),
                                           ('fd_before', [[0, 0, stat.S_IFCHR],
                                                          [1, 1, stat.S_IFIFO],
                                                          [2, 1, stat.S_IFIFO],
                                                          [3, 2, True]])):
                    malformed = dict(self.child_value(family_id), **{field: replacement})
                    with self.assertRaises(probe.ProbeError):
                        probe.validated_child_observation(json.dumps(malformed).encode(), family_id)
            finally:
                os.close(fd)

    def test_extra_text_extra_fd_element_and_duplicate_key_never_publish(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-json-') as root:
            family = Path(root) / 'family'
            family.mkdir(mode=0o700)
            family_id = probe.path_ident(family)
            base = self.child_value(family_id)
            extra_text = dict(base, arbitrary_private_text='DO_NOT_PUBLISH_THIS')
            extra_fd = json.loads(json.dumps(base))
            extra_fd['fd_before'][3].append(999)
            encoded = json.dumps(base)
            duplicate = encoded.replace('"result": "PASS"',
                                        '"result": "PASS", "result": "DO_NOT_PUBLISH_THIS"', 1)
            for index, variant in enumerate((json.dumps(extra_text), json.dumps(extra_fd), duplicate)):
                with self.subTest(index=index):
                    evidence = Path(root) / f'evidence-{index}'
                    evidence.mkdir(mode=0o700)
                    with mock.patch.object(probe, 'EVIDENCE', evidence):
                        try:
                            child_observation = probe.validated_child_observation(
                                variant.encode(), family_id)
                        except probe.ProbeError as exc:
                            result = {'candidate_result': 'UNKNOWN', 'failure_code': exc.code,
                                      'observation': {}}
                        else:
                            result = {'candidate_result': 'PASS',
                                      'observation': {'child': child_observation}}
                        dirfd = probe.evidence_root()
                        try:
                            probe.reserve(dirfd)
                            terminal, _, _, _ = probe.publish_terminal(dirfd, result)
                            self.assertEqual(terminal, 'UNKNOWN')
                            receipt = (evidence / 'attempt-0001.provisional.json').read_bytes()
                            self.assertNotIn(b'DO_NOT_PUBLISH_THIS', receipt)
                            self.assertNotIn(b'arbitrary_private_text', receipt)
                            self.assertEqual(json.loads(receipt)['observation'], {})
                        finally:
                            os.close(dirfd)

    def test_selected_preflight_and_held_bwrap(self):
        fd, selected = probe.fixed_selected(probe.PREFLIGHT, probe.PREFLIGHT_SHA, 8192, os.getuid())
        os.close(fd)

    def test_selected_bwrap_fd3_mechanism_is_explicit(self):
        argv = probe.bwrap_argv(Path('/tmp/inert-family'))
        self.assertEqual(argv[1:7], ['--die-with-parent', '--unshare-all', '--clearenv',
                                     '--as-pid-1', '--sync-fd', '3'])
        self.assertNotIn('--preserve-fds', argv)
        self.assertEqual(probe.stderr_diagnostic(b'bwrap: Unknown option --preserve-fds'),
                         'BWRAP_UNKNOWN_OPTION')
        self.assertEqual(probe.stderr_diagnostic(b'private arbitrary text'), 'OTHER_STDERR')
        fd, selected = probe.fixed_selected(probe.BWRAP, probe.BWRAP_SHA, 100000, 0)
        self.assertEqual(probe.ident(fd), selected)
        os.close(fd)

    def test_symlink_and_changed_selected_bytes_refuse(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-test-') as root:
            path = Path(root) / 'source'
            path.write_bytes(b'a')
            selected = hashlib.sha256(b'a').hexdigest()
            fd, _ = probe.fixed_selected(path, selected, 10)
            path.write_bytes(b'b')
            self.assertNotEqual(probe.hash_fd(fd, 10)[0], selected)
            os.close(fd)
            link = Path(root) / 'link'
            link.symlink_to(path)
            with self.assertRaises(OSError):
                probe.fixed_selected(link, selected, 10)

    def test_no_replace_reservation_and_early_unknown(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-evidence-') as root:
            evidence = Path(root) / 'evidence'
            evidence.mkdir(mode=0o700)
            with mock.patch.object(probe, 'EVIDENCE', evidence):
                fd = probe.evidence_root()
                try:
                    probe.reserve(fd)
                    with self.assertRaises(probe.ProbeError):
                        probe.reserve(fd)
                finally:
                    os.close(fd)
                (evidence / 'attempt-0001.pending').unlink()
                with mock.patch.object(probe.tempfile, 'mkdtemp', side_effect=OSError('injected setup failure')):
                    with contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaisesRegex(probe.ProbeError, 'ATTEMPT_UNKNOWN'):
                            probe.run(hashlib.sha256(SOURCE.read_bytes()).hexdigest())
                receipt = json.loads((evidence / 'attempt-0001.provisional.json').read_text())
                witness = json.loads((evidence / 'attempt-0001.attachment.json').read_text())
                self.assertEqual(receipt['result'], 'PROVISIONAL')
                self.assertEqual(receipt['candidate_result'], 'UNKNOWN')
                self.assertEqual(witness['result'], 'UNKNOWN')
                self.assertEqual(receipt['failure_code'], 'INTERNAL_OR_SETUP_UNKNOWN')
                self.assertIsNone(receipt['scratch_path'])
                self.assertTrue((evidence / 'attempt-0001.pending').exists())

    def test_partial_reservation_fsync_keeps_no_retry_marker(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-reserve-') as root:
            evidence = Path(root) / 'evidence'
            evidence.mkdir(mode=0o700)
            with mock.patch.object(probe, 'EVIDENCE', evidence):
                fd = probe.evidence_root()
                try:
                    with mock.patch.object(probe.os, 'fsync', side_effect=OSError('injected fsync failure')):
                        with self.assertRaises(OSError):
                            probe.reserve(fd)
                    self.assertTrue((evidence / 'attempt-0001.pending').exists())
                    with self.assertRaises(probe.ProbeError):
                        probe.reserve(fd)
                finally:
                    os.close(fd)

    def test_equal_content_evidence_replacement_refuses_terminal_pass(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-attach-') as root:
            evidence = Path(root) / 'evidence'
            moved = Path(root) / 'held-original'
            evidence.mkdir(mode=0o700)
            with mock.patch.object(probe, 'EVIDENCE', evidence):
                fd = probe.evidence_root()
                try:
                    probe.reserve(fd)
                    original = probe.fsync_write
                    def replace_after_provisional(dirfd, name, raw):
                        original(dirfd, name, raw)
                        if name == 'attempt-0001.provisional.json':
                            evidence.rename(moved)
                            evidence.mkdir(mode=0o700)
                            (evidence / 'attempt-0001.pending').write_bytes((moved / 'attempt-0001.pending').read_bytes())
                    with mock.patch.object(probe, 'fsync_write', side_effect=replace_after_provisional):
                        status, _, _, attached = probe.publish_terminal(fd, {'candidate_result': 'PASS'})
                    self.assertEqual(status, 'UNKNOWN')
                    self.assertFalse(attached)
                    self.assertFalse((evidence / 'attempt-0001.provisional.json').exists())
                    self.assertTrue((moved / 'attempt-0001.attachment-drift.json').exists())
                    self.assertTrue((moved / 'attempt-0001.pending').exists())
                finally:
                    os.close(fd)

    def test_detachment_after_witness_refuses_terminal_pass(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-detach-') as root:
            evidence = Path(root) / 'evidence'
            moved = Path(root) / 'held-original'
            evidence.mkdir(mode=0o700)
            with mock.patch.object(probe, 'EVIDENCE', evidence):
                fd = probe.evidence_root()
                try:
                    probe.reserve(fd)
                    original = probe.fsync_write
                    def detach_after_witness(dirfd, name, raw):
                        original(dirfd, name, raw)
                        if name == 'attempt-0001.attachment.json':
                            evidence.rename(moved)
                    with mock.patch.object(probe, 'fsync_write', side_effect=detach_after_witness):
                        status, _, _, attached = probe.publish_terminal(fd, {'candidate_result': 'PASS'})
                    self.assertEqual(status, 'UNKNOWN')
                    self.assertFalse(attached)
                    self.assertFalse(evidence.exists())
                    self.assertEqual(json.loads((moved / 'attempt-0001.attachment-drift.json').read_text())['result'], 'UNKNOWN')
                    self.assertTrue((moved / 'attempt-0001.pending').exists())
                finally:
                    os.close(fd)

    def test_incremental_output_limit_with_other_pipe_open(self):
        ready_r, ready_w = os.pipe()
        stdout_r, stdout_w = os.pipe()
        stderr_r, stderr_w = os.pipe()
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-stream-') as root:
            family = Path(root)
            family_fd = os.open(family, os.O_RDONLY | os.O_DIRECTORY)
            os.write(ready_w, b'S')
            def noisy():
                try:
                    for _ in range(4):
                        os.write(stdout_w, b'x' * 4096)
                except OSError:
                    pass
            thread = threading.Thread(target=noisy)
            thread.start()
            state = {'established': False}
            try:
                with mock.patch.object(probe, 'leader_exited', return_value=False):
                    with self.assertRaisesRegex(probe.ProbeError, 'OUTPUT_OVERFLOW'):
                        probe.streaming(1, 1, ready_r, parent, stdout_r, stderr_r,
                                        family_fd, family, probe.ident(family_fd), time.monotonic() + 2,
                                        state, {'stdout': bytearray(), 'stderr': bytearray()})
            finally:
                for fd in (ready_r, ready_w, stdout_r, stdout_w, stderr_r, stderr_w, family_fd):
                    os.close(fd)
                parent.close()
                child.close()
                thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.assertTrue(state['established'])

    def test_early_failure_retains_bounded_sanitized_stderr(self):
        ready_r, ready_w = os.pipe()
        stdout_r, stdout_w = os.pipe()
        stderr_r, stderr_w = os.pipe()
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-early-') as root:
            family = Path(root)
            family_fd = os.open(family, os.O_RDONLY | os.O_DIRECTORY)
            os.write(ready_w, b'S')
            os.write(stderr_w, b'bwrap: Unknown option --preserve-fds\n')
            os.close(stdout_w)
            os.close(stderr_w)
            child.close()
            state = {'established': False}
            trace = {'stdout': bytearray(), 'stderr': bytearray()}
            try:
                with mock.patch.object(probe, 'leader_exited', return_value=True):
                    with self.assertRaisesRegex(probe.ProbeError, 'MEDIATOR_REQUEST'):
                        probe.streaming(1, 1, ready_r, parent, stdout_r, stderr_r,
                                        family_fd, family, probe.ident(family_fd),
                                        time.monotonic() + 2, state, trace)
                self.assertEqual(bytes(trace['stderr']), b'bwrap: Unknown option --preserve-fds\n')
                self.assertEqual(probe.stderr_diagnostic(trace['stderr']), 'BWRAP_UNKNOWN_OPTION')
            finally:
                for fd in (ready_r, ready_w, stdout_r, stderr_r, family_fd):
                    os.close(fd)
                parent.close()

    def test_exited_leader_still_kills_original_group(self):
        rows = [[(999999, 'Z', 1), (999998, 'S', 2)], [(999999, 'Z', 1)]]
        with mock.patch.object(probe, 'leader_exited', return_value=True), \
             mock.patch.object(probe, 'proc_group_members', side_effect=rows), \
             mock.patch.object(probe.os, 'killpg') as kill, \
             mock.patch.object(probe.os, 'waitpid', return_value=(999999, 0)):
            value = probe.close_group(999999, 1, True, True, time.monotonic() + 1)
        kill.assert_called_with(999999, signal.SIGKILL)
        self.assertTrue(value['original_group_empty'])

    def test_fork_returns_owned_pid_and_exec_payload_has_only_fd0_to_fd3(self):
        executable = os.open('/usr/bin/python3.14', os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        stdin_fd = os.open('/dev/null', os.O_RDONLY | os.O_CLOEXEC)
        ready_r, ready_w = os.pipe2(os.O_CLOEXEC)
        stdout_r, stdout_w = os.pipe2(os.O_CLOEXEC)
        stderr_r, stderr_w = os.pipe2(os.O_CLOEXEC)
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        pid = None
        pidfd = None
        try:
            started = time.monotonic()
            census = "import os,json,fcntl,errno; r=[]; exec('for n in os.listdir(\"/proc/self/fd\"):\\n try: fcntl.fcntl(int(n),fcntl.F_GETFL); r.append(int(n))\\n except OSError as e: assert e.errno==errno.EBADF'); print(json.dumps(sorted(r)))"
            pid = probe.child_launch(['/usr/bin/python3.14', '-B', '-S', '-c', census], executable, child.fileno(), stdin_fd,
                                     stdout_w, stderr_w, ready_w)
            self.assertLess(time.monotonic() - started, 1)
            pidfd = os.pidfd_open(pid)
            self.assertTrue(select.select([ready_r], [], [], 2)[0])
            self.assertEqual(os.read(ready_r, 1), b'S')
            result = probe.close_group(pid, pidfd, True, False, time.monotonic() + 3)
            pid = None
            self.assertTrue(result['leader_reaped'])
            self.assertTrue(os.WIFEXITED(result['leader_status']))
            self.assertEqual(os.WEXITSTATUS(result['leader_status']), 0)
            os.close(stdout_w)
            stdout_w = -1
            self.assertEqual(json.loads(os.read(stdout_r, 128)), [0, 1, 2, 3])
        finally:
            if pid is not None:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)
            if pidfd is not None:
                os.close(pidfd)
            for fd in (executable, stdin_fd, ready_r, ready_w, stdout_r, stdout_w, stderr_r, stderr_w):
                if fd >= 0:
                    os.close(fd)
            parent.close()
            child.close()

    def test_mediator_file_and_directory_fsync_before_ack(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-fsync-') as root:
            family = Path(root)
            fd = os.open(family, os.O_RDONLY | os.O_DIRECTORY)
            syncs = []
            original = os.fsync
            def seen(target):
                syncs.append(target)
                return original(target)
            try:
                with mock.patch.object(probe.os, 'fsync', side_effect=seen):
                    probe.mediator_commit(fd, family, probe.ident(fd))
                self.assertEqual(len(syncs), 2)
                self.assertEqual(syncs[-1], fd)
                self.assertEqual((family / 'mediated.txt').read_bytes(), probe.TOKEN)
            finally:
                os.close(fd)

    def test_legitimate_directory_mutation_passes_poststate(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-post-') as root:
            family = Path(root) / 'family'
            family.mkdir(mode=0o700)
            fd = os.open(family, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                before = probe.ident(fd)
                probe.mediator_commit(fd, family, before)
                after = probe.ident(fd)
                self.assertNotEqual(before, after)
                self.assertEqual(probe.stable_directory_ident(before),
                                 probe.stable_directory_ident(after))
                result = probe.verified_family_poststate(fd, family, before)
                self.assertEqual(result['post_family'], after)
                self.assertEqual(result['leaf_sha256'], probe.digest(probe.TOKEN))
            finally:
                os.close(fd)

    def test_poststate_refuses_directory_swap_and_extra_leaf(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-post-') as root:
            family = Path(root) / 'family'
            held_original = Path(root) / 'held-original'
            family.mkdir(mode=0o700)
            fd = os.open(family, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                before = probe.ident(fd)
                probe.mediator_commit(fd, family, before)
                family.rename(held_original)
                family.mkdir(mode=0o700)
                (family / 'mediated.txt').write_bytes(probe.TOKEN)
                (family / 'mediated.txt').chmod(0o400)
                with self.assertRaisesRegex(probe.ProbeError, 'FAMILY_POSTSTATE'):
                    probe.verified_family_poststate(fd, family, before)
                (family / 'mediated.txt').unlink()
                family.rmdir()
                held_original.rename(family)
                (family / 'extra.txt').write_bytes(b'x')
                with self.assertRaisesRegex(probe.ProbeError, 'FAMILY_POSTSTATE'):
                    probe.verified_family_poststate(fd, family, before)
            finally:
                os.close(fd)

    def test_fifo_poststate_refuses_promptly_in_isolated_child(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-fifo-') as root:
            family = Path(root) / 'family'
            family.mkdir(mode=0o700)
            fd = os.open(family, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                before = probe.ident(fd)
                os.mkfifo('mediated.txt', 0o400, dir_fd=fd)
                pid = os.fork()
                if pid == 0:
                    try:
                        probe.verified_family_poststate(fd, family, before)
                    except probe.ProbeError as exc:
                        os._exit(0 if exc.code == 'MEDIATED_LEAF_TYPE' else 2)
                    except BaseException:
                        os._exit(3)
                    os._exit(4)
                deadline = time.monotonic() + 2
                status = None
                while time.monotonic() < deadline:
                    waited, status = os.waitpid(pid, os.WNOHANG)
                    if waited == pid:
                        break
                    time.sleep(0.01)
                else:
                    os.kill(pid, signal.SIGKILL)
                    os.waitpid(pid, 0)
                    self.fail('FIFO poststate blocked past independent two-second deadline')
                self.assertTrue(os.WIFEXITED(status))
                self.assertEqual(os.WEXITSTATUS(status), 0)
            finally:
                os.close(fd)

    def test_symlink_and_socket_leaf_are_not_regular(self):
        for kind in ('symlink', 'socket'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory(prefix='lc-u02-05-b03b05-special-') as root:
                family = Path(root) / 'family'
                family.mkdir(mode=0o700)
                fd = os.open(family, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                sock = None
                try:
                    before = probe.ident(fd)
                    leaf = family / 'mediated.txt'
                    if kind == 'symlink':
                        leaf.symlink_to('/dev/null')
                    else:
                        sock = socket.socket(socket.AF_UNIX)
                        sock.bind(str(leaf))
                    with self.assertRaisesRegex(probe.ProbeError, 'MEDIATED_LEAF_TYPE'):
                        probe.verified_family_poststate(fd, family, before)
                finally:
                    if sock is not None:
                        sock.close()
                    os.close(fd)


if __name__ == '__main__':
    unittest.main()
