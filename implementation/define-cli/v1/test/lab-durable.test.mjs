// Six source durable-session regressions retained against the Lab successor.
import assert from 'node:assert/strict';
import test from 'node:test';
import {mkdtempSync,rmSync,writeFileSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createDurableDefineRuntime,createDefineSessionClient,JsonFileSessionRepository,InMemorySessionRepository,sessionStateDigest} from '../index.mjs';
const runtimeActor = {
  actor_ref: "actor:define-owner",
  allowed_effects: ["create-session", "set-context-evaluation", "open-question", "record-answer", "defer-question"],
};

function runtimeCommand(commandId, commandType, sessionId, expectedRevision, payload, actor = runtimeActor) {
  return {
    schema_version: "cav2.define-session-command/v1",
    command_id: commandId,
    command_type: commandType,
    session_id: sessionId,
    expected_revision: expectedRevision,
    actor_access_context: actor,
    payload_schema_version: "v1",
    payload,
  };
}

function createRuntimeSession(runtime, sessionId = "define-session:durable-test") {
  return runtime.execute(runtimeCommand("command:create", "create-session", sessionId, 0, {
    goal: "Define a release channel",
    intent: "Remove ambiguity",
    context: "One shared candidate context.",
    consumer: "runtime-test",
    context_sufficiency_evaluation: {
      evaluation_id: "evaluation:fixture",
      status: "sufficient",
      derivation: "Pinned test fixture",
      residue: [],
      evaluator_receipt_ref: "receipt:fixture",
      authority_effect: "none",
    },
  }));
}

test("durable runtime resumes one confirmed session across CLI and chat clients", () => {
  const directory = mkdtempSync(join(tmpdir(), "define-runtime-test-"));
  try {
    const runtime = createDurableDefineRuntime({repository: new JsonFileSessionRepository(directory)});
    const cli = createDefineSessionClient(runtime, "cli");
    const chat = createDefineSessionClient(runtime, "chat");
    assert.equal(createRuntimeSession(runtime).outcome, "confirmed");
    assert.equal(cli.execute(runtimeCommand("command:open", "open-question", "define-session:durable-test", 1, {
      question_id: "question:channel",
      term: "release channel",
      question: "What should release channel mean?",
      owner_route: "Definitions Governance owner",
    })).outcome, "confirmed");
    assert.equal(chat.execute(runtimeCommand("command:answer", "record-answer", "define-session:durable-test", 2, {
      question_id: "question:channel",
      answer: "A named candidate delivery path.",
    })).outcome, "confirmed");
    const restarted = createDurableDefineRuntime({repository: new JsonFileSessionRepository(directory)});
    const resumed = createDefineSessionClient(restarted, "chat").resume("define-session:durable-test");
    assert.equal(resumed.revision, 3);
    assert.equal(resumed.current_question_id, null);
    assert.equal(resumed.answers[0].answer, "A named candidate delivery path.");
    assert.equal(sessionStateDigest(resumed), resumed.state_digest);
  } finally {
    rmSync(directory, {recursive: true, force: true});
  }
});

test("optimistic revision prevents a silent lost update", () => {
  const runtime = createDurableDefineRuntime();
  createRuntimeSession(runtime, "define-session:conflict");
  const first = runtime.execute(runtimeCommand("command:first", "open-question", "define-session:conflict", 1, {
    question_id: "question:first", question: "First?", owner_route: "owner:first",
  }));
  const second = runtime.execute(runtimeCommand("command:second", "open-question", "define-session:conflict", 1, {
    question_id: "question:second", question: "Second?", owner_route: "owner:second",
  }));
  assert.equal(first.outcome, "confirmed");
  assert.equal(second.outcome, "conflict");
  assert.equal(second.failure_class, "revision-conflict");
  assert.equal(runtime.inspect("define-session:conflict").current_question_id, "question:first");
});

test("exact command retry returns the prior result without a second transition", () => {
  const repository = new InMemorySessionRepository();
  const runtime = createDurableDefineRuntime({repository});
  const command = runtimeCommand("command:create-idempotent", "create-session", "define-session:idempotent", 0, {
    goal: "Define X", intent: "Bound X", context: "X is unclear", consumer: "test",
  });
  const first = runtime.execute(command);
  const second = runtime.execute(command);
  assert.deepEqual(second, first);
  const record = repository.load("define-session:idempotent");
  assert.equal(record.snapshot.revision, 1);
  assert.equal(record.events.length, 1);
});

test("failed persistence never advances the last confirmed snapshot", () => {
  const repository = new InMemorySessionRepository();
  const runtime = createDurableDefineRuntime({repository});
  createRuntimeSession(runtime, "define-session:storage-failure");
  const before = runtime.inspect("define-session:storage-failure");
  repository.injectStorageFailure();
  const result = runtime.execute(runtimeCommand("command:failed-open", "open-question", "define-session:storage-failure", 1, {
    question_id: "question:unsaved", question: "Unsaved?", owner_route: "owner:test",
  }));
  assert.equal(result.outcome, "storage-failure");
  assert.deepEqual(runtime.inspect("define-session:storage-failure"), before);
});

test("visibility does not grant answer authority", () => {
  const runtime = createDurableDefineRuntime();
  createRuntimeSession(runtime, "define-session:authority");
  runtime.execute(runtimeCommand("command:open-authority", "open-question", "define-session:authority", 1, {
    question_id: "question:authority", question: "Who decides?", owner_route: "owner:meaning",
  }));
  const visible = runtime.inspect("define-session:authority");
  assert.equal(visible.current_question_id, "question:authority");
  const denied = runtime.execute(runtimeCommand("command:denied-answer", "record-answer", "define-session:authority", 2, {
    question_id: "question:authority", answer: "The observer decides.",
  }, {actor_ref: "actor:observer", allowed_effects: []}));
  assert.equal(denied.outcome, "denied");
  assert.equal(runtime.inspect("define-session:authority").answers.length, 0);
});

test("only sufficient frozen context permits a meaning question", () => {
  const runtime = createDurableDefineRuntime();
  const sessionId = "define-session:context-gate";
  const created = runtime.execute(runtimeCommand("command:create-context-gate", "create-session", sessionId, 0, {
    goal: "Define X", intent: "Bound X", context: "Candidate context", consumer: "test",
  }));
  assert.equal(created.outcome, "confirmed");
  const blocked = runtime.execute(runtimeCommand("command:blocked-question", "open-question", sessionId, 1, {
    question_id: "question:blocked", question: "What is X?", owner_route: "owner:x",
  }));
  assert.equal(blocked.outcome, "invalid");
  assert.equal(blocked.failure_class, "domain.context-not-sufficient");
  const evaluated = runtime.execute(runtimeCommand("command:context-sufficient", "set-context-evaluation", sessionId, 1, {
    evaluation_id: "evaluation:context-gate",
    status: "sufficient",
    derivation: "Frozen fixture requirements are met.",
    residue: [],
    evaluator_receipt_ref: "receipt:context-gate",
  }));
  assert.equal(evaluated.outcome, "confirmed");
  const opened = runtime.execute(runtimeCommand("command:allowed-question", "open-question", sessionId, 2, {
    question_id: "question:allowed", question: "What is X?", owner_route: "owner:x",
  }));
  assert.equal(opened.outcome, "confirmed");
});

