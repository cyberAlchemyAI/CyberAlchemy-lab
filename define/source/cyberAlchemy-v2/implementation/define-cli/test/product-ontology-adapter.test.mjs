import assert from "node:assert/strict";
import test from "node:test";

import {createModulePort} from "../../agent-reasoning-engine/packages/module-port/index.mjs";
import {createDefineCliClient, createDefineChatClient} from "../packages/client-api/index.mjs";
import {createDurableDefineRuntime} from "../src/durable-session-runtime.mjs";
import {createOntologyStagePort, ontologyStageOutputValidators, runOntologyStage} from "../packages/ontology-stage-port/index.mjs";
import {createDefinitionPackPrerequisiteReceipt, createProductOntologyStageAdapter, DEFINITION_PACK_STAGE_ID, PRODUCT_ONTOLOGY_SOURCE_DIGEST, PRODUCT_ONTOLOGY_STAGE_ID} from "../adapters/product-ontology/index.mjs";

const actor = {actor_ref: "actor:alch-language-product-owner", allowed_effects: ["create-session", "open-question", "record-answer", "defer-question", "confirm-artifact"]};
const values = ["Model governed domains with Alch", "Domain owner", "Author domain language", "Shared bounded meaning", "Authority preservation"];

function setup() {
  const fixture = createProductOntologyStageAdapter();
  const modulePort = createModulePort({adapters: [fixture.adapter], output_validators: ontologyStageOutputValidators});
  const port = createOntologyStagePort({module_port: modulePort, descriptors: [fixture.descriptor, fixture.definition_pack_descriptor]});
  const receipt = createDefinitionPackPrerequisiteReceipt({stage_graph_digest: port.stage_graph_digest, module_set_digest: port.module_set_digest, manifest_digest: fixture.adapter.manifest.manifest_digest});
  const runtime = createDurableDefineRuntime();
  return {fixture, port, receipt, cli: createDefineCliClient({runtime, stage_port: port}), chat: createDefineChatClient({runtime, stage_port: port})};
}

function start(client, receipt, workId = "define-work:product-real") {
  return client.startWork({schema_version: "cav2.define-client-start/v1", command_id: `start:${workId}`, work_id: workId, expected_revision: 0, actor_access_context: actor, stage_id: PRODUCT_ONTOLOGY_STAGE_ID, goal: "Author the Alch Product Ontology", intent: "Preserve its product meaning", context: "Use the selected Alch Definition Pack and Product Ontology sources.", consumer: "product-adapter-test", context_sufficiency_evaluation: {evaluation_id: "evaluation:product", status: "sufficient", derivation: "Exact selected sources and owners are present.", residue: [], evaluator_receipt_ref: "receipt:product-context", authority_effect: "none"}, prerequisite_receipts: receipt ? [receipt] : []});
}

function complete() {
  const env = setup(); const workId = "define-work:product-complete"; start(env.cli, env.receipt, workId); let revision = 1;
  for (const response of values) {
    const opened = env.chat.nextQuestion({schema_version: "cav2.define-client-next-question/v1", command_id: `next:${revision}`, work_id: workId, expected_revision: revision, actor_access_context: actor});
    revision = opened.revision;
    const answered = env.cli.submitResponse({schema_version: "cav2.define-client-submit-response/v1", command_id: `answer:${revision}`, work_id: workId, expected_revision: revision, actor_access_context: actor, response_kind: "answer", response, evidence: {semantic_grounding: true, non_collapse: true, orthogonality: true}});
    revision = answered.revision;
  }
  return {...env, workId, revision};
}

test("real Alch Product Ontology reaches exact confirmation and deterministic export", () => {
  const first = complete(); const readiness = first.chat.inspectReadiness({schema_version: "cav2.define-client-inspect-readiness/v1", work_id: first.workId});
  assert.equal(readiness.disposition, "confirmation-required");
  assert.equal(readiness.value.candidate.source_ontology_digest, PRODUCT_ONTOLOGY_SOURCE_DIGEST);
  assert.deepEqual(readiness.value.candidate.product, {capability: values[0], primary_user: values[1], user_job: values[2], outcome: values[3], constraint: values[4]});
  const confirmed = first.cli.confirmArtifact({schema_version: "cav2.define-client-confirm-artifact/v1", command_id: "confirm:product", work_id: first.workId, expected_revision: first.revision, actor_access_context: actor, candidate_bytes: readiness.value.candidate_bytes});
  const exported = first.chat.exportArtifact({schema_version: "cav2.define-client-export-artifact/v1", work_id: first.workId, candidate_bytes: readiness.value.candidate_bytes});
  assert.equal(confirmed.ok, true); assert.equal(exported.disposition, "handoff-ready"); assert.equal(exported.authority_effect, "none");
  const replay = complete().chat.inspectReadiness({schema_version: "cav2.define-client-inspect-readiness/v1", work_id: "define-work:product-complete"});
  assert.equal(replay.value.candidate_bytes, readiness.value.candidate_bytes);
});

test("missing or substituted Definition Pack evidence blocks only Product", () => {
  for (const receipt of [null, {...setup().receipt, candidate_digest: "0".repeat(64)}]) {
    const env = setup();
    const responses = values.map((response, index) => ({question_id: ["product-capability", "primary-user", "user-job", "product-outcome", "product-constraint"][index], response_kind: "answer", response, evidence: {semantic_grounding: true, non_collapse: true, orthogonality: true}}));
    const result = runOntologyStage({stage_port: env.port, stage_id: PRODUCT_ONTOLOGY_STAGE_ID, responses, prerequisite_receipts: receipt ? [receipt] : []});
    assert.equal(result.ok, false); assert.equal(result.candidate, null);
    assert.match(result.reason_codes.join("\n"), /prerequisite|definition-pack|receipt-currency/u);
    assert.equal(env.port.invoke(DEFINITION_PACK_STAGE_ID, "describe", {stage_id: DEFINITION_PACK_STAGE_ID}, `definition:${receipt ? "wrong" : "missing"}`).ok, true);
  }
});

test("Product quality dimensions remain independent", () => {
  for (const field of ["semantic_grounding", "non_collapse", "orthogonality"]) {
    const env = setup();
    const responses = values.map((response, index) => ({question_id: ["product-capability", "primary-user", "user-job", "product-outcome", "product-constraint"][index], response_kind: "answer", response, evidence: {semantic_grounding: true, non_collapse: true, orthogonality: true, [field]: index !== 0}}));
    const result = runOntologyStage({stage_port: env.port, stage_id: PRODUCT_ONTOLOGY_STAGE_ID, responses, prerequisite_receipts: [env.receipt]});
    assert.equal(result.phase, "readiness"); assert.match(result.reason_codes.join("\n"), new RegExp(field.replaceAll("_", "-")));
  }
});
