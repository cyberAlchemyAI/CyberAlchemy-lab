import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  auditReferences,
  collectReferenceMatches,
  type ExceptionEntry,
} from "../audit-retired-orchestration-references";

const thisDir = dirname(fileURLToPath(import.meta.url));
const implRoot = resolve(thisDir, "../..");
const projectRoot = resolve(implRoot, "..");
const repoRoot = resolve(projectRoot, "../..");
const cli = "tools/audit-retired-orchestration-references.ts";

function runCli(args: string[] = []) {
  return spawnSync(process.execPath, ["--import", "tsx", cli, ...args], {
    cwd: implRoot,
    encoding: "utf8",
  });
}

test("clean repository passes the classified reference guard", () => {
  const run = runCli();
  assert.equal(run.status, 0, run.stdout + run.stderr);
  assert.match(run.stdout, /Result: \*\*PASS\*\*/);
  assert.match(run.stdout, /Violations: 0/);
});

test("temporary active Saga match fails and is removed by the harness", () => {
  const fixtureDir = resolve(implRoot, "spec/__fixtures__/audit-retired-orchestration-active");
  const fixture = resolve(fixtureDir, "SPEC.md");
  mkdirSync(fixtureDir, { recursive: true });
  writeFileSync(fixture, "# Seed\n\nSaga is an active type here.\n", "utf8");
  try {
    const run = runCli();
    assert.equal(run.status, 1, run.stdout + run.stderr);
    assert.match(run.stdout, /unclassified/);
    assert.match(run.stdout, /audit-retired-orchestration-active\/SPEC\.md/);
  } finally {
    rmSync(fixtureDir, { recursive: true, force: true });
  }
});

test("changed reviewed reference fails its content digest", () => {
  const temp = mkdtempSync(resolve(tmpdir(), "domainspec-reference-audit-"));
  try {
    const project = resolve(temp, "projects/domainspec-v2");
    const reviewed = resolve(project, "development/current-plan.md");
    const manifest = resolve(temp, "manifest.json");
    const allowlist = resolve(temp, "allowlist.json");
    mkdirSync(dirname(reviewed), { recursive: true });
    writeFileSync(reviewed, "Saga hardening is cancelled.\n", "utf8");
    writeFileSync(
      manifest,
      JSON.stringify({ schema_version: "1", swu_id: "test", entries: [] }),
      "utf8",
    );
    const match = collectReferenceMatches(temp, project)[0];
    assert.ok(match);
    const exception: ExceptionEntry = {
      path: match.path,
      disposition: "reviewed-current-plan-reference",
      reason: "Reviewed cancellation evidence.",
      expected_match_count: match.matchCount,
      match_digest: match.matchDigest,
    };
    writeFileSync(
      allowlist,
      JSON.stringify({ schema_version: "1", guard_id: "test", manifest: "manifest.json", exceptions: [exception] }),
      "utf8",
    );
    writeFileSync(reviewed, "Saga hardening is active again.\n", "utf8");
    const report = auditReferences({
      repoRoot: temp,
      projectRoot: project,
      manifestPath: manifest,
      allowlistPath: allowlist,
      guardOwnedPaths: new Set(),
    });
    assert.equal(report.summary.result, "fail");
    assert.equal(report.violations[0]?.code, "exception-digest-drift");
  } finally {
    rmSync(temp, { recursive: true, force: true });
  }
});

test("missing exception paths fail closed", () => {
  const temp = mkdtempSync(resolve(tmpdir(), "domainspec-reference-missing-"));
  try {
    const project = resolve(temp, "projects/domainspec-v2");
    const manifest = resolve(temp, "manifest.json");
    const allowlist = resolve(temp, "allowlist.json");
    mkdirSync(project, { recursive: true });
    writeFileSync(
      manifest,
      JSON.stringify({ schema_version: "1", swu_id: "test", entries: [] }),
      "utf8",
    );
    writeFileSync(
      allowlist,
      JSON.stringify({
        schema_version: "1",
        guard_id: "test",
        manifest: "manifest.json",
        exceptions: [{
          path: "projects/domainspec-v2/research/missing.md",
          disposition: "post-manifest-historical-reference",
          reason: "Reviewed historical evidence.",
          expected_match_count: 1,
          match_digest: "missing",
        }],
      }),
      "utf8",
    );
    const report = auditReferences({
      repoRoot: temp,
      projectRoot: project,
      manifestPath: manifest,
      allowlistPath: allowlist,
      guardOwnedPaths: new Set(),
    });
    assert.equal(report.summary.result, "fail");
    assert.equal(report.violations[0]?.code, "missing-exception-path");
  } finally {
    rmSync(temp, { recursive: true, force: true });
  }
});

test("unused exceptions fail closed", () => {
  const temp = mkdtempSync(resolve(tmpdir(), "domainspec-reference-unused-"));
  try {
    const project = resolve(temp, "projects/domainspec-v2");
    const reviewed = resolve(project, "research/reviewed.md");
    const manifest = resolve(temp, "manifest.json");
    const allowlist = resolve(temp, "allowlist.json");
    mkdirSync(dirname(reviewed), { recursive: true });
    writeFileSync(reviewed, "No retired orchestration reference remains.\n", "utf8");
    writeFileSync(
      manifest,
      JSON.stringify({ schema_version: "1", swu_id: "test", entries: [] }),
      "utf8",
    );
    writeFileSync(
      allowlist,
      JSON.stringify({
        schema_version: "1",
        guard_id: "test",
        manifest: "manifest.json",
        exceptions: [{
          path: "projects/domainspec-v2/research/reviewed.md",
          disposition: "post-manifest-historical-reference",
          reason: "Reviewed historical evidence.",
          expected_match_count: 1,
          match_digest: "unused",
        }],
      }),
      "utf8",
    );
    const report = auditReferences({
      repoRoot: temp,
      projectRoot: project,
      manifestPath: manifest,
      allowlistPath: allowlist,
      guardOwnedPaths: new Set(),
    });
    assert.equal(report.summary.result, "fail");
    assert.equal(report.violations[0]?.code, "unused-exception");
  } finally {
    rmSync(temp, { recursive: true, force: true });
  }
});

test("machine report is valid JSON", () => {
  const temp = mkdtempSync(resolve(tmpdir(), "domainspec-reference-report-"));
  try {
    const output = resolve(temp, "report.json");
    const run = runCli(["--json-output", output]);
    assert.equal(run.status, 0, run.stdout + run.stderr);
    const report = JSON.parse(readFileSync(output, "utf8")) as { summary?: { result?: string } };
    assert.equal(report.summary?.result, "pass");
  } finally {
    rmSync(temp, { recursive: true, force: true });
  }
});
