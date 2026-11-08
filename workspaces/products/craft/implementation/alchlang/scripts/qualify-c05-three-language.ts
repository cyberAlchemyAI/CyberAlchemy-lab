import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { compileApplicationWhole } from "../src/application-whole.js";
import { digest, json } from "../src/domainspec-profile.js";
import { wholeApplicationFixtureForLanguage } from "../test/fixtures/application-whole-fixture.js";

const languages = ["typescript", "python", "rust"] as const;

function fail(message: string): never {
  throw new Error(`C05_QUALIFICATION:${message}`);
}

function executable(name: string): string {
  const found = execFileSync("/usr/bin/env", ["which", name], { encoding: "utf8" }).trim();
  if (!path.isAbsolute(found)) fail(`missing executable:${name}`);
  return path.resolve(found);
}

function materialize(root: string, files: Readonly<Record<string, string>>): void {
  for (const [relative, content] of Object.entries(files)) {
    const target = path.join(root, relative);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, content);
  }
}

function writeJson(file: string, value: unknown): void {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function runCli(compiler: Awaited<ReturnType<typeof wholeApplicationFixtureForLanguage>>["compiler"], args: readonly string[]): any {
  let stdout = "";
  let stderr = "";
  const code = compiler.runCli(args, {
    stdout(value) { stdout += value; },
    stderr(value) { stderr += value; },
  });
  if (code !== 0) fail(`CLI failed (${code}):${stderr || stdout || args.join(" ")}`);
  if (stderr !== "") fail(`CLI wrote stderr:${stderr}`);
  try { return JSON.parse(stdout); }
  catch { return fail(`CLI did not emit JSON:${stdout}`); }
}

function normalizedOutcome(result: ReturnType<typeof compileApplicationWhole>) {
  const providerArtifact = result.application.artifacts.find(row => row.relative_path === ".domainspec/providers/manifest.json");
  assert.ok(providerArtifact);
  const providerManifest = JSON.parse(providerArtifact.content);
  const graph = result.runtimeBinding.binding.application_graph;
  return {
    integration_source_sha256: result.runtimeBinding.binding.integration_source_sha256,
    nodes: graph.nodes.map((row: any) => [row.node_id, row.node_kind, row.node_origin, row.semantic_sha256]).sort(),
    edges: graph.edges.map((row: any) => [row.edge_id, row.relationship, row.relationship_authority, row.source_node_id, row.target_node_id]).sort(),
    operation_requests: graph.operation_requests.map((row: any) => [row.request_ref, row.operation_ref]).sort(),
    runtime_bindings: graph.runtime_bindings.map((row: any) => [row.binding_id, row.mapping_ref]).sort(),
    providers: Object.entries(providerManifest.providers).map(([role, provider]: [string, any]) => [role, provider.provider_id]).sort(),
    persistence: result.executable.persistence!.trace.references,
    messaging: result.executable.messaging!.trace.references,
    external_api: result.executable.externalApi!.trace.references,
  };
}

const outputRootArgument = process.argv[2];
if (!outputRootArgument || !path.isAbsolute(outputRootArgument) || path.resolve(outputRootArgument) !== outputRootArgument) {
  fail("one normalized absolute new evidence directory is required");
}
if (fs.existsSync(outputRootArgument)) fail("evidence directory already exists");
fs.mkdirSync(outputRootArgument, { recursive: false, mode: 0o700 });

const temporaryRoot = fs.mkdtempSync(path.join(os.tmpdir(), "alch-c05-qualification-"));
const outcomes: unknown[] = [];
const runs: unknown[] = [];
let sourceSha256 = "";

try {
  const tools = {
    node: process.execPath,
    npm: executable("npm"),
    python: executable("python3"),
    cargo: executable("cargo"),
  };
  for (const language of languages) {
    const fixture = await wholeApplicationFixtureForLanguage(language);
    const workspace = path.join(temporaryRoot, language);
    const sourceRoot = path.join(workspace, "source");
    const targetRoot = path.join(workspace, "application");
    fs.mkdirSync(sourceRoot, { recursive: true });
    materialize(sourceRoot, fixture.candidate.projectFiles);
    const graph = fixture.compiler.compileProject(sourceRoot).graph;
    const result = compileApplicationWhole(fixture.candidate, graph, fixture.observation, fixture.compiler);
    sourceSha256 ||= result.trace.source_sha256;
    assert.equal(result.trace.source_sha256, sourceSha256);
    const inputRoot = path.join(workspace, "inputs");
    fs.mkdirSync(inputRoot);
    const compilationSelection = path.join(inputRoot, "compilation-selection.json");
    const integrationSource = path.join(inputRoot, "integration-source.json");
    const providerSelection = path.join(inputRoot, "provider-selection.json");
    writeJson(compilationSelection, fixture.candidate.selection);
    writeJson(integrationSource, result.integrationSource);
    writeJson(providerSelection, fixture.formation.runtime!.selected.selection);
    const common = [
      "--compilation-selection", compilationSelection,
      "--integration-source", integrationSource,
      "--provider-selection", providerSelection,
    ];
    const build = runCli(fixture.compiler, [
      "build", sourceRoot,
      "--language", language,
      "--target-root", targetRoot,
      ...common,
    ]);
    assert.equal(build.result, "pass");
    assert.equal(build.language, language);
    const receiptPath = path.join(outputRootArgument, `${language}-runtime-evidence.json`);
    const languageTools = language === "typescript"
      ? ["--node-executable", tools.node, "--npm-executable", tools.npm]
      : language === "python"
        ? ["--python-executable", tools.python]
        : ["--cargo-executable", tools.cargo];
    const runtime = runCli(fixture.compiler, [
      "verify-runtime", sourceRoot,
      "--language", language,
      "--target-root", targetRoot,
      "--temporary-parent", workspace,
      "--receipt", receiptPath,
      ...languageTools,
      ...common,
    ]);
    const receipt = runtime.receipt;
    assert.equal(runtime.result, "pass");
    assert.equal(receipt.language, language);
    assert.equal(receipt.evidence_scope, "native-compilation-and-bounded-loopback-http");
    assert.equal(receipt.native_compilation.result, "pass");
    assert.equal(receipt.listener_startup.boundary, "loopback-only");
    assert.equal(receipt.signed_webhook_behavior.invalid_signature_status, 401);
    assert.equal(receipt.signed_webhook_behavior.valid_signature_status, 202);
    assert.deepEqual(receipt.provider_dependencies, {
      postgresql: "not-observed",
      nats: "not-observed",
      outbound_http: "not-observed",
    });
    assert.equal(receipt.production_runtime_guarantees_observed, false);
    const outcome = normalizedOutcome(result);
    outcomes.push(outcome);
    runs.push({
      language,
      result: "pass",
      provider_application_plan_sha256: result.application.plan_sha256,
      normalized_semantic_sha256: digest(json(outcome)),
      runtime_evidence: path.basename(receiptPath),
      runtime_evidence_sha256: digest(fs.readFileSync(receiptPath, "utf8")),
      runtime_receipt_sha256: receipt.receipt_sha256,
      native_compilation: "pass",
      signed_loopback_http: "pass",
      provider_dependencies: receipt.provider_dependencies,
    });
  }
  assert.deepEqual(outcomes[1], outcomes[0]);
  assert.deepEqual(outcomes[2], outcomes[0]);
  const qualification = {
    schema_version: "alchlang.c05-three-language-qualification/v1-candidate",
    date: new Date().toISOString().slice(0, 10),
    source_sha256: sourceSha256,
    languages: [...languages],
    normalized_semantic_sha256: digest(json(outcomes[0])),
    normalized_semantic_outcome: outcomes[0],
    runs,
    denominators: { languages: 3, passed: 3, failed: 0, skipped: 0 },
    evidence_scope: "same authored application formation, native compilation, and signed loopback HTTP behavior",
    provider_observation_ceiling: {
      postgresql: "not-observed",
      nats: "not-observed",
      outbound_http: "not-observed",
      transport_delivery_observed: false,
      consumer_completion_observed: false,
      production_runtime_guarantees_observed: false,
    },
    byte_equality_required: false,
    result: "pass",
    authority_effect: "none",
    open_questions: [
      "Durable PostgreSQL, NATS delivery, outbound HTTP, and production runtime guarantees remain later evidence work.",
    ],
  };
  writeJson(path.join(outputRootArgument, "qualification.json"), qualification);
  process.stdout.write(`${JSON.stringify({ result: "pass", output_root: outputRootArgument, qualification }, null, 2)}\n`);
} catch (error) {
  try { fs.rmSync(outputRootArgument, { recursive: true, force: true }); } catch { /* best-effort cleanup of incomplete evidence */ }
  throw error;
} finally {
  fs.rmSync(temporaryRoot, { recursive: true, force: true });
}
