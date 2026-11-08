import { canonicalJson, digestValue } from "./canonical-json.js";
import { fail, type ExactRef, type NormalizedOutcome, type ProviderReceipt } from "./types.js";

export type ProviderReceiptBindings = {
  readonly receipt_id: string;
  readonly request_id: string;
  readonly request_ref: ExactRef;
  readonly fact_manifest_ref: ExactRef;
  readonly property_definition_ref: ExactRef;
  readonly comparison_contract_ref: ExactRef;
  readonly scope_contract_ref: ExactRef;
  readonly facts_digest: string;
  readonly universe_digest: string;
  readonly selected_relation_digest: string;
  readonly scope_digest: string;
  readonly property_id: string;
  readonly property_version: string;
  readonly provider: ProviderReceipt["provider"];
  readonly translation: ProviderReceipt["translation"];
  readonly execution: ProviderReceipt["execution"];
  readonly native_result: ProviderReceipt["native_result"];
  readonly normalized_outcome: NormalizedOutcome;
  readonly evidence_refs: readonly ExactRef[];
  readonly residue?: readonly Readonly<Record<string, unknown>>[];
};

function semanticMaterial(receipt: Omit<ProviderReceipt, "semantic_result_digest">) {
  return {
    request_id: receipt.request_id,
    facts_digest: receipt.facts_digest,
    universe_digest: receipt.universe_digest,
    selected_relation_digest: receipt.selected_relation_digest,
    scope_digest: receipt.scope_digest,
    property_id: receipt.property_id,
    property_version: receipt.property_version,
    provider: receipt.provider,
    translation: receipt.translation,
    native_result: receipt.native_result,
    normalized_result: receipt.normalized_result,
    claim_ceiling: receipt.claim_ceiling,
  };
}

export function buildProviderReceipt(bindings: ProviderReceiptBindings): ProviderReceipt {
  if (
    bindings.execution.status !== "completed" ||
    bindings.execution.exit_code !== 0 ||
    bindings.execution.timed_out
  ) {
    fail("PROVIDER_EXECUTION_FAILED", "mapping", "non-completed process cannot make a property claim");
  }
  if (bindings.evidence_refs.length === 0) {
    fail("PROVIDER_OUTPUT_INVALID", "mapping", "provider receipt needs native evidence");
  }
  const resultPayload = {
    outcome: bindings.normalized_outcome,
    domain_kind: "exact-closed-world-fact-set" as const,
    evaluation_mode: "exact-instance" as const,
    evidence_refs: bindings.evidence_refs,
  };
  const withoutDigest: Omit<ProviderReceipt, "semantic_result_digest"> = {
    schema_version: "evf.graph-law-provider-receipt/v1",
    receipt_id: bindings.receipt_id,
    receipt_family: bindings.provider.kind === "datalog"
      ? "graph-relation"
      : "formal-static",
    request_ref: bindings.request_ref,
    fact_manifest_ref: bindings.fact_manifest_ref,
    property_definition_ref: bindings.property_definition_ref,
    comparison_contract_ref: bindings.comparison_contract_ref,
    scope_contract_ref: bindings.scope_contract_ref,
    request_id: bindings.request_id,
    facts_digest: bindings.facts_digest,
    universe_digest: bindings.universe_digest,
    selected_relation_digest: bindings.selected_relation_digest,
    scope_digest: bindings.scope_digest,
    property_id: bindings.property_id,
    property_version: bindings.property_version,
    provider: bindings.provider,
    translation: bindings.translation,
    execution: bindings.execution,
    native_result: bindings.native_result,
    normalized_result: {
      ...resultPayload,
      result_payload_digest: digestValue(resultPayload),
    },
    residue: bindings.residue ?? [],
    authority_effect: "none",
    release_admission: "not-granted",
    claim_ceiling: bindings.provider.kind === "datalog"
      ? "exact-finite-corpus-relation-result-only"
      : "bounded-static-model-result-only",
  };
  return {
    ...withoutDigest,
    semantic_result_digest: digestValue(semanticMaterial(withoutDigest)),
  };
}

export function verifyProviderReceipt(receipt: ProviderReceipt): ProviderReceipt {
  if (
    receipt.schema_version !== "evf.graph-law-provider-receipt/v1" ||
    receipt.execution.status !== "completed" ||
    receipt.execution.exit_code !== 0 ||
    receipt.execution.timed_out ||
    receipt.authority_effect !== "none" ||
    receipt.release_admission !== "not-granted" ||
    (receipt.provider.kind === "datalog" && receipt.receipt_family !== "graph-relation") ||
    (receipt.provider.kind === "alloy" && receipt.receipt_family !== "formal-static")
  ) {
    fail("PROVIDER_RECEIPT_TAMPERED", "mapping", "provider receipt topology is invalid");
  }
  const payload = {
    outcome: receipt.normalized_result.outcome,
    domain_kind: receipt.normalized_result.domain_kind,
    evaluation_mode: receipt.normalized_result.evaluation_mode,
    evidence_refs: receipt.normalized_result.evidence_refs,
  };
  if (
    digestValue(payload) !== receipt.normalized_result.result_payload_digest ||
    digestValue(semanticMaterial(receipt)) !== receipt.semantic_result_digest
  ) {
    fail("PROVIDER_RECEIPT_TAMPERED", "mapping", "provider semantic digest mismatch");
  }
  if (
    receipt.provider.kind === "datalog" &&
    receipt.native_result.kind !== "violation-relation"
  ) {
    fail("PROVIDER_RESULT_UNMAPPED", "mapping", "Datalog receipt has non-Datalog native result");
  }
  if (
    receipt.provider.kind === "datalog" &&
    receipt.native_result.kind === "violation-relation"
  ) {
    const expected = receipt.native_result.row_count === 0
      ? "no-counterexample"
      : "counterexample";
    if (
      !receipt.native_result.complete ||
      receipt.normalized_result.outcome !== expected
    ) {
      fail("PROVIDER_RESULT_UNMAPPED", "mapping", "Datalog row count and normalized outcome disagree");
    }
  }
  if (
    receipt.provider.kind === "alloy" &&
    receipt.native_result.kind !== "alloy-command"
  ) {
    fail("PROVIDER_RESULT_UNMAPPED", "mapping", "Alloy receipt has non-Alloy native result");
  }
  if (
    receipt.provider.kind === "alloy" &&
    receipt.native_result.kind === "alloy-command"
  ) {
    const expected = receipt.native_result.outcome === "sat"
      ? "counterexample"
      : receipt.native_result.outcome === "unsat"
        ? "no-counterexample"
        : "unresolved";
    const evidenceValid = receipt.native_result.outcome === "sat"
      ? receipt.native_result.instance_or_counterexample_ref !== null &&
        (receipt.native_result.solution_count ?? 0) > 0
      : receipt.native_result.instance_or_counterexample_ref === null &&
        (receipt.native_result.outcome !== "unsat" ||
          (receipt.native_result.solution_count ?? 0) === 0);
    if (receipt.normalized_result.outcome !== expected || !evidenceValid) {
      fail("PROVIDER_RESULT_UNMAPPED", "mapping", "Alloy native evidence and normalized outcome disagree");
    }
  }
  return receipt;
}

export function providerReceiptEqual(left: ProviderReceipt, right: ProviderReceipt): boolean {
  return canonicalJson(left) === canonicalJson(right);
}
