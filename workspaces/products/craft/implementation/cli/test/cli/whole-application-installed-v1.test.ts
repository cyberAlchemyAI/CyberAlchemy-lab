import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const cliRoot = path.resolve(here, "../..");
const canonicalJson = (value: unknown): string => Array.isArray(value) ? `[${value.map(canonicalJson).join(",")}]` : value !== null && typeof value === "object" ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonicalJson((value as Record<string, unknown>)[key])}`).join(",")}}` : JSON.stringify(value) ?? "null";

function executable(name: string): string {
  const candidate = (process.env.PATH ?? "").split(path.delimiter).map(directory => path.join(directory, name)).find(file => fs.existsSync(file));
  assert.ok(candidate, `${name} executable required`);
  return path.resolve(candidate);
}

function assertRuntimeEvidence(language: "typescript" | "python" | "rust", receiptPath: string) {
  const receipt = JSON.parse(fs.readFileSync(receiptPath, "utf8"));
  assert.equal(receipt.schema_version, "domainspec.provider-application-runtime-evidence/v1-candidate");
  assert.equal(receipt.language, language);
  assert.deepEqual(receipt.formation_currentness, { observed: true, before: "pass", after: "pass" });
  assert.deepEqual(receipt.native_compilation, { observed: true, result: "pass" });
  assert.equal(receipt.listener_startup.observed, true);
  assert.equal(receipt.listener_startup.boundary, "loopback-only");
  assert.deepEqual(receipt.signed_webhook_behavior, { observed: true, result: "pass", invalid_signature_status: 401, valid_signature_status: 202, handler_invocations: 1 });
  assert.deepEqual(receipt.provider_dependencies, { postgresql: "not-observed", nats: "not-observed", outbound_http: "not-observed" });
  assert.equal(receipt.production_runtime_guarantees_observed, false);
  assert.equal(receipt.target_mutated, false);
  assert.equal(receipt.temporary_resources_removed, true);
  assert.equal(receipt.authority_effect, "none");
  return receipt;
}

function assertGeneratedApplication(language: "typescript" | "python" | "rust", target: string, buildResult: Record<string, unknown>) {
  const receipt = JSON.parse(fs.readFileSync(path.join(target, ".domainspec/whole-application.json"), "utf8"));
  assert.equal(receipt.language, language);
  assert.equal(buildResult.provider_application_plan_sha256, receipt.provider_application_plan_sha256);
  assert.equal(buildResult.artifact_count, receipt.artifacts.length);
  const observed = receipt.artifacts.map((artifact: { relative_path: string }) => {
    const bytes = fs.readFileSync(path.join(target, artifact.relative_path));
    return { relative_path: artifact.relative_path, size_bytes: bytes.length, sha256: crypto.createHash("sha256").update(bytes).digest("hex") };
  }).sort((left: { relative_path: string }, right: { relative_path: string }) => left.relative_path.localeCompare(right.relative_path));
  assert.deepEqual(observed, receipt.artifacts);
  const artifactSetSha256 = crypto.createHash("sha256").update(canonicalJson(observed)).digest("hex");
  const applicationGraphBytes = fs.readFileSync(path.join(target, ".domainspec/application-graph.json"));
  const applicationGraph = JSON.parse(applicationGraphBytes.toString("utf8"));
  assert.equal(applicationGraph.schema_version, "domainspec.compiled-application-graph/v1-candidate");
  assert.equal(applicationGraph.authority_effect, "none");
  assert.deepEqual([...new Set(applicationGraph.edges.filter((edge: { relationship_authority: string }) => edge.relationship_authority === "integration").map((edge: { relationship: string }) => edge.relationship))].sort(), ["accepts-request", "invokes", "produces-message-contract", "publishes-event", "reads-payload-from"]);
  return { candidate_plan_sha256: receipt.provider_application_plan_sha256, candidate_artifact_set_sha256: artifactSetSha256, candidate_artifacts_matched: receipt.artifacts.length, application_graph_file_sha256: crypto.createHash("sha256").update(applicationGraphBytes).digest("hex"), application_graph_sha256: applicationGraph.graph_sha256 };
}

test("L4 packed CLI builds, starts, and exercises all provider languages outside the checkout", t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "domainspec-whole-installed-"));
  t.after(() => fs.rmSync(temporary, { recursive: true, force: true }));
  const languageReports: Record<string, unknown> = {};
  const applicationGraphFileDigests = new Set<string>();
  const npmEnvironment = { ...process.env, npm_config_cache: path.join(temporary, "npm-cache") };
  const pack = spawnSync("npm", ["pack", "--json", "--ignore-scripts", "--pack-destination", temporary], { cwd: cliRoot, encoding: "utf8", env: npmEnvironment });
  assert.equal(pack.status, 0, `${pack.stdout}\n${pack.stderr}`);
  const packed = JSON.parse(pack.stdout) as readonly { filename: string }[];
  const tarball = path.join(temporary, packed[0]!.filename);
  const tarballSha256 = crypto.createHash("sha256").update(fs.readFileSync(tarball)).digest("hex");
  const consumer = path.join(temporary, "consumer");
  fs.mkdirSync(consumer);
  fs.writeFileSync(path.join(consumer, "package.json"), '{"type":"module","private":true}\n');
  const install = spawnSync("npm", ["install", "--ignore-scripts", "--no-audit", "--no-fund", tarball], { cwd: consumer, encoding: "utf8", env: npmEnvironment });
  assert.equal(install.status, 0, `${install.stdout}\n${install.stderr}`);
  const installed = path.join(consumer, "node_modules/@domainspec-v2/cli");
  const documentedPackageRoot = spawnSync(process.execPath, ["--input-type=module", "-e", "import{fileURLToPath}from'node:url';console.log(fileURLToPath(new URL('../',import.meta.resolve('@domainspec-v2/cli'))))"], { cwd: consumer, encoding: "utf8" });
  assert.equal(documentedPackageRoot.status, 0, `${documentedPackageRoot.stdout}\n${documentedPackageRoot.stderr}`);
  assert.equal(path.resolve(documentedPackageRoot.stdout.trim()), installed);
  const example = path.join(installed, "examples/reconciled-commerce");
  const target = path.join(temporary, "application");
  const runInstalledCli = (args: readonly string[]) => spawnSync("npx", ["--no-install", "domainspec-v2", ...args], { cwd: consumer, encoding: "utf8", env: npmEnvironment });
  const common = [path.join(example, "source"), "--language", "typescript", "--target-root", target, "--compilation-selection", path.join(example, "selections/typescript.json"), "--integration-source", path.join(example, "integrations/application.json")];
  const build = runInstalledCli(["build", ...common]);
  assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
  assert.equal(JSON.parse(build.stdout).schema_version, "domainspec.whole-application-command-result/v1-candidate");
  const verify = runInstalledCli(["verify", ...common]);
  assert.equal(verify.status, 0, `${verify.stdout}\n${verify.stderr}`);
  assert.equal(JSON.parse(verify.stdout).result, "pass");
  const imported = spawnSync(process.execPath, ["--input-type=module", "-e", "import('@domainspec-v2/cli/whole-application').then(m=>{if(typeof m.planWholeApplicationV1!=='function')process.exit(2)})"], { cwd: consumer, encoding: "utf8" });
  assert.equal(imported.status, 0, `${imported.stdout}\n${imported.stderr}`);

  const providerTarget = path.join(temporary, "provider-application");
  const providerCommon = [path.join(example, "source"), "--language", "typescript", "--target-root", providerTarget, "--compilation-selection", path.join(example, "selections/typescript.json"), "--integration-source", path.join(example, "integrations/application.json"), "--provider-selection", path.join(example, "providers/typescript.json")];
  const providerBuild = runInstalledCli(["build", ...providerCommon]);
  assert.equal(providerBuild.status, 0, `${providerBuild.stdout}\n${providerBuild.stderr}`);
  const providerBuildResult = JSON.parse(providerBuild.stdout);
  assert.equal(providerBuildResult.schema_version, "domainspec.provider-application-command-result/v1-candidate");
  const typescriptCandidate = assertGeneratedApplication("typescript", providerTarget, providerBuildResult);
  applicationGraphFileDigests.add(typescriptCandidate.application_graph_file_sha256);
  const providerVerify = runInstalledCli(["verify", ...providerCommon]);
  assert.equal(providerVerify.status, 0, `${providerVerify.stdout}\n${providerVerify.stderr}`);
  assert.equal(JSON.parse(providerVerify.stdout).result, "pass");
  const providerImported = spawnSync(process.execPath, ["--input-type=module", "-e", "Promise.all([import('@domainspec-v2/cli/whole-application'),import('@domainspec-v2/cli/reference-runtime')]).then(([whole,runtime])=>{if(typeof whole.composeProviderApplicationV1!=='function'||typeof whole.publishProviderApplicationV1!=='function'||typeof runtime.planReferenceRuntimeV1!=='function')process.exit(2)})"], { cwd: consumer, encoding: "utf8" });
  assert.equal(providerImported.status, 0, `${providerImported.stdout}\n${providerImported.stderr}`);
  for (const schema of [
    "provider-pack-selection-v1.schema.json",
    "provider-application-runtime-evidence-v1.schema.json",
    "integration-generation-source-v2.schema.json",
    "application-integration-binding-v1.schema.json",
    "compiled-application-graph-v1.schema.json",
    "whole-application-plan-v1.schema.json",
    "persistence-composition-v2.schema.json",
    "messaging-composition-v2.schema.json",
    "external-api-composition-v2.schema.json",
    "integration-observation-v1.schema.json",
    "integration-kernel-v2.schema.json",
  ]) assert.equal(fs.existsSync(path.join(installed, "contracts", schema)), true, schema);
  assert.equal(fs.existsSync(path.join(installed, "WHOLE-APPLICATION.md")), true);

  const typescriptReceiptPath = path.join(temporary, "typescript-runtime-evidence.json");
  const typescriptRuntime = runInstalledCli(["verify-runtime", ...providerCommon, "--temporary-parent", temporary, "--receipt", typescriptReceiptPath, "--node-executable", process.execPath, "--npm-executable", executable("npm")]);
  assert.equal(typescriptRuntime.status, 0, `${typescriptRuntime.stdout}\n${typescriptRuntime.stderr}`);
  const typescriptRuntimeResult = JSON.parse(typescriptRuntime.stdout);
  assert.equal(typescriptRuntimeResult.result, "pass");
  const typescriptEvidence = assertRuntimeEvidence("typescript", typescriptReceiptPath);
  const typescriptVerifyAfter = runInstalledCli(["verify", ...providerCommon]);
  assert.equal(typescriptVerifyAfter.status, 0, `${typescriptVerifyAfter.stdout}\n${typescriptVerifyAfter.stderr}`);
  assert.equal(JSON.parse(typescriptVerifyAfter.stdout).result, "pass");
  languageReports.typescript = { build: "pass", ...typescriptCandidate, verify_before: "pass", runtime_evidence_receipt_sha256: typescriptEvidence.receipt_sha256, execution_environment: typescriptEvidence.execution_environment, target_mutated: false, verify_after: "pass", result: "pass" };

  for (const language of ["python", "rust"] as const) {
    const languageTarget = path.join(temporary, `provider-${language}`);
    const languageCommon = [path.join(example, "source"), "--language", language, "--target-root", languageTarget, "--compilation-selection", path.join(example, `selections/${language}.json`), "--integration-source", path.join(example, "integrations/application.json"), "--provider-selection", path.join(example, `providers/${language}.json`)];
    const languageBuild = runInstalledCli(["build", ...languageCommon]);
    assert.equal(languageBuild.status, 0, `${languageBuild.stdout}\n${languageBuild.stderr}`);
    const languageBuildResult = JSON.parse(languageBuild.stdout);
    assert.equal(languageBuildResult.schema_version, "domainspec.provider-application-command-result/v1-candidate");
    const candidateMatch = assertGeneratedApplication(language, languageTarget, languageBuildResult);
    applicationGraphFileDigests.add(candidateMatch.application_graph_file_sha256);
    const languageVerify = runInstalledCli(["verify", ...languageCommon]);
    assert.equal(languageVerify.status, 0, `${languageVerify.stdout}\n${languageVerify.stderr}`);
    if (language === "python") {
      const pythonImage = "python:3.11.2-slim@sha256:9ad4ffc502779e5508f7ac1eccab4a22786b80bd53d721d735f6de0840b245a1";
      const receiptPath = path.join(temporary, "python-runtime-evidence.json");
      const runtime = runInstalledCli(["verify-runtime", ...languageCommon, "--temporary-parent", temporary, "--receipt", receiptPath, "--docker-executable", executable("docker"), "--python-image", pythonImage]);
      assert.equal(runtime.status, 0, `${runtime.stdout}\n${runtime.stderr}`);
      assert.equal(JSON.parse(runtime.stdout).result, "pass");
      const evidence = assertRuntimeEvidence("python", receiptPath);
      assert.deepEqual(evidence.execution_environment, { kind: "container", identifier: pythonImage });
      const verifyAfter = runInstalledCli(["verify", ...languageCommon]);
      assert.equal(verifyAfter.status, 0, `${verifyAfter.stdout}\n${verifyAfter.stderr}`);
      assert.equal(JSON.parse(verifyAfter.stdout).result, "pass");
      languageReports.python = { build: "pass", ...candidateMatch, verify_before: "pass", runtime_evidence_receipt_sha256: evidence.receipt_sha256, execution_environment: evidence.execution_environment, target_mutated: false, verify_after: "pass", result: "pass" };
    } else {
      const receiptPath = path.join(temporary, "rust-runtime-evidence.json");
      const runtime = runInstalledCli(["verify-runtime", ...languageCommon, "--temporary-parent", temporary, "--receipt", receiptPath, "--cargo-executable", executable("cargo")]);
      assert.equal(runtime.status, 0, `${runtime.stdout}\n${runtime.stderr}`);
      assert.equal(JSON.parse(runtime.stdout).result, "pass");
      const evidence = assertRuntimeEvidence("rust", receiptPath);
      const verifyAfter = runInstalledCli(["verify", ...languageCommon]);
      assert.equal(verifyAfter.status, 0, `${verifyAfter.stdout}\n${verifyAfter.stderr}`);
      assert.equal(JSON.parse(verifyAfter.stdout).result, "pass");
      languageReports.rust = { build: "pass", ...candidateMatch, verify_before: "pass", runtime_evidence_receipt_sha256: evidence.receipt_sha256, execution_environment: evidence.execution_environment, warnings_suppressed: false, target_mutated: false, verify_after: "pass", result: "pass" };
    }
  }
  assert.equal(applicationGraphFileDigests.size, 1, "all language targets must carry the same application graph bytes");
  fs.rmSync(temporary, { recursive: true, force: true });
  const reportPath = process.env.DOMAINSPEC_L4_REPORT_PATH;
  if (reportPath) {
    const report = {
      schema_version: "domainspec.whole-application-installed-consumer-report/v1-candidate",
      layer: "L4",
      recorded_at: new Date().toISOString(),
      result: "pass",
      package_source: "fresh npm pack tarball",
      package_sha256: tarballSha256,
      installed_outside_checkout: true,
      api_import: { result: "pass", entrypoints: ["@domainspec-v2/cli/whole-application", "@domainspec-v2/cli/reference-runtime"], reference_runtime_export: "present" },
      ...languageReports,
      packaged_schemas: ["provider-pack-selection-v1", "provider-application-runtime-evidence-v1", "integration-generation-source-v2", "application-integration-binding-v1", "compiled-application-graph-v1", "whole-application-plan-v1", "persistence-composition-v2", "messaging-composition-v2", "external-api-composition-v2", "integration-observation-v1", "integration-kernel-v2"],
      whole_application_guide: "present",
      consumer_roots_disposed: true,
      task_owned_temporary_resources_disposed: true,
      publication: false,
      release: false,
      authority_effect: "none",
    };
    fs.mkdirSync(path.dirname(reportPath), { recursive: true });
    fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
  }
});
