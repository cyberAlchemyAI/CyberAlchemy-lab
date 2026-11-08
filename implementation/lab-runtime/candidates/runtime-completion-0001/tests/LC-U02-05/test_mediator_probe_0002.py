"""Fault regressions for the inert v2 mediator controller; never launches bwrap."""
import contextlib
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import select
import signal
import socket
import tempfile
import threading
import time
import unittest
from unittest import mock


SOURCE = Path(__file__).absolute().parents[2] / 't35_external_v1' / 'mediator_probe_0002.py'
spec = importlib.util.spec_from_file_location('mediator_probe_0002', SOURCE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbeV2Tests(unittest.TestCase):
    def test_selected_preflight_and_held_bwrap(self):
        fd, selected = probe.fixed_selected(probe.PREFLIGHT, probe.PREFLIGHT_SHA, 8192, os.getuid())
        os.close(fd)
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
                receipt = __import__('json').loads((evidence / 'attempt-0001.json').read_text())
                self.assertEqual(receipt['result'], 'UNKNOWN')
                self.assertEqual(receipt['failure_code'], 'INTERNAL_OR_SETUP_UNKNOWN')
                self.assertIsNone(receipt['scratch_path'])

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
                except BrokenPipeError:
                    pass
            thread = threading.Thread(target=noisy)
            thread.start()
            state = {'established': False}
            try:
                with mock.patch.object(probe, 'leader_exited', return_value=False):
                    with self.assertRaisesRegex(probe.ProbeError, 'OUTPUT_OVERFLOW'):
                        probe.streaming(1, 1, ready_r, parent, stdout_r, stderr_r,
                                        family_fd, family, probe.ident(family_fd), time.monotonic() + 2,
                                        state)
            finally:
                for fd in (ready_r, ready_w, stdout_r, stdout_w, stderr_r, stderr_w, family_fd):
                    os.close(fd)
                parent.close()
                child.close()
                thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.assertTrue(state['established'])

    def test_exited_leader_still_kills_original_group(self):
        rows = [[(999999, 'Z', 1), (999998, 'S', 2)], [(999999, 'Z', 1)]]
        with mock.patch.object(probe, 'leader_exited', return_value=True), \
             mock.patch.object(probe, 'proc_group_members', side_effect=rows), \
             mock.patch.object(probe.os, 'killpg') as kill, \
             mock.patch.object(probe.os, 'waitpid', return_value=(999999, 0)):
            value = probe.close_group(999999, 1, True, True, time.monotonic() + 1)
        kill.assert_called_with(999999, signal.SIGKILL)
        self.assertTrue(value['original_group_empty'])

    def test_fork_returns_owned_pid_before_held_inert_exec(self):
        executable = os.open('/usr/bin/dash', os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        stdin_fd = os.open('/dev/null', os.O_RDONLY | os.O_CLOEXEC)
        ready_r, ready_w = os.pipe2(os.O_CLOEXEC)
        stdout_r, stdout_w = os.pipe2(os.O_CLOEXEC)
        stderr_r, stderr_w = os.pipe2(os.O_CLOEXEC)
        parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        pid = None
        pidfd = None
        try:
            started = time.monotonic()
            pid = probe.child_launch(['/usr/bin/dash', '-c', ':'], executable, child.fileno(), stdin_fd,
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
        finally:
            if pid is not None:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)
            if pidfd is not None:
                os.close(pidfd)
            for fd in (executable, stdin_fd, ready_r, ready_w, stdout_r, stdout_w, stderr_r, stderr_w):
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


if __name__ == '__main__':
    unittest.main()
