import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { renderSqliteTransactionalOutbox } from "../src/index.js";
import { testTsx } from "./toolchain.js";

const effect = {
  id: "PersistOrderWithOutbox",
  pattern_ref: "transactional-outbox",
  integration_binding_ref: "sqlite-transactional-outbox",
  write_refs: ["Order", "OutboxMessage"],
  event_refs: ["order-committed"],
  guarantee: "atomic-state-and-outbox",
  failure_continuation: "rollback",
  authority_boundary_ref: "order-write"
};

test("SQLite Outbox generator emits concrete implementation and executable conformance tests", () => {
  const files = renderSqliteTransactionalOutbox(effect);
  assert.deepEqual(Object.keys(files).sort(), ["domain.generation-manifest.json", "domain.outbox.migration.sql", "domain.outbox.port.ts", "domain.outbox.provider.ts", "domain.outbox.sqlite.ts", "domain.outbox.test.ts", "domain.outbox.worker.ts"]);
  assert.match(files["domain.outbox.sqlite.ts"], /BEGIN IMMEDIATE/);
  assert.match(files["domain.outbox.sqlite.ts"], /ROLLBACK/);
  assert.match(files["domain.outbox.worker.ts"], /markFailed/);
  assert.match(files["domain.outbox.provider.ts"], /DurableOutboxWorker/);
  const directory = mkdtempSync(path.join(tmpdir(), "domainspec-generated-outbox-"));
  for (const [name, bytes] of Object.entries(files)) writeFileSync(path.join(directory, name), bytes);
  const tsx = testTsx();
  const run = spawnSync(tsx, ["--test", path.join(directory, "domain.outbox.test.ts")], { encoding: "utf8", env: { ...process.env, PATH: `/home/vrondelli/.nvm/versions/node/v26.8.1/bin:${process.env.PATH ?? ""}` } });
  assert.equal(run.status, 0, `${run.stdout}\n${run.stderr}`);
});

test("generator refuses inferred or mismatched bindings", () => {
  assert.throws(() => renderSqliteTransactionalOutbox({ ...effect, integration_binding_ref: "implicit" }), /OUTBOX_GENERATOR_BINDING_MISMATCH/);
});
