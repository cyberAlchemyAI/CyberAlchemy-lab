#!/usr/bin/env node

import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "../../../..");
const requireReceipt = process.argv.includes("--require-receipt");
let checks = 0;

function assert(condition, message) {
  checks += 1;
  if (!condition) throw new Error(message);
}

function readJson(path) {
  return JSON.parse(readFileSync(resolve(here, path), "utf8"));
}

function digest(bytes) {
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
const elementTypeDocument = readJson("element-types.json");
const conceptDocument = readJson("concepts.json");
const propertyDocument = readJson("properties.json");
const relationDocument = readJson("relations.json");
const constraintDocument = readJson("constraints.json");
const findingDocument = readJson("findings.json");
const residueDocument = readJson("residue.json");
const schema = readJson("schema/architecture-property-ontology.schema.json");

exactKeys(profile, ["schema_version", "architecture_id", "supersedes", "status", "ontology_type", "ontology_type_selection", "branch", "owner_route", "visibility", "authority_effect", "implementation_state", "processing_guarantee", "logical_atomicity_boundary", "business_effect_boundary", "claim_ceiling", "package_files"], "profile");
assert(profile.schema_version === "domainspec.durable-recovery-architecture-profile/v2", "profile:schema-version");
assert(profile.architecture_id === "domainspec-durable-recovery@2", "profile:architecture-id");
exactKeys(profile.supersedes, ["architecture_id", "reason"], "profile:supersedes");
assert(profile.supersedes.architecture_id === "domainspec-durable-recovery@1", "profile:supersedes-id");
assert(profile.status === "canonical-design", "profile:status");
assert(profile.ontology_type === "architecture-property", "profile:ontology-type");
assert(profile.ontology_type_selection.source === "explicit" && profile.ontology_type_selection.confidence === "exact", "profile:type-selection");
assert(profile.branch === "system" && profile.visibility === "private", "profile:scope");
assert(profile.authority_effect === "architecture-definition-only", "profile:authority-effect");
assert(profile.processing_guarantee === "at-least-once-invocation-with-idempotent-semantic-application", "profile:processing-guarantee");
assert(profile.logical_atomicity_boundary.includes("dispatch-outbox"), "profile:coordination-atomicity-boundary");
assert(profile.business_effect_boundary === "operation-owned-state-and-outbox-transaction", "profile:business-effect-boundary");
assert(profile.claim_ceiling.canonical_architecture_properties === true && profile.claim_ceiling.system_ontology === true, "profile:canonical-design-ceiling");
for (const denied of ["durable_runtime_implemented", "production_store_selected", "deployment_topology_selected", "publication", "release", "deployment", "production"]) assert(profile.claim_ceiling[denied] === false, `profile:inflated-claim:${denied}`);
exactKeys(profile.package_files, ["sources", "element_types", "concepts", "properties", "relations", "constraints", "findings", "residue", "schema", "validator", "human_views", "receipts"], "profile:package-files");
assert(schema.$id === "domainspec://schemas/durable-recovery-architecture-property-ontology/v2", "schema:identity");
for (const name of ["source", "element_type", "concept", "property", "relation_type", "relation", "constraint", "finding", "residue", "receipt"]) assert(schema.$defs?.[name], `schema:missing-definition:${name}`);

for (const [document, version, key] of [
  [sourceDocument, "domainspec.durable-recovery-architecture-sources/v1", "sources"],
  [elementTypeDocument, "domainspec.durable-recovery-element-types/v1", "element_types"],
  [conceptDocument, "domainspec.durable-recovery-system-concepts/v1", "concepts"],
  [propertyDocument, "domainspec.durable-recovery-architecture-properties/v2", "properties"],
  [constraintDocument, "domainspec.durable-recovery-architecture-constraints/v2", "constraints"],
  [findingDocument, "domainspec.durable-recovery-architecture-findings/v2", "findings"],
  [residueDocument, "domainspec.durable-recovery-architecture-residue/v2", "residue"],
]) {
  exactKeys(document, key === "constraints" ? ["schema_version", "architecture_id", "profile_id", "portability", key] : ["schema_version", "architecture_id", key], `document:${key}`);
  assert(document.schema_version === version, `document:${key}:schema-version`);
  assert(document.architecture_id === profile.architecture_id, `document:${key}:architecture-id`);
}
exactKeys(relationDocument, ["schema_version", "architecture_id", "relation_types", "relations"], "document:relations");
assert(relationDocument.schema_version === "domainspec.durable-recovery-architecture-relations/v2", "document:relations:schema-version");
assert(relationDocument.architecture_id === profile.architecture_id, "document:relations:architecture-id");
assert(constraintDocument.profile_id === "dsv2.recovery.profile.portable-durable-recovery-v1" && constraintDocument.portability === "technology-neutral", "constraints:profile");

const sources = sourceDocument.sources;
unique(sources.map(({ source_id }) => source_id), "sources:id");
const sourceById = new Map(sources.map((source) => [source.source_id, source]));
for (const source of sources) {
  exactKeys(source, ["source_id", "path", "sha256", "role", "evidence_stage", "authority_effect"], `source:${source.source_id}`);
  assert(/^[a-f0-9]{64}$/.test(source.sha256), `source:${source.source_id}:digest-shape`);
  const path = resolve(repoRoot, source.path);
  assert(existsSync(path), `source:${source.source_id}:missing:${source.path}`);
  assert(digest(readFileSync(path)) === source.sha256, `source:${source.source_id}:stale:${source.path}`);
}
const threeProfileImplementationSources = [
  "source.workflow-recovery-profile",
  "source.workflow-recovery-profile-tests",
  "source.reference-runtime",
  "source.runtime-tests",
  "source.python-compensation-reference",
  "source.python-compensation-tests",
  "source.rust-compensation-reference",
  "source.rust-compensation-tests",
  "source.cli-generator",
  "source.cli-runtime-test",
];
for (const sourceId of threeProfileImplementationSources) assert(sourceById.has(sourceId), `sources:three-profile-evidence-missing:${sourceId}`);
const systemIntegrationImplementationSources = [
  "source.system-integration-profile",
  "source.system-integration-compiler",
  "source.system-integration-validator",
  "source.system-integration-tests",
  "source.cli-system-integration-compiler",
  "source.cli-system-integration-tests",
];
for (const sourceId of systemIntegrationImplementationSources) assert(sourceById.has(sourceId), `sources:system-integration-evidence-missing:${sourceId}`);

const infrastructureAdmissionSource = sourceById.get("source.infrastructure-binding-admission");
assert(infrastructureAdmissionSource?.authority_effect === "owns-d45-through-d49-and-durable-recovery-architecture-admission", "sources:infrastructure-admission-authority");
const infrastructureAdmission = JSON.parse(readFileSync(resolve(repoRoot, infrastructureAdmissionSource.path), "utf8"));
assert(infrastructureAdmission.decision_id === "DSV2-OWNER-INFRASTRUCTURE-BINDING-ARCHITECTURE-2026-08-30", "infrastructure-admission:decision-id");
assert(infrastructureAdmission.selected_option?.id === "admit-concern-specific-contracts-and-explicit-bindings", "infrastructure-admission:selected-option");
assert(JSON.stringify(infrastructureAdmission.decision_source?.research_refs) === JSON.stringify([
  "projects/domainspec-v2/development/research/2026-08-20-operation-workflow-infrastructure-binding-patterns/TOWER.md",
  "projects/domainspec-v2/development/refinement-runs/20260813T153029Z-system-integration-contract-layer-revision-2/RESULT.md",
]), "infrastructure-admission:research-ref-drift");
assert(Array.isArray(infrastructureAdmission.remaining_owner_decisions) && infrastructureAdmission.remaining_owner_decisions.length === 0, "infrastructure-admission:semantic-decision-residue");
assert(infrastructureAdmission.authority_effect === "project-local-canonical-infrastructure-binding-and-architecture-admission", "infrastructure-admission:authority-effect");
for (const requiredInvariant of [
  "no universal code-level Port",
  "Interface reference is optional",
  "Repository and Unit of Work code contracts remain distinct",
  "Failure Outcome Binding classifies failure but does not choose Retry",
  "without selecting a provider",
  "No database, ORM, broker",
]) assert(infrastructureAdmission.invariants.some((invariant) => invariant.includes(requiredInvariant)), `infrastructure-admission:invariant-missing:${requiredInvariant}`);

const elementTypes = elementTypeDocument.element_types;
unique(elementTypes.map(({ element_type_id }) => element_type_id), "element-types:id");
const elementTypeById = new Map(elementTypes.map((item) => [item.element_type_id, item]));
for (const item of elementTypes) {
  exactKeys(item, ["element_type_id", "label", "parent_ref", "allowed_roles", "description"], `element-type:${item.element_type_id}`);
  unique(item.allowed_roles, `element-type:${item.element_type_id}:roles`);
  if (item.parent_ref !== null) assert(elementTypeById.has(item.parent_ref), `element-type:${item.element_type_id}:unknown-parent`);
}
assert(!elementTypeById.has("dsv2.arch.element.port"), "element-types:universal-port-forbidden");
assert(elementTypeById.has("dsv2.arch.element.contract"), "element-types:dependency-contract-missing");
assert(elementTypeById.has("dsv2.arch.element.binding"), "element-types:infrastructure-binding-missing");

const concepts = conceptDocument.concepts;
unique(concepts.map(({ concept_id }) => concept_id), "concepts:id");
const conceptById = new Map(concepts.map((concept) => [concept.concept_id, concept]));
for (const concept of concepts) {
  exactKeys(concept, ["concept_id", "label", "element_type_ref", "role", "implementation_status", "state_ownership", "source_refs", "summary", "forbidden_inference"], `concept:${concept.concept_id}`);
  const elementType = elementTypeById.get(concept.element_type_ref);
  assert(elementType, `concept:${concept.concept_id}:unknown-element-type`);
  assert(elementType.allowed_roles.includes(concept.role), `concept:${concept.concept_id}:role-not-allowed`);
  assert(["observed", "partial", "designed-only"].includes(concept.implementation_status), `concept:${concept.concept_id}:implementation-status`);
  unique(concept.source_refs, `concept:${concept.concept_id}:sources`);
  for (const ref of concept.source_refs) assert(sourceById.has(ref), `concept:${concept.concept_id}:unknown-source:${ref}`);
}
assert(concepts.some(({ implementation_status }) => implementation_status === "observed"), "concepts:observed-empty");
assert(concepts.some(({ implementation_status }) => implementation_status === "designed-only"), "concepts:designed-empty");
for (const conceptId of [
  "dsv2.recovery.system.coordination-repository-contract",
  "dsv2.recovery.system.coordination-unit-of-work-contract",
  "dsv2.recovery.system.persistence-binding",
  "dsv2.recovery.system.transaction-guarantee-binding",
  "dsv2.recovery.system.failure-outcome-binding",
  "dsv2.recovery.system.runtime-binding",
]) {
  assert(conceptById.has(conceptId), `concepts:infrastructure-contract-or-binding-missing:${conceptId}`);
  assert(conceptById.get(conceptId)?.source_refs.includes("source.infrastructure-binding-admission"), `concepts:infrastructure-admission-missing:${conceptId}`);
  assert(conceptById.get(conceptId)?.implementation_status === "observed", `concepts:system-integration-formation-not-observed:${conceptId}`);
  for (const sourceId of ["source.system-integration-profile", "source.system-integration-compiler", "source.system-integration-tests"]) {
    assert(conceptById.get(conceptId)?.source_refs.includes(sourceId), `concepts:system-integration-evidence-missing:${conceptId}:${sourceId}`);
  }
}
for (const conceptId of ["dsv2.recovery.system.planner", "dsv2.recovery.system.in-process-executor", "dsv2.recovery.system.binding-resolver"]) {
  const concept = conceptById.get(conceptId);
  for (const sourceId of ["source.workflow-recovery-profile", "source.reference-runtime", "source.python-compensation-reference", "source.rust-compensation-reference", "source.cli-generator"]) {
    assert(concept?.source_refs.includes(sourceId), `concept:${conceptId}:three-profile-source-missing:${sourceId}`);
  }
}
const contractTests = conceptById.get("dsv2.recovery.system.contract-tests");
for (const sourceId of ["source.runtime-tests", "source.python-compensation-tests", "source.rust-compensation-tests", "source.workflow-recovery-profile-tests", "source.cli-runtime-test", "source.system-integration-validator", "source.system-integration-tests", "source.cli-system-integration-tests"]) {
  assert(contractTests?.source_refs.includes(sourceId), `concept:dsv2.recovery.system.contract-tests:three-profile-source-missing:${sourceId}`);
}

const properties = propertyDocument.properties;
unique(properties.map(({ property_id }) => property_id), "properties:id");
const propertyById = new Map(properties.map((property) => [property.property_id, property]));
for (const property of properties) {
  exactKeys(property, ["property_id", "label", "value_type", "valid_subject_roles", "observation_stages", "owner_route", "portable", "description", "forbidden_inference"], `property:${property.property_id}`);
  assert(["boolean", "enum", "integer", "string-ref"].includes(property.value_type), `property:${property.property_id}:value-type`);
  assert(property.portable === true, `property:${property.property_id}:not-portable`);
  unique(property.valid_subject_roles, `property:${property.property_id}:subject-roles`);
  unique(property.observation_stages, `property:${property.property_id}:observation-stages`);
}

const relationTypes = relationDocument.relation_types;
unique(relationTypes.map(({ relation_type_id }) => relation_type_id), "relation-types:id");
const relationTypeById = new Map(relationTypes.map((item) => [item.relation_type_id, item]));
for (const item of relationTypes) {
  exactKeys(item, ["relation_type_id", "label", "from_element_types", "to_element_types", "direction", "cycle_policy", "evidence_requirement", "forbidden_inference"], `relation-type:${item.relation_type_id}`);
  for (const ref of [...item.from_element_types, ...item.to_element_types]) assert(elementTypeById.has(ref), `relation-type:${item.relation_type_id}:unknown-element-type:${ref}`);
}
const relations = relationDocument.relations;
unique(relations.map(({ relation_id }) => relation_id), "relations:id");
for (const relation of relations) {
  exactKeys(relation, ["relation_id", "type_ref", "from", "to", "required", "source_refs", "contract", "forbidden_inference"], `relation:${relation.relation_id}`);
  const type = relationTypeById.get(relation.type_ref);
  const from = conceptById.get(relation.from);
  const to = conceptById.get(relation.to);
  assert(type && from && to, `relation:${relation.relation_id}:endpoint-or-type-closure`);
  assert(relation.from !== relation.to, `relation:${relation.relation_id}:self-edge`);
  assert(type.from_element_types.includes(from.element_type_ref), `relation:${relation.relation_id}:from-element-type`);
  assert(type.to_element_types.includes(to.element_type_ref), `relation:${relation.relation_id}:to-element-type`);
  unique(relation.source_refs, `relation:${relation.relation_id}:sources`);
  for (const ref of relation.source_refs) assert(sourceById.has(ref), `relation:${relation.relation_id}:unknown-source:${ref}`);
}

const constraints = constraintDocument.constraints;
unique(constraints.map(({ constraint_id }) => constraint_id), "constraints:id");
const constraintById = new Map(constraints.map((constraint) => [constraint.constraint_id, constraint]));
for (const constraint of constraints) {
  exactKeys(constraint, ["constraint_id", "subject_refs", "property_ref", "operator", "expected_value", "evidence_requirement", "on_unknown", "owner_route"], `constraint:${constraint.constraint_id}`);
  const property = propertyById.get(constraint.property_ref);
  assert(property, `constraint:${constraint.constraint_id}:unknown-property`);
  assert(constraint.on_unknown === "unsupported", `constraint:${constraint.constraint_id}:unknown-policy`);
  unique(constraint.subject_refs, `constraint:${constraint.constraint_id}:subjects`);
  for (const ref of constraint.subject_refs) {
    const subject = conceptById.get(ref);
    assert(subject, `constraint:${constraint.constraint_id}:unknown-subject:${ref}`);
    assert(property.valid_subject_roles.includes(subject.role), `constraint:${constraint.constraint_id}:invalid-subject-role:${subject.role}`);
  }
}
assert(constraints.length === properties.length, "constraints:property-count-mismatch");
for (const property of properties) assert(constraints.some(({ property_ref }) => property_ref === property.property_id), `property:${property.property_id}:constraint-missing`);

const findings = findingDocument.findings;
unique(findings.map(({ finding_id }) => finding_id), "findings:id");
for (const finding of findings) {
  exactKeys(finding, ["finding_id", "constraint_ref", "subject_refs", "property_ref", "expected_value", "observed_value", "originating_profile", "evidence_refs", "observation_stage", "result", "owner_route", "explanation"], `finding:${finding.finding_id}`);
  const constraint = constraintById.get(finding.constraint_ref);
  assert(constraint, `finding:${finding.finding_id}:unknown-constraint`);
  assert(finding.property_ref === constraint.property_ref, `finding:${finding.finding_id}:property-drift`);
  assert(finding.expected_value === constraint.expected_value, `finding:${finding.finding_id}:expected-drift`);
  assert(JSON.stringify(finding.subject_refs) === JSON.stringify(constraint.subject_refs), `finding:${finding.finding_id}:subject-drift`);
  assert(finding.originating_profile === constraintDocument.profile_id, `finding:${finding.finding_id}:profile-drift`);
  assert(["supported", "partial", "unsupported"].includes(finding.result), `finding:${finding.finding_id}:result`);
  if (finding.result === "unsupported") assert(finding.observed_value.startsWith("unknown-"), `finding:${finding.finding_id}:unsupported-without-unknown`);
  unique(finding.evidence_refs, `finding:${finding.finding_id}:evidence`);
  for (const ref of finding.evidence_refs) assert(sourceById.has(ref), `finding:${finding.finding_id}:unknown-evidence:${ref}`);
}
assert(findings.length === constraints.length, "findings:constraint-count-mismatch");
for (const constraint of constraints) assert(findings.some(({ constraint_ref }) => constraint_ref === constraint.constraint_id), `constraint:${constraint.constraint_id}:finding-missing`);
const findingById = new Map(findings.map((finding) => [finding.finding_id, finding]));
for (const findingId of [
  "dsv2.recovery.finding.intent-identity-complete-and-unique",
  "dsv2.recovery.finding.plan-identity-immutable",
  "dsv2.recovery.finding.plan-occurrence-identity",
  "dsv2.recovery.finding.invocation-identity-stable",
  "dsv2.recovery.finding.semantic-and-operational-state-separated",
]) {
  const finding = findingById.get(findingId);
  assert(finding?.result === "partial", `finding:${findingId}:durable-evidence-inflated`);
  for (const sourceId of ["source.reference-runtime", "source.python-compensation-reference", "source.rust-compensation-reference"]) {
    assert(finding?.evidence_refs.includes(sourceId), `finding:${findingId}:three-profile-evidence-missing:${sourceId}`);
  }
}
assert(findingById.get("dsv2.recovery.finding.intent-identity-complete-and-unique")?.observed_value.includes("complete-three-profile"), "findings:d37-three-profile-observation-missing");
assert(findingById.get("dsv2.recovery.finding.invocation-identity-stable")?.observed_value.includes("complete-three-profile-d40"), "findings:d40-three-profile-observation-missing");
for (const findingId of ["dsv2.recovery.finding.binding-preflight-complete", "dsv2.recovery.finding.no-replan-or-substitution", "dsv2.recovery.finding.operation-effect-authority-preserved"]) {
  assert(findingById.get(findingId)?.result === "supported", `finding:${findingId}:observed-slice-not-supported`);
}

const residue = residueDocument.residue;
unique(residue.map(({ residue_id }) => residue_id), "residue:id");
for (const item of residue) {
  exactKeys(item, ["residue_id", "status", "summary", "owner_route", "concept_refs", "property_refs", "decision_state", "forbidden_inference"], `residue:${item.residue_id}`);
  assert(item.status === "open", `residue:${item.residue_id}:status`);
  for (const ref of item.concept_refs) assert(conceptById.has(ref), `residue:${item.residue_id}:unknown-concept:${ref}`);
  for (const ref of item.property_refs) assert(propertyById.has(ref), `residue:${item.residue_id}:unknown-property:${ref}`);
}
assert(sourceById.get("source.infrastructure-binding-tower")?.authority_effect === "none", "sources:research-authority-inflation");
assert(sourceById.get("source.system-integration-r2")?.authority_effect === "none", "sources:revision2-authority-inflation");
for (const findingId of [
  "dsv2.recovery.finding.dependency-contracts-concern-specific",
  "dsv2.recovery.finding.repository-and-persistence-binding-distinct",
  "dsv2.recovery.finding.unit-of-work-and-transaction-binding-distinct",
  "dsv2.recovery.finding.failure-classification-does-not-select-retry",
  "dsv2.recovery.finding.durable-runtime-binding-complete",
]) assert(findingById.get(findingId)?.evidence_refs.includes("source.infrastructure-binding-admission"), `finding:${findingId}:infrastructure-admission-missing`);
for (const findingId of [
  "dsv2.recovery.finding.dependency-contracts-concern-specific",
  "dsv2.recovery.finding.repository-and-persistence-binding-distinct",
  "dsv2.recovery.finding.unit-of-work-and-transaction-binding-distinct",
  "dsv2.recovery.finding.failure-classification-does-not-select-retry",
  "dsv2.recovery.finding.durable-runtime-binding-complete",
]) {
  const finding = findingById.get(findingId);
  assert(finding?.result === "partial", `finding:${findingId}:provider-runtime-claim-inflation`);
  for (const sourceId of ["source.system-integration-profile", "source.system-integration-compiler", "source.system-integration-tests"]) {
    assert(finding?.evidence_refs.includes(sourceId), `finding:${findingId}:system-integration-evidence-missing:${sourceId}`);
  }
}
for (const relationId of [
  "dsv2.recovery.relation.persistence-binding-binds-repository",
  "dsv2.recovery.relation.transaction-binding-binds-unit-of-work",
  "dsv2.recovery.relation.transaction-binding-binds-failure-outcome",
  "dsv2.recovery.relation.runtime-binding-binds-persistence",
]) assert(relations.some(({ relation_id }) => relation_id === relationId), `relations:infrastructure-binding-missing:${relationId}`);
const definitions = readFileSync(resolve(repoRoot, "projects/domainspec-v2/definitions/DEFINITIONS.md"), "utf8");
const definitionsIndex = readFileSync(resolve(repoRoot, "projects/domainspec-v2/definitions/DEFINITIONS-INDEX.md"), "utf8");
for (const id of Array.from({ length: 5 }, (_, index) => `domainspec-v2-D${index + 45}`)) {
  assert(definitions.includes(`## ${id}.`), `definitions:infrastructure-card-missing:${id}`);
  assert(definitionsIndex.includes(`\`${id}\``), `definitions:infrastructure-index-missing:${id}`);
  const start = definitions.indexOf(`## ${id}.`);
  const next = definitions.indexOf("\n## ", start + 4);
  const section = definitions.slice(start, next === -1 ? definitions.length : next);
  for (const evidenceLocator of [
    "2026-08-20-operation-workflow-infrastructure-binding-patterns/TOWER.md",
    "20260813T153029Z-system-integration-contract-layer-revision-2/RESULT.md",
    "OWNER-INFRASTRUCTURE-BINDING-ARCHITECTURE-ADMISSION.json",
  ]) assert(section.includes(evidenceLocator), `definitions:${id}:integration-provenance-missing:${evidenceLocator}`);
}

for (const view of profile.package_files.human_views) {
  const path = resolve(here, view);
  assert(existsSync(path), `view:missing:${view}`);
  const content = readFileSync(path, "utf8");
  for (const match of content.matchAll(/\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)/g)) {
    const target = resolve(dirname(path), match[1]);
    assert(existsSync(target), `view:${view}:broken-link:${match[1]}`);
  }
}

const packagePaths = [
  "README.md", "ARCHITECTURE.md", "ARCHITECTURE-PATTERN-LIBRARY.md",
  ...profile.package_files.human_views.filter((path) => path.startsWith("pattern-library/")),
  profile.package_files.sources, profile.package_files.element_types, profile.package_files.concepts,
  profile.package_files.properties, profile.package_files.relations, profile.package_files.constraints,
  profile.package_files.findings, profile.package_files.residue, profile.package_files.schema,
  profile.package_files.validator, "profile.json",
].sort();
unique(packagePaths, "package-paths");
const packageHash = createHash("sha256");
for (const path of packagePaths) {
  assert(existsSync(resolve(here, path)), `package:missing:${path}`);
  packageHash.update(path).update("\0").update(readFileSync(resolve(here, path))).update("\0");
}
const packageDigest = packageHash.digest("hex");
const counts = {
  sources: sources.length,
  element_types: elementTypes.length,
  concepts: concepts.length,
  properties: properties.length,
  relation_types: relationTypes.length,
  relations: relations.length,
  constraints: constraints.length,
  findings: findings.length,
  residue: residue.length
};

const receiptDirectory = resolve(here, profile.package_files.receipts);
const receiptNames = existsSync(receiptDirectory) ? readdirSync(receiptDirectory).filter((name) => name.endsWith(".json")).sort() : [];
if (requireReceipt) {
  assert(receiptNames.length > 0, "receipt:missing");
  const receipt = readJson(`${profile.package_files.receipts}${receiptNames.at(-1)}`);
  exactKeys(receipt, ["schema_version", "receipt_id", "validated_at", "architecture_id", "ontology_type", "package_digest", "counts", "checks", "result", "authority_effect"], "receipt");
  assert(receipt.schema_version === "domainspec.durable-recovery-architecture-validation-receipt/v2", "receipt:schema-version");
  assert(receipt.architecture_id === profile.architecture_id && receipt.ontology_type === profile.ontology_type, "receipt:identity");
  assert(receipt.package_digest === packageDigest, "receipt:package-digest-drift");
  assert(JSON.stringify(receipt.counts) === JSON.stringify(counts), "receipt:count-drift");
  assert(receipt.result === "pass" && receipt.authority_effect === "none", "receipt:result-or-authority");
}

process.stdout.write(`${JSON.stringify({
  status: "pass",
  architecture_id: profile.architecture_id,
  ontology_type: profile.ontology_type,
  materialization: "package-required",
  package_digest: packageDigest,
  counts,
  receipts: receiptNames.length,
  checks,
  authority_effect: profile.authority_effect,
  durable_runtime_implemented: profile.claim_ceiling.durable_runtime_implemented
}, null, 2)}\n`);
