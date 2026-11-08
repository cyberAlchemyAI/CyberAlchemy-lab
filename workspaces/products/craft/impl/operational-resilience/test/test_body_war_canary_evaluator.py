import unittest

from src.body_war_canary_contracts import TelemetryWindow, WorkloadSummary
from src.body_war_canary_evaluator import evaluate_canary


VALID_WORKLOAD = WorkloadSummary(450, 450, 450, 10, 25)


def window(**updates):
    values = dict(candidate_good=28, candidate_bad=7, stable_good=312, stable_bad=0, target_up=True, fault_active_all_samples=True, candidate_reference_present=True, samples_in_phase=True)
    values.update(updates)
    return TelemetryWindow(**values)


class EvaluatorTests(unittest.TestCase):
    def test_expected_positive_witness_is_rollback(self):
        result = evaluate_canary(window(), VALID_WORKLOAD)
        self.assertEqual((result.outcome, result.candidate_assessment, result.decision), ("passed", "unacceptable", "rollback"))
        self.assertEqual(result.authority_effect, "none")

    def test_threshold_boundaries_are_exact(self):
        rollback = evaluate_canary(window(candidate_good=16, candidate_bad=4, stable_good=180), VALID_WORKLOAD)
        self.assertEqual(rollback.decision, "rollback")
        acceptable = evaluate_canary(window(candidate_good=17, candidate_bad=3, stable_good=180), VALID_WORKLOAD)
        self.assertEqual(acceptable.decision, "continue")
        stable_harm = evaluate_canary(window(candidate_good=16, candidate_bad=4, stable_good=198, stable_bad=2), VALID_WORKLOAD)
        self.assertEqual((stable_harm.outcome, stable_harm.decision), ("passed", "rollback"))
        failed = evaluate_canary(window(candidate_good=16, candidate_bad=4, stable_good=197, stable_bad=3), VALID_WORKLOAD)
        self.assertEqual((failed.outcome, failed.decision), ("failed", "safety-rollback"))

    def test_incomplete_or_invalid_evidence_fails_closed(self):
        for value in [
            window(candidate_good=15, candidate_bad=4),
            window(stable_good=179),
            window(target_up=False),
            window(samples_in_phase=False),
            window(duplicate_series=True),
            window(stale_samples=True),
            window(nan_present=True),
            window(query_error=True),
        ]:
            with self.subTest(value=value):
                result = evaluate_canary(value, VALID_WORKLOAD)
                self.assertEqual((result.outcome, result.decision), ("inconclusive", "safety-rollback"))
        reset = evaluate_canary(window(counter_reset=True), VALID_WORKLOAD)
        self.assertEqual((reset.outcome, reset.decision), ("invalid", "safety-rollback"))


if __name__ == "__main__":
    unittest.main()
