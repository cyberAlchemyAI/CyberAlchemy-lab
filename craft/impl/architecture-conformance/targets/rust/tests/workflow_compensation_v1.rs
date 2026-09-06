#[path = "../src/remaining_types/workflow_compensation_v1.rs"]
mod workflow_compensation_v1;
use workflow_compensation_v1::*;

const EMPTY: &[&str] = &[];
const MAPPINGS: &[RecoveryOperationMapping<'static>] = &[
    RecoveryOperationMapping { step_id: "reserve", operation_id: Some("release-reservation"), depends_on: EMPTY },
    RecoveryOperationMapping { step_id: "charge", operation_id: Some("refund-payment"), depends_on: EMPTY },
    RecoveryOperationMapping { step_id: "persist", operation_id: Some("restore-settlement"), depends_on: EMPTY },
];

fn input<'a>() -> PlanningInput<'a> {
    PlanningInput {
        workflow_id: "settlement-workflow",
        workflow_execution_id: "settlement-run-1",
        failure_occurrence_id: "publish-failure-1",
        failed_step_id: "publish",
        completed_step_ids: &["reserve", "charge", "persist"],
        orchestrated_operation_ids: &["release-reservation", "refund-payment", "restore-settlement"],
        mappings: MAPPINGS,
    }
}

#[test]
fn not_required_means_no_intent() {
    let mut value = input();
    value.completed_step_ids = EMPTY;
    value.mappings = &[];
    let result = plan_workflow_recovery(value).unwrap();
    assert_eq!(result.workflow_evaluation_result, "not-required");
    assert!(result.recovery_intent.is_none());
}

#[test]
fn required_intent_is_deterministic_and_reverse_ordered() {
    let left = plan_workflow_recovery(input()).unwrap();
    let right = plan_workflow_recovery(input()).unwrap();
    assert_eq!(left, right);
    let intent = left.recovery_intent.unwrap();
    assert_eq!(intent.semantic_status, "required");
    assert_eq!(intent.plan.iter().map(|entry| entry.operation_id.as_str()).collect::<Vec<_>>(), vec!["restore-settlement", "refund-payment", "release-reservation"]);
    assert_eq!(intent.completed_step_journal_digest, "4cb1e45d4a5cb20b9625486c7f5ad3cfbbf618d88783231ca7d34f999b58f27f");
    assert_eq!(intent.plan_digest, "745351ce2d5f9bcb7addce926290c57ac0adf5fe3c7c41a899a551abb3964059");
    assert_eq!(intent.intent_id, "98c6bdc1708fa2c8bbd0d2663c55aa6604e1fc57dccb0938b5dc507a10b1381e");
    assert_eq!(intent.plan.iter().map(|entry| entry.invocation_identity.as_str()).collect::<Vec<_>>(), vec![
        "bbaf6487f752a17045c7be19b0b97b5806df9b685d4a26e02472b9945ceac946",
        "4747d078775519d295004113cd3be9140a74ca77caa5f7108c8422b30626b23f",
        "7377dcb316f57ddde660cc468222cb29973d3095c9d2313e48278de648fc5bb4",
    ]);
}

#[test]
fn dependencies_relationships_and_repeated_occurrences_are_closed() {
    const REPEATED: &[RecoveryOperationMapping<'static>] = &[
        RecoveryOperationMapping { step_id: "reserve", operation_id: Some("restore-settlement"), depends_on: EMPTY },
        RecoveryOperationMapping { step_id: "charge", operation_id: Some("restore-settlement"), depends_on: EMPTY },
    ];
    let mut repeated = input();
    repeated.completed_step_ids = &["reserve", "charge"];
    repeated.orchestrated_operation_ids = &["restore-settlement"];
    repeated.mappings = REPEATED;
    let intent = plan_workflow_recovery(repeated).unwrap().recovery_intent.unwrap();
    assert_ne!(intent.plan[0].invocation_identity, intent.plan[1].invocation_identity);

    let mut unbound = input();
    unbound.orchestrated_operation_ids = &["refund-payment", "restore-settlement"];
    assert_eq!(plan_workflow_recovery(unbound).unwrap_err().code, "RECOVERY_OPERATION_NOT_ORCHESTRATED");
}

#[test]
fn exact_binding_preflight_precedes_invocation_and_terminal_state_is_not_invented() {
    let mut value = input();
    value.completed_step_ids = &["reserve", "charge"];
    let intent = plan_workflow_recovery(value).unwrap().recovery_intent.unwrap();
    let incomplete = [RecoveryOperationBinding { workflow_id: "settlement-workflow", operation_id: "refund-payment", failure_continuation: RecoveryFailureContinuation::Retry }];
    let mut calls = Vec::new();
    let result = execute_workflow_recovery(&intent, &incomplete, |operation, identity| {
        calls.push(format!("{operation}:{identity}"));
        Ok(())
    });
    assert_eq!(result.unwrap_err().code, "RECOVERY_BINDING_MISSING");
    assert!(calls.is_empty());

    let bindings = [
        RecoveryOperationBinding { workflow_id: "settlement-workflow", operation_id: "refund-payment", failure_continuation: RecoveryFailureContinuation::Escalate },
        RecoveryOperationBinding { workflow_id: "settlement-workflow", operation_id: "release-reservation", failure_continuation: RecoveryFailureContinuation::Retry },
    ];
    let report = execute_workflow_recovery(&intent, &bindings, |operation, identity| {
        calls.push(format!("{operation}:{identity}"));
        Ok(())
    }).unwrap();
    assert_eq!(report.outcome, "succeeded");
    assert_eq!(report.recovery_intent_semantic_status, "required");
    assert!(report.durable_terminal_disposition.is_none());
    assert_eq!(calls.len(), 2);
}

#[test]
fn failed_operation_preserves_its_continuation() {
    let mut value = input();
    value.completed_step_ids = &["reserve", "charge"];
    let intent = plan_workflow_recovery(value).unwrap().recovery_intent.unwrap();
    let bindings = [
        RecoveryOperationBinding { workflow_id: "settlement-workflow", operation_id: "refund-payment", failure_continuation: RecoveryFailureContinuation::Escalate },
        RecoveryOperationBinding { workflow_id: "settlement-workflow", operation_id: "release-reservation", failure_continuation: RecoveryFailureContinuation::Retry },
    ];
    let report = execute_workflow_recovery(&intent, &bindings, |operation, _| {
        if operation == "refund-payment" { Err("gateway-unavailable".to_owned()) } else { Ok(()) }
    }).unwrap();
    assert_eq!(report.outcome, "failed");
    assert_eq!(report.failure_continuation, Some(RecoveryFailureContinuation::Escalate));
    assert_eq!(report.reason.as_deref(), Some("gateway-unavailable"));
}
