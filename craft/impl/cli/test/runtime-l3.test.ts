import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { runDurableOperation, type DurableCommitRequestV1, type TransactionalOutboxPortV1 } from "../src/runtime/durable.ts";
import { RuntimeContractError } from "../src/runtime/contracts.ts";
import { validateRuntimeReceiptBinding } from "../src/runtime/receipt.ts";
import { createCompleteL1Project } from "./helpers/l1-project.ts";
import { DurableOutboxWorker, DurableSqliteTransactionalOutbox } from "../../../../../cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/durable-outbox-runtime.ts";
import { SqliteIdempotentInbox } from "../../../../../cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/outbox-integrations.ts";

const implementationPath = path.resolve("../../../../cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/durable-outbox-runtime.ts");
const implementationSha256 = createHash("sha256").update(fs.readFileSync(implementationPath)).digest("hex");
function request(guard = true) { return { schema_version: "domainspec.durable-operation-invocation/v1", invocation_id: "durable-settlement", selector: "alpha:settle", operation_input: { state: { customer: "customer-1", "customer.settlement-status": "pending" }, changes: { "customer.settlement-status": "settled" }, guard }, transaction: { aggregate_type: "Settlement", aggregate_id: "settlement-1", expected_version: 0, occurred_at: "2026-09-03T12:00:00.000Z", event_ids: { "alpha:settlement-requested": "event-1" }, event_payloads: { "alpha:settlement-requested": {} }, max_attempts: 3 } }; }
function port(database: string): TransactionalOutboxPortV1 & Disposable & { readonly store: DurableSqliteTransactionalOutbox } {
  const store = new DurableSqliteTransactionalOutbox(database);
  return { provider_id: "sqlite-transactional-outbox-v1", implementation_sha256: implementationSha256, store, commit(value: DurableCommitRequestV1, failpoint?: "after-state-write") { return store.commit(value, failpoint); }, [Symbol.dispose]() { store.close(); } };
}

test("compiled Operation state and Event intent commit atomically through the existing outbox", () => {
  const fixture = createCompleteL1Project(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l3-")); const provider = port(path.join(parent, "outbox.sqlite"));
  try {
    const receipt = runDurableOperation(fixture.root, request(), provider);
    assert.equal(receipt.commit_status, "committed"); assert.equal(receipt.committed_version, 1); assert.deepEqual(receipt.event_ids, ["event-1"]);
    assert.match(receipt.checked_interchange_sha256, /^[a-f0-9]{64}$/); assert.equal(validateRuntimeReceiptBinding(fixture.root, receipt), receipt);
    assert.deepEqual(provider.store.state("Settlement", "settlement-1"), { state: { customer: "customer-1", "customer.settlement-status": "settled" }, version: 1 });
    assert.deepEqual(provider.store.pending().map(({ messageId, eventType }) => ({ messageId, eventType })), [{ messageId: "event-1", eventType: "settlement-requested" }]);
    const replay = runDurableOperation(fixture.root, request(), provider); assert.equal(replay.commit_status, "already-committed"); assert.equal(provider.store.records().length, 1);
  } finally { provider[Symbol.dispose](); fs.rmSync(parent, { recursive: true, force: true }); fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("guard rejection and transaction failpoint leave no state or outbox residue", () => {
  const fixture = createCompleteL1Project(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l3-fail-"));
  try {
    using rejected = port(path.join(parent, "rejected.sqlite")); const receipt = runDurableOperation(fixture.root, request(false), rejected);
    assert.equal(receipt.commit_status, "guard-rejected"); assert.equal(rejected.store.state("Settlement", "settlement-1"), null); assert.deepEqual(rejected.store.records(), []);
    using failed = port(path.join(parent, "failed.sqlite")); assert.throws(() => runDurableOperation(fixture.root, request(), failed, "after-state-write"), /OUTBOX_FAILPOINT_AFTER_STATE_WRITE/);
    assert.equal(failed.store.state("Settlement", "settlement-1"), null); assert.deepEqual(failed.store.records(), []);
  } finally { fs.rmSync(parent, { recursive: true, force: true }); fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("durable binding rejects non-Operation entries and event-envelope drift before persistence", () => {
  const fixture = createCompleteL1Project(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l3-hostile-")); const provider = port(path.join(parent, "outbox.sqlite"));
  try {
    assert.throws(() => runDurableOperation(fixture.root, { ...request(), selector: "alpha:customer" }, provider), (error: unknown) => error instanceof RuntimeContractError && error.code === "MTCLI_DURABLE_ENTRY");
    const extra = structuredClone(request()); extra.transaction.event_ids["beta:settlement-completed"] = "event-2";
    assert.throws(() => runDurableOperation(fixture.root, extra, provider), (error: unknown) => error instanceof RuntimeContractError && error.code === "MTCLI_DURABLE_EVENT");
    assert.equal(provider.store.state("Settlement", "settlement-1"), null); assert.deepEqual(provider.store.records(), []);
  } finally { provider[Symbol.dispose](); fs.rmSync(parent, { recursive: true, force: true }); fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});

test("a fresh relay instance publishes the compiled Event and consumer deduplication admits one effect", async () => {
  const fixture = createCompleteL1Project(); const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-l3-restart-")); const database = path.join(parent, "outbox.sqlite");
  try {
    const producer = port(database); runDurableOperation(fixture.root, request(), producer);
    producer[Symbol.dispose]();
    using restarted = new DurableSqliteTransactionalOutbox(database); const delivered = [] as string[];
    const worker = new DurableOutboxWorker(restarted, { async publish(message) { delivered.push(message.messageId); } }, { workerId: "restart-worker", clock: () => "2026-09-03T12:00:01.000Z" });
    assert.deepEqual(await worker.dispatch(), { published: 1, failed: 0, dead: 0 }); assert.deepEqual(delivered, ["event-1"]); assert.equal(restarted.records("published").length, 1);
    using inbox = new SqliteIdempotentInbox(path.join(parent, "inbox.sqlite")); let effects = 0;
    assert.equal(inbox.consume({ messageId: "event-1", eventType: "settlement-requested" }, "2026-09-03T12:00:02.000Z", () => { effects += 1; }), "processed");
    assert.equal(inbox.consume({ messageId: "event-1", eventType: "settlement-requested" }, "2026-09-03T12:00:03.000Z", () => { effects += 1; }), "duplicate"); assert.equal(effects, 1);
  } finally { fs.rmSync(parent, { recursive: true, force: true }); fs.rmSync(fixture.parent, { recursive: true, force: true }); }
});
