"""Causal checks for final selected Mapper code reconstruction."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).absolute().with_name('replay_mapper_final.py')
SPEC = importlib.util.spec_from_file_location('t31_mapper_final', MODULE)
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


class FinalMapperTests(unittest.TestCase):
    def test_final_code_is_exact_selected_byte_reconstruction(self):
        self.assertEqual(REPLAY.verify()['final_code_sha256'], REPLAY.POST_SHA)

    def test_changed_selected_code_refused(self):
        with tempfile.TemporaryDirectory(prefix='t31-final-mapper-') as directory:
            changed = Path(directory) / 'build.py'
            changed.write_bytes(REPLAY.reconstruct() + b'\n')
            with patch.object(REPLAY, 'POST', changed):
                with self.assertRaisesRegex(ValueError, 'selected final bytes differ'):
                    REPLAY.verify()

    def test_identical_linked_ancestor_refused(self):
        with tempfile.TemporaryDirectory(prefix='t31-final-mapper-') as directory:
            root = Path(directory)
            actual = root / 'actual'
            actual.mkdir()
            (actual / 'build.py').write_bytes(REPLAY.reconstruct())
            (root / 'linked').symlink_to(actual, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'missing or linked'):
                REPLAY.read_regular(root / 'linked' / 'build.py')


if __name__ == '__main__':
    unittest.main()
