import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { compileExternalApiCompositionV2, ExternalApiCompositionError, validateExternalApiCompositionV2 } from "../../src/system-integration/external-api-v2.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixturePath = path.resolve(here, "../../../system-integration/fixtures/external-api-composition-v2/payments-http.json");
const schemaPath = path.resolve(here, "../../../system-integration/contracts/external-api-composition-v2.schema.json");
const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

test("R5 compiles inbound, outbound, and webhook bindings deterministically", () => {
  const left = compileExternalApiCompositionV2(fixture);
  const right = compileExternalApiCompositionV2(clone(fixture));
  assert.deepEqual(left, right);
  assert.match(left.composition_digest, /^[a-f0-9]{64}$/);
  assert.equal(left.inbound_endpoint_bindings.length, 1);
  assert.equal(left.external_api_bindings.length, 1);
  assert.equal(left.webhook_bindings.length, 1);
  assert.equal(left.runtime_calls_observed, false);
});

test("R5 schema closes every API contract, policy, mapping, and binding", () => {
  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
  assert.equal(schema.additionalProperties, false);
  for (const name of ["externalApiOperation", "externalApiContract", "apiMapping", "authenticationBinding", "resiliencePolicy", "apiFailureCase", "apiFailureMapping", "inboundEndpoint", "externalApiBinding", "webhookBinding"]) {
    assert.equal(schema.$defs[name].additionalProperties, false, name);
  }
});

test("application operations remain protocol-independent through explicit mappings", () => {
  const collapsed = clone(fixture);
  const mapping = collapsed.api_mappings.find((item: { mapper_ref: string }) => item.mapper_ref === "payments:webhook-to-notification");
  mapping.target_ref = "protocol-operation:payments-webhook#handler";
  delete mapping.input_paths;
  delete mapping.request_parameters;
  assert.throws(() => validateExternalApiCompositionV2(collapsed), (error) => error instanceof ExternalApiCompositionError && error.code === "API_MAPPING_COLLAPSE");
});

test("authentication contains credential references and never secret values", () => {
  const secret = clone(fixture);
  secret.authentication_bindings[0].contains_secret_values = true;
  assert.throws(() => validateExternalApiCompositionV2(secret), (error) => error instanceof ExternalApiCompositionError && error.code === "API_SECRET_VALUE");
  const wrongBoundary = clone(fixture);
  wrongBoundary.authentication_bindings[0].integration_boundary_ref = "external-api-binding:other";
  assert.throws(() => validateExternalApiCompositionV2(wrongBoundary), (error) => error instanceof ExternalApiCompositionError && error.code === "API_AUTH_BINDING");
});

test("unsafe retries require an explicit idempotency key", () => {
  const unsafe = clone(fixture);
  unsafe.resilience_policies[0].retry_safety = "safe-operation";
  unsafe.resilience_policies[0].idempotency_key_expression = null;
  assert.throws(() => validateExternalApiCompositionV2(unsafe), (error) => error instanceof ExternalApiCompositionError && error.code === "API_RETRY_SAFETY");
  const noKey = clone(fixture);
  noKey.resilience_policies[0].idempotency_key_expression = null;
  assert.throws(() => validateExternalApiCompositionV2(noKey), (error) => error instanceof ExternalApiCompositionError && error.code === "API_RETRY_SAFETY");
});

test("API failure mappings cannot escape the contract failure surface", () => {
  const escaped = clone(fixture);
  escaped.api_failure_mappings[0].cases[0].failure_outcome_ref = "payments:undeclared-failure";
  assert.throws(() => validateExternalApiCompositionV2(escaped), (error) => error instanceof ExternalApiCompositionError && error.code === "API_FAILURE_SURFACE");
});

test("webhooks require sender authentication and never infer application completion", () => {
  const noAuth = clone(fixture);
  noAuth.inbound_endpoint_bindings[0].authentication_binding_ref = null;
  assert.throws(() => validateExternalApiCompositionV2(noAuth), (error) => error instanceof ExternalApiCompositionError && error.code === "API_WEBHOOK_AUTH");
  const inflated = clone(fixture);
  inflated.webhook_bindings[0].application_completion_inferred = true;
  assert.throws(() => validateExternalApiCompositionV2(inflated), (error) => error instanceof ExternalApiCompositionError && error.code === "API_WEBHOOK_CLAIM");
});

test("inbound-only APIs need no fabricated outbound contract or failure translation", () => {
  const inbound = clone(fixture);
  inbound.external_api_contracts = []; inbound.external_api_bindings = [];
  inbound.api_failure_mappings = []; inbound.resilience_policies = [];
  inbound.api_mappings = inbound.api_mappings.filter((m: any) => m.mapping_id.includes("webhook"));
  inbound.authentication_bindings = inbound.authentication_bindings.filter((a: any) => a.binding_id.includes("webhook"));
  inbound.integration_kernel.integration_bindings = inbound.integration_kernel.integration_bindings.filter((b: any) => b.direction === "inbound");
  const result = compileExternalApiCompositionV2(inbound);
  assert.equal(result.inbound_endpoint_bindings.length, 1);
  assert.deepEqual(result.external_api_contracts, []);
  assert.deepEqual(result.external_api_bindings, []);
  assert.deepEqual(result.api_failure_mappings, []);
  assert.equal(result.runtime_calls_observed, false);
  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
  assert.equal(schema.properties.external_api_contracts.minItems ?? 0, 0);
  assert.equal(schema.properties.api_failure_mappings.minItems ?? 0, 0);
  const missing = clone(fixture); missing.external_api_contracts = []; missing.api_failure_mappings = [];
  assert.throws(() => validateExternalApiCompositionV2(missing), (error) => error instanceof ExternalApiCompositionError && error.code === "API_REFERENCE_UNRESOLVED");
});

test("non-null authentication references resolve for both API directions and webhooks", () => {
  for (const side of ["inbound_endpoint_bindings", "external_api_bindings"]) {
    const missing = clone(fixture); missing[side][0].authentication_binding_ref = "authentication:missing";
    assert.throws(() => validateExternalApiCompositionV2(missing), (error) => error instanceof ExternalApiCompositionError && error.code === "API_AUTH_BINDING");
  }
});

test("outbound operation references match the complete declared contract and separator", () => {
  const binding = fixture.external_api_bindings[0];
  const contract = binding.external_api_contract_ref;
  const operation = fixture.external_api_contracts[0].operations[0].operation_id;
  for (const reference of [
    `${contract.slice(0, -1)}X#${operation}`,
    `${contract}/${operation}`,
    `${contract}#missing`,
    `contract:foreign#${operation}`,
  ]) {
    const input = clone(fixture);
    input.external_api_bindings[0].contract_operation_ref = reference;
    assert.throws(() => validateExternalApiCompositionV2(input),
      (error) => error instanceof ExternalApiCompositionError && error.code === "API_REFERENCE_UNRESOLVED", reference);
  }
});

test("outbound failure mapping must belong to the selected contract even with identical outcomes", () => {
  const input = clone(fixture);
  const foreign = clone(input.external_api_contracts[0]);
  foreign.contract_id = "contract:other-gateway";
  foreign.operations[0].operation_id = "other-operation";
  input.external_api_contracts.push(foreign);
  const failure = clone(input.api_failure_mappings[0]);
  failure.mapping_id = "api-failure-mapping:other-provider";
  failure.external_api_contract_ref = foreign.contract_id;
  input.api_failure_mappings.push(failure);
  // Merely declaring a second valid contract and failure mapping is valid.
  assert.equal(compileExternalApiCompositionV2(input).runtime_calls_observed, false);
  input.external_api_bindings[0].failure_mapping_ref = failure.mapping_id;
  assert.throws(() => validateExternalApiCompositionV2(input),
    (error) => error instanceof ExternalApiCompositionError && error.code === "API_REFERENCE_UNRESOLVED");
  input.external_api_bindings[0].failure_mapping_ref = fixture.external_api_bindings[0].failure_mapping_ref;
  input.external_api_bindings[0].contract_operation_ref = `${foreign.contract_id}#other-operation`;
  assert.throws(() => validateExternalApiCompositionV2(input),
    (error) => error instanceof ExternalApiCompositionError && error.code === "API_REFERENCE_UNRESOLVED");
});

test("exact references accept a renamed selected contract and operation without an identity allowlist", () => {
  const originalContract = fixture.external_api_contracts[0].contract_id;
  const renamed = JSON.parse(JSON.stringify(fixture).replaceAll(originalContract, "contract:sample-directory"));
  renamed.external_api_contracts[0].operations[0].operation_id = "publish-sample";
  renamed.external_api_bindings[0].contract_operation_ref = "contract:sample-directory#publish-sample";
  assert.equal(compileExternalApiCompositionV2(renamed).external_api_bindings[0].contract_operation_ref,
    "contract:sample-directory#publish-sample");
  for (const ref of ["contract:sample-directory#publish-sample#suffix", "contract:sample-directory/publish-sample", "contract:sample-directorX#publish-sample"]) {
    const invalid = clone(renamed);invalid.external_api_bindings[0].contract_operation_ref = ref;
    assert.throws(() => compileExternalApiCompositionV2(invalid), {code: "API_REFERENCE_UNRESOLVED"});
  }
});
