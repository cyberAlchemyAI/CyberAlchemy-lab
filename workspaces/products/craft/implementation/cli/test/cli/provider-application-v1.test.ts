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
const providers = (language: string): string => path.join(example, `providers/${language}.json`);

function invoke(args: readonly string[]): { code: number; stdout: string; stderr: string } {
  let stdout = ""; let stderr = "";
  const code = runCli(args, { stdout: value => { stdout += value; }, stderr: value => { stderr += value; } });
  return { code, stdout, stderr };
}

test("L2 CLI publishes and verifies an explicitly selected provider application", t => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-cli-"));
  t.after(() => fs.rmSync(parent, { recursive: true, force: true }));
  const target = path.join(parent, "typescript-application");
  const options = ["--compilation-selection", selection("typescript"), "--integration-source", integrationSource, "--provider-selection", providers("typescript")];
  const published = invoke(["instantiate-project", sourceRoot, "--languages", "typescript", "--target-root", target, ...options]);
  assert.equal(published.code, 0, published.stderr);
  assert.equal(published.stderr, "");
  const result = JSON.parse(published.stdout);
  assert.equal(result.schema_version, "domainspec.provider-application-command-result/v1-candidate");
  assert.equal(result.language, "typescript");
  assert.equal(result.runtime_guarantees_observed, false);
  assert.equal(fs.existsSync(path.join(target, "package-lock.json")), true);
  assert.equal(fs.existsSync(path.join(target, "migrations/0001_domainspec_reference.sql")), true);
  const verified = invoke(["verify", sourceRoot, "--language", "typescript", "--target-root", target, ...options]);
  assert.equal(verified.code, 0, verified.stderr);
  assert.equal(JSON.parse(verified.stdout).result, "pass");
});

test("L4 verify-runtime writes external bounded evidence without mutating the provider target", t => {
  const parent = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-provider-runtime-cli-"));
  t.after(() => fs.rmSync(parent, { recursive: true, force: true }));
  const target = path.join(parent, "typescript-application");
  const options = ["--compilation-selection", selection("typescript"), "--integration-source", integrationSource, "--provider-selection", providers("typescript")];
  const published = invoke(["build", sourceRoot, "--language", "typescript", "--target-root", target, ...options]);
  assert.equal(published.code, 0, published.stderr);

  const tools = path.join(parent, "tools");
  fs.mkdirSync(tools);
  const npm = path.join(tools, "npm");
  const node = path.join(tools, "node");
  fs.writeFileSync(npm, "#!/bin/sh\nmkdir -p node_modules/typescript/bin\n: > node_modules/typescript/bin/tsc\n");
  fs.writeFileSync(node, "#!/bin/sh\ncase \"$*\" in *typescript-webhook.mjs*) printf '%s\\n' '{\"language\":\"typescript\",\"startup\":\"http-listener\",\"invalid_status\":401,\"valid_status\":202,\"handler_invocations\":1,\"result\":\"pass\"}' ;; esac\n");
  fs.chmodSync(npm, 0o755);
  fs.chmodSync(node, 0o755);
  const receipt = path.join(parent, "runtime-evidence.json");
  const runtime = invoke(["verify-runtime", sourceRoot, "--language", "typescript", "--target-root", target, "--temporary-parent", parent, "--receipt", receipt, "--node-executable", node, "--npm-executable", npm, ...options]);
  assert.equal(runtime.code, 0, runtime.stderr);
  const result = JSON.parse(runtime.stdout);
  assert.equal(result.schema_version, "domainspec.provider-application-runtime-command-result/v1-candidate");
  assert.equal(result.receipt.native_compilation.observed, true);
  assert.equal(result.receipt.dependency_installation.cache_boundary, "task-owned-temporary");
  assert.equal(result.receipt.listener_startup.boundary, "loopback-only");
  assert.deepEqual(result.receipt.provider_dependencies, { postgresql: "not-observed", nats: "not-observed", outbound_http: "not-observed" });
  assert.equal(result.receipt.production_runtime_guarantees_observed, false);
  assert.equal(result.receipt.target_mutated, false);
  assert.equal(fs.existsSync(receipt), true);
  assert.equal(fs.readdirSync(parent).some(name => name.startsWith(".domainspec-runtime-evidence-")), false);
  const verified = invoke(["verify", sourceRoot, "--language", "typescript", "--target-root", target, ...options]);
  assert.equal(verified.code, 0, verified.stderr);

  const nestedReceipt = path.join(target, ".domainspec/runtime-evidence.json");
  const nestedReceiptResult = invoke(["verify-runtime", sourceRoot, "--language", "typescript", "--target-root", target, "--temporary-parent", parent, "--receipt", nestedReceipt, "--node-executable", node, "--npm-executable", npm, ...options]);
  assert.equal(nestedReceiptResult.code, 22);
  assert.equal(JSON.parse(nestedReceiptResult.stderr).code, "DS_PROVIDER_RUNTIME_TARGET_BOUNDARY");
  assert.equal(fs.existsSync(nestedReceipt), false);

  const nestedTemporaryResult = invoke(["verify-runtime", sourceRoot, "--language", "typescript", "--target-root", target, "--temporary-parent", target, "--receipt", path.join(parent, "nested-temporary-evidence.json"), "--node-executable", node, "--npm-executable", npm, ...options]);
  assert.equal(nestedTemporaryResult.code, 22);
  assert.equal(JSON.parse(nestedTemporaryResult.stderr).code, "DS_PROVIDER_RUNTIME_TARGET_BOUNDARY");
  assert.equal(fs.readdirSync(target).some(name => name.startsWith(".domainspec-runtime-evidence-")), false);
  const verifiedAfterBoundaryFailures = invoke(["verify", sourceRoot, "--language", "typescript", "--target-root", target, ...options]);
  assert.equal(verifiedAfterBoundaryFailures.code, 0, verifiedAfterBoundaryFailures.stderr);

  const duplicate = invoke(["verify-runtime", sourceRoot, "--language", "typescript", "--target-root", target, "--temporary-parent", parent, "--receipt", receipt, "--node-executable", node, "--npm-executable", npm, ...options]);
  assert.equal(duplicate.code, 22);
  assert.equal(JSON.parse(duplicate.stderr).code, "DS_PROVIDER_RUNTIME_RECEIPT_EXISTS");

  const failingNode = path.join(tools, "node-fail");
  fs.writeFileSync(failingNode, "#!/bin/sh\nexit 9\n");
  fs.chmodSync(failingNode, 0o755);
  const failedReceipt = path.join(parent, "failed-runtime-evidence.json");
  const failed = invoke(["verify-runtime", sourceRoot, "--language", "typescript", "--target-root", target, "--temporary-parent", parent, "--receipt", failedReceipt, "--node-executable", failingNode, "--npm-executable", npm, ...options]);
  assert.equal(failed.code, 1);
  assert.equal(JSON.parse(failed.stderr).code, "DS_PROVIDER_RUNTIME_SUBPROCESS");
  assert.equal(fs.existsSync(failedReceipt), false);
  assert.equal(fs.readdirSync(parent).some(name => name.startsWith(".domainspec-runtime-evidence-")), false);
});

test("L2 CLI rejects partial, duplicate, node-level, and language-conflicting provider selection before publication", () => {
  const missing = path.join(os.tmpdir(), "domainspec-provider-does-not-exist.json");
  const unused = path.join(os.tmpdir(), `domainspec-provider-cli-unused-${process.pid}`);
  const cases: readonly string[][] = [
    ["build", sourceRoot, "--language", "typescript", "--target-root", unused, "--compilation-selection", selection("typescript"), "--provider-selection", providers("typescript")],
    ["instantiate", sourceRoot, "--node", "commerce:order", "--language", "typescript", "--target-root", unused, "--compilation-selection", selection("typescript"), "--integration-source", integrationSource, "--provider-selection", providers("typescript")],
    ["build", sourceRoot, "--language", "typescript", "--target-root", unused, "--compilation-selection", selection("typescript"), "--integration-source", integrationSource, "--provider-selection", missing, "--provider-selection", missing],
    ["build", sourceRoot, "--language", "typescript", "--target-root", unused, "--compilation-selection", selection("typescript"), "--integration-source", integrationSource, "--provider-selection", providers("python")],
  ];
  for (const args of cases) {
    const result = invoke(args);
    assert.equal(result.code, 22, args.join(" "));
    assert.equal(result.stdout, "");
    assert.equal(JSON.parse(result.stderr).result, "fail");
  }
  assert.equal(fs.existsSync(unused), false);
});

test("L2 help states explicit provider selection and its claim boundary", () => {
  const result = invoke(["--help"]);
  assert.equal(result.code, 0);
  assert.match(result.stdout, /--provider-selection <absolute-json-file>/);
  assert.match(result.stdout, /does not establish runtime behavior/);
});
