import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { compileIntegrationKernelV2, IntegrationKernelError, validateIntegrationKernelV2 } from "../../src/system-integration/kernel-v2.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixturePath = path.resolve(here, "../../../system-integration/fixtures/integration-kernel-v2/base-kernel.json");
const schemaPath = path.resolve(here, "../../../system-integration/contracts/integration-kernel-v2.schema.json");
const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

test("R2 integration kernel is deterministic, reference-closed, and non-authoritative", () => {
  const left = compileIntegrationKernelV2(fixture);
  const right = compileIntegrationKernelV2(clone(fixture));
  assert.deepEqual(left, right);
  assert.match(left.kernel_digest, /^[a-f0-9]{64}$/);
  assert.equal(left.runtime_guarantees_observed, false);
  assert.equal(left.authority_effect, "none");
  assert.equal(Object.isFrozen(left.integration_bindings), true);
});

test("R2 schema and all shared record definitions are closed", () => {
  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
  assert.equal(schema.additionalProperties, false);
  for (const name of ["integrationBinding", "providerProfile", "providerRealization", "serializationProfile", "failureCase", "failureMapping", "runtimeReceipt"]) {
    assert.equal(schema.$defs[name].additionalProperties, false, name);
  }
});

test("provider realization and concern references fail closed", () => {
  const missing = clone(fixture);
  missing.integration_bindings[0].provider_realization_ref = "provider-realization:missing";
  assert.throws(() => validateIntegrationKernelV2(missing), (error) => error instanceof IntegrationKernelError && error.code === "IK_REFERENCE_UNRESOLVED");
  const mismatch = clone(fixture);
  mismatch.integration_bindings[0].concern = "messaging";
  assert.throws(() => validateIntegrationKernelV2(mismatch), (error) => error instanceof IntegrationKernelError && error.code === "IK_CONCERN_MISMATCH");
});

test("D48 classification cannot absorb retry or continuation selection", () => {
  const inflated = clone(fixture);
  inflated.failure_mappings[0].retry_selection = "retry";
  assert.throws(() => validateIntegrationKernelV2(inflated), (error) => error instanceof IntegrationKernelError && error.code === "IK_SCHEMA");
});

test("runtime receipts cannot claim beyond their observed stage", () => {
  const inflated = clone(fixture);
  inflated.runtime_receipts = [{
    receipt_id: "receipt:publish-1", binding_ref: "binding:order-persistence", operation_ref: "commerce:submit-order",
    observed_at: "2026-09-15T12:00:00.000Z", observed_stage: "provider-accepted", outcome: "accepted",
    provider_evidence_ref: "evidence:provider-ack-1", correlation_ref: "correlation:order-1",
    claim_ceiling: "business-completed", authority_effect: "none",
  }];
  assert.throws(() => validateIntegrationKernelV2(inflated), (error) => error instanceof IntegrationKernelError && error.code === "IK_RECEIPT_CLAIM");
});

test("universal Port and definition-pack drift are rejected", () => {
  const universal = clone(fixture);
  universal.provider_profiles[0].provider_kind = "Port";
  assert.throws(() => validateIntegrationKernelV2(universal), (error) => error instanceof IntegrationKernelError && error.code === "IK_REFERENCE");
  const drifted = clone(fixture);
  drifted.definition_pack_sha256 = "0".repeat(64);
  assert.throws(() => validateIntegrationKernelV2(drifted), (error) => error instanceof IntegrationKernelError && error.code === "IK_DEFINITION_DRIFT");
});
