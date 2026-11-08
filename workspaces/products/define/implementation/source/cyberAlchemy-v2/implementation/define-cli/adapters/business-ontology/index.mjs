import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";

import {digestModuleValue, sealModuleManifest} from "../../../agent-reasoning-engine/packages/module-port/index.mjs";
import {STAGE_DESCRIPTOR_SCHEMA, STAGE_HANDOFF_SCHEMA, STAGE_PROTOCOLS} from "../../packages/ontology-stage-port/index.mjs";
import {PRODUCT_ONTOLOGY_MANIFEST_DIGEST, PRODUCT_ONTOLOGY_STAGE_ID} from "../product-ontology/index.mjs";
import {execute as selectQuestion} from "../../generated/define-business-ontology/entries/BusinessOntologyQuestion/app/function/behavior.mjs";
import {execute as evaluateReadiness} from "../../generated/define-business-ontology/entries/BusinessOntologyReadiness/app/function/behavior.mjs";

export const BUSINESS_ONTOLOGY_STAGE_ID = "alch-business-ontology";
export const BUSINESS_ONTOLOGY_SOURCE_REF = "language/capabilities/alchlang/define/alch-product-business-ontology-v1/business-ontology.json";

const repositoryRoot = new URL("../../../../", import.meta.url);
const businessSourceBytes = readFileSync(new URL(BUSINESS_ONTOLOGY_SOURCE_REF, repositoryRoot), "utf8");
const businessSource = JSON.parse(businessSourceBytes);
export const BUSINESS_ONTOLOGY_SOURCE_DIGEST = createHash("sha256").update(businessSourceBytes, "utf8").digest("hex");

const capabilities = Object.freeze({
  describe: "define.ontology.alch-business.describe/v1",
  next_question: "define.ontology.alch-business.next-question/v1",
  evaluate: "define.ontology.alch-business.evaluate/v1",
  materialize: "define.ontology.alch-business.materialize/v1",
  validate: "define.ontology.alch-business.validate/v1",
});

const manifest = sealModuleManifest({
  schema_version: "are.module-manifest/v1",
  module_id: "cav2-define-alch-business-ontology-authoring",
  version: "1-candidate",
  adapter_protocol: "are.module-adapter/v1",
  capabilities: Object.entries(capabilities).map(([operation, capability_id]) => ({
    capability_id,
    input_protocol: STAGE_PROTOCOLS[operation].input,
    output_protocol: STAGE_PROTOCOLS[operation].output,
  })),
  required_permissions: [],
  side_effects: false,
  authority_effect: "none",
});
export const BUSINESS_ONTOLOGY_MANIFEST_DIGEST = manifest.manifest_digest;

const questions = Object.freeze({
  "meaning-owner": ["business-meaning-owner", "Who owns the meaning of this bounded business model?", "business-meaning-owner"],
  "bounded-model": ["business-bounded-model", "What bounded domain does this Business Ontology describe?", "business-bounded-model"],
  "concepts-and-relationships": ["business-concepts-and-relationships", "Which core business concepts and relationships must the model preserve?", "business-concepts-and-relationships"],
  "domain-rule": ["business-domain-rule", "What domain rule constrains behavior in this model?", "business-domain-rule"],
  lifecycle: ["business-lifecycle", "What state transition or lifecycle behavior must be explicit?", "business-lifecycle"],
  "authority-boundary": ["business-authority-boundary", "Where does decision authority for this model begin and end?", "business-authority-boundary"],
});

const questionIds = Object.freeze([
  "business-meaning-owner",
  "business-bounded-model",
  "business-concepts-and-relationships",
  "business-domain-rule",
  "business-lifecycle",
  "business-authority-boundary",
]);
const candidateKeys = new Set(["schema_version", "ontology_type", "source_ontology_ref", "source_ontology_digest", "product_candidate_digest", "product_handoff_receipt_digest", "dependency_receipt_set_digest", "business", "orthogonality", "non_collapse", "status", "authority_effect"]);
const businessKeys = new Set(["meaning_owner", "bounded_model", "concepts_and_relationships", "domain_rule", "lifecycle", "authority_boundary"]);

function exactKeys(value, keys) {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    && Object.keys(value).length === keys.size
    && Object.keys(value).every((key) => keys.has(key));
}

function answers(input) {
  return new Map((input.responses ?? [])
    .filter((item) => ["answer", "correction"].includes(item.response_kind))
    .map((item) => [item.question_id, item]));
}

function productReceipt(input) {
  const receipt = input.prerequisite_receipts?.find((item) => item?.stage_id === PRODUCT_ONTOLOGY_STAGE_ID);
  if (!receipt || receipt.schema_version !== STAGE_HANDOFF_SCHEMA
    || receipt.ontology_type !== "product"
    || receipt.manifest_digest !== PRODUCT_ONTOLOGY_MANIFEST_DIGEST
    || receipt.stage_graph_digest !== input.stage_graph_digest
    || receipt.module_set_digest !== input.module_set_digest
    || receipt.authority_effect !== "none") return null;
  const material = {...receipt};
  delete material.handoff_receipt_digest;
  return digestModuleValue(material) === receipt.handoff_receipt_digest ? receipt : null;
}

function quality(map) {
  const values = questionIds.map((id) => map.get(id)).filter(Boolean);
  return {
    semantic_grounding: values.length === questionIds.length && values.every((item) => item.evidence?.semantic_grounding === true),
    non_collapse: values.length === questionIds.length && values.every((item) => item.evidence?.non_collapse === true),
    orthogonality: values.length === questionIds.length && values.every((item) => item.evidence?.orthogonality === true),
  };
}

function candidate(input, receipt) {
  const map = answers(input);
  return {
    schema_version: "cav2.alch-business-ontology-candidate/v1",
    ontology_type: "business",
    source_ontology_ref: BUSINESS_ONTOLOGY_SOURCE_REF,
    source_ontology_digest: BUSINESS_ONTOLOGY_SOURCE_DIGEST,
    product_candidate_digest: receipt.candidate_digest,
    product_handoff_receipt_digest: receipt.handoff_receipt_digest,
    dependency_receipt_set_digest: digestModuleValue(input.prerequisite_receipts),
    business: {
      meaning_owner: map.get("business-meaning-owner")?.response,
      bounded_model: map.get("business-bounded-model")?.response,
      concepts_and_relationships: map.get("business-concepts-and-relationships")?.response,
      domain_rule: map.get("business-domain-rule")?.response,
      lifecycle: map.get("business-lifecycle")?.response,
      authority_boundary: map.get("business-authority-boundary")?.response,
    },
    orthogonality: businessSource.orthogonality,
    non_collapse: businessSource.non_collapse,
    status: "candidate",
    authority_effect: "none",
  };
}

function validCandidate(value) {
  return exactKeys(value, candidateKeys)
    && value?.schema_version === "cav2.alch-business-ontology-candidate/v1"
    && value?.ontology_type === "business"
    && value?.source_ontology_ref === BUSINESS_ONTOLOGY_SOURCE_REF
    && value?.source_ontology_digest === BUSINESS_ONTOLOGY_SOURCE_DIGEST
    && /^[a-f0-9]{64}$/u.test(value?.product_candidate_digest ?? "")
    && /^[a-f0-9]{64}$/u.test(value?.product_handoff_receipt_digest ?? "")
    && /^[a-f0-9]{64}$/u.test(value?.dependency_receipt_set_digest ?? "")
    && exactKeys(value?.business, businessKeys)
    && Object.values(value?.business ?? {}).every((item) => typeof item === "string" && item.length > 0)
    && digestModuleValue(value?.orthogonality) === digestModuleValue(businessSource.orthogonality)
    && digestModuleValue(value?.non_collapse) === digestModuleValue(businessSource.non_collapse)
    && value?.status === "candidate"
    && value?.authority_effect === "none";
}

export function createBusinessOntologyStageAdapter() {
  const descriptor = Object.freeze({
    schema_version: STAGE_DESCRIPTOR_SCHEMA,
    stage_id: BUSINESS_ONTOLOGY_STAGE_ID,
    ontology_type: "business",
    module_id: manifest.module_id,
    module_version: manifest.version,
    manifest_digest: manifest.manifest_digest,
    prerequisite_stage_ids: [PRODUCT_ONTOLOGY_STAGE_ID],
    capabilities,
    alch_entrypoints: ["BusinessOntologyQuestion", "BusinessOntologyReadiness"],
    authority_effect: "none",
  });
  const adapter = Object.freeze({manifest, invoke(invocation) {
    const input = invocation.input;
    if (!Object.values(capabilities).includes(invocation.capability_id) || input.stage_id !== BUSINESS_ONTOLOGY_STAGE_ID) {
      throw new TypeError("Business Ontology capability mismatch.");
    }
    if (invocation.capability_id === capabilities.describe) return {schema_version: STAGE_PROTOCOLS.describe.output, stage_id: BUSINESS_ONTOLOGY_STAGE_ID, ontology_type: "business", label: "Alch Business Ontology", purpose: businessSource.scope, output_artifact_kind: "cav2.alch-business-ontology-candidate/v1", owner_ref: "CyberAlchemy v2 Language Project owner", authority_effect: "none"};
    const map = answers(input);
    const selected = selectQuestion({input: {
      meaning_owner_present: map.has("business-meaning-owner"),
      bounded_model_present: map.has("business-bounded-model"),
      concepts_and_relationships_present: map.has("business-concepts-and-relationships"),
      domain_rule_present: map.has("business-domain-rule"),
      lifecycle_present: map.has("business-lifecycle"),
      authority_boundary_present: map.has("business-authority-boundary"),
    }}, {});
    if (invocation.capability_id === capabilities.next_question) {
      const spec = questions[selected.next_focus];
      return {schema_version: STAGE_PROTOCOLS.next_question.output, stage_id: BUSINESS_ONTOLOGY_STAGE_ID, complete: selected.status === "complete", question: spec ? {question_id: spec[0], prompt: spec[1], answer_kind: spec[2], owner_ref: "CyberAlchemy v2 Language Project owner"} : null, authority_effect: "none"};
    }
    const receipt = productReceipt(input);
    const checks = quality(map);
    const ready = evaluateReadiness({input: {product_receipt_current: receipt !== null, business_questions_complete: map.size === questionIds.length, semantic_grounding_pass: checks.semantic_grounding, non_collapse_pass: checks.non_collapse, orthogonality_pass: checks.orthogonality}}, {});
    if (invocation.capability_id === capabilities.evaluate) return {schema_version: STAGE_PROTOCOLS.evaluate.output, stage_id: BUSINESS_ONTOLOGY_STAGE_ID, interaction_complete: map.size === questionIds.length && receipt !== null, checks, reason_codes: ready.status === "ready" ? [] : [`business.${ready.repair_focus}-required`], authority_effect: "none"};
    if (invocation.capability_id === capabilities.materialize) {
      if (ready.status !== "ready") throw new TypeError(`Business Ontology not ready: ${ready.repair_focus}`);
      const value = candidate(input, receipt);
      return {schema_version: STAGE_PROTOCOLS.materialize.output, stage_id: BUSINESS_ONTOLOGY_STAGE_ID, candidate: value, candidate_digest: digestModuleValue(value), authority_effect: "none"};
    }
    const valid = validCandidate(input.candidate);
    return {schema_version: STAGE_PROTOCOLS.validate.output, stage_id: BUSINESS_ONTOLOGY_STAGE_ID, valid, reason_codes: valid ? [] : ["business.candidate-invalid"], authority_effect: "none"};
  }});
  return Object.freeze({adapter, descriptor});
}
