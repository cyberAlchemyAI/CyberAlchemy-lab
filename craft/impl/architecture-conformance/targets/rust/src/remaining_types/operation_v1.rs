pub const GUARD_ID: &str = "rule.can-settle-payout";
pub const SETTLEMENT_READ_TARGET: &str =
    "settlement.read.settlement-by-id";
pub const PAYOUT_ACCOUNT_READ_TARGET: &str =
    "settlement.read.payout-account";
pub const PAYOUT_WRITE_TARGET: &str =
    "settlement.write.payout-record";
pub const SETTLEMENT_STATUS_WRITE_TARGET: &str =
    "settlement.write.settlement-status";
pub const PAYOUT_CREATED_EFFECT_TARGET: &str =
    "event-store.append.PayoutCreated";
pub const CONTINUATION_CLOSURE: &str =
    "return-await-cancel-close-dispose-finalizer-quiescence";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CompleteSettlementInput<'a> {
    pub settlement_id: &'a str,
    pub expected_state_version: i64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SettlementRecord {
    pub settlement_id: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PayoutAccountRecord {
    pub account_id: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CompleteSettlementRead {
    Settlement(SettlementRecord),
    PayoutAccount(PayoutAccountRecord),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CompleteSettlementWrite {
    PayoutRecord {
        settlement_id: String,
        payout_id: String,
    },
    SettlementStatus {
        settlement_id: String,
        status: String,
    },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PayoutCreatedEvent {
    pub event_type: &'static str,
    pub settlement_id: String,
    pub payout_id: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CompleteSettlementSuccess {
    pub settlement_id: String,
    pub payout_id: String,
    pub status: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CompleteSettlementOperationOutcome {
    Success {
        value: CompleteSettlementSuccess,
        failure_code: Option<&'static str>,
        exactly_once_distributed_delivery_claimed: bool,
    },
    Failure {
        value: Option<CompleteSettlementSuccess>,
        failure_code: &'static str,
        exactly_once_distributed_delivery_claimed: bool,
    },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OperationS1NativeResidue<'a> {
    pub scenario: &'a str,
    pub transaction_id: Option<&'a str>,
    pub occurrence_id: Option<&'a str>,
    pub state_write_attempted: bool,
    pub outbox_append_attempted: bool,
    pub outbox_checkpoint_observed: bool,
    pub transaction_aborted: bool,
    pub state_durable: bool,
    pub outbox_occurrence_durable: bool,
    pub commit_observed: bool,
    pub rollback_requested: bool,
    pub history_erased: bool,
    pub forward_recovery_required: bool,
    pub closed_rejection: bool,
}

pub fn classify_operation_s1_residue(
    observed: &OperationS1NativeResidue<'_>,
) -> Result<Option<&'static str>, &'static str> {
    let transaction_present = observed.transaction_id
        .is_some_and(|value| !value.is_empty());
    let occurrence_present = observed.occurrence_id
        .is_some_and(|value| !value.is_empty());
    let (code, coherent) = match observed.scenario {
        "normal" => (None,
            transaction_present && occurrence_present &&
            observed.state_write_attempted && observed.outbox_append_attempted &&
            observed.outbox_checkpoint_observed && !observed.transaction_aborted &&
            observed.state_durable && observed.outbox_occurrence_durable &&
            observed.commit_observed && !observed.rollback_requested &&
            !observed.history_erased && !observed.forward_recovery_required &&
            !observed.closed_rejection),
        "before-state-write-failure" => (
            Some("RMT_S1_BEFORE_STATE_WRITE_FAILURE"),
            transaction_present && !occurrence_present &&
            observed.state_write_attempted && !observed.outbox_append_attempted &&
            !observed.outbox_checkpoint_observed && observed.transaction_aborted &&
            !observed.state_durable && !observed.outbox_occurrence_durable &&
            !observed.commit_observed && !observed.history_erased &&
            observed.closed_rejection,
        ),
        "between-state-and-outbox-failure" => (
            Some("RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH"),
            transaction_present && occurrence_present &&
            observed.state_write_attempted && !observed.outbox_append_attempted &&
            !observed.outbox_checkpoint_observed && observed.transaction_aborted &&
            !observed.state_durable && !observed.outbox_occurrence_durable &&
            !observed.commit_observed && !observed.history_erased &&
            observed.closed_rejection,
        ),
        "missing-member" => (
            Some("RMT_S1_MISSING_MEMBER"),
            (!transaction_present || !occurrence_present) &&
            !observed.state_write_attempted && !observed.outbox_append_attempted &&
            !observed.outbox_checkpoint_observed && observed.transaction_aborted &&
            !observed.state_durable && !observed.outbox_occurrence_durable &&
            !observed.commit_observed && observed.closed_rejection,
        ),
        "mixed-commit" => (
            Some("RMT_S1_MIXED_COMMIT"),
            observed.state_durable != observed.outbox_occurrence_durable &&
            observed.state_write_attempted && observed.outbox_append_attempted &&
            !observed.outbox_checkpoint_observed && !observed.history_erased &&
            observed.closed_rejection,
        ),
        "rollback-after-commit" => (
            Some("RMT_S1_ROLLBACK_AFTER_COMMIT"),
            observed.commit_observed && observed.state_durable &&
            observed.outbox_occurrence_durable && observed.rollback_requested &&
            observed.state_write_attempted && observed.outbox_append_attempted &&
            observed.outbox_checkpoint_observed && !observed.history_erased &&
            observed.forward_recovery_required && observed.closed_rejection,
        ),
        _ => (None, false),
    };
    if coherent {
        Ok(code)
    } else {
        Err("RMT_OP_S1_RESIDUE_INCOHERENT")
    }
}

pub trait CompleteSettlementTransaction {
    fn write(
        &mut self,
        target_id: &'static str,
        value: CompleteSettlementWrite,
    ) -> Result<(), &'static str>;

    fn commit(&mut self, mode: &'static str) -> Result<(), &'static str>;

    fn rollback(&mut self);
}

pub trait CompleteSettlementOperationPorts {
    fn guard(
        &mut self,
        guard_id: &'static str,
        input: &CompleteSettlementInput<'_>,
    ) -> bool;

    fn read(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> Result<CompleteSettlementRead, &'static str>;

    fn begin_atomic(&mut self) -> Box<dyn CompleteSettlementTransaction>;

    fn external_effect(
        &mut self,
        target_id: &'static str,
        event: PayoutCreatedEvent,
    ) -> Result<(), &'static str>;

    fn close(
        &mut self,
        closure: &'static str,
        failure_code: Option<&'static str>,
    );
}

pub type BoundOperation = for<'a> fn(
    &CompleteSettlementInput<'a>,
    &mut dyn CompleteSettlementOperationPorts,
) -> CompleteSettlementOperationOutcome;

pub const COMPLETE_SETTLEMENT_OPERATION: BoundOperation =
    complete_settlement_operation;

fn failure(failure_code: &'static str) -> CompleteSettlementOperationOutcome {
    CompleteSettlementOperationOutcome::Failure {
        value: None,
        failure_code,
        exactly_once_distributed_delivery_claimed: false,
    }
}

pub fn complete_settlement_operation(
    input: &CompleteSettlementInput<'_>,
    ports: &mut dyn CompleteSettlementOperationPorts,
) -> CompleteSettlementOperationOutcome {
    let guard_allowed = ports.guard(GUARD_ID, input);
    if !guard_allowed {
        ports.close(CONTINUATION_CLOSURE, Some("guard-rejected"));
        return failure("guard-rejected");
    }

    let settlement = match ports.read(
        SETTLEMENT_READ_TARGET,
        input.settlement_id,
    ) {
        Ok(CompleteSettlementRead::Settlement(value)) => value,
        _ => {
            ports.close(CONTINUATION_CLOSURE, Some("read-failed"));
            return failure("read-failed");
        }
    };
    let payout_account = match ports.read(
        PAYOUT_ACCOUNT_READ_TARGET,
        input.settlement_id,
    ) {
        Ok(CompleteSettlementRead::PayoutAccount(value)) => value,
        _ => {
            ports.close(CONTINUATION_CLOSURE, Some("read-failed"));
            return failure("read-failed");
        }
    };

    let payout_id = format!(
        "{}:{}",
        payout_account.account_id,
        settlement.settlement_id,
    );
    let mut transaction = ports.begin_atomic();
    if transaction.write(
        PAYOUT_WRITE_TARGET,
        CompleteSettlementWrite::PayoutRecord {
            settlement_id: input.settlement_id.to_owned(),
            payout_id: payout_id.clone(),
        },
    ).is_err() {
        transaction.rollback();
        ports.close(CONTINUATION_CLOSURE, Some("write-failed"));
        return failure("write-failed");
    }
    if transaction.write(
        SETTLEMENT_STATUS_WRITE_TARGET,
        CompleteSettlementWrite::SettlementStatus {
            settlement_id: input.settlement_id.to_owned(),
            status: "committed".to_owned(),
        },
    ).is_err() {
        transaction.rollback();
        ports.close(CONTINUATION_CLOSURE, Some("write-failed"));
        return failure("write-failed");
    }
    if transaction.commit("all-or-nothing").is_err() {
        transaction.rollback();
        ports.close(CONTINUATION_CLOSURE, Some("write-failed"));
        return failure("write-failed");
    }
    drop(transaction);

    if ports.external_effect(
        PAYOUT_CREATED_EFFECT_TARGET,
        PayoutCreatedEvent {
            event_type: "PayoutCreated",
            settlement_id: input.settlement_id.to_owned(),
            payout_id: payout_id.clone(),
        },
    ).is_err() {
        ports.close(CONTINUATION_CLOSURE, Some("effect-failed"));
        return failure("effect-failed");
    }

    ports.close(CONTINUATION_CLOSURE, None);
    CompleteSettlementOperationOutcome::Success {
        value: CompleteSettlementSuccess {
            settlement_id: input.settlement_id.to_owned(),
            payout_id,
            status: "committed".to_owned(),
        },
        failure_code: None,
        exactly_once_distributed_delivery_claimed: false,
    }
}
