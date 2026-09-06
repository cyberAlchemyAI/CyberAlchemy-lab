import unittest

from src.body_war_canary_controller import retry_allowed, safety_route, transition
from src.body_war_canary_rollback import RollbackAction, execute_rollback, rollback_plan, validate_rollback_order


class RollbackTests(unittest.TestCase):
    def test_route_reference_is_removed_before_container(self):
        actions = rollback_plan("orodi-bw-run-1", 4)
        validate_rollback_order(actions)
        self.assertEqual([a.action_id for a in actions], ["remove-gateway-candidate-reference", "reconcile-gateway-state", "remove-candidate-container"])
        calls = []
        result = execute_rollback(actions, lambda argv: calls.append(argv) or 0)
        self.assertEqual(len(result), 3)
        self.assertEqual(calls[0][0], "gateway-control")
        self.assertEqual(calls[-1][0:2], ("docker", "compose"))

    def test_failure_stops_order_and_full_trial_never_retries(self):
        actions = rollback_plan("orodi-bw-run-1", 4)
        self.assertEqual(len(execute_rollback(actions, lambda argv: 1)), 1)
        self.assertFalse(retry_allowed("full-trial", True, 0))
        self.assertFalse(retry_allowed("fault-activation", True, 0))
        self.assertEqual(transition("not-started", "preflight-valid"), "preflight-valid")
        self.assertEqual(safety_route("candidate-exposed")[0], "rollback-triggered")
        with self.assertRaisesRegex(ValueError, "NON_SEQUENTIAL"):
            transition("not-started", "candidate-exposed")

    def test_wrong_action_order_rejects(self):
        with self.assertRaisesRegex(ValueError, "ORDER"):
            validate_rollback_order((RollbackAction("remove-candidate-container", ("docker",), True),))


if __name__ == "__main__": unittest.main()
