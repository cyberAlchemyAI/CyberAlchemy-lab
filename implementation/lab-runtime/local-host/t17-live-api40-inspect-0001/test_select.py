"""Cold checks for the fifth live API40 operation slice."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t17_inspect_selector", HERE / "select.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


class InspectSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(S.exact(S.RECEIPT, S.PINS[S.RECEIPT]))
        cls.prior = json.loads(S.exact(S.PRIOR, S.PINS[S.PRIOR]))
        cls.prior_receipt = json.loads(S.exact(S.PRIOR_RECEIPT, S.PINS[S.PRIOR_RECEIPT]))

    def test_cold_result(self):
        self.assertEqual(S.select(), json.loads((HERE / "RESULT.json").read_bytes()))
        self.assertEqual(S.select()["cumulative_live_operation_count"], 5)

    def test_missing_or_wrong_cause_does_not_count(self):
        for mutation in (
            lambda r: r["actual_lab_calls"].pop(),
            lambda r: r["actual_lab_calls"][7].update(code="invalid-envelope"),
            lambda r: r["actual_lab_calls"][7].update(case="wrong-scope"),
            lambda r: r["actual_lab_calls"][7].update(kind="result"),
        ):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(self.receipt)
                mutation(changed)
                with self.assertRaisesRegex(ValueError, "pair differs"):
                    S.validate(changed, self.prior, self.prior_receipt)

    def test_changed_effect_or_predecessor_refuses(self):
        changed = copy.deepcopy(self.receipt)
        changed["workspace_after"]["effect_journal"] = 1
        with self.assertRaisesRegex(ValueError, "live cut differs"):
            S.validate(changed, self.prior, self.prior_receipt)
        prior = copy.deepcopy(self.prior)
        prior["cumulative_live_operation_count"] = 34
        with self.assertRaisesRegex(ValueError, "live cut differs"):
            S.validate(self.receipt, prior, self.prior_receipt)

    def test_changed_runtime_cut_refuses(self):
        changed = copy.deepcopy(self.receipt)
        changed["source_cut_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "live cut differs"):
            S.validate(changed, self.prior, self.prior_receipt)

    def test_collapsed_inspection_request_refuses(self):
        changed = copy.deepcopy(self.receipt)
        changed["actual_lab_calls"][7]["request_sha256"] = changed["actual_lab_calls"][6]["request_sha256"]
        with self.assertRaisesRegex(ValueError, "bindings differ"):
            S.validate(changed, self.prior, self.prior_receipt)

    def test_missing_queried_artifact_refuses(self):
        changed = copy.deepcopy(self.receipt)
        del changed["selected_artifact_sha256"]
        with self.assertRaisesRegex(ValueError, "bindings differ"):
            S.validate(changed, self.prior, self.prior_receipt)


if __name__ == "__main__":
    unittest.main()
