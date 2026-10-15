import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";

import {digestModuleValue, sealModuleManifest} from "../../../agent-reasoning-engine/packages/module-port/index.mjs";
import {STAGE_DESCRIPTOR_SCHEMA, STAGE_HANDOFF_SCHEMA, STAGE_PROTOCOLS} from "../../packages/ontology-stage-port/index.mjs";
import {execute as selectQuestion} from "../../generated/define-product-ontology/entries/ProductOntologyQuestion/app/function/behavior.mjs";
import {execute as evaluateReadiness} from "../../generated/define-product-ontology/entries/ProductOntologyReadiness/app/function/behavior.mjs";

export const PRODUCT_ONTOLOGY_STAGE_ID = "alch-product-ontology";
export const DEFINITION_PACK_STAGE_ID = "definition-pack";
export const PRODUCT_ONTOLOGY_SOURCE_REF = "language/capabilities/alchlang/define/alch-product-business-ontology-v1/product-ontology.json";
export const DEFINITION_PACK_SOURCE_REF = "language/capabilities/alchlang/define/alch-product-business-ontology-v1/definition-pack.json";

const repositoryRoot = new URL("../../../../", import.meta.url);
const productSourceBytes = readFileSync(new URL(PRODUCT_ONTOLOGY_SOURCE_REF, repositoryRoot), "utf8");
const definitionPackBytes = readFileSync(new URL(DEFINITION_PACK_SOURCE_REF, repositoryRoot), "utf8");
const productSource = JSON.parse(productSourceBytes);
const definitionPack = JSON.parse(definitionPackBytes);
const rawDigest = (bytes) => createHash("sha256").update(bytes, "utf8").digest("hex");
export const PRODUCT_ONTOLOGY_SOURCE_DIGEST = rawDigest(productSourceBytes);
export const DEFINITION_PACK_SOURCE_DIGEST = rawDigest(definitionPackBytes);
export const DEFINITION_PACK_CANDIDATE_DIGEST = digestModuleValue(definitionPack);

const productCapabilities = Object.freeze({
  describe: "define.ontology.alch-product.describe/v1",
  next_question: "define.ontology.alch-product.next-question/v1",
  evaluate: "define.ontology.alch-product.evaluate/v1",
  materialize: "define.ontology.alch-product.materialize/v1",
  validate: "define.ontology.alch-product.validate/v1",
});
const definitionCapabilities = Object.freeze({
  describe: "define.ontology.definition-pack.describe/v1",
  next_question: "define.ontology.definition-pack.next-question/v1",
  evaluate: "define.ontology.definition-pack.evaluate/v1",
  materialize: "define.ontology.definition-pack.materialize/v1",
  validate: "define.ontology.definition-pack.validate/v1",
});
const productManifest = sealModuleManifest({schema_version: "are.module-manifest/v1", module_id: "cav2-define-alch-product-ontology-authoring", version: "1-candidate", adapter_protocol: "are.module-adapter/v1", capabilities: [...Object.entries(productCapabilities), ...Object.entries(definitionCapabilities)].map(([operation, capability_id]) => ({capability_id, input_protocol: STAGE_PROTOCOLS[operation].input, output_protocol: STAGE_PROTOCOLS[operation].output})), required_permissions: [], side_effects: false, authority_effect: "none"});
export const PRODUCT_ONTOLOGY_MANIFEST_DIGEST = productManifest.manifest_digest;

const questions = Object.freeze({
  capability: ["product-capability", "What stable user-valued capability should this Product Ontology preserve?", "product-capability"],
  "primary-user": ["primary-user", "Who is the primary user of that capability?", "product-user"],
  "user-job": ["user-job", "What job does that user need to accomplish?", "user-job"],
  outcome: ["product-outcome", "What user-visible outcome should the capability achieve?", "product-outcome"],
  constraint: ["product-constraint", "What constraint must remain true while producing that outcome?", "product-constraint"],
});

function answers(input) {
  return new Map((input.responses ?? []).filter((item) => ["answer", "correction"].includes(item.response_kind)).map((item) => [item.question_id, item]));
}

function definitionReceipt(input) {
  const receipt = input.prerequisite_receipts?.find((item) => item?.stage_id === DEFINITION_PACK_STAGE_ID);
  if (!receipt || receipt.candidate_digest !== DEFINITION_PACK_CANDIDATE_DIGEST || receipt.authority_effect !== "none") return null;
  const material = {...receipt};
  delete material.handoff_receipt_digest;
  return digestModuleValue(material) === receipt.handoff_receipt_digest ? receipt : null;
}

function quality(map) {
  const values = [...map.values()];
  return {
    semantic_grounding: values.length === 5 && values.every((item) => item.evidence?.semantic_grounding === true),
    non_collapse: values.length === 5 && values.every((item) => item.evidence?.non_collapse === true),
    orthogonality: values.length === 5 && values.every((item) => item.evidence?.orthogonality === true),
  };
}

function candidate(input) {
  const map = answers(input);
  return {
    schema_version: "cav2.alch-product-ontology-candidate/v1",
    ontology_type: "product",
    source_ontology_ref: PRODUCT_ONTOLOGY_SOURCE_REF,
    source_ontology_digest: PRODUCT_ONTOLOGY_SOURCE_DIGEST,
    definition_pack_digest: DEFINITION_PACK_CANDIDATE_DIGEST,
    product: {
      capability: map.get("product-capability")?.response,
      primary_user: map.get("primary-user")?.response,
      user_job: map.get("user-job")?.response,
      outcome: map.get("product-outcome")?.response,
      constraint: map.get("product-constraint")?.response,
    },
    non_collapse: productSource.non_collapse,
    status: "candidate",
    authority_effect: "none",
  };
}

export function createProductOntologyStageAdapter() {
  const manifest = productManifest;
  const descriptor = Object.freeze({schema_version: STAGE_DESCRIPTOR_SCHEMA, stage_id: PRODUCT_ONTOLOGY_STAGE_ID, ontology_type: "product", module_id: manifest.module_id, module_version: manifest.version, manifest_digest: manifest.manifest_digest, prerequisite_stage_ids: [DEFINITION_PACK_STAGE_ID], capabilities: productCapabilities, alch_entrypoints: ["ProductOntologyQuestion", "ProductOntologyReadiness"], authority_effect: "none"});
  const definition_pack_descriptor = Object.freeze({schema_version: STAGE_DESCRIPTOR_SCHEMA, stage_id: DEFINITION_PACK_STAGE_ID, ontology_type: "definition-pack", module_id: manifest.module_id, module_version: manifest.version, manifest_digest: manifest.manifest_digest, prerequisite_stage_ids: [], capabilities: definitionCapabilities, alch_entrypoints: ["DefinitionPackExistingCandidate"], authority_effect: "none"});
  const adapter = Object.freeze({manifest, invoke(invocation) {
    const input = invocation.input;
    if (Object.values(definitionCapabilities).includes(invocation.capability_id)) {
      if (invocation.capability_id === definitionCapabilities.describe) return {schema_version: STAGE_PROTOCOLS.describe.output, stage_id: DEFINITION_PACK_STAGE_ID, ontology_type: "definition-pack", label: "Alch Definition Pack", purpose: definitionPack.goal, output_artifact_kind: definitionPack.schema_version, owner_ref: definitionPack.owners.join(" + "), authority_effect: "none"};
      if (invocation.capability_id === definitionCapabilities.next_question) return {schema_version: STAGE_PROTOCOLS.next_question.output, stage_id: DEFINITION_PACK_STAGE_ID, complete: true, question: null, authority_effect: "none"};
      if (invocation.capability_id === definitionCapabilities.evaluate) return {schema_version: STAGE_PROTOCOLS.evaluate.output, stage_id: DEFINITION_PACK_STAGE_ID, interaction_complete: true, checks: {semantic_grounding: true, non_collapse: true, orthogonality: true}, reason_codes: [], authority_effect: "none"};
      if (invocation.capability_id === definitionCapabilities.materialize) return {schema_version: STAGE_PROTOCOLS.materialize.output, stage_id: DEFINITION_PACK_STAGE_ID, candidate: definitionPack, candidate_digest: DEFINITION_PACK_CANDIDATE_DIGEST, authority_effect: "none"};
      if (invocation.capability_id === definitionCapabilities.validate) return {schema_version: STAGE_PROTOCOLS.validate.output, stage_id: DEFINITION_PACK_STAGE_ID, valid: digestModuleValue(input.candidate) === digestModuleValue(definitionPack), reason_codes: digestModuleValue(input.candidate) === digestModuleValue(definitionPack) ? [] : ["product.definition-pack-invalid"], authority_effect: "none"};
    }
    if (!Object.values(productCapabilities).includes(invocation.capability_id) || input.stage_id !== PRODUCT_ONTOLOGY_STAGE_ID) throw new TypeError("Product Ontology capability mismatch.");
    if (invocation.capability_id === productCapabilities.describe) return {schema_version: STAGE_PROTOCOLS.describe.output, stage_id: PRODUCT_ONTOLOGY_STAGE_ID, ontology_type: "product", label: "Alch Product Ontology", purpose: productSource.scope, output_artifact_kind: "cav2.alch-product-ontology-candidate/v1", owner_ref: "CyberAlchemy v2 Language Project owner", authority_effect: "none"};
    const map = answers(input);
    const q = selectQuestion({input: {capability_present: map.has("product-capability"), primary_user_present: map.has("primary-user"), user_job_present: map.has("user-job"), outcome_present: map.has("product-outcome"), constraint_present: map.has("product-constraint")}}, {});
    if (invocation.capability_id === productCapabilities.next_question) { const spec = questions[q.next_focus]; return {schema_version: STAGE_PROTOCOLS.next_question.output, stage_id: PRODUCT_ONTOLOGY_STAGE_ID, complete: q.status === "complete", question: spec ? {question_id: spec[0], prompt: spec[1], answer_kind: spec[2], owner_ref: "CyberAlchemy v2 Language Project owner"} : null, authority_effect: "none"}; }
    const checks = quality(map); const ready = evaluateReadiness({input: {definition_pack_current: definitionReceipt(input) !== null, product_questions_complete: map.size === 5, semantic_grounding_pass: checks.semantic_grounding, non_collapse_pass: checks.non_collapse, orthogonality_pass: checks.orthogonality}}, {});
    if (invocation.capability_id === productCapabilities.evaluate) return {schema_version: STAGE_PROTOCOLS.evaluate.output, stage_id: PRODUCT_ONTOLOGY_STAGE_ID, interaction_complete: map.size === 5 && definitionReceipt(input) !== null, checks, reason_codes: ready.status === "ready" ? [] : [`product.${ready.repair_focus}-required`], authority_effect: "none"};
    if (invocation.capability_id === productCapabilities.materialize) { if (ready.status !== "ready") throw new TypeError(`Product Ontology not ready: ${ready.repair_focus}`); const value = candidate(input); return {schema_version: STAGE_PROTOCOLS.materialize.output, stage_id: PRODUCT_ONTOLOGY_STAGE_ID, candidate: value, candidate_digest: digestModuleValue(value), authority_effect: "none"}; }
    const value = input.candidate; const valid = value?.schema_version === "cav2.alch-product-ontology-candidate/v1" && value?.source_ontology_digest === PRODUCT_ONTOLOGY_SOURCE_DIGEST && value?.definition_pack_digest === DEFINITION_PACK_CANDIDATE_DIGEST && Object.values(value?.product ?? {}).every((item) => typeof item === "string" && item.length > 0) && value?.authority_effect === "none"; return {schema_version: STAGE_PROTOCOLS.validate.output, stage_id: PRODUCT_ONTOLOGY_STAGE_ID, valid, reason_codes: valid ? [] : ["product.candidate-invalid"], authority_effect: "none"};
  }});
  return Object.freeze({adapter, descriptor, definition_pack_descriptor});
}

export function createDefinitionPackPrerequisiteReceipt({stage_graph_digest, module_set_digest, manifest_digest}) {
  const material = {schema_version: STAGE_HANDOFF_SCHEMA, stage_id: DEFINITION_PACK_STAGE_ID, ontology_type: "definition-pack", stage_graph_digest, module_set_digest, manifest_digest, candidate_digest: DEFINITION_PACK_CANDIDATE_DIGEST, prerequisite_receipt_set_digest: digestModuleValue([]), confirmation_digest: digestModuleValue({source_ref: DEFINITION_PACK_SOURCE_REF, source_digest: DEFINITION_PACK_SOURCE_DIGEST, candidate_digest: DEFINITION_PACK_CANDIDATE_DIGEST}), adapter_receipt_digests: [], authority_effect: "none"};
  return Object.freeze({...material, handoff_receipt_digest: digestModuleValue(material)});
}
