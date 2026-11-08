from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t35_native_v4_verify', HERE / 'verify.py')
verify_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = verify_module
spec.loader.exec_module(verify_module)


class PhaseReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((HERE / 'RESULT.json').read_bytes())

    def test_selected_run(self):
        verify_module.verify(self.receipt)

    def test_changed_session_lease_refused(self):
        changed = deepcopy(self.receipt)
        changed['session_lease_expires_at'] = changed['reader_lease_expires_at']
        with self.assertRaises(ValueError):
            verify_module.verify(changed)

    def test_missing_callback_refused(self):
        changed = deepcopy(self.receipt)
        changed['observation']['events'].pop()
        changed['observation']['callback_count'] -= 1
        with self.assertRaises(ValueError):
            verify_module.verify(changed)

    def test_false_expiry_or_cleanup_refused(self):
        for key in ('expired_request_refused_without_live_resource',
                    'session_closed_and_memory_disposed'):
            changed = deepcopy(self.receipt)
            changed[key] = False
            with self.assertRaises(ValueError):
                verify_module.verify(changed)


if __name__ == '__main__':
    unittest.main()
