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

function withMessaging(): any {
  const value = clone(bindingSet);
  value.message_channels = [
    { channel_id: "settlement-events", purpose: "delivery", allowed_event_refs: ["alpha:settlement-requested"], publisher_operation_refs: ["alpha:settle"], consumer_operation_refs: ["beta:record-settlement-request"], evidence_boundary: "formation-only-no-delivery-claim" },
    { channel_id: "settlement-events-dead-letter", purpose: "dead-letter", allowed_event_refs: ["alpha:settlement-requested"], publisher_operation_refs: [], consumer_operation_refs: [], evidence_boundary: "terminal-route-configuration-only" },
  ];
  value.delivery_policies = [{ policy_id: "settlement-delivery", semantics: "at-least-once", acknowledgement_boundary: "provider-accepted", ordering_scope: "none", visibility_timeout_seconds: 60, retention_seconds: 345600, max_receive_count: 5, dead_letter_channel_ref: "settlement-events-dead-letter", deduplication_owner_ref: "consumer:inbox-message-id", evidence_boundary: "provider-acceptance-is-not-application-commit" }];
  value.transport_failure_policies = [{ policy_id: "settlement-transport-failure", retry_eligibility: "idempotent-message-id-only", max_attempts: 5, backoff: "exponential-bounded", unknown_outcome: "reconcile-by-message-id", terminal_action: "dead-letter", evidence_boundary: "bounded-attempt-observation-only" }];
  value.transport_bindings = [{ binding_id: "settlement-message-transport", mode: "message", direction: "publish-subscribe", operation_ref: "alpha:settle", event_ref: "alpha:settlement-requested", channel_ref: "settlement-events", delivery_policy_ref: "settlement-delivery", failure_policy_ref: "settlement-transport-failure", envelope_profile_ref: "envelope:domainspec-event-json-v1", evidence_boundary: "intent-send-acceptance-delivery-and-commit-remain-distinct" }];
  return value;
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
    for (const key of ["message_channels", "transport_bindings", "delivery_policies", "transport_failure_policies"] as const) {
      assert.deepEqual(left.canonical_bindings[key], []);
    }
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

test("message contract extension compiles deterministically and rejects collapsed guarantees", () => {
  const candidate = withMessaging();
  assert.deepEqual(compileSystemIntegrationManifest(candidate, "typescript"), compileSystemIntegrationManifest(clone(candidate), "typescript"));
  assert.equal(validateSystemIntegrationBindingSet(candidate).transport_bindings.length, 1);
  candidate.delivery_policies[0].acknowledgement_boundary = "application-committed";
  assert.throws(() => validateSystemIntegrationBindingSet(candidate), (error) => error instanceof SystemIntegrationError && error.code === "SIC_DELIVERY_CLAIM");
  const invalidReference = withMessaging();
  invalidReference.transport_bindings[0].operation_ref = "alpha/op";
  assert.throws(() => validateSystemIntegrationBindingSet(invalidReference), (error) => error instanceof SystemIntegrationError && error.code === "SIC_SCHEMA");
  const mismatchedDeadLetter = withMessaging();
  mismatchedDeadLetter.message_channels[1].allowed_event_refs = ["beta:other-event"];
  assert.throws(() => validateSystemIntegrationBindingSet(mismatchedDeadLetter), (error) => error instanceof SystemIntegrationError && error.code === "SIC_MESSAGE_BINDING_INCOMPLETE");
});
