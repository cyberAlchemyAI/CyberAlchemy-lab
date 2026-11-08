import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { compileIntegrationKernelV2, validateIntegrationKernelV2 } from "./kernel-v2.js";
import type {
  CompiledPersistenceCompositionV2,
  IdentityMappingV1,
  MigrationContractV1,
  MigrationStepV1,
  PersistenceBindingV2,
  PersistenceCompositionV2,
  PersistenceConversionRuleV1,
  PersistenceFieldMappingV1,
  PersistenceIndexMappingV1,
  PersistenceMappingV1,
  PersistenceRelationMappingV1,
  PersistenceShape,
  PhysicalModelV1,
  TransactionGuaranteeBindingV2,
} from "./persistence-v2-types.js";

const REF = /^[A-Za-z][A-Za-z0-9]*(?:[-.:/][A-Za-z0-9]+)*(?:#[A-Za-z][A-Za-z0-9_-]*)?$/;
type UnknownRecord = Record<string, unknown>;

export class PersistenceCompositionError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "PersistenceCompositionError";
  }
}

function fail(code: string, pointer: string, message: string): never {
  throw new PersistenceCompositionError(code, pointer, message);
}

function object(value: unknown, pointer: string): asserts value is UnknownRecord {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail("PERSISTENCE_SCHEMA", pointer, "expected object");
}

function exact(value: unknown, fields: readonly string[], pointer: string): asserts value is UnknownRecord {
  object(value, pointer);
  if (canonicalJson(Object.keys(value).sort()) !== canonicalJson([...fields].sort())) fail("PERSISTENCE_SCHEMA", pointer, "unexpected or missing member");
}

function reference(value: unknown, pointer: string): string {
  if (typeof value !== "string" || !REF.test(value)) fail("PERSISTENCE_REFERENCE", pointer, "invalid reference");
  return value;
}

function text(value: unknown, pointer: string): string {
  if (typeof value !== "string" || value.trim().length === 0) fail("PERSISTENCE_SCHEMA", pointer, "expected non-empty text");
  return value;
}

function bool(value: unknown, pointer: string): boolean {
  if (typeof value !== "boolean") fail("PERSISTENCE_SCHEMA", pointer, "expected boolean");
  return value;
}

function oneOf<T extends string>(value: unknown, allowed: readonly T[], pointer: string): T {
  if (!allowed.includes(value as T)) fail("PERSISTENCE_SCHEMA", pointer, `expected one of:${allowed.join(",")}`);
  return value as T;
}

function records(value: unknown, pointer: string, allowEmpty = true): readonly unknown[] {
  if (!Array.isArray(value) || (!allowEmpty && value.length === 0)) fail("PERSISTENCE_SCHEMA", pointer, "expected record array");
  return value;
}

function refs(value: unknown, pointer: string, allowEmpty = true, preserveOrder = false): readonly string[] {
  if (!Array.isArray(value) || (!allowEmpty && value.length === 0)) fail("PERSISTENCE_SCHEMA", pointer, "expected reference array");
  const result = value.map((entry, index) => reference(entry, `${pointer}/${index}`));
  if (new Set(result).size !== result.length) fail("PERSISTENCE_DUPLICATE", pointer, "duplicate reference");
  return Object.freeze(preserveOrder ? result : [...result].sort());
}

function nullableRef(value: unknown, pointer: string): string | null {
  return value === null ? null : reference(value, pointer);
}

function identities<T>(values: readonly T[], select: (value: T) => string, pointer: string): ReadonlyMap<string, T> {
  const result = new Map<string, T>();
  for (const value of values) {
    const identity = select(value);
    if (result.has(identity)) fail("PERSISTENCE_DUPLICATE", pointer, `duplicate identity:${identity}`);
    result.set(identity, value);
  }
  return result;
}

function freeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) freeze(child);
  }
  return value;
}

function physicalModel(value: unknown, pointer: string): PhysicalModelV1 {
  exact(value, ["model_id", "model_kind", "physical_name", "version"], pointer);
  return Object.freeze({
    model_id: reference(value.model_id, `${pointer}/model_id`),
    model_kind: oneOf(value.model_kind, ["relational-table", "document", "key-value"] as const, `${pointer}/model_kind`),
    physical_name: text(value.physical_name, `${pointer}/physical_name`),
    version: reference(value.version, `${pointer}/version`),
  });
}

function identityMapping(value: unknown, pointer: string): IdentityMappingV1 {
  exact(value, ["logical_property_ref", "physical_field_ref", "conversion_ref"], pointer);
  return Object.freeze({ logical_property_ref: reference(value.logical_property_ref, `${pointer}/logical_property_ref`), physical_field_ref: reference(value.physical_field_ref, `${pointer}/physical_field_ref`), conversion_ref: nullableRef(value.conversion_ref, `${pointer}/conversion_ref`) });
}

function fieldMapping(value: unknown, pointer: string): PersistenceFieldMappingV1 {
  exact(value, ["logical_property_ref", "logical_shape", "physical_field_ref", "storage_shape", "collection_semantics", "conversion_ref"], pointer);
  const logicalShape = oneOf(value.logical_shape, ["scalar", "entity-reference", "value-object", "enum", "sum", "optional", "list", "set"] as const, `${pointer}/logical_shape`);
  const storageShape = oneOf(value.storage_shape, ["scalar", "foreign-key", "embedded", "discriminator", "nullable", "array", "join-table"] as const, `${pointer}/storage_shape`);
  const collectionSemantics = oneOf(value.collection_semantics, ["not-applicable", "ordered", "unique-unordered"] as const, `${pointer}/collection_semantics`);
  const allowedStorage: Readonly<Record<PersistenceShape, readonly PersistenceFieldMappingV1["storage_shape"][]>> = {
    scalar: ["scalar"], "entity-reference": ["foreign-key", "join-table", "embedded"], "value-object": ["scalar", "embedded"], enum: ["scalar"],
    sum: ["discriminator", "embedded"], optional: ["nullable"], list: ["array", "join-table"], set: ["array", "join-table"],
  };
  if (!allowedStorage[logicalShape].includes(storageShape)) fail("PERSISTENCE_SHAPE_COLLAPSE", pointer, `${logicalShape} cannot be stored as ${storageShape}`);
  const requiredCollection = logicalShape === "list" ? "ordered" : logicalShape === "set" ? "unique-unordered" : "not-applicable";
  if (collectionSemantics !== requiredCollection) fail("PERSISTENCE_CARDINALITY_COLLAPSE", `${pointer}/collection_semantics`, `${logicalShape} requires ${requiredCollection}`);
  const conversionRef = nullableRef(value.conversion_ref, `${pointer}/conversion_ref`);
  if (logicalShape === "value-object" && storageShape === "scalar" && conversionRef === null) fail("PERSISTENCE_CONVERSION_REQUIRED", `${pointer}/conversion_ref`, "scalar value-object storage requires an explicit conversion");
  return Object.freeze({ logical_property_ref: reference(value.logical_property_ref, `${pointer}/logical_property_ref`), logical_shape: logicalShape, physical_field_ref: reference(value.physical_field_ref, `${pointer}/physical_field_ref`), storage_shape: storageShape, collection_semantics: collectionSemantics, conversion_ref: conversionRef });
}

function relationMapping(value: unknown, pointer: string): PersistenceRelationMappingV1 {
  exact(value, ["relation_ref", "source_field_ref", "target_model_ref", "target_field_ref", "cardinality", "storage_strategy"], pointer);
  return Object.freeze({
    relation_ref: reference(value.relation_ref, `${pointer}/relation_ref`), source_field_ref: reference(value.source_field_ref, `${pointer}/source_field_ref`),
    target_model_ref: reference(value.target_model_ref, `${pointer}/target_model_ref`), target_field_ref: reference(value.target_field_ref, `${pointer}/target_field_ref`),
    cardinality: oneOf(value.cardinality, ["one-to-one", "many-to-one", "one-to-many", "many-to-many"] as const, `${pointer}/cardinality`),
    storage_strategy: oneOf(value.storage_strategy, ["foreign-key", "join-table", "embedded"] as const, `${pointer}/storage_strategy`),
  });
}

function indexMapping(value: unknown, pointer: string): PersistenceIndexMappingV1 {
  exact(value, ["index_id", "model_ref", "physical_name", "field_refs", "unique", "order"], pointer);
  return Object.freeze({ index_id: reference(value.index_id, `${pointer}/index_id`), model_ref: reference(value.model_ref, `${pointer}/model_ref`), physical_name: text(value.physical_name, `${pointer}/physical_name`), field_refs: refs(value.field_refs, `${pointer}/field_refs`, false, value.order === "ordered"), unique: bool(value.unique, `${pointer}/unique`), order: oneOf(value.order, ["ordered", "unordered"] as const, `${pointer}/order`) });
}

function conversionRule(value: unknown, pointer: string): PersistenceConversionRuleV1 {
  exact(value, ["conversion_id", "source_shape", "target_shape", "direction", "lossless", "implementation_ref"], pointer);
  return Object.freeze({ conversion_id: reference(value.conversion_id, `${pointer}/conversion_id`), source_shape: text(value.source_shape, `${pointer}/source_shape`), target_shape: text(value.target_shape, `${pointer}/target_shape`), direction: oneOf(value.direction, ["to-storage", "from-storage", "bidirectional"] as const, `${pointer}/direction`), lossless: bool(value.lossless, `${pointer}/lossless`), implementation_ref: reference(value.implementation_ref, `${pointer}/implementation_ref`) });
}

function persistenceMapping(value: unknown, pointer: string): PersistenceMappingV1 {
  exact(value, ["mapping_id", "logical_subject_refs", "physical_models", "identity_mappings", "field_mappings", "relation_mappings", "index_mappings", "conversion_rules", "version", "authority_effect"], pointer);
  if (value.authority_effect !== "none") fail("PERSISTENCE_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  const physicalModels = records(value.physical_models, `${pointer}/physical_models`, false).map((entry, index) => physicalModel(entry, `${pointer}/physical_models/${index}`)).sort((a, b) => a.model_id.localeCompare(b.model_id));
  const identityMappings = records(value.identity_mappings, `${pointer}/identity_mappings`, false).map((entry, index) => identityMapping(entry, `${pointer}/identity_mappings/${index}`)).sort((a, b) => a.logical_property_ref.localeCompare(b.logical_property_ref));
  const fieldMappings = records(value.field_mappings, `${pointer}/field_mappings`, false).map((entry, index) => fieldMapping(entry, `${pointer}/field_mappings/${index}`)).sort((a, b) => a.logical_property_ref.localeCompare(b.logical_property_ref));
  const relationMappings = records(value.relation_mappings, `${pointer}/relation_mappings`).map((entry, index) => relationMapping(entry, `${pointer}/relation_mappings/${index}`)).sort((a, b) => a.relation_ref.localeCompare(b.relation_ref));
  const indexMappings = records(value.index_mappings, `${pointer}/index_mappings`).map((entry, index) => indexMapping(entry, `${pointer}/index_mappings/${index}`)).sort((a, b) => a.index_id.localeCompare(b.index_id));
  const conversionRules = records(value.conversion_rules, `${pointer}/conversion_rules`).map((entry, index) => conversionRule(entry, `${pointer}/conversion_rules/${index}`)).sort((a, b) => a.conversion_id.localeCompare(b.conversion_id));
  const models = identities(physicalModels, item => item.model_id, `${pointer}/physical_models`);
  const conversions = identities(conversionRules, item => item.conversion_id, `${pointer}/conversion_rules`);
  const fields = identities(fieldMappings, item => item.logical_property_ref, `${pointer}/field_mappings`);
  identities(indexMappings, item => item.index_id, `${pointer}/index_mappings`);
  identities(relationMappings, item => item.relation_ref, `${pointer}/relation_mappings`);
  for (const item of fieldMappings) if (item.conversion_ref !== null && !conversions.has(item.conversion_ref)) fail("PERSISTENCE_REFERENCE_UNRESOLVED", `${pointer}/field_mappings`, `conversion unresolved:${item.conversion_ref}`);
  for (const item of identityMappings) {
    const field = fields.get(item.logical_property_ref);
    if (!field || field.physical_field_ref !== item.physical_field_ref) fail("PERSISTENCE_IDENTITY_DRIFT", `${pointer}/identity_mappings`, `identity is not the same mapped field:${item.logical_property_ref}`);
    if (item.conversion_ref !== null && !conversions.has(item.conversion_ref)) fail("PERSISTENCE_REFERENCE_UNRESOLVED", `${pointer}/identity_mappings`, `conversion unresolved:${item.conversion_ref}`);
  }
  for (const item of relationMappings) if (!models.has(item.target_model_ref)) fail("PERSISTENCE_REFERENCE_UNRESOLVED", `${pointer}/relation_mappings`, `target model unresolved:${item.target_model_ref}`);
  const modelForField = (fieldRef: string): PhysicalModelV1 | undefined => physicalModels.find(model => fieldRef.startsWith(`physical:${model.model_id.replace(/^physical-model:/, "")}/`));
  for (const item of relationMappings) {
    const sourceModel = modelForField(item.source_field_ref);
    const targetModel = models.get(item.target_model_ref)!;
    if (sourceModel === undefined) fail("PERSISTENCE_RELATION_FIELD", `${pointer}/relation_mappings`, `relation source field has no physical model:${item.source_field_ref}`);
    if (!item.target_field_ref.startsWith(`physical:${targetModel.model_id.replace(/^physical-model:/, "")}/`)) fail("PERSISTENCE_RELATION_FIELD", `${pointer}/relation_mappings`, `relation target field disagrees with target model:${item.target_field_ref}`);
    if (item.storage_strategy === "foreign-key" && sourceModel.model_id === targetModel.model_id && item.cardinality === "many-to-many") fail("PERSISTENCE_RELATION_SHAPE", `${pointer}/relation_mappings`, "many-to-many requires a join-table source model");
  }
  const mappedPhysicalFields = new Set(fieldMappings.map(item => item.physical_field_ref));
  for (const item of indexMappings) {
    if (!models.has(item.model_ref)) fail("PERSISTENCE_REFERENCE_UNRESOLVED", `${pointer}/index_mappings`, `index model unresolved:${item.model_ref}`);
    for (const field of item.field_refs) {
      const owners = physicalModels.filter(model => field.startsWith(`physical:${model.model_id.replace(/^physical-model:/, "")}/`));
      if (!mappedPhysicalFields.has(field) || owners.length !== 1 || owners[0]!.model_id !== item.model_ref)
        fail("PERSISTENCE_INDEX_FIELD", `${pointer}/index_mappings`, `index field must be mapped to exactly its declared model:${field}`);
    }
  }
  return Object.freeze({ mapping_id: reference(value.mapping_id, `${pointer}/mapping_id`), logical_subject_refs: refs(value.logical_subject_refs, `${pointer}/logical_subject_refs`, false), physical_models: Object.freeze(physicalModels), identity_mappings: Object.freeze(identityMappings), field_mappings: Object.freeze(fieldMappings), relation_mappings: Object.freeze(relationMappings), index_mappings: Object.freeze(indexMappings), conversion_rules: Object.freeze(conversionRules), version: reference(value.version, `${pointer}/version`), authority_effect: "none" });
}

function persistenceBinding(value: unknown, pointer: string): PersistenceBindingV2 {
  exact(value, ["binding_id", "integration_binding_ref", "logical_subject_refs", "dependency_contract_ref", "adapter_ref", "resource_ref", "implementation_profile_ref", "logical_physical_mapping_ref", "evidence_boundary", "authority_effect"], pointer);
  if (value.authority_effect !== "none") fail("PERSISTENCE_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ binding_id: reference(value.binding_id, `${pointer}/binding_id`), integration_binding_ref: reference(value.integration_binding_ref, `${pointer}/integration_binding_ref`), logical_subject_refs: refs(value.logical_subject_refs, `${pointer}/logical_subject_refs`, false), dependency_contract_ref: reference(value.dependency_contract_ref, `${pointer}/dependency_contract_ref`), adapter_ref: reference(value.adapter_ref, `${pointer}/adapter_ref`), resource_ref: reference(value.resource_ref, `${pointer}/resource_ref`), implementation_profile_ref: reference(value.implementation_profile_ref, `${pointer}/implementation_profile_ref`), logical_physical_mapping_ref: reference(value.logical_physical_mapping_ref, `${pointer}/logical_physical_mapping_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), authority_effect: "none" });
}

function transactionGuarantee(value: unknown, pointer: string): TransactionGuaranteeBindingV2 {
  exact(value, ["binding_id", "unit_of_work_contract_ref", "persistence_binding_refs", "participant_refs", "atomicity_scope", "local_commit_boundary_ref", "selected_guarantees", "implementation_profile_ref", "failure_mapping_ref", "evidence_boundary", "runtime_guarantees_observed", "authority_effect"], pointer);
  if (value.runtime_guarantees_observed !== false) fail("PERSISTENCE_RUNTIME_CLAIM", `${pointer}/runtime_guarantees_observed`, "formation is not transaction evidence");
  if (value.authority_effect !== "none") fail("PERSISTENCE_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  const guarantees = refs(value.selected_guarantees, `${pointer}/selected_guarantees`, false);
  const allowed = new Set(["atomicity", "isolation", "durability", "conflict-detection", "rollback-restoration"]);
  if (guarantees.some(item => !allowed.has(item))) fail("PERSISTENCE_GUARANTEE", `${pointer}/selected_guarantees`, "unknown guarantee");
  return Object.freeze({ binding_id: reference(value.binding_id, `${pointer}/binding_id`), unit_of_work_contract_ref: reference(value.unit_of_work_contract_ref, `${pointer}/unit_of_work_contract_ref`), persistence_binding_refs: refs(value.persistence_binding_refs, `${pointer}/persistence_binding_refs`, false), participant_refs: refs(value.participant_refs, `${pointer}/participant_refs`, false), atomicity_scope: oneOf(value.atomicity_scope, ["single-resource-local"] as const, `${pointer}/atomicity_scope`), local_commit_boundary_ref: reference(value.local_commit_boundary_ref, `${pointer}/local_commit_boundary_ref`), selected_guarantees: guarantees as TransactionGuaranteeBindingV2["selected_guarantees"], implementation_profile_ref: reference(value.implementation_profile_ref, `${pointer}/implementation_profile_ref`), failure_mapping_ref: reference(value.failure_mapping_ref, `${pointer}/failure_mapping_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), runtime_guarantees_observed: false, authority_effect: "none" });
}

function migrationStep(value: unknown, pointer: string): MigrationStepV1 {
  exact(value, ["step_id", "step_kind", "operation_ref", "reversible"], pointer);
  return Object.freeze({ step_id: reference(value.step_id, `${pointer}/step_id`), step_kind: oneOf(value.step_kind, ["schema", "data", "backfill", "verification"] as const, `${pointer}/step_kind`), operation_ref: reference(value.operation_ref, `${pointer}/operation_ref`), reversible: bool(value.reversible, `${pointer}/reversible`) });
}

function migration(value: unknown, pointer: string): MigrationContractV1 {
  exact(value, ["migration_id", "persistence_binding_ref", "from_version", "to_version", "forward_steps", "data_transform_refs", "compatibility_window", "rollback_posture", "rollback_step_refs", "verification_refs", "authority_effect"], pointer);
  if (value.authority_effect !== "none") fail("PERSISTENCE_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  const steps = records(value.forward_steps, `${pointer}/forward_steps`, false).map((entry, index) => migrationStep(entry, `${pointer}/forward_steps/${index}`));
  identities(steps, item => item.step_id, `${pointer}/forward_steps`);
  const rollbackPosture = oneOf(value.rollback_posture, ["reversible", "forward-only", "restore-from-backup", "manual"] as const, `${pointer}/rollback_posture`);
  const rollbackRefs = refs(value.rollback_step_refs, `${pointer}/rollback_step_refs`);
  if (rollbackPosture === "reversible" && rollbackRefs.length === 0) fail("PERSISTENCE_ROLLBACK", `${pointer}/rollback_step_refs`, "reversible migration requires rollback steps");
  if (rollbackPosture === "forward-only" && rollbackRefs.length !== 0) fail("PERSISTENCE_ROLLBACK", `${pointer}/rollback_step_refs`, "forward-only migration cannot declare rollback steps");
  return Object.freeze({ migration_id: reference(value.migration_id, `${pointer}/migration_id`), persistence_binding_ref: reference(value.persistence_binding_ref, `${pointer}/persistence_binding_ref`), from_version: reference(value.from_version, `${pointer}/from_version`), to_version: reference(value.to_version, `${pointer}/to_version`), forward_steps: Object.freeze(steps), data_transform_refs: refs(value.data_transform_refs, `${pointer}/data_transform_refs`), compatibility_window: oneOf(value.compatibility_window, ["none", "read-old-write-new", "dual-read", "dual-write"] as const, `${pointer}/compatibility_window`), rollback_posture: rollbackPosture, rollback_step_refs: rollbackRefs, verification_refs: refs(value.verification_refs, `${pointer}/verification_refs`, false), authority_effect: "none" });
}

export function validatePersistenceCompositionV2(value: unknown): PersistenceCompositionV2 {
  exact(value, ["schema_version", "composition_id", "integration_kernel", "persistence_bindings", "persistence_mappings", "transaction_guarantees", "migrations", "runtime_guarantees_observed", "authority_effect"], "/");
  if (value.schema_version !== "domainspec.persistence-composition/v2-candidate") fail("PERSISTENCE_SCHEMA", "/schema_version", "unsupported schema");
  if (value.runtime_guarantees_observed !== false) fail("PERSISTENCE_RUNTIME_CLAIM", "/runtime_guarantees_observed", "formation is not runtime evidence");
  if (value.authority_effect !== "none") fail("PERSISTENCE_AUTHORITY", "/authority_effect", "authority growth forbidden");
  const kernel = validateIntegrationKernelV2(value.integration_kernel);
  const bindings = records(value.persistence_bindings, "/persistence_bindings", false).map((entry, index) => persistenceBinding(entry, `/persistence_bindings/${index}`)).sort((a, b) => a.binding_id.localeCompare(b.binding_id));
  const mappings = records(value.persistence_mappings, "/persistence_mappings", false).map((entry, index) => persistenceMapping(entry, `/persistence_mappings/${index}`)).sort((a, b) => a.mapping_id.localeCompare(b.mapping_id));
  const guarantees = records(value.transaction_guarantees, "/transaction_guarantees").map((entry, index) => transactionGuarantee(entry, `/transaction_guarantees/${index}`)).sort((a, b) => a.binding_id.localeCompare(b.binding_id));
  const migrations = records(value.migrations, "/migrations").map((entry, index) => migration(entry, `/migrations/${index}`)).sort((a, b) => a.migration_id.localeCompare(b.migration_id));
  const integrationById = identities(kernel.integration_bindings, item => item.binding_id, "/integration_kernel/integration_bindings");
  const realizationById = identities(kernel.provider_realizations, item => item.realization_id, "/integration_kernel/provider_realizations");
  const mappingById = identities(mappings, item => item.mapping_id, "/persistence_mappings");
  const bindingById = identities(bindings, item => item.binding_id, "/persistence_bindings");
  const failureById = identities(kernel.failure_mappings, item => item.mapping_id, "/integration_kernel/failure_mappings");
  identities(guarantees, item => item.binding_id, "/transaction_guarantees");
  identities(migrations, item => item.migration_id, "/migrations");
  for (const binding of bindings) {
    const integration = integrationById.get(binding.integration_binding_ref);
    if (!integration || integration.concern !== "persistence") fail("PERSISTENCE_REFERENCE_UNRESOLVED", "/persistence_bindings", `persistence integration binding unresolved:${binding.integration_binding_ref}`);
    const realization = realizationById.get(integration.provider_realization_ref)!;
    if (integration.contract_ref !== binding.dependency_contract_ref || realization.adapter_ref !== binding.adapter_ref || realization.resource_ref !== binding.resource_ref || realization.provider_profile_ref !== binding.implementation_profile_ref) fail("PERSISTENCE_BINDING_DRIFT", "/persistence_bindings", `D46 specialization disagrees with shared kernel:${binding.binding_id}`);
    const mapping = mappingById.get(binding.logical_physical_mapping_ref);
    if (!mapping || canonicalJson(mapping.logical_subject_refs) !== canonicalJson(binding.logical_subject_refs)) fail("PERSISTENCE_MAPPING_DRIFT", "/persistence_bindings", `mapping subject mismatch:${binding.binding_id}`);
  }
  for (const guarantee of guarantees) {
    for (const bindingRef of guarantee.persistence_binding_refs) if (!bindingById.has(bindingRef)) fail("PERSISTENCE_REFERENCE_UNRESOLVED", "/transaction_guarantees", `persistence binding unresolved:${bindingRef}`);
    if (!failureById.has(guarantee.failure_mapping_ref)) fail("PERSISTENCE_REFERENCE_UNRESOLVED", "/transaction_guarantees", `failure mapping unresolved:${guarantee.failure_mapping_ref}`);
  }
  for (const item of migrations) if (!bindingById.has(item.persistence_binding_ref)) fail("PERSISTENCE_REFERENCE_UNRESOLVED", "/migrations", `persistence binding unresolved:${item.persistence_binding_ref}`);
  return freeze({ schema_version: "domainspec.persistence-composition/v2-candidate", composition_id: reference(value.composition_id, "/composition_id"), integration_kernel: kernel, persistence_bindings: Object.freeze(bindings), persistence_mappings: Object.freeze(mappings), transaction_guarantees: Object.freeze(guarantees), migrations: Object.freeze(migrations), runtime_guarantees_observed: false, authority_effect: "none" });
}

export function compilePersistenceCompositionV2(value: unknown): CompiledPersistenceCompositionV2 {
  const composition = validatePersistenceCompositionV2(value);
  const compiled = { ...composition, integration_kernel: compileIntegrationKernelV2(composition.integration_kernel) };
  return freeze({ ...compiled, composition_digest: sha256(canonicalJson(compiled)) });
}
