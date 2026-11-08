import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../../");
const validator = "tools/validate-relationships.ts";

function runValidator(args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", validator, ...args], {
    cwd: implRoot,
    encoding: "utf-8",
  });
}

function runFixture(name: string) {
  return runValidator(["--features-root", `spec/__fixtures__/relationships/${name}`]);
}

test("valid relationship endpoints pass, including Query and Operation reads", () => {
  const r = runFixture("valid");
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /PASS/);
  assert.match(r.stdout, /canonicalSignatures=31/);
});

test("same-feature creates passes as the sole authored creation fact", () => {
  const r = runFixture("valid-creates");
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /PASS/);
});

test("cross-feature produces-for passes only in the cross-feature section", () => {
  const r = runFixture("valid-cross-feature-produces-for");
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /PASS/);
});

test("cross-feature enforces uses the canonical base verb", () => {
  const r = runFixture("valid-cross-feature-enforces");
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /PASS/);
});

for (const [fixture, detail] of [
  ["bad-same-feature-produces-for", /Feature scope mismatch/],
  ["bad-creates-authored-projection", /Generated projection creation_targets must not be authored/],
  ["bad-creates-multiple-targets", /source CreatePlayer has 2 outgoing edges/],
  ["bad-creates-multiple-sources", /target Player has 2 incoming edges/],
] as const) {
  test(`${fixture} rejects the scope, authorship, or responsibility-cardinality violation`, () => {
    const r = runFixture(fixture);
    assert.equal(r.status, 1, r.stdout + r.stderr);
    assert.match(r.stdout, detail);
  });
}

for (const fixture of [
  "bad-operation-enforces-value-object",
  "bad-state-machine-enforces-operation",
  "bad-reversed-enforces",
  "bad-calculation-reads",
  "bad-reads-target",
  "bad-operation-emits-event",
  "bad-saga-orchestrates-operation",
]) {
  test(`${fixture} is rejected as unconstructible`, () => {
    const r = runFixture(fixture);
    assert.equal(r.status, 1, r.stdout + r.stderr);
    assert.match(r.stdout, /unconstructible-edge/);
  });
}

test("deprecated queries is rejected with the canonical reads replacement", () => {
  const r = runFixture("bad-queries-target");
  assert.equal(r.status, 1, r.stdout + r.stderr);
  assert.match(r.stdout, /Deprecated relationship label "queries" is not canonical/);
  assert.match(r.stdout, /suggested=reads/);
});

test("generated owned-by inverse is not an authored canonical edge", () => {
  const r = runFixture("bad-generated-owned-by");
  assert.equal(r.status, 1, r.stdout + r.stderr);
  assert.match(r.stdout, /noncanonical-edge/);
  assert.match(r.stdout, /Generated inverse/);
});
