import { assertExactRef, digestValue } from "./exact-ref.js";
import {
  fail,
  P4_IDENTITY,
  R4_IDENTITY,
  type ExactRef,
  type GraphHandle,
  type L1Identity,
  type UnitReceipt,
} from "./types.js";

export const P4_CLAIM_CEILING =
  "candidate-local-financial-settlement-p4-one-way-ordered-effect-only";
export const R4_CLAIM_CEILING =
  "candidate-local-financial-settlement-r4-pure-duplicate-makeup-decision-only";
export const COMPOSITE_CLAIM_CEILING =
  "candidate-local-two-distinct-financial-settlement-rule-slices-over-one-frozen-graph-source-handle-only";

function unsignedReceipt(receipt: UnitReceipt): Omit<UnitReceipt, "receipt_digest"> {
  const { receipt_digest: _digest, ...unsigned } = receipt;
  return unsigned;
}

export function buildUnitReceipt(input: {
  readonly unit: "P4" | "R4";
  readonly graphHandle: GraphHandle;
  readonly evidenceRefs: readonly ExactRef[];
  readonly acceptanceVector: Readonly<Record<string, number>>;
}): UnitReceipt {
  const p4 = input.unit === "P4";
  const identities = p4 ? P4_IDENTITY : R4_IDENTITY;
  const unsigned = {
    schema_version: "evf.financial-settlement-l1-receipt/v1" as const,
    receipt_id: identities.receipt_id,
    unit_id: p4 ? "SWU-GCP-002-P4" as const : "SWU-GCP-003-R4" as const,
    status: "pass" as const,
    identities,
    graph_handle: input.graphHandle,
    evidence_refs: [...input.evidenceRefs],
    acceptance_vector: input.acceptanceVector,
    claim_ceiling: p4 ? P4_CLAIM_CEILING : R4_CLAIM_CEILING,
    authority_effect: "none" as const,
    release_admission: "not-granted" as const,
  };
  return { ...unsigned, receipt_digest: digestValue(unsigned) };
}

function sameIdentity(actual: L1Identity, expected: L1Identity): boolean {
  return Object.keys(expected).every(
    (key) => actual[key as keyof L1Identity] === expected[key as keyof L1Identity],
  );
}

export function verifyUnitReceipt(repoRoot: string, receipt: UnitReceipt): void {
  const expected = receipt.unit_id === "SWU-GCP-002-P4" ? P4_IDENTITY : R4_IDENTITY;
  const ceiling = receipt.unit_id === "SWU-GCP-002-P4" ? P4_CLAIM_CEILING : R4_CLAIM_CEILING;
  if (
    receipt.schema_version !== "evf.financial-settlement-l1-receipt/v1" ||
    receipt.status !== "pass" ||
    receipt.receipt_id !== expected.receipt_id ||
    !sameIdentity(receipt.identities, expected)
  ) {
    fail("RECEIPT_TAMPERED", "receipt", "unit receipt identity is invalid");
  }
  if (
    receipt.claim_ceiling !== ceiling ||
    receipt.authority_effect !== "none" ||
    receipt.release_admission !== "not-granted"
  ) {
    fail("CLAIM_INFLATION", "receipt", "unit receipt exceeds its candidate-local claim ceiling");
  }
  if (receipt.receipt_digest !== digestValue(unsignedReceipt(receipt))) {
    fail("RECEIPT_TAMPERED", "receipt", "unit receipt digest is invalid");
  }
  const handlePayload = {
    graph_ref: receipt.graph_handle.graph_ref,
    source_manifest_ref: receipt.graph_handle.source_manifest_ref,
    source_set_digest: receipt.graph_handle.source_set_digest,
    profile_digest: receipt.graph_handle.profile_digest,
    kinds_digest: receipt.graph_handle.kinds_digest,
    relationships_digest: receipt.graph_handle.relationships_digest,
  };
  if (receipt.graph_handle.handle_digest !== digestValue(handlePayload)) {
    fail("RECEIPT_TAMPERED", "receipt", "graph/source handle digest is invalid");
  }
  assertExactRef(repoRoot, receipt.graph_handle.graph_ref, "SOURCE_GRAPH_DIGEST_STALE");
  assertExactRef(repoRoot, receipt.graph_handle.source_manifest_ref, "SOURCE_GRAPH_DIGEST_STALE");
  if (receipt.evidence_refs.length < 5) {
    fail("RECEIPT_TAMPERED", "receipt", "unit receipt evidence denominator is incomplete");
  }
  for (const ref of receipt.evidence_refs) assertExactRef(repoRoot, ref, "RECEIPT_TAMPERED");
}

export type CompositeReceipt = {
  readonly schema_version: "evf.financial-settlement-l1-composite-receipt/v1";
  readonly receipt_id: "evf.l1.financial-settlement.composite.receipt.v1";
  readonly status: "pass";
  readonly unit_receipts: { readonly p4: ExactRef; readonly r4: ExactRef };
  readonly identity_denominators: {
    readonly rule_ids: readonly string[];
    readonly edge_ids: readonly string[];
    readonly obligation_ids: readonly string[];
    readonly binding_ids: readonly string[];
    readonly test_ids: readonly string[];
    readonly execution_ids: readonly string[];
    readonly receipt_ids: readonly string[];
  };
  readonly shared_handle_digest: string;
  readonly join_checks: {
    readonly distinct_identities: true;
    readonly same_graph_source_handle: true;
    readonly both_unit_receipts_terminal: true;
    readonly semantic_merge_forbidden: true;
    readonly provider_precedence_forbidden: true;
    readonly claim_inflation_forbidden: true;
  };
  readonly claim_ceiling: typeof COMPOSITE_CLAIM_CEILING;
  readonly authority_effect: "none";
  readonly release_admission: "not-granted";
  readonly receipt_digest: string;
};

export function buildCompositeReceipt(input: {
  readonly p4: UnitReceipt;
  readonly r4: UnitReceipt;
  readonly p4Ref: ExactRef;
  readonly r4Ref: ExactRef;
}): CompositeReceipt {
  if (input.p4.unit_id !== "SWU-GCP-002-P4" || input.r4.unit_id !== "SWU-GCP-003-R4") {
    fail("RECEIPT_TAMPERED", "aggregate", "composite unit receipt roles are invalid");
  }
  if (input.p4.graph_handle.handle_digest !== input.r4.graph_handle.handle_digest) {
    fail("SOURCE_GRAPH_DIGEST_STALE", "aggregate", "P4 and R4 do not share one frozen graph/source handle");
  }
  const identitySets = {
    rule_ids: [input.p4.identities.rule_id, input.r4.identities.rule_id],
    edge_ids: [input.p4.identities.edge_id, input.r4.identities.edge_id],
    obligation_ids: [input.p4.identities.obligation_id, input.r4.identities.obligation_id],
    binding_ids: [input.p4.identities.binding_id, input.r4.identities.binding_id],
    test_ids: [input.p4.identities.test_id, input.r4.identities.test_id],
    execution_ids: [input.p4.identities.execution_id, input.r4.identities.execution_id],
    receipt_ids: [input.p4.identities.receipt_id, input.r4.identities.receipt_id],
  };
  if (Object.values(identitySets).some((set) => new Set(set).size !== 2)) {
    fail("RULE_IDENTITY_COLLAPSED", "aggregate", "composite identities are not distinct");
  }
  const unsigned = {
    schema_version: "evf.financial-settlement-l1-composite-receipt/v1" as const,
    receipt_id: "evf.l1.financial-settlement.composite.receipt.v1" as const,
    status: "pass" as const,
    unit_receipts: { p4: input.p4Ref, r4: input.r4Ref },
    identity_denominators: identitySets,
    shared_handle_digest: input.p4.graph_handle.handle_digest,
    join_checks: {
      distinct_identities: true as const,
      same_graph_source_handle: true as const,
      both_unit_receipts_terminal: true as const,
      semantic_merge_forbidden: true as const,
      provider_precedence_forbidden: true as const,
      claim_inflation_forbidden: true as const,
    },
    claim_ceiling: COMPOSITE_CLAIM_CEILING as typeof COMPOSITE_CLAIM_CEILING,
    authority_effect: "none" as const,
    release_admission: "not-granted" as const,
  };
  return { ...unsigned, receipt_digest: digestValue(unsigned) };
}

export function verifyCompositeReceipt(receipt: CompositeReceipt): void {
  const { receipt_digest: digest, ...unsigned } = receipt;
  if (digest !== digestValue(unsigned)) {
    fail("RECEIPT_TAMPERED", "aggregate", "composite receipt digest is invalid");
  }
  if (
    receipt.claim_ceiling !== COMPOSITE_CLAIM_CEILING ||
    receipt.authority_effect !== "none" ||
    receipt.release_admission !== "not-granted"
  ) {
    fail("CLAIM_INFLATION", "aggregate", "composite claim ceiling is invalid");
  }
}
