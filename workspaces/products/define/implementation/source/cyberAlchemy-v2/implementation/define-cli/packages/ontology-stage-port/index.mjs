import {
  canonicalModuleJson,
  digestModuleValue,
} from "../../../agent-reasoning-engine/packages/module-port/index.mjs";
import {execute as decideDependency} from "../../generated/define-integration/entries/StageDependency/app/function/behavior.mjs";
import {execute as decideResponse} from "../../generated/define-integration/entries/StageResponse/app/function/behavior.mjs";
import {execute as decideReadiness} from "../../generated/define-integration/entries/StageReadiness/app/function/behavior.mjs";
import {execute as decideHandoff} from "../../generated/define-integration/entries/StageHandoff/app/function/behavior.mjs";

export const STAGE_DESCRIPTOR_SCHEMA = "cav2.define-ontology-stage/v1";
export const STAGE_PORT_RESULT_SCHEMA = "cav2.define-ontology-stage-result/v1";
export const STAGE_HANDOFF_SCHEMA = "cav2.define-ontology-stage-handoff/v1";

export const STAGE_PROTOCOLS = Object.freeze({
  describe: Object.freeze({input: "cav2.define-stage-describe-query/v1", output: "cav2.define-stage-description/v1"}),
  next_question: Object.freeze({input: "cav2.define-stage-question-query/v1", output: "cav2.define-stage-question/v1"}),
  evaluate: Object.freeze({input: "cav2.define-stage-evaluation-query/v1", output: "cav2.define-stage-evaluation/v1"}),
  materialize: Object.freeze({input: "cav2.define-stage-materialization-query/v1", output: "cav2.define-stage-candidate/v1"}),
  validate: Object.freeze({input: "cav2.define-stage-validation-query/v1", output: "cav2.define-stage-validation/v1"}),
});

const SHA256 = /^[a-f0-9]{64}$/u;
const ID = /^[a-z0-9](?:[-a-z0-9._/:]{0,126}[a-z0-9])?$/u;
const OPERATIONS = Object.freeze(Object.keys(STAGE_PROTOCOLS));
const DESCRIPTOR_KEYS = new Set([
  "schema_version", "stage_id", "ontology_type", "module_id", "module_version",
  "manifest_digest", "prerequisite_stage_ids", "capabilities", "alch_entrypoints",
  "authority_effect",
]);
const CAPABILITY_KEYS = new Set(OPERATIONS);

function record(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    && (Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null);
}

function exactKeys(value, allowed) {
  return record(value) && Object.keys(value).every((key) => allowed.has(key))
    && Object.keys(value).length === allowed.size;
}

function clone(value) {
  return JSON.parse(canonicalModuleJson(value));
}

function freeze(value) {
  if (!value || typeof value !== "object" || Object.isFrozen(value)) return value;
  Object.freeze(value);
  for (const child of Object.values(value)) freeze(child);
  return value;
}

function stableStrings(values) {
  return [...new Set(values)].sort();
}

function sealed(fields) {
  const material = clone({...fields, authority_effect: "none"});
  return freeze({...material, result_digest: digestModuleValue(material)});
}

function validStringList(value, predicate = (item) => typeof item === "string" && item.length > 0) {
  return Array.isArray(value) && value.every(predicate) && new Set(value).size === value.length;
}

export function validateStageDescriptor(value) {
  return exactKeys(value, DESCRIPTOR_KEYS)
    && value.schema_version === STAGE_DESCRIPTOR_SCHEMA
    && ID.test(value.stage_id ?? "")
    && ID.test(value.ontology_type ?? "")
    && ID.test(value.module_id ?? "")
    && typeof value.module_version === "string" && value.module_version.length > 0
    && SHA256.test(value.manifest_digest ?? "")
    && validStringList(value.prerequisite_stage_ids, (item) => ID.test(item))
    && exactKeys(value.capabilities, CAPABILITY_KEYS)
    && OPERATIONS.every((operation) => ID.test(value.capabilities[operation] ?? ""))
    && new Set(Object.values(value.capabilities)).size === OPERATIONS.length
    && validStringList(value.alch_entrypoints)
    && value.authority_effect === "none";
}

function outputExact(value, keys, schema) {
  return exactKeys(value, new Set([...keys, "schema_version", "stage_id", "authority_effect"]))
    && value.schema_version === schema && ID.test(value.stage_id ?? "")
    && value.authority_effect === "none";
}

export function validateStageDescription(value) {
  return outputExact(value, ["ontology_type", "label", "purpose", "output_artifact_kind", "owner_ref"], STAGE_PROTOCOLS.describe.output)
    && ID.test(value.ontology_type ?? "")
    && [value.label, value.purpose, value.output_artifact_kind, value.owner_ref].every((item) => typeof item === "string" && item.length > 0);
}

export function validateStageQuestion(value) {
  const base = outputExact(value, ["complete", "question"], STAGE_PROTOCOLS.next_question.output)
    && typeof value.complete === "boolean";
  if (!base) return false;
  if (value.complete) return value.question === null;
  return exactKeys(value.question, new Set(["question_id", "prompt", "answer_kind", "owner_ref"]))
    && ID.test(value.question.question_id ?? "")
    && [value.question.prompt, value.question.answer_kind, value.question.owner_ref].every((item) => typeof item === "string" && item.length > 0);
}

export function validateStageEvaluation(value) {
  return outputExact(value, ["interaction_complete", "checks", "reason_codes"], STAGE_PROTOCOLS.evaluate.output)
    && typeof value.interaction_complete === "boolean"
    && exactKeys(value.checks, new Set(["semantic_grounding", "non_collapse", "orthogonality"]))
    && Object.values(value.checks).every((item) => typeof item === "boolean")
    && validStringList(value.reason_codes);
}

export function validateStageCandidate(value) {
  if (!outputExact(value, ["candidate", "candidate_digest"], STAGE_PROTOCOLS.materialize.output)
    || !record(value.candidate) || !SHA256.test(value.candidate_digest ?? "")) return false;
  return digestModuleValue(value.candidate) === value.candidate_digest;
}

export function validateStageValidation(value) {
  return outputExact(value, ["valid", "reason_codes"], STAGE_PROTOCOLS.validate.output)
    && typeof value.valid === "boolean" && validStringList(value.reason_codes)
    && (value.valid ? value.reason_codes.length === 0 : value.reason_codes.length > 0);
}

export const ontologyStageOutputValidators = Object.freeze({
  [STAGE_PROTOCOLS.describe.output]: validateStageDescription,
  [STAGE_PROTOCOLS.next_question.output]: validateStageQuestion,
  [STAGE_PROTOCOLS.evaluate.output]: validateStageEvaluation,
  [STAGE_PROTOCOLS.materialize.output]: validateStageCandidate,
  [STAGE_PROTOCOLS.validate.output]: validateStageValidation,
});

function normalizeDescriptors(descriptors) {
  if (!Array.isArray(descriptors)) throw new TypeError("Ontology stage descriptors must be an array.");
  const values = descriptors.map((descriptor) => {
    if (!validateStageDescriptor(descriptor)) throw new TypeError("Ontology stage descriptor is invalid.");
    return clone({...descriptor, prerequisite_stage_ids: [...descriptor.prerequisite_stage_ids].sort()});
  });
  for (const key of ["stage_id", "ontology_type"]) {
    if (new Set(values.map((item) => item[key])).size !== values.length) throw new TypeError(`Ontology stage ${key} is duplicated.`);
  }
  const capabilityIds = values.flatMap((item) => Object.values(item.capabilities));
  if (new Set(capabilityIds).size !== capabilityIds.length) throw new TypeError("Ontology stage capability is duplicated.");
  const byId = new Map(values.map((item) => [item.stage_id, item]));
  for (const descriptor of values) {
    if (descriptor.prerequisite_stage_ids.includes(descriptor.stage_id)) throw new TypeError("Ontology stage cannot depend on itself.");
    for (const prerequisite of descriptor.prerequisite_stage_ids) {
      if (!byId.has(prerequisite)) throw new TypeError(`Ontology stage dependency is missing: ${descriptor.stage_id} -> ${prerequisite}`);
    }
  }
  const pending = new Map(values.map((item) => [item.stage_id, new Set(item.prerequisite_stage_ids)]));
  const order = [];
  while (pending.size > 0) {
    const ready = [...pending.entries()].filter(([, dependencies]) => dependencies.size === 0)
      .map(([stageId]) => stageId).sort();
    if (ready.length === 0) throw new TypeError("Ontology stage dependency cycle detected.");
    for (const stageId of ready) {
      order.push(stageId);
      pending.delete(stageId);
      for (const dependencies of pending.values()) dependencies.delete(stageId);
    }
  }
  const ordered = order.map((stageId) => byId.get(stageId));
  return {ordered, byId, graphDigest: digestModuleValue({schema_version: "cav2.define-stage-graph/v1", stages: ordered, authority_effect: "none"})};
}

function portFailure(stageId, disposition, reasonCodes, extras = {}) {
  return sealed({
    schema_version: STAGE_PORT_RESULT_SCHEMA,
    ok: false,
    disposition,
    stage_id: stageId,
    value: null,
    reason_codes: stableStrings(reasonCodes),
    module_receipt: extras.module_receipt ?? null,
    stage_graph_digest: extras.stage_graph_digest ?? null,
    module_set_digest: extras.module_set_digest ?? null,
  });
}

export function createOntologyStagePort({module_port: modulePort, descriptors = []} = {}) {
  if (!modulePort || typeof modulePort.invoke !== "function" || typeof modulePort.inspect !== "function") {
    throw new TypeError("Ontology stage port requires a Module Port.");
  }
  const graph = normalizeDescriptors(descriptors);
  const moduleInspection = modulePort.inspect();
  const invoke = (stageId, operation, input, invocationId) => {
    const descriptor = graph.byId.get(stageId);
    if (!descriptor) return portFailure(stageId, "unavailable", ["define.stage-unavailable"], {
      stage_graph_digest: graph.graphDigest, module_set_digest: moduleInspection.module_set_digest,
    });
    if (!OPERATIONS.includes(operation)) return portFailure(stageId, "blocked", ["define.stage-operation-invalid"], {
      stage_graph_digest: graph.graphDigest, module_set_digest: moduleInspection.module_set_digest,
    });
    const moduleResult = modulePort.invoke({
      schema_version: "are.module-invocation/v1",
      invocation_id: invocationId,
      consumer_id: "define-ontology-stage-port",
      capability_id: descriptor.capabilities[operation],
      input: clone(input),
      dependency_posture: "required-for-operation",
      authority_effect: "none",
    });
    if (moduleResult.disposition !== "available") return portFailure(stageId, moduleResult.disposition, moduleResult.reason_codes, {
      module_receipt: moduleResult.receipt,
      stage_graph_digest: graph.graphDigest,
      module_set_digest: moduleInspection.module_set_digest,
    });
    if (moduleResult.receipt.module_id !== descriptor.module_id
      || moduleResult.receipt.module_version !== descriptor.module_version
      || moduleResult.receipt.manifest_digest !== descriptor.manifest_digest
      || moduleResult.value.stage_id !== stageId) {
      return portFailure(stageId, "blocked", ["define.stage-provider-identity-drift"], {
        module_receipt: moduleResult.receipt,
        stage_graph_digest: graph.graphDigest,
        module_set_digest: moduleInspection.module_set_digest,
      });
    }
    return sealed({
      schema_version: STAGE_PORT_RESULT_SCHEMA,
      ok: true,
      disposition: "available",
      stage_id: stageId,
      value: moduleResult.value,
      reason_codes: [],
      module_receipt: moduleResult.receipt,
      stage_graph_digest: graph.graphDigest,
      module_set_digest: moduleInspection.module_set_digest,
    });
  };
  return freeze({
    schema_version: "cav2.define-ontology-stage-port/v1",
    stage_graph_digest: graph.graphDigest,
    module_set_digest: moduleInspection.module_set_digest,
    stage_ids: graph.ordered.map((item) => item.stage_id),
    authority_effect: "none",
    inspect() {
      return freeze({
        schema_version: "cav2.define-stage-graph-inspection/v1",
        stage_graph_digest: graph.graphDigest,
        module_set_digest: moduleInspection.module_set_digest,
        stages: clone(graph.ordered),
        discovery: "disabled",
        fallback: "forbidden",
        authority_effect: "none",
      });
    },
    descriptor(stageId) {
      return graph.byId.has(stageId) ? clone(graph.byId.get(stageId)) : null;
    },
    invoke,
  });
}

function stopped(stagePort, stageId, phase, result, extras = {}) {
  return sealed({
    schema_version: "cav2.define-stage-run/v1",
    ok: false,
    disposition: result.disposition === "available" ? "blocked" : result.disposition,
    stage_id: stageId,
    phase,
    candidate: extras.candidate ?? null,
    candidate_digest: extras.candidate_digest ?? null,
    handoff_receipt: null,
    reason_codes: result.reason_codes?.length ? result.reason_codes : [`define.stage-${phase}-blocked`],
    evidence: extras.evidence ?? {},
    stage_graph_digest: stagePort?.stage_graph_digest ?? null,
    module_set_digest: stagePort?.module_set_digest ?? null,
  });
}

export function runOntologyStage({stage_port: stagePort, stage_id: stageId, responses = [], prerequisite_receipts = [], confirmation_candidate_digest = null} = {}) {
  const descriptor = stagePort?.descriptor?.(stageId);
  if (!descriptor) return stopped(stagePort, stageId, "resolve", {
    disposition: "unavailable",
    reason_codes: ["define.stage-unavailable"],
  });
  const responseDecisions = responses.map((response) => decideResponse({input: {
    response_kind: ["answer", "correction", "refusal", "defer"].includes(response?.response_kind) ? response.response_kind : "unsupported",
    response_present: typeof response?.response === "string" && response.response.trim().length > 0,
  }}, {}));
  const responseBlock = responseDecisions.find((item) => item.status !== "accept");
  if (responseBlock) return stopped(stagePort, stageId, "response", {disposition: "available", reason_codes: [`define.stage-response-${responseBlock.disposition}`]}, {evidence: {response_decisions: responseDecisions}});

  const expected = descriptor.prerequisite_stage_ids;
  const supplied = new Map(prerequisite_receipts.map((receipt) => [receipt?.stage_id, receipt]));
  const prerequisitesComplete = expected.every((id) => supplied.has(id)) && supplied.size === expected.length;
  const receiptsCurrent = prerequisitesComplete && expected.every((id) => {
    const receipt = supplied.get(id);
    const prerequisiteDescriptor = stagePort.descriptor(id);
    if (receipt?.schema_version !== STAGE_HANDOFF_SCHEMA || receipt?.stage_id !== id
      || receipt?.authority_effect !== "none" || !SHA256.test(receipt?.candidate_digest ?? "")
      || !SHA256.test(receipt?.handoff_receipt_digest ?? "")
      || receipt?.stage_graph_digest !== stagePort.stage_graph_digest
      || receipt?.module_set_digest !== stagePort.module_set_digest
      || receipt?.manifest_digest !== prerequisiteDescriptor?.manifest_digest) return false;
    const material = clone(receipt);
    delete material.handoff_receipt_digest;
    return digestModuleValue(material) === receipt.handoff_receipt_digest;
  });
  const dependencyDecision = decideDependency({input: {prerequisites_complete: prerequisitesComplete, receipts_current: receiptsCurrent}}, {});
  if (dependencyDecision.status !== "ready") return stopped(stagePort, stageId, "dependencies", {disposition: "available", reason_codes: [`define.stage-${dependencyDecision.repair_focus}`]}, {evidence: {dependency_decision: dependencyDecision}});

  const baseInput = {
    stage_id: stageId,
    responses: clone(responses),
    prerequisite_receipts: clone(prerequisite_receipts),
    stage_graph_digest: stagePort.stage_graph_digest,
    module_set_digest: stagePort.module_set_digest,
  };
  const description = stagePort.invoke(stageId, "describe", {stage_id: stageId}, `define-stage:${stageId}:describe`);
  if (!description.ok) return stopped(stagePort, stageId, "describe", description);
  const question = stagePort.invoke(stageId, "next_question", baseInput, `define-stage:${stageId}:question`);
  if (!question.ok) return stopped(stagePort, stageId, "next-question", question);
  const evaluation = stagePort.invoke(stageId, "evaluate", baseInput, `define-stage:${stageId}:evaluate`);
  if (!evaluation.ok) return stopped(stagePort, stageId, "evaluate", evaluation);
  const readinessDecision = decideReadiness({input: {
    interaction_complete: evaluation.value.interaction_complete && question.value.complete,
    semantic_grounding_pass: evaluation.value.checks.semantic_grounding,
    non_collapse_pass: evaluation.value.checks.non_collapse,
    orthogonality_pass: evaluation.value.checks.orthogonality,
    dependencies_ready: true,
  }}, {});
  const evidence = {
    dependency_decision: dependencyDecision,
    response_decisions: responseDecisions,
    description_receipt: description.module_receipt.receipt_digest,
    question_receipt: question.module_receipt.receipt_digest,
    evaluation_receipt: evaluation.module_receipt.receipt_digest,
    readiness_decision: readinessDecision,
  };
  if (readinessDecision.status !== "ready") return stopped(stagePort, stageId, "readiness", {disposition: "available", reason_codes: stableStrings([...evaluation.value.reason_codes, `define.stage-${readinessDecision.repair_focus}`])}, {evidence});

  const materialized = stagePort.invoke(stageId, "materialize", baseInput, `define-stage:${stageId}:materialize`);
  if (!materialized.ok) return stopped(stagePort, stageId, "materialize", materialized, {evidence});
  evidence.materialization_receipt = materialized.module_receipt.receipt_digest;
  const validation = stagePort.invoke(stageId, "validate", {stage_id: stageId, candidate: materialized.value.candidate}, `define-stage:${stageId}:validate`);
  if (!validation.ok) return stopped(stagePort, stageId, "validate", validation, {candidate: materialized.value.candidate, candidate_digest: materialized.value.candidate_digest, evidence});
  evidence.validation_receipt = validation.module_receipt.receipt_digest;
  const handoffDecision = decideHandoff({input: {
    candidate_present: true,
    adapter_validation_pass: validation.value.valid,
    user_confirmed: confirmation_candidate_digest !== null,
    confirmation_matches: confirmation_candidate_digest === materialized.value.candidate_digest,
    dependency_receipts_current: true,
  }}, {});
  evidence.handoff_decision = handoffDecision;
  if (handoffDecision.status !== "ready") return stopped(stagePort, stageId, "handoff", {disposition: "available", reason_codes: stableStrings([...validation.value.reason_codes, `define.stage-${handoffDecision.repair_focus}`])}, {candidate: materialized.value.candidate, candidate_digest: materialized.value.candidate_digest, evidence});

  const handoffMaterial = clone({
    schema_version: STAGE_HANDOFF_SCHEMA,
    stage_id: stageId,
    ontology_type: descriptor.ontology_type,
    stage_graph_digest: stagePort.stage_graph_digest,
    module_set_digest: stagePort.module_set_digest,
    manifest_digest: descriptor.manifest_digest,
    candidate_digest: materialized.value.candidate_digest,
    prerequisite_receipt_set_digest: digestModuleValue(prerequisite_receipts),
    confirmation_digest: digestModuleValue({stage_id: stageId, candidate_digest: confirmation_candidate_digest}),
    adapter_receipt_digests: stableStrings([
      evidence.description_receipt, evidence.question_receipt, evidence.evaluation_receipt,
      evidence.materialization_receipt, evidence.validation_receipt,
    ]),
    authority_effect: "none",
  });
  const handoffReceipt = freeze({...handoffMaterial, handoff_receipt_digest: digestModuleValue(handoffMaterial)});
  return sealed({
    schema_version: "cav2.define-stage-run/v1",
    ok: true,
    disposition: "handoff-ready",
    stage_id: stageId,
    phase: "complete",
    candidate: materialized.value.candidate,
    candidate_digest: materialized.value.candidate_digest,
    handoff_receipt: handoffReceipt,
    reason_codes: [],
    evidence,
    stage_graph_digest: stagePort.stage_graph_digest,
    module_set_digest: stagePort.module_set_digest,
  });
}
