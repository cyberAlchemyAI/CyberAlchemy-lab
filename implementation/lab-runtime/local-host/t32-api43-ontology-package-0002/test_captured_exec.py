"""Exercise captured child-code execution against substituted pathname bytes."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('_cal_t32_captured_test', HERE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class CapturedExecution(unittest.TestCase):
    def execute(self, entry, modules=()):
        payload = runner.child_payload(entry[0], entry[1], (entry[0],), modules)
        return subprocess.run([sys.executable, '-I', '-B', '-c', runner.CAPTURED_EXEC],
                              input=payload, capture_output=True, timeout=10)

    def test_entry_uses_selected_bytes_after_path_substitution(self):
        with tempfile.TemporaryDirectory(prefix='cal-t32-entry-') as location:
            path = Path(location) / 'entry.py'
            path.write_bytes(b'print("substituted path")\n')
            result = self.execute((path, b'print("captured entry")\n'))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, b'captured entry\n')

    def test_local_module_uses_selected_bytes_after_path_substitution(self):
        with tempfile.TemporaryDirectory(prefix='cal-t32-module-') as location:
            path = Path(location) / 'dependency.py'
            path.write_bytes(b'value = "substituted path"\n')
            entry = Path(location) / 'entry.py'
            result = self.execute((entry, b'from dependency import value\nprint(value)\n'),
                                  (('dependency', path, b'value = "captured module"\n'),))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, b'captured module\n')


if __name__ == '__main__':
    unittest.main()
