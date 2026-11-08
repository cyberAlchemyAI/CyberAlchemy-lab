"""Focused origin and byte-replay checks for the unselected Mapper recut."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import ast

MODULE = Path(__file__).absolute().with_name('replay_mapper_recut.py')
SPEC = importlib.util.spec_from_file_location('t31_mapper_recut', MODULE)
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


class MapperReplayTests(unittest.TestCase):
    def test_staged_recut_reconstructs_exact_preselection_bytes(self):
        before = REPLAY.exact(REPLAY.PRE, REPLAY.PRE_SHA).decode('utf-8')
        self.assertEqual(before.count(REPLAY.OLD), 1)
        staged = before.replace(REPLAY.OLD, REPLAY.NEW)
        ast.parse(staged)
        self.assertEqual(hashlib.sha256(staged.encode()).hexdigest(), REPLAY.POST_SHA)

    def test_linked_ancestor_refused_even_with_identical_bytes(self):
        with tempfile.TemporaryDirectory(prefix='t31-mapper-recut-') as directory:
            root = Path(directory)
            actual = root / 'actual'
            actual.mkdir()
            raw = b'unchanged selected bytes\n'
            (actual / 'selected.py').write_bytes(raw)
            (root / 'linked').symlink_to(actual, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'missing or linked'):
                REPLAY.exact(root / 'linked' / 'selected.py', hashlib.sha256(raw).hexdigest())

    def test_changed_bytes_refused(self):
        with tempfile.TemporaryDirectory(prefix='t31-mapper-recut-') as directory:
            path = Path(directory) / 'selected.py'
            path.write_bytes(b'changed\n')
            with self.assertRaisesRegex(ValueError, 'code changed'):
                REPLAY.exact(path, hashlib.sha256(b'original\n').hexdigest())


if __name__ == '__main__':
    unittest.main()
