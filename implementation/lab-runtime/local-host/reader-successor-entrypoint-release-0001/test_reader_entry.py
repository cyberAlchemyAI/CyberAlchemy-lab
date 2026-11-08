from types import SimpleNamespace
import unittest
from unittest.mock import patch

import reader_entry as E


class EntryReleaseTests(unittest.TestCase):
    def test_exact_tool_basis_is_disabled(self):
        module = E.basis()
        self.assertFalse(module.EFFECT_ENABLED)
        self.assertEqual(module.READER_SHA,
                         '048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756')

    def test_drift_refuses_before_import(self):
        with patch.object(E, 'SELECTION_SHA', '0' * 64):
            with self.assertRaisesRegex(E.Refused, 'READER_TOOL_PIN_DRIFT'):
                E.basis()

    def test_effect_enablement_scoped_to_call(self):
        fake = SimpleNamespace(EFFECT_ENABLED=False)
        def run():
            self.assertTrue(fake.EFFECT_ENABLED)
            return {'result': 'PASS_READER_PRIVATE'}
        fake.run = run
        with patch.object(E, 'basis', return_value=fake):
            self.assertEqual(E.execute()['result'], 'PASS_READER_PRIVATE')
        self.assertFalse(fake.EFFECT_ENABLED)


if __name__ == '__main__':
    unittest.main()
