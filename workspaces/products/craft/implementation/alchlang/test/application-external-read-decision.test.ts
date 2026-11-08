import assert from "node:assert/strict";
import test from "node:test";
import { externalApiFixture } from "./fixtures/application-integration-fixtures.js";
import { wholeApplicationFixture } from "./fixtures/application-whole-fixture.js";
import { digest } from "../src/domainspec-profile.js";
import { parseDomainSource } from "../src/parser.js";
import { deriveApplicationIntegrationBindings } from "../src/application-integration-derivation.js";
import { lowerApplicationExternalApi } from "../src/application-external-api.js";

const decisionMapping = `mapping ProviderResponseToOrder:
  input provider OrderApi.Summary
  target Order
  total true
  field id <- provider.id
  field accepted <- provider.accepted
`;
const decisionSource = (source: string) => source.replace(
  /(outbound-call ProviderCall:[\s\S]*?    -> response OrderApi\.Summary\n)/,
  "$1    -> map ProviderResponseToOrder\n",
) + decisionMapping;

test("authored external response has an exact typed Mapping into the existing Operation decision input", async () => {
  const f = await externalApiFixture();
  const source = decisionSource(f.source);
  const outbound = (parseDomainSource(source).carrier as any).integrations.find((row: any) => row.kind === "outbound-call");
  assert.equal(outbound.decision_mapping.ref, "ProviderResponseToOrder");
  const binding = structuredClone(f.binding);
  binding.source_sha256 = digest(source);
  (binding.declarations.ProviderCall as any).decision_mapper_ref = "commerce:provider-response-to-order";
  const result = lowerApplicationExternalApi(source, binding, f.compiler);
  const artifact = JSON.parse(result.files["external-api-decision-joins.json"]!);
  assert.equal(artifact.source_sha256, digest(source));
  assert.equal(artifact.runtime_calls_observed, false);
  assert.deepEqual(artifact.joins, [{
    source_id: "ProviderCall", binding_ref: binding.composition.external_api_bindings[0].binding_id,
    contract_operation_ref: binding.composition.external_api_bindings[0].contract_operation_ref,
    operation_ref: "commerce:submit-order", response_mapper_ref: "commerce:provider-response",
    decision_mapper_ref: "commerce:provider-response-to-order",
    response_type: { kind: "public-contract", interface: "OrderApi", contract: "Summary" },
    decision_input_type: { kind: "declaration", ref: "Order" },
  }]);
  assert.equal(result.trace.decision_joins_sha256, digest(result.files["external-api-decision-joins.json"]!));

  const wrongMapper = structuredClone(binding);
  (wrongMapper.declarations.ProviderCall as any).decision_mapper_ref = "commerce:missing";
  assert.throws(() => lowerApplicationExternalApi(source, wrongMapper, f.compiler), /APPLICATION_API_DECISION_MAPPING/);
  const missingMapper = decisionSource(f.source).replace("-> map ProviderResponseToOrder", "-> map MissingMapping");
  const missingBinding = structuredClone(binding); missingBinding.source_sha256 = digest(missingMapper);
  assert.throws(() => lowerApplicationExternalApi(missingMapper, missingBinding, f.compiler), /APPLICATION_API_DECISION_MAPPING/);
  const wrongType = source.replace("target Order\n  total true\n  field id <- provider.id", "target OrderApi.SubmitRequest\n  total true\n  field id <- provider.id");
  const wrongTypeBinding = structuredClone(binding); wrongTypeBinding.source_sha256 = digest(wrongType);
  assert.throws(() => lowerApplicationExternalApi(wrongType, wrongTypeBinding, f.compiler), /APPLICATION_API_DECISION_MAPPING/);
  const wrongOperation = structuredClone(binding);
  wrongOperation.composition.external_api_bindings[0].contract_operation_ref = "contract:payment-gateway#missing";
  assert.throws(() => lowerApplicationExternalApi(source, wrongOperation, f.compiler), /APPLICATION_API_OPERATION/);
  const wrongContract = structuredClone(binding);
  wrongContract.composition.external_api_bindings[0].external_api_contract_ref = "contract:missing";
  assert.throws(() => lowerApplicationExternalApi(source, wrongContract, f.compiler), /APPLICATION_API_CONTRACT/);
  const wrongFailure = structuredClone(binding);
  wrongFailure.composition.external_api_bindings[0].failure_mapping_ref = "api-failure-mapping:missing";
  assert.throws(() => lowerApplicationExternalApi(source, wrongFailure, f.compiler), /APPLICATION_API_FAILURE/);
});

test("reference profile derives the decision Mapping choice from source rather than a handwritten binding", async () => {
  const f = await wholeApplicationFixture();
  const source = decisionSource(f.source);
  const derived = deriveApplicationIntegrationBindings(source, "CommerceRuntime", f.compiler);
  assert.equal(derived.externalApi.declarations.ProviderCall.decision_mapper_ref, "commerce:provider-response-to-order");
  const result = lowerApplicationExternalApi(source, derived.externalApi, f.compiler);
  assert.equal(result.decisionJoins?.[0]?.operation_ref, "commerce:submit-order");
  const wrongType = source.replace("target Order\n  total true\n  field id <- provider.id", "target OrderApi.SubmitRequest\n  total true\n  field id <- provider.id");
  assert.throws(() => deriveApplicationIntegrationBindings(wrongType, "CommerceRuntime", f.compiler), /APPLICATION_INTEGRATION_DERIVATION_DECISION_MAPPING/);
});
