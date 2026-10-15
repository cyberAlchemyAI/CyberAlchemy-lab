#!/usr/bin/env node
import {createHash} from "node:crypto";
import {spawnSync} from "node:child_process";
import {mkdtempSync, readFileSync, rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join, resolve} from "node:path";
import {pathToFileURL} from "node:url";

const packageRoot = resolve(import.meta.dirname, "..");
const repositoryRoot = resolve(packageRoot, "../..");
const sourcePath = resolve(packageRoot, "alch/define-runtime.alch");
const selectionPath = resolve(packageRoot, "alch/define-runtime.ontology-selection.json");
const generatedRoot = resolve(packageRoot, "generated/define-service");
const compilerPath = resolve(repositoryRoot, "language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js");
const semanticSourcePath = resolve(repositoryRoot, "language/capabilities/alchlang/plans/general-compiler-v1/extensions/semantic-contract-v1/semantic-prelude.alch");
const semanticGeneratedRoot = resolve(repositoryRoot, "language/capabilities/alchlang/plans/general-compiler-v1/extensions/semantic-contract-v1/evidence/bundle");
const expectedEntries = {
  SemanticGrounding: "define-semantic-grounding.alch",
  GroundingEvidence: "define-grounding-evidence.alch",
  NonCollapse: "define-non-collapse.alch",
  NonCollapseEvidence: "define-non-collapse-evidence.alch",
  Orthogonality: "define-orthogonality.alch",
  OrthogonalityEvidence: "define-orthogonality-evidence.alch",
  LanguageReadiness: "define-language-readiness.alch",
  ScopeReadiness: "define-scope-readiness.alch",
  ConceptDisposition: "define-concept-disposition.alch",
  PackReadiness: "define-pack-readiness.alch",
  AlchHandoffReadiness: "define-alch-handoff-readiness.alch",
};

const bytes = (path) => readFileSync(path);
const json = (path) => JSON.parse(bytes(path).toString("utf8"));
const sha256 = (value) => createHash("sha256").update(value).digest("hex");
const requireCheck = (condition, code) => { if (!condition) throw new Error(code); };

function verifySelection() {
  const selection = json(selectionPath);
  requireCheck(selection.schema_version === "cav2.define-alch-ontology-selection/v1-candidate", "alch-runtime.selection-version");
  requireCheck(selection.ontology_admitted === false && selection.authority_effect === "none", "alch-runtime.selection-authority");
  for (const source of [selection.business_source, selection.system_source]) {
    const selectedSourcePath = resolve(repositoryRoot, source.path);
    requireCheck(sha256(bytes(selectedSourcePath)) === source.sha256, `alch-runtime.selection-source-drift:${source.path}`);
    const ids = new Set(json(selectedSourcePath).nodes.map((record) => record.id ?? record.node_id));
    for (const id of source.selected_records) requireCheck(ids.has(id), `alch-runtime.selection-record-missing:${id}`);
  }
  const exposed = new Set(Object.keys(expectedEntries));
  for (const bridge of selection.bridges) {
    requireCheck(["realized_by", "constrained_by", "tested_by"].includes(bridge.relation), "alch-runtime.selection-bridge-relation");
    for (const entry of bridge.alch_entries) requireCheck(exposed.has(entry), `alch-runtime.selection-entry-missing:${entry}`);
  }
  requireCheck(selection.semantic_runtime?.profile === "semantic-contract-v1", "alch-runtime.selection-semantic-profile");
  requireCheck(JSON.stringify(selection.semantic_runtime.operations) === JSON.stringify(["semantic-key", "contains-phrase"]), "alch-runtime.selection-semantic-operations");
  requireCheck(selection.semantic_runtime.ontology_admitted === false && selection.semantic_runtime.constitution_adopted === false && selection.semantic_runtime.authority_effect === "none", "alch-runtime.selection-semantic-authority");
  return selection;
}

function verifyInventory(root, manifest) {
  for (const [relativePath, expected] of Object.entries(manifest.files)) {
    requireCheck(sha256(bytes(resolve(root, relativePath))) === expected, `alch-runtime.generated-drift:${relativePath}`);
  }
}

async function verifySemanticPrelude(temporaryRoot) {
  const manifest = json(resolve(semanticGeneratedRoot, "manifest.json"));
  requireCheck(manifest.schema_version === "alchlang.semantic-contract-build/v1" && manifest.profile === "semantic-contract-v1", "alch-runtime.semantic-manifest");
  requireCheck(manifest.source_sha256 === sha256(bytes(semanticSourcePath)), "alch-runtime.semantic-source-drift");
  requireCheck(bytes(resolve(semanticGeneratedRoot, "provenance/alch/source.alch")).equals(bytes(semanticSourcePath)), "alch-runtime.semantic-provenance-drift");
  requireCheck(manifest.ontology_admitted === false && manifest.constitution_adopted === false && manifest.authority_effect === "none", "alch-runtime.semantic-authority");
  verifyInventory(semanticGeneratedRoot, manifest);
  const report = json(resolve(semanticGeneratedRoot, "evidence/validation/report.json"));
  requireCheck(report.status === "pass" && report.summary.failed === 0 && report.authority_effect === "none", "alch-runtime.semantic-validation");
  const semantic = await import(pathToFileURL(resolve(semanticGeneratedRoot, "app/prelude.mjs")).href);
  requireCheck(semantic.invoke("semantic-key", " Release—Gate ") === "release gate", "alch-runtime.semantic-key");
  requireCheck(semantic.invoke("contains-phrase", {text: "The release-gate is ready", phrase: "release gate"}) === true, "alch-runtime.semantic-phrase-match");
  requireCheck(semantic.invoke("contains-phrase", {text: "A predefined runtime", phrase: "define"}) === false, "alch-runtime.semantic-phrase-collapse");
  const rebuilt = resolve(temporaryRoot, "semantic-prelude");
  const compilation = spawnSync(process.execPath, [compilerPath, "build", semanticSourcePath, "--out", rebuilt], {cwd: repositoryRoot, encoding: "utf8", env: process.env});
  requireCheck(compilation.status === 0, `alch-runtime.semantic-recompile:${compilation.stderr.trim()}`);
  requireCheck(bytes(resolve(rebuilt, "manifest.json")).equals(bytes(resolve(semanticGeneratedRoot, "manifest.json"))), "alch-runtime.semantic-recompile-manifest-drift");
  for (const relativePath of Object.keys(manifest.files)) requireCheck(bytes(resolve(rebuilt, relativePath)).equals(bytes(resolve(semanticGeneratedRoot, relativePath))), `alch-runtime.semantic-recompile-byte-drift:${relativePath}`);
  return {operations: ["semantic-key", "contains-phrase"], source_sha256: manifest.source_sha256, generated_files: Object.keys(manifest.files).length};
}

async function verifyOutcomes() {
  const {invoke} = await import(pathToFileURL(resolve(generatedRoot, "app/service/index.mjs")).href);
  const cases = [
    ["SemanticGrounding", {schema_valid: true, targets_valid: true, coverage_complete: true, sources_present: true, direct_matches: true, evidence_valid: true, candidate_inference_present: true, user_confirmed: false}, "review"],
    ["SemanticGrounding", {schema_valid: true, targets_valid: true, coverage_complete: false, sources_present: true, direct_matches: true, evidence_valid: true, candidate_inference_present: false, user_confirmed: true}, "block"],
    ["GroundingEvidence", {posture: "candidate-inference", rationale_present: true}, "review"],
    ["GroundingEvidence", {posture: "unsupported", rationale_present: true}, "block"],
    ["NonCollapse", {terms_valid: true, pair_targets_valid: true, pair_coverage_complete: true, evidence_valid: true, terms_distinct: true, pairs_resolved: true, option_coverage_complete: true, definitions_distinct: true}, "pass"],
    ["NonCollapse", {terms_valid: true, pair_targets_valid: true, pair_coverage_complete: true, evidence_valid: true, terms_distinct: false, pairs_resolved: true, option_coverage_complete: true, definitions_distinct: true}, "block"],
    ["NonCollapseEvidence", {relation: "distinct", difference_present: true}, "accept"],
    ["NonCollapseEvidence", {relation: "collapsed", difference_present: true}, "block"],
    ["Orthogonality", {applicability_valid: true, axis_identity_valid: true, axis_structure_valid: true, rationale_present: true, cardinality_valid: true, pair_targets_valid: true, pair_coverage_complete: true, pair_evidence_valid: true, axes_non_redundant: true, pairs_resolved: true, couplings_named: true}, "pass"],
    ["Orthogonality", {applicability_valid: true, axis_identity_valid: true, axis_structure_valid: true, rationale_present: true, cardinality_valid: true, pair_targets_valid: true, pair_coverage_complete: true, pair_evidence_valid: true, axes_non_redundant: false, pairs_resolved: true, couplings_named: true}, "block"],
    ["OrthogonalityEvidence", {relation: "coupled", difference_present: true, coupling_named: true}, "accept"],
    ["OrthogonalityEvidence", {relation: "coupled", difference_present: true, coupling_named: false}, "block"],
    ["LanguageReadiness", {semantic_grounding: "pass", non_collapse: "pass", orthogonality: "pass", user_confirmed: false}, "review"],
    ["LanguageReadiness", {semantic_grounding: "pass", non_collapse: "pass", orthogonality: "pass", user_confirmed: true}, "pass"],
    ["ScopeReadiness", {agent_scope_ready: true, context_present: true, desired_outcome_present: true, intent_present: true, language_not_blocked: true}, "ready"],
    ["ScopeReadiness", {agent_scope_ready: true, context_present: true, desired_outcome_present: true, intent_present: true, language_not_blocked: false}, "repair"],
    ["ConceptDisposition", {action: "propose", definition_reference_present: false, base_reference_present: false, specialization_scope_present: false, proposal_present: true}, "accepted"],
    ["ConceptDisposition", {action: "reuse", definition_reference_present: false, base_reference_present: false, specialization_scope_present: false, proposal_present: false}, "block"],
    ["PackReadiness", {version_supported: true, identity_complete: true, scope_complete: true, concepts_present: true, dispositions_exact: true, dispositions_declared: true, authority_none: true, language_quality_pass: true, language_evidence_complete: true, open_questions_empty: false}, "valid_open"],
    ["PackReadiness", {version_supported: true, identity_complete: true, scope_complete: true, concepts_present: true, dispositions_exact: true, dispositions_declared: true, authority_none: true, language_quality_pass: true, language_evidence_complete: true, open_questions_empty: true}, "handoff_ready"],
    ["AlchHandoffReadiness", {pack_handoff_ready: true, language_quality_present: true, semantic_grounding_pass: true, non_collapse_pass: true, orthogonality_pass: true, output_target_new: true}, "ready"],
    ["AlchHandoffReadiness", {pack_handoff_ready: true, language_quality_present: true, semantic_grounding_pass: true, non_collapse_pass: false, orthogonality_pass: true, output_target_new: true}, "block"],
  ];
  for (const [entry, input, status] of cases) {
    const result = await invoke(entry, input);
    requireCheck(result.status === status && result.authority_effect === "none", `alch-runtime.outcome:${entry}:${status}`);
  }
}

async function verify() {
  const selection = verifySelection();
  const source = bytes(sourcePath);
  const sourceDigest = sha256(source);
  const manifest = json(resolve(generatedRoot, "manifest.json"));
  requireCheck(manifest.schema_version === "alchlang.service-build/v1" && manifest.profile === "service-v1", "alch-runtime.service-manifest");
  requireCheck(manifest.source_sha256 === sourceDigest, "alch-runtime.service-source-drift");
  requireCheck(JSON.stringify(manifest.entries) === JSON.stringify(Object.keys(expectedEntries)), "alch-runtime.service-entry-drift");
  requireCheck(bytes(resolve(generatedRoot, "provenance/service/source.alch")).equals(source), "alch-runtime.service-provenance-drift");
  verifyInventory(generatedRoot, manifest);

  const serviceOntology = json(resolve(generatedRoot, "provenance/service/ontology.json"));
  requireCheck(serviceOntology.schema_version === "alchlang.service-ontology/v1" && serviceOntology.ontology_admitted === false && serviceOntology.authority_effect === "none", "alch-runtime.service-ontology");
  const trace = json(resolve(generatedRoot, "evidence/service/assembly-trace.json"));
  requireCheck(JSON.stringify(trace.pipeline) === JSON.stringify(selection.construction_pipeline), "alch-runtime.pipeline-drift");
  requireCheck(trace.entries.length === Object.keys(expectedEntries).length && trace.authority_effect === "none", "alch-runtime.trace-entries");

  for (const [entry, filename] of Object.entries(expectedEntries)) {
    const entryRoot = resolve(generatedRoot, "entries", entry);
    const authored = bytes(resolve(packageRoot, "alch", filename));
    const childManifest = json(resolve(entryRoot, "manifest.json"));
    requireCheck(childManifest.schema_version === "alchlang.function-build/v1" && childManifest.source_sha256 === sha256(authored), `alch-runtime.entry-manifest:${entry}`);
    requireCheck(bytes(resolve(entryRoot, "provenance/function/source.alch")).equals(authored), `alch-runtime.entry-source:${entry}`);
    verifyInventory(entryRoot, childManifest);
    const ontology = json(resolve(entryRoot, "provenance/function/ontology.json"));
    requireCheck(ontology.schema_version === "domainspec.composition-ontology/v1" && ontology.source_format === "alchlang" && ontology.ontology_admitted === false && ontology.authority_effect === "none", `alch-runtime.entry-ontology:${entry}`);
    requireCheck(json(resolve(entryRoot, "provenance/lowering/project/project.json")).schema_version === "domainspec.project/v2", `alch-runtime.entry-craft-project:${entry}`);
    const certificate = json(resolve(entryRoot, "evidence/lowering/certificate.json"));
    requireCheck(certificate.compiler?.package === "@domainspec-v2/cli" && certificate.authority_effect === "none", `alch-runtime.entry-certificate:${entry}`);
  }

  await verifyOutcomes();
  const temporaryRoot = mkdtempSync(join(tmpdir(), "define-alch-service-verify-"));
  const rebuilt = resolve(temporaryRoot, "define-service");
  try {
    const semanticPrelude = await verifySemanticPrelude(temporaryRoot);
    const compilation = spawnSync(process.execPath, [compilerPath, "build", sourcePath, "--out", rebuilt], {cwd: repositoryRoot, encoding: "utf8", env: process.env});
    requireCheck(compilation.status === 0, `alch-runtime.recompile:${compilation.stderr.trim()}`);
    requireCheck(bytes(resolve(rebuilt, "manifest.json")).equals(bytes(resolve(generatedRoot, "manifest.json"))), "alch-runtime.recompile-manifest-drift");
    for (const relativePath of Object.keys(manifest.files)) requireCheck(bytes(resolve(rebuilt, relativePath)).equals(bytes(resolve(generatedRoot, relativePath))), `alch-runtime.recompile-byte-drift:${relativePath}`);
    selection.semanticPrelude = semanticPrelude;
  } finally {
    rmSync(temporaryRoot, {recursive: true, force: true});
  }

  return {
    schema_version: "cav2.define-alch-runtime-verification/v2",
    status: "PASS",
    source: "implementation/define-cli/alch/define-runtime.alch",
    source_sha256: sourceDigest,
    entries: Object.keys(expectedEntries),
    generated_files: Object.keys(manifest.files).length,
    ontology_selection: "implementation/define-cli/alch/define-runtime.ontology-selection.json",
    construction_pipeline: trace.pipeline,
    semantic_runtime: selection.semanticPrelude,
    fresh_recompilation: "byte-identical",
    authority_effect: "none",
  };
}

verify().then((result) => process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)).catch((error) => {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
});
