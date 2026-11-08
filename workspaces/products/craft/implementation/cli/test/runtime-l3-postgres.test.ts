import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { runDurableOperation } from "../src/runtime/durable.ts";
import { HttpPostgresOutboxTransport, POSTGRES_OUTBOX_DEDUPLICATION_OWNER, POSTGRES_OUTBOX_SQS_ENVELOPE_PROFILE, SqsPostgresOutboxTransport, PostgresOutboxWorker, PostgresTransactionalOutbox, type PostgresOutboxRecord } from "../src/runtime/postgres-outbox.ts";
import { canonicalJson } from "../src/input/source-manifest.ts";
import { createCompleteL1Project } from "./helpers/l1-project.ts";
import { validateRuntimeReceiptBinding } from "../src/runtime/receipt.ts";
import {createPostgresDocker, installPostgresClients, POSTGRES_TEST_IMAGE} from "./helpers/postgres-clients.ts";

const node = process.execPath;
function invocation(aggregateId: string, eventId: string) { return { schema_version: "domainspec.durable-operation-invocation/v1", invocation_id: `run-${aggregateId}`, selector: "alpha:settle", operation_input: { state: { customer: aggregateId, "customer.settlement-status": "pending" }, changes: { "customer.settlement-status": "settled" }, guard: true }, transaction: { aggregate_type: "Settlement", aggregate_id: aggregateId, expected_version: 0, occurred_at: "2026-09-03T12:00:00.000Z", event_ids: { "alpha:settlement-requested": eventId }, event_payloads: { "alpha:settlement-requested": { aggregate_id: aggregateId } }, max_attempts: 2 } }; }

test("SQS outbox transport records provider acceptance without claiming delivery", async () => {
  const message = { messageId: "event-sqs-1", eventType: "settlement-requested", payload: { settlement: "one" }, occurredAt: "2026-09-03T12:00:00.000Z", aggregateType: "Settlement", aggregateId: "one", status: "leased", attempts: 1, maxAttempts: 5, availableAt: "2026-09-03T12:00:00.000Z", leaseOwner: "worker", leaseUntil: "2026-09-03T12:01:00.000Z", lastError: null, quarantineReason: null, publishedAt: null } satisfies PostgresOutboxRecord;
  let observed: unknown = null;
  const transport = new SqsPostgresOutboxTransport("https://sqs.eu-west-2.amazonaws.com/123456789012/settlement-events", { async send(input) { observed = input; return { messageId: "provider-message-1" }; } });
  await transport.publish(message);
  assert.equal(transport.envelope_profile_ref, POSTGRES_OUTBOX_SQS_ENVELOPE_PROFILE);
  assert.equal(transport.deduplication_owner_ref, POSTGRES_OUTBOX_DEDUPLICATION_OWNER);
  assert.equal((observed as { messageAttributes: Record<string, { stringValue: string }> }).messageAttributes.messageId.stringValue, message.messageId);
  assert.equal((observed as { messageBody: string }).messageBody, canonicalJson({ messageId: message.messageId, eventType: message.eventType, payload: message.payload, occurredAt: message.occurredAt, aggregateType: message.aggregateType, aggregateId: message.aggregateId }));
  const missingAcceptance = new SqsPostgresOutboxTransport("https://sqs.eu-west-2.amazonaws.com/123456789012/settlement-events", { async send() { return {}; } });
  await assert.rejects(() => missingAcceptance.publish(message), /PROVIDER_ACCEPTANCE_MISSING/);
  assert.throws(() => new SqsPostgresOutboxTransport("http://localhost/queue", { async send() { return { messageId: "x" }; } }), /SQS_URL_INVALID/);
});

test("PostgreSQL profile passes transaction, replay, leases, retry, quarantine, restart, and CLI seams", async () => {
  let control: ReturnType<typeof createPostgresDocker> | null = null;
  let name: string | null = null;
  let cidFile: string | null = null;
  const originalPath = process.env.PATH;
  let fixtureParent: string | null = null;
  let output: string | null = null;
  try {
    output = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-postgres-"));
    control = createPostgresDocker(output);
    name = `domainspec-pg-${control.owner}`;
    cidFile = path.join(output, "server.cid");
    const started = control.run(["run", "--rm", "-d", "--pull", "never", "--name", name, "--label", control.label, "--cidfile", cidFile,
      "--read-only", "--security-opt", "no-new-privileges", "--tmpfs", "/tmp:rw,nosuid,noexec", "--tmpfs", "/var/run/postgresql:rw,nosuid,noexec", "--tmpfs", "/var/lib/postgresql/data:rw,nosuid,noexec",
      "-e", "POSTGRES_PASSWORD=domainspec-test", "-e", "POSTGRES_DB=domainspec", "-p", "127.0.0.1::5432", POSTGRES_TEST_IMAGE]);
    assert.equal(started.status, 0, started.stderr);
    assert.match(started.stdout.trim(), /^[0-9a-f]{64}$/);
    assert.equal(fs.readFileSync(cidFile, 'utf8').trim(), started.stdout.trim(), 'server launch acknowledgement must match the CID file');
    const fixture = createCompleteL1Project();
    fixtureParent = fixture.parent;
    const portOutput = control.run(["port", name, "5432/tcp"]); assert.equal(portOutput.status, 0, portOutput.stderr); const port = Number(portOutput.stdout.trim().split(":").at(-1));
    assert.match(portOutput.stdout.trim(), /^127\.0\.0\.1:\d+$/, 'server must expose only its owned loopback TCP port');
    const clients = installPostgresClients(output, control, port);
    process.env.PATH = clients + path.delimiter + (originalPath ?? "/usr/bin:/bin");
    let ready = false; for (let attempt = 0; attempt < 60; attempt++) { const check = spawnSync("pg_isready", ["-h", "127.0.0.1", "-p", String(port), "-U", "postgres", "-d", "domainspec"]); if (check.status === 0) { ready = true; break; } Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 250); } assert.equal(ready, true, "PostgreSQL did not become ready");
    const config = { host: "127.0.0.1", port, database: "domainspec", user: "postgres", password: "domainspec-test", maxAttempts: 2 }; const store = new PostgresTransactionalOutbox(config); assert.equal(store.publish_max_attempts, 2); assert.equal(store.deduplication_owner_ref, POSTGRES_OUTBOX_DEDUPLICATION_OWNER);
    const tcp = spawnSync("psql", ["-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-h", config.host, "-p", String(port), "-U", config.user, "-d", config.database], {input: "select current_database(), inet_client_addr() is not null;", encoding: "utf8", env: {...process.env, PGPASSWORD: config.password}});
    assert.equal(tcp.status, 0, tcp.stderr);
    assert.equal(tcp.stdout.trim(), "domainspec|t", 'real client must connect through TCP, not a Unix socket or fake SQL result');
    const first = runDurableOperation(fixture.root, invocation("settlement-pg-1", "event-pg-1"), store); assert.equal(first.commit_status, "committed"); assert.equal(validateRuntimeReceiptBinding(fixture.root, first), first); assert.equal(store.records("pending").length, 1);
    assert.equal(runDurableOperation(fixture.root, invocation("settlement-pg-1", "event-pg-1"), store).commit_status, "already-committed"); assert.equal(store.records().length, 1);
    const mismatchedAttempts = invocation("settlement-pg-policy-mismatch", "event-pg-policy-mismatch"); mismatchedAttempts.transaction.max_attempts = 3; assert.throws(() => runDurableOperation(fixture.root, mismatchedAttempts, store), /OUTBOX_MAX_ATTEMPTS_MISMATCH/);
    assert.throws(() => runDurableOperation(fixture.root, invocation("settlement-pg-fail", "event-pg-fail"), store, "after-state-write"), /OUTBOX_FAILPOINT_AFTER_STATE_WRITE/); assert.equal(store.state("Settlement", "settlement-pg-fail"), null);
    const claimed = store.claim("worker-a", "2026-09-03T12:00:00.000Z", 1000); assert.equal(claimed.length, 1); assert.equal(store.claim("worker-b", "2026-09-03T12:00:00.500Z", 1000).length, 0); assert.throws(() => store.markPublished("event-pg-1", "worker-b", "2026-09-03T12:00:00.500Z"), /LEASE_NOT_OWNED/);
    let publishedRequest: { url: string; headers: Readonly<Record<string, string>>; body: string } | null = null; const http = new HttpPostgresOutboxTransport("https://events.example.test/outbox", { async send(input) { publishedRequest = input; return { status: 202 }; } }); await http.publish(claimed[0]!); assert.equal(publishedRequest!.headers["idempotency-key"], "event-pg-1"); assert.equal(JSON.parse(publishedRequest!.body).eventType, "settlement-requested");
    store.markFailed("event-pg-1", "worker-a", "broker-down", "2026-09-03T12:00:01.000Z"); const clock = "2026-09-03T12:00:01.000Z"; const worker = new PostgresOutboxWorker(store, { async publish() { throw new Error("poison"); } }, { workerId: "worker-b", clock: () => clock, retryBaseMs: 1000 }); assert.deepEqual(await worker.dispatch(), { published: 0, failed: 1, dead: 1 }); assert.equal(store.records("dead")[0]!.quarantineReason, "poison"); assert.equal(store.attempts("event-pg-1").length, 2); store.requeueDead("event-pg-1", "2026-09-03T12:00:03.000Z"); assert.equal(store.records("pending").length, 1);
    assert.equal(store.consumeOnce("event-pg-1", "settlement-requested", "2026-09-03T12:00:02.000Z", "settlement-effect-1"), "processed"); assert.equal(store.consumeOnce("event-pg-1", "settlement-requested", "2026-09-03T12:00:03.000Z", "settlement-effect-1"), "duplicate"); assert.equal(store.consumerEffects(), 1);
    const requestPath = path.join(output, "request.json"), receiptPath = path.join(output, "receipt.json"); fs.writeFileSync(requestPath, `${JSON.stringify(invocation("settlement-pg-cli", "event-pg-cli"), null, 2)}\n`);
    const cli = spawnSync(node, ["--import", "tsx", path.resolve("src/cli/main.ts"), "run", fixture.root, "--request", requestPath, "--receipt", receiptPath, "--provider", "postgres-transactional-outbox-v1"], { cwd: path.resolve("."), encoding: "utf8", env: { ...process.env, PGHOST: config.host, PGPORT: String(port), PGDATABASE: config.database, PGUSER: config.user, PGPASSWORD: config.password, OUTBOX_MAX_ATTEMPTS: "2" } }); assert.equal(cli.status, 0, `${cli.stdout}\n${cli.stderr}`); const receipt = JSON.parse(fs.readFileSync(receiptPath, "utf8")); assert.equal(receipt.provider, "postgres-transactional-outbox-v1"); assert.equal(receipt.commit_status, "committed"); assert.equal(store.records().length, 2);
    const schema = spawnSync("python3", ["-c", "import json,sys;from jsonschema import Draft202012Validator;Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(open(sys.argv[2])));Draft202012Validator(json.load(open(sys.argv[3]))).validate(json.load(open(sys.argv[4])))", path.resolve("contracts/durable-operation-invocation.schema.json"), requestPath, path.resolve("contracts/durable-operation-receipt.schema.json"), receiptPath], { encoding: "utf8" }); assert.equal(schema.status, 0, schema.stderr);
  } finally {
    if (originalPath === undefined) delete process.env.PATH; else process.env.PATH = originalPath;
    try {
      if (control !== null) control.cleanupAll();
    } finally {
      if (fixtureParent !== null) fs.rmSync(fixtureParent, { recursive: true, force: true });
    }
    if (output !== null) fs.rmSync(output, { recursive: true, force: true });
  }
});
