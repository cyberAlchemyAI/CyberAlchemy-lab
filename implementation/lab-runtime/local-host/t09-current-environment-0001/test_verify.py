"""Focused supported/unsupported current composite environment checks."""
import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t09_current_environment', HERE / 'verify.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class EnvironmentTests(unittest.TestCase):
    def test_selected_environment_and_complete_install(self):
        result = check.verify()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['installed_file_count'], 1010)
        self.assertEqual(result['actual_environment']['guard'], 'PASS')

    def test_changed_requested_environment_refuses(self):
        with self.assertRaisesRegex(ValueError, 'requested composite environment differs'):
            check.verify(expected_environment={'python': '0.0.0'})

    def test_unselected_jsonschema_environment_refuses(self):
        with self.assertRaisesRegex(ValueError, 'API environment differs without selected jsonschema overlay'):
            check.verify(include_overlay=False)

    def test_changed_source_pin_refuses(self):
        path = check.API / 'source-manifest.json'
        with patch.dict(check.PINS, {path: '0' * 64}):
            with self.assertRaisesRegex(ValueError, 'selected environment input changed'):
                check.verify()

    def test_equal_byte_symlinked_ancestor_refuses(self):
        with tempfile.TemporaryDirectory(prefix='t09-', dir=HERE) as scratch:
            parent = Path(scratch)
            real = parent / 'real'
            real.mkdir()
            (real / 'selected.json').write_bytes(b'{}')
            (parent / 'alias').symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'missing, linked or unsafe'):
                check.read_exact(parent / 'alias' / 'selected.json', hashlib.sha256(b'{}').hexdigest())

if __name__ == '__main__':
    unittest.main()
