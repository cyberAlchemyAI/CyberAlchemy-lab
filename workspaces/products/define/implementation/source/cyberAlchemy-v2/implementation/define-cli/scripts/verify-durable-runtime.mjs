#!/usr/bin/env node
import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {spawnSync} from "node:child_process";

const packageRoot = resolve(import.meta.dirname, "..");
const repositoryRoot = resolve(packageRoot, "../../..");
const bindingPath = resolve(packageRoot, "runtime-implementation-binding.json");
const binding = JSON.parse(readFileSync(bindingPath, "utf8"));

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

const checks = [];
for (const row of [...binding.byte_closure, ...binding.runtime_provider_bindings, ...binding.source_bindings]) {
  const path = resolve(repositoryRoot, row.path);
  let observed = null;
  try { observed = sha256(path); } catch {}
  checks.push({check_id: `digest:${row.path}`, outcome: observed === row.sha256 ? "PASS" : "BLOCK", expected: row.sha256, observed});
}

const testRun = spawnSync(process.execPath, ["--test", "test/define-cli.test.mjs"], {
  cwd: packageRoot,
  encoding: "utf8",
  env: {...process.env, NO_COLOR: "1"},
});
checks.push({check_id: "durable-runtime-and-regression-tests", outcome: testRun.status === 0 ? "PASS" : "BLOCK", detail: `exit ${testRun.status}`});

const blocked = checks.filter((row) => row.outcome === "BLOCK").length;
const result = {
  schema_version: "cav2.define-durable-runtime-verification/v1",
  binding_id: binding.binding_id,
  overall: blocked === 0 ? "PASS" : "BLOCK",
  checks,
  test_exit: testRun.status,
  claim_ceiling: "Exact candidate byte currentness and local product tests only; no DomainSpec conformance, runtime adoption, identity-provider selection, acceptance, publication, release, deployment, or external effect.",
  authority_effect: "none",
};
process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
process.exitCode = blocked === 0 ? 0 : 1;
