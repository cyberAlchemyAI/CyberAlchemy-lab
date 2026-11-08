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
const evidenceRoot = path.join(historicalEvidenceRoot, "successor-v6-candidate");
const p01Path = path.join(planRoot, "evidence/p01-package-boundaries/qualification.v5-candidate.json");
const previousPath = path.join(historicalEvidenceRoot, "successor-v5-candidate/qualification.json");
const evidenceDate = new Date().toISOString().slice(0, 10);
const toolchain = path.join(repoRoot, "tools/toolchain/run");
const languages: readonly Language[] = ["typescript", "python", "rust"];

assert.equal(process.argv.length, 2, "P02 v6 measurement takes no arguments and never persists evidence");
const subprocessEnv = { ...process.env };
for (const key of ["ALCHLANG_DOMAINSPEC_PACKAGE_ROOT", "NODE_PATH", "NODE_OPTIONS", "PYTHONPATH", "PYTHONHOME", "NPM_CONFIG_CACHE"]) delete subprocessEnv[key];

const sha256Bytes = (bytes: string | Buffer) => crypto.createHash("sha256").update(bytes).digest("hex");
const sha256File = (file: string) => sha256Bytes(fs.readFileSync(file));
const readJson = (file: string): Json => JSON.parse(fs.readFileSync(file, "utf8"));
const relative = (file: string) => path.relative(repoRoot, file).split(path.sep).join("/");

function run(command: string, args: readonly string[], options: { cwd?: string; env?: NodeJS.ProcessEnv; timeout?: number } = {}) {
  const result = spawnSync(command, [...args], {
    cwd: options.cwd,
    env: options.env ?? subprocessEnv,
    maxBuffer: 8 * 1024 * 1024,
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
  assert.equal(fs.realpathSync(root), root, `${name} ancestors must not be checkout links`);
  const containment = path.relative(fs.realpathSync(consumer), fs.realpathSync(root));
  assert.ok(containment && !containment.startsWith("..") && !path.isAbsolute(containment));
  assert.ok(!fs.realpathSync(consumer).startsWith(repoRoot + path.sep));
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
  const interpreter = run(python,["-c","import os,sys;print(os.path.realpath(sys.executable))"]);
  assert.equal(fs.lstatSync(interpreter).isFile(),true,"Python must resolve to a regular executable");
  const interpreterSha = sha256File(interpreter);
  run(python, ["-m", "venv", path.join(nativeRoot, "venv")]);
  const nativePython = path.join(nativeRoot, "venv/bin/python");
  assert.equal(sha256File(fs.realpathSync(nativePython)),interpreterSha,"venv interpreter drift");
  run(nativePython, ["-m", "pip", "--isolated", "install", "--index-url", "https://pypi.org/simple", "--disable-pip-version-check", "--no-input", "--no-cache-dir", "--quiet", "-r", path.join(application, "requirements.lock")], { timeout: 600_000 });
  run(nativePython, ["-m", "compileall", "-q", path.join(application, "src")]);
  const sitePackages = run(nativePython, ["-c", "import site;print(site.getsitepackages()[0])"]);
  const env = { ...subprocessEnv, PYTHONDONTWRITEBYTECODE: "1", PYTHONPATH: `${sitePackages}${path.delimiter}${path.join(application, "src")}` };
  const observed = scenarioResult(run(nativePython, [scenario, application, route], { env }), "python");
  const compiler = run(nativePython,["--version"]);
  assert.equal(sha256File(interpreter),interpreterSha,"base Python interpreter drift");
  assert.equal(sha256File(fs.realpathSync(nativePython)),interpreterSha,"venv Python interpreter drift");
  return { native_compilation: "pass", compiler, compiler_identity: {version:compiler,executable_sha256:interpreterSha,base_executable_sha256:interpreterSha}, dependency_install: "pip-locked-registry-read", scenario: observed };
}

function qualifyRust(target: string, nativeRoot: string, scenario: string, route: string) {
  fs.cpSync(target, nativeRoot, { recursive: true, errorOnExist: true, force: false });
  const binaryRoot = path.join(nativeRoot, "src/bin");
  fs.mkdirSync(binaryRoot, { recursive: true });
  fs.copyFileSync(scenario, path.join(binaryRoot, "domainspec-installed-scenario.rs"));
  const env = { ...subprocessEnv, CARGO_NET_OFFLINE: "true", CARGO_TARGET_DIR: path.join(path.dirname(nativeRoot), "rust-target") };
  run(toolchain, ["cargo", "check", "--manifest-path", path.join(nativeRoot, "Cargo.toml"), "--locked", "--offline"], { env, timeout: 600_000 });
  const observed = scenarioResult(run(toolchain, ["cargo", "run", "--manifest-path", path.join(nativeRoot, "Cargo.toml"), "--locked", "--offline", "--quiet", "--bin", "domainspec-installed-scenario", "--", route], { env, timeout: 600_000 }), "rust");
  return { native_compilation: "pass", compiler: run(toolchain, ["cargo", "--version"]), dependency_install: "cargo-locked-offline", scenario: observed };
}

function binding(file: string) {
  return { path: relative(file), sha256: sha256File(file) };
}


function p01Paths(): string[] {
  return [...new Set<string>([
    ...Object.values(p01.bindings).map((b: any) => b.path as string),
    p01.supersedes_previous_qualification.path, p01.inherited_boundary.path, p01.dag.path,
    ...["package.json","package-lock.json","tsconfig.json","tsconfig.build.json","scripts/run-toolchain.mjs","scripts/copy-event-templates.mjs"].map(f => relative(path.join(implementationRoot, f))),
    "tools/toolchain/run", "tools/toolchain/lock.json", relative(path.join(domainSpecRoot, "package-lock.json")),
    ...boundaries.packages.flatMap((item: Json) => item.files.map((f: string) => relative(path.join(implementationRoot, f)))),
    ...boundaries.domainspec_cli.expanded_files.map((f: string) => boundaries.domainspec_cli.package_root + "/" + f),
  ])];
}
function envelope(paths: string[], schema: string) {
  const rows = [...new Set(paths)].sort().map(file => {
    const absolute = path.join(repoRoot, file);
    assert.equal(fs.lstatSync(absolute).isFile(), true, "nonregular source: " + file);
    assert.equal(fs.realpathSync(absolute), absolute, "symlinked source: " + file);
    return { path: file, sha256: sha256File(absolute) };
  });
  return { schema_version: schema, algorithm: "sha256-json-sorted-repository-path-file-sha256/v1", file_count: rows.length, sha256: sha256Bytes(JSON.stringify(rows)) };
}
function p01SourceEnvelope() {
  return envelope(p01Paths(), "alchlang.p01-source-envelope/v1-candidate");
}
function sourceEnvelope() {
  return envelope([...p01Paths(), relative(p01Path), relative(previousPath),
    relative(path.join(historicalEvidenceRoot, "qualification.json")), relative(path.join(planRoot, "O01-COMPLETION.md")),
    ...["scripts/qualify-p02-clean-consumers-v6.ts","scripts/qualify-p02-clean-consumers.ts",
      "test/application-p02-qualification.test.ts","scripts/materialize-application-v1-examples.ts",
      "CLEAN-CONSUMER.md","test/fixtures/application-whole-fixture.ts"].map(f => relative(path.join(implementationRoot, f))),
  ], "alchlang.p02-source-envelope/v1-candidate");
}
const inspectScript = [
  'import gzip,hashlib,io,json,os,sys,tarfile',
  'archive=sys.argv[1]',
  "assert os.path.getsize(archive)<=64*1024*1024, 'P01_ARCHIVE_SIZE'",
  'with gzip.open(archive,"rb") as compressed: raw=compressed.read(256*1024*1024+1)',
  "assert len(raw)<=256*1024*1024, 'P01_ARCHIVE_TAR_SIZE'",
  'rows=[];seen=set();total=0',
  'with tarfile.open(fileobj=io.BytesIO(raw),mode="r:") as stream:',
  ' for member in stream:',
  "  assert len(rows)<10000, 'P01_ARCHIVE_MEMBER_COUNT'",
  "  assert member.isfile(), 'P01_ARCHIVE_NONREGULAR'",
  "  assert member.name.startswith('package/'), 'P01_ARCHIVE_PATH'",
  "  relative=member.name[len('package/'):]",
  "  assert relative and chr(92) not in relative and all(p not in ('','.','..') for p in relative.split('/')), 'P01_ARCHIVE_PATH'",
  "  assert relative not in seen, 'P01_ARCHIVE_DUPLICATE'",
  "  assert 0<=member.size<=32*1024*1024, 'P01_ARCHIVE_MEMBER_SIZE'",
  '  total+=member.size',
  "  assert total<=256*1024*1024, 'P01_ARCHIVE_UNCOMPRESSED_SIZE'",
  '  seen.add(relative)',
  '  handle=stream.extractfile(member)',
  "  assert handle is not None, 'P01_ARCHIVE_CONTENT'",
  '  data=handle.read(member.size+1)',
  "  assert len(data)==member.size, 'P01_ARCHIVE_CONTENT'",
  "  rows.append({'path':relative,'size_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})",
  "rows.sort(key=lambda row:row['path'])",
  "fingerprint=hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()",
  "print(json.dumps({'filename':os.path.basename(archive),'archive_sha256':hashlib.sha256(open(archive,'rb').read()).hexdigest(),'size_bytes':os.path.getsize(archive),'entry_count':len(rows),'content_manifest_sha256':fingerprint,'paths':[r['path'] for r in rows]}))",
].join('\n');

function inspectArchive(file: string) {
  const result = spawnSync('python3',['-I','-c',inspectScript,file],{encoding:'utf8',timeout:30000,maxBuffer:2*1024*1024});
  assert.equal(result.status,0,result.stderr);
  return JSON.parse(result.stdout);
}

function defaultArchiveSnapshot() {
  const version=readJson(path.join(implementationRoot, 'package.json')).version;
  const base=path.join(implementationRoot,'package-artifacts',version,'split-release');
  const rows: Array<Record<string,string>>=[];
  function visit(file: string) {
    let stat: fs.Stats;
    try { stat=fs.lstatSync(file); } catch(error) {
      if((error as NodeJS.ErrnoException).code==='ENOENT'){rows.push({path:path.relative(base,file),type:'absent'});return;}
      throw error;
    }
    const relative=path.relative(base,file);
    if(stat.isSymbolicLink())rows.push({path:relative,type:'symlink',target:fs.readlinkSync(file)});
    else if(stat.isDirectory()){rows.push({path:relative,type:'directory'});for(const entry of fs.readdirSync(file).sort())visit(path.join(file,entry));}
    else if(stat.isFile())rows.push({path:relative,type:'file',sha256:sha256File(file)});
    else rows.push({path:relative,type:'other'});
  }
  visit(base);return rows;
}


const p01 = readJson(p01Path);
assert.equal(p01.result, "blocked");
assert.equal(p01.package_shape_result, "scoped-pass");
const boundaries = readJson(path.join(implementationRoot, "package-boundaries.json"));
const p01Before = p01SourceEnvelope();
assert.deepEqual(p01.source_envelope, p01Before);
const sourceBefore = sourceEnvelope();
const defaultBefore = defaultArchiveSnapshot();
run(process.execPath, ["scripts/run-toolchain.mjs", "tsx", "scripts/materialize-application-v1-examples.ts", "--check"], { cwd: implementationRoot });
run(process.execPath, ["scripts/materialize-package-boundaries.mjs", "--check"], { cwd: implementationRoot });

const runRoot = fs.mkdtempSync(path.join(os.tmpdir(), "alchlang-p02-clean-consumers-"));
subprocessEnv.npm_config_cache = path.join(runRoot, "npm-cache");
let reports: Json[] = [];
let archiveObservations: Json[] = [];
try {
  const archiveRoot = path.join(runRoot, "archives");
  fs.mkdirSync(archiveRoot);
  const domainPack = runJson("npm", ["pack", "--json", "--ignore-scripts", "--pack-destination", archiveRoot], { cwd: domainSpecRoot });
  const domainArchive = path.join(archiveRoot, domainPack[0].filename);
  const alchPlan = runJson(process.execPath, ["scripts/package-release.mjs", archiveRoot], { cwd: implementationRoot });
  const archives = Object.fromEntries(alchPlan.artifacts.map((artifact: Json) => [artifact.id, artifact.file]));
  archiveObservations = [
    { id: "domainspec-cli", ...inspectArchive(domainArchive) },
    ...alchPlan.artifacts.map((artifact: Json) => {
      assert.equal(path.dirname(artifact.file), archiveRoot);
      return { id: artifact.id, ...inspectArchive(artifact.file) };
    }),
  ];
  for (const observation of archiveObservations) {
    const expected = observation.id === "domainspec-cli" ? boundaries.domainspec_cli.expanded_files
      : boundaries.packages.find((item: Json) => item.id === observation.id).files;
    assert.deepEqual(observation.paths, expected);
  }
  assert.deepEqual(archiveObservations.slice(1).map(({ paths: _paths, ...rest }) => rest), p01.archive_observations);
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
  assert.deepEqual(p01SourceEnvelope(), p01Before, "P01 source drift during consumers");
  assert.deepEqual(sourceEnvelope(), sourceBefore, "selected P02 source drift during consumers");
  assert.deepEqual(defaultArchiveSnapshot(), defaultBefore, "default archives changed during consumers");
}

assert.equal(fs.existsSync(runRoot), false, "P02 run root must be disposed before reports are persisted");
const reportBindings = Object.fromEntries(reports.map(report => [report.language, {
  path: relative(path.join(evidenceRoot, `${report.language}.json`)),
  sha256: sha256Bytes(JSON.stringify(report, null, 2) + "\n"),
}]));
const qualification = {
  schema_version: "alchlang.p02-clean-consumers-qualification/v6-candidate",
  date: evidenceDate,
  task: "P02",
  result: "blocked",
  consumer_result: "pass",
  authority_effect: "none",
  source_envelope: sourceBefore,
  archive_observations: archiveObservations.map(({ paths: _paths, ...rest }) => rest),
  archive_content_algorithm: "sha256-json-sorted-path-size-sha256/v1",
  execution_controls: { selected_sources_before_after: "identical", default_archives_before_after: "identical", installed_realpaths_confined: true, checkout_override_environment_removed: true, measurement_stdout_only: true },
  supersedes_historical_qualification: binding(path.join(historicalEvidenceRoot, "qualification.json")),
  supersedes_previous_qualification: binding(previousPath),
  inherited_boundaries: {
    P01: { ...binding(p01Path), result: "blocked", package_shape_result: "scoped-pass" },
    O01: binding(path.join(planRoot, "O01-COMPLETION.md")),
  },
  bindings: {
    qualifier: binding(path.join(implementationRoot, "scripts/qualify-p02-clean-consumers-v6.ts")),
    historical_qualifier: binding(path.join(implementationRoot, "scripts/qualify-p02-clean-consumers.ts")),
    qualification_validator: binding(path.join(implementationRoot, "test/application-p02-qualification.test.ts")),
    example_materializer: binding(path.join(implementationRoot, "scripts/materialize-application-v1-examples.ts")),
    example_guide: binding(path.join(implementationRoot, "CLEAN-CONSUMER.md")),
    package_boundaries: binding(path.join(implementationRoot, "package-boundaries.json")),
    fixture_generator: binding(path.join(implementationRoot, "test/fixtures/application-whole-fixture.ts")),
    package_builder: binding(path.join(implementationRoot, "scripts/package-release.mjs")),
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
  claim_ceiling: "P02 lifecycle remains blocked by P01 v5/L3X. P02 clean installed-consumer construction evidence only; no candidate freeze, D65 admission, product approval, release admission, publication, deployment, production guarantee, or authority effect.",
  open_questions: ["P01/L3X lifecycle needs its own genuine execution evidence.", "P03 owns freezing the exact candidate and currentness validator."],
};
process.stdout.write(`${JSON.stringify({ qualification, reports }, null, 2)}\n`);

