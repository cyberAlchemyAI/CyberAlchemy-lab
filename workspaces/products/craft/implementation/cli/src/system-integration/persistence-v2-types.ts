import type { CompiledIntegrationKernelV2, IntegrationKernelV2 } from "./kernel-v2-types.js";

export type PersistenceShape =
  | "scalar"
  | "entity-reference"
  | "value-object"
  | "enum"
  | "sum"
  | "optional"
  | "list"
  | "set";

export interface PersistenceBindingV2 {
  readonly binding_id: string;
  readonly integration_binding_ref: string;
  readonly logical_subject_refs: readonly string[];
  readonly dependency_contract_ref: string;
  readonly adapter_ref: string;
  readonly resource_ref: string;
  readonly implementation_profile_ref: string;
  readonly logical_physical_mapping_ref: string;
  readonly evidence_boundary: string;
  readonly authority_effect: "none";
}

export interface PhysicalModelV1 {
  readonly model_id: string;
  readonly model_kind: "relational-table" | "document" | "key-value";
  readonly physical_name: string;
  readonly version: string;
}

export interface IdentityMappingV1 {
  readonly logical_property_ref: string;
  readonly physical_field_ref: string;
  readonly conversion_ref: string | null;
}

export interface PersistenceFieldMappingV1 {
  readonly logical_property_ref: string;
  readonly logical_shape: PersistenceShape;
  readonly physical_field_ref: string;
  readonly storage_shape: "scalar" | "foreign-key" | "embedded" | "discriminator" | "nullable" | "array" | "join-table";
  readonly collection_semantics: "not-applicable" | "ordered" | "unique-unordered";
  readonly conversion_ref: string | null;
}

export interface PersistenceRelationMappingV1 {
  readonly relation_ref: string;
  readonly source_field_ref: string;
  readonly target_model_ref: string;
  readonly target_field_ref: string;
  readonly cardinality: "one-to-one" | "many-to-one" | "one-to-many" | "many-to-many";
  readonly storage_strategy: "foreign-key" | "join-table" | "embedded";
}

export interface PersistenceIndexMappingV1 {
  readonly index_id: string;
  readonly model_ref: string;
  readonly physical_name: string;
  readonly field_refs: readonly string[];
  readonly unique: boolean;
  readonly order: "ordered" | "unordered";
}

export interface PersistenceConversionRuleV1 {
  readonly conversion_id: string;
  readonly source_shape: string;
  readonly target_shape: string;
  readonly direction: "to-storage" | "from-storage" | "bidirectional";
  readonly lossless: boolean;
  readonly implementation_ref: string;
}

export interface PersistenceMappingV1 {
  readonly mapping_id: string;
  readonly logical_subject_refs: readonly string[];
  readonly physical_models: readonly PhysicalModelV1[];
  readonly identity_mappings: readonly IdentityMappingV1[];
  readonly field_mappings: readonly PersistenceFieldMappingV1[];
  readonly relation_mappings: readonly PersistenceRelationMappingV1[];
  readonly index_mappings: readonly PersistenceIndexMappingV1[];
  readonly conversion_rules: readonly PersistenceConversionRuleV1[];
  readonly version: string;
  readonly authority_effect: "none";
}

export interface TransactionGuaranteeBindingV2 {
  readonly binding_id: string;
  readonly unit_of_work_contract_ref: string;
  readonly persistence_binding_refs: readonly string[];
  readonly participant_refs: readonly string[];
  readonly atomicity_scope: "single-resource-local";
  readonly local_commit_boundary_ref: string;
  readonly selected_guarantees: readonly ("atomicity" | "isolation" | "durability" | "conflict-detection" | "rollback-restoration")[];
  readonly implementation_profile_ref: string;
  readonly failure_mapping_ref: string;
  readonly evidence_boundary: string;
  readonly runtime_guarantees_observed: false;
  readonly authority_effect: "none";
}

export interface MigrationStepV1 {
  readonly step_id: string;
  readonly step_kind: "schema" | "data" | "backfill" | "verification";
  readonly operation_ref: string;
  readonly reversible: boolean;
}

export interface MigrationContractV1 {
  readonly migration_id: string;
  readonly persistence_binding_ref: string;
  readonly from_version: string;
  readonly to_version: string;
  readonly forward_steps: readonly MigrationStepV1[];
  readonly data_transform_refs: readonly string[];
  readonly compatibility_window: "none" | "read-old-write-new" | "dual-read" | "dual-write";
  readonly rollback_posture: "reversible" | "forward-only" | "restore-from-backup" | "manual";
  readonly rollback_step_refs: readonly string[];
  readonly verification_refs: readonly string[];
  readonly authority_effect: "none";
}

export interface PersistenceCompositionV2 {
  readonly schema_version: "domainspec.persistence-composition/v2-candidate";
  readonly composition_id: string;
  readonly integration_kernel: IntegrationKernelV2;
  readonly persistence_bindings: readonly PersistenceBindingV2[];
  readonly persistence_mappings: readonly PersistenceMappingV1[];
  readonly transaction_guarantees: readonly TransactionGuaranteeBindingV2[];
  readonly migrations: readonly MigrationContractV1[];
  readonly runtime_guarantees_observed: false;
  readonly authority_effect: "none";
}

export interface CompiledPersistenceCompositionV2 extends Omit<PersistenceCompositionV2, "integration_kernel"> {
  readonly integration_kernel: CompiledIntegrationKernelV2;
  readonly composition_digest: string;
}
