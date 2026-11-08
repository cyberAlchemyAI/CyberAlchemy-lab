import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { CompilationRejected, compileCarrier, parseDomainSource } from "../src/index.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = readFileSync(path.join(root, "examples/backend-types.alch"), "utf8");

test("canonical source lowers all thirteen DomainSpec backend meta-types", () => {
  const result = compileCarrier(parseDomainSource(source).carrier);
  assert.equal(result.plan.type_model.length, 2);
  assert.deepEqual(result.plan.type_model.find((type) => type.id === "Order")?.fields.map((field) => field.id), ["orderId", "messageId", "amount", "status"]);
  assert.deepEqual(result.plan.type_model.find((type) => type.id === "OutboxMessage")?.fields.map((field) => field.id), ["payload"]);
  assert.equal(result.plan.value_object_contracts[0].id, "Money");
  assert.deepEqual(result.plan.value_object_contracts[0].equality_fields, ["value", "currency"]);
  assert.deepEqual(result.plan.enum_contracts[0].values.map((value) => value.id), ["pending", "committed"]);
  assert.equal(result.plan.operation_contracts.length, 2);
  assert.equal(result.plan.query_contracts[0].id, "OpenOrders");
  assert.equal(result.plan.calculation_contracts[0].id, "AddFee");
  assert.equal(result.plan.predicate_model[0].id, "PositiveAmount");
  assert.equal(result.plan.policy_contracts[0].id, "OrderPolicy");
  assert.equal(result.plan.workflow_contracts[0].id, "FulfilOrder");
  assert.equal(result.plan.interface_contracts[0].id, "OrdersApi");
  assert.equal(result.plan.event_contracts[0].id, "order-committed");
  assert.equal(result.plan.mapping_contracts[0].id, "OrderToMessage");
  assert.deepEqual(result.plan.state_machines.map((machine) => machine.subject_ref), ["Order"]);
  assert.equal(result.plan.state_machines[0].states.length, 2);
  assert.match(result.files["domain.types.ts"], /readonly "currency": string/);
  assert.match(result.files["domain.types.ts"], /export type OrderStatus = "pending" \| "committed"/);
  assert.match(result.files["domain.operations.ts"], /CommitOrder/);
  assert.match(result.files["domain.workflows.ts"], /FulfilOrder/);
  assert.match(result.files["domain.interfaces.ts"], /OrdersApi/);
});

test("backend declarations fail closed on their distinguishing criteria", () => {
  const invalid = source
    .replace("  equality value, currency\n", "")
    .replace("  state-change yes\n", "  state-change no\n")
    .replace("  scope intra-feature\n", "  scope ambient\n")
    .replace("  kind external\n", "  kind ambient\n");
  assert.throws(() => parseDomainSource(invalid), (error: unknown) => error instanceof CompilationRejected && ["VALUE_OBJECT_EQUALITY", "OPERATION_STATE_CHANGE", "TEXT_WORKFLOW", "WORKFLOW_SCOPE", "TEXT_INTERFACE", "INTERFACE_KIND"].every((code) => error.issues.some((issue) => issue.code === code)));
});

test("operation rejects effects and writes that are not declared exactly", () => {
  const invalid = source.replace("  writes Order, OutboxMessage\n  effects PersistOrderWithOutbox", "  writes Order\n  effects PersistOrderWithOutbox");
  const carrier = parseDomainSource(invalid).carrier;
  assert.throws(() => compileCarrier(carrier), (error: unknown) => error instanceof CompilationRejected && error.issues.some((issue) => issue.code === "UNDECLARED_OPERATION_WRITE"));
});
