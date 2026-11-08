"""Fail-closed disposable Source probe guards; no historical builder effects."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
sys.path.insert(0, str(REPO / 'implementation/lab-runtime/candidates/runtime-completion-0001'))
from t35_external_v1 import scratch_source_probe as probe


class ScratchSourceProbeGuards(unittest.TestCase):
    def test_bounded_diagnostics_and_nonzero_status(self):
        code, stdout, stderr = probe._run_bounded(
            [sys.executable, '-c', 'import sys; sys.stderr.write("x"*10000)'],
            stream_limit=256, timeout=5)
        self.assertEqual(code, 125)
        self.assertLessEqual(len(stdout), 256)
        self.assertLessEqual(len(stderr), 256)
        code, stdout, stderr = probe._run_bounded(
            [sys.executable, '-c', 'import sys; sys.stderr.write("private fixture"); sys.exit(7)'],
            stream_limit=256, timeout=5)
        self.assertEqual(code, 7)
        self.assertEqual(stdout, b'')
        self.assertEqual(stderr, b'private fixture')

    def test_timeout_reaps_process_group(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-probe-guard-') as scratch:
            marker = Path(scratch) / 'late-marker'
            program = ('import pathlib,time; time.sleep(3); '
                       f'pathlib.Path({str(marker)!r}).write_text("late")')
            code, stdout, stderr = probe._run_bounded(
                [sys.executable, '-c', program], timeout=1)
            self.assertEqual(code, 124)
            self.assertFalse(marker.exists())
            self.assertEqual(stdout, b'')
            self.assertEqual(stderr, b'')

    def test_tree_refuses_aliases_and_observes_empty_directory(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-probe-tree-') as scratch:
            root = Path(scratch)
            first = root / 'first.json'
            first.write_bytes(b'fixture')
            (root / 'empty').mkdir()
            self.assertEqual(probe._tree_files(root), {'first.json': probe._sha(b'fixture')})
            self.assertEqual(probe._tree_dirs(root), {'empty'})
            alias = root / 'alias.json'
            os.link(first, alias)
            with self.assertRaises(ValueError):
                probe._tree_files(root)
            alias.unlink()
            alias.symlink_to(first)
            with self.assertRaises(ValueError):
                probe._tree_files(root)

    def test_historical_member_names_are_closed(self):
        raw = probe._held_input(probe.HISTORICAL_SOURCE_PACKAGE)
        names = probe._historical_package_names(raw)
        self.assertEqual(len(names), 36)
        self.assertIn('branch.snapshot', names)
        self.assertIn('artifacts/20.json', names)
        self.assertNotIn('owner.pem', names)


if __name__ == '__main__':
    unittest.main()
