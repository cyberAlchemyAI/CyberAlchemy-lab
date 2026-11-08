#!/usr/bin/env node
import {createHash} from "node:crypto";
import {spawnSync} from "node:child_process";
import {readFileSync, readdirSync} from "node:fs";
import {resolve} from "node:path";

const packageRoot = resolve(import.meta.dirname, "..");
const repositoryRoot = resolve(packageRoot, "../../..");
const binding = JSON.parse(readFileSync(resolve(packageRoot, "language-quality-implementation-binding.json"), "utf8"));

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

const checks = binding.byte_closure.map((row) => {
  let observed = null;
  try { observed = sha256(resolve(repositoryRoot, row.path)); } catch {}
  return {check_id: `digest:${row.path}`, outcome: observed === row.sha256 ? "PASS" : "BLOCK", expected: row.sha256, observed};
});
const testRun = spawnSync(process.execPath, ["--test", "test/define-cli.test.mjs"], {
  cwd: packageRoot,
  encoding: "utf8",
  env: {...process.env, NO_COLOR: "1"},
});
checks.push({check_id: "define-language-quality-regression-tests", outcome: testRun.status === 0 ? "PASS" : "BLOCK", detail: `exit ${testRun.status}`});

function runNodeTests(root, relativeFiles) {
  const files = relativeFiles ?? readdirSync(resolve(root, "test"))
    .filter((name) => name.endsWith(".test.mjs"))
    .sort()
    .map((name) => `test/${name}`);
  return spawnSync(process.execPath, ["--test", ...files], {
    cwd: root,
    encoding: "utf8",
    env: {...process.env, NO_COLOR: "1"},
    maxBuffer: 8 * 1024 * 1024,
  });
}

const semanticExtensionRoot = resolve(repositoryRoot, "cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/semantic-contract-v1");
const routerRoot = resolve(repositoryRoot, "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/request-decision-router");
const intentRoot = resolve(repositoryRoot, "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/request-intent-runtime");
const modulePortRoot = resolve(repositoryRoot, "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/module-port");
const wrapperRoot = resolve(repositoryRoot, "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/codex-app-server-wrapper");
for (const [checkId, run] of [
  ["semantic-contract-cross-consumer-parity", runNodeTests(semanticExtensionRoot, ["consumer-parity.test.mjs"])],
  ["semantic-contract-governance-candidate", runNodeTests(semanticExtensionRoot, ["governance-candidate/validate.test.mjs"])],
  ["are-module-port-regression-tests", runNodeTests(modulePortRoot)],
  ["router-semantic-contract-regression-tests", runNodeTests(routerRoot)],
  ["are-intent-semantic-contract-regression-tests", runNodeTests(intentRoot)],
  ["are-wrapper-module-port-integration-tests", runNodeTests(wrapperRoot, [
    "test/objective-lifecycle.test.mjs", "test/objective-meanings.test.mjs", "test/objective-requirements.test.mjs",
  ])],
]) {
  checks.push({check_id: checkId, outcome: run.status === 0 ? "PASS" : "BLOCK", detail: `exit ${run.status}`});
}
const blocked = checks.filter((check) => check.outcome === "BLOCK").length;
const result = {
  schema_version: "cav2.define-language-quality-verification/v1",
  binding_id: binding.binding_id,
  overall: blocked === 0 ? "PASS" : "BLOCK",
  checks,
  test_exit: testRun.status,
  claim_ceiling: binding.claim_ceiling,
  authority_effect: "none",
};
process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
process.exitCode = blocked === 0 ? 0 : 1;
