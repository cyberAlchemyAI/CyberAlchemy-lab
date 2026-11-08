import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE))
from lab_runtime.sources import capture


class SuccessorCapture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads((HERE / "profile.json").read_bytes())

    def test_current_t12_source_snapshot(self):
        snapshot = capture(ROOT, self.profile)
        self.assertEqual(snapshot["state"]["node_id"],
                         "project-state:cyberalchemy-v2-to-lab-migration:specialist-owner-bootstrap-0003")
        self.assertGreaterEqual(len(snapshot["subjects"]), 500)

    def test_missing_predecessor_bundle_refused(self):
        wrong = copy.deepcopy(self.profile)
        wrong["operational_roots"].pop(1)
        with self.assertRaisesRegex(Exception, "successor admission predecessor differs"):
            capture(ROOT, wrong)

    def test_wrong_lookup_pin_refused(self):
        wrong = copy.deepcopy(self.profile)
        wrong["current_selection"]["lookup"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(Exception, "source digest mismatch"):
            capture(ROOT, wrong)


if __name__ == "__main__":
    unittest.main()
