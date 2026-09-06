use domainspec_architecture_conformance_rust::w4::{
    run_settlement_workflow, transition_settlement_lifecycle, SettlementState, SettlementTrigger, WorkflowStep,
};
use std::cell::RefCell;

#[test]
fn state_machine_returns_effect_intents_and_rejects_terminal_transition() {
    let accepted = transition_settlement_lifecycle(SettlementState::Pending, SettlementTrigger::Confirm);
    assert_eq!(accepted.next_state, Some(SettlementState::Settled));
    assert_eq!(accepted.effect_intents, vec!["persist-settlement", "append-settlement-created"]);
    let rejected = transition_settlement_lifecycle(SettlementState::Pending, SettlementTrigger::Reject);
    assert_eq!(rejected.next_state, Some(SettlementState::Failed));
    assert_eq!(rejected.effect_intents, vec!["record-rejection"]);
    assert!(!transition_settlement_lifecycle(SettlementState::Settled, SettlementTrigger::Confirm).accepted);
}

#[test]
fn workflow_executes_the_declared_order() {
    let calls = RefCell::new(Vec::new());
    let mut validate = || { calls.borrow_mut().push("validate"); Ok(()) };
    let mut decide = || { calls.borrow_mut().push("decide"); Ok(()) };
    let mut persist = || { calls.borrow_mut().push("persist"); Ok(()) };
    let mut publish = || { calls.borrow_mut().push("publish"); Ok(()) };
    let mut rollback = || { calls.borrow_mut().push("undo-persist"); Ok(()) };
    let result = run_settlement_workflow(&mut [
        WorkflowStep {step_id: "validate", run: &mut validate, compensation_id: None, compensate: None},
        WorkflowStep {step_id: "decide", run: &mut decide, compensation_id: None, compensate: None},
        WorkflowStep {step_id: "persist", run: &mut persist, compensation_id: Some("rollback-settlement"), compensate: Some(&mut rollback)},
        WorkflowStep {step_id: "publish", run: &mut publish, compensation_id: None, compensate: None},
    ]).expect("workflow should run");
    assert_eq!(result.outcome, "settlement-completed");
    assert_eq!(result.trace, vec!["validate", "decide", "persist", "publish"]);
    assert_eq!(*calls.borrow(), vec!["validate", "decide", "persist", "publish"]);
}

#[test]
fn workflow_rejects_a_missing_step() {
    let mut okay = || Ok(());
    let result = run_settlement_workflow(&mut [WorkflowStep {step_id: "validate", run: &mut okay, compensation_id: None, compensate: None}]);
    assert_eq!(result, Err("ARCH_WORKFLOW_STEP_MISSING"));
}

#[test]
fn workflow_compensates_exact_completed_steps_in_reverse_order() {
    let calls = RefCell::new(Vec::new());
    let mut validate = || { calls.borrow_mut().push("validate"); Ok(()) };
    let mut decide = || { calls.borrow_mut().push("decide"); Ok(()) };
    let mut persist = || { calls.borrow_mut().push("persist"); Ok(()) };
    let mut publish = || Err("publication failed");
    let mut rollback = || { calls.borrow_mut().push("undo-persist"); Ok(()) };
    let result = run_settlement_workflow(&mut [
        WorkflowStep {step_id: "validate", run: &mut validate, compensation_id: None, compensate: None},
        WorkflowStep {step_id: "decide", run: &mut decide, compensation_id: None, compensate: None},
        WorkflowStep {step_id: "persist", run: &mut persist, compensation_id: Some("rollback-settlement"), compensate: Some(&mut rollback)},
        WorkflowStep {step_id: "publish", run: &mut publish, compensation_id: None, compensate: None},
    ]).expect("failure is a declared workflow outcome");
    assert_eq!(result.failed_step_id, Some("publish"));
    assert_eq!(result.compensations, vec!["rollback-settlement"]);
    assert_eq!(*calls.borrow(), vec!["validate", "decide", "persist", "undo-persist"]);
}

#[test]
fn workflow_rejects_duplicate_steps_before_execution() {
    let calls = RefCell::new(Vec::new());
    let mut validate = || { calls.borrow_mut().push("validate"); Ok(()) };
    let mut decide = || Ok(());
    let mut persist_a = || Ok(());
    let mut persist_b = || Ok(());
    let mut publish = || Ok(());
    let mut rollback_a = || Ok(());
    let mut rollback_b = || Ok(());
    let result = run_settlement_workflow(&mut [
        WorkflowStep {step_id: "validate", run: &mut validate, compensation_id: None, compensate: None},
        WorkflowStep {step_id: "decide", run: &mut decide, compensation_id: None, compensate: None},
        WorkflowStep {step_id: "persist", run: &mut persist_a, compensation_id: Some("rollback-settlement"), compensate: Some(&mut rollback_a)},
        WorkflowStep {step_id: "persist", run: &mut persist_b, compensation_id: Some("rollback-settlement"), compensate: Some(&mut rollback_b)},
        WorkflowStep {step_id: "publish", run: &mut publish, compensation_id: None, compensate: None},
    ]);
    assert_eq!(result, Err("ARCH_WORKFLOW_STEP_SET_INVALID"));
    assert!(calls.borrow().is_empty());
}
