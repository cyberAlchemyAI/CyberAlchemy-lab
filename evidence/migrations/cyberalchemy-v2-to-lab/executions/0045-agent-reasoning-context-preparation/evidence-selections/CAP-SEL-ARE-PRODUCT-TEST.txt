import {readdirSync} from "node:fs";
import {resolve} from "node:path";
import {spawnSync} from "node:child_process";

import {inspectProduct, productRoot} from "../src/product.mjs";

const health = inspectProduct({require_exact_runtime: true});
if (health.status !== "PASS") {
  process.stderr.write(`${JSON.stringify(health, null, 2)}\n`);
  process.exit(1);
}

const targets = [productRoot, ...health.components.map((component) => component.path), ...health.integrations.map((integration) => integration.path)];
const results = [];
for (const target of targets) {
  const testDirectory = resolve(target, "test");
  let tests = [];
  try { tests = readdirSync(testDirectory).filter((name) => name.endsWith(".test.mjs")).sort().map((name) => resolve(testDirectory, name)); } catch {}
  if (tests.length === 0) continue;
  const started = performance.now();
  const run = spawnSync(process.execPath, ["--test", "--test-reporter=tap", ...tests], {cwd: target, encoding: "utf8", timeout: 600_000});
  const testCases = Number(run.stdout?.match(/^# tests (\d+)$/m)?.[1] ?? 0);
  results.push({target, test_files: tests.length, test_cases: testCases, status: run.status === 0 ? "PASS" : "FAIL", elapsed_ms: performance.now() - started});
  if (run.status !== 0) {
    process.stderr.write(run.stdout ?? "");
    process.stderr.write(run.stderr ?? "");
    process.stdout.write(`${JSON.stringify({schema_version: "are.product-test-result/v1", status: "FAIL", results, authority_effect: "none"}, null, 2)}\n`);
    process.exit(1);
  }
}
process.stdout.write(`${JSON.stringify({schema_version: "are.product-test-result/v1", status: "PASS", product_id: health.product_id, product_version: health.product_version, total_test_cases: results.reduce((sum, result) => sum + result.test_cases, 0), results, authority_effect: "none"}, null, 2)}\n`);
