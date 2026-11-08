import { createHash } from "node:crypto";

import {
  canonicalJson,
  contractSuccess,
  type SfolContractResult,
} from "../language/contracts.js";

export const FORMAL_OBLIGATION_REQUEST_VERSION =
  "evf.formal-obligation-request/v1" as const;
export const SMT_PROVIDER_RECEIPT_VERSION =
  "evf.smt-provider-receipt/v1" as const;

export type RequestState = "ready" | "blocked" | "stale";
export type QueryKind = "counterexample" | "witness";
export type ExecutionStatus = "completed" | "blocked" | "failed" | "stale";
export type FailureKind =
  | "timeout"
  | "process-error"
  | "invalid-output"
  | "missing-output"
  | "policy-block"
  | "stale-input"
  | null;
export type NativeOutcome = "sat" | "unsat" | "unknown";
export type EvidenceOrigin =
  | "observed-solver-execution"
  | "synthetic-validator-input";
export type ProtocolConsumer = "observed-provider-evidence" | "validator-test";
export type NormalizedOutcome =
  | "counterexample"
  | "no-counterexample"
  | "witness"
  | "no-witness"
  | "unresolved";
export type SmtClaimCeiling =
  | "exact-formula-solver-result-only"
  | "no-property-claim"
  | "protocol-validation-only-no-solver-or-domain-claim";

export interface ExactArtifactRef {
  readonly path: string;
  readonly sha256: string;
  readonly size_bytes: number;
  readonly current?: boolean;
}

export interface FormalObligationRequest {
  readonly schema_version: typeof FORMAL_OBLIGATION_REQUEST_VERSION;
  readonly request_id: string;
  readonly request_state: RequestState;
  readonly query_kind: QueryKind;
  readonly semantic_source_ref: ExactArtifactRef;
  readonly formal_obligation_ref: ExactArtifactRef;
  readonly theory_profile_ref: ExactArtifactRef;
  readonly symbol_table_ref: ExactArtifactRef;
  readonly assumptions_ref: ExactArtifactRef;
  readonly translation_contract_ref: ExactArtifactRef;
  readonly runtime_manifest_ref: ExactArtifactRef;
  readonly execution_policy: {
    readonly timeout_ms: number;
    readonly memory_ceiling_bytes: number;
    readonly max_output_bytes: number;
    readonly network: "forbidden";
    readonly working_directory: string;
    readonly environment_allowlist: readonly string[];
  };
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
  readonly claim_ceiling: "request-only-no-evaluation-claim";
  readonly residue: readonly string[];
}

export interface TranslationReceiptBinding {
  readonly receipt_ref: ExactArtifactRef;
  readonly validation_status: "valid" | "blocked" | "stale";
  readonly translated_query_digest: string;
  readonly omitted_term_count: number;
  readonly invented_term_count: number;
}

export interface ExecutionTuple {
  readonly run_id: string;
  readonly status: string;
  readonly timed_out: boolean;
  readonly failure_kind: string | null;
  readonly exit_code: number | null;
}

export interface NativeResult {
  readonly outcome: NativeOutcome;
  readonly result_ref: ExactArtifactRef;
  readonly result_digest: string;
}

export interface BoundWitness {
  readonly model_ref: ExactArtifactRef;
  readonly request_ref: string;
  readonly translated_query_digest: string;
  readonly runtime_manifest_ref: string;
  readonly execution_run_id: string;
  readonly native_result_digest: string;
  readonly bindings_digest: string;
}

export interface ProtocolMappingInput {
  readonly receipt_id: string;
  readonly request: FormalObligationRequest;
  readonly translation: TranslationReceiptBinding;
  readonly execution: ExecutionTuple;
  readonly native_result: NativeResult | null;
  readonly witness: BoundWitness | null;
  readonly evidence_origin: string;
  readonly consumer: string;
  readonly inline_predicate_present: boolean;
  readonly claimed_normalized: string;
  readonly claimed_ceiling: string;
  readonly claimed_broad: boolean;
  readonly evidence_refs: readonly ExactArtifactRef[];
  readonly residue: readonly string[];
}

export interface SmtProviderReceipt {
  readonly schema_version: typeof SMT_PROVIDER_RECEIPT_VERSION;
  readonly receipt_id: string;
  readonly evidence_origin: EvidenceOrigin;
  readonly request_ref: string;
  readonly semantic_source_ref: ExactArtifactRef;
  readonly formal_obligation_ref: ExactArtifactRef;
  readonly translation_receipt_ref: ExactArtifactRef;
  readonly runtime_manifest_ref: ExactArtifactRef;
  readonly query_kind: QueryKind;
  readonly execution: ExecutionTuple;
  readonly native_result: NativeResult | null;
  readonly witness: BoundWitness | null;
  readonly normalized_result: { readonly outcome: NormalizedOutcome };
  readonly semantic_result_digest: string;
  readonly evidence_refs: readonly ExactArtifactRef[];
  readonly residue: readonly string[];
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
  readonly claim_ceiling: SmtClaimCeiling;
  readonly receipt_payload_digest: string;
}

export type SmtProtocolDiagnosticCode =
  | "EVIDENCE_ORIGIN_INVALID"
  | "INLINE_SEMANTICS_FORBIDDEN"
  | "READY_REF_STALE"
  | "TRANSLATION_NOT_CLOSED"
  | "COMPLETED_EXECUTION_CONTRADICTION"
  | "COMPLETED_NATIVE_REQUIRED"
  | "NONCOMPLETED_NATIVE_PRESENT"
  | "FAILED_EXECUTION_ALGEBRA_INVALID"
  | "BLOCKED_EXECUTION_ALGEBRA_INVALID"
  | "STALE_EXECUTION_ALGEBRA_INVALID"
  | "REQUEST_EXECUTION_STATE_CONTRADICTION"
  | "SAT_WITNESS_REQUIRED"
  | "SAT_WITNESS_BINDING_MISMATCH"
  | "NON_SAT_WITNESS_FORBIDDEN"
  | "SYNTHETIC_OBSERVED_CONSUMER_FORBIDDEN"
  | "NORMALIZED_OUTCOME_MISMATCH"
  | "BROAD_CLAIM_FORBIDDEN"
  | "CLAIM_CEILING_MISMATCH";

export interface SmtProtocolDiagnostic {
  readonly code: SmtProtocolDiagnosticCode;
  readonly stage: "contract";
  readonly path: string;
  readonly detail: string;
}

type SfolContractSuccess<T> = Extract<SfolContractResult<T>, { ok: true }>;

export type SmtProtocolResult<T> =
  | SfolContractSuccess<T>
  | {
      readonly ok: false;
      readonly diagnostics: readonly SmtProtocolDiagnostic[];
    };

const OBSERVED_ORIGIN: EvidenceOrigin = "observed-solver-execution";
const SYNTHETIC_ORIGIN: EvidenceOrigin = "synthetic-validator-input";
const OBSERVED_CLAIM: SmtClaimCeiling =
  "exact-formula-solver-result-only";
const NO_PROPERTY_CLAIM: SmtClaimCeiling = "no-property-claim";
const SYNTHETIC_CLAIM: SmtClaimCeiling =
  "protocol-validation-only-no-solver-or-domain-claim";

export function mapSmtProviderReceipt(
  input: ProtocolMappingInput,
): SmtProtocolResult<SmtProviderReceipt> {
  if (
    input.evidence_origin !== OBSERVED_ORIGIN &&
    input.evidence_origin !== SYNTHETIC_ORIGIN
  ) {
    return protocolFailure(
      "EVIDENCE_ORIGIN_INVALID",
      "$.evidence_origin",
      `unsupported evidence origin ${input.evidence_origin}`,
    );
  }

  if (input.inline_predicate_present) {
    return protocolFailure(
      "INLINE_SEMANTICS_FORBIDDEN",
      "$.request",
      "domain predicates must be supplied through exact owner-authored references",
    );
  }

  if (
    input.request.request_state === "ready" &&
    requestRefs(input.request).some((reference) => reference.current !== true)
  ) {
    return protocolFailure(
      "READY_REF_STALE",
      "$.request",
      "a ready request requires every exact reference to be current",
    );
  }

  const translationStateCoherent =
    input.translation.validation_status === "valid" ||
    (input.request.request_state === "stale" &&
      input.translation.validation_status === "stale");
  if (
    !translationStateCoherent ||
    input.translation.omitted_term_count !== 0 ||
    input.translation.invented_term_count !== 0
  ) {
    return protocolFailure(
      "TRANSLATION_NOT_CLOSED",
      "$.translation",
      "mapping requires a valid translation, or one stale translation on a stale request, with zero omissions and inventions",
    );
  }

  const executionFailure = validateExecution(input.execution, input.native_result);
  if (executionFailure !== null) {
    return executionFailure;
  }

  if (
    (input.request.request_state === "blocked" ||
      input.request.request_state === "stale") &&
    input.execution.status === "completed"
  ) {
    return protocolFailure(
      "REQUEST_EXECUTION_STATE_CONTRADICTION",
      "$.request.request_state",
      `${input.request.request_state} requests cannot carry completed execution`,
    );
  }

  const witnessFailure = validateWitness(input);
  if (witnessFailure !== null) {
    return witnessFailure;
  }

  if (
    input.evidence_origin === SYNTHETIC_ORIGIN &&
    input.consumer === "observed-provider-evidence"
  ) {
    return protocolFailure(
      "SYNTHETIC_OBSERVED_CONSUMER_FORBIDDEN",
      "$.consumer",
      "synthetic validator input cannot enter an observed-provider-evidence consumer",
    );
  }

  const normalized = normalize(input.request.query_kind, input.execution, input.native_result);
  if (input.claimed_normalized !== normalized) {
    return protocolFailure(
      "NORMALIZED_OUTCOME_MISMATCH",
      "$.claimed_normalized",
      `claimed ${input.claimed_normalized}; exact mapping requires ${normalized}`,
    );
  }

  if (input.claimed_broad) {
    return protocolFailure(
      "BROAD_CLAIM_FORBIDDEN",
      "$.claimed_broad",
      "protocol receipts cannot claim theorem, full-FOL validity, runtime conformance, implementation correctness, release readiness, or production behavior",
    );
  }

  const claimCeiling = claimFor(
    input.evidence_origin,
    input.execution,
    input.native_result,
  );
  if (input.claimed_ceiling !== claimCeiling) {
    return protocolFailure(
      "CLAIM_CEILING_MISMATCH",
      "$.claimed_ceiling",
      `claimed ${input.claimed_ceiling}; exact mapping requires ${claimCeiling}`,
    );
  }

  const normalizedResult = Object.freeze({ outcome: normalized });
  const payload = {
    schema_version: SMT_PROVIDER_RECEIPT_VERSION,
    receipt_id: input.receipt_id,
    evidence_origin: input.evidence_origin,
    request_ref: input.request.request_id,
    semantic_source_ref: receiptRef(input.request.semantic_source_ref),
    formal_obligation_ref: receiptRef(input.request.formal_obligation_ref),
    translation_receipt_ref: receiptRef(input.translation.receipt_ref),
    runtime_manifest_ref: receiptRef(input.request.runtime_manifest_ref),
    query_kind: input.request.query_kind,
    execution: Object.freeze({ ...input.execution }),
    native_result:
      input.native_result === null
        ? null
        : Object.freeze({
            ...input.native_result,
            result_ref: receiptRef(input.native_result.result_ref),
          }),
    witness:
      input.witness === null
        ? null
        : Object.freeze({
            ...input.witness,
            model_ref: receiptRef(input.witness.model_ref),
          }),
    normalized_result: normalizedResult,
    semantic_result_digest: sha256(canonicalJson(normalizedResult)),
    evidence_refs: Object.freeze(input.evidence_refs.map(receiptRef)),
    residue: Object.freeze([...input.residue]),
    authority_effect: "none" as const,
    release_admission: "not-granted" as const,
    claim_ceiling: claimCeiling,
  };
  const receipt: SmtProviderReceipt = Object.freeze({
    ...payload,
    receipt_payload_digest: sha256(canonicalJson(payload)),
  });
  return protocolSuccess(receipt);
}

export function witnessBindingsDigest(
  witness: Omit<BoundWitness, "bindings_digest">,
): string {
  return sha256(
    canonicalJson({
      execution_run_id: witness.execution_run_id,
      model_ref: receiptRef(witness.model_ref),
      native_result_digest: witness.native_result_digest,
      request_ref: witness.request_ref,
      runtime_manifest_ref: witness.runtime_manifest_ref,
      translated_query_digest: witness.translated_query_digest,
    }),
  );
}

function validateExecution(
  execution: ExecutionTuple,
  nativeResult: NativeResult | null,
): SmtProtocolResult<never> | null {
  if (execution.status === "completed") {
    if (
      execution.timed_out ||
      execution.failure_kind !== null ||
      execution.exit_code !== 0
    ) {
      return protocolFailure(
        "COMPLETED_EXECUTION_CONTRADICTION",
        "$.execution",
        "completed requires timed_out=false, failure_kind=null, and exit_code=0",
      );
    }
    if (nativeResult === null) {
      return protocolFailure(
        "COMPLETED_NATIVE_REQUIRED",
        "$.native_result",
        "completed execution requires one native result",
      );
    }
    return null;
  }

  if (nativeResult !== null) {
    return protocolFailure(
      "NONCOMPLETED_NATIVE_PRESENT",
      "$.native_result",
      `${execution.status} execution forbids a native result`,
    );
  }

  if (execution.status === "blocked") {
    if (
      execution.timed_out ||
      execution.failure_kind !== "policy-block" ||
      execution.exit_code !== null
    ) {
      return protocolFailure(
        "BLOCKED_EXECUTION_ALGEBRA_INVALID",
        "$.execution",
        "blocked requires timed_out=false, failure_kind=policy-block, and exit_code=null",
      );
    }
    return null;
  }

  if (execution.status === "failed") {
    const validFailure = execution.timed_out
      ? execution.failure_kind === "timeout"
      : execution.failure_kind === "process-error" ||
        execution.failure_kind === "invalid-output" ||
        execution.failure_kind === "missing-output";
    if (!validFailure) {
      return protocolFailure(
        "FAILED_EXECUTION_ALGEBRA_INVALID",
        "$.execution",
        "failed execution must use timeout iff timed_out, otherwise one process/output failure kind",
      );
    }
    return null;
  }

  if (execution.status === "stale") {
    if (
      execution.timed_out ||
      execution.failure_kind !== "stale-input" ||
      execution.exit_code !== null
    ) {
      return protocolFailure(
        "STALE_EXECUTION_ALGEBRA_INVALID",
        "$.execution",
        "stale requires timed_out=false, failure_kind=stale-input, and exit_code=null",
      );
    }
    return null;
  }

  return protocolFailure(
    "FAILED_EXECUTION_ALGEBRA_INVALID",
    "$.execution.status",
    `unsupported execution status ${execution.status}`,
  );
}

function validateWitness(
  input: ProtocolMappingInput,
): SmtProtocolResult<never> | null {
  const sat =
    input.execution.status === "completed" &&
    input.native_result?.outcome === "sat";
  if (sat && input.witness === null) {
    return protocolFailure(
      "SAT_WITNESS_REQUIRED",
      "$.witness",
      "completed SAT requires one receipt-bound witness",
    );
  }
  if (!sat && input.witness !== null) {
    return protocolFailure(
      "NON_SAT_WITNESS_FORBIDDEN",
      "$.witness",
      "witness is forbidden unless execution is completed SAT",
    );
  }
  if (input.witness === null || input.native_result === null) {
    return null;
  }

  const witnessWithoutDigest = {
    model_ref: input.witness.model_ref,
    request_ref: input.witness.request_ref,
    translated_query_digest: input.witness.translated_query_digest,
    runtime_manifest_ref: input.witness.runtime_manifest_ref,
    execution_run_id: input.witness.execution_run_id,
    native_result_digest: input.witness.native_result_digest,
  };
  const matches =
    input.witness.request_ref === input.request.request_id &&
    input.witness.translated_query_digest ===
      input.translation.translated_query_digest &&
    input.witness.runtime_manifest_ref ===
      input.request.runtime_manifest_ref.path &&
    input.witness.execution_run_id === input.execution.run_id &&
    input.witness.native_result_digest === input.native_result.result_digest &&
    input.witness.bindings_digest ===
      witnessBindingsDigest(witnessWithoutDigest);
  if (!matches) {
    return protocolFailure(
      "SAT_WITNESS_BINDING_MISMATCH",
      "$.witness",
      "witness fields and canonical bindings digest must bind the containing request, query, runtime, execution, and native result",
    );
  }
  return null;
}

function normalize(
  queryKind: QueryKind,
  execution: ExecutionTuple,
  nativeResult: NativeResult | null,
): NormalizedOutcome {
  if (execution.status !== "completed" || nativeResult === null) {
    return "unresolved";
  }
  if (nativeResult.outcome === "unknown") {
    return "unresolved";
  }
  if (queryKind === "counterexample") {
    return nativeResult.outcome === "sat"
      ? "counterexample"
      : "no-counterexample";
  }
  return nativeResult.outcome === "sat" ? "witness" : "no-witness";
}

function claimFor(
  origin: EvidenceOrigin,
  execution: ExecutionTuple,
  nativeResult: NativeResult | null,
): SmtClaimCeiling {
  if (origin === SYNTHETIC_ORIGIN) {
    return SYNTHETIC_CLAIM;
  }
  return execution.status === "completed" &&
    nativeResult !== null &&
    nativeResult.outcome !== "unknown"
    ? OBSERVED_CLAIM
    : NO_PROPERTY_CLAIM;
}

function requestRefs(
  request: FormalObligationRequest,
): readonly ExactArtifactRef[] {
  return [
    request.semantic_source_ref,
    request.formal_obligation_ref,
    request.theory_profile_ref,
    request.symbol_table_ref,
    request.assumptions_ref,
    request.translation_contract_ref,
    request.runtime_manifest_ref,
  ];
}

function receiptRef(reference: ExactArtifactRef): ExactArtifactRef {
  return Object.freeze({
    path: reference.path,
    sha256: reference.sha256,
    size_bytes: reference.size_bytes,
  });
}

function protocolSuccess<T>(value: T): SfolContractSuccess<T> {
  const result = contractSuccess(value);
  if (!result.ok) {
    throw new Error("contractSuccess returned a failure variant");
  }
  return result;
}

function protocolFailure<T>(
  code: SmtProtocolDiagnosticCode,
  path: string,
  detail: string,
): SmtProtocolResult<T> {
  return Object.freeze({
    ok: false,
    diagnostics: Object.freeze([
      Object.freeze({ code, stage: "contract" as const, path, detail }),
    ]),
  });
}

function sha256(value: string): string {
  return createHash("sha256").update(value).digest("hex");
}
