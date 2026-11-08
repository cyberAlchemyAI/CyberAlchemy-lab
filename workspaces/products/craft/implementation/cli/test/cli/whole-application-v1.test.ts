import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { runCli } from "../../src/cli/main.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const example = path.resolve(here, "../../examples/reconciled-commerce");
const sourceRoot = path.join(example, "source");
const integrationSource = path.join(example, "integrations/application.json");
const selection = (language: string): string => path.join(example, `selections/${language}.json`);

function invoke(args: readonly string[]): { code: number; stdout: string; stderr: string } {
  let stdout = ""; let stderr = "";
  const code = runCli(args, { stdout: value => { stdout += value; }, stderr: value => { stderr += value; } });
  return { code, stdout, stderr };
}

test("L1 CLI publishes and verifies a whole application from one explicit integration source", t => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-whole-cli-"));
  t.after(() => fs.rmSync(parent, { recursive: true, force: true }));
  const target = path.join(parent, "python-application");
  const published = invoke(["instantiate-project", sourceRoot, "--languages", "python", "--target-root", target, "--compilation-selection", selection("python"), "--integration-source", integrationSource]);
  assert.equal(published.code, 0, published.stderr);
  assert.equal(published.stderr, "");
  const result = JSON.parse(published.stdout);
  assert.equal(result.schema_version, "domainspec.whole-application-command-result/v1-candidate");
  assert.equal(result.language, "python");
  assert.equal(result.artifact_count, 108);
  const verified = invoke(["verify", sourceRoot, "--language", "python", "--target-root", target, "--compilation-selection", selection("python"), "--integration-source", integrationSource]);
  assert.equal(verified.code, 0, verified.stderr);
  assert.equal(JSON.parse(verified.stdout).result, "pass");
});

test("L1 CLI rejects partial, duplicate, node-level, and layout-conflicting integration options before source reads", () => {
  const missing = path.join(os.tmpdir(), "domainspec-does-not-exist.json");
  const cases: readonly string[][] = [
    ["build", sourceRoot, "--language", "typescript", "--target-root", "/tmp/unused", "--integration-source", missing],
    ["instantiate", sourceRoot, "--node", "commerce:order", "--language", "typescript", "--target-root", "/tmp/unused", "--compilation-selection", missing, "--integration-source", missing],
    ["build", sourceRoot, "--language", "typescript", "--target-root", "/tmp/unused", "--compilation-selection", missing, "--integration-source", missing, "--integration-source", missing],
    ["build", sourceRoot, "--language", "typescript", "--target-root", "/tmp/unused", "--output-layout", "domainspec.application-layout/v1", "--compilation-selection", selection("typescript"), "--integration-source", integrationSource],
  ];
  for (const args of cases) {
    const result = invoke(args);
    assert.equal(result.code, 22, args.join(" "));
    assert.equal(JSON.parse(result.stderr).code, "MTCLI_USAGE", result.stderr);
    assert.equal(result.stdout, "");
  }
});

test("L1 no-option reconciled command retains the established result envelope", t => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-reconciled-compat-"));
  t.after(() => fs.rmSync(parent, { recursive: true, force: true }));
  const target = path.join(parent, "typescript-project");
  const result = invoke(["instantiate-project", sourceRoot, "--languages", "typescript", "--target-root", target, "--compilation-selection", selection("typescript")]);
  assert.equal(result.code, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).schema_version, "domainspec.reconciled-command-result/v1-candidate");
  assert.equal(fs.existsSync(path.join(target, ".domainspec/whole-application.json")), false);
});
