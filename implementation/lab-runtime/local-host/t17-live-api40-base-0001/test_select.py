"""Check the second live API40 operation without calling the API again."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t17_api40_base_selector", HERE / "select.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BaseStatusSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(module.exact(module.RECEIPT, module.PINS[module.RECEIPT]))
        cls.prior = json.loads(module.exact(
            next(p for p in module.PINS if p.endswith("t17-live-api40-slice-0001/RESULT.json")),
            next(d for p, d in module.PINS.items() if p.endswith("t17-live-api40-slice-0001/RESULT.json"))))

    def test_cold_selected_result_and_retained_bytes(self):
        selected = module.select()
        self.assertEqual(selected, json.loads((HERE / "RESULT.json").read_bytes()))
        self.assertEqual(selected["cumulative_live_operation_count"], 2)
        self.assertFalse(selected["T17_complete"])

    def test_missing_or_changed_refusal_cannot_count(self):
        for mutation in (
            lambda r: r["actual_lab_calls"].pop(),
            lambda r: r["actual_lab_calls"][2].update(code="ok"),
            lambda r: r["actual_lab_calls"][2].update(operation="catalog.get"),
        ):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(self.receipt)
                mutation(changed)
                with self.assertRaisesRegex(ValueError, "pair differs|inventory differs"):
                    module.validate(changed, self.prior)

    def test_changed_effect_or_predecessor_refuses(self):
        changed = copy.deepcopy(self.receipt)
        changed["workspace_after"]["effect_journal"] = 1
        with self.assertRaisesRegex(ValueError, "live cut differs"):
            module.validate(changed, self.prior)
        prior = copy.deepcopy(self.prior)
        prior["qualified_operation_slice"] = []
        with self.assertRaisesRegex(ValueError, "live cut differs"):
            module.validate(self.receipt, prior)

    def test_collapsed_request_bindings_refuse(self):
        changed = copy.deepcopy(self.receipt)
        changed["actual_lab_calls"][2]["request_sha256"] = changed["actual_lab_calls"][0]["request_sha256"]
        with self.assertRaisesRegex(ValueError, "byte bindings differ"):
            module.validate(changed, self.prior)


if __name__ == "__main__":
    unittest.main()
