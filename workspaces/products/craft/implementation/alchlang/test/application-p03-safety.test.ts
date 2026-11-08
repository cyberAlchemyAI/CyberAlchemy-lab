import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";
import { selectedPredecessorCheck, validateCandidate } from "../scripts/p03-exact-candidate.js";

const repo = path.resolve(defaultDomainSpecPackageRoot(), "../../../../..");
const implementation = path.join(repo, "language/capabilities/alchlang/plans/general-compiler-v1/implementation");
const evidence = path.join(repo, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p03-exact-candidate");
const candidatePath = path.join(evidence, "candidate.json");
const qualificationPath = path.join(evidence, "qualification.json");
const digest = (file: string) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const hash = (value: string) => crypto.createHash("sha256").update(value).digest("hex");
const canonical = (value: any): string => Array.isArray(value) ? `[${value.map(canonical).join(",")}]`
  : value !== null && typeof value === "object" ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`
  : JSON.stringify(value) ?? "null";

function reseal(value: Record<string, any>) {
  delete value.candidate_id;
  delete value.manifest_sha256;
  value.candidate_id = `alchlang-domainspec-p03-${hash(canonical(value)).slice(0, 16)}`;
  value.manifest_sha256 = hash(canonical(value));
}

test("historical P03 does not bind the selected P01 and P02 successors", () => {
  const historical = JSON.parse(fs.readFileSync(candidatePath, "utf8"));
  const result = selectedPredecessorCheck(historical);
  assert.equal(result.result, "fail");
  assert.ok(result.missing_or_stale_receipts.some((item: string) => item.endsWith("qualification.v3-candidate.json")));
  assert.ok(result.missing_or_stale_receipts.some((item: string) => item.includes("successor-v5-candidate/qualification.json")));
  assert.ok(result.mismatched_archives.length > 0);
});

test("P03 rejects an independently resealed environment substitution", () => {
  const changed = JSON.parse(fs.readFileSync(candidatePath, "utf8"));
  changed.environment.platform = "substituted-platform";
  reseal(changed);
  const checks = new Map(validateCandidate(changed, true).checks.map(item => [item.id, item.result]));
  assert.equal(checks.get("candidate-id"), "pass");
  assert.equal(checks.get("manifest-self-digest"), "pass");
  assert.equal(checks.get("environment-current"), "fail");
});

test("P03 legacy write is disabled and cannot replace historical evidence", () => {
  const before = [digest(candidatePath), digest(qualificationPath)];
  const result = spawnSync(process.execPath, ["scripts/run-toolchain.mjs", "tsx", "scripts/p03-exact-candidate.ts", "--write"], {
    cwd: implementation, encoding: "utf8", env: { ...process.env, TMPDIR: "/var/tmp" },
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /P03_HISTORICAL_WRITE_DISABLED/);
  assert.deepEqual([digest(candidatePath), digest(qualificationPath)], before);
});
