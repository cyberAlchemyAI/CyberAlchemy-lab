import assert from "node:assert/strict";
import test from "node:test";

import {createModulePort, digestModuleValue} from "../../agent-reasoning-engine/packages/module-port/index.mjs";
import {createDefineCliClient, createDefineChatClient} from "../packages/client-api/index.mjs";
import {createDurableDefineRuntime} from "../src/durable-session-runtime.mjs";
import {createOntologyStagePort, ontologyStageOutputValidators, runOntologyStage} from "../packages/ontology-stage-port/index.mjs";
import {BUSINESS_ONTOLOGY_SOURCE_DIGEST, BUSINESS_ONTOLOGY_STAGE_ID, createBusinessOntologyStageAdapter} from "../adapters/business-ontology/index.mjs";
import {createDefinitionPackPrerequisiteReceipt, createProductOntologyStageAdapter, DEFINITION_PACK_STAGE_ID, PRODUCT_ONTOLOGY_STAGE_ID} from "../adapters/product-ontology/index.mjs";

const actor = {actor_ref: "actor:alch-language-owner", allowed_effects: ["create-session", "open-question", "record-answer", "defer-question", "confirm-artifact"]};
const productValues = ["Model governed domains with Alch", "Domain owner", "Author domain language", "Shared bounded meaning", "Authority preservation"];
const businessValues = ["Domain owner", "Order fulfillment", "Order relates to fulfillment request", "Only payable orders may be fulfilled", "Requested then fulfilled or rejected", "Fulfillment owner decides within the order boundary"];
const businessQuestionIds = ["business-meaning-owner", "business-bounded-model", "business-concepts-and-relationships", "business-domain-rule", "business-lifecycle", "business-authority-boundary"];

function setup({reverse = false, business = true} = {}) {
  const productFixture = createProductOntologyStageAdapter();
  const businessFixture = createBusinessOntologyStageAdapter();
  const adapters = business ? [productFixture.adapter, businessFixture.adapter] : [productFixture.adapter];
  const descriptors = business
    ? [productFixture.definition_pack_descriptor, productFixture.descriptor, businessFixture.descriptor]
    : [productFixture.definition_pack_descriptor, productFixture.descriptor];
  if (reverse) { adapters.reverse(); descriptors.reverse(); }
  const modulePort = createModulePort({adapters, output_validators: ontologyStageOutputValidators});
  const port = createOntologyStagePort({module_port: modulePort, descriptors});
  const definitionReceipt = createDefinitionPackPrerequisiteReceipt({stage_graph_digest: port.stage_graph_digest, module_set_digest: port.module_set_digest, manifest_digest: productFixture.adapter.manifest.manifest_digest});
  return {productFixture, businessFixture, port, definitionReceipt};
}

function clients(port) {
  const runtime = createDurableDefineRuntime();
  return {cli: createDefineCliClient({runtime, stage_port: port}), chat: createDefineChatClient({runtime, stage_port: port})};
}

function start(client, {workId, stageId, receipt}) {
  return client.startWork({schema_version: "cav2.define-client-start/v1", command_id: `start:${workId}`, work_id: workId, expected_revision: 0, actor_access_context: actor, stage_id: stageId, goal: `Author ${stageId}`, intent: "Preserve selected ontology meaning", context: "Use the selected Alch ontology sources and exact prerequisite evidence.", consumer: "business-adapter-test", context_sufficiency_evaluation: {evaluation_id: `evaluation:${workId}`, status: "sufficient", derivation: "Exact selected sources and owners are present.", residue: [], evaluator_receipt_ref: `receipt:${workId}`, authority_effect: "none"}, prerequisite_receipts: receipt ? [receipt] : []});
}

function completeClientStage({port, stageId, receipt, values, workId}) {
  const client = clients(port);
  start(client.cli, {workId, stageId, receipt});
  let revision = 1;
  for (const response of values) {
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

function currentProduct(env, suffix = "current") {
  return completeClientStage({port: env.port, stageId: PRODUCT_ONTOLOGY_STAGE_ID, receipt: env.definitionReceipt, values: productValues, workId: `define-work:product-${suffix}`});
}

function businessResponses(overrides = {}) {
  return businessValues.map((response, index) => ({question_id: businessQuestionIds[index], response_kind: "answer", response, evidence: {semantic_grounding: true, non_collapse: true, orthogonality: true, ...overrides[index]}}));
}

test("Product then Business preserves the exact prerequisite identity and deterministic bytes", () => {
  const first = setup();
  const product = currentProduct(first, "business-first");
  const business = completeClientStage({port: first.port, stageId: BUSINESS_ONTOLOGY_STAGE_ID, receipt: product.handoff_receipt, values: businessValues, workId: "define-work:business-first"});
  assert.equal(business.candidate.source_ontology_digest, BUSINESS_ONTOLOGY_SOURCE_DIGEST);
  assert.equal(business.candidate.product_candidate_digest, product.candidate_digest);
  assert.equal(business.candidate.product_handoff_receipt_digest, product.handoff_receipt.handoff_receipt_digest);
  assert.equal(business.candidate.dependency_receipt_set_digest, digestModuleValue([product.handoff_receipt]));
  assert.deepEqual(business.candidate.business, {meaning_owner: businessValues[0], bounded_model: businessValues[1], concepts_and_relationships: businessValues[2], domain_rule: businessValues[3], lifecycle: businessValues[4], authority_boundary: businessValues[5]});
  const hostile = first.port.invoke(BUSINESS_ONTOLOGY_STAGE_ID, "validate", {stage_id: BUSINESS_ONTOLOGY_STAGE_ID, candidate: {...business.candidate, undeclared: true}}, "business:closed-candidate");
  assert.equal(hostile.ok, true);
  assert.equal(hostile.value.valid, false);

  const replayEnv = setup({reverse: true});
  const replayProduct = currentProduct(replayEnv, "business-replay");
  const replayBusiness = completeClientStage({port: replayEnv.port, stageId: BUSINESS_ONTOLOGY_STAGE_ID, receipt: replayProduct.handoff_receipt, values: businessValues, workId: "define-work:business-replay"});
  assert.equal(replayEnv.port.stage_graph_digest, first.port.stage_graph_digest);
  assert.equal(replayEnv.port.module_set_digest, first.port.module_set_digest);
  assert.equal(replayBusiness.candidate_bytes, business.candidate_bytes);
  assert.equal(replayBusiness.handoff_receipt.handoff_receipt_digest, business.handoff_receipt.handoff_receipt_digest);
  assert.deepEqual(first.port.stage_ids, [DEFINITION_PACK_STAGE_ID, PRODUCT_ONTOLOGY_STAGE_ID, BUSINESS_ONTOLOGY_STAGE_ID]);
});

test("missing, tampered, stale, or wrong-provider Product evidence blocks only Business", () => {
  const env = setup();
  const product = currentProduct(env, "isolation");
  const staleEnv = setup({business: false});
  const stale = currentProduct(staleEnv, "stale").handoff_receipt;
  const tampered = {...product.handoff_receipt, candidate_digest: "0".repeat(64)};
  const wrongProviderMaterial = {...product.handoff_receipt, manifest_digest: "1".repeat(64)};
  delete wrongProviderMaterial.handoff_receipt_digest;
  const wrongProvider = {...wrongProviderMaterial, handoff_receipt_digest: digestModuleValue(wrongProviderMaterial)};
  for (const receipt of [null, tampered, stale, wrongProvider]) {
    const result = runOntologyStage({stage_port: env.port, stage_id: BUSINESS_ONTOLOGY_STAGE_ID, responses: businessResponses(), prerequisite_receipts: receipt ? [receipt] : []});
    assert.equal(result.ok, false);
    assert.equal(result.phase, "dependencies");
    assert.match(result.reason_codes.join("\n"), /prerequisite|receipt-currency/u);
    assert.equal(env.port.invoke(PRODUCT_ONTOLOGY_STAGE_ID, "describe", {stage_id: PRODUCT_ONTOLOGY_STAGE_ID}, `product:${receipt?.handoff_receipt_digest ?? "missing"}`).ok, true);
  }
});

test("Business quality dimensions remain independent while Product bytes remain stable", () => {
  const baseline = setup();
  const baselineProduct = currentProduct(baseline, "quality-baseline");
  for (const field of ["semantic_grounding", "non_collapse", "orthogonality"]) {
    const env = setup();
    const product = currentProduct(env, `quality-${field}`);
    const responses = businessResponses({0: {[field]: false}});
    const result = runOntologyStage({stage_port: env.port, stage_id: BUSINESS_ONTOLOGY_STAGE_ID, responses, prerequisite_receipts: [product.handoff_receipt]});
    assert.equal(result.phase, "readiness");
    assert.match(result.reason_codes.join("\n"), new RegExp(field.replaceAll("_", "-")));
    assert.equal(product.candidate_bytes, baselineProduct.candidate_bytes);
  }
});
