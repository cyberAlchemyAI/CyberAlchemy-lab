#!/usr/bin/env node

import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const scopeRoot = resolve(here, "../..");
const repoRoot = resolve(scopeRoot, "../..");
const registryPath = resolve(here, "META-TYPE-ENFORCEMENT-ASSETS.json");
const schemaPath = resolve(here, "meta-type-enforcement-assets.schema.json");
const ledgerPath = resolve(scopeRoot, ".craft/ledger.yml");
const viewPath = resolve(scopeRoot, "CRAFT.md");
const registry = JSON.parse(readFileSync(registryPath, "utf8"));
const ledger = readFileSync(ledgerPath, "utf8");
const view = readFileSync(viewPath, "utf8");
let checks = 0;

function assert(condition, message) {
  checks += 1;
  if (!condition) throw new Error(message);
}

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function expandSwu(ref) {
  const match = /^SWU-MTCLI-(\d{3})(?:\.\.(\d{3}))?$/.exec(ref);
  assert(Boolean(match), `invalid SWU ref:${ref}`);
  const start = Number(match[1]);
  const end = Number(match[2] ?? match[1]);
  assert(start <= end, `reversed SWU range:${ref}`);
  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
}

const schemaRun = spawnSync("python3", ["-c", [
  "import json,sys",
  "from jsonschema import Draft202012Validator",
  "schema=json.load(open(sys.argv[1],encoding='utf-8'))",
  "value=json.load(open(sys.argv[2],encoding='utf-8'))",
  "Draft202012Validator.check_schema(schema)",
  "Draft202012Validator(schema,format_checker=Draft202012Validator.FORMAT_CHECKER).validate(value)",
].join(";"), schemaPath, registryPath], { encoding: "utf8" });
assert(schemaRun.status === 0, `enforcement asset schema validation failed:${(schemaRun.stderr || schemaRun.stdout).trim()}`);

assert(registry.authority_effect === "none", "registry authority effect widened");
assert(registry.asset_count === registry.assets.length, "asset count mismatch");
assert(registry.baseline_binding.effect_of_this_registry === "none", "registry changed frozen baseline");
assert(registry.next_selectable_asset_id === "MTM-CATALOG", "next selectable enforcement asset drift");

const expectedIds = [
  "MTENF-BASELINE-V2",
  "MTENF-INSTANTIATE-CONTRACT-C3",
  "MTFIX-VALUE-OBJECT-BINDINGS",
  "MTFIX-ENUM-BINDINGS",
  "MTFIX-RULE-EVIDENCE-DRIFT",
  "MTFIND-OPERATION-AOP-BOUNDARY",
  "MTFIND-WORKFLOW-COMPENSATION",
  "MTFIX-FRONTIER-POINTER-DRIFT",
  "MTM-CATALOG",
  "MTM-DECODER",
  "MTM-PLANNER",
  "MTM-WRITER",
  "MTM-RECEIPT",
  "MTM-GENERALIZATION",
  "MTM-RELATIONSHIP-OBSERVER",
  "MTM-PACKAGE",
];
const ids = registry.assets.map(({ asset_id }) => asset_id);
assert(new Set(ids).size === ids.length, "duplicate enforcement asset id");
assert(JSON.stringify(ids) === JSON.stringify(expectedIds), "enforcement asset identity or order drift");
const byId = new Map(registry.assets.map((asset) => [asset.asset_id, asset]));

const computedCounts = Object.fromEntries(Object.keys(registry.class_counts).map((name) => [name, 0]));
for (const asset of registry.assets) {
  assert(Object.hasOwn(computedCounts, asset.asset_class), `unknown enforcement asset class:${asset.asset_class}`);
  computedCounts[asset.asset_class] += 1;
  assert(asset.authority_effect === "none", `asset authority effect widened:${asset.asset_id}`);
  for (const dependency of asset.dependencies) assert(byId.has(dependency), `missing dependency:${asset.asset_id}->${dependency}`);
  for (const evidence of asset.evidence_refs) {
    const path = resolve(scopeRoot, evidence.path);
    assert(existsSync(path), `missing evidence:${evidence.path}`);
    assert(sha256(path) === evidence.sha256, `evidence digest drift:${evidence.path}`);
  }
}
assert(JSON.stringify(computedCounts) === JSON.stringify(registry.class_counts), "enforcement asset class counts drift");

const visiting = new Set();
const visited = new Set();
function visit(id) {
  assert(!visiting.has(id), `enforcement asset dependency cycle:${id}`);
  if (visited.has(id)) return;
  visiting.add(id);
  for (const dependency of byId.get(id).dependencies) visit(dependency);
  visiting.delete(id);
  visited.add(id);
}
for (const id of ids) visit(id);

const baselinePath = resolve(scopeRoot, registry.baseline_binding.manifest_path);
const baseline = JSON.parse(readFileSync(baselinePath, "utf8"));
assert(sha256(baselinePath) === registry.baseline_binding.manifest_sha256, "baseline manifest file digest drift");
assert(baseline.baseline_id === registry.baseline_binding.baseline_id, "baseline identity drift");
assert(baseline.baseline_digest === registry.baseline_binding.baseline_digest, "baseline body digest drift");
assert(baseline.denominators.frozen_evidence_files === 771, "baseline frozen-file denominator drift");
assert(baseline.denominators.backend_meta_types === 13, "baseline meta-type denominator drift");
assert(baseline.denominators.realization_rows === 39, "baseline realization denominator drift");

const contractReceipt = JSON.parse(readFileSync(resolve(scopeRoot, "impl/cli/contracts/foundation-contract.candidate-3.validation.json"), "utf8"));
assert(contractReceipt.swu_id === "SWU-MTCLI-002", "candidate-3 SWU identity drift");
assert(contractReceipt.result === "pass-with-unrelated-package-boundary-residue", "candidate-3 validation result drift");
assert(contractReceipt.test.passed === 17 && contractReceipt.test.failed === 0, "candidate-3 test result drift");
assert(contractReceipt.baseline_binding.baseline_id === registry.baseline_binding.baseline_id, "candidate-3 baseline identity drift");
assert(contractReceipt.baseline_binding.baseline_digest === registry.baseline_binding.baseline_digest, "candidate-3 baseline digest drift");
assert(contractReceipt.claim_ceiling.instantiate_contract_selected === true, "instantiate contract not selected");
for (const field of ["instantiate_implementation", "generated_target_conformance", "relationship_enforcement", "behavioral_effect_enforcement", "publication", "release", "deployment", "production"]) {
  assert(contractReceipt.claim_ceiling[field] === false, `candidate-3 claim ceiling widened:${field}`);
}
assert(contractReceipt.next_unit.swu_id === "SWU-MTCLI-003" && contractReceipt.next_unit.state === "selectable-not-selected", "candidate-3 next unit drift");
const canonicalCurrentState = JSON.parse(readFileSync(resolve(scopeRoot, "definitions/meta-types/current-implementation.json"), "utf8"));
const canonicalCurrentView = readFileSync(resolve(scopeRoot, "definitions/meta-types/current-implementation.md"), "utf8");
const cliWorkPack = readFileSync(resolve(scopeRoot, "development/meta-type-instantiation-cli/WORK-PACK.md"), "utf8");
assert(canonicalCurrentState.product_frontier.next_unit === "SWU-MTCLI-002", "canonical frontier pointer changed; resolve or retire MTFIX-FRONTIER-POINTER-DRIFT");
assert(canonicalCurrentView.includes("next product unit is `SWU-MTCLI-002`"), "canonical human frontier pointer changed; resolve or retire MTFIX-FRONTIER-POINTER-DRIFT");
assert(cliWorkPack.includes("Select `SWU-MTCLI-002` next"), "work-pack frontier pointer changed; resolve or retire MTFIX-FRONTIER-POINTER-DRIFT");

const maturity = JSON.parse(readFileSync(resolve(scopeRoot, "development/backend-meta-type-conformance/evidence/WP-BMC-001/BMC-EVD-001.MATURITY-MATRIX.json"), "utf8"));
const valueObject = maturity.rows.find(({ meta_type_id }) => meta_type_id === "DS-D1.2");
const enumRow = maturity.rows.find(({ meta_type_id }) => meta_type_id === "DS-D1.3");
const rule = maturity.rows.find(({ meta_type_id }) => meta_type_id === "DS-D1.7");
assert(valueObject.findings.length === 3 && valueObject.findings.every(({ code }) => code === "BMC_EVD_CANDIDATE_BINDING_STALE"), "Value Object repair findings drift");
assert(enumRow.findings.length === 9 && enumRow.findings.every(({ code }) => code === "BMC_EVD_CANDIDATE_BINDING_ABSENT"), "Enum repair findings drift");
assert(rule.findings.length === 0, "historical Rule findings changed; refresh asset classification");
const ruleLiveDrift = [];
for (const realization of rule.realization_refs) {
  for (const role of ["source", "provider", "binding"]) {
    const ref = realization[role];
    if (sha256(resolve(repoRoot, ref.path)) !== ref.sha256) ruleLiveDrift.push(`${realization.language}:${role}`);
  }
}
assert(JSON.stringify(ruleLiveDrift.sort()) === JSON.stringify(["python:provider", "python:source", "rust:provider", "rust:source", "typescript:provider", "typescript:source"].sort()), `Rule live drift changed:${ruleLiveDrift.join(",")}`);
assert(byId.get("MTFIX-VALUE-OBJECT-BINDINGS").classification.includes("not a proven canonical realization-source defect"), "Value Object source/evidence planes collapsed");
assert(byId.get("MTFIX-ENUM-BINDINGS").classification.includes("not evidence that admitted realizations are missing"), "Enum source/evidence planes collapsed");
assert(byId.get("MTFIX-RULE-EVIDENCE-DRIFT").classification.includes("refresh evidence"), "Rule evidence/source planes collapsed");

const operationReceipt = JSON.parse(readFileSync(resolve(scopeRoot, "development/architecture-pattern-enforcement/evidence/WP-APE-OP-PROFILE-001/WORK-PACK-VERIFICATION.json"), "utf8"));
const workflowReceipt = JSON.parse(readFileSync(resolve(scopeRoot, "development/architecture-pattern-enforcement/evidence/WP-APE-WF-PROFILE-001/WORK-PACK-VERIFICATION.json"), "utf8"));
assert(operationReceipt.selected_subject_evaluation.result === "fail", "Operation target result drift");
assert(operationReceipt.selected_subject_evaluation.primary_finding === "AOP_BOUNDARY_INSTRUMENTATION_PLACEMENT", "Operation target finding drift");
assert(operationReceipt.selected_subject_evaluation.implementation_interpretation.includes("evaluator implementation passes"), "Operation target/evaluator planes collapsed");
assert(workflowReceipt.selected_subject_evaluation.result === "incomplete", "Workflow target result drift");
assert(workflowReceipt.selected_subject_evaluation.primary_finding === "AOP_WF_COMPENSATION_CALLABLE_MISSING", "Workflow target finding drift");
assert(workflowReceipt.selected_subject_evaluation.implementation_interpretation.includes("evaluator implementation passes"), "Workflow target/evaluator planes collapsed");

const machinery = registry.assets.filter(({ asset_class }) => asset_class === "machinery");
assert(machinery.length === 8, "machinery asset denominator drift");
assert(machinery.filter(({ state }) => state === "selectable-not-selected").map(({ asset_id }) => asset_id).join() === "MTM-CATALOG", "more than one machinery asset selected/selectable");
assert(machinery.every(({ classification }) => classification === "planned machinery; not implemented"), "planned machinery overclaimed as implemented");
const coveredSwus = new Set(machinery.flatMap(({ swu_refs }) => swu_refs.flatMap(expandSwu)));
assert(JSON.stringify([...coveredSwus].sort((a, b) => a - b)) === JSON.stringify(Array.from({ length: 17 }, (_, index) => index + 3)), "SWU-MTCLI-003..019 machinery coverage drift");

const expectedObligations = [
  "declared read set",
  "declared write set",
  "declared effect set",
  "guard executes before state mutation",
  "atomic state-and-outbox behavior",
  "explicit failure continuation",
  "no undeclared read, write or effect",
  "typed relationships to Rule, Event and Workflow",
];
assert(JSON.stringify(registry.operation_enforcement_contract.obligations) === JSON.stringify(expectedObligations), "Operation obligation set drift");
const relationshipAuthority = readFileSync(resolve(scopeRoot, "definitions/relationships/relationships.yml"), "utf8");
for (const relation of registry.operation_enforcement_contract.relationship_authority) assert(relationshipAuthority.includes(`\"markdown\": \"${relation}`), `missing relationship authority:${relation}`);
assert(registry.operation_enforcement_contract.implementation_state === "not-implemented", "Operation enforcement overclaim");

for (const field of ["instantiate_implementation", "generated_target_conformance", "relationship_enforcement", "behavioral_effect_enforcement", "publication", "release", "deployment", "production"]) {
  assert(registry.claim_ceiling[field] === false, `registry claim ceiling widened:${field}`);
}
assert(ledger.includes("ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS: artifacts[152]"), "registry Craft by-id index missing");
assert(ledger.includes("ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS-SCHEMA: artifacts[153]"), "schema Craft by-id index missing");
assert(ledger.includes("ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS-VALIDATOR: artifacts[154]"), "validator Craft by-id index missing");
for (const path of [".craft/artifacts/META-TYPE-ENFORCEMENT-ASSETS.json", ".craft/artifacts/meta-type-enforcement-assets.schema.json", ".craft/artifacts/validate-meta-type-enforcement-assets.mjs"]) assert(ledger.includes(`${path}:`), `Craft by-path index missing:${path}`);
assert(view.includes("## Meta-type enforcement assets"), "human enforcement asset section missing");
for (const id of ids) assert(view.includes(`\`${id}\``), `human enforcement asset missing:${id}`);

process.stdout.write(`${JSON.stringify({
  status: "pass",
  registry_id: registry.registry_id,
  checks,
  assets: registry.assets.length,
  machinery_assets: machinery.length,
  next_selectable_asset_id: registry.next_selectable_asset_id,
  baseline_effect: "none",
  authority_effect: "none",
}, null, 2)}\n`);
