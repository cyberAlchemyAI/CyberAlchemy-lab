"""Decision and accounting checks for the synthetic EA whole-model path."""

import unittest

from integrated_scenario import case, report


class IntegratedScenarioTests(unittest.TestCase):
    def test_controlled_repair_earns_separate_work_and_research_rewards(self):
        result = report()["cases"]["controlled_improvement_sales"]
        self.assertEqual(result["product_decision"], "adopt-scorer-variant")
        self.assertEqual([row["w_award_units"] for row in result["research_chain"]],
                         [100, 100, 0])
        self.assertEqual([row["u_award_units"] for row in result["research_chain"]],
                         [0, 100, 0])
        self.assertEqual(result["completed_periods"], 5)
        self.assertEqual(result["u_paid_c"], 198)
        self.assertEqual(result["f_paid_c"], 300)
        self.assertEqual(result["last_valid_state"]["cash_c"], 1802)
        self.assertEqual(result["last_valid_state"]["w_burned"], 200)
        self.assertEqual(result["last_valid_state"]["service_reserve_c"], 0)

    def test_decision_closing_negative_can_earn_u_without_adopting_variant(self):
        result = report()["cases"]["decision_closing_negative_sales"]
        self.assertEqual(result["research_chain"][1]["u_award_units"], 100)
        self.assertEqual(result["product_decision"], "retain-baseline-scorer")
        self.assertEqual(result["research_chain"][1]["decision_scope"],
                         "local authored-fixture uncertainty only")

    def test_valid_but_inconclusive_execution_earns_w_without_u(self):
        result = report()["cases"]["valid_but_inconclusive_sales"]
        self.assertEqual(result["research_chain"][1]["w_award_units"], 100)
        self.assertEqual(result["research_chain"][1]["u_award_units"], 0)
        self.assertEqual(result["last_valid_state"]["u_remaining"], 300)
        self.assertEqual(result["u_paid_c"], 0)
        self.assertEqual(result["f_paid_c"], 300)

    def test_sponsor_units_pay_zero_without_product_receipts(self):
        result = report()["cases"]["improvement_no_sales"]
        self.assertEqual(result["first_refused_period"], 4)
        self.assertEqual(result["completed_periods"], 3)
        self.assertEqual(result["u_paid_c"], 0)
        self.assertEqual(result["f_paid_c"], 0)
        self.assertEqual(result["last_valid_state"]["f_remaining"], 0)

    def test_lost_product_sales_right_refuses_forecast_receipt(self):
        result = report()["cases"]["rights_lost_blocks_sales"]
        self.assertEqual(result["completed_periods"], 2)
        self.assertEqual(result["first_refused_period"], 3)
        self.assertEqual(result["reason"], "product-revenue-rights-lost")
        self.assertEqual(result["last_valid_state"]["cash_c"], 1200)
        self.assertEqual(result["f_paid_c"], 0)

    def test_unknown_outcome_or_negative_sale_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown synthetic outcome"):
            case(outcome="self-declared-winner")
        with self.assertRaisesRegex(ValueError, "invalid synthetic Product receipt"):
            case(outcome="inconclusive", sale_c=-1)


if __name__ == "__main__":
    unittest.main()
