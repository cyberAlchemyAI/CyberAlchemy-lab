import {canonicalModuleJson, digestModuleValue} from "../../../agent-reasoning-engine/packages/module-port/index.mjs";
import {STAGE_HANDOFF_SCHEMA} from "../ontology-stage-port/index.mjs";

export const PLAN_ONTOLOGY_HANDOFF_INPUT_SCHEMA = "cav2.plan-ontology-handoff-input/v1";
export const PLAN_ONTOLOGY_HANDOFF_RESULT_SCHEMA = "cav2.plan-ontology-handoff-result/v1";
export const PLAN_ONTOLOGY_CONSUMER_ID = "cav2.plan.ontology-candidate-consumer";

const inputKeys = new Set(["schema_version", "consumer_id", "expected_stage", "candidate_bytes", "handoff_receipt", "claim_posture", "implementation_authority", "authority_effect"]);
const expectedKeys = new Set(["stage_id", "ontology_type", "stage_graph_digest", "module_set_digest", "manifest_digest"]);
const receiptKeys = new Set(["schema_version", "stage_id", "ontology_type", "stage_graph_digest", "module_set_digest", "manifest_digest", "candidate_digest", "prerequisite_receipt_set_digest", "confirmation_digest", "adapter_receipt_digests", "authority_effect", "handoff_receipt_digest"]);

function exactKeys(value, keys) {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    && Object.keys(value).length === keys.size && Object.keys(value).every((key) => keys.has(key));
}

function result({ok, disposition, stageId = null, candidateDigest = null, handoffDigest = null, reasonCodes = []}) {
  const material = {schema_version: PLAN_ONTOLOGY_HANDOFF_RESULT_SCHEMA, ok, disposition, stage_id: stageId, candidate_digest: candidateDigest, handoff_receipt_digest: handoffDigest, reason_codes: [...new Set(reasonCodes)].sort(), planning_effect: "none", implementation_authority: "not-granted", authority_effect: "none"};
  return Object.freeze({...material, result_digest: digestModuleValue(material)});
}

export function acceptOntologyHandoffForPlan(input) {
  if (!exactKeys(input, inputKeys) || input.schema_version !== PLAN_ONTOLOGY_HANDOFF_INPUT_SCHEMA) return result({ok: false, disposition: "incompatible-schema", reasonCodes: ["plan.handoff-input-schema"]});
  if (input.consumer_id !== PLAN_ONTOLOGY_CONSUMER_ID || input.claim_posture !== "candidate-evidence-only" || input.implementation_authority !== "not-granted" || input.authority_effect !== "none") return result({ok: false, disposition: "blocked", reasonCodes: ["plan.handoff-authority-posture"]});
  if (!exactKeys(input.expected_stage, expectedKeys) || !exactKeys(input.handoff_receipt, receiptKeys)) return result({ok: false, disposition: "blocked", reasonCodes: ["plan.handoff-binding-shape"]});
  let candidate;
  try { candidate = JSON.parse(input.candidate_bytes); } catch { return result({ok: false, disposition: "blocked", reasonCodes: ["plan.handoff-candidate-json"]}); }
  if (canonicalModuleJson(candidate) !== input.candidate_bytes || candidate?.status !== "candidate" || candidate?.authority_effect !== "none") return result({ok: false, disposition: "blocked", reasonCodes: ["plan.handoff-candidate-posture"]});
  const receipt = input.handoff_receipt;
  const receiptMaterial = {...receipt};
  delete receiptMaterial.handoff_receipt_digest;
  if (receipt.schema_version !== STAGE_HANDOFF_SCHEMA || receipt.authority_effect !== "none" || digestModuleValue(receiptMaterial) !== receipt.handoff_receipt_digest) return result({ok: false, disposition: "blocked", reasonCodes: ["plan.handoff-receipt-integrity"]});
  const expected = input.expected_stage;
  if (receipt.stage_id !== expected.stage_id || receipt.ontology_type !== expected.ontology_type || receipt.stage_graph_digest !== expected.stage_graph_digest || receipt.module_set_digest !== expected.module_set_digest || receipt.manifest_digest !== expected.manifest_digest) return result({ok: false, disposition: "blocked", reasonCodes: ["plan.handoff-stage-binding"]});
  const candidateDigest = digestModuleValue(candidate);
  if (candidateDigest !== receipt.candidate_digest) return result({ok: false, disposition: "blocked", reasonCodes: ["plan.handoff-candidate-drift"]});
  return result({ok: true, disposition: "accepted-evidence", stageId: receipt.stage_id, candidateDigest, handoffDigest: receipt.handoff_receipt_digest});
}
