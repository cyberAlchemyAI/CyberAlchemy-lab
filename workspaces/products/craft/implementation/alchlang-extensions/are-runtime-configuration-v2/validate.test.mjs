import assert from "node:assert/strict";
import test from "node:test";

import {validateRuntimeConfiguration} from "./validate.mjs";

test("candidate successor binds the injected runtime and all three entries", async () => {
  const result = await validateRuntimeConfiguration();
  assert.equal(result.status, "PASS");
  assert.equal(result.runtime_admitted, false);
  assert.equal(result.enforcement_active, false);
  assert.match(result.module_set_digest, /^[a-f0-9]{64}$/u);
  assert.deepEqual(result.checks.filter((row) => row.outcome === "BLOCK"), []);
  for (const id of ["RequestIntentContainsPhrase", "RequestIntentSemanticKey", "RouterContainsPhrase"]) {
    assert.equal(result.checks.find((row) => row.check_id === `entry-invocation:${id}`)?.outcome, "PASS");
  }
  for (const id of ["factory", "runtime", "compiled"]) {
    assert.equal(result.checks.find((row) => row.check_id === `${id}-source-binding`)?.outcome, "PASS");
  }
});
