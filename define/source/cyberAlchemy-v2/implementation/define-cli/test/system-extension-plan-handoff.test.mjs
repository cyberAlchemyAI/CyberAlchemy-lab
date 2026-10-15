import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";

import {canonicalModuleJson} from "../../agent-reasoning-engine/packages/module-port/index.mjs";
import {BUSINESS_ONTOLOGY_STAGE_ID} from "../adapters/business-ontology/index.mjs";
import {PRODUCT_ONTOLOGY_STAGE_ID} from "../adapters/product-ontology/index.mjs";
import {SYSTEM_ONTOLOGY_MANIFEST_DIGEST, SYSTEM_ONTOLOGY_SOURCE_SNAPSHOT_DIGEST, SYSTEM_ONTOLOGY_STAGE_ID} from "../adapters/system-ontology/index.mjs";
import {createConfiguredOntologyAuthoring} from "../configuration/ontology-authoring.mjs";
import {createDefineChatClient, createDefineCliClient} from "../packages/client-api/index.mjs";
import {acceptOntologyHandoffForPlan, PLAN_ONTOLOGY_CONSUMER_ID} from "../packages/plan-handoff-consumer/index.mjs";
import {runOntologyStage} from "../packages/ontology-stage-port/index.mjs";
import {createDurableDefineRuntime} from "../src/durable-session-runtime.mjs";

const actor = {actor_ref: "actor:define-system-runtime-owner", allowed_effects: ["create-session", "open-question", "record-answer", "defer-question", "confirm-artifact"]};
const values = Object.freeze({
  [PRODUCT_ONTOLOGY_STAGE_ID]: ["Author governed domain systems", "Domain owner", "Define exact system meaning", "A source-bound system candidate", "No inferred authority"],
  [BUSINESS_ONTOLOGY_STAGE_ID]: ["Domain owner", "Define runtime", "Session relates to questions and answers", "Only confirmed bytes may export", "Created then active then completed", "Define owner controls runtime meaning"],
  [SYSTEM_ONTOLOGY_STAGE_ID]: ["One durable Define session runtime", "Session core, repository port, and semantic evaluator", "CLI and chat over one shared client boundary", "Created, active, blocked, and completed transitions", "Compare-and-commit with last-confirmed recovery", "Candidate only; no implementation or conformance claim"],
});
const questionIds = Object.freeze({
  [SYSTEM_ONTOLOGY_STAGE_ID]: ["system-runtime-boundary", "system-components", "system-interfaces", "system-state-model", "system-persistence-recovery", "system-operating-constraints"],
});

function clients(stagePort) {
  const runtime = createDurableDefineRuntime();
  return {cli: createDefineCliClient({runtime, stage_port: stagePort}), chat: createDefineChatClient({runtime, stage_port: stagePort})};
}

function completeStage({stagePort, stageId, receipt, suffix}) {
  const client = clients(stagePort);
  const workId = `define-work:${stageId}:${suffix}`;
  const started = client.cli.startWork({schema_version: "cav2.define-client-start/v1", command_id: `start:${workId}`, work_id: workId, expected_revision: 0, actor_access_context: actor, stage_id: stageId, goal: `Author ${stageId}`, intent: "Preserve selected meaning", context: "Use exact source and prerequisite receipt identities.", consumer: "l4-extension-test", context_sufficiency_evaluation: {evaluation_id: `evaluation:${workId}`, status: "sufficient", derivation: "Exact selected source and prerequisite identities are present.", residue: [], evaluator_receipt_ref: `receipt:${workId}`, authority_effect: "none"}, prerequisite_receipts: [receipt]});
  assert.equal(started.ok, true);
  let revision = started.revision;
  for (const response of values[stageId]) {
    const opened = client.chat.nextQuestion({schema_version: "cav2.define-client-next-question/v1", command_id: `next:${workId}:${revision}`, work_id: workId, expected_revision: revision, actor_access_context: actor});
    assert.equal(opened.ok, true);
    revision = opened.revision;
    const answered = client.cli.submitResponse({schema_version: "cav2.define-client-submit-response/v1", command_id: `answer:${workId}:${revision}`, work_id: workId, expected_revision: revision, actor_access_context: actor, response_kind: "answer", response, evidence: {semantic_grounding: true, non_collapse: true, orthogonality: true}});
    assert.equal(answered.ok, true);
    revision = answered.revision;
  }
  const readiness = client.chat.inspectReadiness({schema_version: "cav2.define-client-inspect-readiness/v1", work_id: workId});
  assert.equal(readiness.disposition, "confirmation-required");
  const confirmed = client.cli.confirmArtifact({schema_version: "cav2.define-client-confirm-artifact/v1", command_id: `confirm:${workId}`, work_id: workId, expected_revision: revision, actor_access_context: actor, candidate_bytes: readiness.value.candidate_bytes});
  assert.equal(confirmed.ok, true);
  const exported = client.chat.exportArtifact({schema_version: "cav2.define-client-export-artifact/v1", work_id: workId, candidate_bytes: readiness.value.candidate_bytes});
  assert.equal(exported.disposition, "handoff-ready");
  return exported.value;
}

function completeChain(config, suffix) {
  const product = completeStage({stagePort: config.stage_port, stageId: PRODUCT_ONTOLOGY_STAGE_ID, receipt: config.definition_pack_receipt, suffix: `${suffix}:product`});
  const business = completeStage({stagePort: config.stage_port, stageId: BUSINESS_ONTOLOGY_STAGE_ID, receipt: product.handoff_receipt, suffix: `${suffix}:business`});
  const system = completeStage({stagePort: config.stage_port, stageId: SYSTEM_ONTOLOGY_STAGE_ID, receipt: business.handoff_receipt, suffix: `${suffix}:system`});
  return {product, business, system};
}

function planInput(config, exported) {
  const descriptor = config.stage_port.descriptor(SYSTEM_ONTOLOGY_STAGE_ID);
  return {schema_version: "cav2.plan-ontology-handoff-input/v1", consumer_id: PLAN_ONTOLOGY_CONSUMER_ID, expected_stage: {stage_id: descriptor.stage_id, ontology_type: descriptor.ontology_type, stage_graph_digest: config.stage_port.stage_graph_digest, module_set_digest: config.stage_port.module_set_digest, manifest_digest: descriptor.manifest_digest}, candidate_bytes: exported.candidate_bytes, handoff_receipt: exported.handoff_receipt, claim_posture: "candidate-evidence-only", implementation_authority: "not-granted", authority_effect: "none"};
}

test("a configured System stage completes the exact chain and Plan accepts evidence only", () => {
  const first = createConfiguredOntologyAuthoring();
  assert.deepEqual(first.stage_port.stage_ids, ["definition-pack", PRODUCT_ONTOLOGY_STAGE_ID, BUSINESS_ONTOLOGY_STAGE_ID, SYSTEM_ONTOLOGY_STAGE_ID]);
  assert.deepEqual(first.stage_port.descriptor(SYSTEM_ONTOLOGY_STAGE_ID).alch_entrypoints, ["SystemOntologyQuestion", "SystemOntologyReadiness"]);
  const chain = completeChain(first, "first");
  assert.equal(chain.system.candidate.source_snapshot_digest, SYSTEM_ONTOLOGY_SOURCE_SNAPSHOT_DIGEST);
  assert.equal(chain.system.candidate.source_implementation_status, "not-implemented");
  assert.equal(chain.system.candidate.source_compiler_conformance, "not_evaluable");
  assert.equal(chain.system.candidate.business_candidate_digest, chain.business.candidate_digest);
  const accepted = acceptOntologyHandoffForPlan(planInput(first, chain.system));
  assert.equal(accepted.ok, true);
  assert.equal(accepted.disposition, "accepted-evidence");
  assert.equal(accepted.planning_effect, "none");
  assert.equal(accepted.implementation_authority, "not-granted");

  const replay = createConfiguredOntologyAuthoring();
  const replayChain = completeChain(replay, "replay");
  assert.equal(replay.stage_port.stage_graph_digest, first.stage_port.stage_graph_digest);
  assert.equal(replay.stage_port.module_set_digest, first.stage_port.module_set_digest);
  assert.equal(replayChain.system.candidate_bytes, chain.system.candidate_bytes);
  assert.equal(replayChain.system.handoff_receipt.handoff_receipt_digest, chain.system.handoff_receipt.handoff_receipt_digest);
});

test("multiple stage entry points are explicit and an unavailable System branch leaves Product bytes unchanged", () => {
  const full = createConfiguredOntologyAuthoring();
  const withoutSystem = createConfiguredOntologyAuthoring({include_system: false});
  const fullProduct = completeStage({stagePort: full.stage_port, stageId: PRODUCT_ONTOLOGY_STAGE_ID, receipt: full.definition_pack_receipt, suffix: "full-entry"});
  const smallerProduct = completeStage({stagePort: withoutSystem.stage_port, stageId: PRODUCT_ONTOLOGY_STAGE_ID, receipt: withoutSystem.definition_pack_receipt, suffix: "smaller-entry"});
  assert.equal(fullProduct.candidate_bytes, smallerProduct.candidate_bytes);
  assert.equal(withoutSystem.stage_port.descriptor(SYSTEM_ONTOLOGY_STAGE_ID), null);
  const client = clients(withoutSystem.stage_port);
  const unknown = client.cli.startWork({schema_version: "cav2.define-client-start/v1", command_id: "start:unknown-system", work_id: "define-work:unknown-system", expected_revision: 0, actor_access_context: actor, stage_id: SYSTEM_ONTOLOGY_STAGE_ID, goal: "Unknown", intent: "No fallback", context: "System stage omitted", consumer: "l4-extension-test", prerequisite_receipts: []});
  assert.equal(unknown.disposition, "unavailable");
  const configurationBytes = readFileSync(new URL("../configuration/ontology-authoring.mjs", import.meta.url), "utf8");
  assert.doesNotMatch(configurationBytes, /\/src\//u);
  assert.doesNotMatch(configurationBytes, /packages\/client-api|packages\/ontology-stage-port\/index\.mjs.*write/u);
});

test("System and Plan reject stale, drifted, incompatible, and authority-bearing evidence", () => {
  const current = createConfiguredOntologyAuthoring();
  const chain = completeChain(current, "negative");
  const staleConfig = createConfiguredOntologyAuthoring({include_system: false});
  const staleProduct = completeStage({stagePort: staleConfig.stage_port, stageId: PRODUCT_ONTOLOGY_STAGE_ID, receipt: staleConfig.definition_pack_receipt, suffix: "stale-product"});
  const staleBusiness = completeStage({stagePort: staleConfig.stage_port, stageId: BUSINESS_ONTOLOGY_STAGE_ID, receipt: staleProduct.handoff_receipt, suffix: "stale-business"});
  const responses = questionIds[SYSTEM_ONTOLOGY_STAGE_ID].map((question_id, index) => ({question_id, response_kind: "answer", response: values[SYSTEM_ONTOLOGY_STAGE_ID][index], evidence: {semantic_grounding: true, non_collapse: true, orthogonality: true}}));
  const staleRun = runOntologyStage({stage_port: current.stage_port, stage_id: SYSTEM_ONTOLOGY_STAGE_ID, responses, prerequisite_receipts: [staleBusiness.handoff_receipt]});
  assert.equal(staleRun.phase, "dependencies");

  const valid = planInput(current, chain.system);
  const cases = [
    {...valid, schema_version: "unsupported"},
    {...valid, expected_stage: {...valid.expected_stage, stage_graph_digest: "0".repeat(64)}},
    {...valid, candidate_bytes: `${valid.candidate_bytes}\n`},
    {...valid, authority_effect: "grant"},
    {...valid, handoff_receipt: {...valid.handoff_receipt, handoff_receipt_digest: "0".repeat(64)}},
    {...valid, candidate_bytes: canonicalModuleJson({...chain.system.candidate, authority_effect: "grant"})},
  ];
  for (const value of cases) assert.equal(acceptOntologyHandoffForPlan(value).ok, false);

  for (const field of ["semantic_grounding", "non_collapse", "orthogonality"]) {
    const defective = responses.map((response, index) => ({...response, evidence: {...response.evidence, [field]: index !== 0}}));
    const run = runOntologyStage({stage_port: current.stage_port, stage_id: SYSTEM_ONTOLOGY_STAGE_ID, responses: defective, prerequisite_receipts: [chain.business.handoff_receipt]});
    assert.equal(run.phase, "readiness");
    assert.match(run.reason_codes.join("\n"), new RegExp(field.replaceAll("_", "-")));
  }
  assert.equal(current.stage_port.descriptor(SYSTEM_ONTOLOGY_STAGE_ID).manifest_digest, SYSTEM_ONTOLOGY_MANIFEST_DIGEST);
});
