import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { testTsx } from "./toolchain.js";

const root = path.resolve(import.meta.dirname, "..");
const tsx = testTsx();
const cli = path.join(root, "src/cli.ts");
const source = path.join(root, "examples/outbox-operation.md");
const effectRequest = path.join(root, "examples/outbox-request.json");
const facts = JSON.stringify({ operationId: "operation-1", orderId: "order-1", status: "pending", outboxMessageId: "message-1", occurredAt: "2026-09-03T12:00:00.000Z", payload: { kind: "order-committed" } });

function invoke(args: string[]) {
  return spawnSync(tsx, [cli, ...args], { cwd: root, encoding: "utf8", env: { ...process.env, PATH: `/home/vrondelli/.nvm/versions/node/v26.8.1/bin:${process.env.PATH ?? ""}` } });
}

test("CLI runs the declared SQLite effect, inspects pending and dispatches to stdout", () => {
  const database = path.join(mkdtempSync(path.join(tmpdir(), "domainspec-cli-outbox-")), "outbox.sqlite");
  const common = [source, "CommitOrderWithOutbox", "--actor", "OrderService", "--facts", facts, "--grant", "order-transaction-authority"];
  const run = invoke(["run", ...common, "--binding", "sqlite-transactional-outbox", "--database", database, "--effect-request-file", effectRequest]);
  assert.equal(run.status, 0, `${run.stdout}\n${run.stderr}`);
  const result = JSON.parse(run.stdout);
  assert.equal(result.outcome, "committed-with-outbox");
  assert.deepEqual(result.outbox, { pending: 1, leased: 0, published: 0, dead: 0 });

  const pending = invoke(["outbox", "pending", "--database", database]);
  assert.equal(pending.status, 0, pending.stderr);
  const inspected = JSON.parse(pending.stdout);
  assert.equal(inspected.messages[0].messageId, "message-1");

  const dispatch = invoke(["outbox", "dispatch", "--database", database, "--transport", "stdout", "--worker-id", "cli-test", "--now", "2026-09-03T12:00:00.000Z"]);
  assert.equal(dispatch.status, 0, dispatch.stderr);
  const dispatched = JSON.parse(dispatch.stdout);
  assert.deepEqual(dispatched.result, { published: 1, failed: 0, dead: 0 });
  assert.equal(dispatched.messages[0].messageId, "message-1");
  assert.deepEqual(dispatched.stats, { pending: 0, leased: 0, published: 1, dead: 0 });
});

test("effectful actions never fall back to memory and mismatched bindings fail closed", () => {
  const withoutBinding = invoke(["run", source, "CommitOrderWithOutbox", "--actor", "OrderService", "--facts", facts, "--grant", "order-transaction-authority", "--adapter", "memory"]);
  assert.notEqual(withoutBinding.status, 0);
  assert.match(withoutBinding.stderr, /EFFECT_BINDING_REQUIRED/);
  const mismatch = invoke(["run", source, "CommitOrderWithOutbox", "--actor", "OrderService", "--facts", facts, "--grant", "order-transaction-authority", "--binding", "postgres-outbox", "--database", path.join(mkdtempSync(path.join(tmpdir(), "domainspec-cli-outbox-")), "outbox.sqlite"), "--effect-request-file", effectRequest]);
  assert.notEqual(mismatch.status, 0);
  assert.match(mismatch.stderr, /EFFECT_BINDING_NOT_DECLARED/);
});
