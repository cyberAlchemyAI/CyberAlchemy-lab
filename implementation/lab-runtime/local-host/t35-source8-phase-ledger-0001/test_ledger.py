from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t35_ledger", HERE / "ledger.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


class FrozenTimingLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v4 = json.loads(ledger.selected(ledger.V4))
        cls.v5 = json.loads(ledger.selected(ledger.V5))
        cls.period = json.loads(ledger.selected(ledger.OLD_PERIOD))

    def test_fresh_result_and_bounded_counts(self):
        fresh = ledger.build()
        self.assertEqual(fresh, json.loads((HERE / "RESULT.json").read_bytes()))
        self.assertEqual((len(fresh["case_rows"]), fresh["case_counts"]["positive_total"]), (85, 85))
        self.assertEqual(fresh["observed_lease_phase"]["v5_lease_capture"], "not_instrumented")
        self.assertEqual(len(fresh["session_expiry_timers"]), 2)

    def test_wrong_source_period_refuses(self):
        bad = deepcopy(self.v4)
        bad["selected_source_period_expires_at"] = "2026-10-23T07:20:00+00:00"
        with self.assertRaisesRegex(ValueError, "source period"):
            ledger.validate_receipts(bad, self.v5)

    def test_utc_monotonic_clock_divergence_refuses(self):
        bad = deepcopy(self.v4)
        bad["case_rows"][27]["monotonic_elapsed_seconds"] += 20
        with self.assertRaisesRegex(ValueError, "clocks disagree"):
            ledger.validate_receipts(bad, self.v5)

    def test_lease_summary_and_timer_false_claims_refuse(self):
        bad = deepcopy(self.v4)
        bad["observed_lease_expiries"]["context_delivery"]["observations"] = 57
        with self.assertRaisesRegex(ValueError, "lease summary"):
            ledger.validate_receipts(bad, self.v5)
        bad = deepcopy(self.v4)
        timer = next(row for row in bad["case_rows"] if row["observed_lease_expiries"]["session"])
        timer["observed_lease_expiries"]["session"] = "2026-10-23T20:00:00+00:00"
        expiries = [row["observed_lease_expiries"]["session"] for row in bad["case_rows"][:68]
                    if row["observed_lease_expiries"]["session"]]
        bad["observed_lease_expiries"]["session"] = {
            "observations": len(expiries), "earliest_expires_at": min(expiries),
            "latest_expires_at": max(expiries)}
        with self.assertRaisesRegex(ValueError, "Session expiry timer"):
            ledger.validate_receipts(bad, self.v5)

    def test_false_pass_or_false_expired_refusal_refuses(self):
        bad = deepcopy(self.v4)
        bad["case_rows"][68]["result"] = "PASS"
        with self.assertRaisesRegex(ValueError, "v4 case selection"):
            ledger.validate_receipts(bad, self.v5)
        bad = deepcopy(self.v5)
        bad["expired_original_claim"] = "expired original constructor passed"
        with self.assertRaisesRegex(ValueError, "expired refusal"):
            ledger.validate_receipts(self.v4, bad)

    def test_selected_byte_drift_refuses(self):
        with self.assertRaisesRegex(ValueError, "selected file bytes changed"):
            ledger.selected((ledger.V4[0], "0" * 64))

    def test_unexpired_historical_period_refuses(self):
        period = deepcopy(self.period)
        period["expires_at"] = "2026-10-24T02:45:14.443492+00:00"
        with self.assertRaisesRegex(ValueError, "not expired"):
            ledger.validate_original_period(period, self.v5)


if __name__ == "__main__":
    unittest.main()
