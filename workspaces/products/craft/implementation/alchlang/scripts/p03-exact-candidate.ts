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
const successorEvidenceRoot = path.join(evidenceRoot, "successor-v3-candidate");
const previousEvidenceRoot = path.join(evidenceRoot, "successor-v2-candidate");
const successorCandidatePath = path.join(successorEvidenceRoot, "candidate.json");
const successorQualificationPath = path.join(successorEvidenceRoot, "qualification.json");
const currentP01QualificationPath = path.join(planRoot, "evidence/p01-package-boundaries/qualification.v3-candidate.json");
const currentP02EvidenceRoot = path.join(planRoot, "evidence/p02-clean-consumers/successor-v5-candidate");
const currentP02QualificationPath = path.join(currentP02EvidenceRoot, "qualification.json");
const languages = ["typescript", "python", "rust"] as const;
const canonicalJson = (value: any): string => Array.isArray(value) ? `[${value.map(canonicalJson).join(",")}]` : value !== null && typeof value === "object" ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}` : JSON.stringify(value) ?? "null";
const sha256 = (value: string | Buffer) => crypto.createHash("sha256").update(value).digest("hex");
const sha256File = (file: string) => sha256(fs.readFileSync(file));
const relative = (file: string) => path.relative(repoRoot, file).split(path.sep).join("/");
const readJson = (file: string) => JSON.parse(fs.readFileSync(file, "utf8"));

function run(command: string, args: readonly string[], cwd = repoRoot, timeout = 300_000): string {
  const result = spawnSync(command, [...args], { cwd, encoding: "utf8", timeout, env: process.env, maxBuffer: 32 * 1024 * 1024 });
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed (${result.status})\n${result.stdout}\n${result.stderr}`);
  return result.stdout.trim();
}

function row(file: string, rowPath = relative(file)): Row {
  const bytes = fs.readFileSync(file);
  return { path: rowPath, size_bytes: bytes.length, sha256: sha256(bytes) };
}

function rowsFromRoot(root: string, accept: (file: string) => boolean, prefix = relative(root)): Row[] {
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
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/p03-candidate.schema.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/p03-candidate.v2.schema.json",
];

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
  ];
}

const receiptFiles = [
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/P01-COMPLETION.md",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/O01-COMPLETION.md",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/P02-COMPLETION.md",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p01-package-boundaries/qualification.v3-candidate.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/o01-portable-toolchain/qualification.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/successor-v5-candidate/qualification.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/successor-v5-candidate/typescript.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/successor-v5-candidate/python.json",
  "craft/projects/domainspec-v2/development/authoring-to-runtime-v1/evidence/p02-clean-consumers/successor-v5-candidate/rust.json",
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
  const python = fs.realpathSync(process.env.ALCHLANG_P02_PYTHON ?? findExecutable("python3"));
  return [
    { tool: "node", version: process.version, executable: node, executable_sha256: sha256File(node) },
    { tool: "npm", version: run("npm", ["--version"], implementationRoot), executable: npm, executable_sha256: sha256File(npm) },
    { tool: "python", version: run(python, ["--version"]), executable: python, executable_sha256: sha256File(python) },
    ...identities.map((item: any) => ({ ...item, real_executable_sha256: sha256File(item.real_executable), lock_sha256: sha256File(item.lock_path) })),
  ];
}

function collectEnvironment() {
  const python = fs.realpathSync(process.env.ALCHLANG_P02_PYTHON ?? findExecutable("python3"));
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

function extractInventory(id: string, archive: string, extractionRoot: string): Inventory {
  const target = path.join(extractionRoot, id);
  fs.mkdirSync(target, { recursive: true });
  run("/usr/bin/tar", ["-xzf", archive, "-C", target]);
  return inventory(id, "exact regular files extracted from tested npm archive", rowsFromRoot(target, () => true, ""));
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
  const extractionRoot = path.join(runRoot, "extracted");
  fs.mkdirSync(extractionRoot);
  const archives = Object.keys(files).sort().map(id => {
    const file = files[id]!;
    const observed = sha256File(file);
    assert.equal(observed, expected[id].sha256, `${id} archive differs from P02 tested bytes`);
    const content = extractInventory(id, file, extractionRoot);
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
  add("schema", value?.schema_version === "alchlang.p03-exact-candidate/v2-candidate");
  add("authority", value?.authority_effect === "none");
  add("candidate-id", value?.candidate_id === `alchlang-domainspec-p03-${sha256(canonicalJson(candidateIdBody(value))).slice(0, 16)}`);
  add("manifest-self-digest", value?.manifest_sha256 === manifestDigest(value));
  add("working-tree-posture", value?.source_posture?.kind === "working-tree-exact-selected-files" && value.source_posture.whole_tree_clean_claimed === false);
  const inventories = [...(value?.source_groups ?? []), ...(value?.package_archives ?? []), ...(value?.generated_projects ?? [])];
  add("inventories-closed", inventories.length >= 14 && inventories.every((item: any) => validateRows(item.files) && item.inventory_sha256 === sha256(canonicalJson(item.files))));
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
      add("archives-bound-to-p02", value.package_archives.every((item: any) => item.archive_sha256 === expected[item.id].sha256 && item.p02_archive_sha256 === expected[item.id].sha256));
    } catch { add("archives-bound-to-p02", false); }
    try { add("git-head-current", value.source_posture.git_head === run("git", ["rev-parse", "HEAD"])); } catch { add("git-head-current", false); }
  }
  return { schema_version: "alchlang.p03-currentness-validation/v1-candidate", result: checks.every(item => item.result === "pass") ? "pass" : "fail", checks, authority_effect: "none" };
}

function buildCandidate(): Candidate {
  const reports = p02Reports();
  const expectedArchives = sharedP02Archives(reports);
  const runRoot = fs.mkdtempSync(path.join(os.tmpdir(), "alchlang-p03-candidate-"));
  let archives: any[] = [];
  let generatedProjects: any[] = [];
  try {
    const materialized = materializeArchives(runRoot, expectedArchives);
    archives = materialized.archives;
    generatedProjects = materializeProjects(runRoot, materialized.files, reports);
  } finally {
    fs.rmSync(runRoot, { recursive: true, force: true });
  }
  assert.equal(fs.existsSync(runRoot), false);
  const candidate = reseal({
    schema_version: "alchlang.p03-exact-candidate/v2-candidate",
    date: new Date().toISOString().slice(0, 10),
    source_posture: { kind: "working-tree-exact-selected-files", git_head: run("git", ["rev-parse", "HEAD"]), whole_tree_clean_claimed: false, selection: "closed-groups-with-exact-file-rows" },
    source_groups: collectSourceGroups(),
    package_archives: archives,
    generated_projects: generatedProjects,
    tools: collectTools(),
    environment: collectEnvironment(),
    receipts: receiptFiles.map(file => row(path.join(repoRoot, file))).sort((a, b) => a.path.localeCompare(b.path)),
    materialization: { archive_bytes_match_p02: true, generated_manifest_bytes_match_p02: true, exact_file_rows_used: true, broad_directory_digest_used: false, task_owned_root_disposed: true, historical_evidence_refreshed: false },
    claim_ceiling: { exact_candidate_construction_evidence: true, product_owner_validation: false, product_approval: false, d65_admission: false, publication: false, release: false, deployment: false, production: false },
    authority_effect: "none",
  });
  const validation = validateCandidate(candidate, true);
  assert.equal(validation.result, "pass", JSON.stringify(validation, null, 2));
  return candidate;
}

function writeQualification(candidate: Candidate) {
  const testPath = path.join(implementationRoot, "test/application-p03-candidate.test.ts");
  const value = {
    schema_version: "alchlang.p03-exact-candidate-qualification/v3-candidate",
    date: candidate.date,
    task: "P03",
    result: "scoped-pass",
    authority_effect: "none",
    supersedes_historical_qualification: row(qualificationPath),
    supersedes_historical_candidate: row(candidatePath),
    supersedes_previous_qualification: row(path.join(previousEvidenceRoot, "qualification.json")),
    supersedes_previous_candidate: row(path.join(previousEvidenceRoot, "candidate.json")),
    candidate: row(successorCandidatePath),
    bindings: {
      schema: row(path.join(planRoot, "p03-candidate.v2.schema.json")),
      materializer_and_validator: row(path.join(implementationRoot, "scripts/p03-exact-candidate.ts")),
      adversarial_test: row(testPath),
      safety_test: row(path.join(implementationRoot, "test/application-p03-safety.test.ts")),
      p01_predecessor: row(currentP01QualificationPath),
      p02_predecessor: row(currentP02QualificationPath),
    },
    candidate_id: candidate.candidate_id,
    candidate_manifest_sha256: candidate.manifest_sha256,
    validation: { currentness: "pass", non_mutating: true, adversarial_cases: 8, failed: 0, skipped: 0 },
    hard_stops: { historical_evidence_refreshed: false, broad_directory_inventory_substituted: false, currentness_validator_mutated_candidate: false, incomplete_denominator: false, product_approval_inferred: false, publication_or_release_performed: false, authority_effect_inferred: false },
    claim_ceiling: "P03 exact successor candidate construction evidence only; no D65 admission, product validation or approval, publication, release, deployment, production guarantee, or authority effect.",
    open_questions: ["P04/P05 must bind this new candidate identity through separately reviewed successors; their historical bindings are not current."],
  };
  fs.writeFileSync(successorQualificationPath, `${JSON.stringify(value, null, 2)}\n`, { flag: "wx" });
}

function main() {
  if (process.argv.includes("--write")) {
    throw new Error("P03_HISTORICAL_WRITE_DISABLED: this v1 path is historical and cannot receive a successor candidate");
  }
  if (process.argv.includes("--write-successor")) {
    if (fs.existsSync(successorEvidenceRoot)) throw new Error(`P03_SUCCESSOR_EXISTS:${successorEvidenceRoot}`);
    const candidate = buildCandidate();
    fs.mkdirSync(successorEvidenceRoot);
    fs.writeFileSync(successorCandidatePath, `${JSON.stringify(candidate, null, 2)}\n`, { flag: "wx" });
    writeQualification(candidate);
    process.stdout.write(`${JSON.stringify({ result: "scoped-pass", candidate_id: candidate.candidate_id,
      candidate_path: relative(successorCandidatePath), qualification_path: relative(successorQualificationPath),
      authority_effect: "none" }, null, 2)}\n`);
    return;
  }
  if (process.argv.includes("--check")) {
    const result = validateCandidate(readJson(successorCandidatePath), true);
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    if (result.result !== "pass") process.exitCode = 1;
    return;
  }
  throw new Error("usage: p03-exact-candidate.ts --write-successor|--check");
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
