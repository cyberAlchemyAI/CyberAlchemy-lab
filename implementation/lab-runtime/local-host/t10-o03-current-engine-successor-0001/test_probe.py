"""Exact one-row rebind and semantic refusal tests for the O03 successor probe."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t10_o03_engine_probe', HERE / 'probe.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class EngineSuccessorProbe(unittest.TestCase):
    def test_01_copied_engine_exact_one_row_profile_rebind(self):
        manifest = probe.verify_successor()
        self.assertEqual(len(manifest['files']), 21)
        self.assertEqual(manifest['profile_binding']['sha256'], probe.NEW_PROFILE_SHA)
        self.assertEqual(probe.sha(probe.ROOT / probe.SOURCE_PATH), probe.NEW_SOURCE_SHA)

    def test_02_changed_current_source_refuses(self):
        with self.assertRaisesRegex(ValueError, 'current authority source differs'):
            probe.verify_successor('0' * 64)

    def test_03_changed_copied_engine_byte_refuses(self):
        actual_sha = probe.sha
        target = HERE / 'engine/lab_runtime/sources.py'
        def changed(path):
            if path == target:
                return '0' * 64
            return actual_sha(path)
        with patch.object(probe, 'sha', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'successor engine member changed'):
                probe.verify_successor()

    def test_04_semantic_current_epoch_mismatch_is_not_selected(self):
        result = probe.attempt()
        self.assertTrue(result['engine_manifest_selected'])
        self.assertEqual(result['scope_state'], 'REFUSED')
        self.assertEqual(result['exception_message'], 'current lookup differs from frozen admission selection')
        self.assertEqual(result['queries_executed'], 0)
        self.assertEqual(result['selected_governed_model_representations'], 0)
        self.assertEqual(result['authority_effect'], 'none')


if __name__ == '__main__':
    unittest.main()
