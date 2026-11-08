#!/usr/bin/env node
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

type Language = "typescript" | "python" | "rust";
type Json = Record<string, any>;

const implementationRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(implementationRoot, "../../../../../..");
const domainSpecRoot = path.join(repoRoot, "craft/projects/domainspec-v2/impl/cli");
const planRoot = path.join(repoRoot, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1");
const historicalEvidenceRoot = path.join(planRoot, "evidence/p02-clean-consumers");
const evidenceRoot = path.join(historicalEvidenceRoot, "successor-v5-candidate");
const evidenceDate = new Date().toISOString().slice(0, 10);
const toolchain = path.join(repoRoot, "tools/toolchain/run");
const languages: readonly Language[] = ["typescript", "python", "rust"];

assert.equal(fs.existsSync(evidenceRoot), false, `P02 successor evidence already exists: ${evidenceRoot}`);

const sha256Bytes = (bytes: string | Buffer) => crypto.createHash("sha256").update(bytes).digest("hex");
const sha256File = (file: string) => sha256Bytes(fs.readFileSync(file));
const readJson = (file: string): Json => JSON.parse(fs.readFileSync(file, "utf8"));
const relative = (file: string) => path.relative(repoRoot, file).split(path.sep).join("/");

function run(command: string, args: readonly string[], options: { cwd?: string; env?: NodeJS.ProcessEnv; timeout?: number } = {}) {
  const result = spawnSync(command, [...args], {
    cwd: options.cwd,
    env: options.env ?? process.env,
    encoding: "utf8",
    timeout: options.timeout ?? 300_000,
  });
  assert.equal(result.status, 0, `${command} ${args.join(" ")}\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`);
  return result.stdout.trim();
}

function runJson(command: string, args: readonly string[], options: { cwd?: string; env?: NodeJS.ProcessEnv; timeout?: number } = {}): Json {
  return JSON.parse(run(command, args, options));
}

function installedPackage(consumer: string, name: string): { name: string; version: string; root: string; package_json_sha256: string } {
  const root = path.join(consumer, "node_modules", ...name.split("/"));
  const manifestPath = path.join(root, "package.json");
  assert.ok(fs.existsSync(manifestPath), `missing installed package ${name}`);
  assert.equal(fs.lstatSync(root).isSymbolicLink(), false, `${name} must not be linked into the checkout`);
  const manifest = readJson(manifestPath);
  assert.equal(manifest.name, name);
  return { name, version: manifest.version, root, package_json_sha256: sha256File(manifestPath) };
}

function inspectTarget(language: Language, target: string) {
  const files = {
    alch_manifest: path.join(target, ".alch/manifest.json"),
    application_artifact_index: path.join(target, ".alch/whole/application-artifact-index.json"),
    application_runtime_binding: path.join(target, ".alch/whole/application-runtime-binding.json"),
    external_api_routes: path.join(target, ".alch/formation/external-api-routes.json"),
    application_graph: path.join(target, ".domainspec/application-graph.json"),
    provider_manifest: path.join(target, ".domainspec/providers/manifest.json"),
  };
  for (const [name, file] of Object.entries(files)) assert.ok(fs.existsSync(file), `${language}: missing ${name}`);
  const graph = readJson(files.application_graph);
  const runtime = readJson(files.application_runtime_binding);
  const artifactIndex = readJson(files.application_artifact_index);
  const alch = readJson(files.alch_manifest);
  const routes = readJson(files.external_api_routes);
  assert.equal(graph.schema_version, "domainspec.compiled-application-graph/v1-candidate");
  assert.equal(graph.authority_effect, "none");
  assert.equal(runtime.language, language);
  assert.equal(runtime.authority_effect, "none");
  assert.equal(artifactIndex.authority_effect, "none");
  assert.equal(alch.authority_effect, "none");
  assert.equal(routes.schema_version, "alchlang.application-api-routes/v1-candidate");
  assert.equal(routes.authority_effect, "none");
  assert.equal(routes.runtime_listener_observed, false);
  assert.equal(routes.routes.length, 1, `${language}: expected one authored inbound route`);
  const inboundRoute = routes.routes[0];
  assert.equal(inboundRoute.method, "POST");
  assert.match(inboundRoute.path, /^\/[A-Za-z0-9/_-]+$/u);
  assert.equal(inboundRoute.path.includes("//"), false);
  const relationships = [...new Set(graph.edges.filter((edge: Json) => edge.relationship_authority === "integration").map((edge: Json) => edge.relationship))].sort();
  assert.deepEqual(relationships, ["accepts-request", "invokes", "produces-message-contract", "publishes-event", "reads-payload-from"]);
  return {
    files: Object.fromEntries(Object.entries(files).map(([name, file]) => [name, { relative_path: path.relative(target, file).split(path.sep).join("/"), sha256: sha256File(file) }])),
    application_graph_sha256: graph.graph_sha256,
    inbound_route: { method: inboundRoute.method, path: inboundRoute.path },
    integration_relationships: relationships,
    authority_effect: "none",
  };
}

function scenarioResult(stdout: string, language: Language) {
  const result = JSON.parse(stdout);
  const startup = language === "typescript" ? "http-listener" : language === "python" ? "asgi-http-listener" : "axum-http-listener";
  assert.deepEqual(result, {
    language,
    startup,
    invalid_status: 401,
    valid_status: 202,
    handler_invocations: 1,
    result: "pass",
  });
  return result;
}

function qualifyTypeScript(target: string, nativeRoot: string, scenario: string, route: string) {
  fs.cpSync(target, nativeRoot, { recursive: true, errorOnExist: true, force: false });
  run("npm", ["ci", "--ignore-scripts", "--no-audit", "--no-fund"], { cwd: nativeRoot });
  const tsc = path.join(nativeRoot, "node_modules/.bin/tsc");
  run(tsc, ["--noEmit", "--pretty", "false"], { cwd: nativeRoot });
  run(tsc, ["--noEmit", "false", "--outDir", "dist", "--pretty", "false"], { cwd: nativeRoot });
  const observed = scenarioResult(run(process.execPath, [scenario, nativeRoot, route]), "typescript");
  return { native_compilation: "pass", compiler: run(tsc, ["--version"], { cwd: nativeRoot }), dependency_install: "npm-ci-locked-registry-read", scenario: observed };
}

function qualifyPython(target: string, nativeRoot: string, scenario: string, route: string) {
  fs.mkdirSync(nativeRoot, { recursive: true });
  const application = path.join(nativeRoot, "application");
  fs.cpSync(target, application, { recursive: true, errorOnExist: true, force: false });
  const python = process.env.ALCHLANG_P02_PYTHON ?? "python3";
  run(python, ["-m", "venv", path.join(nativeRoot, "venv")]);
  const nativePython = path.join(nativeRoot, "venv/bin/python");
  run(nativePython, ["-m", "pip", "install", "--disable-pip-version-check", "--no-input", "--no-cache-dir", "--quiet", "-r", path.join(application, "requirements.lock")], { timeout: 600_000 });
  run(nativePython, ["-m", "compileall", "-q", path.join(application, "src")]);
  const sitePackages = run(nativePython, ["-c", "import site;print(site.getsitepackages()[0])"]);
  const env = { ...process.env, PYTHONDONTWRITEBYTECODE: "1", PYTHONPATH: `${sitePackages}${path.delimiter}${path.join(application, "src")}` };
  const observed = scenarioResult(run(nativePython, [scenario, application, route], { env }), "python");
  return { native_compilation: "pass", compiler: run(nativePython, ["--version"]), dependency_install: "pip-locked-registry-read", scenario: observed };
}

function qualifyRust(target: string, nativeRoot: string, scenario: string, route: string) {
  fs.cpSync(target, nativeRoot, { recursive: true, errorOnExist: true, force: false });
  const binaryRoot = path.join(nativeRoot, "src/bin");
  fs.mkdirSync(binaryRoot, { recursive: true });
  fs.copyFileSync(scenario, path.join(binaryRoot, "domainspec-installed-scenario.rs"));
  const env = { ...process.env, CARGO_NET_OFFLINE: "true", CARGO_TARGET_DIR: path.join(path.dirname(nativeRoot), "rust-target") };
  run(toolchain, ["cargo", "check", "--manifest-path", path.join(nativeRoot, "Cargo.toml"), "--locked", "--offline"], { env, timeout: 600_000 });
  const observed = scenarioResult(run(toolchain, ["cargo", "run", "--manifest-path", path.join(nativeRoot, "Cargo.toml"), "--locked", "--offline", "--quiet", "--bin", "domainspec-installed-scenario", "--", route], { env, timeout: 600_000 }), "rust");
  return { native_compilation: "pass", compiler: run(toolchain, ["cargo", "--version"]), dependency_install: "cargo-locked-offline", scenario: observed };
}

function binding(file: string) {
  return { path: relative(file), sha256: sha256File(file) };
}

run(process.execPath, ["scripts/run-toolchain.mjs", "tsx", "scripts/materialize-application-v1-examples.ts", "--check"], { cwd: implementationRoot });
run(process.execPath, ["scripts/materialize-package-boundaries.mjs", "--check"], { cwd: implementationRoot });

const runRoot = fs.mkdtempSync(path.join(os.tmpdir(), "alchlang-p02-clean-consumers-"));
let reports: Json[] = [];
try {
  const archiveRoot = path.join(runRoot, "archives");
  fs.mkdirSync(archiveRoot);
  const domainPack = runJson("npm", ["pack", "--json", "--ignore-scripts", "--pack-destination", archiveRoot], { cwd: domainSpecRoot });
  const domainArchive = path.join(archiveRoot, domainPack[0].filename);
  const alchPlan = runJson(process.execPath, ["scripts/package-release.mjs", archiveRoot], { cwd: implementationRoot });
  const archives = Object.fromEntries(alchPlan.artifacts.map((artifact: Json) => [artifact.id, artifact.file]));
  const archiveEvidence = {
    domainspec_cli: { name: "@domainspec-v2/cli", sha256: sha256File(domainArchive), size_bytes: fs.statSync(domainArchive).size },
    ...Object.fromEntries(alchPlan.artifacts.map((artifact: Json) => [artifact.id, { name: artifact.name, sha256: sha256File(artifact.file), size_bytes: fs.statSync(artifact.file).size, file_count: artifact.file_count }])),
  };
  for (const language of languages) {
    const consumer = path.join(runRoot, "consumers", language);
    fs.mkdirSync(consumer, { recursive: true });
    fs.writeFileSync(path.join(consumer, "package.json"), `${JSON.stringify({ private: true, type: "module" }, null, 2)}\n`);
    const requested = [domainArchive, archives.core];
    if (language === "rust") requested.push(archives.rust);
    run("npm", ["install", "--offline", "--ignore-scripts", "--no-audit", "--no-fund", ...requested], { cwd: consumer });
    const core = installedPackage(consumer, "@cyberalchemy/alchlang");
    const domain = installedPackage(consumer, "@domainspec-v2/cli");
    const installed = [core, domain];
    if (language === "rust") installed.push(installedPackage(consumer, "@cyberalchemy/alchlang-rust"));
    const source = path.join(core.root, "examples/application-v1", language, "commerce.alch");
    assert.ok(fs.existsSync(source));
    const target = path.join(consumer, "generated-application");
    const alchlang = path.join(consumer, "node_modules/.bin/alchlang");
    const check = runJson(alchlang, ["check", source], { cwd: consumer });
    assert.equal(check.status, "valid");
    assert.equal(check.scope, "provider-application-artifacts");
    const build = runJson(alchlang, ["build", source, "--out", target], { cwd: consumer });
    assert.equal(build.status, "built");
    assert.equal(build.scope, "provider-application-artifacts");
    const verifyBefore = runJson(alchlang, ["verify", source, "--out", target], { cwd: consumer });
    assert.equal(verifyBefore.status, "verified");
    assert.equal(verifyBefore.manifest_sha256, build.manifest_sha256);
    const inspection = inspectTarget(language, target);
    const scenario = path.join(domain.root, "examples/reconciled-commerce/scenarios", `${language}-webhook.${language === "typescript" ? "mjs" : language === "python" ? "py" : "rs"}`);
    const nativeRoot = path.join(runRoot, "native", language);
    const native = language === "typescript" ? qualifyTypeScript(target, nativeRoot, scenario, inspection.inbound_route.path)
      : language === "python" ? qualifyPython(target, nativeRoot, scenario, inspection.inbound_route.path)
      : qualifyRust(target, nativeRoot, scenario, inspection.inbound_route.path);
    const verifyAfter = runJson(alchlang, ["verify", source, "--out", target], { cwd: consumer });
    assert.equal(verifyAfter.status, "verified");
    assert.equal(verifyAfter.manifest_sha256, build.manifest_sha256);
    reports.push({
      schema_version: "alchlang.p02-clean-consumer-report/v1-candidate",
      date: evidenceDate,
      task: "P02",
      language,
      result: "pass",
      authority_effect: "none",
      installed_outside_checkout: true,
      package_archives: archiveEvidence,
      installed_packages: installed.map(item => ({ name: item.name, version: item.version, package_json_sha256: item.package_json_sha256 })),
      documented_source: { package: "@cyberalchemy/alchlang", path: `examples/application-v1/${language}/commerce.alch`, sha256: sha256File(source) },
      application: {
        check: { status: check.status, scope: check.scope, generated_artifacts: check.generated_artifacts },
        lowering: "pass",
        build: { status: build.status, scope: build.scope, manifest_sha256: build.manifest_sha256 },
        verify_before: { status: verifyBefore.status, manifest_sha256: verifyBefore.manifest_sha256 },
        inspection,
        native,
        verify_after: { status: verifyAfter.status, manifest_sha256: verifyAfter.manifest_sha256 },
      },
      cleanup: { consumer_root_disposed: true, native_root_disposed: true, task_owned_temporary_resources_disposed: true },
      publication: false,
      release: false,
      deployment: false,
      product_owner_validation: "deferred-to-L4X",
      claim_ceiling: "P02 clean installed-consumer construction evidence only; no product approval, release admission, publication, deployment, production guarantee, or authority effect.",
      open_questions: ["P03 owns freezing one exact candidate and a non-mutating currentness validator."],
    });
  }
  assert.equal(new Set(reports.map(report => report.application.inspection.files.application_graph.sha256)).size, 1, "all languages must retain identical application graph bytes");
} finally {
  fs.rmSync(runRoot, { recursive: true, force: true });
}

assert.equal(fs.existsSync(runRoot), false, "P02 run root must be disposed before reports are persisted");
fs.mkdirSync(evidenceRoot);
for (const report of reports) fs.writeFileSync(path.join(evidenceRoot, `${report.language}.json`), `${JSON.stringify(report, null, 2)}\n`);
const reportBindings = Object.fromEntries(languages.map(language => [language, binding(path.join(evidenceRoot, `${language}.json`))]));
const qualification = {
  schema_version: "alchlang.p02-clean-consumers-qualification/v5-candidate",
  date: evidenceDate,
  task: "P02",
  result: "pass",
  authority_effect: "none",
  supersedes_historical_qualification: binding(path.join(historicalEvidenceRoot, "qualification.json")),
  supersedes_previous_qualification: binding(path.join(historicalEvidenceRoot, "successor-v4-candidate/qualification.json")),
  inherited_boundaries: {
    P01: binding(path.join(planRoot, "evidence/p01-package-boundaries/qualification.v3-candidate.json")),
    O01: binding(path.join(planRoot, "O01-COMPLETION.md")),
  },
  bindings: {
    qualifier: binding(path.join(implementationRoot, "scripts/qualify-p02-clean-consumers.ts")),
    example_materializer: binding(path.join(implementationRoot, "scripts/materialize-application-v1-examples.ts")),
    example_guide: binding(path.join(implementationRoot, "CLEAN-CONSUMER.md")),
    package_boundaries: binding(path.join(implementationRoot, "package-boundaries.json")),
    fixture_generator: binding(path.join(implementationRoot, "test/fixtures/application-whole-fixture.ts")),
  },
  reports: reportBindings,
  languages: languages.map(language => ({ language, result: "pass", report_sha256: reportBindings[language].sha256 })),
  validation: {
    clean_consumer_reports: { tests: 3, passed: 3, failed: 0, skipped: 0 },
    check_lower_build_verify_native_scenario_inspection_cleanup: "pass",
    cross_language_application_graph_bytes: "identical",
    product_owner_validation: "deferred-to-L4X",
  },
  hard_stops: {
    undocumented_repair: false,
    weaker_language_path: false,
    checkout_link_or_fallback: false,
    owned_temporary_residue: false,
    publication_or_release_performed: false,
    product_approval_inferred: false,
    authority_effect_inferred: false,
  },
  claim_ceiling: "P02 clean installed-consumer construction evidence only; no candidate freeze, D65 admission, product approval, release admission, publication, deployment, production guarantee, or authority effect.",
  open_questions: ["P03 owns freezing the exact candidate and currentness validator."],
};
fs.writeFileSync(path.join(evidenceRoot, "qualification.json"), `${JSON.stringify(qualification, null, 2)}\n`);
process.stdout.write(`${JSON.stringify({ result: "pass", languages, evidence: relative(path.join(evidenceRoot, "qualification.json")) }, null, 2)}\n`);
