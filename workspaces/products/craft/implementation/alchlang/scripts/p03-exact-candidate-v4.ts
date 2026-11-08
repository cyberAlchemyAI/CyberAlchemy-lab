#!/usr/bin/env node
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

type Row = { path: string; size_bytes: number; sha256: string };
type Inventory = { id: string; selector: string; files: Row[]; inventory_sha256: string };
type Candidate = Record<string, any>;

const implementationRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(implementationRoot, "../../../../../..");
const domainSpecRoot = path.join(repoRoot, "craft/projects/domainspec-v2/impl/cli");
const systemIntegrationRoot = path.join(repoRoot, "craft/projects/domainspec-v2/impl/system-integration");
const planRoot = path.join(repoRoot, "craft/projects/domainspec-v2/development/authoring-to-runtime-v1");
const evidenceRoot = path.join(planRoot, "evidence/p03-exact-candidate");
const candidatePath = path.join(evidenceRoot, "candidate.json");
const qualificationPath = path.join(evidenceRoot, "qualification.json");
const successorEvidenceRoot = path.join(evidenceRoot, "successor-v4-candidate");
const previousEvidenceRoot = path.join(evidenceRoot, "successor-v3-candidate");
const successorCandidatePath = path.join(successorEvidenceRoot, "candidate.json");
const successorQualificationPath = path.join(successorEvidenceRoot, "qualification.json");
const currentP01QualificationPath = path.join(planRoot, "evidence/p01-package-boundaries/qualification.v5-candidate.json");
const currentP02EvidenceRoot = path.join(planRoot, "evidence/p02-clean-consumers/successor-v6-candidate");
const currentP02QualificationPath = path.join(currentP02EvidenceRoot, "qualification.json");
const p02Qualification = () => readJson(currentP02QualificationPath);
const subprocessEnv = { ...process.env };
for (const key of ["ALCHLANG_DOMAINSPEC_PACKAGE_ROOT","NODE_PATH","NODE_OPTIONS","PYTHONPATH","PYTHONHOME","NPM_CONFIG_CACHE"]) delete subprocessEnv[key];
const languages = ["typescript", "python", "rust"] as const;
const canonicalJson = (value: any): string => Array.isArray(value) ? `[${value.map(canonicalJson).join(",")}]` : value !== null && typeof value === "object" ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}` : JSON.stringify(value) ?? "null";
const sha256 = (value: string | Buffer) => crypto.createHash("sha256").update(value).digest("hex");
const sha256File = (file: string) => sha256(fs.readFileSync(file));
const relative = (file: string) => path.relative(repoRoot, file).split(path.sep).join("/");
const readJson = (file: string) => JSON.parse(fs.readFileSync(file, "utf8"));

function run(command: string, args: readonly string[], cwd = repoRoot, timeout = 300_000, input?: string): string {
  const result = spawnSync(command, [...args], { cwd, encoding: "utf8", timeout, env: subprocessEnv, input, maxBuffer: 32 * 1024 * 1024 });
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed (${result.status})\n${result.stdout}\n${result.stderr}`);
  return result.stdout.trim();
}

function row(file: string, rowPath = relative(file)): Row {
  assert.equal(fs.lstatSync(file).isFile(), true, `P03_NON_REGULAR_FILE:${file}`);
  assert.equal(fs.realpathSync(file), file, `P03_SYMLINK_REJECTED:${file}`);
  const bytes = fs.readFileSync(file);
  return { path: rowPath, size_bytes: bytes.length, sha256: sha256(bytes) };
}

function rowsFromRoot(root: string, accept: (file: string) => boolean, prefix = relative(root)): Row[] {
  assert.equal(fs.realpathSync(root), root, `P03_SYMLINK_REJECTED:${root}`);
  const rows: Row[] = [];
  const visit = (directory: string, sub = "") => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const absolute = path.join(directory, entry.name);
      const child = sub ? `${sub}/${entry.name}` : entry.name;
      if (entry.isSymbolicLink()) throw new Error(`P03_SYMLINK_REJECTED:${relative(absolute)}`);
      if (entry.isDirectory()) visit(absolute, child);
      else if (entry.isFile() && accept(absolute)) rows.push(row(absolute, `${prefix}/${child}`));
      else if (!entry.isFile()) throw new Error(`P03_NON_REGULAR_FILE:${relative(absolute)}`);
    }
  };
  visit(root);
  return rows.sort((left, right) => left.path.localeCompare(right.path));
}

function inventory(id: string, selector: string, files: Row[]): Inventory {
  assert.ok(files.length > 0, `${id} must not be empty`);
  assert.equal(files.length, new Set(files.map(item => item.path)).size, `${id} duplicate paths`);
  assert.deepEqual(files.map(item => item.path), [...files.map(item => item.path)].sort((left, right) => left.localeCompare(right)), `${id} must be sorted`);
  return { id, selector, files, inventory_sha256: sha256(canonicalJson(files)) };
}

const explicitTools = [
  "language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/run-toolchain.mjs",
  "language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/materialize-package-boundaries.mjs",
  "language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/package-release.mjs",
  "language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/copy-event-templates.mjs",
  "language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/materialize-application-v1-examples.ts",
  "language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/qualify-p02-clean-consumers.ts",
  "language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/p03-exact-candidate.ts",
  "language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/p03-exact-candidate-v4.ts",
  "language/capabilities/alchlang/plans/general-compiler-v1/implementation/scripts/qualify-p02-clean-consumers-v6.ts",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/p03-candidate.schema.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/p03-candidate.v2.schema.json",
];


export function validatePredecessorSemantics(p01: Candidate, p02: Candidate) {
  assert.equal(p01.result,"blocked");
  assert.equal(p01.package_shape_result,"scoped-pass");
  assert.equal(p02.result,"blocked");
  assert.equal(p02.consumer_result,"pass");
  assert.equal(p01.authority_effect,"none");
  assert.equal(p02.authority_effect,"none");
  assert.equal(p01.inherited_boundary.result,"blocked");
  assert.deepEqual(p02.validation.clean_consumer_reports,{tests:3,passed:3,failed:0,skipped:0});
  assert.equal(p02.validation.check_lower_build_verify_native_scenario_inspection_cleanup,"pass");
  assert.equal(p02.validation.cross_language_application_graph_bytes,"identical");
  const p01Stops=["broad_directory_copy_used_as_allowlist","development_residue_packaged","checkout_only_declaration_import_present","missing_export_target","alchlang_archive_inventory_differs_from_allowlist","domainspec_cli_expanded_inventory_differs_from_allowlist","clean_consumer_claimed_before_p02","publication_or_release_performed","authority_effect_inferred"];
  const p02Stops=["undocumented_repair","weaker_language_path","checkout_link_or_fallback","owned_temporary_residue","publication_or_release_performed","product_approval_inferred","authority_effect_inferred"];
  assert.deepEqual(Object.keys(p01.hard_stops),p01Stops);
  assert.deepEqual(Object.keys(p02.hard_stops),p02Stops);
  assert.ok(Object.values(p01.hard_stops).every(v=>v===false));
  assert.ok(Object.values(p02.hard_stops).every(v=>v===false));
  assert.deepEqual(p02.archive_observations.map((a: any)=>a.id),["domainspec-cli","core","rust","local-host"]);
  assert.deepEqual(p02.archive_observations.slice(1),p01.archive_observations,"P03_P01_P02_ARCHIVE_CHAIN_MISMATCH");
  assert.deepEqual(Object.keys(p02.reports),[...languages]);
}

function predecessorPaths() {
  const p01 = readJson(currentP01QualificationPath);
  const boundaries = readJson(path.join(implementationRoot, "package-boundaries.json"));
  const p01Paths = [...new Set<string>([
    ...Object.values(p01.bindings).map((b: any) => b.path as string),
    p01.supersedes_previous_qualification.path, p01.inherited_boundary.path, p01.dag.path,
    ...["package.json","package-lock.json","tsconfig.json","tsconfig.build.json","scripts/run-toolchain.mjs","scripts/copy-event-templates.mjs"].map(f => relative(path.join(implementationRoot,f))),
    "tools/toolchain/run","tools/toolchain/lock.json",relative(path.join(domainSpecRoot,"package-lock.json")),
    ...boundaries.packages.flatMap((p: any) => p.files.map((f: string) => relative(path.join(implementationRoot,f)))),
    ...boundaries.domainspec_cli.expanded_files.map((f: string) => boundaries.domainspec_cli.package_root + "/" + f),
  ])];
  const p02 = p02Qualification();
  validatePredecessorSemantics(p01,p02);
  const p02Paths = [...new Set<string>([...p01Paths,relative(currentP01QualificationPath),
    p02.supersedes_previous_qualification.path,p02.supersedes_historical_qualification.path,
    p02.inherited_boundaries.O01.path,
    ...["scripts/qualify-p02-clean-consumers-v6.ts","scripts/qualify-p02-clean-consumers.ts","test/application-p02-qualification.test.ts","scripts/materialize-application-v1-examples.ts","CLEAN-CONSUMER.md","test/fixtures/application-whole-fixture.ts"].map(f => relative(path.join(implementationRoot,f))),
  ])];
  const envelope = (paths: string[], schema: string) => {
    const rows = paths.sort().map(p => ({path:p,sha256:row(path.join(repoRoot,p)).sha256}));
    return {schema_version:schema,algorithm:"sha256-json-sorted-repository-path-file-sha256/v1",file_count:rows.length,sha256:sha256(JSON.stringify(rows))};
  };
  assert.equal(p01.result,"blocked");
  assert.equal(p01.package_shape_result,"scoped-pass");
  assert.equal(p02.result,"blocked");
  assert.equal(p02.consumer_result,"pass");
  assert.equal(p01.authority_effect,"none");
  assert.equal(p02.authority_effect,"none");
  assert.equal(p01.inherited_boundary.result,"blocked");
  assert.equal(readJson(path.join(repoRoot,p01.inherited_boundary.path)).result,"blocked");
  assert.deepEqual(p02.validation.clean_consumer_reports,{tests:3,passed:3,failed:0,skipped:0});
  assert.equal(p02.validation.check_lower_build_verify_native_scenario_inspection_cleanup,"pass");
  assert.equal(p02.validation.cross_language_application_graph_bytes,"identical");
  assert.ok(Object.values(p01.hard_stops).every(v=>v===false));
  assert.ok(Object.values(p02.hard_stops).every(v=>v===false));
  assert.deepEqual(p02.archive_observations.map((a: any)=>a.id),["domainspec-cli","core","rust","local-host"]);
  assert.deepEqual(p02.inherited_boundaries.P01,{path:relative(currentP01QualificationPath),sha256:sha256File(currentP01QualificationPath),result:"blocked",package_shape_result:"scoped-pass"});
  assert.deepEqual(envelope(p01Paths,"alchlang.p01-source-envelope/v1-candidate"),p01.source_envelope);
  assert.deepEqual(envelope(p02Paths,"alchlang.p02-source-envelope/v1-candidate"),p02.source_envelope);
  for (const [language,binding] of Object.entries(p02.reports) as Array<[string,any]>) {
    assert.ok(languages.includes(language as any));
    assert.equal(binding.path,relative(path.join(currentP02EvidenceRoot,language+".json")));
    assert.equal(binding.sha256,sha256File(path.join(repoRoot,binding.path)));
    const report=readJson(path.join(repoRoot,binding.path));
    assert.equal(report.language,language);
    assert.equal(report.result,"pass");
    assert.equal(report.authority_effect,"none");
    assert.equal(report.installed_outside_checkout,true);
    for(const flag of ["publication","release","deployment"])assert.equal(report[flag],false);
    assert.equal(report.application.native.native_compilation,"pass");
    assert.deepEqual(report.application.native.scenario,{language,startup:language==="typescript"?"http-listener":language==="python"?"asgi-http-listener":"axum-http-listener",invalid_status:401,valid_status:202,handler_invocations:1,result:"pass"});
    assert.ok(Object.values(report.cleanup).every(v=>v===true));
    assert.equal(report.application.check.status,"valid");
    assert.equal(report.application.build.status,"built");
    for(const stage of ["verify_before","verify_after"]) {
      assert.equal(report.application[stage].status,"verified");
      assert.equal(report.application[stage].manifest_sha256,report.application.build.manifest_sha256);
    }
  }
  assert.deepEqual(Object.keys(p02.reports),[...languages]);
  return p02Paths.map(p => row(path.join(repoRoot,p))).sort((a,b) => a.path.localeCompare(b.path));
}

function collectSourceGroups(): Inventory[] {
  const alchSource = path.join(implementationRoot, "src");
  const alchTests = path.join(implementationRoot, "test");
  const domainSource = path.join(domainSpecRoot, "src");
  const domainTools = path.join(domainSpecRoot, "tools");
  const rootFiles = ["package.json", "package-lock.json", "tsconfig.json", "tsconfig.build.json", "package-boundaries.json", "CLEAN-CONSUMER.md", "PACKAGE-BOUNDARIES.md"].map(name => row(path.join(implementationRoot, name))).sort((a, b) => a.path.localeCompare(b.path));
  const planFiles = ["IMPLEMENTATION-DAG.md", "EXECUTION-DAG.json", "validate_dag.py", "P01-COMPLETION.md", "O01-COMPLETION.md", "P02-COMPLETION.md"].map(name => row(path.join(planRoot, name))).sort((a, b) => a.path.localeCompare(b.path));
  return [
    inventory("alchlang-source", "implementation/src/**/*.ts plus exact root build contracts", [...rowsFromRoot(alchSource, file => file.endsWith(".ts")), ...rootFiles].sort((a, b) => a.path.localeCompare(b.path))),
    inventory("alchlang-tests", "implementation/test/**/*.ts", rowsFromRoot(alchTests, file => file.endsWith(".ts"))),
    inventory("candidate-tools", "closed explicit construction and validation tool list", explicitTools.map(file => row(path.join(repoRoot, file))).sort((a, b) => a.path.localeCompare(b.path))),
    inventory("domainspec-source", "cli/src/**/*.ts plus exact root build contracts", [...rowsFromRoot(domainSource, file => file.endsWith(".ts")), ...["package.json", "package-lock.json", "tsconfig.json"].map(name => row(path.join(domainSpecRoot, name)))].sort((a, b) => a.path.localeCompare(b.path))),
    inventory("domainspec-tools", "cli/tools exact regular-file inventory", rowsFromRoot(domainTools, () => true)),
    inventory("domainspec-system-integration", "system-integration exact regular-file inventory", rowsFromRoot(systemIntegrationRoot, () => true)),
    inventory("plan-contract", "closed exact P01-O01-P02-P03 plan and predecessor list", planFiles),
    inventory("selected-consumer-envelope", "exact reconstructed P01 v5 and P02 v6 selected file rows", predecessorPaths()),
  ];
}

const receiptFiles = [
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/P01-COMPLETION.md",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/O01-COMPLETION.md",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/P02-COMPLETION.md",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p01-package-boundaries/qualification.v5-candidate.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/o01-portable-toolchain/qualification.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/successor-v6-candidate/qualification.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/successor-v6-candidate/typescript.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/successor-v6-candidate/python.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/successor-v6-candidate/rust.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p03-exact-candidate/successor-v3-candidate/candidate.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p03-exact-candidate/successor-v3-candidate/qualification.json",
];

function findExecutable(name: string): string {
  const found = (process.env.PATH ?? "").split(path.delimiter).map(directory => path.join(directory, name)).find(file => fs.existsSync(file));
  if (!found) throw new Error(`P03_TOOL_MISSING:${name}`);
  return fs.realpathSync(found);
}

function collectTools(): any[] {
  const identities = JSON.parse(run(process.execPath, ["scripts/run-toolchain.mjs", "--identity-all"], implementationRoot));
  const node = fs.realpathSync(process.execPath);
  const npm = findExecutable("npm");
  const python = fs.realpathSync(findExecutable("python3"));
  return [
    { tool: "node", version: process.version, executable: node, executable_sha256: sha256File(node) },
    { tool: "npm", version: run("npm", ["--version"], implementationRoot), executable: npm, executable_sha256: sha256File(npm) },
    { tool: "python", version: run(python, ["--version"]), executable: python, executable_sha256: sha256File(python) },
    ...identities.map((item: any) => ({ ...item, real_executable_sha256: sha256File(item.real_executable), lock_sha256: sha256File(item.lock_path) })),
  ];
}

function collectEnvironment() {
  const python = fs.realpathSync(findExecutable("python3"));
  return {
    platform: process.platform,
    architecture: process.arch,
    os_release: os.release(),
    node: process.version,
    npm: run("npm", ["--version"], implementationRoot),
    python: run(python, ["--version"]),
    rust_lock_sha256: sha256File(path.join(repoRoot, "tools/toolchain/lock.json")),
  };
}

function p02Reports() {
  return currentP02Reports();
}

function currentP02Reports() {
  return Object.fromEntries(languages.map(language => [language, readJson(path.join(currentP02EvidenceRoot, `${language}.json`))]));
}

export function selectedPredecessorCheck(value: Candidate) {
  const required = [currentP01QualificationPath, currentP02QualificationPath,
    ...languages.map(language => path.join(currentP02EvidenceRoot, `${language}.json`))]
    .map(file => row(file));
  const receipts = new Map((value?.receipts ?? []).map((item: Row) => [item.path, item]));
  const missingOrStale = required.filter(item => canonicalJson(receipts.get(item.path)) !== canonicalJson(item));
  const expected = sharedP02Archives(currentP02Reports());
  const archiveMismatch = (value?.package_archives ?? []).filter((item: any) => item.archive_sha256 !== expected[item.id]?.sha256 || item.p02_archive_sha256 !== expected[item.id]?.sha256);
  return { result: missingOrStale.length === 0 && archiveMismatch.length === 0 ? "pass" : "fail", missing_or_stale_receipts: missingOrStale.map(item => item.path), mismatched_archives: archiveMismatch.map((item: any) => item.id) };
}

function sharedP02Archives(reports: Record<string, any>) {
  const expected = reports.typescript.package_archives;
  for (const language of languages) assert.deepEqual(reports[language].package_archives, expected, `P02 archive set differs for ${language}`);
  return expected;
}

export function inspectArchive(archive: string) {
  const script = [
    'import gzip,hashlib,io,json,os,sys,tarfile',
    'archive=sys.argv[1]',
    "assert os.path.getsize(archive)<=64*1024*1024, 'P03_ARCHIVE_SIZE'",
    'with gzip.open(archive,"rb") as compressed: raw=compressed.read(256*1024*1024+1)',
    "assert len(raw)<=256*1024*1024, 'P03_ARCHIVE_TAR_SIZE'",
    'rows=[];seen=set();total=0',
    'with tarfile.open(fileobj=io.BytesIO(raw),mode="r:") as stream:',
    ' for member in stream:',
    "  assert len(rows)<10000, 'P03_ARCHIVE_MEMBER_COUNT'",
    "  assert member.isfile(), 'P03_ARCHIVE_NONREGULAR'",
    "  assert member.name.startswith('package/'), 'P03_ARCHIVE_PATH'",
    "  relative=member.name[len('package/'):]",
    "  assert relative and chr(92) not in relative and all(p not in ('','.','..') for p in relative.split('/')), 'P03_ARCHIVE_PATH'",
    "  assert relative not in seen, 'P03_ARCHIVE_DUPLICATE'",
    "  assert 0<=member.size<=32*1024*1024, 'P03_ARCHIVE_MEMBER_SIZE'",
    '  total+=member.size',
    "  assert total<=256*1024*1024, 'P03_ARCHIVE_UNCOMPRESSED_SIZE'",
    '  seen.add(relative)',
    '  handle=stream.extractfile(member)',
    "  assert handle is not None, 'P03_ARCHIVE_CONTENT'",
    '  data=handle.read(member.size+1)',
    "  assert len(data)==member.size, 'P03_ARCHIVE_CONTENT'",
    "  rows.append({'path':relative,'size_bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})",
    "rows.sort(key=lambda row:row['path'])",
    "print(json.dumps({'files':rows}))",
  ].join("\n");
  return JSON.parse(run("python3",["-I","-c",script,archive],repoRoot,30000)).files as Row[];
}
function archiveContentDigest(files: Row[]) {
  const rows = files.map(item => {
    assert.ok(item.path.startsWith("package/"));
    assert.equal(path.isAbsolute(item.path),false);
    return {...item,path:item.path.slice("package/".length)};
  })
    .sort((a,b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
  return sha256(JSON.stringify(rows));
}
function expectedArchiveObservations() {
  return Object.fromEntries(p02Qualification().archive_observations.map((item: any) => [item.id==="domainspec-cli"?"domainspec_cli":item.id,item]));
}

function materializeArchives(runRoot: string, expected: any) {
  const archiveRoot = path.join(runRoot, "archives");
  fs.mkdirSync(archiveRoot);
  const domainPack = JSON.parse(run("npm", ["pack", "--json", "--ignore-scripts", "--pack-destination", archiveRoot], domainSpecRoot));
  const domainArchive = path.join(archiveRoot, domainPack[0].filename);
  const alch = JSON.parse(run(process.execPath, ["scripts/package-release.mjs", archiveRoot], implementationRoot));
  const files: Record<string, string> = { domainspec_cli: domainArchive, ...Object.fromEntries(alch.artifacts.map((item: any) => [item.id, item.file])) };
  const names: Record<string, string> = { domainspec_cli: "@domainspec-v2/cli", core: "@cyberalchemy/alchlang", rust: "@cyberalchemy/alchlang-rust", "local-host": "@cyberalchemy/alchlang-local-host" };
  const versions: Record<string, string> = { domainspec_cli: "1.0.0", core: alch.version, rust: alch.version, "local-host": alch.version };
  const observations = expectedArchiveObservations();
  const boundaries = readJson(path.join(implementationRoot,"package-boundaries.json"));
  const archives = Object.keys(files).sort().map(id => {
    const file = files[id]!;
    const observed = sha256File(file);
    assert.equal(observed, expected[id].sha256, `${id} archive differs from P02 tested bytes`);
    assert.equal(path.dirname(file),archiveRoot,"archive must remain under owned root");
    const rows = inspectArchive(file);
    const paths = rows.map(item => item.path);
    const allowlist = id==="domainspec_cli" ? boundaries.domainspec_cli.expanded_files : boundaries.packages.find((p: any) => p.id===id).files;
    assert.deepEqual(paths,allowlist);
    const content = inventory(id,"exact relative regular files inspected in memory from tested npm archive",rows.map(item => ({...item,path:"package/"+item.path})).sort((a,b) => a.path.localeCompare(b.path)));
    assert.equal(content.files.length,observations[id].entry_count);
    assert.equal(archiveContentDigest(content.files),observations[id].content_manifest_sha256);
    assert.equal(fs.statSync(file).size,observations[id].size_bytes);
    assert.equal(observed,observations[id].archive_sha256);
    return { ...content, name: names[id], version: versions[id], archive_sha256: observed, archive_size_bytes: fs.statSync(file).size, p02_archive_sha256: expected[id].sha256 };
  });
  return { files, archives };
}

function materializeProjects(runRoot: string, archives: Record<string, string>, reports: Record<string, any>) {
  const archiveSetSha256 = sha256(canonicalJson(Object.fromEntries(Object.entries(archives).sort().map(([id, file]) => [id, sha256File(file)]))));
  return languages.map(language => {
    const consumer = path.join(runRoot, "consumers", language);
    fs.mkdirSync(consumer, { recursive: true });
    fs.writeFileSync(path.join(consumer, "package.json"), '{"private":true,"type":"module"}\n');
    const install = [archives.domainspec_cli, archives.core];
    if (language === "rust") install.push(archives.rust);
    run("npm", ["install", "--offline", "--ignore-scripts", "--no-audit", "--no-fund", ...install], consumer);
    for (const name of ["@domainspec-v2/cli","@cyberalchemy/alchlang",...(language==="rust"?["@cyberalchemy/alchlang-rust"]:[])]) {
      const installed = path.join(consumer,"node_modules",...name.split("/"));
      assert.equal(fs.realpathSync(installed),installed,"installed package must not be linked");
      assert.equal(fs.lstatSync(installed).isDirectory(),true);
      assert.ok(installed.startsWith(consumer+path.sep));
      assert.ok(!installed.startsWith(repoRoot+path.sep));
      assert.equal(readJson(path.join(installed,"package.json")).name,name);
    }
    const core = path.join(consumer, "node_modules/@cyberalchemy/alchlang");
    const source = path.join(core, `examples/application-v1/${language}/commerce.alch`);
    const target = path.join(consumer, "generated");
    const cli = path.join(consumer, "node_modules/.bin/alchlang");
    const built = JSON.parse(run(cli, ["build", source, "--out", target], consumer));
    const verified = JSON.parse(run(cli, ["verify", source, "--out", target], consumer));
    assert.equal(built.status, "built");
    assert.equal(verified.status, "verified");
    assert.equal(built.manifest_sha256, reports[language].application.build.manifest_sha256, `${language} build differs from P02`);
    assert.equal(verified.manifest_sha256, built.manifest_sha256);
    for (const observed of Object.values(reports[language].application.inspection.files) as any[]) {
      assert.equal(sha256File(path.join(target,observed.relative_path)),observed.sha256,`${language} P02 artifact join`);
    }
    const project = inventory(language, "exact installed application-v1 generated project files", rowsFromRoot(target, () => true, "generated"));
    return { ...project, language, build_manifest_sha256: built.manifest_sha256, p02_build_manifest_sha256: reports[language].application.build.manifest_sha256, archive_set_sha256: archiveSetSha256 };
  });
}

function candidateIdBody(value: Candidate) {
  const body = structuredClone(value);
  delete body.candidate_id;
  delete body.manifest_sha256;
  return body;
}

function manifestDigest(value: Candidate) {
  const body = structuredClone(value);
  delete body.manifest_sha256;
  return sha256(canonicalJson(body));
}

function reseal(value: Candidate): Candidate {
  const candidate = structuredClone(value);
  delete candidate.candidate_id;
  delete candidate.manifest_sha256;
  candidate.candidate_id = `alchlang-domainspec-p03-${sha256(canonicalJson(candidate)).slice(0, 16)}`;
  candidate.manifest_sha256 = manifestDigest(candidate);
  return candidate;
}

function validateRows(files: Row[]): boolean {
  return Array.isArray(files) && files.length > 0 && files.length === new Set(files.map(item => item.path)).size
    && canonicalJson(files.map(item => item.path)) === canonicalJson(files.map(item => item.path).sort((left, right) => left.localeCompare(right)))
    && files.every(item => typeof item.path === "string" && item.path.length > 0 && Number.isInteger(item.size_bytes) && item.size_bytes >= 0 && /^[a-f0-9]{64}$/.test(item.sha256));
}

export function validateCandidate(value: Candidate, checkCurrent = true) {
  const checks: Array<{ id: string; result: "pass" | "fail" }> = [];
  const add = (id: string, pass: boolean) => checks.push({ id, result: pass ? "pass" : "fail" });
  try {
    run("python3",["-I","-c","import json,jsonschema,sys;jsonschema.Draft202012Validator(json.load(open(sys.argv[1]))).validate(json.load(sys.stdin))",path.join(planRoot,"p03-candidate.v2.schema.json")],repoRoot,30000,JSON.stringify(value));
    add("schema",true);
  } catch { add("schema",false); }
  add("authority", value?.authority_effect === "none");
  add("candidate-id", value?.candidate_id === `alchlang-domainspec-p03-${sha256(canonicalJson(candidateIdBody(value))).slice(0, 16)}`);
  add("manifest-self-digest", value?.manifest_sha256 === manifestDigest(value));
  add("working-tree-posture", value?.source_posture?.kind === "working-tree-exact-selected-files" && value.source_posture.whole_tree_clean_claimed === false);
  const inventories = [...(value?.source_groups ?? []), ...(value?.package_archives ?? []), ...(value?.generated_projects ?? [])];
  add("inventories-closed", inventories.length === 15 && inventories.every((item: any) => validateRows(item.files) && item.inventory_sha256 === sha256(canonicalJson(item.files))));
  add("source-denominator",canonicalJson(value?.source_groups?.map((i: any) => i.id))===canonicalJson(["alchlang-source","alchlang-tests","candidate-tools","domainspec-source","domainspec-tools","domainspec-system-integration","plan-contract","selected-consumer-envelope"]));
  add("archive-denominator", canonicalJson(value?.package_archives?.map((item: any) => item.id)) === canonicalJson(["core", "domainspec_cli", "local-host", "rust"]));
  add("language-denominator", canonicalJson(value?.generated_projects?.map((item: any) => item.language)) === canonicalJson(languages));
  add("materialization-cleanup", value?.materialization?.task_owned_root_disposed === true && value?.materialization?.historical_evidence_refreshed === false);
  add("claim-ceiling", canonicalJson(value?.claim_ceiling) === canonicalJson({ exact_candidate_construction_evidence: true, product_owner_validation: false, product_approval: false, d65_admission: false, publication: false, release: false, deployment: false, production: false }));
  if (checkCurrent) {
    try { add("selected-successor-predecessors", selectedPredecessorCheck(value).result === "pass"); } catch { add("selected-successor-predecessors", false); }
    try { add("source-current", canonicalJson(value.source_groups) === canonicalJson(collectSourceGroups())); } catch { add("source-current", false); }
    try { add("receipts-current", canonicalJson(value.receipts) === canonicalJson(receiptFiles.map(file => row(path.join(repoRoot, file))).sort((a, b) => a.path.localeCompare(b.path)))); } catch { add("receipts-current", false); }
    try { add("tools-current", canonicalJson(value.tools) === canonicalJson(collectTools())); } catch { add("tools-current", false); }
    try { add("environment-current", canonicalJson(value.environment) === canonicalJson(collectEnvironment())); } catch { add("environment-current", false); }
    try {
      const expected = sharedP02Archives(p02Reports());
      const observations = expectedArchiveObservations();
      add("archives-bound-to-p02",value.package_archives.every((item: any) =>
        item.archive_sha256===expected[item.id].sha256 && item.p02_archive_sha256===expected[item.id].sha256 &&
        item.archive_size_bytes===observations[item.id].size_bytes && item.files.length===observations[item.id].entry_count &&
        archiveContentDigest(item.files)===observations[item.id].content_manifest_sha256 &&
        item.name===expected[item.id].name && item.version===(item.id==="domainspec_cli"?"1.0.0":readJson(path.join(implementationRoot,"package.json")).version)));
      const archiveSet = sha256(canonicalJson(Object.fromEntries(value.package_archives.map((a: any) => [a.id,a.archive_sha256]))));
      add("generated-p02-joins",value.generated_projects.every((project: any) => {
        const report = p02Reports()[project.language];
        return project.id===project.language && project.archive_set_sha256===archiveSet &&
          project.build_manifest_sha256===report.application.build.manifest_sha256 &&
          project.p02_build_manifest_sha256===report.application.build.manifest_sha256 &&
          Object.values(report.application.inspection.files).every((observed: any) =>
            project.files.find((f: any) => f.path==="generated/"+observed.relative_path)?.sha256===observed.sha256);
      }));
    } catch { add("archives-bound-to-p02", false); add("generated-p02-joins",false); }
    try { add("git-head-current", value.source_posture.git_head === run("git", ["rev-parse", "HEAD"])); } catch { add("git-head-current", false); }
  }
  return { schema_version: "alchlang.p03-currentness-validation/v1-candidate", result: checks.every(item => item.result === "pass") ? "pass" : "fail", checks, artifact_replay_performed: false, authority_effect: "none" };
}


function defaultArchiveSnapshot() {
  const base = path.join(implementationRoot,"package-artifacts",readJson(path.join(implementationRoot,"package.json")).version,"split-release");
  const rows: any[] = [];
  function visit(file: string) {
    let stat: fs.Stats;
    try { stat=fs.lstatSync(file); } catch(error) {
      if((error as NodeJS.ErrnoException).code==="ENOENT"){rows.push({path:path.relative(base,file),type:"absent"});return;}
      throw error;
    }
    const relative=path.relative(base,file);
    if(stat.isSymbolicLink())rows.push({path:relative,type:"symlink",target:fs.readlinkSync(file)});
    else if(stat.isDirectory()){rows.push({path:relative,type:"directory"});for(const name of fs.readdirSync(file).sort())visit(path.join(file,name));}
    else if(stat.isFile())rows.push({path:relative,type:"file",sha256:sha256File(file)});
    else throw Error("P03_DEFAULT_NONREGULAR:"+file);
  }
  visit(base);return rows;
}
function custody() {
  return {source:collectSourceGroups(),receipts:receiptFiles.map(f => row(path.join(repoRoot,f))).sort((a,b) => a.path.localeCompare(b.path)),
    tools:collectTools(),environment:collectEnvironment(),git_head:run("git",["rev-parse","HEAD"]),default_archives:defaultArchiveSnapshot()};
}
export function compareArtifactReplay(candidate: Candidate, measured: Candidate) {
  assert.deepEqual(candidate,measured,"P03_FULL_ARTIFACT_REPLAY_MISMATCH");
}

export function buildCandidate(date = new Date().toISOString().slice(0,10)): Candidate {
  const before = custody();
  const reports = p02Reports();
  const expectedArchives = sharedP02Archives(reports);
  const runRoot = fs.mkdtempSync(path.join(os.tmpdir(), "alchlang-p03-candidate-"));
  subprocessEnv.npm_config_cache = path.join(runRoot,"npm-cache");
  let archives: any[] = [];
  let generatedProjects: any[] = [];
  try {
    const materialized = materializeArchives(runRoot, expectedArchives);
    archives = materialized.archives;
    generatedProjects = materializeProjects(runRoot, materialized.files, reports);
  } finally {
    fs.rmSync(runRoot, { recursive: true, force: true });
    delete subprocessEnv.npm_config_cache;
    assert.deepEqual(custody(),before,"P03_SELECTED_CUSTODY_DRIFT");
  }
  assert.equal(fs.existsSync(runRoot), false);
  const candidate = reseal({
    schema_version: "alchlang.p03-exact-candidate/v2-candidate",
    date,
    source_posture: { kind: "working-tree-exact-selected-files", git_head: run("git", ["rev-parse", "HEAD"]), whole_tree_clean_claimed: false, selection: "closed-groups-with-exact-file-rows" },
    source_groups: before.source,
    package_archives: archives,
    generated_projects: generatedProjects,
    tools: before.tools,
    environment: before.environment,
    receipts: before.receipts,
    materialization: { archive_bytes_match_p02: true, generated_manifest_bytes_match_p02: true, exact_file_rows_used: true, broad_directory_digest_used: false, task_owned_root_disposed: true, historical_evidence_refreshed: false },
    claim_ceiling: { exact_candidate_construction_evidence: true, product_owner_validation: false, product_approval: false, d65_admission: false, publication: false, release: false, deployment: false, production: false },
    authority_effect: "none",
  });
  const validation = validateCandidate(candidate, true);
  assert.equal(validation.result, "pass", JSON.stringify(validation, null, 2));
  return candidate;
}

export function createQualification(candidate: Candidate) {
  const testPath = path.join(implementationRoot, "test/application-p03-candidate.test.ts");
  const value = {
    schema_version: "alchlang.p03-exact-candidate-qualification/v4-candidate",
    date: candidate.date,
    task: "P03",
    result: "blocked",
    construction_result: "scoped-pass",
    inherited_boundaries: { P01: { ...row(currentP01QualificationPath), result:"blocked", package_shape_result:"scoped-pass" }, P02: { ...row(currentP02QualificationPath), result:"blocked", consumer_result:"pass" } },
    authority_effect: "none",
    supersedes_historical_qualification: row(qualificationPath),
    supersedes_historical_candidate: row(candidatePath),
    supersedes_previous_qualification: row(path.join(previousEvidenceRoot, "qualification.json")),
    supersedes_previous_candidate: row(path.join(previousEvidenceRoot, "candidate.json")),
    candidate: {path:relative(successorCandidatePath),size_bytes:Buffer.byteLength(JSON.stringify(candidate,null,2)+"\n"),sha256:sha256(JSON.stringify(candidate,null,2)+"\n")},
    bindings: {
      schema: row(path.join(planRoot, "p03-candidate.v2.schema.json")),
      materializer_and_validator: row(path.join(implementationRoot, "scripts/p03-exact-candidate-v4.ts")),
      historical_materializer: row(path.join(implementationRoot,"scripts/p03-exact-candidate.ts")),
      adversarial_test: row(testPath),
      safety_test: row(path.join(implementationRoot, "test/application-p03-safety.test.ts")),
      p01_predecessor: row(currentP01QualificationPath),
      p02_predecessor: row(currentP02QualificationPath),
    },
    candidate_id: candidate.candidate_id,
    candidate_manifest_sha256: candidate.manifest_sha256,
    validation: { currentness:"pass", archives_measured:4, generated_projects_measured:3, exact_source_groups:8, selected_consumer_rows:predecessorPaths().length, selected_custody_before_after:"identical", default_archives_before_after:"identical", task_owned_root_disposed:true, measurement_stdout_only:true },
    hard_stops: { historical_evidence_refreshed: false, broad_directory_inventory_substituted: false, currentness_validator_mutated_candidate: false, incomplete_denominator: false, product_approval_inferred: false, publication_or_release_performed: false, authority_effect_inferred: false },
    claim_ceiling: "P03 lifecycle remains blocked by P01 v5/P02 v6/L3X. Exact successor candidate construction evidence only; no completed lifecycle freeze, D65 admission, product validation or approval, publication, release, deployment, production guarantee, or authority effect.",
    open_questions: ["Genuine upstream E03/L3X execution evidence remains required before P03 lifecycle completion.","Full regression, finding closure and independently reviewed P04/P05 successors remain outstanding.","Cheap currentness is not a full artifact replay; use --replay for exact regenerated row comparison."],
  };
  return value;
}

export function validateQualification(value: Candidate, candidate: Candidate) {
  try { assert.deepEqual(value,createQualification(candidate)); return {result:"pass"}; }
  catch { return {result:"fail"}; }
}

function main() {
  const argv = process.argv.slice(2);
  if (argv.some(a => a.startsWith("--write"))) throw Error("P03_HISTORICAL_WRITE_DISABLED: v4 measurement is stdout-only");
  if (argv.length!==1 || !["--measure","--check","--replay"].includes(argv[0]!)) throw Error("usage: p03-exact-candidate-v4.ts --measure|--check|--replay");
  if (argv[0]==="--measure") {
    const candidate=buildCandidate();
    process.stdout.write(JSON.stringify({candidate,qualification:createQualification(candidate)},null,2)+"\n");return;
  }
  const saved=readJson(successorCandidatePath);
  if(argv[0]==="--replay") {
    const measured=buildCandidate(saved.date);
    compareArtifactReplay(saved,measured);
    assert.deepEqual(readJson(successorQualificationPath),createQualification(measured),"P03_QUALIFICATION_REPLAY_MISMATCH");
    process.stdout.write(JSON.stringify({result:"pass",artifact_replay_performed:true,candidate_id:saved.candidate_id,
      source_rows:saved.source_groups.reduce((n: number,g: any)=>n+g.files.length,0),
      archive_rows:saved.package_archives.reduce((n: number,g: any)=>n+g.files.length,0),
      generated_rows:saved.generated_projects.reduce((n: number,g: any)=>n+g.files.length,0),
      lifecycle_result:"blocked",authority_effect:"none"},null,2)+"\n");return;
  }
  const result=validateCandidate(saved,true);
  result.checks.push({id:"qualification-current",result:validateQualification(readJson(successorQualificationPath),saved).result as "pass"|"fail"});
  result.result=result.checks.every(c => c.result==="pass")?"pass":"fail";
  process.stdout.write(JSON.stringify(result,null,2)+"\n");
  if(result.result!=="pass")process.exitCode=1;
}
if (process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) main();

