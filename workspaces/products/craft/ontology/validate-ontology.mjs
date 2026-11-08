#!/usr/bin/env node

import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "../../..");
const requireReceipt = process.argv.includes("--require-receipt");
let checks = 0;

function assert(condition, message) {
  checks += 1;
  if (!condition) throw new Error(message);
}

function readJson(relativePath) {
  return JSON.parse(readFileSync(resolve(here, relativePath), "utf8"));
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function exactKeys(value, expected, label) {
  assert(value && typeof value === "object" && !Array.isArray(value), `${label}:object-required`);
  assert(JSON.stringify(Object.keys(value).sort()) === JSON.stringify([...expected].sort()), `${label}:closed-shape-drift`);
}

function unique(values, label) {
  assert(new Set(values).size === values.length, `${label}:duplicate`);
}

const profile = readJson("profile.json");
const sourceDocument = readJson("sources.json");
const nodeDocument = readJson("nodes.json");
const relationDocument = readJson("relations.json");
const residueDocument = readJson("residue.json");
const schema = readJson("schema/ontology-package.schema.json");
const schemaAmendments = profile.package_files.schema_amendments.map(readJson);

exactKeys(profile, ["schema_version", "ontology_id", "status", "ontology_type", "ontology_type_selection", "branches", "bridge", "owner_route", "visibility", "authority_effect", "authority_boundaries", "current_implementation", "package_files"], "profile");
assert(profile.schema_version === "domainspec.product-ontology-profile/v1", "profile:schema-version");
assert(profile.ontology_id === "domainspec-product-ontology@1", "profile:ontology-id");
assert(profile.status === "canonical", "profile:status");
assert(profile.ontology_type === "business-system-bridge", "profile:ontology-type");
assert(profile.ontology_type_selection.source === "inferred" && profile.ontology_type_selection.confidence === "high", "profile:type-selection");
assert(JSON.stringify(profile.branches) === JSON.stringify(["business", "system"]), "profile:branches");
assert(profile.bridge === "business-system", "profile:bridge");
assert(profile.visibility === "private", "profile:visibility");
assert(profile.authority_effect === "project-local-canonical-product-read-model", "profile:authority-effect");
exactKeys(profile.package_files, ["sources", "nodes", "relations", "residue", "schema", "schema_amendments", "validator", "views", "receipts"], "profile:package-files");
assert(schema.$id === "domainspec://schemas/product-ontology-package/v1", "schema:identity");
for (const definition of ["source", "node", "relation", "residue", "receipt"]) assert(schema.$defs?.[definition], `schema:missing-${definition}`);
assert(schemaAmendments.length === 4, "schema-amendment:count");
unique(schemaAmendments.map(({ amendment_id }) => amendment_id), "schema-amendment:id");
for (const amendment of schemaAmendments) {
  exactKeys(amendment, ["schema_version", "amendment_id", "recorded_at", "ontology_id", "decision_ref", "prior_package", "changes", "migration_impact", "authority_effect"], `schema-amendment:${amendment.amendment_id}`);
  assert(amendment.schema_version === "domainspec.product-ontology-schema-amendment/v1", "schema-amendment:schema-version");
  assert(amendment.ontology_id === profile.ontology_id, "schema-amendment:ontology-id");
}
const businessRelationAmendment = schemaAmendments.find(({ amendment_id }) => amendment_id === "dsv2.ontology.schema-amendment.business-relations-residue-node-bindings");
assert(businessRelationAmendment?.prior_package.package_digest === "73e6f3a3f76583a0aab95605295619f52d4f8f7b53f796e79723747ab2464d2b", "schema-amendment:business-relations:prior-digest");
assert(businessRelationAmendment.changes.some(({ record }) => record === "relation"), "schema-amendment:business-relations:relation-change-missing");
assert(businessRelationAmendment.changes.some(({ record }) => record === "residue"), "schema-amendment:business-relations:residue-change-missing");
const designedSystemAmendment = schemaAmendments.find(({ amendment_id }) => amendment_id === "dsv2.ontology.schema-amendment.designed-system-components");
assert(designedSystemAmendment?.prior_package.package_digest === "74867151ed61403ec61326a58ed5462569f925ff70649db81af7bb00eb5ca343", "schema-amendment:designed-system:prior-digest");
for (const record of ["node", "source", "relation", "residue"]) assert(designedSystemAmendment.changes.some((change) => change.record === record), `schema-amendment:designed-system:${record}-change-missing`);
assert(designedSystemAmendment.migration_impact.new_system_nodes === 13, "schema-amendment:designed-system:node-count");
assert(designedSystemAmendment.migration_impact.new_bridge_relations === 9, "schema-amendment:designed-system:bridge-count");
const infrastructureBindingAmendment = schemaAmendments.find(({ amendment_id }) => amendment_id === "dsv2.ontology.schema-amendment.infrastructure-binding-contracts");
assert(infrastructureBindingAmendment?.prior_package.package_digest === "03728315de6e1fd7f786504be9545aab8f012fcf2e1a70d58b235e92d1132c38", "schema-amendment:infrastructure-binding:prior-digest");
assert(infrastructureBindingAmendment.migration_impact.new_system_nodes === 10, "schema-amendment:infrastructure-binding:node-count");
assert(infrastructureBindingAmendment.migration_impact.new_system_relations === 13, "schema-amendment:infrastructure-binding:relation-count");
for (const record of ["node", "source", "relation", "residue"]) assert(infrastructureBindingAmendment.changes.some((change) => change.record === record), `schema-amendment:infrastructure-binding:${record}-change-missing`);
const repositoryBridgeAmendment = schemaAmendments.find(({ amendment_id }) => amendment_id === "dsv2.ontology.schema-amendment.repository-bridge-non-collapse");
assert(repositoryBridgeAmendment?.prior_package.package_digest === "d18e84c7a5e28a8e0974778032c8b5409dd16243b1eebf8b106a9707a2862e05", "schema-amendment:repository-bridge:prior-digest");
assert(repositoryBridgeAmendment.migration_impact.changed_bridge_relations === 2, "schema-amendment:repository-bridge:relation-count");
assert(repositoryBridgeAmendment.changes.length === 1 && repositoryBridgeAmendment.changes[0].record === "relation", "schema-amendment:repository-bridge:shape");

exactKeys(sourceDocument, ["schema_version", "ontology_id", "sources"], "sources-document");
assert(sourceDocument.schema_version === "domainspec.product-ontology-sources/v1", "sources:schema-version");
const sources = sourceDocument.sources;
unique(sources.map(({ source_id }) => source_id), "sources:id");
const sourceById = new Map(sources.map((source) => [source.source_id, source]));
for (const source of sources) {
  exactKeys(source, ["source_id", "path", "sha256", "branch", "role", "authority_effect"], `source:${source.source_id}`);
  assert(/^[a-f0-9]{64}$/.test(source.sha256), `source:${source.source_id}:digest-shape`);
  assert(["business", "system", "mixed"].includes(source.branch), `source:${source.source_id}:branch`);
  const path = resolve(repoRoot, source.path);
  assert(existsSync(path), `source:${source.source_id}:missing:${source.path}`);
  assert(sha256(readFileSync(path)) === source.sha256, `source:${source.source_id}:stale:${source.path}`);
}

assert(sourceById.get("source.infrastructure-binding-tower")?.authority_effect === "none", "integration-research:tower-authority-inflation");
assert(sourceById.get("source.system-integration-r2")?.authority_effect === "none", "integration-research:revision2-authority-inflation");
const infrastructureAdmissionSource = sourceById.get("source.infrastructure-binding-admission");
assert(infrastructureAdmissionSource?.authority_effect === "owns-d45-through-d49-admission", "integration-research:admission-source-authority");
const infrastructureAdmission = JSON.parse(readFileSync(resolve(repoRoot, infrastructureAdmissionSource.path), "utf8"));
assert(infrastructureAdmission.decision_id === "DSV2-OWNER-INFRASTRUCTURE-BINDING-ARCHITECTURE-2026-08-30", "integration-research:admission-decision-id");
assert(infrastructureAdmission.selected_option?.id === "admit-concern-specific-contracts-and-explicit-bindings", "integration-research:admission-selected-option");
assert(JSON.stringify(infrastructureAdmission.decision_source?.research_refs) === JSON.stringify([
  sourceById.get("source.infrastructure-binding-tower").path,
  sourceById.get("source.system-integration-r2").path,
]), "integration-research:admission-research-ref-drift");
assert(Array.isArray(infrastructureAdmission.remaining_owner_decisions) && infrastructureAdmission.remaining_owner_decisions.length === 0, "integration-research:semantic-decision-residue");
assert(infrastructureAdmission.authority_effect === "project-local-canonical-infrastructure-binding-and-architecture-admission", "integration-research:admission-authority-effect");
for (const requiredInvariant of [
  "no universal code-level Port",
  "Interface reference is optional",
  "Repository and Unit of Work code contracts remain distinct",
  "Failure Outcome Binding classifies failure but does not choose Retry",
  "without selecting a provider",
  "No database, ORM, broker",
]) assert(infrastructureAdmission.invariants.some((invariant) => invariant.includes(requiredInvariant)), `integration-research:admission-invariant-missing:${requiredInvariant}`);

const workflowRecoveryProfileSource = sourceById.get("source.workflow-recovery-profile");
assert(workflowRecoveryProfileSource, "workflow-recovery-profile:source-missing");
const workflowRecoveryProfile = JSON.parse(readFileSync(resolve(repoRoot, workflowRecoveryProfileSource.path), "utf8"));
assert(workflowRecoveryProfile.schema_version === "domainspec.workflow-recovery-profile/v1", "workflow-recovery-profile:schema-version");
assert(workflowRecoveryProfile.status === "candidate-local-validated", "workflow-recovery-profile:status-inflation");
assert(workflowRecoveryProfile.meta_type_id === "DS-D1.9" && workflowRecoveryProfile.adds_meta_type === false, "workflow-recovery-profile:meta-type-drift");
assert(JSON.stringify(workflowRecoveryProfile.definition_ids) === JSON.stringify(["domainspec-v2-D36", "domainspec-v2-D37", "domainspec-v2-D40"]), "workflow-recovery-profile:definition-set-drift");
assert(JSON.stringify(workflowRecoveryProfile.relationship_contract) === JSON.stringify({
  source_type: "Workflow",
  relationship: "orchestrates",
  target_type: "Operation",
  new_relationship_verb: false,
  preflight_before_invocation: true,
}), "workflow-recovery-profile:relationship-contract-drift");
assert(JSON.stringify(workflowRecoveryProfile.language_profiles.map(({ language }) => language)) === JSON.stringify(["typescript", "python", "rust"]), "workflow-recovery-profile:language-set-drift");
const workflowRecoveryLanguageSources = new Map([
  ["typescript", { target: "source.compensation-reference", test: "source.compensation-typescript-test" }],
  ["python", { target: "source.compensation-python-reference", test: "source.compensation-python-test" }],
  ["rust", { target: "source.compensation-rust-reference", test: "source.compensation-rust-test" }],
]);
for (const languageProfile of workflowRecoveryProfile.language_profiles) {
  const expectedSources = workflowRecoveryLanguageSources.get(languageProfile.language);
  assert(expectedSources, `workflow-recovery-profile:unknown-language:${languageProfile.language}`);
  for (const role of ["target", "test"]) {
    const source = sourceById.get(expectedSources[role]);
    const reference = languageProfile[role];
    assert(source?.path === reference.path, `workflow-recovery-profile:${languageProfile.language}:${role}:path-drift`);
    assert(source?.sha256 === reference.sha256, `workflow-recovery-profile:${languageProfile.language}:${role}:digest-drift`);
  }
  for (const role of ["target", "test", "workflow_binding"]) {
    const reference = languageProfile[role];
    const bytes = readFileSync(resolve(repoRoot, reference.path));
    assert(bytes.length === reference.size_bytes, `workflow-recovery-profile:${languageProfile.language}:${role}:size-drift`);
    assert(sha256(bytes) === reference.sha256, `workflow-recovery-profile:${languageProfile.language}:${role}:source-drift`);
  }
}
for (const flag of ["workflow_recovery_planning", "exact_binding_preflight", "in_process_invocation"]) {
  assert(workflowRecoveryProfile.claim_ceiling[flag] === true, `workflow-recovery-profile:missing-observed-capability:${flag}`);
}
for (const flag of ["durable_dispatch", "claim", "lease", "durable_attempt", "persisted_retry", "terminal_disposition", "restart_recovery", "publication", "deployment", "production"]) {
  assert(workflowRecoveryProfile.claim_ceiling[flag] === false, `workflow-recovery-profile:claim-inflation:${flag}`);
}
assert(workflowRecoveryProfile.authority_effect === "none", "workflow-recovery-profile:authority-effect");

exactKeys(nodeDocument, ["schema_version", "ontology_id", "nodes"], "nodes-document");
assert(nodeDocument.schema_version === "domainspec.product-ontology-nodes/v1", "nodes:schema-version");
const nodes = nodeDocument.nodes;
unique(nodes.map(({ node_id }) => node_id), "nodes:id");
const nodeById = new Map(nodes.map((node) => [node.node_id, node]));
for (const node of nodes) {
  exactKeys(node, ["node_id", "label", "branch", "role", "status", "source_refs", "summary", "forbidden_inference"], `node:${node.node_id}`);
  assert(["business", "system"].includes(node.branch), `node:${node.node_id}:branch`);
  assert(["canonical", "implemented", "evidence-bound", "designed"].includes(node.status), `node:${node.node_id}:status`);
  if (node.status === "designed") assert(node.branch === "system", `node:${node.node_id}:designed-non-system`);
  assert(node.source_refs.length > 0, `node:${node.node_id}:sources-empty`);
  unique(node.source_refs, `node:${node.node_id}:source-ref`);
  for (const ref of node.source_refs) assert(sourceById.has(ref), `node:${node.node_id}:unknown-source:${ref}`);
}
assert(nodes.some(({ branch }) => branch === "business"), "nodes:business-branch-empty");
assert(nodes.some(({ branch }) => branch === "system"), "nodes:system-branch-empty");

exactKeys(relationDocument, ["schema_version", "ontology_id", "relations"], "relations-document");
assert(relationDocument.schema_version === "domainspec.product-ontology-relations/v1", "relations:schema-version");
const relations = relationDocument.relations;
unique(relations.map(({ relation_id }) => relation_id), "relations:id");
const allowedRelations = new Set(["realized_by", "depends_on", "constrained_by", "observed_by", "tested_by", "drifts_from", "traced_to"]);
for (const relation of relations) {
  exactKeys(relation, ["relation_id", "type", "from", "to", "branch", "evidence", "authority_effect", "forbidden_inference"], `relation:${relation.relation_id}`);
  assert(allowedRelations.has(relation.type), `relation:${relation.relation_id}:type`);
  assert(nodeById.has(relation.from) && nodeById.has(relation.to), `relation:${relation.relation_id}:endpoint-closure`);
  assert(relation.from !== relation.to, `relation:${relation.relation_id}:self-edge`);
  exactKeys(relation.evidence, ["business_refs", "system_refs"], `relation:${relation.relation_id}:evidence`);
  unique(relation.evidence.business_refs, `relation:${relation.relation_id}:business-evidence`);
  unique(relation.evidence.system_refs, `relation:${relation.relation_id}:system-evidence`);
  for (const ref of relation.evidence.business_refs) assert(sourceById.get(ref)?.branch === "business", `relation:${relation.relation_id}:business-source-polarity:${ref}`);
  for (const ref of relation.evidence.system_refs) assert(sourceById.get(ref)?.branch === "system", `relation:${relation.relation_id}:system-source-polarity:${ref}`);
  const fromBranch = nodeById.get(relation.from).branch;
  const toBranch = nodeById.get(relation.to).branch;
  if (relation.branch === "bridge") {
    assert(fromBranch !== toBranch, `relation:${relation.relation_id}:bridge-polarity`);
    assert(relation.evidence.business_refs.length > 0, `relation:${relation.relation_id}:business-evidence-empty`);
    assert(relation.evidence.system_refs.length > 0, `relation:${relation.relation_id}:system-evidence-empty`);
  } else if (relation.branch === "system") {
    assert(relation.branch === "system" && fromBranch === "system" && toBranch === "system", `relation:${relation.relation_id}:system-polarity`);
    assert(relation.evidence.business_refs.length === 0, `relation:${relation.relation_id}:system-business-evidence`);
    assert(relation.evidence.system_refs.length > 0, `relation:${relation.relation_id}:system-evidence-empty`);
  } else {
    assert(relation.branch === "business" && fromBranch === "business" && toBranch === "business", `relation:${relation.relation_id}:business-polarity`);
    assert(relation.evidence.business_refs.length > 0, `relation:${relation.relation_id}:business-evidence-empty`);
    assert(relation.evidence.system_refs.length === 0, `relation:${relation.relation_id}:business-system-evidence`);
  }
}

exactKeys(residueDocument, ["schema_version", "ontology_id", "residue"], "residue-document");
assert(residueDocument.schema_version === "domainspec.product-ontology-residue/v1", "residue:schema-version");
const residue = residueDocument.residue;
unique(residue.map(({ residue_id }) => residue_id), "residue:id");
for (const item of residue) {
  exactKeys(item, ["residue_id", "status", "summary", "owner_route", "source_refs", "node_refs", "forbidden_inference"], `residue:${item.residue_id}`);
  assert(item.status === "open", `residue:${item.residue_id}:status`);
  for (const ref of item.source_refs) assert(sourceById.has(ref), `residue:${item.residue_id}:unknown-source:${ref}`);
  unique(item.node_refs, `residue:${item.residue_id}:node-ref`);
  for (const ref of item.node_refs) assert(nodeById.has(ref), `residue:${item.residue_id}:unknown-node:${ref}`);
}

const manifest = JSON.parse(readFileSync(resolve(repoRoot, profile.authority_boundaries.implementation_selection), "utf8"));
const currentState = JSON.parse(readFileSync(resolve(repoRoot, profile.current_implementation.state_ref), "utf8"));
assert(manifest.baseline_id === profile.current_implementation.baseline_id, "baseline:profile-id-drift");
assert(manifest.baseline_digest === profile.current_implementation.baseline_digest, "baseline:profile-digest-drift");
assert(currentState.baseline.id === profile.current_implementation.baseline_id, "baseline:state-id-drift");
assert(currentState.baseline.baseline_digest === profile.current_implementation.baseline_digest, "baseline:state-digest-drift");
assert(currentState.claim_ceiling.generated_target_conformance === true, "baseline:target-conformance-not-admitted");
assert(currentState.compensation_contract.definition_id === "domainspec-v2-D36", "compensation:definition-not-admitted");
assert(currentState.compensation_contract.executor_owner === "external-runtime", "compensation:executor-owner-drift");
assert(currentState.compensation_contract.durable_model_admitted === true, "compensation:durable-model-not-admitted");
assert(currentState.compensation_contract.replay_protection_contract === true, "compensation:replay-protection-absent");
assert(currentState.compensation_contract.claim_and_lease_contract === true, "compensation:claim-lease-contract-absent");
assert(currentState.compensation_contract.durable_dispatch_implemented === false, "compensation:durable-dispatch-inflation");
assert(JSON.stringify(currentState.infrastructure_binding_contract.definition_ids) === JSON.stringify(Array.from({ length: 5 }, (_, index) => `domainspec-v2-D${index + 45}`)), "infrastructure-binding:definition-set-drift");
assert(currentState.infrastructure_binding_contract.code_contract_model === "concern-specific-no-universal-port", "infrastructure-binding:universal-port-reintroduced");
assert(currentState.infrastructure_binding_contract.provider_selection === "open", "infrastructure-binding:provider-selection-inflated");
assert(currentState.infrastructure_binding_contract.system_profile_id === "domainspec.system-integration-profile/provider-neutral-v1", "infrastructure-binding:profile-drift");
assert(currentState.infrastructure_binding_contract.contract_profile_implementation === true, "infrastructure-binding:profile-implementation-missing");
assert(currentState.infrastructure_binding_contract.cli_binding_formation === true && currentState.infrastructure_binding_contract.cli_exact_observation === true, "infrastructure-binding:cli-formation-or-observation-missing");
assert(currentState.infrastructure_binding_contract.provider_runtime_implementation === false, "infrastructure-binding:provider-runtime-inflated");
assert(currentState.infrastructure_binding_contract.runtime_guarantees_observed === false, "infrastructure-binding:runtime-guarantee-inflated");

const definitions = readFileSync(resolve(repoRoot, "projects/domainspec-v2/definitions/DEFINITIONS.md"), "utf8");
const definitionsIndex = readFileSync(resolve(repoRoot, "projects/domainspec-v2/definitions/DEFINITIONS-INDEX.md"), "utf8");
const metaTypes = readFileSync(resolve(repoRoot, "projects/domainspec-v2/definitions/meta-types/meta-types.yml"), "utf8");
const relationships = readFileSync(resolve(repoRoot, "projects/domainspec-v2/definitions/relationships/relationships.yml"), "utf8");
for (const id of Array.from({ length: 9 }, (_, index) => `domainspec-v2-D${index + 36}`)) {
  assert(definitions.includes(`## ${id}.`), `compensation:definition-card-missing:${id}`);
  assert(definitionsIndex.includes(`\`${id}\``), `compensation:index-row-missing:${id}`);
}
for (const id of Array.from({ length: 5 }, (_, index) => `domainspec-v2-D${index + 45}`)) {
  assert(definitions.includes(`## ${id}.`), `infrastructure-binding:definition-card-missing:${id}`);
  assert(definitionsIndex.includes(`\`${id}\``), `infrastructure-binding:index-row-missing:${id}`);
  const start = definitions.indexOf(`## ${id}.`);
  const next = definitions.indexOf("\n## ", start + 4);
  const section = definitions.slice(start, next === -1 ? definitions.length : next);
  for (const evidenceLocator of [
    "2026-08-20-operation-workflow-infrastructure-binding-patterns/TOWER.md",
    "20260813T153029Z-system-integration-contract-layer-revision-2/RESULT.md",
    "OWNER-INFRASTRUCTURE-BINDING-ARCHITECTURE-ADMISSION.json",
  ]) assert(section.includes(evidenceLocator), `infrastructure-binding:definition-provenance-missing:${id}:${evidenceLocator}`);
}
assert(metaTypes.includes("role: forward-recovery-operation"), "compensation:operation-role-missing");
assert(metaTypes.includes("adds no DS-D1 type or DS-D8 verb"), "compensation:non-collapse-boundary-missing");
assert(relationships.includes('"id": "orchestrates"'), "compensation:orchestrates-authority-missing");
for (const label of ["Workflow Compensation", "Recovery Intent", "Durable Compensation Dispatch", "Compensation Execution Attempt", "Compensation Invocation Identity", "Compensation Claim", "Compensation Claim Lease", "Compensation Retry", "Compensation Terminal Disposition"]) {
  assert(!nodes.some((node) => node.label === label && node.role === "meta-type"), `compensation:invented-meta-type:${label}`);
}
assert(nodes.find(({ node_id }) => node_id === "dsv2.compensation.intent")?.label === "Recovery Intent", "compensation:Recovery-Intent-label-drift");
const expectedBusinessDependencies = [
  ["dsv2.product.workflow-compensation", "dsv2.compensation.intent"],
  ["dsv2.product.workflow-compensation", "dsv2.compensation.dispatch"],
  ["dsv2.compensation.dispatch", "dsv2.compensation.attempt"],
  ["dsv2.compensation.attempt", "dsv2.compensation.invocation-identity"],
  ["dsv2.compensation.dispatch", "dsv2.compensation.claim"],
  ["dsv2.compensation.claim", "dsv2.compensation.claim-lease"],
  ["dsv2.compensation.dispatch", "dsv2.compensation.retry"],
  ["dsv2.compensation.dispatch", "dsv2.compensation.terminal-disposition"],
];
for (const [from, to] of expectedBusinessDependencies) {
  assert(relations.some((relation) => relation.from === from && relation.to === to && relation.type === "depends_on" && relation.branch === "business"), `compensation:business-binding-missing:${from}:${to}`);
}
for (const target of ["dsv2.system.compensation-planner", "dsv2.system.compensation-executor"]) {
  assert(relations.some(({ from, to, type }) => from === "dsv2.product.workflow-compensation" && to === target && type === "realized_by"), `compensation:bridge-missing:${target}`);
}
for (const [from, to] of [
  ["dsv2.compensation.intent", "dsv2.system.compensation-planner"],
  ["dsv2.compensation.invocation-identity", "dsv2.system.compensation-planner"],
]) assert(relations.some((relation) => relation.from === from && relation.to === to && relation.type === "realized_by"), `compensation:partial-realization-bridge-missing:${from}:${to}`);
for (const nodeId of ["dsv2.system.workflow-runtime", "dsv2.system.compensation-planner", "dsv2.system.compensation-executor", "dsv2.system.operation-binding-resolver-contract"]) {
  assert(nodeById.get(nodeId)?.source_refs.includes("source.workflow-recovery-profile"), `workflow-recovery-profile:node-evidence-missing:${nodeId}`);
}
for (const relationId of [
  "dsv2.bridge.compensation-realized-by-planner",
  "dsv2.bridge.compensation-realized-by-executor",
  "dsv2.bridge.recovery-intent-realized-by-planner",
  "dsv2.bridge.invocation-identity-realized-by-planner",
  "dsv2.system.workflow-depends-on-planner",
  "dsv2.system.executor-depends-on-planner",
  "dsv2.system.executor-depends-on-binding-resolver",
  "dsv2.system.worker-depends-on-executor",
]) {
  assert(relations.find(({ relation_id }) => relation_id === relationId)?.evidence.system_refs.includes("source.workflow-recovery-profile"), `workflow-recovery-profile:relation-evidence-missing:${relationId}`);
}
const expectedDesignedBridges = [
  ["dsv2.product.workflow-compensation", "dsv2.system.durable-recovery-worker"],
  ["dsv2.compensation.attempt", "dsv2.system.recovery-attempt-journal"],
  ["dsv2.compensation.invocation-identity", "dsv2.system.operation-invocation-ledger"],
  ["dsv2.compensation.claim", "dsv2.system.recovery-claim-authority"],
  ["dsv2.compensation.claim-lease", "dsv2.system.recovery-lease-service"],
  ["dsv2.compensation.retry", "dsv2.system.recovery-retry-scheduler"],
  ["dsv2.compensation.terminal-disposition", "dsv2.system.recovery-terminal-recorder"],
];
for (const [from, to] of expectedDesignedBridges) {
  const relation = relations.find((candidate) => candidate.from === from && candidate.to === to && candidate.type === "realized_by" && candidate.branch === "bridge");
  assert(relation, `compensation:designed-bridge-missing:${from}:${to}`);
  assert(nodeById.get(to)?.status === "designed", `compensation:designed-bridge-status-inflation:${to}`);
  assert(relation.authority_effect === "designed-traceability-only", `compensation:designed-bridge-authority:${from}:${to}`);
}
const integrationBridgeTargets = new Map([
  ["dsv2.integration.dependency-contract", "dsv2.system.recovery-architecture-profile"],
  ["dsv2.integration.persistence-binding", "dsv2.system.recovery-persistence-binding"],
  ["dsv2.integration.transaction-guarantee-binding", "dsv2.system.recovery-transaction-guarantee-binding"],
  ["dsv2.integration.failure-outcome-binding", "dsv2.system.recovery-failure-outcome-binding"],
  ["dsv2.integration.durable-workflow-runtime-binding", "dsv2.system.durable-workflow-runtime-binding"],
]);
for (const [businessNodeId, systemNodeId] of integrationBridgeTargets) {
  const businessNode = nodeById.get(businessNodeId);
  assert(businessNode?.branch === "business" && businessNode.status === "canonical", `integration-research:business-node-state:${businessNodeId}`);
  for (const sourceId of ["source.definitions", "source.infrastructure-binding-admission", "source.infrastructure-binding-tower", "source.system-integration-r2"]) {
    assert(businessNode.source_refs.includes(sourceId), `integration-research:business-node-source:${businessNodeId}:${sourceId}`);
  }
  const systemNode = nodeById.get(systemNodeId);
  assert(systemNode?.branch === "system", `integration-research:system-node-state:${systemNodeId}`);
  for (const sourceId of ["source.infrastructure-binding-admission", "source.infrastructure-binding-tower", "source.system-integration-r2"]) {
    assert(systemNode.source_refs.includes(sourceId), `integration-research:system-node-source:${systemNodeId}:${sourceId}`);
  }
  const bridge = relations.find((relation) => relation.from === businessNodeId && relation.to === systemNodeId && relation.type === "realized_by" && relation.branch === "bridge");
  assert(bridge, `integration-research:bridge-missing:${businessNodeId}:${systemNodeId}`);
  for (const sourceId of ["source.definitions", "source.infrastructure-binding-admission"]) assert(bridge.evidence.business_refs.includes(sourceId), `integration-research:bridge-business-evidence:${businessNodeId}:${sourceId}`);
  for (const sourceId of ["source.infrastructure-binding-tower", "source.system-integration-r2", "source.durable-recovery-architecture"]) assert(bridge.evidence.system_refs.includes(sourceId), `integration-research:bridge-system-evidence:${businessNodeId}:${sourceId}`);
  for (const sourceId of ["source.system-integration-profile", "source.system-integration-compiler", "source.system-integration-tests"]) assert(bridge.evidence.system_refs.includes(sourceId), `system-integration:bridge-evidence:${businessNodeId}:${sourceId}`);
}
const systemIntegrationFormationNodes = [
  "dsv2.system.recovery-coordination-repository-contract",
  "dsv2.system.recovery-coordination-unit-of-work-contract",
  "dsv2.system.recovery-persistence-binding",
  "dsv2.system.recovery-transaction-guarantee-binding",
  "dsv2.system.recovery-failure-outcome-binding",
  "dsv2.system.durable-workflow-runtime-binding",
  "dsv2.system.recovery-clock-contract",
  "dsv2.system.recovery-wakeup-contract",
];
for (const nodeId of systemIntegrationFormationNodes) {
  const node = nodeById.get(nodeId);
  assert(node?.status === "implemented", `system-integration:formation-node-status:${nodeId}`);
  for (const sourceId of ["source.system-integration-profile", "source.system-integration-compiler", "source.system-integration-tests"]) assert(node.source_refs.includes(sourceId), `system-integration:formation-node-evidence:${nodeId}:${sourceId}`);
}
for (const [from, to] of [
  ["dsv2.compensation.intent", "dsv2.system.recovery-coordination-repository-contract"],
  ["dsv2.compensation.dispatch", "dsv2.system.recovery-coordination-repository-contract"],
]) {
  const relation = relations.find((candidate) => candidate.from === from && candidate.to === to && candidate.type === "realized_by" && candidate.branch === "bridge");
  assert(relation?.authority_effect === "bounded-formation-traceability", `system-integration:formation-bridge:${from}:${to}`);
}
const designedSystemNodes = [
  "dsv2.system.recovery-coordination-store",
  "dsv2.system.recovery-claim-authority",
  "dsv2.system.recovery-lease-service",
  "dsv2.system.durable-recovery-worker",
  "dsv2.system.recovery-attempt-journal",
  "dsv2.system.operation-invocation-ledger",
  "dsv2.system.recovery-retry-scheduler",
  "dsv2.system.recovery-terminal-recorder",
  "dsv2.system.recovery-restart-reconciler",
  "dsv2.system.dispatch-outbox-publisher",
  "dsv2.system.recovery-telemetry-contract",
];
assert(nodeById.get("dsv2.system.recovery-architecture-profile")?.status === "canonical", "compensation:architecture-profile-not-canonical");
assert(nodeById.get("dsv2.system.operation-binding-resolver-contract")?.status === "implemented", "infrastructure-binding:resolver-status");
for (const nodeId of designedSystemNodes) {
  const node = nodeById.get(nodeId);
  assert(node?.status === "designed", `compensation:designed-node-status:${nodeId}`);
  assert(node.source_refs.includes("source.durable-recovery-architecture") || node.source_refs.includes("source.durable-recovery-properties"), `compensation:designed-node-source:${nodeId}`);
}
for (const subject of ["dsv2.system.recovery-coordination-store", "dsv2.system.durable-recovery-worker"]) {
  assert(relations.some(({ from, to, type, branch }) => from === subject && to === "dsv2.system.recovery-architecture-profile" && type === "constrained_by" && branch === "system"), `compensation:architecture-profile-binding-missing:${subject}`);
}
for (const [from, to] of [
  ["dsv2.system.recovery-coordination-repository-contract", "dsv2.system.recovery-coordination-store"],
  ["dsv2.system.recovery-coordination-unit-of-work-contract", "dsv2.system.recovery-coordination-store"],
]) assert(relations.some((relation) => relation.from === from && relation.to === to && relation.type === "realized_by" && relation.branch === "system"), `infrastructure-binding:realization-edge-missing:${from}:${to}`);
for (const [from, to] of [
  ["dsv2.system.durable-recovery-worker", "dsv2.system.recovery-coordination-repository-contract"],
  ["dsv2.system.durable-recovery-worker", "dsv2.system.recovery-coordination-unit-of-work-contract"],
  ["dsv2.system.recovery-persistence-binding", "dsv2.system.recovery-coordination-repository-contract"],
  ["dsv2.system.recovery-persistence-binding", "dsv2.system.recovery-coordination-store"],
  ["dsv2.system.recovery-transaction-guarantee-binding", "dsv2.system.recovery-coordination-unit-of-work-contract"],
  ["dsv2.system.recovery-transaction-guarantee-binding", "dsv2.system.recovery-failure-outcome-binding"],
  ["dsv2.system.durable-workflow-runtime-binding", "dsv2.system.recovery-persistence-binding"],
  ["dsv2.system.durable-workflow-runtime-binding", "dsv2.system.recovery-transaction-guarantee-binding"],
  ["dsv2.system.durable-workflow-runtime-binding", "dsv2.system.recovery-clock-contract"],
  ["dsv2.system.durable-workflow-runtime-binding", "dsv2.system.recovery-wakeup-contract"],
]) assert(relations.some((relation) => relation.from === from && relation.to === to && relation.type === "depends_on" && relation.branch === "system"), `infrastructure-binding:dependency-edge-missing:${from}:${to}`);
const durableResidue = residue.find(({ residue_id }) => residue_id === "dsv2.residue.durable-compensation-dispatch");
assert(durableResidue?.source_refs.includes("source.workflow-recovery-profile"), "workflow-recovery-profile:durable-residue-evidence-missing");
for (const sourceId of ["source.infrastructure-binding-admission", "source.infrastructure-binding-tower", "source.system-integration-r2", "source.system-integration-profile", "source.system-integration-compiler", "source.system-integration-tests", "source.cli-system-integration-compiler", "source.cli-system-integration-tests"]) assert(durableResidue?.source_refs.includes(sourceId), `system-integration:durable-residue-source-missing:${sourceId}`);
for (const nodeId of ["dsv2.compensation.dispatch", "dsv2.compensation.attempt", "dsv2.compensation.claim", "dsv2.compensation.claim-lease", "dsv2.compensation.retry", "dsv2.compensation.terminal-disposition"]) {
  assert(durableResidue?.node_refs.includes(nodeId), `compensation:implementation-gap-unbound:${nodeId}`);
}
for (const nodeId of [...systemIntegrationFormationNodes, ...designedSystemNodes]) assert(durableResidue?.node_refs.includes(nodeId), `compensation:implementation-gap-unbound:${nodeId}`);

for (const view of profile.package_files.views) {
  const content = readFileSync(resolve(here, view), "utf8");
  const branch = view.includes("business") ? "business" : view.includes("system") ? "system" : null;
  if (branch) for (const node of nodes.filter((candidate) => candidate.branch === branch)) assert(content.includes(node.node_id), `view:${view}:missing-node:${node.node_id}`);
}

const packagePaths = [
  "README.md", "profile.json", "sources.json", "nodes.json", "relations.json", "residue.json",
  "schema/ontology-package.schema.json", ...profile.package_files.schema_amendments,
  "validate-ontology.mjs", ...profile.package_files.views,
].sort((left, right) => Buffer.from(left).compare(Buffer.from(right)));
const packageDigest = sha256(Buffer.concat(packagePaths.flatMap((path) => [Buffer.from(`${path}\0`), readFileSync(resolve(here, path))])));

const receiptRoot = resolve(here, "validation-receipts");
const receiptNames = existsSync(receiptRoot) ? readdirSync(receiptRoot).filter((name) => name.endsWith(".json")).sort() : [];
for (const name of receiptNames) {
  const receipt = JSON.parse(readFileSync(resolve(receiptRoot, name), "utf8"));
  exactKeys(receipt, ["schema_version", "receipt_id", "validated_at", "ontology_id", "ontology_type", "package_digest", "source_count", "node_count", "relation_count", "bridge_relation_count", "residue_count", "checks", "result", "authority_effect"], `receipt:${name}`);
  assert(receipt.schema_version === "domainspec.product-ontology-validation-receipt/v1", `receipt:${name}:schema-version`);
  assert(receipt.ontology_id === profile.ontology_id, `receipt:${name}:ontology-id`);
  assert(receipt.result === "pass" && receipt.authority_effect === "none", `receipt:${name}:claim-ceiling`);
}
const versionedReceiptEpochs = receiptNames.flatMap((name) => {
  const match = name.match(/-v(\d+)-/);
  return match ? [{ name, epoch: Number.parseInt(match[1], 10) }] : [];
});
for (const { name, epoch } of versionedReceiptEpochs) assert(Number.isSafeInteger(epoch) && epoch > 0, `receipt:${name}:invalid-epoch`);
assert(versionedReceiptEpochs.length > 0, "receipt:versioned-epoch-required");
const highestReceiptEpoch = Math.max(...versionedReceiptEpochs.map(({ epoch }) => epoch));
const latestReceiptCandidates = versionedReceiptEpochs.filter(({ epoch }) => epoch === highestReceiptEpoch);
assert(latestReceiptCandidates.length === 1, `receipt:highest-epoch-not-unique:v${highestReceiptEpoch}`);
if (requireReceipt) {
  assert(receiptNames.length > 0, "receipt:required");
  const latest = JSON.parse(readFileSync(resolve(receiptRoot, latestReceiptCandidates[0].name), "utf8"));
  assert(latest.package_digest === packageDigest, "receipt:latest-package-digest-stale");
  assert(latest.source_count === sources.length, "receipt:source-count-drift");
  assert(latest.node_count === nodes.length, "receipt:node-count-drift");
  assert(latest.relation_count === relations.length, "receipt:relation-count-drift");
  assert(latest.bridge_relation_count === relations.filter(({ branch }) => branch === "bridge").length, "receipt:bridge-count-drift");
  assert(latest.residue_count === residue.length, "receipt:residue-count-drift");
}

process.stdout.write(`${JSON.stringify({
  status: "pass",
  ontology_id: profile.ontology_id,
  ontology_type: profile.ontology_type,
  materialization: "package-required",
  package_digest: packageDigest,
  sources: sources.length,
  business_nodes: nodes.filter(({ branch }) => branch === "business").length,
  system_nodes: nodes.filter(({ branch }) => branch === "system").length,
  relations: relations.length,
  bridge_relations: relations.filter(({ branch }) => branch === "bridge").length,
  residue: residue.length,
  receipts: receiptNames.length,
  checks,
  authority_effect: profile.authority_effect,
}, null, 2)}\n`);
