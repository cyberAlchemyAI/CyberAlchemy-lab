export type CompleteSettlementOperationInput = Readonly<{
  settlement_id: string;
  expected_state_version: number;
}>;

export type CompleteSettlementOperationFailureCode =
  | "guard-rejected"
  | "read-failed"
  | "write-failed"
  | "effect-failed";

export type CompleteSettlementOperationOutcome =
  | Readonly<{
    kind: "success";
    value: Readonly<{
      settlement_id: string;
      payout_id: string;
      status: string;
    }>;
    failure_code: null;
    exactly_once_distributed_delivery_claimed: false;
  }>
  | Readonly<{
    kind: "failure";
    value: null;
    failure_code: CompleteSettlementOperationFailureCode;
    exactly_once_distributed_delivery_claimed: false;
  }>;

export type CompleteSettlementOperationTransaction = Readonly<{
  write: (
    target_id:
      | "settlement.write.payout-record"
      | "settlement.write.settlement-status",
    value: Readonly<Record<string, string | number>>,
  ) => Promise<void>;
  commit: (mode?: "all-or-nothing" | "best-effort") => Promise<void>;
  rollback: () => Promise<void>;
}>;

export type CompleteSettlementOperationPorts = Readonly<{
  guard: (
    guard_id: "rule.can-settle-payout",
    input: CompleteSettlementOperationInput,
  ) => Promise<Readonly<{allowed: boolean}>>;
  read: (
    target_id:
      | "settlement.read.settlement-by-id"
      | "settlement.read.payout-account",
    settlement_id: string,
  ) => Promise<Readonly<Record<string, string | number>>>;
  beginAtomic: () => Promise<CompleteSettlementOperationTransaction>;
  externalEffect: (
    target_id: "event-store.append.PayoutCreated",
    event: Readonly<{
      event_type: "PayoutCreated";
      settlement_id: string;
      payout_id: string;
    }>,
  ) => Promise<void>;
  close: (
    closure: "return-await-cancel-close-dispose-finalizer-quiescence",
    failure_code: CompleteSettlementOperationFailureCode | null,
  ) => Promise<void>;
}>;

export type OperationS1NativeResidue = Readonly<{
  scenario:string;transaction_id:string|null;occurrence_id:string|null;
  state_write_attempted:boolean;outbox_append_attempted:boolean;
  outbox_checkpoint_observed:boolean;transaction_aborted:boolean;
  state_durable:boolean;outbox_occurrence_durable:boolean;
  commit_observed:boolean;rollback_requested:boolean;history_erased:boolean;
  forward_recovery_required:boolean;closed_rejection:boolean;
}>;

export const classifyOperationS1Residue=(observed:OperationS1NativeResidue):string|null=>{
  const present=(value:string|null)=>typeof value==="string"&&value.length>0;
  let code:string|null=null,coherent=false;
  if(observed.scenario==="normal")coherent=present(observed.transaction_id)&&present(observed.occurrence_id)&&observed.state_write_attempted&&observed.outbox_append_attempted&&observed.outbox_checkpoint_observed&&!observed.transaction_aborted&&observed.state_durable&&observed.outbox_occurrence_durable&&observed.commit_observed&&!observed.rollback_requested&&!observed.history_erased&&!observed.forward_recovery_required&&!observed.closed_rejection;
  else if(observed.scenario==="before-state-write-failure"){code="RMT_S1_BEFORE_STATE_WRITE_FAILURE";coherent=present(observed.transaction_id)&&observed.occurrence_id===null&&observed.state_write_attempted&&!observed.outbox_append_attempted&&!observed.outbox_checkpoint_observed&&observed.transaction_aborted&&!observed.state_durable&&!observed.outbox_occurrence_durable&&!observed.commit_observed&&!observed.history_erased&&observed.closed_rejection;}
  else if(observed.scenario==="between-state-and-outbox-failure"){code="RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH";coherent=present(observed.transaction_id)&&present(observed.occurrence_id)&&observed.state_write_attempted&&!observed.outbox_append_attempted&&!observed.outbox_checkpoint_observed&&observed.transaction_aborted&&!observed.state_durable&&!observed.outbox_occurrence_durable&&!observed.commit_observed&&!observed.history_erased&&observed.closed_rejection;}
  else if(observed.scenario==="missing-member"){code="RMT_S1_MISSING_MEMBER";coherent=(!present(observed.transaction_id)||!present(observed.occurrence_id))&&!observed.state_write_attempted&&!observed.outbox_append_attempted&&!observed.outbox_checkpoint_observed&&observed.transaction_aborted&&!observed.state_durable&&!observed.outbox_occurrence_durable&&!observed.commit_observed&&observed.closed_rejection;}
  else if(observed.scenario==="mixed-commit"){code="RMT_S1_MIXED_COMMIT";coherent=observed.state_durable!==observed.outbox_occurrence_durable&&observed.state_write_attempted&&observed.outbox_append_attempted&&!observed.outbox_checkpoint_observed&&!observed.history_erased&&observed.closed_rejection;}
  else if(observed.scenario==="rollback-after-commit"){code="RMT_S1_ROLLBACK_AFTER_COMMIT";coherent=observed.commit_observed&&observed.state_durable&&observed.outbox_occurrence_durable&&observed.rollback_requested&&observed.state_write_attempted&&observed.outbox_append_attempted&&observed.outbox_checkpoint_observed&&!observed.history_erased&&observed.forward_recovery_required&&observed.closed_rejection;}
  if(!coherent)throw Object.assign(new Error("RMT_OP_S1_RESIDUE_INCOHERENT"),{code:"RMT_OP_S1_RESIDUE_INCOHERENT"});
  return code;
};

const failure = (
  failureCode: CompleteSettlementOperationFailureCode,
): CompleteSettlementOperationOutcome => Object.freeze({
  kind: "failure",
  value: null,
  failure_code: failureCode,
  exactly_once_distributed_delivery_claimed: false,
});

export const completeSettlementOperation = async (
  input: CompleteSettlementOperationInput,
  ports: CompleteSettlementOperationPorts,
): Promise<CompleteSettlementOperationOutcome> => {
  const guard = await ports.guard("rule.can-settle-payout", input);
  if (!guard.allowed) {
    await ports.close(
      "return-await-cancel-close-dispose-finalizer-quiescence",
      "guard-rejected",
    );
    return failure("guard-rejected");
  }

  let settlement: Readonly<Record<string, string | number>>;
  let payoutAccount: Readonly<Record<string, string | number>>;
  try {
    settlement = await ports.read(
      "settlement.read.settlement-by-id",
      input.settlement_id,
    );
    payoutAccount = await ports.read(
      "settlement.read.payout-account",
      input.settlement_id,
    );
  } catch {
    await ports.close(
      "return-await-cancel-close-dispose-finalizer-quiescence",
      "read-failed",
    );
    return failure("read-failed");
  }

  const transaction = await ports.beginAtomic();
  const payoutId = `${String(payoutAccount.account_id)}:${String(
    settlement.settlement_id,
  )}`;
  try {
    await transaction.write("settlement.write.payout-record", {
      settlement_id: input.settlement_id,
      payout_id: payoutId,
    });
    await transaction.write("settlement.write.settlement-status", {
      settlement_id: input.settlement_id,
      status: "committed",
    });
    await transaction.commit();
  } catch {
    await transaction.rollback();
    await ports.close(
      "return-await-cancel-close-dispose-finalizer-quiescence",
      "write-failed",
    );
    return failure("write-failed");
  }

  try {
    await ports.externalEffect("event-store.append.PayoutCreated", {
      event_type: "PayoutCreated",
      settlement_id: input.settlement_id,
      payout_id: payoutId,
    });
  } catch {
    await ports.close(
      "return-await-cancel-close-dispose-finalizer-quiescence",
      "effect-failed",
    );
    return failure("effect-failed");
  }

  await ports.close(
    "return-await-cancel-close-dispose-finalizer-quiescence",
    null,
  );
  return Object.freeze({
    kind: "success",
    value: Object.freeze({
      settlement_id: input.settlement_id,
      payout_id: payoutId,
      status: "committed",
    }),
    failure_code: null,
    exactly_once_distributed_delivery_claimed: false,
  });
};
