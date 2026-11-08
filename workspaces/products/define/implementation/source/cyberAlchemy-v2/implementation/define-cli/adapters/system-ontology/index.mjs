import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";

import {digestModuleValue, sealModuleManifest} from "../../../agent-reasoning-engine/packages/module-port/index.mjs";
import {STAGE_DESCRIPTOR_SCHEMA, STAGE_HANDOFF_SCHEMA, STAGE_PROTOCOLS} from "../../packages/ontology-stage-port/index.mjs";
import {BUSINESS_ONTOLOGY_MANIFEST_DIGEST, BUSINESS_ONTOLOGY_STAGE_ID} from "../business-ontology/index.mjs";
import {execute as selectQuestion} from "../../generated/define-system-ontology/entries/SystemOntologyQuestion/app/function/behavior.mjs";
import {execute as evaluateReadiness} from "../../generated/define-system-ontology/entries/SystemOntologyReadiness/app/function/behavior.mjs";

export const SYSTEM_ONTOLOGY_STAGE_ID = "define-system-ontology";
export const SYSTEM_ONTOLOGY_SOURCE_REF = "define/system-ontology";

const repositoryRoot = new URL("../../../../", import.meta.url);
const sourceRefs = Object.freeze({
  profile: `${SYSTEM_ONTOLOGY_SOURCE_REF}/PROFILE.json`,
  nodes: `${SYSTEM_ONTOLOGY_SOURCE_REF}/NODES.json`,
  relations: `${SYSTEM_ONTOLOGY_SOURCE_REF}/RELATIONS.json`,
});
const sourceBytes = Object.fromEntries(Object.entries(sourceRefs).map(([key, ref]) => [key, readFileSync(new URL(ref, repositoryRoot), "utf8")]));
const source = Object.fromEntries(Object.entries(sourceBytes).map(([key, bytes]) => [key, JSON.parse(bytes)]));
const sha = (bytes) => createHash("sha256").update(bytes, "utf8").digest("hex");
export const SYSTEM_ONTOLOGY_SOURCE_SNAPSHOT = Object.freeze({
  profile_sha256: sha(sourceBytes.profile),
  nodes_sha256: sha(sourceBytes.nodes),
  relations_sha256: sha(sourceBytes.relations),
});
export const SYSTEM_ONTOLOGY_SOURCE_SNAPSHOT_DIGEST = digestModuleValue(SYSTEM_ONTOLOGY_SOURCE_SNAPSHOT);

const capabilities = Object.freeze({
  describe: "define.ontology.system-runtime.describe/v1",
  next_question: "define.ontology.system-runtime.next-question/v1",
  evaluate: "define.ontology.system-runtime.evaluate/v1",
  materialize: "define.ontology.system-runtime.materialize/v1",
  validate: "define.ontology.system-runtime.validate/v1",
});
const manifest = sealModuleManifest({
  schema_version: "are.module-manifest/v1",
  module_id: "cav2-define-system-runtime-ontology-authoring",
  version: "1-candidate",
  adapter_protocol: "are.module-adapter/v1",
  capabilities: Object.entries(capabilities).map(([operation, capability_id]) => ({capability_id, input_protocol: STAGE_PROTOCOLS[operation].input, output_protocol: STAGE_PROTOCOLS[operation].output})),
  required_permissions: [],
  side_effects: false,
  authority_effect: "none",
});
export const SYSTEM_ONTOLOGY_MANIFEST_DIGEST = manifest.manifest_digest;

const questions = Object.freeze({
  "runtime-boundary": ["system-runtime-boundary", "What runtime boundary does this System Ontology describe?", "system-runtime-boundary"],
  components: ["system-components", "Which system components own the required responsibilities?", "system-components"],
  interfaces: ["system-interfaces", "Which interfaces connect those components without sharing ownership?", "system-interfaces"],
  "state-model": ["system-state-model", "Which states and transitions must the runtime preserve?", "system-state-model"],
  "persistence-recovery": ["system-persistence-recovery", "What persistence and recovery behavior must remain explicit?", "system-persistence-recovery"],
  "operating-constraints": ["system-operating-constraints", "Which operating constraints and claim ceiling govern this candidate?", "system-operating-constraints"],
});
const questionIds = Object.freeze(["system-runtime-boundary", "system-components", "system-interfaces", "system-state-model", "system-persistence-recovery", "system-operating-constraints"]);
const candidateKeys = new Set(["schema_version", "ontology_type", "source_package_ref", "source_snapshot", "source_snapshot_digest", "source_status", "source_implementation_status", "source_compiler_conformance", "business_candidate_digest", "business_handoff_receipt_digest", "dependency_receipt_set_digest", "system", "claim_ceiling", "status", "authority_effect"]);
const systemKeys = new Set(["runtime_boundary", "components", "interfaces", "state_model", "persistence_recovery", "operating_constraints"]);

function exactKeys(value, keys) {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    && Object.keys(value).length === keys.size && Object.keys(value).every((key) => keys.has(key));
}

function answers(input) {
  return new Map((input.responses ?? []).filter((item) => ["answer", "correction"].includes(item.response_kind)).map((item) => [item.question_id, item]));
}

function businessReceipt(input) {
  const receipt = input.prerequisite_receipts?.find((item) => item?.stage_id === BUSINESS_ONTOLOGY_STAGE_ID);
  if (!receipt || receipt.schema_version !== STAGE_HANDOFF_SCHEMA || receipt.ontology_type !== "business"
    || receipt.manifest_digest !== BUSINESS_ONTOLOGY_MANIFEST_DIGEST
    || receipt.stage_graph_digest !== input.stage_graph_digest || receipt.module_set_digest !== input.module_set_digest
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
    schema_version: "cav2.define-system-ontology-candidate/v1",
    ontology_type: "system-runtime",
    source_package_ref: SYSTEM_ONTOLOGY_SOURCE_REF,
    source_snapshot: SYSTEM_ONTOLOGY_SOURCE_SNAPSHOT,
    source_snapshot_digest: SYSTEM_ONTOLOGY_SOURCE_SNAPSHOT_DIGEST,
    source_status: source.profile.status,
    source_implementation_status: source.profile.implementation_status,
    source_compiler_conformance: source.profile.domainspec_binding.compiler_conformance,
    business_candidate_digest: receipt.candidate_digest,
    business_handoff_receipt_digest: receipt.handoff_receipt_digest,
    dependency_receipt_set_digest: digestModuleValue(input.prerequisite_receipts),
    system: {
      runtime_boundary: map.get("system-runtime-boundary")?.response,
      components: map.get("system-components")?.response,
      interfaces: map.get("system-interfaces")?.response,
      state_model: map.get("system-state-model")?.response,
      persistence_recovery: map.get("system-persistence-recovery")?.response,
      operating_constraints: map.get("system-operating-constraints")?.response,
    },
    claim_ceiling: source.profile.claim_ceiling,
    status: "candidate",
    authority_effect: "none",
  };
}

function validCandidate(value) {
  return exactKeys(value, candidateKeys)
    && value.schema_version === "cav2.define-system-ontology-candidate/v1"
    && value.ontology_type === "system-runtime" && value.source_package_ref === SYSTEM_ONTOLOGY_SOURCE_REF
    && digestModuleValue(value.source_snapshot) === SYSTEM_ONTOLOGY_SOURCE_SNAPSHOT_DIGEST
    && value.source_snapshot_digest === SYSTEM_ONTOLOGY_SOURCE_SNAPSHOT_DIGEST
    && value.source_status === "candidate" && value.source_implementation_status === "not-implemented"
    && value.source_compiler_conformance === "not_evaluable"
    && [value.business_candidate_digest, value.business_handoff_receipt_digest, value.dependency_receipt_set_digest].every((item) => /^[a-f0-9]{64}$/u.test(item ?? ""))
    && exactKeys(value.system, systemKeys) && Object.values(value.system).every((item) => typeof item === "string" && item.length > 0)
    && digestModuleValue(value.claim_ceiling) === digestModuleValue(source.profile.claim_ceiling)
    && value.status === "candidate" && value.authority_effect === "none";
}

export function createSystemOntologyStageAdapter() {
  const descriptor = Object.freeze({schema_version: STAGE_DESCRIPTOR_SCHEMA, stage_id: SYSTEM_ONTOLOGY_STAGE_ID, ontology_type: "system-runtime", module_id: manifest.module_id, module_version: manifest.version, manifest_digest: manifest.manifest_digest, prerequisite_stage_ids: [BUSINESS_ONTOLOGY_STAGE_ID], capabilities, alch_entrypoints: ["SystemOntologyQuestion", "SystemOntologyReadiness"], authority_effect: "none"});
  const adapter = Object.freeze({manifest, invoke(invocation) {
    const input = invocation.input;
    if (!Object.values(capabilities).includes(invocation.capability_id) || input.stage_id !== SYSTEM_ONTOLOGY_STAGE_ID) throw new TypeError("System Ontology capability mismatch.");
    if (invocation.capability_id === capabilities.describe) return {schema_version: STAGE_PROTOCOLS.describe.output, stage_id: SYSTEM_ONTOLOGY_STAGE_ID, ontology_type: "system-runtime", label: source.profile.label, purpose: "Author a source-bound candidate projection of the Define System Runtime Ontology.", output_artifact_kind: "cav2.define-system-ontology-candidate/v1", owner_ref: source.profile.owner_route, authority_effect: "none"};
    const map = answers(input);
    const selected = selectQuestion({input: {runtime_boundary_present: map.has("system-runtime-boundary"), components_present: map.has("system-components"), interfaces_present: map.has("system-interfaces"), state_model_present: map.has("system-state-model"), persistence_recovery_present: map.has("system-persistence-recovery"), operating_constraints_present: map.has("system-operating-constraints")}}, {});
    if (invocation.capability_id === capabilities.next_question) {
      const spec = questions[selected.next_focus];
      return {schema_version: STAGE_PROTOCOLS.next_question.output, stage_id: SYSTEM_ONTOLOGY_STAGE_ID, complete: selected.status === "complete", question: spec ? {question_id: spec[0], prompt: spec[1], answer_kind: spec[2], owner_ref: source.profile.owner_route} : null, authority_effect: "none"};
    }
    const receipt = businessReceipt(input);
    const checks = quality(map);
    const sourceCurrent = source.profile.ontology_id === "cav2.define.system-runtime.v1" && source.nodes.nodes.length === 65 && source.relations.relations.length === 131;
    const ready = evaluateReadiness({input: {business_receipt_current: receipt !== null, source_candidate_current: sourceCurrent, system_questions_complete: map.size === questionIds.length, semantic_grounding_pass: checks.semantic_grounding, non_collapse_pass: checks.non_collapse, orthogonality_pass: checks.orthogonality}}, {});
    if (invocation.capability_id === capabilities.evaluate) return {schema_version: STAGE_PROTOCOLS.evaluate.output, stage_id: SYSTEM_ONTOLOGY_STAGE_ID, interaction_complete: map.size === questionIds.length && receipt !== null && sourceCurrent, checks, reason_codes: ready.status === "ready" ? [] : [`system.${ready.repair_focus}-required`], authority_effect: "none"};
    if (invocation.capability_id === capabilities.materialize) {
      if (ready.status !== "ready") throw new TypeError(`System Ontology not ready: ${ready.repair_focus}`);
      const value = candidate(input, receipt);
      return {schema_version: STAGE_PROTOCOLS.materialize.output, stage_id: SYSTEM_ONTOLOGY_STAGE_ID, candidate: value, candidate_digest: digestModuleValue(value), authority_effect: "none"};
    }
    const valid = validCandidate(input.candidate);
    return {schema_version: STAGE_PROTOCOLS.validate.output, stage_id: SYSTEM_ONTOLOGY_STAGE_ID, valid, reason_codes: valid ? [] : ["system.candidate-invalid"], authority_effect: "none"};
  }});
  return Object.freeze({adapter, descriptor});
}
