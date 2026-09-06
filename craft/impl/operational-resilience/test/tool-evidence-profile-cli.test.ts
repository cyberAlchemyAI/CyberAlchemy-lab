import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import type { ToolEvidenceProfileValidationResult } from "../contracts/tool-evidence-profile.js";

type CliHostileCase = Readonly<{
  case_id: string;
  kind: "cli";
  scenario: "url-descriptor" | "directory-descriptor" | "extra-output" | "discovery-pattern";
  expected_code: string;
}>;

const thisDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(thisDir, "..");
const implRoot = resolve(packageRoot, "..");
const goldenBase = "operational-resilience/fixtures/tool-evidence-profiles/golden";
const inventory = "operational-resilience/contracts/tool-evidence-profile-family-inventory.json";
const policy = "operational-resilience/contracts/tool-evidence-profile-attribute-policy.json";
const referents = "operational-resilience/fixtures/tool-evidence-profiles/referents.json";
const at = "2026-08-26T12:37:54Z";
const families = ["telemetry", "health-failure", "workload", "fault", "canary-analysis", "deployment-observation", "rollback-observation"];

const run = (descriptor: string, extra: readonly string[] = [], evaluatedAt = at) => spawnSync(
  process.execPath,
  ["--import", "tsx", "operational-resilience/src/tool-evidence-profile-cli.ts", "validate", descriptor,
    "--inventory", inventory, "--attribute-policy", policy, "--referents", referents, "--at", evaluatedAt, ...extra],
  { cwd: implRoot, encoding: "utf8" },
);

for (const family of families) {
  test(`CLI validates exact ${family} bytes and emits only one denied result`, () => {
    const invocation = run(`${goldenBase}/${family}.json`);
    assert.equal(invocation.status, 0, invocation.stdout + invocation.stderr);
    assert.equal(invocation.stderr, "");
    const result = JSON.parse(invocation.stdout) as ToolEvidenceProfileValidationResult;
    assert.equal(result.verdict, "pass");
    assert.equal(result.family_id, family);
    assert.equal(result.runtime_admission, "denied");
    assert.equal(result.referent_trust, "unverified");
    assert.equal(result.authority_effect, "none");
    assert.equal(invocation.stdout.trim().split("\n").filter((line) => line.startsWith("{")).length, 1);
  });
}

const allCases = JSON.parse(readFileSync(resolve(packageRoot, "fixtures/tool-evidence-profiles/hostile/cases.json"), "utf8")) as { cases: CliHostileCase[] };
const cliCases = allCases.cases.filter(({ kind }) => kind === "cli");

for (const hostileCase of cliCases) {
  test(`${hostileCase.case_id} rejects path discovery or output expansion`, () => {
    let invocation;
    switch (hostileCase.scenario) {
      case "url-descriptor":
        invocation = run("https://example.invalid/profile.json");
        break;
      case "directory-descriptor":
        invocation = run(goldenBase);
        break;
      case "extra-output":
        invocation = run(`${goldenBase}/telemetry.json`, ["--output", "/tmp/forbidden.json"]);
        break;
      case "discovery-pattern":
        invocation = run(`${goldenBase}/*.json`);
        break;
    }
    assert.equal(invocation.status, 2, invocation.stdout + invocation.stderr);
    assert.equal(invocation.stdout, "");
    assert.match(invocation.stderr, new RegExp(hostileCase.expected_code));
  });
}

test("CLI preserves validator rejection status and never upgrades expiry", () => {
  const invocation = run(`${goldenBase}/telemetry.json`, [], "2026-08-27T00:00:00Z");
  assert.equal(invocation.status, 1, invocation.stdout + invocation.stderr);
  assert.equal(invocation.stderr, "");
  const result = JSON.parse(invocation.stdout) as ToolEvidenceProfileValidationResult;
  assert.equal(result.verdict, "reject");
  assert.ok(result.findings.some(({ code }) => code === "PROFILE_BINDING_EXPIRED"));
  assert.equal(result.runtime_admission, "denied");
});
