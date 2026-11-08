"""Effect-free preflight checks for the B03/B05 mediator feasibility probe."""
import ast
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


SOURCE = Path(__file__).absolute().parents[2] / 't35_external_v1' / 'mediator_probe_0001.py'
spec = importlib.util.spec_from_file_location('mediator_probe_0001', SOURCE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbePreflightTests(unittest.TestCase):
    def test_selected_bwrap_and_preflight_current(self):
        probe.pin_preflight()
        self.assertEqual(hashlib.sha256(probe.TOKEN).hexdigest(),
                         'b5af833c7d35d2097ea775e0b6b53d97649f27cb745315774b41d40732db148d')

    def test_embedded_child_is_syntax_valid_and_has_no_builder_import(self):
        ast.parse(probe.CHILD)
        self.assertNotIn('Source8', probe.CHILD)
        self.assertNotIn('build.py', probe.CHILD)
        self.assertNotIn('mapper', probe.CHILD.lower())

    def test_existing_receipt_refuses_before_scratch_effect(self):
        with tempfile.TemporaryDirectory(prefix='lc-u02-05-mediator-test-') as temp:
            path = Path(temp) / 'existing.json'
            path.write_text('old')
            with self.assertRaisesRegex(RuntimeError, 'fresh receipt required'):
                probe.run(path)
            self.assertEqual(path.read_text(), 'old')


if __name__ == '__main__':
    unittest.main()
