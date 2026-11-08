import assert from "node:assert/strict";
import test from "node:test";
import { runTrial } from "../../extensions/domainspec-application-trial-v1/trial.js";

test("unchanged commerce application preserves local behavior and exposes exact target migration blockers", async () => {
  const result=await runTrial();
  assert.equal(result.local_generated_application,"pass");
  assert.equal(result.target_migration,"blocked");
  assert.equal(result.numeric_probe.status,"incompatible");
  assert.equal(result.authority_effect,"none");
});
