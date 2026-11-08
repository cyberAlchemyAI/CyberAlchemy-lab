"""Fast changed-code, linked-origin, and no-replace controls for replay."""

import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t08_byte_backed_replay', HERE / 'replay.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class ReplayControls(unittest.TestCase):
    def test_changed_code_refuses_before_side_effect(self):
        with tempfile.TemporaryDirectory(prefix='cal-t08-replay-origin-') as dirname:
            root = Path(dirname)
            prior = R.ROOT
            R.ROOT = root
            try:
                marker = root / 'executed'
                changed = root / 'selected.py'
                changed.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('bad')\n")
                with self.assertRaisesRegex(ValueError, 'selected byte origin differs'):
                    R.exact(Path('selected.py'), hashlib.sha256(b'pass\n').hexdigest())
                self.assertFalse(marker.exists())
            finally:
                R.ROOT = prior

    def test_linked_ancestor_refuses(self):
        with tempfile.TemporaryDirectory(prefix='cal-t08-replay-link-') as dirname:
            root = Path(dirname)
            prior = R.ROOT
            R.ROOT = root
            try:
                real = root / 'real'
                real.mkdir()
                (real / 'selected.py').write_bytes(b'pass\n')
                (root / 'alias').symlink_to(real, target_is_directory=True)
                with self.assertRaises(OSError):
                    R.exact(Path('alias/selected.py'), hashlib.sha256(b'pass\n').hexdigest())
            finally:
                R.ROOT = prior

    def test_receipt_is_no_replace(self):
        with tempfile.TemporaryDirectory(prefix='cal-t08-replay-output-') as dirname:
            prior = R.WORK
            R.WORK = Path(dirname)
            try:
                R.publish('RESULT.json', b'first')
                with self.assertRaises(FileExistsError):
                    R.publish('RESULT.json', b'second')
                self.assertEqual((R.WORK / 'RESULT.json').read_bytes(), b'first')
            finally:
                R.WORK = prior


if __name__ == '__main__':
    unittest.main()
