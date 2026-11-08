import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { loadCompiledProjectGraph } from "../../src/input/project-model.ts";
import {
  APPLICATION_REFERENCE_KIND_MATRIX,
  ApplicationIntegrationBindingError,
  validateApplicationIntegrationBinding,
} from "../../src/system-integration/application-binding-v1.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const example = path.resolve(here, "../../examples/reconciled-commerce");
const readSource = (): any => JSON.parse(fs.readFileSync(path.join(example, "integrations/application.json"), "utf8"));

test("L0 binding closes every application reference against the compiled graph", () => {
  const graph = loadCompiledProjectGraph(path.join(example, "source"));
  const binding = validateApplicationIntegrationBinding(graph, readSource());
  const expected = JSON.parse(fs.readFileSync(path.join(example, "integrations/expected-binding.json"), "utf8"));
  assert.deepEqual(binding, expected);
  assert.equal(binding.references.length, 58);
  assert.equal(new Set(binding.references.map(item => item.pointer)).size, binding.references.length);
  assert.equal(new Set(graph.nodes.map(item => item.selector)).size, graph.nodes.length, "compiled graph makes ambiguous selectors inadmissible");
  assert.deepEqual(binding.reference_kind_matrix, APPLICATION_REFERENCE_KIND_MATRIX);
  assert.equal(binding.runtime_guarantees_observed, false);
  assert.equal(binding.authority_effect, "none");
});

test("L0 binding compiles one deterministic cross-authority application graph", () => {
  const graph = loadCompiledProjectGraph(path.join(example, "source"));
  const left = validateApplicationIntegrationBinding(graph, readSource()).application_graph;
  const right = validateApplicationIntegrationBinding(graph, readSource()).application_graph;
  assert.deepEqual(right, left);
  assert.notEqual(left.domain_relationship_authority_sha256, left.integration_relationship_authority_sha256);
  assert.deepEqual(
    [...new Set(left.edges.filter(edge => edge.relationship_authority === "integration").map(edge => edge.relationship))].sort(),
    ["accepts-request", "invokes", "produces-message-contract", "publishes-event", "reads-payload-from"],
  );
  assert.equal(left.edges.some(edge => edge.relationship_authority === "integration" && edge.relationship === "emits"), false);
  assert.equal(left.nodes.some(node => node.node_origin === "integration" && node.node_kind === "request-contract"), true);
  assert.equal(left.runtime_bindings.length, 6);
  assert.deepEqual(left.operation_requests, [{
    request_ref: "commerce:perform#request",
    operation_ref: "commerce:perform",
    mapping_binding_refs: ["api-mapping:payment-webhook-request", "message-mapping:order-submitted-in"],
    source_refs: ["message-type:order-submitted-v1", "provider-operation:payment-webhook#request"],
    bindings: [
      {
        mapping_binding_ref: "api-mapping:payment-webhook-request",
        source_ref: "provider-operation:payment-webhook#request",
        parameters: [
          { parameter: "amount", source: { kind: "mapping-result", path: [] } },
          { parameter: "notice_input", source: { kind: "source-body", path: ["notice_input"] } },
        ],
      },
      {
        mapping_binding_ref: "message-mapping:order-submitted-in",
        source_ref: "message-type:order-submitted-v1",
        parameters: [
          { parameter: "amount", source: { kind: "mapping-result", path: [] } },
          { parameter: "notice_input", source: { kind: "source-body", path: ["notice_input"] } },
        ],
      },
    ],
  }]);
  assert.deepEqual(left.runtime_bindings.find(binding => binding.binding_id === "message-mapping:order-submitted-out")?.inputs[0]?.source, { kind: "event-identity-reference", reference: "commerce:posted", path: ["order-id"] });
  assert.deepEqual(left.runtime_bindings.find(binding => binding.binding_id === "api-mapping:authorize-request")?.inputs[0], {parameter:"order",value_type:{kind:"reference",selector:"commerce:order",projection:["id"]},source:{kind:"entity-identity",reference:"commerce:order",path:["id"]}});
  assert.deepEqual(left.runtime_bindings.find(binding => binding.binding_id === "api-mapping:payment-webhook-response")?.inputs[0]?.source, { kind: "operation-result", reference: "commerce:perform#result", path: [] });
  assert.equal(left.runtime_bindings.find(binding => binding.binding_id === "message-mapping:order-submitted-in")?.target_ref, "commerce:perform#request");
  assert.deepEqual(left.runtime_bindings.find(binding => binding.binding_id === "message-mapping:order-submitted-in")?.inputs[0]?.source, { kind: "message-body", reference: "message-type:order-submitted-v1", path: ["amount"] });
  assert.equal(left.runtime_guarantees_observed, false);
  assert.equal(left.authority_effect, "none");
});

test("L0 binding rejects missing, case-drifted, wrong-kind, provider, field, and failure joins", () => {
  const graph = loadCompiledProjectGraph(path.join(example, "source"));
  const persistenceSubject = (value: string) => (source: any) => {
    source.persistence.persistence_bindings[0].logical_subject_refs[0] = value;
    source.persistence.persistence_mappings[0].logical_subject_refs[0] = value;
  };
  const cases: readonly [string, (source: any) => void, string][] = [
    ["missing", persistenceSubject("commerce:missing"), "DS_APPLICATION_BINDING_MISSING"],
    ["case", persistenceSubject("Commerce:customer"), "DS_APPLICATION_BINDING_CASE_DRIFT"],
    ["wrong kind", persistenceSubject("commerce:posted"), "DS_APPLICATION_BINDING_WRONG_KIND"],
    ["provider", persistenceSubject("provider-realization:orders-postgresql"), "DS_APPLICATION_BINDING_MISSING"],
    ["field", source => { source.persistence.persistence_mappings[0].field_mappings[1].logical_property_ref = "commerce:order#missing"; }, "DS_APPLICATION_BINDING_FIELD"],
    ["failure", source => { source.persistence.integration_kernel.failure_mappings[0].unknown_failure_outcome_ref = "commerce:order"; }, "DS_APPLICATION_BINDING_WRONG_KIND"],
    ["event is not message", source => { source.messaging.message_types[0].logical_payload_ref = "commerce:order"; source.messaging.message_mappings[0].source_ref = "commerce:order"; source.messaging.publication_bindings[0].logical_source_ref = "commerce:order"; }, "DS_APPLICATION_BINDING_WRONG_KIND"],
  ];
  for (const [name, mutate, code] of cases) {
    const source = readSource();
    mutate(source);
    assert.throws(() => validateApplicationIntegrationBinding(graph, source), (error: unknown) => error instanceof ApplicationIntegrationBindingError && error.code === code, name);
  }
});

test("L0 binding keeps the integration source envelope closed", () => {
  const graph = loadCompiledProjectGraph(path.join(example, "source"));
  assert.throws(() => validateApplicationIntegrationBinding(graph, { ...readSource(), accidental: true }), { code: "INTEGRATION_GENERATION_SCHEMA" });
});

test("L0 binding rejects incomplete or shape-collapsed persistence mappings", () => {
  const graph = loadCompiledProjectGraph(path.join(example, "source"));
  const missing = readSource();
  missing.persistence.persistence_mappings[0].field_mappings = missing.persistence.persistence_mappings[0].field_mappings.filter((item: { logical_property_ref: string }) => item.logical_property_ref !== "commerce:order#billing_customer_id");
  assert.throws(() => validateApplicationIntegrationBinding(graph, missing), (error: unknown) => error instanceof ApplicationIntegrationBindingError && error.code === "DS_APPLICATION_BINDING_PERSISTENCE_COVERAGE");

  const collapsed = readSource();
  collapsed.persistence.persistence_mappings[0].field_mappings.find((item: { logical_property_ref: string }) => item.logical_property_ref === "commerce:order#customer").logical_shape = "scalar";
  collapsed.persistence.persistence_mappings[0].field_mappings.find((item: { logical_property_ref: string }) => item.logical_property_ref === "commerce:order#customer").storage_shape = "scalar";
  assert.throws(() => validateApplicationIntegrationBinding(graph, collapsed), (error: unknown) => error instanceof ApplicationIntegrationBindingError && error.code === "DS_APPLICATION_BINDING_PERSISTENCE_SHAPE");
});

test("L0 binding rejects integration totality that disagrees with its authored Mapping", () => {
  const graph = loadCompiledProjectGraph(path.join(example, "source"));
  const source = readSource();
  source.external_api.api_mappings[0].total = false;
  assert.throws(() => validateApplicationIntegrationBinding(graph, source), (error: unknown) => error instanceof ApplicationIntegrationBindingError && error.code === "DS_APPLICATION_BINDING_MAPPING_TOTALITY");
});
