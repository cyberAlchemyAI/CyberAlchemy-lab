import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { IntegrationObservationError, projectIntegrationObservation, validateOrodiObservationBindingV1 } from "../../src/system-integration/observation-v2.ts";

const receipt: any = { receipt_id: "receipt:payment-1", binding_ref: "binding:authorize-payment-api", operation_ref: "payments:authorize", observed_at: "2026-09-15T12:00:00.000Z", observed_stage: "provider-accepted", outcome: "accepted", provider_evidence_ref: "evidence:http-202", correlation_ref: "correlation:payment-1", claim_ceiling: "provider-accepted", authority_effect: "none" };
const policy: any = { policy_id: "disclosure:integration-default", allowed_attribute_keys: ["provider", "statusCode"], max_attribute_count: 2, max_string_length: 64, forbidden_key_fragments: ["secret", "token", "credential", "authorization"], authority_effect: "none" };
const binding: any = { binding_id: "orodi-binding:integration", observation_selector: "domainspec:integration-observation", projection_mapper_ref: "mapping:integration-to-orodi", orodi_adapter_ref: "adapter:orodi-observation", evaluator_ref: "orodi:evaluator", disclosure_policy_ref: "disclosure:integration-default", edge_sequence: ["runtime", "observer", "orodi-adapter", "orodi-evaluator"], return_edge: "prohibited", runtime_control_capabilities: { select_retries: false, write_provider_state: false, call_apis: false, deploy: false, enact_business_effects: false }, evidence_boundary: "observation-input-only-no-admission", authority_effect: "none" };

test("R6 projects a deterministic immutable observation at the receipt claim ceiling", () => {
  const input = { observation_id: "observation:payment-1", receipt, duration_ms: 42, attributes: { provider: "payments", statusCode: 202 }, evidence_refs: ["evidence:http-202"], disclosure_policy: policy, orodi_binding: binding };
  const left = projectIntegrationObservation(input); const right = projectIntegrationObservation(structuredClone(input));
  assert.deepEqual(left, right); assert.equal(left.stage, "provider-accepted"); assert.equal(left.claim_ceiling, "provider-accepted"); assert.equal(left.immutable, true); assert.equal(Object.isFrozen(left), true); assert.match(left.source_receipt_digest, /^[a-f0-9]{64}$/);
});

test("R6 observation schema and nested records are closed", () => {
  const here = path.dirname(fileURLToPath(import.meta.url)); const schema = JSON.parse(fs.readFileSync(path.resolve(here, "../../../system-integration/contracts/integration-observation-v1.schema.json"), "utf8"));
  assert.equal(schema.additionalProperties, false); assert.equal(schema.$defs.disclosurePolicy.additionalProperties, false); assert.equal(schema.$defs.orodiBinding.additionalProperties, false); assert.equal(schema.$defs.runtimeCapabilities.additionalProperties, false);
});

test("ORODI has exactly one forward edge sequence and no control capability", () => {
  const reverse = structuredClone(binding); reverse.edge_sequence = ["orodi-evaluator", "orodi-adapter", "observer", "runtime"];
  assert.throws(() => validateOrodiObservationBindingV1(reverse), (error) => error instanceof IntegrationObservationError && error.code === "OBS_RETURN_EDGE");
  const actuator = structuredClone(binding); actuator.runtime_control_capabilities.select_retries = true;
  assert.throws(() => validateOrodiObservationBindingV1(actuator), (error) => error instanceof IntegrationObservationError && error.code === "OBS_ACTUATION");
});

test("disclosure policy rejects secrets, unlisted keys, and oversized values", () => {
  const base = { observation_id: "observation:payment-1", receipt, duration_ms: null, attributes: {}, evidence_refs: [], disclosure_policy: policy, orodi_binding: binding };
  assert.throws(() => projectIntegrationObservation({ ...base, attributes: { token: "secret" } }), (error) => error instanceof IntegrationObservationError && error.code === "OBS_DISCLOSURE");
  assert.throws(() => projectIntegrationObservation({ ...base, attributes: { unknown: "value" } }), (error) => error instanceof IntegrationObservationError && error.code === "OBS_DISCLOSURE");
  assert.throws(() => projectIntegrationObservation({ ...base, attributes: { provider: "x".repeat(65) } }), (error) => error instanceof IntegrationObservationError && error.code === "OBS_DISCLOSURE");
});

test("observation cannot inflate a receipt beyond its observed stage", () => {
  const inflated = structuredClone(receipt); inflated.claim_ceiling = "business-completed";
  assert.throws(() => projectIntegrationObservation({ observation_id: "observation:inflated", receipt: inflated, duration_ms: null, attributes: {}, evidence_refs: [], disclosure_policy: policy, orodi_binding: binding }), (error) => error instanceof IntegrationObservationError && error.code === "OBS_CLAIM");
});
