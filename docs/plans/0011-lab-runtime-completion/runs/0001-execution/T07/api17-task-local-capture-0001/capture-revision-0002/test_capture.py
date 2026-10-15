"""Real owned filesystem races, scheduled at this helper's OS read boundary.

The scheduler delegates to actual os.read, then physically mutates only owned
technical inputs. No original runtime callback, clock, or source is imported or
patched; no read or hash success is mocked.
"""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import anchored_capture as A

HERE = Path(__file__).resolve().parent


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=HERE)
        self.root = Path(self.temp.name)
        self.parent = self.root / 'controlled'; self.parent.mkdir(mode=0o700)
        self.path = self.parent / 'metadata'
        self.raw = b'owned exact metadata\n' * 150000
        self.path.write_bytes(self.raw); self.path.chmod(0o644)
        self.binding = {'path': 'controlled/metadata', 'sha256': hashlib.sha256(self.raw).hexdigest()}

    def tearDown(self):
        self.temp.cleanup()

    def capture(self, binding=None):
        return A._capture_exact(self.root, binding or self.binding)

    def race(self, action, reason):
        actual_read = os.read
        original_identity = (self.path.stat().st_dev, self.path.stat().st_ino)
        scheduled = []
        def read_and_schedule(handle, count):
            raw = actual_read(handle, count)
            info = os.fstat(handle)
            if raw and not scheduled and (info.st_dev, info.st_ino) == original_identity:
                scheduled.append(True); action()
            return raw
        with patch.object(A.os, 'read', side_effect=read_and_schedule):
            with self.assertRaisesRegex(ValueError, reason):
                self.capture()
        self.assertEqual(scheduled, [True])

    def test_01_same_exact_verified_bytes_relative_and_absolute(self):
        self.assertEqual(self.capture(), self.raw)
        self.assertEqual(self.capture(dict(self.binding, path=str(self.path))), self.raw)

    def test_02_symlink_leaf_refused(self):
        self.path.rename(self.parent / 'real'); self.path.symlink_to(self.parent / 'real')
        with self.assertRaisesRegex(ValueError, 'unsafe/unreadable'):
            self.capture()

    def test_03_symlink_ancestor_refused(self):
        self.parent.rename(self.root / 'real'); self.parent.symlink_to(self.root / 'real')
        with self.assertRaisesRegex(ValueError, 'unsafe/unreadable'):
            self.capture()

    def test_04_leaf_replaced_with_identical_bytes_after_read(self):
        def replace():
            self.path.rename(self.parent / 'held-old'); self.path.write_bytes(self.raw)
        self.race(replace, 'file identity changed')

    def test_05_ancestor_replaced_with_identical_leaf_bytes(self):
        def replace():
            self.parent.rename(self.root / 'held-old'); self.parent.mkdir(mode=0o700)
            self.path.write_bytes(self.raw)
        self.race(replace, 'ancestor attachment changed')

    def test_06_already_read_bytes_mutated_refused_even_if_returned_digest_matches(self):
        def mutate():
            with self.path.open('r+b') as stream:
                stream.write(b'X'); stream.flush(); os.fsync(stream.fileno())
        self.race(mutate, 'file identity changed')

    def test_07_truncation_during_capture_refused(self):
        self.race(lambda: self.path.write_bytes(b''), 'file identity changed')

    def test_08_growth_during_capture_refused(self):
        def grow():
            with self.path.open('ab') as stream:
                stream.write(b'new unselected bytes')
        self.race(grow, 'file identity changed')

    def test_09_permission_change_during_capture_refused(self):
        self.race(lambda: self.path.chmod(0o600), 'file identity changed')

    def test_10_ancestor_permission_change_during_capture_refused(self):
        self.race(lambda: self.parent.chmod(0o755), 'ancestor attachment changed')

    def test_11_wrong_digest_refused(self):
        with self.assertRaisesRegex(ValueError, 'digest differs'):
            self.capture(dict(self.binding, sha256='0' * 64))

    def test_12_missing_unreadable_directory_and_nonregular_refused(self):
        self.path.unlink()
        with self.assertRaisesRegex(ValueError, 'unsafe/unreadable'):
            self.capture()
        self.path.write_bytes(b'private technical unreadable'); self.path.chmod(0)
        with self.assertRaisesRegex(ValueError, 'readable'):
            self.capture()
        self.path.chmod(0o600); self.path.unlink(); os.mkfifo(self.path)
        with self.assertRaisesRegex(ValueError, 'regular readable'):
            self.capture()

    def test_13_oversized_sparse_metadata_refused_before_body_read(self):
        with self.path.open('wb') as stream:
            stream.truncate(64 * 1024 * 1024 + 1)
        with self.assertRaisesRegex(ValueError, 'exceeds 64 MiB'):
            self.capture()

    def test_14_closed_canonical_binding_refusals(self):
        for binding in (dict(self.binding, extra=True), dict(self.binding, path='../outside'),
                        dict(self.binding, path='controlled//metadata'), dict(self.binding, sha256='unknown')):
            with self.assertRaises(ValueError):
                self.capture(binding)


if __name__ == '__main__':
    unittest.main(verbosity=2)
