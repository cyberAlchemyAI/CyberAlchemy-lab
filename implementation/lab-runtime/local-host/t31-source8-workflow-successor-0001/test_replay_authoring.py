"""Focused negative checks for the read-only T31 source-code reconstruction."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t31_replay_authoring', HERE / 'replay_authoring.py')
author = importlib.util.module_from_spec(spec)
spec.loader.exec_module(author)


class ReplayAuthoring(unittest.TestCase):
    def test_selected_bytes_reconstruct(self):
        author.main()

    def test_missing_or_ambiguous_anchor_refuses(self):
        for value in ('other', 'before before'):
            with self.assertRaisesRegex(ValueError, 'anchor missing or ambiguous'):
                author.once(value, 'before', 'after')

    def test_changed_or_linked_preimage_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            regular = root / 'input.py'
            regular.write_bytes(b'changed source')
            with self.assertRaisesRegex(ValueError, 'input changed'):
                author.read_exact(regular, '0' * 64)
            linked = root / 'linked.py'
            linked.symlink_to(regular)
            with self.assertRaisesRegex(ValueError, 'missing or linked'):
                author.read_exact(linked, author.sha(regular.read_bytes()))


if __name__ == '__main__':
    unittest.main()
