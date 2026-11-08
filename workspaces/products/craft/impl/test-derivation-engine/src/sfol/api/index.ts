import { digestSfolValue } from "../cases/index.js";
import type { ClauseDenominator } from "../denominator/index.js";
import { decodeNodeLogicModule } from "../language/decoder.js";
import type { NodeLogicModuleV1 } from "../language/ast.js";
import { typecheckLogicModule } from "../language/typecheck.js";
import {
  evaluateNegativeControls,
  type NegativeControlEvaluationInput,
  type NegativeControlEvaluationResult,
} from "../negative-controls/index.js";
import type { DetectionMatrixReceipt } from "../negative-controls/index.js";
import {
  derivePureFixtures,
  type PartitionDomain,
  type PartitionRuleSet,
  type PureFixtureDerivationResult,
} from "../partitions/index.js";
import {
  replayPureProofReceipt,
  type PureProofBuildInput,
  type PureProofReceipt,
  type PureReplayAllowlist,
  type PureReplayResult,
} from "../proof/index.js";

export const SFOL_TDE_API_VERSION = "domainspec-sfol-tde-api/v1" as const;
export const SFOL_TDE_OPTIONAL_EVF_API_VERSION = "domainspec-sfol-tde-api/v2" as const;

export interface DerivePartitionsRequest {
  readonly api_version: typeof SFOL_TDE_API_VERSION;
  readonly module: unknown;
  readonly denominator: ClauseDenominator;
  readonly ruleset: PartitionRuleSet;
  readonly domain?: PartitionDomain;
}

export type DerivePartitionsResponse =
  | PureFixtureDerivationResult
  | {
      readonly ok: false;
      readonly diagnostics: readonly {
        readonly code: "SFOL_API_DECODE_FAILED" | "SFOL_API_TYPECHECK_FAILED" | "SFOL_API_VERSION_UNSUPPORTED";
        readonly stage: "api";
        readonly subject: string;
        readonly detail: string;
      }[];
    };

export interface ReplayPureRequest {
  readonly api_version: typeof SFOL_TDE_API_VERSION;
  readonly receipt: PureProofReceipt;
  readonly input: PureProofBuildInput;
  readonly allowlist: PureReplayAllowlist;
}

export type ReceiptVerificationResult =
  | { readonly ok: true; readonly value: { readonly receipt_digest: string } }
  | { readonly ok: false; readonly diagnostics: readonly { readonly code: "SFOL_RECEIPT_INVALID"; readonly stage: "verify"; readonly subject: string; readonly detail: string }[] };

export interface CloseTestClosureV1Request {
  readonly api_version: typeof SFOL_TDE_API_VERSION;
  readonly proof_receipt: unknown;
  readonly detection_matrix: DetectionMatrixReceipt;
  readonly migration_boundary_digest?: string;
}

export interface CloseTestClosureV2Request {
  readonly api_version: typeof SFOL_TDE_OPTIONAL_EVF_API_VERSION;
  readonly proof_receipt: unknown;
  readonly detection_matrix?: DetectionMatrixReceipt;
  readonly migration_boundary_digest?: string;
}

export type CloseTestClosureRequest = CloseTestClosureV1Request | CloseTestClosureV2Request;

export type CloseTestClosureResult =
  | { readonly ok: true; readonly value: { readonly schema_version: "domainspec-sfol-test-closure-receipt/v1"; readonly status: "pass"; readonly proof_receipt_digest: string; readonly detection_matrix_digest: string; readonly migration_boundary_digest: string | null; readonly receipt_digest: string } }
  | { readonly ok: true; readonly value: { readonly schema_version: "domainspec-sfol-test-closure-receipt/v2"; readonly status: "pass"; readonly proof_receipt_digest: string; readonly evf_status: "not_requested" | "passed"; readonly detection_matrix_digest: string | null; readonly migration_boundary_digest: string | null; readonly receipt_digest: string } }
  | { readonly ok: false; readonly diagnostics: readonly { readonly code: "SFOL_TEST_CLOSURE_INCOMPLETE"; readonly stage: "close"; readonly subject: string; readonly detail: string }[] };

export function derivePartitions(request: DerivePartitionsRequest): DerivePartitionsResponse {
  if (request.api_version !== SFOL_TDE_API_VERSION) return apiFailure("SFOL_API_VERSION_UNSUPPORTED", "api_version", `expected ${SFOL_TDE_API_VERSION}`);
  const decoded = decodeNodeLogicModule(request.module);
  if (!decoded.ok) return apiFailure("SFOL_API_DECODE_FAILED", "module", decoded.diagnostics[0]?.detail ?? "module decode failed");
  const typed = typecheckLogicModule(decoded.value);
  if (!typed.ok) return apiFailure("SFOL_API_TYPECHECK_FAILED", "module", typed.diagnostics[0]?.detail ?? "module typecheck failed");
  return derivePureFixtures({
    typed: typed.value,
    typed_module_digest: digestSfolValue(typed.value.source),
    typed_clause_digests: Object.fromEntries(typed.value.source.clauses.map((clause) => [clause.clause_id, digestSfolValue(clause)])),
    denominator: request.denominator,
    ruleset: request.ruleset,
    domain: request.domain,
  });
}

export function challengeTestClosure(request: NegativeControlEvaluationInput): NegativeControlEvaluationResult {
  return evaluateNegativeControls(request);
}

export function closeTestClosure(request: CloseTestClosureRequest): CloseTestClosureResult {
  if (request.api_version !== SFOL_TDE_API_VERSION && request.api_version !== SFOL_TDE_OPTIONAL_EVF_API_VERSION) {
    return closureFailure("api_version", `expected ${SFOL_TDE_API_VERSION} or ${SFOL_TDE_OPTIONAL_EVF_API_VERSION}`);
  }
  const proof = verifyContentAddressedReceipt(request.proof_receipt);
  if (!proof.ok) return closureFailure("proof_receipt", proof.diagnostics[0]?.detail ?? "proof receipt is invalid");
  if (request.migration_boundary_digest !== undefined && !/^[0-9a-f]{64}$/.test(request.migration_boundary_digest)) return closureFailure("migration_boundary_digest", "migration boundary digest must be lowercase SHA-256");
  if (request.api_version === SFOL_TDE_API_VERSION) {
    const detection = verifyContentAddressedReceipt(request.detection_matrix);
    if (!detection.ok || request.detection_matrix.result !== "pass") return closureFailure("detection_matrix", "a content-valid passing detection matrix is required");
    const unsigned = { schema_version: "domainspec-sfol-test-closure-receipt/v1" as const, status: "pass" as const, proof_receipt_digest: proof.value.receipt_digest, detection_matrix_digest: detection.value.receipt_digest, migration_boundary_digest: request.migration_boundary_digest ?? null };
    return Object.freeze({ ok: true, value: Object.freeze({ ...unsigned, receipt_digest: digestSfolValue(unsigned) }) });
  }
  let evfStatus: "not_requested" | "passed" = "not_requested";
  let detectionMatrixDigest: string | null = null;
  if (request.detection_matrix !== undefined) {
    const detection = verifyContentAddressedReceipt(request.detection_matrix);
    if (!detection.ok || request.detection_matrix.result !== "pass") return closureFailure("detection_matrix", "when EVF is requested, a content-valid passing detection matrix is required");
    evfStatus = "passed";
    detectionMatrixDigest = detection.value.receipt_digest;
  }
  const unsigned = { schema_version: "domainspec-sfol-test-closure-receipt/v2" as const, status: "pass" as const, proof_receipt_digest: proof.value.receipt_digest, evf_status: evfStatus, detection_matrix_digest: detectionMatrixDigest, migration_boundary_digest: request.migration_boundary_digest ?? null };
  return Object.freeze({ ok: true, value: Object.freeze({ ...unsigned, receipt_digest: digestSfolValue(unsigned) }) });
}

export function replayPure(request: ReplayPureRequest): PureReplayResult {
  if (request.api_version !== SFOL_TDE_API_VERSION) {
    return { ok: false, diagnostics: [{ code: "SFOL_REPLAY_NOT_ALLOWLISTED", stage: "replay", subject: "api_version", detail: `expected ${SFOL_TDE_API_VERSION}` }] };
  }
  return replayPureProofReceipt(request.receipt, request.input, request.allowlist);
}

export function verifyContentAddressedReceipt(receipt: unknown): ReceiptVerificationResult {
  if (typeof receipt !== "object" || receipt === null || Array.isArray(receipt)) return receiptFailure("receipt must be an object");
  const record = receipt as Record<string, unknown>;
  if (typeof record.receipt_digest !== "string" || !/^[0-9a-f]{64}$/.test(record.receipt_digest)) return receiptFailure("receipt_digest must be a lowercase SHA-256 digest");
  const { receipt_digest: expected, ...unsigned } = record;
  if (digestSfolValue(unsigned) !== expected) return receiptFailure("receipt content does not match receipt_digest");
  return Object.freeze({ ok: true, value: Object.freeze({ receipt_digest: expected }) });
}

export function decodeAndTypecheckModule(module: unknown):
  | { readonly ok: true; readonly value: NodeLogicModuleV1 }
  | Exclude<DerivePartitionsResponse, { readonly ok: true }> {
  const decoded = decodeNodeLogicModule(module);
  if (!decoded.ok) return apiFailure("SFOL_API_DECODE_FAILED", "module", decoded.diagnostics[0]?.detail ?? "module decode failed");
  const typed = typecheckLogicModule(decoded.value);
  if (!typed.ok) return apiFailure("SFOL_API_TYPECHECK_FAILED", "module", typed.diagnostics[0]?.detail ?? "module typecheck failed");
  return { ok: true, value: typed.value.source };
}

function apiFailure(code: "SFOL_API_DECODE_FAILED" | "SFOL_API_TYPECHECK_FAILED" | "SFOL_API_VERSION_UNSUPPORTED", subject: string, detail: string) {
  return Object.freeze({ ok: false as const, diagnostics: Object.freeze([Object.freeze({ code, stage: "api" as const, subject, detail })]) });
}

function receiptFailure(detail: string): ReceiptVerificationResult {
  return Object.freeze({ ok: false, diagnostics: Object.freeze([Object.freeze({ code: "SFOL_RECEIPT_INVALID" as const, stage: "verify" as const, subject: "receipt", detail })]) });
}

function closureFailure(subject: string, detail: string): CloseTestClosureResult {
  return Object.freeze({ ok: false, diagnostics: Object.freeze([Object.freeze({ code: "SFOL_TEST_CLOSURE_INCOMPLETE" as const, stage: "close" as const, subject, detail })]) });
}
