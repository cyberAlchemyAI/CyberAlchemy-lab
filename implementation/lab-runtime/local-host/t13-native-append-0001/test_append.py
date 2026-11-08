import json
from pathlib import Path
import unittest

import append


HERE = Path(__file__).resolve().parent


class NativeAppendTests(unittest.TestCase):
    def test_disposable_append_and_cold_read(self):
        observed = append.run()
        retained = json.loads((HERE / "RESULT.json").read_bytes())
        self.assertEqual(observed, retained)
        self.assertEqual((observed["original_semantic_events_appended"],
                          observed["technical_successor_governance_events_appended"],
                          observed["cold_governance_events"]), (88, 88, 176))
        self.assertTrue(observed["wrong_predecessor_refused_without_effect"])
        self.assertTrue(observed["duplicate_refused_without_effect"])

    def test_changed_preparation_source_refuses_before_native_work(self):
        old = append.PREPARATION_SHA
        try:
            append.PREPARATION_SHA = "0" * 64
            with self.assertRaisesRegex(ValueError, "selected T13 preparation changed"):
                append.run()
        finally:
            append.PREPARATION_SHA = old


if __name__ == "__main__":
    unittest.main()
