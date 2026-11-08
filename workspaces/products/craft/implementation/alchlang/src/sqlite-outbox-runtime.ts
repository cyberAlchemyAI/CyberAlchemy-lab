import { DatabaseSync } from "node:sqlite";

export interface OutboxMessage {
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
  readonly lastError: string | null;
}

export interface OutboxTransport {
  publish(message: PendingOutboxMessage): Promise<void>;
}

export const sqliteOutboxMigrationSql = `CREATE TABLE IF NOT EXISTS domainspec_aggregate_state (
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

type OutboxRow = {
  message_id: string;
  aggregate_type: string;
  aggregate_id: string;
  event_type: string;
  payload_json: string;
  occurred_at: string;
  attempts: number;
  last_error: string | null;
};

function nonEmpty(value: unknown, code: string): asserts value is string {
  if (typeof value !== "string" || value.length === 0) throw new Error(code);
}

export function validateAtomicStateAndOutboxRequest(value: unknown): asserts value is AtomicStateAndOutboxRequest {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("OUTBOX_REQUEST_INVALID");
  const request = value as Record<string, unknown>;
  nonEmpty(request.aggregateType, "OUTBOX_AGGREGATE_TYPE_REQUIRED");
  nonEmpty(request.aggregateId, "OUTBOX_AGGREGATE_ID_REQUIRED");
  if (!request.state || typeof request.state !== "object" || Array.isArray(request.state)) throw new Error("OUTBOX_STATE_REQUIRED");
  if (!Number.isSafeInteger(request.expectedVersion) || Number(request.expectedVersion) < 0) throw new Error("OUTBOX_EXPECTED_VERSION_INVALID");
  if (!Array.isArray(request.messages) || request.messages.length === 0) throw new Error("OUTBOX_MESSAGE_REQUIRED");
  const ids = new Set<string>();
  for (const raw of request.messages) {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) throw new Error("OUTBOX_MESSAGE_INVALID");
    const message = raw as Record<string, unknown>;
    nonEmpty(message.messageId, "OUTBOX_MESSAGE_ID_REQUIRED");
    nonEmpty(message.eventType, "OUTBOX_EVENT_TYPE_REQUIRED");
    nonEmpty(message.occurredAt, "OUTBOX_OCCURRED_AT_REQUIRED");
    if (Number.isNaN(Date.parse(message.occurredAt))) throw new Error("OUTBOX_OCCURRED_AT_INVALID");
    if (!message.payload || typeof message.payload !== "object" || Array.isArray(message.payload)) throw new Error("OUTBOX_PAYLOAD_REQUIRED");
    if (ids.has(message.messageId)) throw new Error("OUTBOX_DUPLICATE_MESSAGE_ID");
    ids.add(message.messageId);
  }
}

export class SqliteTransactionalOutbox implements Disposable {
  readonly database: DatabaseSync;

  constructor(path: string) {
    nonEmpty(path, "OUTBOX_DATABASE_PATH_REQUIRED");
    this.database = new DatabaseSync(path);
    this.database.exec(sqliteOutboxMigrationSql);
  }

  commit(request: AtomicStateAndOutboxRequest, failpoint?: "after-state-write"): void {
    validateAtomicStateAndOutboxRequest(request);
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
    if (!Number.isSafeInteger(limit) || limit < 1) throw new Error("OUTBOX_LIMIT_INVALID");
    const rows = this.database.prepare("SELECT message_id, aggregate_type, aggregate_id, event_type, payload_json, occurred_at, attempts, last_error FROM domainspec_outbox WHERE status = 'pending' ORDER BY occurred_at, message_id LIMIT ?").all(limit) as OutboxRow[];
    return rows.map((row) => ({ messageId: row.message_id, aggregateType: row.aggregate_type, aggregateId: row.aggregate_id, eventType: row.event_type, payload: JSON.parse(row.payload_json) as Readonly<Record<string, unknown>>, occurredAt: row.occurred_at, attempts: row.attempts, lastError: row.last_error }));
  }

  markPublished(messageId: string): void {
    const result = this.database.prepare("UPDATE domainspec_outbox SET status = 'published', attempts = attempts + 1, last_error = NULL WHERE message_id = ? AND status = 'pending'").run(messageId);
    if (result.changes !== 1) throw new Error(`OUTBOX_PENDING_MESSAGE_NOT_FOUND:${messageId}`);
  }

  markFailed(messageId: string, error: string): void {
    const result = this.database.prepare("UPDATE domainspec_outbox SET attempts = attempts + 1, last_error = ? WHERE message_id = ? AND status = 'pending'").run(error, messageId);
    if (result.changes !== 1) throw new Error(`OUTBOX_PENDING_MESSAGE_NOT_FOUND:${messageId}`);
  }

  stats(): Readonly<{ pending: number; published: number }> {
    const rows = this.database.prepare("SELECT status, COUNT(*) AS count FROM domainspec_outbox GROUP BY status").all() as Array<{ status: "pending" | "published"; count: number }>;
    const result = { pending: 0, published: 0 };
    for (const row of rows) result[row.status] = row.count;
    return result;
  }

  close(): void { this.database.close(); }
  [Symbol.dispose](): void { this.close(); }
}

export class TransactionalOutboxWorker {
  constructor(private readonly outbox: SqliteTransactionalOutbox, private readonly transport: OutboxTransport) {}

  async dispatchPending(limit = 100): Promise<{ published: number; failed: number }> {
    let published = 0;
    let failed = 0;
    for (const message of this.outbox.pending(limit)) {
      try {
        await this.transport.publish(message);
        this.outbox.markPublished(message.messageId);
        published += 1;
      } catch (error) {
        this.outbox.markFailed(message.messageId, error instanceof Error ? error.message : String(error));
        failed += 1;
      }
    }
    return { published, failed };
  }
}

export class CollectingStdoutOutboxTransport implements OutboxTransport {
  readonly messages: PendingOutboxMessage[] = [];
  async publish(message: PendingOutboxMessage): Promise<void> { this.messages.push(structuredClone(message)); }
}
