import assert from "node:assert/strict";
import test from "node:test";
import { loadCompiledProjectGraph } from "../../src/input/project-model.ts";
import { compileApplicationGraphV1, compileExternalApiRuntimeBindingsV1 } from "../../src/system-integration/application-graph-v1.ts";
import { validateApplicationIntegrationBinding } from "../../src/system-integration/application-binding-v1.ts";
import { publicApiApplication } from "../fixtures/public-api-application.ts";

test("API runtime join retains public identity and agrees with the complete application binding", t => {
  const f = publicApiApplication(t), graph = loadCompiledProjectGraph(f.root);
  const result = compileExternalApiRuntimeBindingsV1(graph, f.source.external_api);
  const whole = compileApplicationGraphV1(graph, f.source), binding = validateApplicationIntegrationBinding(graph, f.source);
  assert.deepEqual(binding.application_graph, whole);
  const ids = new Set(f.source.external_api.api_mappings.map((m: any) => m.mapping_id));
  assert.deepEqual(result.runtime_bindings, whole.runtime_bindings.filter(row => ids.has(row.binding_id)));
  const request = result.runtime_bindings.find(row => row.mapping_ref === "commerce:public-api-request")!;
  assert.deepEqual(request.inputs[0]!.value_type, f.type); assert.deepEqual(request.result_type, f.type);
  assert.equal(request.inputs[0]!.source.reference, "commerce:api#response");
  assert.equal(request.inputs[0]!.source.kind, "direct-value");
  const references = binding.references.filter(row => row.reference_kind === "public-contract");
  assert.equal(references.length, 2);
  for (const reference of references) {
    assert.equal(reference.selector, "commerce:api"); assert.equal(reference.fragment, "response");
    assert.equal(reference.actual_node_kind, "Interface"); assert.deepEqual(reference.expected_node_kinds, ["Interface"]);
  }
  assert.equal(result.runtime_calls_observed, false); assert.equal(result.authority_effect, "none");
  assert.deepEqual(result, compileExternalApiRuntimeBindingsV1(graph, structuredClone(f.source.external_api)));
  assert.throws(() => compileExternalApiRuntimeBindingsV1(structuredClone(graph), f.source.external_api));
  const totality = structuredClone(f.source.external_api); totality.api_mappings[0].total = false;
  assert.throws(() => compileExternalApiRuntimeBindingsV1(graph, totality), /DS_APPLICATION_GRAPH_MAPPING_TOTALITY/);
});

test("public API references reject missing contracts, wrong owners and mapping identity substitution", t => {
  const f = publicApiApplication(t), graph = loadCompiledProjectGraph(f.root);
  for (const reference of ["commerce:api#missing", "commerce:order#response", "commerce:api"]) {
    const source = structuredClone(f.source);
    source.external_api.external_api_contracts[0].operations[0].request_type_ref = reference;
    source.external_api.api_mappings[0].source_ref = reference;
    assert.throws(() => validateApplicationIntegrationBinding(graph, source), /DS_APPLICATION_BINDING_(PUBLIC_CONTRACT|WRONG_KIND)/);
  }
  const source = structuredClone(f.source);
  source.external_api.api_mappings[0].mapper_ref = "commerce:integration-outbound";
  source.external_api.external_api_bindings[0].request_mapper_ref = "commerce:integration-outbound";
  assert.throws(() => validateApplicationIntegrationBinding(graph, source), /DS_APPLICATION_BINDING_MAPPING_INPUT/);
});
