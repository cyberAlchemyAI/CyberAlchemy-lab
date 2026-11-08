import assert from "node:assert/strict";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { qualifyBehavioralClaim } from "../src/behavioral-qualification.js";
import { CompilationRejected } from "../src/model.js";
import { testTsx } from "./toolchain.js";

const source = `domain question-cycle "Question cycle"
profile application-v1
owner test-owner
entity Session:
  id String
  identity id
event QuestionOpened:
  event-type question-opened
  version 1
  occurrence-id eventId String
  occurred-at generated
operation OpenQuestion:
  input Session
  output Session
  writes Session
  produces QuestionOpened
state-machine SessionLifecycle:
  subject Session
  initial ready
  transition Open:
    from ready
    to question-open
    on QuestionOpened
`;

function code(expected: string) {
  return (error: unknown) => error instanceof CompilationRejected
    && error.issues.some(issue => issue.code === expected);
}

test("closed state model requires canonical meta-types and a producer for each transition", () => {
  const result = qualifyBehavioralClaim(source, "closed-state-model");
  assert.deepEqual(result.operations, ["OpenQuestion"]);
  assert.deepEqual(result.state_machines, ["SessionLifecycle"]);
  assert.equal(result.transition_count, 1);
  assert.equal(result.runtime_guarantees_observed, false);
  assert.throws(() => qualifyBehavioralClaim(source.replace("profile application-v1", "profile declarative-function-v1"), "closed-state-model"), code("ALCH_BEHAVIOR_PROFILE"));
  assert.throws(() => qualifyBehavioralClaim(source.replace("  produces QuestionOpened\n", ""), "closed-state-model"), code("ALCH_STATE_MODEL_PRODUCER"));
  assert.throws(() => qualifyBehavioralClaim(source.replace("  writes Session\n", ""), "closed-state-model"), code("ALCH_STATE_MODEL_WRITE"));
  assert.throws(() => qualifyBehavioralClaim(source.replace("  subject Session\n", ""), "closed-state-model"), code("ALCH_STATE_MODEL_SUBJECT"));
  assert.throws(() => qualifyBehavioralClaim(source.replace("  transition Open:\n    from ready\n    to question-open\n    on QuestionOpened\n", ""), "closed-state-model"), code("APPLICATION_STATE_MACHINE"));
  assert.throws(() => qualifyBehavioralClaim(source.replace("  transition Open:\n    from ready\n    to question-open\n    on QuestionOpened", "  ready -> question-open"), "closed-state-model"), code("ALCH_STATE_MODEL_TRIGGER"));
});

test("source closure cannot be promoted into an executable runtime claim", () => {
  assert.throws(() => qualifyBehavioralClaim(source, "executable-runtime"), code("ALCH_RUNTIME_UNOBSERVED"));
  assert.throws(() => qualifyBehavioralClaim(source, "invented-type" as never), code("ALCH_BEHAVIOR_CLAIM"));
});

test("CLI qualification exposes the same fail-closed boundary", t => {
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const directory = mkdtempSync(path.join(tmpdir(), "alch-behavior-qualification-"));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const file = path.join(directory, "cycle.alch");
  writeFileSync(file, source);
  const invoke = (claim: string) => spawnSync(testTsx(), [path.join(root, "src/cli.ts"), "qualify", file, "--claim", claim], {
    cwd: root, encoding: "utf8", env: process.env,
  });
  const model = invoke("closed-state-model");
  assert.equal(model.status, 0, model.stderr);
  assert.equal(JSON.parse(model.stdout).status, "source-qualified");
  const runtime = invoke("executable-runtime");
  assert.notEqual(runtime.status, 0);
  assert.match(runtime.stderr, /ALCH_RUNTIME_UNOBSERVED/);
});
