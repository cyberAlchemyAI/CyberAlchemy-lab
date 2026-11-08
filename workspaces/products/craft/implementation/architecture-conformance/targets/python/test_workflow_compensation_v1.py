import importlib.util
import pathlib
import sys
import unittest

MODULE_PATH = pathlib.Path(__file__).with_name("remaining_types") / "workflow_compensation_v1.py"
SPEC = importlib.util.spec_from_file_location("workflow_compensation_v1", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def decision(**overrides):
    values = {
        "workflow_id": "settlement-workflow",
        "workflow_execution_id": "settlement-run-1",
        "failure_occurrence_id": "publish-failure-1",
        "failed_step_id": "publish",
        "completed_step_ids": ("reserve", "charge", "persist"),
        "orchestrated_operation_ids": ("release-reservation", "refund-payment", "restore-settlement"),
        "mappings": (
            MODULE.RecoveryOperationMapping("reserve", "release-reservation"),
            MODULE.RecoveryOperationMapping("charge", "refund-payment"),
            MODULE.RecoveryOperationMapping("persist", "restore-settlement"),
        ),
    }
    values.update(overrides)
    return MODULE.plan_workflow_recovery(**values)


class WorkflowRecoveryV1Test(unittest.TestCase):
    def test_not_required_means_no_intent(self) -> None:
        result = decision(completed_step_ids=(), mappings=())
        self.assertEqual(result.workflow_evaluation_result, "not-required")
        self.assertIsNone(result.recovery_intent)

    def test_required_intent_is_deterministic_and_reverse_ordered(self) -> None:
        result = decision()
        assert result.recovery_intent
        self.assertEqual(result.workflow_evaluation_result, "recovery-required")
        self.assertEqual(result.recovery_intent.semantic_status, "required")
        self.assertEqual([entry.operation_id for entry in result.recovery_intent.plan], ["restore-settlement", "refund-payment", "release-reservation"])
        self.assertEqual(result.recovery_intent.completed_step_journal_digest, "4cb1e45d4a5cb20b9625486c7f5ad3cfbbf618d88783231ca7d34f999b58f27f")
        self.assertEqual(result.recovery_intent.plan_digest, "745351ce2d5f9bcb7addce926290c57ac0adf5fe3c7c41a899a551abb3964059")
        self.assertEqual(result.recovery_intent.intent_id, "98c6bdc1708fa2c8bbd0d2663c55aa6604e1fc57dccb0938b5dc507a10b1381e")
        self.assertEqual([entry.invocation_identity for entry in result.recovery_intent.plan], [
            "bbaf6487f752a17045c7be19b0b97b5806df9b685d4a26e02472b9945ceac946",
            "4747d078775519d295004113cd3be9140a74ca77caa5f7108c8422b30626b23f",
            "7377dcb316f57ddde660cc468222cb29973d3095c9d2313e48278de648fc5bb4",
        ])
        self.assertEqual(result, decision())

    def test_explicit_dependencies_precede_reverse_tie_breaker(self) -> None:
        result = decision(mappings=(
            MODULE.RecoveryOperationMapping("reserve", "release-reservation"),
            MODULE.RecoveryOperationMapping("charge", "refund-payment"),
            MODULE.RecoveryOperationMapping("persist", "restore-settlement", ("release-reservation",)),
        ))
        assert result.recovery_intent
        self.assertEqual([entry.operation_id for entry in result.recovery_intent.plan], ["refund-payment", "release-reservation", "restore-settlement"])

    def test_repeated_operation_has_distinct_invocation_identity(self) -> None:
        result = decision(
            completed_step_ids=("reserve", "charge"),
            orchestrated_operation_ids=("restore-settlement",),
            mappings=(
                MODULE.RecoveryOperationMapping("reserve", "restore-settlement"),
                MODULE.RecoveryOperationMapping("charge", "restore-settlement"),
            ),
        )
        assert result.recovery_intent
        identities = [entry.invocation_identity for entry in result.recovery_intent.plan]
        self.assertEqual(len(set(identities)), 2)

    def test_rejects_missing_orchestrates_relation(self) -> None:
        with self.assertRaisesRegex(MODULE.WorkflowRecoveryError, "RECOVERY_OPERATION_NOT_ORCHESTRATED"):
            decision(orchestrated_operation_ids=("refund-payment", "restore-settlement"))

    def test_preflights_all_bindings_before_invocation(self) -> None:
        intent = decision(completed_step_ids=("reserve", "charge")).recovery_intent
        assert intent
        calls: list[str] = []
        with self.assertRaisesRegex(MODULE.WorkflowRecoveryError, "RECOVERY_BINDING_MISSING"):
            MODULE.execute_workflow_recovery(intent, (
                MODULE.RecoveryOperationBinding("settlement-workflow", "refund-payment", "retry", lambda identity: (calls.append(identity) is None, None)),
            ))
        self.assertEqual(calls, [])

    def test_executes_exact_bindings_without_terminal_overclaim(self) -> None:
        intent = decision(completed_step_ids=("reserve", "charge")).recovery_intent
        assert intent
        calls: list[str] = []
        bindings = tuple(MODULE.RecoveryOperationBinding(
            "settlement-workflow",
            operation_id,
            "escalate",
            lambda identity, operation_id=operation_id: (calls.append(f"{operation_id}:{identity}") is None, None),
        ) for operation_id in {entry.operation_id for entry in intent.plan})
        report = MODULE.execute_workflow_recovery(intent, bindings)
        self.assertEqual(report.outcome, "succeeded")
        self.assertEqual(report.recovery_intent_semantic_status, "required")
        self.assertIsNone(report.durable_terminal_disposition)
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
