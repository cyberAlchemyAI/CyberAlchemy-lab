import types
import unittest
from unittest.mock import patch

import release as R


class ReleaseTests(unittest.TestCase):
    def test_live_basis_selects_exact_disabled_stage(self):
        stage = R.basis()
        self.assertFalse(stage.STAGE_EFFECT_ENABLED)
        self.assertEqual(stage.PLAN_SHA, R.PLAN_SHA)
        self.assertEqual(stage.COPY_SHA, R.COPY_SHA)
        self.assertEqual(stage.preflight()['input_files'], 991)

    def test_selected_modules_are_compiled_from_verified_buffers(self):
        original = R._exact_module
        observed = []
        def capture(name, raw, path):
            observed.append((name, raw, path))
            return original(name, raw, path)
        with patch.object(R, '_exact_module', capture):
            R.basis()
        self.assertEqual([name for name, _, _ in observed],
                         ['anchored_copy', 'held_stage', 'stage'])
        for name, raw, path in observed:
            self.assertEqual(R.sha(raw), R.sha(path.read_bytes()), name)

    def test_success_route_temporarily_enables_exact_stage(self):
        fake = types.SimpleNamespace(STAGE_EFFECT_ENABLED=False)
        calls = []
        def preflight():
            calls.append('preflight')
            self.assertFalse(fake.STAGE_EFFECT_ENABLED)
        def execute():
            calls.append('execute')
            self.assertTrue(fake.STAGE_EFFECT_ENABLED)
            return {'overall': 'OBSERVED_STAGE_ONLY'}
        fake.preflight = preflight
        fake.execute = execute
        with patch.object(R, 'basis', return_value=fake):
            self.assertEqual(R.execute_reviewed_one_shot()['overall'],
                             'OBSERVED_STAGE_ONLY')
        self.assertEqual(calls, ['preflight', 'execute'])
        self.assertFalse(fake.STAGE_EFFECT_ENABLED)

    def test_post_terminal_failure_propagates_and_disables(self):
        fake = types.SimpleNamespace(STAGE_EFFECT_ENABLED=False)
        fake.preflight = lambda: None
        def failed_close():
            self.assertTrue(fake.STAGE_EFFECT_ENABLED)
            raise RuntimeError('final close failed after terminal write')
        fake.execute = failed_close
        with patch.object(R, 'basis', return_value=fake):
            with self.assertRaisesRegex(RuntimeError, 'final close failed'):
                R.execute_reviewed_one_shot()
        self.assertFalse(fake.STAGE_EFFECT_ENABLED)


if __name__ == '__main__':
    unittest.main()
