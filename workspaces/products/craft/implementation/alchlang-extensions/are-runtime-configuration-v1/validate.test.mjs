import assert from "node:assert/strict";
import test from "node:test";

import {validateRuntimeConfiguration} from "./validate.mjs";

test("historical exact configuration blocks after adapter drift", () => {
  const result = validateRuntimeConfiguration();
  assert.equal(result.status, "BLOCK");
  assert.equal(result.runtime_admitted, false);
  assert.equal(result.enforcement_active, false);
  assert.equal(result.checks.find((row) => row.check_id === "static-composition-available")?.outcome, "BLOCK");
});

test("historical entry projections remain explicit but cannot currently invoke", () => {
  const result = validateRuntimeConfiguration();
  for (const id of ["RequestIntentContainsPhrase", "RequestIntentSemanticKey", "RouterContainsPhrase"]) {
    assert.equal(result.checks.find((row) => row.check_id === `entry-invocation:${id}`)?.outcome, "BLOCK");
  }
  assert.equal(result.checks.find((row) => row.check_id === "entry-semantic-orthogonality")?.outcome, "PASS");
});
