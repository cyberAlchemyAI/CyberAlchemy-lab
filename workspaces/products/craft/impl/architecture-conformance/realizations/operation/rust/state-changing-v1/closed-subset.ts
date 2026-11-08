import {createHash} from "node:crypto";

import type {OperationFindingCode} from
  "../../../../families/state-changing-action/contracts/state-changing-action-contracts.js";

export const RUST_OPERATION_OBSERVER_ID =
  "observer.rust-operation-ports/v1" as const;

export const RUST_OPERATION_SOURCE_CONTROLS = Object.freeze([
  {control_id: "rust-op/undeclared-write",
    expected_code: "RMT_OP_UNDECLARED_WRITE"},
  {control_id: "rust-op/undeclared-effect",
    expected_code: "RMT_OP_UNDECLARED_EFFECT"},
  {control_id: "rust-op/guard-bypass",
    expected_code: "RMT_OP_GUARD_BYPASS"},
  {control_id: "rust-op/order-swap",
    expected_code: "RMT_OP_ORDER_SWAP"},
  {control_id: "rust-op/atomicity-removed",
    expected_code: "RMT_OP_ATOMICITY_REMOVED"},
  {control_id: "rust-op/success-failure-collapse",
    expected_code: "RMT_OP_SUCCESS_FAILURE_COLLAPSE"},
  {control_id: "rust-op/emitted-before-commit",
    expected_code: "RMT_OP_EMITTED_BEFORE_COMMIT"},
  {control_id: "rust-op/continuation-mismatch",
    expected_code: "RMT_OP_CONTINUATION_MISMATCH"},
  {control_id: "rust-op/read-set-drift",
    expected_code: "RMT_OP_READ_SET_DRIFT"},
  {control_id: "rust-op/output-contract-overclaim",
    expected_code: "RMT_OP_OUTPUT_CONTRACT_OVERCLAIM"},
] as const satisfies readonly Readonly<{
  control_id: string;
  expected_code: OperationFindingCode;
}>[]);

export type RustOperationClosedSubsetProofV1 = Readonly<{
  schema_version: "RustOperationClosedSubsetProof/v1";
  result: "pass";
  source_sha256: string;
  symbol_name: "COMPLETE_SETTLEMENT_OPERATION";
  observer_id: typeof RUST_OPERATION_OBSERVER_ID;
  admitted_form:
    "synchronous-function-with-borrowed-input-and-injected-owned-transaction";
  source_control_count: 10;
  ambient_dependencies: readonly [];
  authority_effect: "none";
}>;

export class RustOperationSubsetError extends Error {
  readonly code: string;

  constructor(code: string) {
    super(code);
    this.name = "RustOperationSubsetError";
    this.code = code;
  }
}

const fail = (code: string): never => {
  throw new RustOperationSubsetError(code);
};
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8").digest("hex");
const replaceOnce = (
  source: string,
  needle: string,
  replacement: string,
  controlId: string,
): string => {
  const first = source.indexOf(needle);
  if (first < 0 || source.indexOf(needle, first + needle.length) >= 0) {
    return fail(`RUST_OP_SOURCE_CONTROL_TARGET_INVALID:${controlId}`);
  }
  return source.slice(0, first) + replacement +
    source.slice(first + needle.length);
};

export const inspectRustOperationClosedSubset = (
  source: string,
): RustOperationClosedSubsetProofV1 => {
  if (!/^[\x00-\x7F]*$/u.test(source) ||
      (source.match(/pub fn complete_settlement_operation\s*\(/gu) ?? [])
        .length !== 1 ||
      !source.includes("input: &CompleteSettlementInput<'_>") ||
      !source.includes("ports: &mut dyn CompleteSettlementOperationPorts") ||
      !source.includes(
        "pub const COMPLETE_SETTLEMENT_OPERATION: BoundOperation =",
      ) ||
      /(?:\bextern\s+crate\b|\bunsafe\b|\b(?:include|include_bytes|include_str|env|option_env)!\s*\()/u
        .test(source) ||
      /(?:static\s+mut|macro_rules!|\basync\b|\bFuture\b)/u.test(source) ||
      /(?:std::(?:env|fs|net|process|thread)|Command::new|File::|OpenOptions)/u
        .test(source)) {
    return fail("RUST_OP_CLOSED_SUBSET_SOURCE_SHAPE");
  }
  for (const required of [
    "rule.can-settle-payout",
    "settlement.read.settlement-by-id",
    "settlement.read.payout-account",
    "settlement.write.payout-record",
    "settlement.write.settlement-status",
    "event-store.append.PayoutCreated",
    "return-await-cancel-close-dispose-finalizer-quiescence",
  ]) {
    if (!source.includes(required)) {
      return fail("RUST_OP_CLOSED_SUBSET_DECLARED_PORT_MISSING");
    }
  }
  return Object.freeze({
    schema_version: "RustOperationClosedSubsetProof/v1" as const,
    result: "pass" as const,
    source_sha256: sha256(source),
    symbol_name: "COMPLETE_SETTLEMENT_OPERATION" as const,
    observer_id: RUST_OPERATION_OBSERVER_ID,
    admitted_form:
      "synchronous-function-with-borrowed-input-and-injected-owned-transaction" as const,
    source_control_count: 10 as const,
    ambient_dependencies: Object.freeze([]) as readonly [],
    authority_effect: "none" as const,
  });
};

export const applyRustOperationSourceControl = (
  source: string,
  controlId: string,
): string => {
  inspectRustOperationClosedSubset(source);
  let mutated: string;
  if (controlId === "rust-op/undeclared-write") {
    const commit = '    if transaction.commit("all-or-nothing").is_err() {';
    mutated = replaceOnce(source, commit, `    let _ = transaction.write(
        "settlement.write.undeclared-audit-row",
        CompleteSettlementWrite::SettlementStatus {
            settlement_id: input.settlement_id.to_owned(),
            status: "audit".to_owned(),
        },
    );
${commit}`, controlId);
  } else if (controlId === "rust-op/undeclared-effect") {
    const close = "    ports.close(CONTINUATION_CLOSURE, None);";
    mutated = replaceOnce(source, close, `    let _ = ports.external_effect(
        "network.send.undeclared-webhook",
        PayoutCreatedEvent {
            event_type: "PayoutCreated",
            settlement_id: input.settlement_id.to_owned(),
            payout_id: payout_id.clone(),
        },
    );
${close}`, controlId);
  } else if (controlId === "rust-op/guard-bypass") {
    mutated = replaceOnce(
      source,
      "    if !guard_allowed {",
      "    if false && !guard_allowed {",
      controlId,
    );
  } else if (controlId === "rust-op/order-swap") {
    const first = `    let settlement = match ports.read(
        SETTLEMENT_READ_TARGET,
        input.settlement_id,
    ) {
        Ok(CompleteSettlementRead::Settlement(value)) => value,
        _ => {
            ports.close(CONTINUATION_CLOSURE, Some("read-failed"));
            return failure("read-failed");
        }
    };`;
    const second = `    let payout_account = match ports.read(
        PAYOUT_ACCOUNT_READ_TARGET,
        input.settlement_id,
    ) {
        Ok(CompleteSettlementRead::PayoutAccount(value)) => value,
        _ => {
            ports.close(CONTINUATION_CLOSURE, Some("read-failed"));
            return failure("read-failed");
        }
    };`;
    mutated = replaceOnce(source, first, "__RUST_OP_READ_ONE__", controlId);
    mutated = replaceOnce(mutated, second, `${second}\n${first}`, controlId);
    mutated = replaceOnce(mutated, "__RUST_OP_READ_ONE__\n", "", controlId);
  } else if (controlId === "rust-op/atomicity-removed") {
    mutated = replaceOnce(
      source,
      'transaction.commit("all-or-nothing")',
      'transaction.commit("best-effort")',
      controlId,
    );
  } else if (controlId === "rust-op/success-failure-collapse") {
    mutated = replaceOnce(
      source,
      '        return failure("guard-rejected");',
      `        return CompleteSettlementOperationOutcome::Failure {
            value: Some(CompleteSettlementSuccess {
                settlement_id: input.settlement_id.to_owned(),
                payout_id: "forbidden".to_owned(),
                status: "committed".to_owned(),
            }),
            failure_code: "guard-rejected",
            exactly_once_distributed_delivery_claimed: false,
        };`,
      controlId,
    );
  } else if (controlId === "rust-op/emitted-before-commit") {
    const commit = '    if transaction.commit("all-or-nothing").is_err() {';
    mutated = replaceOnce(source, commit, `    let _ = ports.external_effect(
        PAYOUT_CREATED_EFFECT_TARGET,
        PayoutCreatedEvent {
            event_type: "PayoutCreated",
            settlement_id: input.settlement_id.to_owned(),
            payout_id: payout_id.clone(),
        },
    );
${commit}`, controlId);
  } else if (controlId === "rust-op/continuation-mismatch") {
    mutated = source.replaceAll(
      "return-await-cancel-close-dispose-finalizer-quiescence",
      "return-await-cancel-close-dispose-finalizer-quiescence-mismatch",
    );
  } else if (controlId === "rust-op/read-set-drift") {
    const begin = "    let mut transaction = ports.begin_atomic();";
    mutated = replaceOnce(source, begin, `    let _ = ports.read(
        "settlement.read.undeclared-audit-log",
        input.settlement_id,
    );
${begin}`, controlId);
  } else if (controlId === "rust-op/output-contract-overclaim") {
    mutated = source.replaceAll(
      "exactly_once_distributed_delivery_claimed: false",
      "exactly_once_distributed_delivery_claimed: true",
    );
  } else {
    return fail(`RUST_OP_SOURCE_CONTROL_UNKNOWN:${controlId}`);
  }
  if (sha256(mutated) === sha256(source)) {
    return fail(`RUST_OP_SOURCE_CONTROL_NOOP:${controlId}`);
  }
  return mutated;
};
