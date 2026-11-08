import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { FetchHttpTransport, HttpActionAdapter, MemoryActionAdapter, SqliteActionAdapter } from "../src/index.js";
import type { AdapterRequest } from "../src/runtime.js";

const request: AdapterRequest = { domain_id: "test", action_id: "Act", actor_ref: "Actor", facts: { value: 1 }, authority_grants: ["boundary"], authority_boundary_ref: "boundary" };

test("memory adapter records a defensive copy", async () => {
  const adapter = new MemoryActionAdapter(); await adapter.execute(request); assert.deepEqual(adapter.records[0].facts, { value: 1 });
});

test("SQLite adapter persists local action records", async () => {
  const directory = mkdtempSync(path.join(tmpdir(), "domainspec-sqlite-"));
  const adapter = await SqliteActionAdapter.open(path.join(directory, "actions.sqlite"));
  try { await adapter.execute(request); assert.equal(adapter.records().length, 1); } finally { adapter.close(); }
});

test("HTTP adapter uses only its injected transport", async () => {
  const calls: unknown[] = [];
  const adapter = new HttpActionAdapter("http://local.invalid/action", { async request(input) { calls.push(input); return { status: 202, body: "{\"accepted\":true}" }; } }, ["done"]);
  const result = await adapter.execute(request); assert.equal(calls.length, 1); assert.equal(result.outcome, "http-accepted"); assert.deepEqual(result.emitted_events, ["done"]);
});

test("fetch transport permits only an explicitly allowlisted loopback origin", async () => {
  const server = createServer((incoming, response) => { let body = ""; incoming.setEncoding("utf8"); incoming.on("data", (chunk) => { body += chunk; }); incoming.on("end", () => { response.writeHead(202, { "content-type": "application/json" }); response.end(JSON.stringify({ received: JSON.parse(body).action_id })); }); });
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    const address = server.address(); assert.ok(address && typeof address === "object"); const origin = `http://127.0.0.1:${address.port}`;
    const adapter = new HttpActionAdapter(`${origin}/action`, new FetchHttpTransport([origin]));
    const result = await adapter.execute(request); assert.deepEqual(result.data, { received: "Act" });
    const denied = new HttpActionAdapter(`${origin}/action`, new FetchHttpTransport([])); await assert.rejects(() => denied.execute(request), /HTTP_ORIGIN_DENIED/);
  } finally { await new Promise<void>((resolve, reject) => server.close((error) => error ? reject(error) : resolve())); }
});
