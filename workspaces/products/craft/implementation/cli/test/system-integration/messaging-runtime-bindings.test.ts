import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { loadCompiledProjectGraph } from "../../src/input/project-model.ts";
import { compileApplicationGraphV1, compileMessagingRuntimeBindingsV1 } from "../../src/system-integration/application-graph-v1.ts";
import { validateOperationRequestContracts } from "../../src/generation/whole-application-v1.ts";
import { decodeReconciledCompilationSelection } from "../../src/generation/reconciled-project.ts";

const example = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../examples/reconciled-commerce");
const fixture = () => ({ graph: loadCompiledProjectGraph(path.join(example, "source")),
  integration: JSON.parse(fs.readFileSync(path.join(example, "integrations/application.json"), "utf8")),
  selection: decodeReconciledCompilationSelection(JSON.parse(fs.readFileSync(path.join(example, "selections/typescript.json"), "utf8"))) });

test("bounded messaging join agrees with whole-application runtime bindings without claiming a full graph", () => {
  const { graph, integration, selection } = fixture();
  const whole = compileApplicationGraphV1(graph, integration), result = compileMessagingRuntimeBindingsV1(graph, integration.messaging);
  const ids = new Set(integration.messaging.message_mappings.map((m: any) => m.mapping_id));
  assert.deepEqual(result.runtime_bindings, whole.runtime_bindings.filter(row => ids.has(row.binding_id)));
  assert.deepEqual(result.operation_requests, whole.operation_requests.map(row => ({ ...row,
    mapping_binding_refs: row.mapping_binding_refs.filter(id => ids.has(id)),
    source_refs: row.source_refs.filter(ref => ref.startsWith("message-type:")),
    bindings: row.bindings.filter(binding => ids.has(binding.mapping_binding_ref)),
  })).filter(row => row.bindings.length));
  validateOperationRequestContracts({ selection }, result.operation_requests, result.runtime_bindings);
  assert.deepEqual(result, compileMessagingRuntimeBindingsV1(graph, structuredClone(integration.messaging)));
  assert.equal(result.runtime_bindings.find(row => row.direction === "logical-to-message")!.inputs[0]!.source.kind, "event-identity-reference");
  assert.equal(result.runtime_delivery_observed, false); assert.equal(result.authority_effect, "none");
  assert.equal(Object.hasOwn(result, "edges"), false);
});

test("messaging join preserves snapshot and operation request failure boundaries", () => {
  const { graph, integration, selection } = fixture();
  assert.throws(() => compileMessagingRuntimeBindingsV1(structuredClone(graph), integration.messaging));
  const bad = structuredClone(integration.messaging);
  const inbound = bad.message_mappings.find((m: any) => m.direction === "message-to-application");
  inbound.input_paths[0].parameter = "unbound";
  assert.throws(() => compileMessagingRuntimeBindingsV1(graph, bad), /request Mapping input paths/);
  const result = compileMessagingRuntimeBindingsV1(graph, integration.messaging);
  const wrong: any = structuredClone(result.operation_requests);
  wrong[0]!.bindings[0]!.parameters[0] = { parameter: "unbound", source: { kind: "mapping-result", path: [] } };
  assert.throws(() => validateOperationRequestContracts({ selection }, wrong, result.runtime_bindings), /request parameters must exactly cover/);
});
