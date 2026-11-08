import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import test from "node:test";

import {createModulePort} from "../../agent-reasoning-engine/packages/module-port/index.mjs";
import {
  createDefineChatClient,
  createDefineCliClient,
} from "../packages/client-api/index.mjs";
import {
  createDurableDefineRuntime,
  InMemorySessionRepository,
} from "../src/durable-session-runtime.mjs";
import {
  createOntologyStagePort,
  ontologyStageOutputValidators,
} from "../packages/ontology-stage-port/index.mjs";
import {
  createSyntheticOntologyStageAdapter,
  SYNTHETIC_STAGE_ID,
} from "../packages/ontology-stage-port/synthetic-adapter.mjs";

const actor = Object.freeze({
  actor_ref: "actor:define-owner",
  allowed_effects: ["create-session", "open-question", "record-answer", "defer-question", "confirm-artifact"],
});

function configured(options = {}) {
  const fixture = createSyntheticOntologyStageAdapter();
  const modulePort = createModulePort({adapters: [fixture.adapter], output_validators: ontologyStageOutputValidators});
  const stagePort = createOntologyStagePort({module_port: modulePort, descriptors: [fixture.descriptor]});
  const runtime = createDurableDefineRuntime(options);
  return {
    runtime,
    cli: createDefineCliClient({runtime, stage_port: stagePort}),
    chat: createDefineChatClient({runtime, stage_port: stagePort}),
  };
}

function sufficient() {
  return {
    evaluation_id: "evaluation:client-fixture",
    status: "sufficient",
    derivation: "Pinned client test fixture.",
    residue: [],
    evaluator_receipt_ref: "receipt:client-fixture",
    authority_effect: "none",
  };
}

function startRequest(workId = "define-work:client-fixture") {
  return {
    schema_version: "cav2.define-client-start/v1",
    command_id: `command:start:${workId}`,
    work_id: workId,
    expected_revision: 0,
    actor_access_context: actor,
    stage_id: SYNTHETIC_STAGE_ID,
    goal: "Define a product ontology candidate",
    intent: "Preserve one bounded product meaning",
    context: "The user is defining a candidate product promise.",
    consumer: "client-api-test",
    context_sufficiency_evaluation: sufficient(),
  };
}

function nextRequest(workId, revision, commandId = `command:next:${revision}`) {
  return {schema_version: "cav2.define-client-next-question/v1", command_id: commandId, work_id: workId, expected_revision: revision, actor_access_context: actor};
}

function answerRequest(workId, revision, commandId = `command:answer:${revision}`) {
  return {
    schema_version: "cav2.define-client-submit-response/v1",
    command_id: commandId,
    work_id: workId,
    expected_revision: revision,
    actor_access_context: actor,
    response_kind: "answer",
    response: "Help teams agree on one bounded product promise.",
    evidence: {semantic_grounding: true, non_collapse: true, orthogonality: true},
  };
}

test("CLI and chat share all eight stable operations and exact-byte confirmation", () => {
  const {cli, chat} = configured();
  const workId = "define-work:cross-interface";
  const listed = cli.listStages({schema_version: "cav2.define-client-list-stages/v1"});
  assert.equal(listed.ok, true);
  assert.deepEqual(listed.value.stages.map((item) => item.stage_id), [SYNTHETIC_STAGE_ID]);

  const started = cli.startWork(startRequest(workId));
  assert.equal(started.disposition, "confirmed");
  assert.equal(chat.resumeWork({schema_version: "cav2.define-client-resume/v1", work_id: workId}).revision, 1);

  assert.equal(chat.nextQuestion(nextRequest(workId, 1)).revision, 2);
  assert.equal(cli.submitResponse(answerRequest(workId, 2)).revision, 3);
  const readiness = chat.inspectReadiness({schema_version: "cav2.define-client-inspect-readiness/v1", work_id: workId});
  assert.equal(readiness.disposition, "confirmation-required");
  assert.match(readiness.value.candidate_digest, /^[a-f0-9]{64}$/u);

  const confirmed = cli.confirmArtifact({
    schema_version: "cav2.define-client-confirm-artifact/v1",
    command_id: "command:confirm:3",
    work_id: workId,
    expected_revision: 3,
    actor_access_context: actor,
    candidate_bytes: readiness.value.candidate_bytes,
  });
  assert.equal(confirmed.revision, 4);

  const exported = chat.exportArtifact({schema_version: "cav2.define-client-export-artifact/v1", work_id: workId, candidate_bytes: readiness.value.candidate_bytes});
  assert.equal(exported.disposition, "handoff-ready");
  assert.equal(exported.value.candidate.product_purpose, "Help teams agree on one bounded product promise.");
  assert.equal(exported.value.handoff_receipt.authority_effect, "none");
  assert.equal(Object.hasOwn(cli, "stage_port"), false);
  assert.equal(Object.hasOwn(chat, "runtime"), false);
});

test("replay and optimistic revision behavior survive interface changes", () => {
  const repository = new InMemorySessionRepository();
  const {cli, chat} = configured({repository});
  const request = startRequest("define-work:replay");
  const first = cli.startWork(request);
  assert.deepEqual(chat.startWork(request), first);
  const opened = cli.nextQuestion(nextRequest(request.work_id, 1, "command:next:shared"));
  assert.equal(opened.revision, 2);
  const stale = chat.nextQuestion(nextRequest(request.work_id, 1, "command:next:stale"));
  assert.equal(stale.disposition, "conflict");
  assert.deepEqual(stale.reason_codes, ["revision-conflict"]);
  assert.equal(repository.load(request.work_id).events.length, 2);
});

test("deferral posture remains replayable and cannot materialize a candidate", () => {
  const {cli, chat} = configured();
  const workId = "define-work:defer";
  cli.startWork(startRequest(workId));
  cli.nextQuestion(nextRequest(workId, 1));
  const deferred = chat.submitResponse({
    schema_version: "cav2.define-client-submit-response/v1",
    command_id: "command:defer",
    work_id: workId,
    expected_revision: 2,
    actor_access_context: actor,
    response_kind: "defer",
    reason: "Product owner input is still required.",
  });
  assert.equal(deferred.revision, 3);
  assert.equal(deferred.value.snapshot.dispositions.at(-1).disposition, "deferred");
  assert.equal(deferred.value.snapshot.dispositions.at(-1).response_kind, "defer");
  const readiness = cli.inspectReadiness({schema_version: "cav2.define-client-inspect-readiness/v1", work_id: workId});
  assert.equal(readiness.value.candidate, null);
  assert.match(readiness.reason_codes.join("\n"), /define\.stage-response-deferred/u);
});

test("closed requests, actor denial, and candidate drift fail distinctly", () => {
  const {cli} = configured();
  const workId = "define-work:failures";
  assert.equal(cli.startWork({...startRequest(workId), extra: true}).disposition, "invalid");
  assert.equal(cli.resumeWork({schema_version: "wrong", work_id: workId}).disposition, "incompatible-schema");
  assert.equal(cli.startWork(startRequest(workId)).ok, true);
  const denied = cli.nextQuestion({...nextRequest(workId, 1), actor_access_context: {actor_ref: "actor:observer", allowed_effects: []}});
  assert.equal(denied.disposition, "denied");
  cli.nextQuestion(nextRequest(workId, 1, "command:next:allowed"));
  cli.submitResponse(answerRequest(workId, 2));
  const readiness = cli.inspectReadiness({schema_version: "cav2.define-client-inspect-readiness/v1", work_id: workId});
  const drifted = cli.confirmArtifact({schema_version: "cav2.define-client-confirm-artifact/v1", command_id: "command:drift", work_id: workId, expected_revision: 3, actor_access_context: actor, candidate_bytes: `${readiness.value.candidate_bytes} `});
  assert.equal(drifted.disposition, "conflict");
  assert.deepEqual(drifted.reason_codes, ["define.client-confirmation-candidate-drift"]);
});

test("client audit records preserve interface identity without prompt or response bytes", () => {
  const records = [];
  const {cli, chat} = configured({audit: (record) => records.push(record), clock: () => "2026-09-08T00:00:00.000Z"});
  const workId = "define-work:audit";
  cli.startWork(startRequest(workId));
  chat.nextQuestion(nextRequest(workId, 1));
  cli.submitResponse(answerRequest(workId, 2));
  assert.deepEqual(records.map((item) => item.interface_id), ["cli", "chat", "cli"]);
  assert.doesNotMatch(JSON.stringify(records), /bounded product promise|What product meaning/u);
});

test("correction and refusal postures remain explicit durable facts", () => {
  const corrected = configured();
  const correctionWork = "define-work:correction";
  corrected.cli.startWork(startRequest(correctionWork));
  corrected.cli.nextQuestion(nextRequest(correctionWork, 1));
  const correction = corrected.chat.submitResponse({...answerRequest(correctionWork, 2), response_kind: "correction", command_id: "command:correction"});
  assert.equal(correction.value.snapshot.answers[0].response_kind, "correction");
  assert.equal(correction.value.snapshot.dispositions[0].disposition, "corrected");

  const refused = configured();
  const refusalWork = "define-work:refusal";
  refused.cli.startWork(startRequest(refusalWork));
  refused.cli.nextQuestion(nextRequest(refusalWork, 1));
  const refusal = refused.chat.submitResponse({
    schema_version: "cav2.define-client-submit-response/v1",
    command_id: "command:refusal",
    work_id: refusalWork,
    expected_revision: 2,
    actor_access_context: actor,
    response_kind: "refusal",
    reason: "The user declines to define this meaning.",
  });
  assert.equal(refusal.value.snapshot.dispositions[0].response_kind, "refusal");
  assert.equal(refusal.value.snapshot.dispositions[0].disposition, "refused");
});

test("storage failure returns a closed failure and preserves the confirmed revision", () => {
  const repository = new InMemorySessionRepository();
  const {cli} = configured({repository});
  const workId = "define-work:storage";
  cli.startWork(startRequest(workId));
  repository.injectStorageFailure();
  const failed = cli.nextQuestion(nextRequest(workId, 1));
  assert.equal(failed.disposition, "storage-failure");
  assert.equal(failed.revision, 1);
  assert.equal(cli.resumeWork({schema_version: "cav2.define-client-resume/v1", work_id: workId}).revision, 1);
  assert.deepEqual(Object.keys(failed).sort(), ["authority_effect", "disposition", "ok", "operation", "reason_codes", "result_digest", "revision", "schema_version", "value", "work_id"]);
});

test("the published Client API schema names every operation and closes results", () => {
  const schema = JSON.parse(readFileSync(resolve(import.meta.dirname, "../schemas/integration/client-api.schema.json"), "utf8"));
  assert.equal(schema.additionalProperties, false);
  assert.deepEqual(Object.keys(schema.properties.requests.properties).sort(), ["confirmArtifact", "exportArtifact", "inspectReadiness", "listStages", "nextQuestion", "resumeWork", "startWork", "submitResponse"]);
  assert.equal(schema.$defs.result.additionalProperties, false);
  assert.equal(schema.$defs.result.properties.authority_effect.const, "none");
});
