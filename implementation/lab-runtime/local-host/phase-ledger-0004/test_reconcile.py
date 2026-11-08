import datetime as dt
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reconcile


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cal-phase-ledger-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.family = self.root / "family/one"
        self.family.mkdir(parents=True)
        self.begin = dt.datetime(2026, 10, 22, 20, 0, tzinfo=dt.timezone.utc)
        self.end = self.begin + dt.timedelta(hours=24)
        self.chain_path = self.root / "chain.json"
        self.api_path = self.root / "api.json"

    def emit(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(reconcile.json.dumps(value, sort_keys=True).encode())
        return {"path": path.relative_to(self.root).as_posix(),
                "sha256": reconcile.sha(path.read_bytes())}

    def fixture(self):
        period = self.emit(self.family / "source/packages/0001/period.json",
                           {"not_before": self.begin.isoformat(), "expires_at": self.end.isoformat()})
        source = self.emit(self.family / "source/source-manifest.json", {"role": "source"})
        source_package = self.emit(self.family / "source/packages/0001/manifest.json", {"role": "source-package"})
        build = self.emit(self.family / "source/packages/0001/build-result.json", {"result": "PASS"})
        reader = self.emit(self.family / "reader/source-manifest.json", {"role": "reader"})
        mapper = self.emit(self.family / "mapped/source-manifest.json", {"role": "mapper"})
        mapper_package = self.emit(self.family / "mapped/packages/0001/manifest.json", {"role": "mapper-package"})
        context = self.emit(self.family / "context/source-manifest.json", {"role": "context"})
        implementation = self.emit(self.family / "context/implementation-binding.json", {"role": "implementation"})
        old_delivery = self.emit(self.family / "context/packages/0001/delivery.json",
                                 {"expires_at": (self.begin + dt.timedelta(minutes=15)).isoformat()})
        context_package = self.emit(self.family / "context/packages/0001/manifest.json",
                                    {"delivery_binding": old_delivery})
        phases = {
            "source": {"source_binding": source, "package_binding": source_package,
                       "native_build_receipt": build},
            "cold": {"result": "PASS-native-cold", "independent_cold_replays": 2,
                     "original_byte_parity": True, "source_binding": source,
                     "package_binding": source_package, "period_binding": period},
            "reader": {"result": "PASS-current-reader", "reader_binding": reader},
            "mapped": {"result": "PASS-native-mapper", "mapper_binding": mapper,
                       "package_binding": mapper_package},
            "context": {"result": "PASS-native-Context-construction", "context_binding": context,
                        "package_binding": context_package, "implementation_binding": implementation},
        }
        rows = {name: self.emit(self.family / (name + "-result.json"), value)
                for name, value in phases.items()}
        self.chain_path.write_text(json.dumps({
            "schema": "cal-native-current-source8-local-chain-receipt/v1",
            "protected_source8_qualification": False, "authority_effect": "none",
            "family_path": "family/one", "instance": "one",
            "not_before": self.begin.isoformat(), "expires_at": self.end.isoformat(),
            "period_binding": period, "phase_results": rows,
        }))
        start = self.begin + dt.timedelta(hours=1)
        end = start + dt.timedelta(seconds=5)
        self.api = {
            "schema": "cal-api33-versioned-whole-classes-timer/v1",
            "test_27_selection": {"successor_sha256": reconcile.TIMER_SUCCESSOR_SHA},
            "family_context_manifest_sha256": context["sha256"],
            "selected_source_period_expires_at": self.end.isoformat(),
            "started_at_utc": start.isoformat(), "completed_at_utc": end.isoformat(),
            "monotonic_elapsed_seconds": 5, "result": "FAIL", "tests_run": 1,
            "selected_case_ids": ["example.Session.test_01"],
            "wrong_origin_old_source_refused": True, "expired_original_negative_passed": True,
            "case_rows": [{"test_id": "example.Session.test_01", "result": "PASS",
                           "started_at_utc": start.isoformat(), "completed_at_utc": end.isoformat(),
                           "monotonic_elapsed_seconds": 5,
                           "observed_lease_expiries": {
                               "reader_policy": (end + dt.timedelta(minutes=5)).isoformat(),
                               "reader_context": None,
                               "context_delivery": (end + dt.timedelta(minutes=4)).isoformat(),
                               "session": (end + dt.timedelta(minutes=3)).isoformat()}}],
            "current_source8_machine_case_rows": [],
        }
        self.api_path.write_text(json.dumps(self.api))

    def test_binds_actual_case_deadlines_without_old_delivery_confusion(self):
        self.fixture()
        value = reconcile.reconcile(self.root, self.chain_path, self.api_path)
        self.assertTrue(value["all_cases_passed"])
        self.assertTrue(value["all_observed_lease_checks_current_at_case_end"])
        self.assertEqual(value["observed_lease_counts"]["session"], 1)
        self.assertEqual(value["original_context_construction_delivery_expires_at"],
                         (self.begin + dt.timedelta(minutes=15)).isoformat())
        self.assertIsNone(value["cases"][0]["callback_count"])

    def test_expired_observed_session_is_reported_without_relabeling(self):
        self.fixture()
        self.api["case_rows"][0]["observed_lease_expiries"]["session"] = (
            self.begin + dt.timedelta(minutes=20)).isoformat()
        self.api_path.write_text(json.dumps(self.api))
        value = reconcile.reconcile(self.root, self.chain_path, self.api_path)
        self.assertFalse(value["all_observed_lease_checks_current_at_case_end"])
        self.assertFalse(value["all_nonexpiry_cases_current_at_case_end"])
        self.assertEqual(value["unexpected_expired_observed_lease_cases"][0]["lease_kinds"], ["session"])
        self.assertFalse(value["cases"][0]["ended_before_strictest_observed_expiry"])

    def test_deliberate_session_expiry_is_evidence_not_unexpected_lease_failure(self):
        self.fixture()
        row = self.api["case_rows"][0]
        row["test_id"] = sorted(reconcile.DELIBERATE_SESSION_EXPIRY_CASES)[0]
        self.api["selected_case_ids"] = [row["test_id"]]
        row["observed_lease_expiries"]["session"] = (
            self.begin + dt.timedelta(minutes=20)).isoformat()
        self.api_path.write_text(json.dumps(self.api))
        value = reconcile.reconcile(self.root, self.chain_path, self.api_path)
        self.assertEqual(value["deliberate_session_expiry_count"], 1)
        self.assertTrue(value["all_nonexpiry_cases_current_at_case_end"])
        self.assertFalse(value["all_observed_lease_checks_current_at_case_end"])
        self.assertEqual(value["unexpected_expired_observed_lease_cases"], [])
        self.assertGreater(value["cases"][0]["session_expiry_lag_seconds"], 0)

    def test_deliberate_expiry_without_observed_session_deadline_refuses(self):
        self.fixture()
        row = self.api["case_rows"][0]
        row["test_id"] = sorted(reconcile.DELIBERATE_SESSION_EXPIRY_CASES)[0]
        self.api["selected_case_ids"] = [row["test_id"]]
        row["observed_lease_expiries"]["session"] = None
        self.api_path.write_text(json.dumps(self.api))
        with self.assertRaisesRegex(ValueError, "DELIBERATE_SESSION_EXPIRY_NOT_OBSERVED"):
            reconcile.reconcile(self.root, self.chain_path, self.api_path)

    def test_deliberate_session_expiry_does_not_hide_expired_reader_policy(self):
        self.fixture()
        row = self.api["case_rows"][0]
        row["test_id"] = sorted(reconcile.DELIBERATE_SESSION_EXPIRY_CASES)[0]
        self.api["selected_case_ids"] = [row["test_id"]]
        row["observed_lease_expiries"]["session"] = (
            self.begin + dt.timedelta(minutes=20)).isoformat()
        row["observed_lease_expiries"]["reader_policy"] = (
            self.begin + dt.timedelta(minutes=25)).isoformat()
        self.api_path.write_text(json.dumps(self.api))
        value = reconcile.reconcile(self.root, self.chain_path, self.api_path)
        self.assertEqual(value["unexpected_expired_observed_lease_cases"][0]["lease_kinds"],
                         ["reader_policy"])

    def test_wrong_timer_successor_pin_refuses(self):
        self.fixture()
        self.api["test_27_selection"]["successor_sha256"] = "0" * 64
        self.api_path.write_text(json.dumps(self.api))
        with self.assertRaisesRegex(ValueError, "VERSIONED_TIMER_SELECTION_REFUSED"):
            reconcile.reconcile(self.root, self.chain_path, self.api_path)

    def test_duplicate_or_swapped_whole_case_refuses(self):
        self.fixture()
        first = self.api["case_rows"][0]
        second = dict(first, test_id="example.Session.test_02")
        self.api["case_rows"] = [first, dict(first)]
        self.api["tests_run"] = 2
        self.api["selected_case_ids"] = ["example.Session.test_01", "example.Session.test_02"]
        self.api_path.write_text(json.dumps(self.api))
        with self.assertRaisesRegex(ValueError, "API_CASE_SET_REFUSED"):
            reconcile.reconcile(self.root, self.chain_path, self.api_path)
        self.api["case_rows"] = [second, first]
        self.api_path.write_text(json.dumps(self.api))
        with self.assertRaisesRegex(ValueError, "API_CASE_SET_REFUSED"):
            reconcile.reconcile(self.root, self.chain_path, self.api_path)

    def test_equal_byte_symlinked_ancestor_refuses(self):
        source = self.root / "real/one/data.json"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"{}")
        (self.root / "alias").symlink_to(self.root / "real", target_is_directory=True)
        row = {"path": "alias/one/data.json", "sha256": reconcile.sha(source.read_bytes())}
        with self.assertRaisesRegex(ValueError, "BINDING_ANCESTOR_SYMLINK_REFUSED"):
            reconcile.checked(self.root, row)

    def test_changed_phase_and_wrong_source_period_refuse(self):
        self.fixture()
        (self.family / "mapped-result.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "BINDING_DIGEST_CHANGED"):
            reconcile.reconcile(self.root, self.chain_path, self.api_path)
        self.fixture()
        self.api["selected_source_period_expires_at"] = self.begin.isoformat()
        self.api_path.write_text(json.dumps(self.api))
        with self.assertRaisesRegex(ValueError, "API_FAMILY_BINDING_REFUSED"):
            reconcile.reconcile(self.root, self.chain_path, self.api_path)

    def test_receipt_is_exclusive_and_private(self):
        output = self.root / "receipt.json"
        reconcile.write_new(output, {"digest_only": True})
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
        self.assertEqual(output.stat().st_uid, os.getuid())
        with self.assertRaises(FileExistsError):
            reconcile.write_new(output, {"digest_only": False})


if __name__ == "__main__":
    unittest.main()
