import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { createInstantiationReceipt, validateInstantiationReceipt } from "../../src/conformance/receipt.ts";
import { planInstantiation } from "../../src/generation/plan-instantiation.ts";
import { loadProjectNode } from "../../src/input/project-model.ts";
import {
  SystemIntegrationError,
  compileSystemIntegrationManifest,
  loadSystemIntegrationSelection,
  renderSystemIntegrationContract,
  validateSystemIntegrationBindingSet,
  verifySystemIntegrationContract,
} from "../../src/system-integration/compiler.ts";
import { FROZEN_SYSTEM_INTEGRATION } from "../../src/system-integration/profile.ts";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const fixtureRoot = path.resolve(testDir, "../../fixtures/input-roots/canonical-project");
const bindingPath = path.join(fixtureRoot, "integrations/settle-runtime.json");
const bindingSet = JSON.parse(fs.readFileSync(bindingPath, "utf8"));

function clone(value: unknown): any {
  return JSON.parse(JSON.stringify(value));
}

test("frozen provider-neutral profile covers D45-D49 in exactly three languages", () => {
  assert.deepEqual(FROZEN_SYSTEM_INTEGRATION.profile.definition_ids, [
    "domainspec-v2-D45",
    "domainspec-v2-D46",
    "domainspec-v2-D47",
    "domainspec-v2-D48",
    "domainspec-v2-D49",
  ]);
  assert.deepEqual(Object.keys(FROZEN_SYSTEM_INTEGRATION.language_profiles).sort(), ["python", "rust", "typescript"]);
  assert.equal(FROZEN_SYSTEM_INTEGRATION.profile.claim_ceiling.provider_selected_by_domainspec, false);
  assert.equal(FROZEN_SYSTEM_INTEGRATION.profile.claim_ceiling.runtime_guarantees_observed, false);
});

test("binding compilation and generated contracts are deterministic in all language profiles", () => {
  for (const language of ["typescript", "python", "rust"] as const) {
    const left = compileSystemIntegrationManifest(bindingSet, language);
    const right = compileSystemIntegrationManifest(clone(bindingSet), language);
    assert.deepEqual(left, right);
    const source = renderSystemIntegrationContract(left);
    assert.equal(verifySystemIntegrationContract(source, left), true);
    assert.equal(/\bPort\b/.test(source), false);
    assert.equal(left.runtime_guarantees_observed, false);
  }
});

test("an explicit system-integration selection adds one digest-bound plan and receipt artifact", () => {
  const node = loadProjectNode(fixtureRoot, "alpha:settle");
  for (const language of ["typescript", "python", "rust"] as const) {
    const selection = loadSystemIntegrationSelection(fixtureRoot, "settle-runtime", "provider-neutral-v1", "alpha:settle", language);
    const plan = planInstantiation(node, language, selection);
    assert.equal(plan.artifacts.length, 2);
    assert.equal(plan.system_integration?.manifest.binding_digest, selection.manifest.binding_digest);
    assert.equal(plan.artifacts.some(({ relative_path }) => relative_path === selection.generated_relative_path), true);
    const receipt = createInstantiationReceipt(plan);
    assert.equal(validateInstantiationReceipt(receipt), receipt);
    assert.equal(receipt.system_integration?.generated_relative_path, selection.generated_relative_path);
    assert.equal("generated_content" in (receipt.system_integration ?? {}), false);
  }
});

test("profile, subject, continuation, universal abstraction, and reference drift fail closed", () => {
  assert.throws(
    () => loadSystemIntegrationSelection(fixtureRoot, "settle-runtime", "sqlite", "alpha:settle", "typescript"),
    (error) => error instanceof SystemIntegrationError && error.code === "SIC_PROFILE_UNRESOLVED",
  );
  assert.throws(
    () => loadSystemIntegrationSelection(fixtureRoot, "settle-runtime", "provider-neutral-v1", "alpha:customer", "typescript"),
    (error) => error instanceof SystemIntegrationError && error.code === "SIC_REFERENCE_KIND_MISMATCH",
  );
  const continuation = clone(bindingSet);
  continuation.failure_outcome_bindings[0].retry_selection = "retry";
  assert.throws(() => validateSystemIntegrationBindingSet(continuation), (error) => error instanceof SystemIntegrationError && error.code === "SIC_FAILURE_CONTINUATION_FORBIDDEN");
  const universal = clone(bindingSet);
  universal.dependency_contracts[0].concern = "Port";
  assert.throws(() => validateSystemIntegrationBindingSet(universal), (error) => error instanceof SystemIntegrationError && error.code === "SIC_UNIVERSAL_PORT_FORBIDDEN");
  const missing = clone(bindingSet);
  missing.persistence_bindings[0].dependency_contract_ref = "missing-repository";
  assert.throws(() => validateSystemIntegrationBindingSet(missing), (error) => error instanceof SystemIntegrationError && error.code === "SIC_REFERENCE_UNRESOLVED");
});
