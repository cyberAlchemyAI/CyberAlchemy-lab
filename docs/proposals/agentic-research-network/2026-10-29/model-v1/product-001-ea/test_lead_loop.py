"""Tests for the cohort-level lead loop, including unpaid supply."""

from dataclasses import replace
import unittest

from lead_loop import Cohort, evaluate, minimum_introductions


class LeadLoopTest(unittest.TestCase):
    def test_base_cohort_pays_engineers_and_funds_research(self):
        result = evaluate(Cohort())
        self.assertEqual(result["engineer_rewards_c"], 1800)
        self.assertEqual(result["locked_reserve_c"], 300)
        self.assertEqual((result["distributable_c"], result["u_pool_c"], result["f_pool_c"]), (1600, 320, 160))
        self.assertEqual(result["spendable_after_commitments_c"], 420)

    def test_cohort_threshold_includes_unsold_assessments(self):
        self.assertEqual(minimum_introductions(Cohort()), 25)
        low = evaluate(replace(Cohort(), paid_introductions=10))
        self.assertEqual(low["funding_gap_c"], 1500)
        self.assertEqual((low["u_pool_c"], low["f_pool_c"]), (0, 0))

    def test_process_api_can_fund_without_lead_sales(self):
        result = evaluate(replace(Cohort(), paid_introductions=0, process_revenue_c=3000))
        self.assertTrue(result["funds_all_commitments"])
        self.assertEqual(result["spendable_after_commitments_c"], 0)
        self.assertEqual(result["engineer_rewards_c"], 0)

    def test_unpaid_requests_never_count_as_receipts(self):
        result = evaluate(replace(Cohort(), paid_introductions=0))
        self.assertEqual(result["gross_realized_c"], 0)
        self.assertEqual(result["funding_gap_c"], 2700)

    def test_w_visibility_spends_token_and_cash_without_new_receipts(self):
        base = evaluate(Cohort())
        promoted = evaluate(replace(Cohort(), fulfilled_w_promotions=5))
        self.assertEqual((promoted["w_units_burned"], promoted["w_promotion_service_cost_c"]), (100, 10))
        self.assertEqual(promoted["gross_realized_c"], base["gross_realized_c"])
        self.assertEqual((promoted["u_pool_c"], promoted["f_pool_c"]), (base["u_pool_c"], base["f_pool_c"]))
        self.assertEqual(promoted["spendable_after_commitments_c"], 410)

    def test_w_visibility_requires_supply_and_capacity(self):
        with self.assertRaises(ValueError):
            evaluate(replace(Cohort(), fulfilled_w_promotions=6))
        with self.assertRaises(ValueError):
            evaluate(replace(Cohort(), fulfilled_w_promotions=5, available_w_units=99))

    def test_rejects_over_issue_and_invalid_shares(self):
        with self.assertRaises(ValueError):
            evaluate(replace(Cohort(), paid_introductions=101))
        with self.assertRaises(ValueError):
            evaluate(replace(Cohort(), beta_bps=9000))
        with self.assertRaises(ValueError):
            evaluate(replace(Cohort(), engineer_reward_c=-1))


if __name__ == "__main__":
    unittest.main()
