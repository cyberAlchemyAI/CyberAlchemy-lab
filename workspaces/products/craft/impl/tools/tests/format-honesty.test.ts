import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  evaluate,
  loadBaseline,
  parseBaseline,
  scan,
  type Baseline,
  type Report,
  type Violation,
} from "../validate-format-honesty";

const HERE = dirname(fileURLToPath(import.meta.url));
const FIXTURES = resolve(HERE, "../../../development/format-honesty/fixtures/format-honesty");
const V2_ROOT = resolve(HERE, "../../..");
const BASELINE_PATH = resolve(HERE, "../format-honesty-baseline.json");

function reportWith(violations: Violation[]): Report {
  return {
    root: "/fixture",
    scanned: violations.length,
    violations,
    excludedSegments: [],
    ignoreMarker: ".format-honesty-ignore",
  };
}

function violation(path: string, kind: Violation["kind"]): Violation {
  return { path, kind, detail: "test finding" };
}

function baseline(findings: Baseline["findings"]): Baseline {
  return parseBaseline({
    schemaVersion: "domainspec.format-honesty-baseline.v1",
    comparison: "exact-finding-set",
    pathBase: "scan-root-relative-posix",
    expectedCount: findings.length,
    findings,
  });
}

test("passes on a tree whose names are honest", () => {
  const report = scan(resolve(FIXTURES, "honest"));
  assert.deepEqual(report.violations, []);
  assert.equal(report.scanned, 2);
  assert.equal(evaluate(report).exitCode, 0);
});

test("rejects a .yml whose content is JSON", () => {
  const report = scan(resolve(FIXTURES, "violating"));
  assert.equal(report.violations.find((x) => x.path === "misnamed.yml")?.kind, "json-content-yaml-name");
});

test("rejects a .json that does not parse as JSON", () => {
  const report = scan(resolve(FIXTURES, "violating"));
  assert.equal(report.violations.find((x) => x.path === "broken.json")?.kind, "broken-json");
});

test("does not inspect YAML validity — a real .yml is left alone", () => {
  const report = scan(resolve(FIXTURES, "honest"));
  assert.ok(!report.violations.map((finding) => finding.path).includes("settings.yml"));
});

test("declares its exclusions rather than hiding them", () => {
  const report = scan(resolve(FIXTURES, "honest"));
  assert.ok(report.excludedSegments.includes("node_modules"));
  assert.ok(report.excludedSegments.includes("refinement-runs"));
  assert.equal(report.ignoreMarker, ".format-honesty-ignore");
});

test("skips a subtree carrying the ignore marker", () => {
  const report = scan(FIXTURES);
  assert.deepEqual(report.violations, []);
});

test("strict no-baseline mode still rejects every finding", () => {
  const report = reportWith([violation("misnamed.yml", "json-content-yaml-name")]);
  const result = evaluate(report);
  assert.equal(result.mode, "strict");
  assert.equal(result.exactMatch, false);
  assert.equal(result.exitCode, 4);
  assert.deepEqual(result.added, report.violations);
});

test("the governed surface exactly matches all 49 acknowledged baseline findings", () => {
  const expected = loadBaseline(BASELINE_PATH);
  const report = scan(V2_ROOT);
  const result = evaluate(report, expected);
  assert.equal(expected.expectedCount, 49);
  assert.equal(result.acknowledged.length, 49);
  assert.deepEqual(result.added, []);
  assert.deepEqual(result.removed, []);
  assert.deepEqual(result.reclassified, []);
  assert.equal(result.exactMatch, true);
  assert.equal(result.exitCode, 0);
});

test("baseline mode fails on an added finding", () => {
  const expected = baseline([{ path: "known.yml", kind: "json-content-yaml-name" }]);
  const result = evaluate(reportWith([
    violation("known.yml", "json-content-yaml-name"),
    violation("new.json", "broken-json"),
  ]), expected);
  assert.equal(result.exitCode, 4);
  assert.deepEqual(result.added.map((finding) => finding.path), ["new.json"]);
});

test("baseline mode fails when a known finding is removed or resolved", () => {
  const expected = baseline([
    { path: "first.yml", kind: "json-content-yaml-name" },
    { path: "second.yml", kind: "json-content-yaml-name" },
  ]);
  const result = evaluate(reportWith([
    violation("first.yml", "json-content-yaml-name"),
  ]), expected);
  assert.equal(result.exitCode, 4);
  assert.deepEqual(result.removed, [{ path: "second.yml", kind: "json-content-yaml-name" }]);
});

test("baseline mode fails when a known path is reclassified", () => {
  const expected = baseline([{ path: "finding.json", kind: "broken-json" }]);
  const result = evaluate(reportWith([
    violation("finding.json", "json-content-yaml-name"),
  ]), expected);
  assert.equal(result.exitCode, 4);
  assert.deepEqual(result.reclassified, [{
    path: "finding.json",
    baselineKind: "broken-json",
    actualKind: "json-content-yaml-name",
  }]);
});

test("malformed and duplicate baselines fail closed", () => {
  const root = mkdtempSync(join(tmpdir(), "format-honesty-baseline-"));
  try {
    const malformedPath = join(root, "malformed.json");
    writeFileSync(malformedPath, "{", "utf8");
    assert.throws(() => loadBaseline(malformedPath), /cannot parse baseline/);

    const duplicatePath = join(root, "duplicate.json");
    writeFileSync(duplicatePath, JSON.stringify({
      schemaVersion: "domainspec.format-honesty-baseline.v1",
      comparison: "exact-finding-set",
      pathBase: "scan-root-relative-posix",
      expectedCount: 2,
      findings: [
        { path: "same.yml", kind: "json-content-yaml-name" },
        { path: "same.yml", kind: "json-content-yaml-name" },
      ],
    }), "utf8");
    assert.throws(() => loadBaseline(duplicatePath), /duplicate baseline path/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
