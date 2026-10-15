#!/usr/bin/env node
import {createHash} from "node:crypto";
import {spawnSync} from "node:child_process";
import {mkdtempSync, readFileSync, rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join, resolve} from "node:path";
import {pathToFileURL} from "node:url";

const packageRoot = resolve(import.meta.dirname, "..");
const repositoryRoot = resolve(packageRoot, "../..");
const sourcePath = resolve(packageRoot, "alch/integration/define-integration.alch");
const generatedRoot = resolve(packageRoot, "generated/define-integration");
const compilerPath = resolve(repositoryRoot, "language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js");
const entries = {
  StageDependency: "stage-dependency.alch",
  StageResponse: "stage-response.alch",
  StageReadiness: "stage-readiness.alch",
  StageHandoff: "stage-handoff.alch",
};

const bytes = (path) => readFileSync(path);
const json = (path) => JSON.parse(bytes(path).toString("utf8"));
const sha256 = (value) => createHash("sha256").update(value).digest("hex");
const requireCheck = (condition, code) => { if (!condition) throw new Error(code); };

function verifyInventory(root, manifest) {
  for (const [relativePath, expected] of Object.entries(manifest.files)) {
    requireCheck(sha256(bytes(resolve(root, relativePath))) === expected, `define-stage.generated-drift:${relativePath}`);
  }
}

async function verify() {
  const source = bytes(sourcePath);
  const manifest = json(resolve(generatedRoot, "manifest.json"));
  requireCheck(manifest.schema_version === "alchlang.service-build/v1", "define-stage.manifest-version");
  requireCheck(manifest.source_sha256 === sha256(source), "define-stage.source-drift");
  requireCheck(JSON.stringify(manifest.entries) === JSON.stringify(Object.keys(entries)), "define-stage.entry-drift");
  requireCheck(bytes(resolve(generatedRoot, "provenance/service/source.alch")).equals(source), "define-stage.provenance-drift");
  verifyInventory(generatedRoot, manifest);
  const ontology = json(resolve(generatedRoot, "provenance/service/ontology.json"));
  requireCheck(ontology.schema_version === "alchlang.service-ontology/v1" && ontology.ontology_admitted === false && ontology.authority_effect === "none", "define-stage.ontology-authority");
  for (const [entry, filename] of Object.entries(entries)) {
    const root = resolve(generatedRoot, "entries", entry);
    const authored = bytes(resolve(packageRoot, "alch/integration", filename));
    const child = json(resolve(root, "manifest.json"));
    requireCheck(child.source_sha256 === sha256(authored), `define-stage.entry-source:${entry}`);
    requireCheck(bytes(resolve(root, "provenance/function/source.alch")).equals(authored), `define-stage.entry-provenance:${entry}`);
    requireCheck(json(resolve(root, "provenance/function/ontology.json")).source_format === "alchlang", `define-stage.entry-ontology:${entry}`);
    requireCheck(json(resolve(root, "provenance/lowering/project/project.json")).schema_version === "domainspec.project/v2", `define-stage.entry-project:${entry}`);
    requireCheck(json(resolve(root, "evidence/lowering/certificate.json")).authority_effect === "none", `define-stage.entry-certificate:${entry}`);
    verifyInventory(root, child);
  }
  const {invoke} = await import(pathToFileURL(resolve(generatedRoot, "app/service/index.mjs")).href);
  const outcomes = [
    ["StageDependency", {prerequisites_complete: false, receipts_current: false}, "block", "prerequisites"],
    ["StageDependency", {prerequisites_complete: true, receipts_current: true}, "ready", "none"],
    ["StageResponse", {response_kind: "defer", response_present: false}, "open", "none"],
    ["StageResponse", {response_kind: "answer", response_present: false}, "block", "response"],
    ["StageReadiness", {interaction_complete: true, semantic_grounding_pass: true, non_collapse_pass: false, orthogonality_pass: true, dependencies_ready: true}, "block", "non-collapse"],
    ["StageReadiness", {interaction_complete: true, semantic_grounding_pass: true, non_collapse_pass: true, orthogonality_pass: true, dependencies_ready: true}, "ready", "none"],
    ["StageHandoff", {candidate_present: true, adapter_validation_pass: true, user_confirmed: true, confirmation_matches: false, dependency_receipts_current: true}, "block", "confirmation-drift"],
    ["StageHandoff", {candidate_present: true, adapter_validation_pass: true, user_confirmed: true, confirmation_matches: true, dependency_receipts_current: true}, "ready", "none"],
  ];
  for (const [entry, input, status, repairFocus] of outcomes) {
    const result = await invoke(entry, input);
    requireCheck(result.status === status && result.repair_focus === repairFocus && result.authority_effect === "none", `define-stage.outcome:${entry}:${status}:${repairFocus}`);
  }
  const temporaryRoot = mkdtempSync(join(tmpdir(), "define-stage-verify-"));
  try {
    const rebuilt = resolve(temporaryRoot, "bundle");
    const compilation = spawnSync(process.execPath, [compilerPath, "build", sourcePath, "--out", rebuilt], {cwd: repositoryRoot, encoding: "utf8", env: process.env});
    requireCheck(compilation.status === 0, `define-stage.recompile:${compilation.stderr.trim()}`);
    requireCheck(bytes(resolve(rebuilt, "manifest.json")).equals(bytes(resolve(generatedRoot, "manifest.json"))), "define-stage.recompile-manifest-drift");
    for (const relativePath of Object.keys(manifest.files)) {
      requireCheck(bytes(resolve(rebuilt, relativePath)).equals(bytes(resolve(generatedRoot, relativePath))), `define-stage.recompile-byte-drift:${relativePath}`);
    }
  } finally {
    rmSync(temporaryRoot, {recursive: true, force: true});
  }
  return {
    schema_version: "cav2.define-ontology-stage-port-verification/v1",
    status: "PASS",
    source: "implementation/define-cli/alch/integration/define-integration.alch",
    source_sha256: manifest.source_sha256,
    entries: Object.keys(entries),
    generated_files: Object.keys(manifest.files).length,
    construction_pipeline: ["alch-source", "composition-ontology", "craft-project", "domainspec-compile", "compiled-entry", "service-assembly"],
    fresh_recompilation: "byte-identical",
    ontology_admitted: false,
    authority_effect: "none",
  };
}

verify().then((result) => process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)).catch((error) => {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
});

