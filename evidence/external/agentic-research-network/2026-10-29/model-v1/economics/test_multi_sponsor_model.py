"""Check sponsor identity, exit and Product solvency behavior in the candidate model."""

import unittest
from dataclasses import replace

from multi_sponsor_model import Period, Refusal, run, step
from multi_sponsor_scenarios import cases, funding_periods, report, setup


class MultiSponsorTests(unittest.TestCase):
    def test_staggered_sponsors_keep_distinct_vested_shares_after_exit(self):
        case = report()["cases"]["staggered_exit_with_access"]
        self.assertEqual(case["completed_periods"], 5)
        self.assertEqual(case["end_f_units"], {"sponsor-A": 900,
                                               "sponsor-B": 500})
        self.assertEqual(case["f_paid_c"], {"sponsor-A": 192,
                                             "sponsor-B": 105})
        self.assertEqual(case["u_paid_c"], 600)
        self.assertEqual(case["f_rounding_dust_c"], 3)
        self.assertEqual(case["end_headroom_c"], 853)

    def test_access_has_cash_cost_and_outstanding_reserve(self):
        cases_ = report()["cases"]
        with_access = cases_["staggered_exit_with_access"]
        without = cases_["staggered_exit_no_access"]
        self.assertEqual(with_access["access_cost_c"], 90)
        self.assertEqual(with_access["end_access_remaining"]["sponsor-B"], 2)
        self.assertEqual(without["access_cost_c"], 0)
        self.assertEqual(without["end_headroom_c"] - with_access["end_headroom_c"], 150)

    def test_no_sales_and_downturn_stop_new_commitments(self):
        cases_ = report()["cases"]
        self.assertEqual((cases_["exit_no_product"]["first_refused_period"],
                          cases_["exit_no_product"]["reason"]), (3, "cash-floor"))
        self.assertEqual((cases_["product_downturn"]["first_refused_period"],
                          cases_["product_downturn"]["reason"]), (4, "cash-floor"))

    def test_ip_transfer_without_retained_sales_right_excludes_revenue(self):
        case = report()["cases"]["sales_right_lost"]
        self.assertEqual((case["first_refused_period"], case["reason"]),
                         (3, "product-revenue-rights-lost"))
        self.assertEqual(case["f_paid_c"], {"sponsor-A": 0, "sponsor-B": 0})

    def test_refund_and_pledge_do_not_mint_or_reuse_funding(self):
        cases_ = report()["cases"]
        self.assertEqual(cases_["refund_before_vesting"]["end_f_units"],
                         {"sponsor-A": 500, "sponsor-B": 0})
        self.assertEqual(cases_["unpaid_pledge"]["reason"],
                         "vest-or-refund-exceeds-cleared")
        self.assertEqual(cases_["unpaid_pledge"]["end_f_units"],
                         {"sponsor-A": 0, "sponsor-B": 0})

    def test_refundable_deposit_is_reserved_until_it_vests(self):
        policy, terms, state = setup()
        pending, _ = step(policy, terms, state,
                          Period(deposits_c={"sponsor-A": 900},
                                 operating_c=0, research_c=0, w_service_c=0))
        self.assertEqual(pending.cash_c, 1900)
        self.assertEqual(pending.accounts["sponsor-A"].pending_refundable_c, 900)
        with self.assertRaisesRegex(Refusal, "cash-floor"):
            step(policy, terms, pending, Period())
        self.assertEqual(pending.accounts["sponsor-A"].f_units, 0)

    def test_reserved_units_and_access_cannot_be_overpromised(self):
        policy, terms, state = setup()
        with self.assertRaisesRegex(Refusal, "f-reservation-exceeds-cap"):
            step(policy, (replace(terms[0], f_limit=1000), terms[1]),
                 state, funding_periods()[0])
        self.assertEqual(report()["cases"]["access_abuse"]["reason"],
                         "access-quota-exceeded")

    def test_ip_rights_clearance_required_before_vesting(self):
        policy, terms, state = setup(lost_sales_right=True)
        uncleared = (terms[0], replace(terms[1], rights_cleared=False))
        first = step(policy, uncleared, state, funding_periods()[0])[0]
        with self.assertRaisesRegex(Refusal, "ip-rights-not-cleared"):
            step(policy, uncleared, first, funding_periods()[1])


if __name__ == "__main__":
    unittest.main()
