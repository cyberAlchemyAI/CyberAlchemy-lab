import type { ActionAdapter, AdapterRequest, AdapterResult } from "./runtime.js";

export class MemoryActionAdapter implements ActionAdapter {
  readonly records: AdapterRequest[] = [];
  constructor(private readonly result: AdapterResult = { outcome: "completed" }) {}
  async execute(request: AdapterRequest): Promise<AdapterResult> { this.records.push(structuredClone(request)); return structuredClone(this.result); }
}

type LocalDatabase = { exec(sql: string): void; prepare(sql: string): { run(...values: unknown[]): unknown; all(): unknown[] }; close(): void };

export class SqliteActionAdapter implements ActionAdapter, Disposable {
  private constructor(private readonly database: LocalDatabase, private readonly result: AdapterResult) {
    this.database.exec("CREATE TABLE IF NOT EXISTS domainspec_actions (id INTEGER PRIMARY KEY AUTOINCREMENT, domain_id TEXT NOT NULL, action_id TEXT NOT NULL, actor_ref TEXT NOT NULL, authority_boundary_ref TEXT NOT NULL, facts_json TEXT NOT NULL)");
  }
  static async open(path: string, result: AdapterResult = { outcome: "persisted" }): Promise<SqliteActionAdapter> {
    const { DatabaseSync } = await import("node:sqlite");
    return new SqliteActionAdapter(new DatabaseSync(path), result);
  }
  async execute(request: AdapterRequest): Promise<AdapterResult> {
    this.database.prepare("INSERT INTO domainspec_actions (domain_id, action_id, actor_ref, authority_boundary_ref, facts_json) VALUES (?, ?, ?, ?, ?)").run(request.domain_id, request.action_id, request.actor_ref, request.authority_boundary_ref, JSON.stringify(request.facts));
    return structuredClone(this.result);
  }
  records(): unknown[] { return this.database.prepare("SELECT domain_id, action_id, actor_ref, authority_boundary_ref, facts_json FROM domainspec_actions ORDER BY id").all(); }
  close(): void { this.database.close(); }
  [Symbol.dispose](): void { this.close(); }
}

export interface HttpTransport { request(input: { url: string; method: "POST"; headers: Readonly<Record<string, string>>; body: string }): Promise<{ status: number; body: string }> }

export class FetchHttpTransport implements HttpTransport {
  constructor(private readonly allowedOrigins: readonly string[]) {}
  async request(input: { url: string; method: "POST"; headers: Readonly<Record<string, string>>; body: string }): Promise<{ status: number; body: string }> {
    const url = new URL(input.url);
    if (!this.allowedOrigins.includes(url.origin)) throw new Error(`HTTP_ORIGIN_DENIED:${url.origin}`);
    const response = await fetch(url, { method: input.method, headers: input.headers, body: input.body, redirect: "error" });
    return { status: response.status, body: await response.text() };
  }
}

export class HttpActionAdapter implements ActionAdapter {
  constructor(private readonly endpoint: string, private readonly transport: HttpTransport, private readonly emittedEvents: readonly string[] = []) {}
  async execute(request: AdapterRequest): Promise<AdapterResult> {
    const response = await this.transport.request({ url: this.endpoint, method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(request) });
    if (response.status < 200 || response.status >= 300) throw new Error(`HTTP_ADAPTER_FAILED:${response.status}`);
    return { outcome: "http-accepted", emitted_events: this.emittedEvents, data: response.body ? JSON.parse(response.body) : null };
  }
}
