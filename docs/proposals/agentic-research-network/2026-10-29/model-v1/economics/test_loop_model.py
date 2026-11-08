"""Behavioral checks for the two synthetic research-funding loops."""

import unittest
from dataclasses import replace

from loop_model import LoopRefusal, Period, max_safe_constant_research, run, step
from loop_scenarios import cases, initial, policy, recurring_period, report


class LoopTests(unittest.TestCase):
    def test_product_receipts_can_replenish_cash_only_under_assumed_margin(self):
        result = report()["cases"]["product_recurring"]
        self.assertEqual(result["completed_periods"], 5)
        self.assertIsNone(result["reason"])
        self.assertEqual(result["end_cash_c"], 1500)
        self.assertEqual(result["end_w_inventory"], 300)
        self.assertEqual(result["end_u_remaining"], 0)

    def test_product_downturn_and_no_sales_stop_new_periods(self):
        result = report()["cases"]
        self.assertEqual((result["product_downturn"]["completed_periods"],
                          result["product_downturn"]["reason"]), (2, "cash-floor"))
        self.assertEqual((result["product_no_sales"]["completed_periods"],
                          result["product_no_sales"]["reason"]), (0, "cash-floor"))
        self.assertEqual(report()["stress_budget_c_per_period"]
                         ["product_downturn_five_periods"], 280)

    def test_recurring_unrestricted_sponsorship_is_a_separate_regime(self):
        result = report()["cases"]["sponsor_recurring"]
        self.assertEqual(result["completed_periods"], 5)
        self.assertEqual(result["end_cash_c"], 1000)
        sponsor_policy, sponsor_state, periods = cases()["sponsor_recurring"]
        self.assertEqual(step(sponsor_policy, sponsor_state, periods[0]).u_payout_c, 0)

    def test_sponsor_withdrawal_stops_and_reduces_safe_budget(self):
        result = report()["cases"]["sponsor_withdrawal"]
        self.assertEqual(result["first_refused_period"], 3)
        self.assertEqual(result["reason"], "cash-floor")
        self.assertEqual(report()["stress_budget_c_per_period"]
                         ["sponsor_withdrawal_five_periods"], 80)

    def test_research_only_sponsor_cannot_cover_overhead_or_service(self):
        result = report()["cases"]["sponsor_research_only"]
        self.assertEqual(result["first_refused_period"], 1)
        self.assertEqual(result["reason"], "cash-floor")
        p = recurring_period(product_net_c=0, distributable_c=0,
                             sponsor_research_only_c=700)
        accepted = step(policy(), initial(u_remaining=300), p)
        self.assertEqual(accepted.research_from_sponsor_c, 400)
        self.assertEqual(accepted.state.research_only_c, 300)
        self.assertEqual(accepted.state.headroom_c, 700)

    def test_finite_burn_and_u_cap_stop_even_when_cash_is_healthy(self):
        results = report()["cases"]
        self.assertEqual((results["product_w_burn"]["first_refused_period"],
                          results["product_w_burn"]["reason"]),
                         (4, "w-reward-inventory-exhausted"))
        self.assertEqual((results["product_u_exhaustion"]["first_refused_period"],
                          results["product_u_exhaustion"]["reason"]),
                         (4, "u-allocation-cap-exhausted"))
        self.assertGreater(results["product_w_burn"]["end_headroom_c"], 500)
        self.assertGreater(results["product_u_exhaustion"]["end_headroom_c"], 500)

    def test_w_recycling_does_not_create_treasury_cash(self):
        period = Period(service_reserve_add_c=100, service_cost_c=100,
                        w_award=100, w_redeem=100)
        accepted = step(policy(), initial(u_remaining=300), period)
        self.assertEqual(accepted.state.cash_c, 900)
        self.assertEqual(accepted.state.w_inventory, 300)
        self.assertEqual(accepted.state.w_circulating, 0)
        self.assertEqual(accepted.state.w_burned, 0)

    def test_invalid_receipt_or_missing_reserve_is_refused_atomically(self):
        state = initial(u_remaining=300)
        with self.assertRaisesRegex(LoopRefusal, "distributable-exceeds-product-net"):
            step(policy(), state, Period(product_net_c=0, distributable_c=100))
        with self.assertRaisesRegex(LoopRefusal, "service-reserve-insufficient"):
            step(policy(), state, Period(service_cost_c=100, w_award=100,
                                         w_redeem=100))
        self.assertEqual(state.cash_c, 1000)
        self.assertEqual(state.w_inventory, 300)

    def test_committed_liability_and_cost_shock_reduce_headroom(self):
        state = replace(initial(), committed_unpaid_c=400)
        self.assertEqual(state.headroom_c, 600)
        self.assertEqual(step(policy(), state, recurring_period()).state.headroom_c,
                         700)
        with self.assertRaisesRegex(LoopRefusal, "cash-floor"):
            step(policy(), state, recurring_period(other_loss_c=250))

    def test_budget_controller_only_guarantees_named_finite_path(self):
        loop_policy, state, periods = cases()["product_downturn"]
        budget = max_safe_constant_research(loop_policy, state, periods, 1000)
        self.assertEqual(budget, 280)
        self.assertIsNone(run(loop_policy, state,
                              [replace(p, research_c=budget) for p in periods])
                          ["first_refused_period"])
        self.assertEqual(run(loop_policy, state,
                             [replace(p, research_c=budget + 1) for p in periods])
                         ["reason"], "cash-floor")

    def test_vested_sponsor_keeps_product_share_after_funding_stops(self):
        loop_policy, state, periods = cases()["sponsor_vested_exit_product"]
        result = run(loop_policy, state, periods)
        self.assertIsNone(result["reason"])
        self.assertEqual(result["last_valid_state"]["f_remaining"], 0)
        self.assertEqual([row["f_payout_c"] for row in result["trace"]],
                         [0, 0, 100, 100, 100])
        self.assertEqual(result["last_valid_state"]["cash_c"], 1000)
        self.assertEqual(report()["cases"]["sponsor_vested_exit_product"]
                         ["f_payout_total_c"], 300)

    def test_vested_sponsor_share_survives_exit_but_zero_revenue_pays_zero(self):
        case = report()["cases"]["sponsor_vested_exit_no_product"]
        self.assertEqual(case["f_awarded_units"], 1400)
        self.assertEqual(case["end_f_remaining"], 0)
        self.assertEqual(case["f_payout_total_c"], 0)
        self.assertEqual(case["first_refused_period"], 3)

    def test_pledge_cannot_mint_f_and_unspent_restricted_cash_can_refund(self):
        blocked = report()["cases"]["sponsor_pledge_cannot_vest"]
        self.assertEqual(blocked["reason"], "f-award-exceeds-vested-funding")
        self.assertEqual(blocked["f_awarded_units"], 0)
        refunded = report()["cases"]["sponsor_refund_unspent"]
        self.assertEqual(refunded["sponsor_refunded_c"], 300)
        self.assertEqual(refunded["f_awarded_units"], 400)
        self.assertEqual(refunded["end_headroom_c"], 700)

    def test_sponsor_and_research_shares_cannot_exceed_all_product_cash(self):
        invalid = replace(policy(sponsor_participation=True),
                          u_share_bps=9500, f_share_bps=1000)
        with self.assertRaisesRegex(LoopRefusal, "invalid-policy:combined-share"):
            invalid.validate()

    def test_sponsor_share_changes_product_break_even(self):
        without_f = step(policy(), initial(), recurring_period()).state.cash_c
        with_f = step(policy(sponsor_participation=True),
                      initial(f_remaining=0), recurring_period()).state.cash_c
        self.assertEqual(without_f, 1100)
        self.assertEqual(with_f, 1000)

    def test_free_sponsor_access_needs_cash_service_reserve(self):
        case = report()["cases"]["sponsor_free_access_cost"]
        self.assertEqual(case["first_refused_period"], 6)
        self.assertEqual(case["reason"], "cash-floor")
        self.assertEqual(case["f_payout_total_c"], 300)
        self.assertEqual(case["end_cash_c"], 550)


if __name__ == "__main__":
    unittest.main()
