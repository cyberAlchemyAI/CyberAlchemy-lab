"""Focused code-origin and no-follow checks for the API46 status runner."""

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name('run_api46_status_v2.py')


def runner():
    spec = importlib.util.spec_from_file_location('_cal_t31_status_v2_test', SCRIPT)
    selected = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(selected)
    return selected


class StatusOrigin(unittest.TestCase):
    def test_byte_backed_loader_never_reopens_changed_module(self):
        r = runner()
        with tempfile.TemporaryDirectory(prefix='cal-t31-byte-loader-') as temporary:
            path = Path(temporary) / 'selected.py'
            path.write_text('VALUE = "selected"\n')
            captured = r.exact(path, r.sha(path.read_bytes()))
            path.write_text('VALUE = "unselected"\n')
            name = r.PACKAGE_NAME + '.probe'
            finder = r.PinnedAPIFinder({'__init__.py': (path, b''), 'probe.py': (path, captured)})
            sys.meta_path.insert(0, finder)
            try:
                selected = __import__(name, fromlist=['VALUE'])
                self.assertEqual(selected.VALUE, 'selected')
                self.assertEqual(finder.loaded, ['__init__.py', 'probe.py'])
            finally:
                sys.modules.pop(name, None)
                sys.modules.pop(r.PACKAGE_NAME, None)
                sys.meta_path.remove(finder)

    def test_linked_ancestor_and_changed_byte_refuse_capture(self):
        r = runner()
        with tempfile.TemporaryDirectory(prefix='cal-t31-exact-reader-') as temporary:
            root = Path(temporary)
            actual = root / 'actual'
            actual.mkdir()
            file = actual / 'selected.py'
            file.write_text('VALUE = 1\n')
            digest = r.sha(file.read_bytes())
            self.assertEqual(r.exact(file, digest), file.read_bytes())
            with self.assertRaisesRegex(ValueError, 'digest differs'):
                r.exact(file, '0' * 64)
            (root / 'linked').symlink_to(actual, target_is_directory=True)
            with self.assertRaises(OSError):
                r.exact(root / 'linked' / file.name, digest)


if __name__ == '__main__':
    unittest.main(verbosity=2)
