import type { NormalizedEffect } from "./model.js";

const literal = (value: unknown): string => JSON.stringify(value, null, 2);

export function renderSqliteTransactionalOutbox(effect: NormalizedEffect): Record<string, string> {
  if (effect.pattern_ref !== "transactional-outbox" || effect.integration_binding_ref !== "sqlite-transactional-outbox") {
    throw new Error(`OUTBOX_GENERATOR_BINDING_MISMATCH:${effect.id}`);
  }
  const contract = {
    effect_id: effect.id,
    pattern_ref: effect.pattern_ref,
    integration_binding_ref: effect.integration_binding_ref,
    write_refs: effect.write_refs,
    event_refs: effect.event_refs,
    guarantee: effect.guarantee,
    failure_continuation: effect.failure_continuation,
    authority_boundary_ref: effect.authority_boundary_ref,
    delivery: "at-least-once"
  };
  const migration = `CREATE TABLE IF NOT EXISTS domainspec_aggregate_state (
  aggregate_type TEXT NOT NULL,
  aggregate_id TEXT NOT NULL,
  state_json TEXT NOT NULL,
  version INTEGER NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (aggregate_type, aggregate_id)
);
CREATE TABLE IF NOT EXISTS domainspec_outbox (
  message_id TEXT PRIMARY KEY,
  aggregate_type TEXT NOT NULL,
  aggregate_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'published')),
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT
);
CREATE INDEX IF NOT EXISTS domainspec_outbox_pending_idx ON domainspec_outbox(status, occurred_at, message_id);
`;
  const port = `export interface OutboxMessage {
  readonly messageId: string;
  readonly eventType: string;
  readonly payload: Readonly<Record<string, unknown>>;
  readonly occurredAt: string;
}
export interface AtomicStateAndOutboxRequest {
  readonly aggregateType: string;
  readonly aggregateId: string;
  readonly state: Readonly<Record<string, unknown>>;
  readonly expectedVersion: number;
  readonly messages: readonly OutboxMessage[];
}
export interface PendingOutboxMessage extends OutboxMessage {
  readonly aggregateType: string;
  readonly aggregateId: string;
  readonly attempts: number;
}
export interface TransactionalOutboxPort {
  commit(request: AtomicStateAndOutboxRequest, failpoint?: "after-state-write"): void;
  pending(limit?: number): readonly PendingOutboxMessage[];
  markPublished(messageId: string): void;
  markFailed(messageId: string, error: string): void;
}
export interface OutboxTransport { publish(message: PendingOutboxMessage): Promise<void>; }
export const transactionalOutboxContract = ${literal(contract)} as const;
`;
  const sqlite = `import { DatabaseSync } from "node:sqlite";
import type { AtomicStateAndOutboxRequest, PendingOutboxMessage, TransactionalOutboxPort } from "./domain.outbox.port.js";

export const migrationSql = ${JSON.stringify(migration)};
type Row = { message_id: string; aggregate_type: string; aggregate_id: string; event_type: string; payload_json: string; occurred_at: string; attempts: number };

export class SqliteTransactionalOutbox implements TransactionalOutboxPort, Disposable {
  readonly database: DatabaseSync;
  constructor(path: string) { this.database = new DatabaseSync(path); this.database.exec(migrationSql); }
  commit(request: AtomicStateAndOutboxRequest, failpoint?: "after-state-write"): void {
    if (request.messages.length === 0) throw new Error("OUTBOX_MESSAGE_REQUIRED");
    this.database.exec("BEGIN IMMEDIATE");
    try {
      const existing = this.database.prepare("SELECT version FROM domainspec_aggregate_state WHERE aggregate_type = ? AND aggregate_id = ?").get(request.aggregateType, request.aggregateId) as { version: number } | undefined;
      if ((existing?.version ?? 0) !== request.expectedVersion) throw new Error("OUTBOX_VERSION_CONFLICT");
      this.database.prepare("INSERT INTO domainspec_aggregate_state (aggregate_type, aggregate_id, state_json, version, updated_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(aggregate_type, aggregate_id) DO UPDATE SET state_json = excluded.state_json, version = excluded.version, updated_at = excluded.updated_at").run(request.aggregateType, request.aggregateId, JSON.stringify(request.state), request.expectedVersion + 1, request.messages[0].occurredAt);
      if (failpoint === "after-state-write") throw new Error("OUTBOX_FAILPOINT_AFTER_STATE_WRITE");
      const insert = this.database.prepare("INSERT INTO domainspec_outbox (message_id, aggregate_type, aggregate_id, event_type, payload_json, occurred_at) VALUES (?, ?, ?, ?, ?, ?)");
      for (const message of request.messages) insert.run(message.messageId, request.aggregateType, request.aggregateId, message.eventType, JSON.stringify(message.payload), message.occurredAt);
      this.database.exec("COMMIT");
    } catch (error) {
      this.database.exec("ROLLBACK");
      throw error;
    }
  }
  state(aggregateType: string, aggregateId: string): { state: Readonly<Record<string, unknown>>; version: number } | null {
    const row = this.database.prepare("SELECT state_json, version FROM domainspec_aggregate_state WHERE aggregate_type = ? AND aggregate_id = ?").get(aggregateType, aggregateId) as { state_json: string; version: number } | undefined;
    return row ? { state: JSON.parse(row.state_json) as Readonly<Record<string, unknown>>, version: row.version } : null;
  }
  pending(limit = 100): readonly PendingOutboxMessage[] {
    const rows = this.database.prepare("SELECT message_id, aggregate_type, aggregate_id, event_type, payload_json, occurred_at, attempts FROM domainspec_outbox WHERE status = 'pending' ORDER BY occurred_at, message_id LIMIT ?").all(limit) as Row[];
    return rows.map((row) => ({ messageId: row.message_id, aggregateType: row.aggregate_type, aggregateId: row.aggregate_id, eventType: row.event_type, payload: JSON.parse(row.payload_json) as Readonly<Record<string, unknown>>, occurredAt: row.occurred_at, attempts: row.attempts }));
  }
  markPublished(messageId: string): void { this.database.prepare("UPDATE domainspec_outbox SET status = 'published', attempts = attempts + 1, last_error = NULL WHERE message_id = ?").run(messageId); }
  markFailed(messageId: string, error: string): void { this.database.prepare("UPDATE domainspec_outbox SET attempts = attempts + 1, last_error = ? WHERE message_id = ?").run(error, messageId); }
  close(): void { this.database.close(); }
  [Symbol.dispose](): void { this.close(); }
}
`;
  const worker = `import type { OutboxTransport } from "./domain.outbox.port.js";
import type { SqliteTransactionalOutbox } from "./domain.outbox.sqlite.js";

export class TransactionalOutboxWorker {
  constructor(private readonly outbox: SqliteTransactionalOutbox, private readonly transport: OutboxTransport) {}
  async dispatchPending(limit = 100): Promise<{ published: number; failed: number }> {
    let published = 0; let failed = 0;
    for (const message of this.outbox.pending(limit)) {
      try { await this.transport.publish(message); this.outbox.markPublished(message.messageId); published += 1; }
      catch (error) { this.outbox.markFailed(message.messageId, error instanceof Error ? error.message : String(error)); failed += 1; }
    }
    return { published, failed };
  }
}
`;
  const durableProvider = `// Provider binding generated from the exact sqlite-transactional-outbox effect.
export {
  CollectingOutboxTelemetry,
  DurableOutboxWorker,
  DurableSqliteTransactionalOutbox,
  FetchOutboxHttpClient,
  HttpOutboxTransport,
  SqliteIdempotentInbox
} from "@cyberalchemy/domainspec-cli-candidate";
export type {
  DurableCommitRequest,
  DurableOutboxRecord,
  DurableOutboxTransport,
  DurableWorkerOptions,
  OutboxTelemetrySink
} from "@cyberalchemy/domainspec-cli-candidate";
export const providerBinding = ${literal({ binding: "sqlite-transactional-outbox", schema_version: 2, dispatch: "claim-lease-at-least-once", retry: "bounded-exponential-dead-letter", consumer: "sqlite-transactional-inbox", network: "explicit-confirmed-allowlisted-http" })} as const;
`;
  const test = `import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { SqliteTransactionalOutbox } from "./domain.outbox.sqlite.js";
import { TransactionalOutboxWorker } from "./domain.outbox.worker.js";

const request = { aggregateType: "Order", aggregateId: "order-1", state: { status: "committed" }, expectedVersion: 0, messages: [{ messageId: "message-1", eventType: "order-committed", payload: { orderId: "order-1" }, occurredAt: "2026-09-02T00:00:00.000Z" }] } as const;
test("business state and pending message commit atomically", () => {
  const store = new SqliteTransactionalOutbox(path.join(mkdtempSync(path.join(tmpdir(), "generated-outbox-")), "db.sqlite"));
  try { store.commit(request); assert.deepEqual(store.state("Order", "order-1"), { state: { status: "committed" }, version: 1 }); assert.equal(store.pending().length, 1); }
  finally { store.close(); }
});
test("failure after state write rolls back state and message", () => {
  const store = new SqliteTransactionalOutbox(path.join(mkdtempSync(path.join(tmpdir(), "generated-outbox-")), "db.sqlite"));
  try { assert.throws(() => store.commit(request, "after-state-write"), /OUTBOX_FAILPOINT/); assert.equal(store.state("Order", "order-1"), null); assert.equal(store.pending().length, 0); }
  finally { store.close(); }
});
test("delivery is at least once and retains stable message identity across retry", async () => {
  const store = new SqliteTransactionalOutbox(path.join(mkdtempSync(path.join(tmpdir(), "generated-outbox-")), "db.sqlite"));
  const seen: string[] = []; let first = true;
  try {
    store.commit(request);
    const worker = new TransactionalOutboxWorker(store, { async publish(message) { seen.push(message.messageId); if (first) { first = false; throw new Error("ack-lost"); } } });
    assert.deepEqual(await worker.dispatchPending(), { published: 0, failed: 1 });
    assert.deepEqual(await worker.dispatchPending(), { published: 1, failed: 0 });
    assert.deepEqual(seen, ["message-1", "message-1"]); assert.equal(store.pending().length, 0);
  } finally { store.close(); }
});
`;
  return {
    "domain.outbox.port.ts": port,
    "domain.outbox.sqlite.ts": sqlite,
    "domain.outbox.migration.sql": migration,
    "domain.outbox.worker.ts": worker,
    "domain.outbox.provider.ts": durableProvider,
    "domain.outbox.test.ts": test,
    "domain.generation-manifest.json": `${JSON.stringify({ schema_version: "cav2.alchlang.effect-generation-manifest/v1-candidate", effect: contract, generated_artifacts: ["domain.outbox.port.ts", "domain.outbox.sqlite.ts", "domain.outbox.migration.sql", "domain.outbox.worker.ts", "domain.outbox.provider.ts", "domain.outbox.test.ts"], provider_runtime: { schema_version: 2, claim_lease: true, bounded_retry: true, dead_letter: true, replay_reconciliation: true, idempotent_inbox: true, confirmed_http: true, telemetry: true }, authority_effect: "none", claim_ceiling: "Generated local SQLite provider binding candidate; HTTP remains explicit and confirmation-gated, and no stable promotion, release, deployment, production or exactly-once delivery claim follows." }, null, 2)}\\n`
  };
}
