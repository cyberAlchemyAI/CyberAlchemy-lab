import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

import baseline_guard_v2 as guard
import test_baseline_guard as original_tests

original_tests.guard = guard


class ExistingCases(original_tests.BaselineGuardTests):
    # All original cases rerun against the v2 verification implementation.
    pass


class AnchoredReadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='owned-case-v2-', dir=Path(__file__).parent)
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def test_fifo_refuses_in_bounded_child_before_read(self):
        os.mkfifo(self.root / 'fifo')
        code = 'import baseline_guard_v2 as g; g.read_verified(__import__("pathlib").Path(__import__("sys").argv[1]),"fifo","0"*64)'
        result = subprocess.run([sys.executable, '-B', '-c', code, str(self.root)],
                                cwd=Path(__file__).parent, capture_output=True, timeout=2)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'nonregular binding', result.stderr)

    def test_coherent_repin_refuses_against_independent_old_anchor(self):
        original = b'{"selected_inputs":[{"path":"source"}]}'
        (self.root / 'baseline').write_bytes(b'{"selected_inputs":[]}')
        with self.assertRaisesRegex(ValueError, 'digest drift'):
            guard.anchored_record(self.root, 'baseline', hashlib.sha256(original).hexdigest())

    def test_missing_cli_anchor_has_no_default(self):
        result = subprocess.run([sys.executable, '-B', str(Path(guard.__file__)),
                                 '--root', str(self.root), '--baseline', str(self.root / 'baseline')],
                                capture_output=True, timeout=2)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b'--baseline-sha256', result.stderr)
        self.assertIn(b'--supplement-sha256', result.stderr)

    def test_nonempty_inventory_and_digest_shape(self):
        with self.assertRaisesRegex(ValueError, 'nonempty'):
            guard.verify_bindings(self.root, [])
        for digest in ('', 'X' * 64, None):
            with self.assertRaises(ValueError):
                guard.read_verified(self.root, 'missing', digest)

    def test_record_and_selected_file_size_bounds(self):
        (self.root / 'big').write_bytes(b'12345')
        digest = hashlib.sha256(b'12345').hexdigest()
        with self.assertRaisesRegex(ValueError, 'bound'):
            guard.read_verified(self.root, 'big', digest, limit=4)
        with self.assertRaisesRegex(ValueError, 'bound'):
            guard.read_verified(self.root, 'big', digest, expected_size=3)

    def test_parse_uses_same_verified_held_bytes_without_reopen(self):
        raw = b'{"verified":"original"}'
        (self.root / 'record').write_bytes(raw)
        actual = guard.read_verified
        calls = []
        def interpose(*args, **kwargs):
            data = actual(*args, **kwargs)
            calls.append(args[1])
            (self.root / 'record').write_bytes(b'{"verified":"replacement"}')
            return data
        with mock.patch.object(guard, 'read_verified', side_effect=interpose), mock.patch.object(Path, 'read_text', side_effect=AssertionError('unverified reopen')):
            result = guard.anchored_record(self.root, 'record', hashlib.sha256(raw).hexdigest())
        self.assertEqual(calls, ['record'])
        self.assertEqual(result, {'verified': 'original'})

    def test_named_file_replacement_during_read_refuses(self):
        raw = b'original'
        (self.root / 'record').write_bytes(raw)
        original_read = os.read
        changed = False
        def interpose(fd, size):
            nonlocal changed
            value = original_read(fd, size)
            if not changed:
                changed = True
                (self.root / 'record').rename(self.root / 'retained')
                (self.root / 'record').write_bytes(raw)
            return value
        with mock.patch.object(os, 'read', side_effect=interpose), self.assertRaisesRegex(ValueError, 'detached'):
            guard.read_verified(self.root, 'record', hashlib.sha256(raw).hexdigest())

    def test_anchor_refusal_happens_before_json_parse(self):
        (self.root / 'record').write_bytes(b'not-json')
        with mock.patch.object(guard, 'parse_verified', side_effect=AssertionError('parse-before-anchor')):
            with self.assertRaisesRegex(ValueError, 'digest drift'):
                guard.anchored_record(self.root, 'record', '0' * 64)


if __name__ == '__main__':
    unittest.main()
