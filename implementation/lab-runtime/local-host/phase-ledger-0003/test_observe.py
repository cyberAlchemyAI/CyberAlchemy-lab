"""Actual-clock, fail-closed tests for explicit T35 boundary accounting."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest

from observe import BoundaryLedger, BoundaryRefusal, Selection, VerifiedBoundaries, verify_boundary_selection

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def add_one(value):
    return value + 1


def different(value):
    return value


def raises_original():
    raise RuntimeError("original failure")


def slow_callback():
    time.sleep(0.8)
    return "completed"


def slow_raises_original():
    time.sleep(0.8)
    raise RuntimeError("late original failure")


@contextmanager
def owned_scope(exits):
    try:
        yield "sealed fact"
    finally:
        exits.append("exit")


def selection(name, kind, callback):
    path = Path(__file__).resolve()
    return Selection(name, kind, path, hashlib.sha256(path.read_bytes()).hexdigest(),
                     callback.__qualname__)


def future(seconds=2):
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)


class ExplicitBoundaryObservations(unittest.TestCase):
    def test_closed_candidate_inventory_requires_independent_release_pin(self):
        path = HERE / "selected-boundaries.json"
        pin = hashlib.sha256(path.read_bytes()).hexdigest()
        rows = verify_boundary_selection(path, pin, ROOT)
        self.assertEqual(len(rows), 15)
        self.assertEqual(rows["FACT_SCOPE.read_scope"].kind, "pure_scope")
        self.assertEqual(rows["Service._call"].kind, "callback")
        self.assertEqual(rows["Vault.lock"].kind, "pure_scope")
        self.assertEqual(rows["ApplicationJournal.lock"].kind, "pure_scope")
        with self.assertRaises(TypeError):
            rows.rows["Service._call"] = rows["Service.call"]
        with self.assertRaisesRegex(BoundaryRefusal, "VERIFIED_SELECTION_IMMUTABLE"):
            rows.release_pin = "0" * 64
        with self.assertRaisesRegex(BoundaryRefusal, "BOUNDARY_RELEASE_PIN_REFUSED"):
            verify_boundary_selection(path, "0" * 64, ROOT)
        altered = json.loads(path.read_bytes())
        altered["boundaries"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="cal-t35-boundary-selection-") as temp:
            changed = Path(temp) / "changed.json"
            changed.write_text(json.dumps(altered))
            with self.assertRaisesRegex(BoundaryRefusal, "BOUNDARY_API_ROW_REFUSED"):
                verify_boundary_selection(changed, hashlib.sha256(changed.read_bytes()).hexdigest(), ROOT)
            external = json.loads(path.read_bytes())
            next(row for row in external["boundaries"] if row["name"] == "FACT_SCOPE.read_scope")["sha256"] = "0" * 64
            changed.write_text(json.dumps(external))
            with self.assertRaisesRegex(BoundaryRefusal, "BOUNDARY_ROW_BYTE_REFUSED"):
                verify_boundary_selection(changed, hashlib.sha256(changed.read_bytes()).hexdigest(), ROOT)

    def test_actual_callback_pass_counts_exact_identity_once(self):
        chosen = selection("selected-callback", "callback", add_one)
        ledger = BoundaryLedger("case:pass", future(), VerifiedBoundaries.fixture(chosen))
        self.assertEqual(ledger.callback(chosen, add_one, add_one, future(), 4), 5)
        result = ledger.result()
        self.assertEqual(result["measurement_class"], "fixture-only")
        self.assertEqual(result["boundary_selection_sha256"], "fixture-only")
        self.assertEqual(result["callback_count"], 1)
        self.assertEqual(result["pure_scope_boundary_count"], 0)
        self.assertEqual(result["events"][0]["status"], "PASS")
        self.assertLess(result["events"][0]["completed_at_utc"],
                        result["events"][0]["strictest_observed_expires_at"])

    def test_wrong_callback_identity_or_source_byte_refuses_before_call(self):
        chosen = selection("selected-callback", "callback", add_one)
        ledger = BoundaryLedger("case:origin", future(), VerifiedBoundaries.fixture(chosen))
        with self.assertRaisesRegex(BoundaryRefusal, "BOUNDARY_CALLBACK_IDENTITY_REFUSED"):
            ledger.callback(chosen, different, add_one, future(), 4)
        corrupt = Selection(chosen.name, chosen.kind, chosen.path, "0" * 64, chosen.qualname)
        with self.assertRaisesRegex(BoundaryRefusal, "CLOSED_BOUNDARY_SELECTION_REFUSED"):
            ledger.callback(corrupt, add_one, add_one, future(), 4)
        duplicate = Selection(chosen.name, chosen.kind, chosen.path, chosen.sha256, chosen.qualname)
        with self.assertRaisesRegex(BoundaryRefusal, "CLOSED_BOUNDARY_SELECTION_REFUSED"):
            ledger.callback(duplicate, add_one, add_one, future(), 4)
        bad_ledger = BoundaryLedger("case:bad-digest", future(), VerifiedBoundaries.fixture(corrupt))
        with self.assertRaisesRegex(BoundaryRefusal, "BOUNDARY_CALLBACK_ORIGIN_REFUSED"):
            bad_ledger.callback(corrupt, add_one, add_one, future(), 4)
        self.assertEqual(ledger.result()["events"], [])

    def test_same_selected_function_with_replaced_code_refuses(self):
        chosen = selection("same-object", "callback", add_one)
        ledger = BoundaryLedger("case:replaced-code", future(), VerifiedBoundaries.fixture(chosen))
        original = add_one.__code__
        try:
            add_one.__code__ = different.__code__.replace(co_name="add_one", co_qualname="add_one")
            with self.assertRaisesRegex(BoundaryRefusal, "BOUNDARY_CALLBACK_CODE_REFUSED"):
                ledger.callback(chosen, add_one, add_one, future(), 4)
            self.assertEqual(ledger.result()["events"], [])
        finally:
            add_one.__code__ = original

    def test_actual_expired_deadline_refuses_without_invocation(self):
        calls = []
        def unused():
            calls.append(1)
        chosen = selection("expired", "callback", unused)
        ledger = BoundaryLedger("case:expired-before", future(), VerifiedBoundaries.fixture(chosen))
        with self.assertRaisesRegex(BoundaryRefusal, "OBSERVED_DEADLINE_EXPIRED_BEFORE"):
            ledger.callback(chosen, unused, unused,
                            datetime.now(timezone.utc) - timedelta(milliseconds=1))
        self.assertEqual(calls, [])
        self.assertEqual(ledger.result()["callback_count"], 0)
        self.assertEqual(ledger.result()["events"][0]["status"], "REFUSED_EXPIRED_BEFORE")

    def test_expired_source_period_refuses_even_with_future_lease(self):
        calls = []
        def unused():
            calls.append(1)
        chosen = selection("expired-source", "callback", unused)
        ledger = BoundaryLedger("case:source-expired", datetime.now(timezone.utc) - timedelta(milliseconds=1),
                                VerifiedBoundaries.fixture(chosen))
        with self.assertRaisesRegex(BoundaryRefusal, "OBSERVED_DEADLINE_EXPIRED_BEFORE"):
            ledger.callback(chosen, unused, unused, future())
        self.assertEqual(calls, [])
        self.assertEqual(ledger.result()["callback_count"], 0)

    def test_real_clock_expiry_after_callback_refuses_result(self):
        chosen = selection("slow", "callback", slow_callback)
        ledger = BoundaryLedger("case:expired-after", future(), VerifiedBoundaries.fixture(chosen))
        with self.assertRaisesRegex(BoundaryRefusal, "OBSERVED_DEADLINE_EXPIRED_AFTER"):
            ledger.callback(chosen, slow_callback, slow_callback,
                            datetime.now(timezone.utc) + timedelta(milliseconds=500))
        self.assertEqual(ledger.result()["callback_count"], 1)
        self.assertEqual(ledger.result()["events"][0]["status"], "EXPIRED_AFTER")
        self.assertTrue(ledger.result()["events"][0]["expired_at_completion"])

    def test_original_callback_exception_is_preserved_and_counted(self):
        chosen = selection("raises", "callback", raises_original)
        ledger = BoundaryLedger("case:exception", future(), VerifiedBoundaries.fixture(chosen))
        with self.assertRaisesRegex(RuntimeError, "original failure"):
            ledger.callback(chosen, raises_original, raises_original, future())
        self.assertEqual(ledger.result()["callback_count"], 1)
        self.assertEqual(ledger.result()["events"][0]["exception_class"], "RuntimeError")
        self.assertFalse(ledger.result()["events"][0]["expired_at_completion"])

    def test_original_exception_after_deadline_stays_original_and_marks_expiry(self):
        chosen = selection("slow-raises", "callback", slow_raises_original)
        ledger = BoundaryLedger("case:late-exception", future(), VerifiedBoundaries.fixture(chosen))
        with self.assertRaisesRegex(RuntimeError, "late original failure"):
            ledger.callback(chosen, slow_raises_original, slow_raises_original,
                            datetime.now(timezone.utc) + timedelta(milliseconds=500))
        row = ledger.result()["events"][0]
        self.assertEqual(row["status"], "CALLBACK_RAISED")
        self.assertTrue(row["expired_at_completion"])

    def test_real_pure_scope_entry_exit_and_expiry_preserve_cleanup(self):
        exits = []
        chosen = selection("fact-scope", "pure_scope", owned_scope)
        ledger = BoundaryLedger("case:scope", future(), VerifiedBoundaries.fixture(chosen))
        with ledger.pure_scope(chosen, owned_scope, owned_scope, future(), exits) as fact:
            self.assertEqual(fact, "sealed fact")
        self.assertEqual(exits, ["exit"])
        self.assertEqual(ledger.result()["pure_scope_boundary_count"], 2)
        with self.assertRaisesRegex(BoundaryRefusal, "OBSERVED_DEADLINE_EXPIRED_AFTER"):
            with ledger.pure_scope(chosen, owned_scope, owned_scope,
                                   datetime.now(timezone.utc) + timedelta(milliseconds=500), exits):
                time.sleep(0.8)
        self.assertEqual(exits, ["exit", "exit"])
        self.assertEqual(ledger.result()["pure_scope_boundary_count"], 4)
        self.assertEqual(ledger.result()["events"][-1]["status"], "EXPIRED_AFTER")

    def test_scope_body_exception_preserves_original_and_runs_exit(self):
        exits = []
        chosen = selection("fact-scope", "pure_scope", owned_scope)
        ledger = BoundaryLedger("case:scope-error", future(), VerifiedBoundaries.fixture(chosen))
        with self.assertRaisesRegex(RuntimeError, "original body failure"):
            with ledger.pure_scope(chosen, owned_scope, owned_scope, future(), exits):
                raise RuntimeError("original body failure")
        self.assertEqual(exits, ["exit"])
        self.assertEqual(ledger.result()["pure_scope_boundary_count"], 2)
        self.assertEqual(ledger.result()["events"][0]["exception_class"], "RuntimeError")


if __name__ == "__main__":
    unittest.main()
