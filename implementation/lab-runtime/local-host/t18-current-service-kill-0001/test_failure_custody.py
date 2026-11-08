"""Failure custody remains useful when its own diagnostic storage fails."""
from contextlib import redirect_stderr
import io
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch
import probe

class FailureCustody(unittest.TestCase):
    def test_success_removes_owned_root(self):
        with probe.retained_case_root() as folder:
            path=Path(folder)
            (path/'actual-journal').write_bytes(b'actual controlled fixture')
        self.assertFalse(path.exists())
    def test_body_failure_keeps_actual_bytes_and_original_error(self):
        stream=io.StringIO()
        with self.assertRaisesRegex(ValueError,'primary fixture failure'),redirect_stderr(stream):
            with probe.retained_case_root() as folder:
                path=Path(folder);(path/'actual-journal').write_bytes(b'actual controlled fixture')
                raise ValueError('primary fixture failure')
        try:
            self.assertEqual((path/'actual-journal').read_bytes(),b'actual controlled fixture')
            self.assertTrue((path/'FAILED-RETAINED.json').is_file())
            self.assertIn(str(path),stream.getvalue())
        finally:shutil.rmtree(path)
    def test_failed_marker_cannot_replace_primary_error_or_lose_locator(self):
        stream=io.StringIO()
        with patch.object(probe,'write',side_effect=OSError('synthetic full diagnostic device')):
            with self.assertRaisesRegex(ValueError,'primary fixture failure'),redirect_stderr(stream):
                with probe.retained_case_root() as folder:
                    path=Path(folder);(path/'actual-journal').write_bytes(b'actual controlled fixture')
                    raise ValueError('primary fixture failure')
        try:
            self.assertEqual((path/'actual-journal').read_bytes(),b'actual controlled fixture')
            self.assertFalse((path/'FAILED-RETAINED.json').exists())
            self.assertIn(str(path),stream.getvalue())
        finally:shutil.rmtree(path)

if __name__=='__main__':unittest.main()
