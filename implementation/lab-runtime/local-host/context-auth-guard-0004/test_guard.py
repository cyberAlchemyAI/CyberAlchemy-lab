"""Causal held AUTH read tests; all files are disposable dummy bytes, not grants."""
import ast
import hashlib
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import held_auth as H
import projector as P

DUMMY = b'{"not_an_authorization":true}\n'


def fixture(temp):
    root = Path(temp) / 'snapshot'
    auth = root / 'authorization'
    auth.mkdir(parents=True, mode=0o700)
    root.chmod(0o700)
    auth.chmod(0o700)
    leaf = auth / 'context-development.json'
    leaf.write_bytes(DUMMY)
    leaf.chmod(0o600)
    return root, auth, leaf


def pin(raw=DUMMY):
    return hashlib.sha256(raw).hexdigest()


class GuardTests(unittest.TestCase):
    def test_effective_uid_change_during_cleanup_refuses_result_after_all_closes(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            uid = os.getuid()
            state = {'euid': uid, 'cleanup_calls': 0}
            opened, closed = [], []
            real_open, real_close, real_cleanup = os.open, os.close, H._auth_close
            def observed_open(path, flags, *args, **kwargs):
                fd = real_open(path, flags, *args, **kwargs)
                opened.append(fd)
                return fd
            def observed_close(fd):
                real_close(fd)
                closed.append(fd)
            def mutate_after_cleanup(fds):
                failures = real_cleanup(fds)
                state['cleanup_calls'] += 1
                if state['cleanup_calls'] == 1:
                    state['euid'] = uid + 1
                return failures
            with mock.patch.object(H._auth_os, 'getuid', return_value=uid), \
                 mock.patch.object(H._auth_os, 'geteuid', side_effect=lambda: state['euid']), \
                 mock.patch.object(H._auth_os, 'open', observed_open), \
                 mock.patch.object(H._auth_os, 'close', observed_close), \
                 mock.patch.object(H, '_auth_close', mutate_after_cleanup):
                with self.assertRaisesRegex(H.AuthRefused, 'changed during cleanup'):
                    H.read_auth_bytes(leaf, root, pin(), uid)
            self.assertEqual(state['cleanup_calls'], 2)
            self.assertCountEqual(closed, opened)

    def test_cleanup_fault_takes_precedence_over_concurrent_uid_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            uid = os.getuid()
            state = {'euid': uid}
            attempted = []
            real_close = os.close
            def close_and_change(fd):
                index = len(attempted)
                attempted.append(fd)
                real_close(fd)
                if index == 0:
                    state['euid'] = uid + 1
                    raise OSError(5, 'injected close uncertainty')
            with mock.patch.object(H._auth_os, 'getuid', return_value=uid), \
                 mock.patch.object(H._auth_os, 'geteuid', side_effect=lambda: state['euid']), \
                 mock.patch.object(H._auth_os, 'close', close_and_change):
                with self.assertRaises(H.AuthCleanupRefused) as caught:
                    H.read_auth_bytes(leaf, root, pin(), uid)
            self.assertEqual(len(attempted), 2 * len(leaf.parts))
            self.assertEqual(len(caught.exception.cleanup_errors), 1)
            self.assertIsNone(caught.exception.primary_error)

    def test_real_effective_split_refused_before_any_open(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            opened = []
            def forbidden_open(*args, **kwargs):
                opened.append(args)
                raise AssertionError('identity split reached filesystem open')
            with mock.patch.object(H._auth_os, 'getuid', return_value=1000), \
                 mock.patch.object(H._auth_os, 'geteuid', return_value=1001), \
                 mock.patch.object(H._auth_os, 'open', forbidden_open):
                for selected in (1000, 1001):
                    with self.subTest(selected=selected):
                        with self.assertRaisesRegex(H.AuthRefused, 'identity split'):
                            H.read_auth_bytes(leaf, root, pin(), selected)
            self.assertEqual(opened, [])

    def test_wrong_selected_effective_uid_refused_before_any_open(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            opened = []
            with mock.patch.object(H._auth_os, 'getuid', return_value=1000), \
                 mock.patch.object(H._auth_os, 'geteuid', return_value=1000), \
                 mock.patch.object(H._auth_os, 'open', side_effect=lambda *a, **k: opened.append(a)):
                with self.assertRaisesRegex(H.AuthRefused, 'selected effective UID'):
                    H.read_auth_bytes(leaf, root, pin(), 1001)
            self.assertEqual(opened, [])

    def test_effective_uid_change_before_return_refuses_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            uid = os.getuid()
            with mock.patch.object(H._auth_os, 'getuid', return_value=uid), \
                 mock.patch.object(H._auth_os, 'geteuid', side_effect=[uid, uid, uid + 1]):
                with self.assertRaisesRegex(H.AuthRefused, 'changed during read'):
                    H.read_auth_bytes(leaf, root, pin(), uid)

    def test_multiple_close_faults_are_all_reported_without_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            leaf = Path(temp) / 'dummy'
            leaf.write_bytes(DUMMY)
            fds = [os.open(leaf, os.O_RDONLY) for _ in range(3)]
            attempted = []
            real_close = os.close
            def failing_close(fd):
                index = len(attempted)
                attempted.append(fd)
                real_close(fd)
                if index in (0, 2):
                    raise OSError(5, 'injected after-release close fault')
            with mock.patch.object(H._auth_os, 'close', failing_close):
                errors = H._auth_close(fds)
            self.assertEqual(attempted, list(reversed(fds)))
            self.assertEqual([fd for fd, _ in errors], [fds[-1], fds[0]])

    def test_first_middle_last_close_fault_attempts_every_owned_fd(self):
        for position in ('first', 'middle', 'last'):
            with self.subTest(position=position), tempfile.TemporaryDirectory() as temp:
                root, _, leaf = fixture(temp)
                expected = 2 * len(leaf.parts)
                target = {'first': 0, 'middle': expected // 2, 'last': expected - 1}[position]
                opened, attempted, closed = [], [], []
                real_open, real_close = os.open, os.close
                def observed_open(path, flags, *args, **kwargs):
                    fd = real_open(path, flags, *args, **kwargs)
                    opened.append(fd)
                    return fd
                def failing_close(fd):
                    index = len(attempted)
                    attempted.append(fd)
                    real_close(fd)
                    closed.append(fd)
                    if index == target:
                        raise OSError(5, 'injected close after OS release')
                with mock.patch.object(H._auth_os, 'open', observed_open), \
                     mock.patch.object(H._auth_os, 'close', failing_close):
                    with self.assertRaises(H.AuthCleanupRefused) as caught:
                        H.read_auth_bytes(leaf, root, pin(), os.getuid())
                self.assertEqual(len(opened), expected)
                self.assertEqual(len(attempted), expected)
                self.assertCountEqual(attempted, opened)
                self.assertCountEqual(closed, opened)
                self.assertEqual(len(caught.exception.cleanup_errors), 1)
                self.assertIsNone(caught.exception.primary_error)

    def test_uncertain_close_is_not_retried_but_other_fds_are_attempted(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            expected = 2 * len(leaf.parts)
            opened, attempted, closed = [], [], []
            real_open, real_close = os.open, os.close
            uncertain = None
            def observed_open(path, flags, *args, **kwargs):
                fd = real_open(path, flags, *args, **kwargs)
                opened.append(fd)
                return fd
            def failing_close(fd):
                nonlocal uncertain
                index = len(attempted)
                attempted.append(fd)
                if index == 0:
                    uncertain = fd
                    raise OSError(5, 'injected close before OS release')
                real_close(fd)
                closed.append(fd)
            try:
                with mock.patch.object(H._auth_os, 'open', observed_open), \
                     mock.patch.object(H._auth_os, 'close', failing_close):
                    with self.assertRaises(H.AuthCleanupRefused) as caught:
                        H.read_auth_bytes(leaf, root, pin(), os.getuid())
                self.assertEqual(len(opened), expected)
                self.assertEqual(len(attempted), expected)
                self.assertEqual(attempted.count(uncertain), 1)
                self.assertEqual(len(closed), expected - 1)
                self.assertEqual(caught.exception.cleanup_errors[0][0], uncertain)
            finally:
                if uncertain is not None:
                    real_close(uncertain)  # external test cleanup, never production retry

    def test_primary_read_failure_retained_with_secondary_cleanup_fault(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            opened, attempted = [], []
            real_open, real_close = os.open, os.close
            def observed_open(path, flags, *args, **kwargs):
                fd = real_open(path, flags, *args, **kwargs)
                opened.append(fd)
                return fd
            def failing_close(fd):
                index = len(attempted)
                attempted.append(fd)
                real_close(fd)
                if index == 0:
                    raise OSError(5, 'injected cleanup fault')
            primary = H.AuthRefused('primary read validation failed')
            with mock.patch.object(H._auth_os, 'open', observed_open), \
                 mock.patch.object(H._auth_os, 'close', failing_close), \
                 mock.patch.object(H, '_auth_read_bounded', side_effect=primary):
                with self.assertRaises(H.AuthCleanupRefused) as caught:
                    H.read_auth_bytes(leaf, root, pin(), os.getuid())
            self.assertIs(caught.exception.primary_error, primary)
            self.assertIs(caught.exception.__cause__, primary)
            self.assertEqual(len(caught.exception.cleanup_errors), 1)
            self.assertCountEqual(attempted, opened)

    def test_partial_open_failure_retains_primary_and_closes_all_ancestors(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            opened, attempted = [], []
            real_open, real_close = os.open, os.close
            def observed_open(path, flags, *args, **kwargs):
                fd = real_open(path, flags, *args, **kwargs)
                opened.append(fd)
                return fd
            def failing_close(fd):
                index = len(attempted)
                attempted.append(fd)
                real_close(fd)
                if index == 0:
                    raise OSError(5, 'injected cleanup fault')
            primary = OSError(5, 'injected pre-leaf stat failure')
            with mock.patch.object(H._auth_os, 'open', observed_open), \
                 mock.patch.object(H._auth_os, 'close', failing_close), \
                 mock.patch.object(H._auth_os, 'stat', side_effect=primary):
                with self.assertRaises(H.AuthCleanupRefused) as caught:
                    H.read_auth_bytes(leaf, root, pin(), os.getuid())
            self.assertIs(caught.exception.primary_error, primary)
            self.assertIs(caught.exception.__cause__, primary)
            self.assertCountEqual(attempted, opened)

    def test_held_attached_bounded_exact_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            self.assertEqual(H.read_auth_bytes(leaf, root, pin(), os.getuid()), DUMMY)
            with self.assertRaisesRegex(H.AuthRefused, 'digest differs'):
                H.read_auth_bytes(leaf, root, 'a' * 64, os.getuid())

    def test_final_symlink_refused_without_target_read(self):
        with tempfile.TemporaryDirectory() as temp:
            root, auth, leaf = fixture(temp)
            leaf.unlink()
            target = Path(temp) / 'unselected-target'
            target.write_bytes(DUMMY)
            leaf.symlink_to(target)
            opened = []
            original = os.open
            def observed(path, flags, *args, **kwargs):
                if path == 'context-development.json':
                    opened.append(path)
                return original(path, flags, *args, **kwargs)
            with mock.patch.object(H._auth_os, 'open', observed):
                with self.assertRaises(H.AuthRefused):
                    H.read_auth_bytes(leaf, root, pin(), os.getuid())
            self.assertEqual(opened, [])

    def test_ancestor_symlink_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root, auth, leaf = fixture(temp)
            other = root / 'other'
            auth.rename(other)
            auth.symlink_to(other, target_is_directory=True)
            with self.assertRaises((OSError, H.AuthRefused)):
                H.read_auth_bytes(leaf, root, pin(), os.getuid())

    def test_fifo_refused_before_leaf_open_without_blocking(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            leaf.unlink()
            os.mkfifo(leaf, 0o600)
            opened = []
            original = os.open
            def observed(path, flags, *args, **kwargs):
                if path == 'context-development.json':
                    opened.append(path)
                return original(path, flags, *args, **kwargs)
            start = time.monotonic()
            with mock.patch.object(H._auth_os, 'open', observed):
                with self.assertRaisesRegex(H.AuthRefused, 'regular file'):
                    H.read_auth_bytes(leaf, root, pin(), os.getuid())
            self.assertLess(time.monotonic() - start, 1)
            self.assertEqual(opened, [])

    def test_oversize_refused_before_leaf_open(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            leaf.write_bytes(b'x' * (H.AUTH_LIMIT + 1))
            leaf.chmod(0o600)
            opened = []
            original = os.open
            def observed(path, flags, *args, **kwargs):
                if path == 'context-development.json':
                    opened.append(path)
                return original(path, flags, *args, **kwargs)
            with mock.patch.object(H._auth_os, 'open', observed):
                with self.assertRaisesRegex(H.AuthRefused, 'bounded single-link'):
                    H.read_auth_bytes(leaf, root, pin(), os.getuid())
            self.assertEqual(opened, [])

    def test_growth_is_refused_with_opening_size_plus_one_budget(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, leaf = fixture(temp)
            counts = []
            def growing(fd, count):
                counts.append(count)
                return b'x' * count
            with mock.patch.object(H._auth_os, 'read', growing):
                with self.assertRaisesRegex(H.AuthRefused, 'grew during bounded read'):
                    H.read_auth_bytes(leaf, root, pin(), os.getuid())
            self.assertEqual(counts, [len(DUMMY) + 1])

    def test_leaf_swap_after_first_read_refused_even_with_same_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root, auth, leaf = fixture(temp)
            original = H._auth_read_bounded
            calls = []
            def swap(fd, identity):
                raw = original(fd, identity)
                calls.append(1)
                if len(calls) == 1:
                    leaf.rename(auth / 'previous')
                    leaf.write_bytes(DUMMY)
                    leaf.chmod(0o600)
                return raw
            with mock.patch.object(H, '_auth_read_bounded', swap):
                with self.assertRaisesRegex(H.AuthRefused, 'attachment changed'):
                    H.read_auth_bytes(leaf, root, pin(), os.getuid())
            self.assertEqual(len(calls), 1)

    def test_leaf_swap_to_fifo_between_stat_and_open_is_nonblocking(self):
        with tempfile.TemporaryDirectory() as temp:
            root, auth, leaf = fixture(temp)
            original = os.open
            swapped = []
            def swap_open(path, flags, *args, **kwargs):
                if path == 'context-development.json' and not swapped:
                    leaf.rename(auth / 'previous')
                    os.mkfifo(leaf, 0o600)
                    swapped.append(1)
                return original(path, flags, *args, **kwargs)
            start = time.monotonic()
            with mock.patch.object(H._auth_os, 'open', swap_open):
                with self.assertRaisesRegex(H.AuthRefused, 'changed during open'):
                    H.read_auth_bytes(leaf, root, pin(), os.getuid())
            self.assertEqual(swapped, [1])
            self.assertLess(time.monotonic() - start, 1)

    def test_ancestor_swap_after_read_refused_even_with_same_leaf_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root, auth, leaf = fixture(temp)
            original = H._auth_read_bounded
            calls = []
            def swap(fd, identity):
                raw = original(fd, identity)
                calls.append(1)
                if len(calls) == 1:
                    auth.rename(root / 'previous-authorization')
                    replacement = root / 'authorization'
                    replacement.mkdir(mode=0o700)
                    (replacement / leaf.name).write_bytes(DUMMY)
                    (replacement / leaf.name).chmod(0o600)
                return raw
            with mock.patch.object(H, '_auth_read_bounded', swap):
                with self.assertRaisesRegex(H.AuthRefused, 'attachment changed'):
                    H.read_auth_bytes(leaf, root, pin(), os.getuid())
            self.assertEqual(len(calls), 1)

    def test_owner_mode_and_hardlink_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root, auth, leaf = fixture(temp)
            leaf.chmod(0o644)
            with self.assertRaisesRegex(H.AuthRefused, 'owned bounded'):
                H.read_auth_bytes(leaf, root, pin(), os.getuid())
            leaf.chmod(0o600)
            os.link(leaf, auth / 'alias')
            with self.assertRaisesRegex(H.AuthRefused, 'single-link'):
                H.read_auth_bytes(leaf, root, pin(), os.getuid())
            (auth / 'alias').unlink()
            auth.chmod(0o755)
            with self.assertRaisesRegex(H.AuthRefused, 'directory mode'):
                H.read_auth_bytes(leaf, root, pin(), os.getuid())

    def test_exact_pure_projection_replaces_both_sites_and_keeps_hold(self):
        projected, proof = P.project_control('a' * 64)
        tree = ast.parse(projected)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and
                 isinstance(n.func, ast.Name) and n.func.id == '_context_development_auth']
        self.assertEqual(len(calls), 2)
        self.assertEqual(projected.count(b'read_auth_bytes(AUTH, ROOT, AUTH_SHA, os.geteuid())'), 1)
        self.assertNotIn(b'AUTH.read_bytes()', projected)
        self.assertTrue(proof['byte_inverse'])
        self.assertFalse(proof['grant_created'])
        with self.assertRaisesRegex(P.Refused, 'fresh same-family'):
            P.final_context_source_manifest()
        with self.assertRaisesRegex(P.Refused, 'effect-disabled'):
            P.launch_context()


if __name__ == '__main__':
    unittest.main(verbosity=2)
