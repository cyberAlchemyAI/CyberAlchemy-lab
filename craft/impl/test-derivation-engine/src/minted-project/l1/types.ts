export const L1_ERROR_CODES = [
  "TARGET_BASELINE_DRIFT",
  "CREATE_TARGET_COLLISION",
  "SOURCE_GRAPH_DIGEST_STALE",
  "SOURCE_MANIFEST_INCOMPLETE",
  "RULE_IDENTITY_COLLAPSED",
  "EDGE_ID_DUPLICATE",
  "EDGE_ENDPOINT_MISMATCH",
  "RELATIONSHIP_SIGNATURE_MISMATCH",
  "OBLIGATION_MISMATCH",
  "PREDICATE_DIGEST_STALE",
  "BINDING_DIGEST_STALE",
  "FIXTURE_DIGEST_STALE",
  "P4_WRITE_MISSING",
  "P4_EVENT_MISSING",
  "P4_EFFECT_ORDER_MISMATCH",
  "P4_EFFECT_CARDINALITY_MISMATCH",
  "P4_WRITE_AMOUNT_MISMATCH",
  "P4_EVENT_AMOUNT_MISMATCH",
  "P4_WRITE_DATE_MISMATCH",
  "P4_EVENT_DATE_MISMATCH",
  "R4_RESULT_MISMATCH",
  "R4_CONTROL_MISMATCH",
  "OBSERVATION_TAMPERED",
  "RECEIPT_TAMPERED",
  "VERIFIER_TARGET_OMITTED",
  "UNDECLARED_WRITE",
  "HIDDEN_RESIDUE",
  "CLAIM_INFLATION",
] as const;

export type L1ErrorCode = (typeof L1_ERROR_CODES)[number];
export type L1Phase = "admission" | "derivation" | "binding" | "execution" | "mutation" | "receipt" | "aggregate";

export class L1Error extends Error {
  readonly exitCode: 1 | 2;

  constructor(
    readonly code: L1ErrorCode,
    readonly phase: L1Phase,
    message: string,
    exitCode: 1 | 2 = 1,
  ) {
    super(message);
    this.name = "L1Error";
    this.exitCode = exitCode;
  }
}

export function fail(
  code: L1ErrorCode,
  phase: L1Phase,
  message: string,
  exitCode: 1 | 2 = 1,
): never {
  throw new L1Error(code, phase, message, exitCode);
}

export type ExactRef = {
  readonly path: string;
  readonly sha256: string;
  readonly size_bytes: number;
};

export type GraphHandle = {
  readonly graph_ref: ExactRef;
  readonly source_manifest_ref: ExactRef;
  readonly source_set_digest: string;
  readonly profile_digest: string;
  readonly kinds_digest: string;
  readonly relationships_digest: string;
  readonly handle_digest: string;
};

export type L1Obligation = {
  readonly obligation_id: string;
  readonly rule_id: string;
  readonly edge_id: string;
  readonly relationship: "enforces";
  readonly target_id: "financial-settlement.GenerateSettlement";
  readonly contract_kind: "ordered-effect-implication" | "pure-decision-truth-table";
  readonly semantic_contract: Readonly<Record<string, unknown>>;
  readonly excluded_claims: readonly string[];
};

export type L1Identity = {
  readonly rule_id: string;
  readonly edge_id: string;
  readonly obligation_id: string;
  readonly binding_id: string;
  readonly test_id: string;
  readonly execution_id: string;
  readonly receipt_id: string;
};

export const P4_IDENTITY: L1Identity = {
  rule_id: "financial-settlement.PayoutEligibilityRule",
  edge_id: "financial-settlement.edge.payout-rule-enforces-generation",
  obligation_id: "evf.l1.financial-settlement.p4.obligation.v1",
  binding_id: "evf.l1.financial-settlement.p4.binding.v1",
  test_id: "evf.l1.financial-settlement.p4.test.v1",
  execution_id: "evf.l1.financial-settlement.p4.execution.v1",
  receipt_id: "evf.l1.financial-settlement.p4.receipt.v1",
};

export const R4_IDENTITY: L1Identity = {
  rule_id: "financial-settlement.NoDuplicateMakeupRule",
  edge_id: "financial-settlement.edge.no-duplicate-makeup-rule-enforces-generation",
  obligation_id: "evf.l1.financial-settlement.r4.obligation.v1",
  binding_id: "evf.l1.financial-settlement.r4.binding.v1",
  test_id: "evf.l1.financial-settlement.r4.test.v1",
  execution_id: "evf.l1.financial-settlement.r4.execution.v1",
  receipt_id: "evf.l1.financial-settlement.r4.receipt.v1",
};

export type P4Effect = {
  readonly sequence: number;
  readonly kind: "write" | "event";
  readonly name: "PAYOUT" | "PayoutCreated";
  readonly amount: number;
  readonly date: string;
};

export type P4Execution = {
  readonly schema_version: "evf.financial-settlement-p4-execution/v1";
  readonly execution_id: typeof P4_IDENTITY.execution_id;
  readonly fixture_id: "evf.l1.financial-settlement.p4.fixture.v1";
  readonly antecedent: {
    readonly total_payout: number;
    readonly existing_payout_count: number;
    readonly end_date: string;
  };
  readonly post: {
    readonly payout_write_count: number;
    readonly payout_event_count: number;
  };
  readonly effects: readonly P4Effect[];
  readonly resources: {
    readonly opened: readonly string[];
    readonly closed: readonly string[];
  };
  readonly status: "pass";
};

export type UnitReceipt = {
  readonly schema_version: "evf.financial-settlement-l1-receipt/v1";
  readonly receipt_id: string;
  readonly unit_id: "SWU-GCP-002-P4" | "SWU-GCP-003-R4";
  readonly status: "pass";
  readonly identities: L1Identity;
  readonly graph_handle: GraphHandle;
  readonly evidence_refs: readonly ExactRef[];
  readonly acceptance_vector: Readonly<Record<string, number>>;
  readonly claim_ceiling: string;
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
  readonly receipt_digest: string;
};

export type DerivationResult = {
  readonly unit: "P4" | "R4";
  readonly identity: L1Identity;
  readonly graph_handle: GraphHandle;
  readonly O_spec: L1Obligation;
  readonly O_gen: L1Obligation;
  readonly comparison: "equal";
};
