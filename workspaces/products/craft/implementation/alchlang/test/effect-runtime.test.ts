import assert from "node:assert/strict";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { CompilationRejected, SqliteTransactionalOutbox, SqliteTransactionalOutboxActionAdapter, TransactionalOutboxWorker, compileCarrier, executeAction, parseDomainSource, resolveSqliteTransactionalOutboxEffect } from "../src/index.js";
import type { AtomicStateAndOutboxRequest } from "../src/index.js";

const root = path.resolve(import.meta.dirname, "..");
const model = compileCarrier(parseDomainSource(readFileSync(path.join(root, "examples/outbox-operation.md"), "utf8")).carrier).plan.model;
const request: AtomicStateAndOutboxRequest = {
  aggregateType: "OrderOperation",
  aggregateId: "operation-1",
  state: { operationId: "operation-1", orderId: "order-1", status: "committed" },
  expectedVersion: 0,
  messages: [{ messageId: "message-1", eventType: "outbox-message-recorded", payload: { orderId: "order-1" }, occurredAt: "2026-09-03T12:00:00.000Z" }]
};
const facts = { operationId: "operation-1", orderId: "order-1", status: "pending", outboxMessageId: "message-1", occurredAt: "2026-09-03T12:00:00.000Z", payload: { kind: "order-committed" } };
const databasePath = (): string => path.join(mkdtempSync(path.join(tmpdir(), "domainspec-runtime-outbox-")), "outbox.sqlite");

test("resolver closes the exact action, effect, provider, guarantee and boundary", () => {
  const effect = resolveSqliteTransactionalOutboxEffect(model, "CommitOrderWithOutbox", "sqlite-transactional-outbox");
  assert.equal(effect.id, "PersistOrderWithOutbox");
  assert.throws(() => resolveSqliteTransactionalOutboxEffect(model, "CommitOrderWithOutbox", "postgres-outbox"), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "EFFECT_BINDING_NOT_DECLARED");
});

test("action adapter commits versioned state and pending message after guards", async () => {
  const adapter = SqliteTransactionalOutboxActionAdapter.open({ model, actionId: "CommitOrderWithOutbox", bindingId: "sqlite-transactional-outbox", databasePath: databasePath(), effectRequest: request });
  try {
    const result = await executeAction(model, { action_id: "CommitOrderWithOutbox", actor_ref: "OrderService", facts, authority_grants: ["order-transaction-authority"] }, { CommitOrderWithOutbox: adapter });
    assert.equal(result.outcome, "committed-with-outbox");
    assert.deepEqual(adapter.outbox.state("OrderOperation", "operation-1"), { state: request.state, version: 1 });
    assert.equal(adapter.outbox.pending()[0].messageId, "message-1");
  } finally { adapter.close(); }
});

test("binding resolver rejects undeclared aggregates and events before persistence", () => {
  assert.throws(() => SqliteTransactionalOutboxActionAdapter.open({ model, actionId: "CommitOrderWithOutbox", bindingId: "sqlite-transactional-outbox", databasePath: databasePath(), effectRequest: { ...request, aggregateType: "Customer" } }), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "EFFECT_AGGREGATE_NOT_DECLARED");
  assert.throws(() => SqliteTransactionalOutboxActionAdapter.open({ model, actionId: "CommitOrderWithOutbox", bindingId: "sqlite-transactional-outbox", databasePath: databasePath(), effectRequest: { ...request, messages: [{ ...request.messages[0], eventType: "undeclared" }] } }), (error: unknown) => error instanceof CompilationRejected && error.issues[0].code === "EFFECT_EVENT_NOT_DECLARED");
});

test("transaction failpoint and stale version leave no partial successor write", () => {
  const outbox = new SqliteTransactionalOutbox(databasePath());
  try {
    assert.throws(() => outbox.commit(request, "after-state-write"), /OUTBOX_FAILPOINT_AFTER_STATE_WRITE/);
    assert.equal(outbox.state("OrderOperation", "operation-1"), null);
    assert.deepEqual(outbox.pending(), []);
    outbox.commit(request);
    assert.throws(() => outbox.commit({ ...request, messages: [{ ...request.messages[0], messageId: "message-2" }] }), /OUTBOX_VERSION_CONFLICT/);
    assert.equal(outbox.pending().length, 1);
    assert.equal(outbox.state("OrderOperation", "operation-1")?.version, 1);
  } finally { outbox.close(); }
});

test("worker keeps failed messages retryable and marks a later success published", async () => {
  const outbox = new SqliteTransactionalOutbox(databasePath());
  let fail = true;
  const seen: string[] = [];
  try {
    outbox.commit(request);
    const worker = new TransactionalOutboxWorker(outbox, { async publish(message) { seen.push(message.messageId); if (fail) throw new Error("transport-down"); } });
    assert.deepEqual(await worker.dispatchPending(), { published: 0, failed: 1 });
    assert.equal(outbox.pending()[0].attempts, 1);
    assert.equal(outbox.pending()[0].lastError, "transport-down");
    fail = false;
    assert.deepEqual(await worker.dispatchPending(), { published: 1, failed: 0 });
    assert.deepEqual(seen, ["message-1", "message-1"]);
    assert.deepEqual(outbox.stats(), { pending: 0, published: 1 });
  } finally { outbox.close(); }
});
