import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const artifactDir = dirname(fileURLToPath(import.meta.url));
const scopeRoot = resolve(artifactDir, "../..");
const repoRoot = resolve(scopeRoot, "../..");
const statePath = resolve(artifactDir, "META-TYPE-STATE.json");
const ledgerPath = resolve(scopeRoot, ".craft/ledger.yml");
const viewPath = resolve(scopeRoot, "CRAFT.md");
const state = JSON.parse(readFileSync(statePath, "utf8"));
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

function resolveStatePath(path) {
  return path.startsWith("[repo-root]/")
    ? resolve(repoRoot, path.slice("[repo-root]/".length))
    : resolve(scopeRoot, path);
}

function contextBlock(text, contextId) {
  const marker = `  - context_id: ${contextId}`;
  const contextsStart = text.indexOf("\ncontexts:\n");
  assert(contextsStart >= 0, "missing contexts collection");
  const start = text.indexOf(marker, contextsStart);
  assert(start >= 0, `missing ledger context: ${contextId}`);
  const end = text.indexOf("\n  - context_id: ", start + marker.length);
  return text.slice(start, end < 0 ? text.length : end);
}

function unique(values, label) {
  assert(new Set(values).size === values.length, `duplicate ${label}`);
}

assert(state.schema_version === "domainspec.craft-meta-type-state/v1", "state schema drift");
assert(state.authority_effect === "none", "state must have no authority effect");
assert(state.ordering_rule.includes("file modification time does not"), "freshness ordering drift");
assert(state.audit_provenance.joined === true && state.audit_provenance.write_effect === "none", "helper closeout drift");
assert(state.headline.backend_meta_types === 13, "backend denominator drift");
assert(state.headline.backend_realization_rows_present === 39, "realization denominator drift");
assert(state.headline.ui_meta_type_candidates === 11, "UI denominator drift");
assert(state.headline.architecture_relationship_rows === 31, "relationship denominator drift");
assert(state.headline.exact_target_implementation_enforcement === "not-implemented", "claim ceiling drift");
assert(state.headline.canonical_baseline_state === "owner-admitted-frozen", "baseline state drift");
assert(
  state.headline.canonical_baseline_id === "domainspec-meta-types-current-implemented@2",
  "baseline identity drift",
);
assert(
  state.headline.canonical_baseline_digest === "10c29c2a4feb5039b6c90dcd7e2d44024757b4dd2414f9c0383c82387ec6e836",
  "baseline digest projection drift",
);
assert(state.headline.canonical_baseline_evidence_files === 771, "baseline evidence denominator drift");
assert(state.headline.historical_queue_controls_baseline === false, "historical queue regained baseline authority");

const baselinePath = resolveStatePath(state.canonical_baseline.manifest_path);
const baseline = JSON.parse(readFileSync(baselinePath, "utf8"));
const ownerDecisionPath = resolveStatePath(state.canonical_baseline.owner_decision_path);
const ownerDecision = JSON.parse(readFileSync(ownerDecisionPath, "utf8"));
assert(state.canonical_baseline.status === "owner-admitted-frozen", "canonical baseline status drift");
assert(baseline.baseline_id === state.canonical_baseline.baseline_id, "canonical baseline identity mismatch");
assert(baseline.baseline_digest === state.canonical_baseline.baseline_digest, "canonical baseline digest mismatch");
assert(sha256(baselinePath) === state.canonical_baseline.manifest_sha256, "canonical baseline file digest mismatch");
assert(sha256(ownerDecisionPath) === state.canonical_baseline.owner_decision_sha256, "owner decision digest mismatch");
assert(
  ownerDecision.selected_option.id === "definitions-and-ontology-first-then-freeze-v2",
  "owner baseline selection drift",
);
assert(ownerDecision.remaining_owner_decisions.length === 0, "unexpected remaining baseline owner decision");
assert(baseline.denominators.frozen_evidence_files === state.canonical_baseline.evidence_files, "baseline file count mismatch");
assert(baseline.denominators.backend_meta_types === state.canonical_baseline.backend_types, "baseline type count mismatch");
assert(
  baseline.denominators.realization_rows === state.canonical_baseline.realization_rows,
  "baseline realization count mismatch",
);
assert(baseline.denominators.ui_state_rows === state.canonical_baseline.ui_state_rows, "baseline UI count mismatch");
assert(state.canonical_baseline.prior_form_queue_effect === "historical-provenance-only", "form queue effect drift");
assert(state.canonical_baseline.next_selectable_unit === "SWU-MTCLI-003", "next CLI unit drift");
assert(state.headline.enforcement_assets_state === "first-class-registry", "enforcement asset state drift");
assert(state.headline.enforcement_asset_count === 16, "enforcement asset denominator drift");
assert(state.headline.next_selectable_unit === "SWU-MTCLI-003", "headline next CLI unit drift");
assert(state.execution_runtime.runtime_id === "domainspec-v2-node@26.8.1", "meta-type execution runtime drift");
assert(state.execution_runtime.canonical_baseline_effect === "none-on-771-frozen-implementation-bytes", "runtime migration changed frozen baseline");
assert(existsSync(resolveStatePath(state.execution_runtime.runtime_contract)), "runtime contract missing");
assert(existsSync(resolveStatePath(state.execution_runtime.runtime_validator)), "runtime validator missing");
assert(existsSync(resolveStatePath(state.execution_runtime.owner_decision)), "runtime owner decision missing");

const enforcementRegistryPath = resolveStatePath(state.enforcement_asset_registry.registry_path);
const enforcementSchemaPath = resolveStatePath(state.enforcement_asset_registry.schema_path);
const enforcementValidatorPath = resolveStatePath(state.enforcement_asset_registry.validator_path);
assert(existsSync(enforcementRegistryPath), "enforcement asset registry missing");
assert(existsSync(enforcementSchemaPath), "enforcement asset schema missing");
assert(existsSync(enforcementValidatorPath), "enforcement asset validator missing");
assert(sha256(enforcementRegistryPath) === state.enforcement_asset_registry.registry_sha256, "enforcement asset registry digest drift");
assert(sha256(enforcementSchemaPath) === state.enforcement_asset_registry.schema_sha256, "enforcement asset schema digest drift");
assert(sha256(enforcementValidatorPath) === state.enforcement_asset_registry.validator_sha256, "enforcement asset validator digest drift");
const enforcementRegistry = JSON.parse(readFileSync(enforcementRegistryPath, "utf8"));
assert(enforcementRegistry.asset_count === state.enforcement_asset_registry.asset_count, "enforcement asset count projection drift");
assert(JSON.stringify(enforcementRegistry.class_counts) === JSON.stringify(state.enforcement_asset_registry.class_counts), "enforcement asset class projection drift");
assert(enforcementRegistry.next_selectable_asset_id === state.enforcement_asset_registry.next_selectable_asset_id, "next enforcement asset projection drift");
assert(state.enforcement_asset_registry.next_selectable_unit === "SWU-MTCLI-003", "enforcement registry next SWU drift");
assert(state.enforcement_asset_registry.baseline_effect === "none", "enforcement registry changed baseline");
assert(state.enforcement_asset_registry.authority_effect === "none", "enforcement registry authority effect widened");
const enforcementRun = spawnSync(process.execPath, [enforcementValidatorPath], { encoding: "utf8" });
assert(enforcementRun.status === 0, `enforcement asset validation failed:${(enforcementRun.stderr || enforcementRun.stdout).trim()}`);

for (const source of state.controlling_sources) {
  const path = resolveStatePath(source.path);
  assert(existsSync(path), `missing controlling source: ${source.path}`);
  assert(sha256(path) === source.sha256, `controlling source digest drift: ${source.path}`);
}

const maturity = JSON.parse(
  readFileSync(
    resolve(
      scopeRoot,
      "development/backend-meta-type-conformance/evidence/WP-BMC-001/BMC-EVD-001.MATURITY-MATRIX.json",
    ),
    "utf8",
  ),
);
assert(maturity.rows.length === 13, "maturity matrix type denominator drift");
assert(maturity.relationship_scope.authority_audit_rows === 31, "maturity relationship denominator drift");
assert(maturity.relationship_scope.backend_implementation_rows === 17, "backend relation denominator drift");
assert(maturity.status === "flag" && maturity.authority_effect === "none", "maturity claim ceiling drift");

const backendIds = state.backend_types.map(({ id }) => id);
unique(backendIds, "backend type id");
assert(backendIds.length === 13, "state backend row count drift");
let realizationRows = 0;
let matrixFindingCount = 0;
const liveDrift = [];
for (const row of maturity.rows) {
  const projection = state.backend_types.find(({ id }) => id === row.meta_type_id);
  assert(Boolean(projection), `missing backend state row: ${row.meta_type_id}`);
  assert(projection.label === row.meta_type_label, `backend label drift: ${row.meta_type_id}`);
  assert(projection.canonical_maturity === row.lifecycle_status.canonical_maturity, `maturity drift: ${row.meta_type_id}`);
  assert(projection.realizations_present === row.realization_refs.length, `realization count drift: ${row.meta_type_id}`);
  assert(
    projection.snapshot_registered_providers ===
      `${row.registry_status.registered_provider_ids.length}/${row.registry_status.provider_ids.length}`,
    `provider registration projection drift: ${row.meta_type_id}`,
  );
  assert(projection.snapshot_profile_status === row.profile_status.kind, `profile projection drift: ${row.meta_type_id}`);
  assert(projection.ontology_queue === row.ontology_status.queue_state, `ontology queue drift: ${row.meta_type_id}`);
  assert(projection.queue_ready === row.lifecycle_status.queue_readiness, `queue readiness drift: ${row.meta_type_id}`);
  assert(projection.snapshot_findings === row.findings.length, `finding count drift: ${row.meta_type_id}`);
  realizationRows += row.realization_refs.length;
  matrixFindingCount += row.findings.length;
  for (const realization of row.realization_refs) {
    for (const role of ["source", "provider", "binding"]) {
      const ref = realization[role];
      const path = resolve(repoRoot, ref.path);
      assert(existsSync(path), `missing live realization ${role}: ${ref.path}`);
      if (sha256(path) !== ref.sha256) liveDrift.push(`${row.meta_type_label}:${realization.language}:${role}`);
    }
  }
}
assert(realizationRows === 39, "live realization row denominator drift");
assert(matrixFindingCount === 30, "historical binding finding denominator drift");
assert(
  JSON.stringify(liveDrift.sort()) ===
    JSON.stringify(
      [
        "Rule:python:provider",
        "Rule:python:source",
        "Rule:rust:provider",
        "Rule:rust:source",
        "Rule:typescript:provider",
        "Rule:typescript:source",
      ].sort(),
    ),
  `unrepresented live maturity drift: ${liveDrift.join(", ")}`,
);

const uiPacket = JSON.parse(
  readFileSync(resolve(scopeRoot, "development/ui-profile-implementation/authority-packet/packet.json"), "utf8"),
);
assert(uiPacket.status === "owner-review-required", "UI authority state drift");
assert(uiPacket.ds_d1.required_concept_count === 11, "UI packet denominator drift");
assert(uiPacket.ds_d1.rows.length === state.ui_types.length, "UI state row count drift");
for (const row of uiPacket.ds_d1.rows) {
  const projection = state.ui_types.find(({ id }) => id === row.id);
  assert(Boolean(projection), `missing UI state row: ${row.id}`);
  assert(projection.label === row.term, `UI label drift: ${row.id}`);
  assert(projection.state === row.current_status, `UI lifecycle drift: ${row.id}`);
  assert(projection.development_formation === row.formation, `UI formation drift: ${row.id}`);
  assert(existsSync(resolve(scopeRoot, row.formation)), `missing UI formation: ${row.formation}`);
}

const queue = JSON.parse(
  readFileSync(resolve(scopeRoot, "development/ontology-form-decisions/IMPLEMENTATION-QUEUE.json"), "utf8"),
);
assert(queue.ready.length === 0 && queue.blocked.length === 13, "ontology implementation queue drift");
assert(state.headline.ontology_queue_ready === 0, "state ontology queue projection drift");

const operation = JSON.parse(
  readFileSync(resolve(scopeRoot, "development/remaining-meta-types/candidates/operation.json"), "utf8"),
);
assert(operation.meta_type.id === "DS-D1.4", "Operation identity drift");
assert(operation.architecture_implementation.direct_provider_ids.length === 3, "Operation provider denominator drift");
assert(operation.architecture_implementation.provider_registration_status === "unregistered", "Operation registration drift");
assert(operation.targets.length === 3, "Operation language realization drift");
assert(operation.architecture_relations.materialized_relation_count === 0, "Operation relation materialization drift");
assert(operation.architecture_relations.relation_contract_ids.length === 4, "Operation relation blueprint drift");
assert(operation.lifecycle.admission_status === "not-admitted", "Operation admission drift");
assert(state.operation_contract_state.exact_target_project_enforcement === "missing", "Operation enforcement overclaim");
assert(
  state.operation_contract_state.target_enforcement_gap_id === "GAP-DSV2-META-TYPE-TARGET-ENFORCEMENT",
  "Operation enforcement gap routing drift",
);
for (const obligation of [
  "declared read set",
  "declared write set",
  "declared effect set",
  "guard executes before state mutation",
  "atomic state-and-outbox behavior",
  "explicit failure continuation",
  "no undeclared read, write or effect",
  "typed relationships to Rule, Event and Workflow",
]) {
  assert(state.operation_contract_state.declared_obligations.includes(obligation), `missing Operation state: ${obligation}`);
}
for (const hostile of [
  "undeclared-write.json",
  "undeclared-effect.json",
  "guard-bypass.json",
  "atomicity-removed.json",
  "continuation-mismatch.json",
  "read-set-drift.json",
  "before-state-write-failure.json",
  "between-state-and-outbox-failure.json",
]) {
  assert(
    existsSync(resolve(scopeRoot, `impl/architecture-conformance/families/state-changing-action/hostiles/${hostile}`)),
    `missing Operation hostile control: ${hostile}`,
  );
}

for (const family of [
  "identity-lifecycle",
  "complete-value",
  "finite-vocabulary",
  "state-changing-action",
  "read-model",
  "value-computation",
  "pure-boolean-rule",
  "strategy-selection",
  "ordered-workflow",
  "versioned-interface-boundary",
  "past-tense-event",
  "directional-mapping",
  "lifecycle-state-machine",
]) {
  assert(existsSync(resolve(scopeRoot, `impl/architecture-conformance/families/${family}`)), `missing family root: ${family}`);
}
const familyRoots = readdirSync(resolve(scopeRoot, "impl/architecture-conformance/families"), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();
assert(
  JSON.stringify(familyRoots) ===
    JSON.stringify(
      [
        "complete-value",
        "directional-mapping",
        "effects-connections",
        "enforces-relation",
        "finite-vocabulary",
        "identity-lifecycle",
        "lifecycle-state-machine",
        "orchestration-lifecycle",
        "ordered-workflow",
        "outcome-function",
        "past-tense-event",
        "pure-boolean-rule",
        "read-model",
        "state-change",
        "state-changing-action",
        "strategy-selection",
        "value-computation",
        "versioned-interface-boundary",
      ].sort(),
    ),
  `unrepresented family root change: ${familyRoots.join(", ")}`,
);
assert(familyRoots.length === state.headline.active_backend_family_roots + state.headline.supporting_relationship_family_roots, "family denominator projection drift");
const realizationRoots = readdirSync(resolve(scopeRoot, "impl/architecture-conformance/realizations"), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();
assert(
  JSON.stringify(realizationRoots) ===
    JSON.stringify(
      [
        "calculation",
        "entity",
        "enum",
        "event",
        "interface",
        "mapping",
        "operation",
        "policy",
        "query",
        "relation",
        "rule",
        "state-machine",
        "value-object",
        "workflow",
      ].sort(),
    ),
  `unrepresented realization root change: ${realizationRoots.join(", ")}`,
);

const implPackage = JSON.parse(readFileSync(resolve(scopeRoot, "impl/package.json"), "utf8"));
assert(!implPackage.scripts.validate.includes("factory:test"), "aggregate validation state changed; refresh Craft");
assert(!implPackage.scripts.validate.includes("architecture-conformance/kernel"), "kernel aggregate wiring changed; refresh Craft");

const machineryIds = state.machinery.map(({ context_id }) => context_id);
unique(machineryIds, "machinery context id");
for (const row of state.machinery) {
  const block = contextBlock(ledger, row.context_id);
  assert(block.includes(`stage: ${row.stage}`), `stage projection drift: ${row.context_id}`);
  assert(block.includes(`gate: ${row.gate}`), `gate projection drift: ${row.context_id}`);
  assert(ledger.includes(`- ${row.context_id}`), `meta-type index missing context: ${row.context_id}`);
  assert(view.includes(`\`${row.context_id}\``), `human view missing context: ${row.context_id}`);
}

for (const row of [...state.backend_types, ...state.ui_types]) {
  assert(view.includes(`\`${row.id}\``), `human view missing meta-type: ${row.id}`);
}
assert(ledger.includes("ART-DSV2-META-TYPE-STATE: artifacts[142]"), "state artifact by-id index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-STATE-VALIDATOR: artifacts[143]"), "validator by-id index drift");
assert(ledger.includes("ART-DSV2-REALIZATION-KERNEL-FAMILIES: artifacts[141]"), "kernel artifact by-id index drift");
assert(ledger.includes("DEC-DSV2-META-TYPE-BASELINE: decisions[14]"), "baseline decision by-id index drift");
assert(ledger.includes("DEC-DSV2-META-TYPE-CANONICAL-DOCS-BASELINE-V2: decisions[15]"), "baseline v2 decision by-id index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-BASELINE-DECISION: artifacts[144]"), "baseline decision artifact index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-BASELINE: artifacts[145]"), "baseline artifact index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-BASELINE-VALIDATOR: artifacts[146]"), "baseline validator index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-CLI-PLAN: artifacts[147]"), "CLI plan artifact index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-CURRENT-IMPLEMENTATION: artifacts[148]"), "current implementation artifact index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-ONTOLOGY-STATE: artifacts[149]"), "ontology state artifact index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-ONTOLOGY-PROJECTION: artifacts[150]"), "ontology projection artifact index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-ONTOLOGY-MATERIALIZER: artifacts[151]"), "ontology materializer artifact index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS: artifacts[152]"), "enforcement registry artifact index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS-SCHEMA: artifacts[153]"), "enforcement schema artifact index drift");
assert(ledger.includes("ART-DSV2-META-TYPE-ENFORCEMENT-ASSETS-VALIDATOR: artifacts[154]"), "enforcement validator artifact index drift");
assert(ledger.includes("GAP-DSV2-META-TYPE-TARGET-ENFORCEMENT: gaps[23]"), "target enforcement gap by-id drift");
assert(view.includes("### `GAP-DSV2-META-TYPE-TARGET-ENFORCEMENT`"), "human target enforcement gap missing");
assert(view.includes("## Meta-type state"), "human meta-type state section missing");
assert(view.includes("domainspec-meta-types-current-implemented@2"), "human baseline identity missing");
assert(view.includes("DEC-DSV2-META-TYPE-CANONICAL-DOCS-BASELINE-V2"), "human baseline v2 decision missing");
assert(view.includes(state.canonical_baseline.baseline_digest), "human baseline digest missing");
assert(view.includes("product implementation work"), "human target enforcement classification missing");
assert(view.includes("exact target implementation enforcement: **missing**"), "human claim ceiling missing");
assert(view.includes("30 snapshot binding findings"), "human BMC finding denominator drift");
assert(view.includes("31 authority/audit relationship rows"), "human relationship denominator drift");
assert(view.includes("## Meta-type enforcement assets"), "human enforcement asset section missing");
assert(view.includes("SWU-MTCLI-003"), "human next selectable unit drift");

process.stdout.write(
  `${JSON.stringify({
    status: "pass",
    state_id: state.state_id,
    checks,
    backend_types: state.backend_types.length,
    ui_types: state.ui_types.length,
    realization_rows: realizationRows,
    machinery_rows: state.machinery.length,
    enforcement_assets: enforcementRegistry.assets.length,
    next_selectable_unit: state.enforcement_asset_registry.next_selectable_unit,
    authority_effect: "none",
  }, null, 2)}\n`,
);
