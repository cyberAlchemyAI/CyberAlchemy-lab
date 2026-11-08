from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t17_live_slice", HERE / "select.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LiveSlice(unittest.TestCase):
    def setUp(self):
        self.live = json.loads((module.ROOT / module.LIVE).read_bytes())

    def test_selected_live_action_sequence(self):
        result = module.build()
        self.assertEqual(result["qualified_operation_slice"], ["action.dispatch"])
        self.assertFalse(result["T17_complete"])

    def test_wrong_scope_did_not_mutate_owned_effect(self):
        changed = deepcopy(self.live)
        changed["result"]["observations"][4]["counter_after"] = 2
        with self.assertRaisesRegex(ValueError, "Action causal sequence differs"):
            module.classify(changed)

    def test_wrong_scope_must_be_causal_refusal(self):
        changed = deepcopy(self.live)
        changed["result"]["observations"][4]["code"] = "integrity-failed"
        with self.assertRaisesRegex(ValueError, "Action causal sequence differs"):
            module.classify(changed)

    def test_selected_origin_and_34_catalog_required(self):
        for key, value in (("source_manifest_sha256", "0" * 64),):
            changed = deepcopy(self.live)
            changed[key] = value
            with self.assertRaisesRegex(ValueError, "origin or terminal differs"):
                module.classify(changed)
        changed = deepcopy(self.live)
        changed["result"]["events"][1]["catalog_operation_count"] = 33
        with self.assertRaisesRegex(ValueError, "origin or terminal differs"):
            module.classify(changed)


if __name__ == "__main__":
    unittest.main()
