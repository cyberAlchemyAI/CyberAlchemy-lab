import unittest

from src.body_war_canary_observer import RestorationFacts, observe_restoration


def restored(**updates):
    values = dict(gateway_candidate_target_present=False, gateway_candidate_weight=0, candidate_reference_gauge=0, candidate_containers=0, candidate_endpoints=0, gateway_probe_statuses=(200,) * 20, direct_stable_probe_statuses=(200,) * 5, stable_image_unchanged=True, elapsed_ms=19999)
    values.update(updates)
    return RestorationFacts(**values)


class ObserverTests(unittest.TestCase):
    def test_five_reference_classes_and_probes_pass_independently(self):
        result = observe_restoration(restored())
        self.assertEqual((result.outcome, result.candidate_reference_absent, result.probes_passed, result.deadline_met), ("passed", True, True, True))

    def test_each_reference_probe_and_deadline_failure_is_visible(self):
        mutations = [
            dict(gateway_candidate_target_present=True), dict(gateway_candidate_weight=10),
            dict(candidate_reference_gauge=1), dict(candidate_containers=1), dict(candidate_endpoints=1),
            dict(gateway_probe_statuses=(200,) * 19), dict(direct_stable_probe_statuses=(500,) * 5),
            dict(stable_image_unchanged=False), dict(elapsed_ms=20001),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.assertEqual(observe_restoration(restored(**mutation)).outcome, "failed")


if __name__ == "__main__": unittest.main()
