import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { compileCarrier, parseDomainSource } from "../src/index.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

test("an Entity-only source emits only structural and semantic graph artifacts", () => {
  const source = `domain entity-only "Entity only"\nowner test-owner\nlogic sfol-v1\n\nentity Customer:\n  customerId: identifier required\n  name: string optional\n`;
  const result = compileCarrier(parseDomainSource(source).carrier);
  assert.deepEqual(Object.keys(result.files).sort(), ["domain.graph.json", "domain.schema.ts", "domain.types.ts"]);
  assert.match(result.files["domain.types.ts"], /interface Customer/);
  assert.deepEqual(JSON.parse(result.files["domain.graph.json"]).nodes.map((node: { id: string; kind: string }) => node.kind), ["entity", "fact", "fact"]);
});

test("the thirteen backend meta-types select their populated artifact families", () => {
  const source = readFileSync(path.join(root, "examples/backend-types.alch"), "utf8");
  const result = compileCarrier(parseDomainSource(source).carrier);
  const files = new Set(Object.keys(result.files));
  for (const expected of ["domain.types.ts", "domain.schema.ts", "domain.machine.ts", "domain.events.ts", "domain.tools.ts", "domain.operations.ts", "domain.workflows.ts", "domain.interfaces.ts", "domain.test-obligations.json", "domain.graph.json", "traceability.json", "domain.typed-backend.ts", "domain.effects.ts"]) assert.ok(files.has(expected), expected);
  assert.equal(files.has("unsupported-residue.json"), false);
  const nodes = JSON.parse(result.files["domain.graph.json"]).nodes as Array<{ id: string; kind: string }>;
  assert.equal(new Set(nodes.map((node) => node.id)).size, nodes.length, "graph node IDs must be unique");
  for (const [id, kind] of [["Order", "entity"], ["Money", "value-object"], ["OrderStatus", "enum"], ["CommitOrder", "operation"], ["OpenOrders", "query"], ["AddFee", "calculation"], ["PositiveAmount", "rule"], ["OrderPolicy", "policy"], ["FulfilOrder", "workflow"], ["order-committed", "event"], ["OrdersApi", "interface"], ["OrderToMessage", "mapping"]]) assert.ok(nodes.some((node) => node.id === id && node.kind === kind), `${kind}:${id}`);
  assert.ok(result.plan.state_machines.some((machine) => machine.subject_ref === "Order" && machine.transitions.length > 0), "State Machine:Order");
  assert.equal(result.plan.state_machines.some((machine) => machine.subject_ref === "OutboxMessage"), false, "entities without states must not produce empty state machines");
});

test("one graph identity resolves deterministically to its specialized normalized kind", () => {
  const source = `domain conflict "Conflict"\nowner test-owner\nlogic sfol-v1\n\nentity Shared:\n  id: identifier required\n\nevent Shared:\n  payload id\n`;
  const nodes = JSON.parse(compileCarrier(parseDomainSource(source).carrier).files["domain.graph.json"]).nodes as Array<{ id: string; kind: string }>;
  assert.deepEqual(nodes.filter((node) => node.id === "Shared"), [{ id: "Shared", kind: "event" }]);
});
