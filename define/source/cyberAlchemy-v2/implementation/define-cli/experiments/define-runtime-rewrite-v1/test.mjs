import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {test} from "node:test";
import {invoke} from "./generated/app/function/index.mjs";
import {createSession, transition} from "./runtime.mjs";
import {createDurableDefineRuntime} from "../../src/durable-session-runtime.mjs";

const actor = {
  actor_ref: "actor:synthetic-define-owner",
  allowed_effects: ["create-session", "open-question", "record-answer", "defer-question"],
};

function currentCommand(id, type, revision, payload) {
  return {
    schema_version: "cav2.define-session-command/v1",
    command_id: id,
    command_type: type,
    session_id: "define-session:rewrite-parity",
    expected_revision: revision,
    actor_access_context: actor,
    payload_schema_version: "v1",
    payload,
  };
}

test("generated source and artifact manifest remain bound", () => {
  const manifest = JSON.parse(readFileSync(new URL("./generated/manifest.json", import.meta.url)));
  const source = readFileSync(new URL("./question-cycle.alch", import.meta.url));
  assert.equal(createHash("sha256").update(source).digest("hex"), manifest.source_sha256);
  assert.equal(manifest.authority_effect, "none");
  for (const [path, hash] of Object.entries(manifest.files)) {
    const bytes = readFileSync(new URL(`./generated/${path}`, import.meta.url));
    assert.equal(createHash("sha256").update(bytes).digest("hex"), hash, path);
  }
});

test("generated decision is total and non-overlapping for the bounded fact space", async () => {
  let count = 0;
  for (const command of ["open-question", "record-answer", "defer-question"])
    for (const context_sufficient of [false, true])
      for (const current_question_present of [false, true])
        for (const question_matches of [false, true])
          for (const payload_complete of [false, true]) {
            const decision = await invoke({command, context_sufficient, current_question_present, question_matches, payload_complete});
            assert.ok(["accepted", "block"].includes(decision.status));
            assert.equal(decision.authority_effect, "none");
            count += 1;
          }
  assert.equal(count, 48);
});

test("open, answer, and defer change only the in-memory candidate state", async () => {
  const original = createSession();
  const opened = await transition(original, {type: "open-question", question_id: "q1", question: "What is customer?", owner_route: "owner"});
  assert.equal(original.revision, 1);
  assert.equal(opened.decision.status, "accepted");
  assert.equal(opened.state.lifecycle_state, "question-open");
  const wrong = await transition(opened.state, {type: "record-answer", question_id: "q2", answer: "Buyer"});
  assert.equal(wrong.decision.repair_focus, "question-match");
  assert.equal(wrong.state, opened.state);
  const answered = await transition(opened.state, {type: "record-answer", question_id: "q1", answer: "Buyer"});
  assert.equal(answered.state.lifecycle_state, "ready");
  assert.equal(answered.state.answers[0].answer, "Buyer");
  const openedAgain = await transition(answered.state, {type: "open-question", question_id: "q2", question: "What is the window?", owner_route: "owner"});
  const deferred = await transition(openedAgain.state, {type: "defer-question", question_id: "q2"});
  assert.equal(deferred.state.lifecycle_state, "ready-with-open-gaps");
  assert.deepEqual(deferred.state.gaps, [{question_id: "q2", status: "open"}]);
});

test("context and payload defects do not advance state", async () => {
  const awaiting = createSession({context_sufficient: false});
  const blocked = await transition(awaiting, {type: "open-question", question_id: "q1", question: "Why?", owner_route: "owner"});
  assert.equal(blocked.decision.repair_focus, "context");
  assert.equal(blocked.state, awaiting);
  const incomplete = await transition(createSession(), {type: "open-question", question_id: "q1", question: "", owner_route: "owner"});
  assert.equal(incomplete.decision.repair_focus, "payload");
});

test("bounded question-cycle states agree with the current Define runtime", async () => {
  const current = createDurableDefineRuntime();
  const created = current.execute(currentCommand("cmd:create", "create-session", 0, {
    goal: "Clarify customer", intent: "Avoid a collapsed term", context: "Synthetic refund flow", consumer: "test",
    context_sufficiency_evaluation: {
      evaluation_id: "evaluation:synthetic", status: "sufficient", derivation: "Synthetic test input",
      residue: [], evaluator_receipt_ref: "receipt:synthetic", authority_effect: "none",
    },
  }));
  assert.equal(created.outcome, "confirmed");
  let candidate = createSession();
  const sequence = [
    ["open-question", {question_id: "q1", question: "What is customer?", owner_route: "owner"}, "question-open"],
    ["record-answer", {question_id: "q1", answer: "Buyer"}, "ready"],
    ["open-question", {question_id: "q2", question: "When does a refund start?", owner_route: "owner"}, "question-open"],
    ["defer-question", {question_id: "q2"}, "ready-with-open-gaps"],
  ];
  for (const [type, payload, expectedState] of sequence) {
    const result = current.execute(currentCommand(`cmd:${candidate.revision}`, type, candidate.revision, payload));
    const successor = await transition(candidate, {type, ...payload});
    assert.equal(result.outcome, "confirmed");
    assert.equal(successor.decision.status, "accepted");
    candidate = successor.state;
    const snapshot = current.inspect("define-session:rewrite-parity");
    assert.equal(candidate.revision, snapshot.revision);
    assert.equal(candidate.lifecycle_state, expectedState);
    assert.equal(candidate.lifecycle_state, snapshot.lifecycle_state);
    assert.equal(candidate.current_question?.question_id ?? null, snapshot.current_question_id);
    assert.equal(candidate.gaps.length, snapshot.gaps.length);
  }
});
