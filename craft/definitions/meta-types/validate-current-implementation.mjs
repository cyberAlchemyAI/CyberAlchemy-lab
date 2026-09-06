#!/usr/bin/env node

import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(here, "../..");
const repoRoot = resolve(projectRoot, "../..");
const statePath = resolve(here, "current-implementation.json");
const schemaPath = resolve(here, "current-implementation.schema.json");
const humanPath = resolve(here, "current-implementation.md");
const ontologyPath = resolve(projectRoot, "ontology/profile.json");
const registryPath = resolve(here, "meta-types.yml");
const definitionsPath = resolve(projectRoot, "definitions/DEFINITIONS.md");
const indexPath = resolve(projectRoot, "definitions/DEFINITIONS-INDEX.md");
let checks = 0;

const assert = (condition, message) => {
  checks += 1;
  if (!condition) throw new Error(message);
};
const sha256 = (path) => createHash("sha256").update(readFileSync(path)).digest("hex");
const canonicalObject = (value) => Object.fromEntries(Object.entries(value).sort(([left], [right]) => left.localeCompare(right)));
const state = JSON.parse(readFileSync(statePath, "utf8"));
const schema = JSON.parse(readFileSync(schemaPath, "utf8"));
const human = readFileSync(humanPath, "utf8");
const registry = readFileSync(registryPath, "utf8");
const definitions = readFileSync(definitionsPath, "utf8");
const index = readFileSync(indexPath, "utf8");
const ontology = JSON.parse(readFileSync(ontologyPath, "utf8"));

const schemaRun = spawnSync("python3", ["-c", [
  "import json,sys",
  "from jsonschema import Draft202012Validator",
  "schema=json.load(open(sys.argv[1],encoding='utf-8'))",
  "value=json.load(open(sys.argv[2],encoding='utf-8'))",
  "Draft202012Validator.check_schema(schema)",
  "Draft202012Validator(schema).validate(value)",
].join(";"), schemaPath, statePath], { encoding: "utf8" });
assert(schemaRun.status === 0, `current-state schema validation failed:${(schemaRun.stderr || schemaRun.stdout).trim()}`);

const manifestPath = resolve(repoRoot, state.baseline.manifest);
const ownerDecisionPath = resolve(repoRoot, state.baseline.owner_decision);
assert(existsSync(manifestPath), "current baseline manifest missing");
assert(existsSync(ownerDecisionPath), "current baseline owner decision missing");
const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
assert(state.baseline.id === "domainspec-meta-types-current-implemented@10", "current baseline identity is not @10");
assert(sha256(manifestPath) === state.baseline.manifest_sha256, "current baseline manifest file digest drift");
assert(sha256(ownerDecisionPath) === state.baseline.owner_decision_sha256, "current baseline decision digest drift");
assert(manifest.baseline_id === state.baseline.id, "current baseline identity drift");
assert(manifest.baseline_digest === state.baseline.baseline_digest, "current baseline body digest drift");
assert(JSON.stringify(canonicalObject(manifest.denominators)) === JSON.stringify(canonicalObject(state.scope)), "current baseline scope drift");

const expectedIds = manifest.backend_meta_types.map(({ id }) => id).sort();
const actualIds = state.backend_meta_types.map(({ id }) => id).sort();
assert(JSON.stringify(expectedIds) === JSON.stringify(actualIds), "current backend meta-type set drift");
assert(new Set(actualIds).size === 13, "duplicate current backend meta-type id");
for (const row of state.backend_meta_types) {
  const realized = manifest.realization_rows.filter(({ meta_type_id }) => meta_type_id === row.id);
  assert(realized.length === row.realization_rows, `realization count drift:${row.id}`);
  assert(
    JSON.stringify(realized.map(({ language }) => language).sort()) === JSON.stringify(row.realization_languages),
    `realization language drift:${row.id}`,
  );
}

for (const obligation of [
  "declared read set",
  "declared write set",
  "declared effect set",
  "guard executes before state mutation",
  "atomic state-and-outbox behavior",
  "explicit failure continuation",
  "no undeclared read, write or effect",
  "typed relationships to Rule, Event and Workflow",
]) assert(state.operation_contract.obligations.includes(obligation), `missing Operation obligation:${obligation}`);

assert(registry.includes("current_implementation_state: current-implementation.json"), "DS-D1 registry current-state pointer missing");
for (const id of Array.from({ length: 19 }, (_, index) => `domainspec-v2-D${index + 31}`)) {
  assert(definitions.includes(`## ${id}.`), `definition card missing:${id}`);
  assert(index.includes(`\`${id}\``), `definition index row missing:${id}`);
}
assert(ontology.current_implementation?.baseline_id === state.baseline.id, "ontology current baseline identity drift");
assert(ontology.current_implementation?.state_ref === "projects/domainspec-v2/definitions/meta-types/current-implementation.json", "ontology current-state ref drift");
assert(human.includes(state.baseline.id), "human current-state identity drift");
assert(human.includes(state.baseline.baseline_digest), "human current-state digest drift");
assert(human.includes("durable compensation model is admitted"), "human product frontier missing");
assert(state.compensation_contract.definition_id === "domainspec-v2-D36", "compensation definition drift");
assert(state.compensation_contract.recovery_intent_definition_id === "domainspec-v2-D37", "Recovery Intent definition drift");
assert(definitions.includes("## domainspec-v2-D37. Recovery Intent"), "Recovery Intent canonical label drift");
assert(JSON.stringify(state.compensation_contract.supporting_definition_ids) === JSON.stringify(Array.from({ length: 8 }, (_, index) => `domainspec-v2-D${index + 37}`)), "compensation supporting definition drift");
assert(state.compensation_contract.executor_owner === "external-runtime", "compensation executor owner drift");
assert(state.compensation_contract.durable_model_admitted === true, "durable compensation model admission missing");
assert(state.compensation_contract.replay_protection_contract === true, "compensation replay protection missing");
assert(state.compensation_contract.claim_and_lease_contract === true, "compensation claim/lease contract missing");
assert(state.claim_ceiling.generated_target_conformance === true, "generated target conformance admission missing");
assert(state.target_conformance.status === "admitted-static-generated-target", "target conformance state drift");
assert(JSON.stringify(state.target_conformance.profiles) === JSON.stringify(["python", "rust", "typescript"]), "target conformance profiles drift");
assert(state.claim_ceiling.durable_compensation_model_admitted === true, "durable compensation semantic admission missing");
assert(JSON.stringify(state.infrastructure_binding_contract.definition_ids) === JSON.stringify(Array.from({ length: 5 }, (_, index) => `domainspec-v2-D${index + 45}`)), "infrastructure binding definition drift");
assert(state.infrastructure_binding_contract.code_contract_model === "concern-specific-no-universal-port", "universal Port model reintroduced");
assert(state.infrastructure_binding_contract.interface_reference_policy === "optional-only-for-actual-domain-interface", "Interface reference policy drift");
assert(JSON.stringify(state.infrastructure_binding_contract.bindings) === JSON.stringify(["persistence", "transaction-guarantee", "failure-outcome", "durable-workflow-runtime"]), "infrastructure binding set drift");
assert(state.infrastructure_binding_contract.provider_selection === "open", "provider selection inflated");
assert(state.infrastructure_binding_contract.system_profile_id === "domainspec.system-integration-profile/provider-neutral-v1", "system-integration profile drift");
assert(state.infrastructure_binding_contract.system_profile_digest === "4b223f7ad48512fbd9568ff427de7d151792567bb96d64e65d869e094b82a5ab", "system-integration profile digest drift");
assert(JSON.stringify(state.infrastructure_binding_contract.language_profiles) === JSON.stringify(["python", "rust", "typescript"]), "system-integration language profile drift");
assert(state.infrastructure_binding_contract.contract_profile_implementation === true, "system-integration contract profile implementation missing");
assert(state.infrastructure_binding_contract.cli_binding_formation === true && state.infrastructure_binding_contract.cli_exact_observation === true, "system-integration CLI formation or observation missing");
for (const [role, reference] of Object.entries(state.infrastructure_binding_contract.implementation_evidence)) {
  const evidencePath = resolve(repoRoot, reference.path);
  assert(existsSync(evidencePath), `system-integration evidence missing:${role}`);
  assert(sha256(evidencePath) === reference.sha256, `system-integration evidence digest drift:${role}`);
}
assert(state.infrastructure_binding_contract.provider_runtime_implementation === false, "provider runtime implementation inflated");
assert(state.infrastructure_binding_contract.runtime_guarantees_observed === false, "provider runtime guarantee inflated");
assert(state.claim_ceiling.infrastructure_binding_model_admitted === true, "infrastructure binding admission missing");
assert(state.claim_ceiling.durable_workflow_runtime_binding_admitted === true, "durable workflow runtime binding admission missing");
assert(state.claim_ceiling.durable_recovery_architecture_admitted === true, "durable recovery architecture admission missing");
assert(state.claim_ceiling.system_integration_contract_profiles_implemented === true, "system-integration contract profiles missing");
assert(state.claim_ceiling.system_integration_provider_runtime_implemented === false, "system-integration provider runtime claim inflated");
assert(state.claim_ceiling.durable_compensation_dispatch_implemented === false, "durable compensation implementation boundary widened");

process.stdout.write(`${JSON.stringify({
  status: "pass",
  state_id: state.state_id,
  baseline_id: state.baseline.id,
  baseline_digest: state.baseline.baseline_digest,
  checks,
  backend_meta_types: state.backend_meta_types.length,
  realization_rows: state.scope.realization_rows,
  authority_effect: state.authority_effect,
}, null, 2)}\n`);
