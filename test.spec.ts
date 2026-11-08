import assert from "node:assert/strict";
import test from "node:test";
import { Progress, reduceProgress, stateFor } from "./progress";

test("repeated delivery of one step does not finish an export", () => {
  let p: Progress = {
    runId: "", attempts: { render: 0, upload: 0 }, done: new Set(),
  };
  p = reduceProgress(p, { type: "START_EXPORT", runId: "duplicate" });
  p = reduceProgress(p, { type: "STEP_DONE", runId: "duplicate", step: "render", attempt: 1 });
  p = reduceProgress(p, { type: "STEP_DONE", runId: "duplicate", step: "render", attempt: 1 });
  assert.equal(stateFor(p), "running");
});