export type ArchitectureValueType = Readonly<Record<string, unknown>>;

export type ArchitecturePropertyRequirement = Readonly<{
  property_id: string;
  value_type: ArchitectureValueType;
  observation_stage: string;
  owner_route: string;
  forbidden_inference: string;
}>;

export type ArchitectureConstraintOperator = Readonly<{
  operator_id: string;
  accepted_value_types: readonly string[];
  expected_operand_kinds: readonly string[];
}>;

export type ArchitectureRealizationSpec = Readonly<{
  schema_version: "ArchitectureRealizationSpec/v1";
  spec_id: string;
  ontology_ref: Readonly<{
    ontology_id: string;
    schema_version: string;
    sha256: string;
  }>;
  profile_ref: Readonly<{
    profile_id: string;
    schema_version: string;
    sha256: string;
    extends: readonly Readonly<{
      profile_id: string;
      schema_version: string;
      sha256: string;
    }>[];
  }>;
  realization_type: "architecture.EnumImplementation";
  definition_type_ref: string;
  required_properties: readonly ArchitecturePropertyRequirement[];
  required_relations: readonly string[];
  constraint_operators: readonly ArchitectureConstraintOperator[];
  composition_kind: "direct";
  unsupported_outcomes: readonly string[];
  spec_sha256: string;
  authority_effect: "none";
}>;

export type ArchitectureRealizationSourceDigests = Readonly<{
  ontology_sha256: string;
  base_profile_sha256: string;
  typescript_profile_sha256: string;
}>;

export type EnumRealizationProjectionInput = Readonly<{
  spec_id: string;
  ontology_json: string;
  base_profile_json: string;
  typescript_profile_json: string;
  expected_source_digests: ArchitectureRealizationSourceDigests;
}>;

export type ArchitectureRealizationFailure = Error & Readonly<{
  code: string;
  detail?: Readonly<Record<string, unknown>>;
}>;

