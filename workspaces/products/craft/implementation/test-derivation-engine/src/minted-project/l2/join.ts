import { canonicalJson, digestValue } from "./canonical-json.js";
import { verifyProviderReceipt } from "./provider-receipt.js";
import { fail, type ExactRef, type JoinReceipt, type NormalizedOutcome, type ProviderReceipt } from "./types.js";

const sameRef = (left: ExactRef, right: ExactRef): boolean =>
  canonicalJson(left) === canonicalJson(right);

function valid(receipt: ProviderReceipt): boolean {
  try {
    verifyProviderReceipt(receipt);
    return true;
  } catch {
    return false;
  }
}

function expectedJoin(
  comparable: boolean,
  datalog: NormalizedOutcome,
  alloy: NormalizedOutcome,
): Pick<JoinReceipt, "join_status" | "consistency_class"> {
  if (!comparable) {
    return { join_status: "blocked", consistency_class: "not-comparable" };
  }
  if (datalog === "unresolved" || alloy === "unresolved" || datalog !== alloy) {
    return { join_status: "unresolved", consistency_class: "provider-disagreement" };
  }
  return datalog === "counterexample"
    ? { join_status: "consistent", consistency_class: "counterexample-consistent" }
    : {
        join_status: "consistent",
        consistency_class: "no-counterexample-consistent-under-declared-bounds",
      };
}

function payload(receipt: Omit<JoinReceipt, "join_payload_digest">): unknown {
  return receipt;
}

export function buildJoinReceipt(input: {
  readonly joinReceiptId: string;
  readonly datalog: ProviderReceipt;
  readonly alloy: ProviderReceipt;
  readonly datalogRef: ExactRef;
  readonly alloyRef: ExactRef;
  readonly evidenceRefs?: readonly ExactRef[];
}): JoinReceipt {
  const { datalog, alloy } = input;
  const preflight = {
    same_request:
      datalog.request_id === alloy.request_id &&
      sameRef(datalog.request_ref, alloy.request_ref),
    same_facts:
      datalog.facts_digest === alloy.facts_digest &&
      sameRef(datalog.fact_manifest_ref, alloy.fact_manifest_ref),
    same_universe: datalog.universe_digest === alloy.universe_digest,
    same_property:
      datalog.property_id === alloy.property_id &&
      datalog.property_version === alloy.property_version &&
      sameRef(datalog.property_definition_ref, alloy.property_definition_ref),
    same_mapping:
      sameRef(datalog.comparison_contract_ref, alloy.comparison_contract_ref) &&
      sameRef(datalog.translation.projection_receipt_ref, alloy.translation.projection_receipt_ref) &&
      datalog.translation.source_facts_digest === datalog.facts_digest &&
      alloy.translation.source_facts_digest === alloy.facts_digest &&
      datalog.translation.omitted_fact_count === 0 &&
      datalog.translation.invented_fact_count === 0 &&
      alloy.translation.omitted_fact_count === 0 &&
      alloy.translation.invented_fact_count === 0 &&
      datalog.normalized_result.domain_kind === alloy.normalized_result.domain_kind &&
      datalog.normalized_result.evaluation_mode === alloy.normalized_result.evaluation_mode,
    provider_kinds_exact:
      datalog.provider.kind === "datalog" &&
      alloy.provider.kind === "alloy" &&
      datalog.provider.id === "souffle" &&
      alloy.provider.id === "alloy",
    receipts_valid: valid(datalog) && valid(alloy),
    domains_comparable:
      datalog.scope_digest === alloy.scope_digest &&
      datalog.selected_relation_digest === alloy.selected_relation_digest &&
      sameRef(datalog.scope_contract_ref, alloy.scope_contract_ref),
  };
  const comparable = Object.values(preflight).every(Boolean);
  const status = expectedJoin(
    comparable,
    datalog.normalized_result.outcome,
    alloy.normalized_result.outcome,
  );
  const residue = status.join_status === "consistent"
    ? []
    : [{
        residue_id: status.join_status === "blocked"
          ? "evf.l2.join.not-comparable"
          : "evf.l2.join.provider-disagreement",
        class: status.join_status === "blocked"
          ? "domain-not-comparable"
          : "provider-disagreement",
        severity: "blocking",
        message: status.join_status === "blocked"
          ? "Provider bindings are not exactly comparable."
          : "Provider outcomes disagree or one provider is unresolved.",
        source_refs: [input.datalogRef, input.alloyRef],
        claim_effect: "no consistency claim",
      }];
  const withoutDigest: Omit<JoinReceipt, "join_payload_digest"> = {
    schema_version: "evf.graph-law-join-receipt/v1",
    join_receipt_id: input.joinReceiptId,
    request_ref: datalog.request_ref,
    fact_manifest_ref: datalog.fact_manifest_ref,
    property_definition_ref: datalog.property_definition_ref,
    comparison_contract_ref: datalog.comparison_contract_ref,
    scope_contract_ref: datalog.scope_contract_ref,
    request_id: datalog.request_id,
    facts_digest: datalog.facts_digest,
    universe_digest: datalog.universe_digest,
    selected_relation_digest: datalog.selected_relation_digest,
    scope_digest: datalog.scope_digest,
    property_id: datalog.property_id,
    property_version: datalog.property_version,
    provider_receipts: { datalog: input.datalogRef, alloy: input.alloyRef },
    provider_semantic_result_digests: {
      datalog: datalog.semantic_result_digest,
      alloy: alloy.semantic_result_digest,
    },
    preflight,
    mapped_results: {
      datalog: {
        outcome: datalog.normalized_result.outcome,
        domain_kind: datalog.normalized_result.domain_kind,
        evaluation_mode: datalog.normalized_result.evaluation_mode,
        result_payload_digest: datalog.normalized_result.result_payload_digest,
      },
      alloy: {
        outcome: alloy.normalized_result.outcome,
        domain_kind: alloy.normalized_result.domain_kind,
        evaluation_mode: alloy.normalized_result.evaluation_mode,
        result_payload_digest: alloy.normalized_result.result_payload_digest,
      },
    },
    ...status,
    evidence_refs: input.evidenceRefs ?? [input.datalogRef, input.alloyRef],
    residue,
    authority_effect: "none",
    release_admission: "not-granted",
    claim_ceiling: "property-specific-consistency-over-shared-facts-only",
  };
  return { ...withoutDigest, join_payload_digest: digestValue(payload(withoutDigest)) };
}

export function verifyJoinReceipt(
  receipt: JoinReceipt,
  datalog: ProviderReceipt,
  alloy: ProviderReceipt,
): JoinReceipt {
  const rebuilt = buildJoinReceipt({
    joinReceiptId: receipt.join_receipt_id,
    datalog,
    alloy,
    datalogRef: receipt.provider_receipts.datalog,
    alloyRef: receipt.provider_receipts.alloy,
    evidenceRefs: receipt.evidence_refs,
  });
  if (
    receipt.authority_effect !== "none" ||
    receipt.release_admission !== "not-granted" ||
    receipt.claim_ceiling !== "property-specific-consistency-over-shared-facts-only" ||
    receipt.join_status === ("pass" as string) ||
    canonicalJson(receipt) !== canonicalJson(rebuilt)
  ) {
    fail("JOIN_RECEIPT_TAMPERED", "join", "join receipt does not independently replay");
  }
  return receipt;
}
