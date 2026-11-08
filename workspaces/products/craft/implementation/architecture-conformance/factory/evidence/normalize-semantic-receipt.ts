import type {
  FactorySemanticNodeReceiptV1,
  FactorySemanticReceiptV1,
  FactoryVerifiedSemanticNodeReceiptV1,
} from "../contracts/factory-semantic-receipt-v1.js";
import type { FactoryRunPlanV1 } from "../contracts/factory-run-plan-v1.js";
import { recomputeProofAccounting } from
  "../../kernel/evidence/recompute-proof-accounting.js";
import { canonicalJson, fail, sha256 } from "../shared/canonical.js";

const countKeys = Object.freeze([
  "positives_declared",
  "positives_passed",
  "mutants_declared",
  "mutants_killed",
] as const);

const validateCounts = (accounting: FactorySemanticNodeReceiptV1["accounting"]): void => {
  if (countKeys.some((key) => !Number.isInteger(accounting[key]) || accounting[key] < 0)) {
    fail("FACTORY_ACCOUNTING_INVALID", "counts");
  }
  if (accounting.positives_declared !== accounting.positives_passed ||
      accounting.mutants_declared !== accounting.mutants_killed) {
    fail("FACTORY_ACCOUNTING_INCOMPLETE");
  }
};

const normalizeNode = (
  plan: FactoryRunPlanV1,
  node: FactorySemanticNodeReceiptV1,
): FactoryVerifiedSemanticNodeReceiptV1 => {
  validateCounts(node.accounting);
  const locked = plan.lock.nodes.find(({ node_id: id }) => id === node.node_id);
  if (locked === undefined || locked.provider_id !== node.provider_id) {
    return fail("FACTORY_ACCOUNTING_NODE_INVALID", node.node_id);
  }
  if (node.claim_ceiling !== locked.claim_ceiling) {
    return fail("FACTORY_CLAIM_CEILING_MISMATCH", node.node_id);
  }
  const denominatorRefs = locked.inputs.filter(({ role }) => role === "proof-denominator");
  if (denominatorRefs.length > 1) {
    return fail("FACTORY_PROOF_DENOMINATOR_AMBIGUOUS", node.node_id);
  }
  if (denominatorRefs.length === 0 && node.accounting.proof !== undefined) {
    return fail("FACTORY_PROOF_EVIDENCE_UNLOCKED", node.node_id);
  }
  if (denominatorRefs.length === 1 && node.accounting.proof === undefined) {
    return fail("FACTORY_PROOF_EVIDENCE_REQUIRED", node.node_id);
  }

  let accounting: FactoryVerifiedSemanticNodeReceiptV1["accounting"];
  if (denominatorRefs.length === 0) {
    accounting = Object.freeze({
      positives_declared: node.accounting.positives_declared,
      positives_passed: node.accounting.positives_passed,
      mutants_declared: node.accounting.mutants_declared,
      mutants_killed: node.accounting.mutants_killed,
    });
  } else {
    const recomputed = recomputeProofAccounting({
      locked_denominator_ref: Object.freeze({
        role: "proof-denominator" as const,
        path: denominatorRefs[0]!.path,
        sha256: denominatorRefs[0]!.sha256,
      }),
      provider_id: node.provider_id,
      evidence: node.accounting.proof,
    });
    if (recomputed.result !== "pass" || recomputed.proof === null) {
      return fail("FACTORY_PROOF_ACCOUNTING_BLOCKED", recomputed.diagnostics.join(","));
    }
    if (countKeys.some((key) => node.accounting[key] !== recomputed.totals[key])) {
      return fail("FACTORY_PROOF_TOTALS_MISMATCH", node.node_id);
    }
    accounting = Object.freeze({ ...recomputed.totals, proof: recomputed.proof });
  }
  return Object.freeze({
    node_id: node.node_id,
    provider_id: node.provider_id,
    depends_on: Object.freeze([...node.depends_on]),
    semantic_sha256: node.semantic_sha256,
    replay_sha256: node.replay_sha256,
    accounting,
    claim_ceiling: node.claim_ceiling,
  });
};

export const normalizeFactorySemanticReceipt = (input: Readonly<{
  plan: FactoryRunPlanV1;
  nodes: readonly FactorySemanticNodeReceiptV1[];
}>): Readonly<{
  receipt: FactorySemanticReceiptV1;
  semantic_receipt_sha256: string;
}> => {
  const nodes = Object.freeze(input.nodes.map((node) => normalizeNode(input.plan, node)));
  const receipt = Object.freeze({
    schema_version: "FactorySemanticReceipt/v1" as const,
    result: "pass" as const,
    request_sha256: input.plan.lock.request_sha256,
    lock_sha256: input.plan.lock.lock_sha256,
    run_id: input.plan.run_id,
    ordered_nodes: nodes,
    claim_ceiling: input.plan.request.claim_ceiling,
    authority_effect: "none" as const,
  });
  return Object.freeze({ receipt, semantic_receipt_sha256: sha256(canonicalJson(receipt)) });
};
