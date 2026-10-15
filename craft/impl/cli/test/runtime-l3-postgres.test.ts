import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { runDurableOperation } from "../src/runtime/durable.ts";
import { HttpPostgresOutboxTransport, PostgresOutboxWorker, PostgresTransactionalOutbox } from "../src/runtime/postgres-outbox.ts";
import { createCompleteL1Project } from "./helpers/l1-project.ts";
import { validateRuntimeReceiptBinding } from "../src/runtime/receipt.ts";

const node = process.execPath;

function requireCommand(command: string, arguments_: string[]): void {
  const result = spawnSync(command, arguments_, { encoding: "utf8", timeout: 10_000 });
  assert.equal(result.status, 0, `PostgreSQL test prerequisite ${command}: ${result.error?.message ?? result.stderr}`);
}
function invocation(aggregateId: string, eventId: string) { return { schema_version: "domainspec.durable-operation-invocation/v1", invocation_id: `run-${aggregateId}`, selector: "alpha:settle", operation_input: { state: { customer: aggregateId, "customer.settlement-status": "pending" }, changes: { "customer.settlement-status": "settled" }, guard: true }, transaction: { aggregate_type: "Settlement", aggregate_id: aggregateId, expected_version: 0, occurred_at: "2026-09-03T12:00:00.000Z", event_ids: { "alpha:settlement-requested": eventId }, event_payloads: { "alpha:settlement-requested": { aggregate_id: aggregateId } }, max_attempts: 2 } }; }

test("PostgreSQL profile passes transaction, replay, leases, retry, quarantine, restart, and CLI seams", async () => {
  requireCommand("psql", ["--version"]);
  requireCommand("pg_isready", ["--version"]);
  requireCommand("docker", ["version", "--format", "{{.Server.Version}}"]);
  const name = `domainspec-pg-${process.pid}-${Date.now()}`;
  const fixture = createCompleteL1Project(); const output = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-postgres-"));
  let started = false;
  let launchAttempted = false;
  try {
    launchAttempted = true;
    const launched = spawnSync("docker", ["run", "--rm", "-d", "--name", name, "-e", "POSTGRES_PASSWORD=domainspec-test", "-e", "POSTGRES_DB=domainspec", "-p", "127.0.0.1::5432", process.env.DOMAINSPEC_TEST_POSTGRES_IMAGE ?? "postgres:16"], { encoding: "utf8", timeout: 60_000 });
    started = launched.status === 0;
    assert.equal(launched.status, 0, launched.error?.message ?? launched.stderr);
    const portOutput = spawnSync("docker", ["port", name, "5432/tcp"], { encoding: "utf8" }); assert.equal(portOutput.status, 0, portOutput.stderr); const port = Number(portOutput.stdout.trim().split(":").at(-1));
    let ready = false; let readinessDiagnostic = "";
    for (let attempt = 0; attempt < 60; attempt++) {
      const check = spawnSync("pg_isready", ["-h", "127.0.0.1", "-p", String(port), "-U", "postgres", "-d", "domainspec", "-t", "1"], { encoding: "utf8", timeout: 2_000 });
      readinessDiagnostic = check.error?.message ?? `${check.stdout}${check.stderr}`;
      if (check.status === 0) { ready = true; break; }
      assert.equal(check.error, undefined, readinessDiagnostic);
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 250);
    }
    assert.equal(ready, true, `PostgreSQL did not become ready: ${readinessDiagnostic}`);
    const config = { host: "127.0.0.1", port, database: "domainspec", user: "postgres", password: "domainspec-test" }; const store = new PostgresTransactionalOutbox(config);
    const first = runDurableOperation(fixture.root, invocation("settlement-pg-1", "event-pg-1"), store); assert.equal(first.commit_status, "committed"); assert.equal(validateRuntimeReceiptBinding(fixture.root, first), first); assert.equal(store.records("pending").length, 1);
    assert.equal(runDurableOperation(fixture.root, invocation("settlement-pg-1", "event-pg-1"), store).commit_status, "already-committed"); assert.equal(store.records().length, 1);
    assert.throws(() => runDurableOperation(fixture.root, invocation("settlement-pg-fail", "event-pg-fail"), store, "after-state-write"), /OUTBOX_FAILPOINT_AFTER_STATE_WRITE/); assert.equal(store.state("Settlement", "settlement-pg-fail"), null);
    const claimed = store.claim("worker-a", "2026-09-03T12:00:00.000Z", 1000); assert.equal(claimed.length, 1); assert.equal(store.claim("worker-b", "2026-09-03T12:00:00.500Z", 1000).length, 0); assert.throws(() => store.markPublished("event-pg-1", "worker-b", "2026-09-03T12:00:00.500Z"), /LEASE_NOT_OWNED/);
    let publishedRequest: { url: string; headers: Readonly<Record<string, string>>; body: string } | null = null; const http = new HttpPostgresOutboxTransport("https://events.example.test/outbox", { async send(input) { publishedRequest = input; return { status: 202 }; } }); await http.publish(claimed[0]!); assert.equal(publishedRequest!.headers["idempotency-key"], "event-pg-1"); assert.equal(JSON.parse(publishedRequest!.body).eventType, "settlement-requested");
    store.markFailed("event-pg-1", "worker-a", "broker-down", "2026-09-03T12:00:01.000Z"); const clock = "2026-09-03T12:00:01.000Z"; const worker = new PostgresOutboxWorker(store, { async publish() { throw new Error("poison"); } }, { workerId: "worker-b", clock: () => clock, retryBaseMs: 1000 }); assert.deepEqual(await worker.dispatch(), { published: 0, failed: 1, dead: 1 }); assert.equal(store.records("dead")[0]!.quarantineReason, "poison"); assert.equal(store.attempts("event-pg-1").length, 2); store.requeueDead("event-pg-1", "2026-09-03T12:00:03.000Z"); assert.equal(store.records("pending").length, 1);
    assert.equal(store.consumeOnce("event-pg-1", "settlement-requested", "2026-09-03T12:00:02.000Z", "settlement-effect-1"), "processed"); assert.equal(store.consumeOnce("event-pg-1", "settlement-requested", "2026-09-03T12:00:03.000Z", "settlement-effect-1"), "duplicate"); assert.equal(store.consumerEffects(), 1);
    const requestPath = path.join(output, "request.json"), receiptPath = path.join(output, "receipt.json"); fs.writeFileSync(requestPath, `${JSON.stringify(invocation("settlement-pg-cli", "event-pg-cli"), null, 2)}\n`);
    const cli = spawnSync(node, ["--import", "tsx", path.resolve("src/cli/main.ts"), "run", fixture.root, "--request", requestPath, "--receipt", receiptPath, "--provider", "postgres-transactional-outbox-v1"], { cwd: path.resolve("."), encoding: "utf8", env: { ...process.env, PGHOST: config.host, PGPORT: String(port), PGDATABASE: config.database, PGUSER: config.user, PGPASSWORD: config.password } }); assert.equal(cli.status, 0, `${cli.stdout}\n${cli.stderr}`); const receipt = JSON.parse(fs.readFileSync(receiptPath, "utf8")); assert.equal(receipt.provider, "postgres-transactional-outbox-v1"); assert.equal(receipt.commit_status, "committed"); assert.equal(store.records().length, 2);
    const schema = spawnSync("python3", ["-c", "import json,sys;from jsonschema import Draft202012Validator;Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(open(sys.argv[2])));Draft202012Validator(json.load(open(sys.argv[3]))).validate(json.load(open(sys.argv[4])))", path.resolve("contracts/durable-operation-invocation.schema.json"), requestPath, path.resolve("contracts/durable-operation-receipt.schema.json"), receiptPath], { encoding: "utf8" }); assert.equal(schema.status, 0, schema.stderr);
  } finally {
    try {
      if (launchAttempted) {
        const removed = spawnSync("docker", ["rm", "-f", "-v", name], { encoding: "utf8", timeout: 10_000 });
        if (started) assert.equal(removed.status, 0, removed.error?.message ?? removed.stderr);
      }
    } finally {
      fs.rmSync(output, { recursive: true, force: true }); fs.rmSync(fixture.parent, { recursive: true, force: true });
    }
  }
});
