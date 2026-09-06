#[path = "../src/remaining_types/operation_v1.rs"]
mod operation_v1;

use std::cell::RefCell;
use std::rc::Rc;

use operation_v1::{
    classify_operation_s1_residue, BoundOperation, CompleteSettlementInput,
    CompleteSettlementOperationOutcome, CompleteSettlementOperationPorts,
    CompleteSettlementRead, CompleteSettlementTransaction,
    CompleteSettlementWrite, OperationS1NativeResidue, PayoutAccountRecord,
    PayoutCreatedEvent,
    SettlementRecord, COMPLETE_SETTLEMENT_OPERATION,
};

#[derive(Default)]
struct TraceState {
    calls: Vec<String>,
    fail_write: bool,
}

struct FixtureTransaction {
    state: Rc<RefCell<TraceState>>,
}

impl CompleteSettlementTransaction for FixtureTransaction {
    fn write(
        &mut self,
        target_id: &'static str,
        _value: CompleteSettlementWrite,
    ) -> Result<(), &'static str> {
        let mut state = self.state.borrow_mut();
        state.calls.push(format!("write:{target_id}"));
        if state.fail_write {
            Err("write-failed")
        } else {
            Ok(())
        }
    }

    fn commit(&mut self, _mode: &'static str) -> Result<(), &'static str> {
        self.state.borrow_mut().calls.push("atomic:commit".to_owned());
        Ok(())
    }

    fn rollback(&mut self) {
        self.state.borrow_mut().calls.push("atomic:rollback".to_owned());
    }
}

struct FixturePorts {
    state: Rc<RefCell<TraceState>>,
    allowed: bool,
}

impl CompleteSettlementOperationPorts for FixturePorts {
    fn guard(
        &mut self,
        guard_id: &'static str,
        _input: &CompleteSettlementInput<'_>,
    ) -> bool {
        self.state.borrow_mut().calls.push(format!("guard:{guard_id}"));
        self.allowed
    }

    fn read(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> Result<CompleteSettlementRead, &'static str> {
        self.state.borrow_mut().calls.push(format!("read:{target_id}"));
        if target_id == "settlement.read.settlement-by-id" {
            Ok(CompleteSettlementRead::Settlement(SettlementRecord {
                settlement_id: settlement_id.to_owned(),
            }))
        } else {
            Ok(CompleteSettlementRead::PayoutAccount(PayoutAccountRecord {
                account_id: "account-001".to_owned(),
            }))
        }
    }

    fn begin_atomic(&mut self) -> Box<dyn CompleteSettlementTransaction> {
        self.state.borrow_mut().calls.push("atomic:begin".to_owned());
        Box::new(FixtureTransaction {state: Rc::clone(&self.state)})
    }

    fn external_effect(
        &mut self,
        target_id: &'static str,
        event: PayoutCreatedEvent,
    ) -> Result<(), &'static str> {
        let mut state = self.state.borrow_mut();
        state.calls.push(format!("effect:{target_id}"));
        state.calls.push(format!("event:{}", event.event_type));
        Ok(())
    }

    fn close(
        &mut self,
        _closure: &'static str,
        failure_code: Option<&'static str>,
    ) {
        let mut state = self.state.borrow_mut();
        if failure_code.is_some() {
            state.calls.push("outcome:failure".to_owned());
        }
        state.calls.push("continuation:close".to_owned());
    }
}

fn fixture(allowed: bool, fail_write: bool) -> (FixturePorts, Rc<RefCell<TraceState>>) {
    let state = Rc::new(RefCell::new(TraceState {
        calls: Vec::new(),
        fail_write,
    }));
    (FixturePorts {state: Rc::clone(&state), allowed}, state)
}

fn normal_s1_residue() -> OperationS1NativeResidue<'static> {
    OperationS1NativeResidue {
        scenario: "normal",
        transaction_id: Some("transaction-001"),
        occurrence_id: Some("occurrence-001"),
        state_write_attempted: true,
        outbox_append_attempted: true,
        outbox_checkpoint_observed: true,
        transaction_aborted: false,
        state_durable: true,
        outbox_occurrence_durable: true,
        commit_observed: true,
        rollback_requested: false,
        history_erased: false,
        forward_recovery_required: false,
        closed_rejection: false,
    }
}

#[test]
fn operation_v1_runs_the_exact_committed_trace_and_returns_success() {
    let operation: BoundOperation = COMPLETE_SETTLEMENT_OPERATION;
    let (mut ports, state) = fixture(true, false);
    let result = operation(
        &CompleteSettlementInput {
            settlement_id: "settlement-001",
            expected_state_version: 7,
        },
        &mut ports,
    );
    state.borrow_mut().calls.push("outcome:success".to_owned());
    assert_eq!(state.borrow().calls, vec![
        "guard:rule.can-settle-payout",
        "read:settlement.read.settlement-by-id",
        "read:settlement.read.payout-account",
        "atomic:begin",
        "write:settlement.write.payout-record",
        "write:settlement.write.settlement-status",
        "atomic:commit",
        "effect:event-store.append.PayoutCreated",
        "event:PayoutCreated",
        "continuation:close",
        "outcome:success",
    ]);
    assert_eq!(result, CompleteSettlementOperationOutcome::Success {
        value: operation_v1::CompleteSettlementSuccess {
            settlement_id: "settlement-001".to_owned(),
            payout_id: "account-001:settlement-001".to_owned(),
            status: "committed".to_owned(),
        },
        failure_code: None,
        exactly_once_distributed_delivery_claimed: false,
    });
}

#[test]
fn operation_v1_rejects_before_transition_and_returns_no_success_value() {
    let (mut ports, state) = fixture(false, false);
    let result = COMPLETE_SETTLEMENT_OPERATION(
        &CompleteSettlementInput {
            settlement_id: "settlement-001",
            expected_state_version: 6,
        },
        &mut ports,
    );
    assert_eq!(state.borrow().calls, vec![
        "guard:rule.can-settle-payout",
        "outcome:failure",
        "continuation:close",
    ]);
    assert_eq!(result, CompleteSettlementOperationOutcome::Failure {
        value: None,
        failure_code: "guard-rejected",
        exactly_once_distributed_delivery_claimed: false,
    });
}

#[test]
fn operation_v1_rolls_back_write_failure_without_external_effect() {
    let (mut ports, state) = fixture(true, true);
    let result = COMPLETE_SETTLEMENT_OPERATION(
        &CompleteSettlementInput {
            settlement_id: "settlement-001",
            expected_state_version: 7,
        },
        &mut ports,
    );
    assert!(state.borrow().calls.contains(&"atomic:rollback".to_owned()));
    assert!(!state.borrow().calls.iter().any(|entry| entry.starts_with("effect:")));
    assert!(matches!(result, CompleteSettlementOperationOutcome::Failure {
        value: None,
        failure_code: "write-failed",
        ..
    }));
}

#[test]
fn operation_v1_classifies_all_five_s1_residues_from_native_fields() {
    let mut before = normal_s1_residue();
    before.scenario = "before-state-write-failure";
    before.occurrence_id = None;
    before.outbox_append_attempted = false;
    before.outbox_checkpoint_observed = false;
    before.transaction_aborted = true;
    before.state_durable = false;
    before.outbox_occurrence_durable = false;
    before.commit_observed = false;
    before.closed_rejection = true;

    let mut between = normal_s1_residue();
    between.scenario = "between-state-and-outbox-failure";
    between.outbox_append_attempted = false;
    between.outbox_checkpoint_observed = false;
    between.transaction_aborted = true;
    between.state_durable = false;
    between.outbox_occurrence_durable = false;
    between.commit_observed = false;
    between.closed_rejection = true;

    let mut missing = normal_s1_residue();
    missing.scenario = "missing-member";
    missing.transaction_id = None;
    missing.state_write_attempted = false;
    missing.outbox_append_attempted = false;
    missing.outbox_checkpoint_observed = false;
    missing.transaction_aborted = true;
    missing.state_durable = false;
    missing.outbox_occurrence_durable = false;
    missing.commit_observed = false;
    missing.closed_rejection = true;

    let mut mixed = normal_s1_residue();
    mixed.scenario = "mixed-commit";
    mixed.outbox_occurrence_durable = false;
    mixed.outbox_checkpoint_observed = false;
    mixed.closed_rejection = true;

    let mut rollback = normal_s1_residue();
    rollback.scenario = "rollback-after-commit";
    rollback.rollback_requested = true;
    rollback.forward_recovery_required = true;
    rollback.closed_rejection = true;

    for (observed, code) in [
        (before, "RMT_S1_BEFORE_STATE_WRITE_FAILURE"),
        (between, "RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH"),
        (missing, "RMT_S1_MISSING_MEMBER"),
        (mixed, "RMT_S1_MIXED_COMMIT"),
        (rollback, "RMT_S1_ROLLBACK_AFTER_COMMIT"),
    ] {
        assert_eq!(classify_operation_s1_residue(&observed), Ok(Some(code)));
    }
}

#[test]
fn operation_v1_rejects_incoherent_s1_residue_without_label_oracle() {
    let mut observed = normal_s1_residue();
    observed.scenario = "before-state-write-failure";
    observed.occurrence_id = None;
    observed.outbox_append_attempted = false;
    observed.outbox_checkpoint_observed = false;
    observed.state_durable = false;
    observed.outbox_occurrence_durable = false;
    observed.commit_observed = false;
    observed.closed_rejection = true;
    assert_eq!(
        classify_operation_s1_residue(&observed),
        Err("RMT_OP_S1_RESIDUE_INCOHERENT"),
    );
}

#[test]
fn operation_v1_source_has_no_ambient_effect_or_exactly_once_claim() {
    let source = include_str!("../src/remaining_types/operation_v1.rs");
    for forbidden in [
        "use std::fs", "use std::net", "std::process", "std::thread",
        "unsafe {", "exactly_once_distributed_delivery_claimed: true",
    ] {
        assert!(!source.contains(forbidden), "forbidden source: {forbidden}");
    }
}
