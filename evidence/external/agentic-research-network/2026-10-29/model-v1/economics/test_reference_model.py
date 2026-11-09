"""Risk-focused checks for the candidate economic mechanism."""

import unittest
from pathlib import Path

from reference_model import ADVANCE_GATES, REVIEW_GATES, Model, Policy, Refusal
from scenario import run as run_scenario
import json


class EconomicsTests(unittest.TestCase):
    def setUp(self):
        self.model = Model(Policy.load(Path(__file__).with_name("simulation-policy.json")))

    def offer(self, name, miner="alice", result="negative"):
        m = self.model
        m.offer_task(name, "epoch-1", slots=1, base=100, bonus=50,
                     reviewer_fee=5, commit_deadline=10, reveal_deadline=20,
                     challenge_end=30)
        m.assign(name, 0, miner)
        commitment = m.commitment(name, 0, miner, "content-digest", "secret")
        m.commit(name, 0, commitment, at=5)
        m.reveal(name, 0, "content-digest", "secret", set(), result, at=15)

    def review(self, name, *, gate_value="pass", resolved=True):
        gates = {key: gate_value for key in REVIEW_GATES}
        self.model.review(name, 0, "reviewer-1", gates, resolved, quality_status="pass")
        self.model.review(name, 0, "reviewer-2", gates, resolved, quality_status="pass")

    def test_negative_and_positive_results_get_equal_valid_work_reward(self):
        self.offer("negative", "alice", "negative")
        self.review("negative")
        self.offer("positive", "bob", "positive")
        self.review("positive")
        self.assertEqual(self.model.finalize_slot("negative", 0, at=31, owner_decision=True, appeal_closed=True), 150)
        self.assertEqual(self.model.finalize_slot("positive", 0, at=31, owner_decision=True, appeal_closed=True), 150)
        self.assertEqual(self.model.w["alice"], self.model.w["bob"])
        self.assertEqual(self.model.epoch_spent["epoch-1"], 320)

    def test_bad_reveal_self_review_and_unknown_gate_hold_award(self):
        self.model.offer_task("task", "epoch-1", slots=1, base=100, bonus=50,
                              reviewer_fee=5, commit_deadline=10, reveal_deadline=20,
                              challenge_end=30)
        self.model.assign("task", 0, "alice")
        self.model.commit("task", 0, self.model.commitment("task", 0, "alice", "a", "n"), at=5)
        with self.assertRaises(Refusal):
            self.model.reveal("task", 0, "b", "n", set(), "positive", at=15)
        self.model.reveal("task", 0, "a", "n", set(), "null", at=15)
        with self.assertRaises(Refusal):
            self.model.review("task", 0, "alice", {key: "pass" for key in REVIEW_GATES}, False,
                              quality_status="pass")
        self.review("task", gate_value="unknown", resolved=False)
        with self.assertRaises(Refusal):
            self.model.finalize_slot("task", 0, at=31, owner_decision=True, appeal_closed=True)
        self.assertEqual(self.model.w.get("alice", 0), 0)

    def test_failed_submission_pays_valid_reviewers_but_not_miner(self):
        self.offer("failed")
        self.review("failed", gate_value="fail", resolved=False)
        self.assertEqual(self.model.finalize_slot("failed", 0, at=31, owner_decision=True, appeal_closed=True), 0)
        self.assertEqual(self.model.w.get("alice", 0), 0)
        self.assertEqual(self.model.w["reviewer-1"], 5)
        self.assertEqual(self.model.w["reviewer-2"], 5)

    def test_unverified_review_quality_blocks_fees_and_miner_award(self):
        self.offer("quality")
        gates = {key: "pass" for key in REVIEW_GATES}
        self.model.review("quality", 0, "reviewer-1", gates, True, quality_status="pass")
        self.model.review("quality", 0, "reviewer-2", gates, True, quality_status="unknown")
        with self.assertRaises(Refusal):
            self.model.finalize_slot("quality", 0, at=31, owner_decision=True, appeal_closed=True)
        self.assertEqual(len(self.model.events), 0)

    def test_task_reservation_rejects_epoch_overspend(self):
        with self.assertRaises(Refusal):
            self.model.offer_task("too-large", "epoch-1", slots=100, base=100,
                                  bonus=50, reviewer_fee=5,
                                  commit_deadline=10, reveal_deadline=20,
                                  challenge_end=30)
        self.assertEqual(self.model.encumbered_w, 0)

    def test_transfer_replay_double_spend_and_redemption_gate(self):
        self.offer("paid")
        self.review("paid")
        self.model.finalize_slot("paid", 0, at=31, owner_decision=True, appeal_closed=True)
        self.model.transfer_w("alice", "bob", 40, event_id="xfer-1", nonce=0)
        for event_id, nonce, amount in (("xfer-1", 1, 1), ("xfer-2", 0, 1), ("xfer-3", 2, 1000)):
            with self.assertRaises(Refusal):
                self.model.transfer_w("alice", "bob", amount, event_id=event_id, nonce=nonce)
        with self.assertRaises(Refusal):
            self.model.redeem_w("bob", 10, service_ref="service:demo",
                                authorized=False, capacity_reserved=True,
                                event_id="redeem-1", nonce=0)
        self.model.redeem_w("bob", 10, service_ref="service:demo",
                            authorized=True, capacity_reserved=True,
                            event_id="redeem-1", nonce=0)
        self.assertEqual(self.model.w["burn"], 10)
        self.model.check_invariants()

    def test_unit_cap_duplicate_advance_and_nontransferability(self):
        self.model.reserve_milestone("m1", 2000)
        gates = {key: True for key in ADVANCE_GATES}
        self.assertEqual(self.model.allocate_advance("advance-1", "m1", {"alice": 6000, "bob": 4000}, gates,
                                                    agreement_signed=True, owner_decision=True,
                                                    appeal_closed=True), {"alice": 1200, "bob": 800})
        self.assertEqual(self.model.u["unit-reserve"], 8000)
        with self.assertRaises(Refusal):
            self.model.allocate_advance("advance-1", "m1", {"alice": 10000}, gates,
                                        agreement_signed=True, owner_decision=True,
                                        appeal_closed=True)
        with self.assertRaises(Refusal):
            self.model.transfer_u("alice", "bob", 100)
        with self.assertRaises(Refusal):
            self.model.reserve_milestone("too-large", 8001)

    def test_revenue_settlement_fixed_denominator_and_exclusions(self):
        self.model.reserve_milestone("m1", 2000)
        self.model.allocate_advance("advance-1", "m1", {"alice": 6000, "bob": 4000},
                                    {key: True for key in ADVANCE_GATES},
                                    agreement_signed=True, owner_decision=True, appeal_closed=True)
        with self.assertRaises(Refusal):
            self.model.deposit_revenue("q1", 100000, source_kind="token-sale", event_id="bad", nonce=0)
        self.model.deposit_revenue("q1", 100000, source_kind="product-receipts", event_id="income", nonce=0)
        args = dict(gross=100000, refunds=5000, taxes=2000, fees=1000,
                    direct_costs=1000, reserves=1000, exclusions=0,
                    active_units={"alice": 1200, "bob": 800},
                    audited=True, agreements_active=True, payment_finality_confirmed=True)
        result = self.model.settle_revenue("q1", **args)
        self.assertEqual(result["distributable"], 90000)
        self.assertEqual(result["pool"], 18000)
        self.assertEqual(result["payouts"], {"alice": 2160, "bob": 1440})
        self.assertEqual(result["unallocated"], 14400)
        with self.assertRaises(Refusal):
            self.model.settle_revenue("q1", **args)
        self.model.check_invariants()

    def test_no_finality_no_payment_and_zero_revenue(self):
        self.model.deposit_revenue("q1", 100, source_kind="product-receipts", event_id="income", nonce=0)
        with self.assertRaises(Refusal):
            self.model.settle_revenue("q1", gross=100, refunds=0, taxes=0, fees=0,
                                      direct_costs=0, reserves=0, exclusions=0,
                                      active_units={},
                                      audited=True, agreements_active=True,
                                      payment_finality_confirmed=False)
        self.assertEqual(self.model.c["treasury"], 100)
        result = self.model.settle_revenue("q1", gross=100, refunds=100, taxes=0,
                                           fees=0, direct_costs=0, reserves=0,
                                           exclusions=0, active_units={}, audited=True,
                                           agreements_active=True,
                                           payment_finality_confirmed=True)
        self.assertEqual(result["pool"], 0)

    def test_later_unit_issue_does_not_dilute_fixed_cap_fraction(self):
        gates = {key: True for key in ADVANCE_GATES}
        self.model.reserve_milestone("m1", 2000)
        self.model.allocate_advance("a1", "m1", {"alice": 6000, "bob": 4000},
                                    gates, agreement_signed=True,
                                    owner_decision=True, appeal_closed=True)
        self.model.deposit_revenue("q1", 10000, source_kind="product-receipts",
                                   event_id="income-1", nonce=0)
        q1 = self.model.settle_revenue("q1", gross=10000, refunds=0,
                                       taxes=0, fees=0, direct_costs=0,
                                       reserves=0, exclusions=0,
                                       active_units={"alice": 1200, "bob": 800},
                                       audited=True, agreements_active=True,
                                       payment_finality_confirmed=True)
        self.model.reserve_milestone("m2", 1000)
        self.model.allocate_advance("a2", "m2", {"carol": 10000},
                                    gates, agreement_signed=True,
                                    owner_decision=True, appeal_closed=True)
        self.model.deposit_revenue("q2", 10000, source_kind="product-receipts",
                                   event_id="income-2", nonce=3)
        q2 = self.model.settle_revenue("q2", gross=10000, refunds=0,
                                       taxes=0, fees=0, direct_costs=0,
                                       reserves=0, exclusions=0,
                                       active_units={"alice": 1200, "bob": 800,
                                                     "carol": 1000},
                                       audited=True, agreements_active=True,
                                       payment_finality_confirmed=True)
        self.assertEqual(q1["payouts"]["alice"], q2["payouts"]["alice"])
        self.assertEqual(q2["payouts"]["carol"], 200)
        with self.assertRaises(Refusal):
            self.model.settle_revenue("q3", gross=0, refunds=0, taxes=0,
                                      fees=0, direct_costs=0, reserves=0,
                                      exclusions=0, active_units={"alice": 1201},
                                      audited=True, agreements_active=True,
                                      payment_finality_confirmed=True)

    def test_event_tampering_detected(self):
        self.offer("paid")
        self.review("paid")
        self.model.finalize_slot("paid", 0, at=31, owner_decision=True, appeal_closed=True)
        self.model.events[0]["amount"] += 1
        with self.assertRaises(Refusal):
            self.model.check_invariants()

    def test_multi_payment_award_is_atomic_on_later_failure(self):
        self.offer("paid")
        self.review("paid")
        before = (dict(self.model.w), self.model.encumbered_w,
                  dict(self.model.epoch_spent), len(self.model.events))
        original = self.model._post
        calls = 0

        def fail_second_post(**kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise Refusal("synthetic ledger fault")
            return original(**kwargs)

        self.model._post = fail_second_post
        with self.assertRaises(Refusal):
            self.model.finalize_slot("paid", 0, at=31, owner_decision=True, appeal_closed=True)
        del self.model._post
        self.assertEqual((dict(self.model.w), self.model.encumbered_w,
                          dict(self.model.epoch_spent), len(self.model.events)), before)
        self.assertEqual(self.model.tasks["paid"].slots[0].state, "reviewing")

    def test_saved_synthetic_transactions_match_reference_run(self):
        root = Path(__file__).resolve().parent
        summary, transactions = run_scenario()
        self.assertEqual(json.loads((root / "fixtures/scenario.json").read_text()), summary)
        saved = [json.loads(path.read_text()) for path in sorted((root / "fixtures/transactions").glob("*.json"))]
        self.assertEqual(saved, transactions)


if __name__ == "__main__":
    unittest.main()
