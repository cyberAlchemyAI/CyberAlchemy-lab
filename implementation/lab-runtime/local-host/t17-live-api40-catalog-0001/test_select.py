"""Cold checks for the third live API40 operation slice."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t17_catalog_selector", HERE / "select.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


class CatalogSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(S.exact(S.RECEIPT, S.PINS[S.RECEIPT]))
        cls.prior = json.loads(S.exact(S.PRIOR, S.PINS[S.PRIOR]))

    def test_cold_result(self):
        self.assertEqual(S.select(), json.loads((HERE / "RESULT.json").read_bytes()))
        self.assertEqual(S.select()["cumulative_live_operation_count"], 3)

    def test_missing_or_wrong_cause_does_not_count(self):
        for mutation in (
            lambda r: r["actual_lab_calls"].pop(),
            lambda r: r["actual_lab_calls"][3].update(code="invalid-envelope"),
            lambda r: r["actual_lab_calls"][3].update(case="wrong-scope"),
            lambda r: r["actual_lab_calls"][3].update(kind="result"),
        ):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(self.receipt)
                mutation(changed)
                with self.assertRaisesRegex(ValueError, "pair differs"):
                    S.validate(changed, self.prior)

    def test_changed_effect_or_predecessor_refuses(self):
        changed = copy.deepcopy(self.receipt)
        changed["workspace_after"]["effect_journal"] = 1
        with self.assertRaisesRegex(ValueError, "live cut differs"):
            S.validate(changed, self.prior)
        prior = copy.deepcopy(self.prior)
        prior["cumulative_live_operation_count"] = 34
        with self.assertRaisesRegex(ValueError, "live cut differs"):
            S.validate(self.receipt, prior)

    def test_collapsed_catalog_request_refuses(self):
        changed = copy.deepcopy(self.receipt)
        changed["actual_lab_calls"][3]["request_sha256"] = changed["actual_lab_calls"][1]["request_sha256"]
        with self.assertRaisesRegex(ValueError, "bindings differ"):
            S.validate(changed, self.prior)


if __name__ == "__main__":
    unittest.main()
