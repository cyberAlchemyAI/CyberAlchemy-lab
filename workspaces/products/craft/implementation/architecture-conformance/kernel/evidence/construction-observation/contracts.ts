export type LockedConstructionObserverRefV1 = Readonly<{
  role: "independent-construction-observer";
  observer_id: string;
  observer_sha256: string;
  owner_ref: string;
  provider_id: string;
  provider_sha256: string;
}>;

export type ConstructionFactoryRefV1 = Readonly<{
  factory_id: string;
  factory_sha256: string;
  concept_id: string;
}>;

export type ConstructionComponentBindingV1 = Readonly<{
  component_name: string;
  protocol_id: string;
  protocol_sha256: string;
  normalized_value_sha256: string;
  nested_value_object: boolean;
}>;

export type ConstructionValidatorRefV1 = Readonly<{
  validator_id: string;
  validator_sha256: string;
  origin: "base" | "extension";
}>;

export type ConstructionAttemptV1 = Readonly<{
  case_id: string;
  input_class: "valid" | "invalid";
  component_bindings: readonly ConstructionComponentBindingV1[];
  validator_trace: readonly Readonly<ConstructionValidatorRefV1 & {
    ordinal: number;
    outcome: "pass" | "fail";
  }>[];
  formation_ordinal: number | null;
  result: Readonly<{
    status: "formed" | "validation-failure";
    object_created: boolean;
    failure_codes: readonly string[];
  }>;
  normalized_tuple: readonly Readonly<{
    component_name: string;
    normalized_value_sha256: string;
  }>[] | null;
  immutability: Readonly<{
    formed_value_frozen: boolean;
    recursively_owned_components_frozen: boolean;
    nested_alias_observed: boolean;
    nested_mutation_observed: boolean;
  }>;
}>;

export type ConstructionEqualityProbeV1 = Readonly<{
  probe_id: string;
  left_case_id: string;
  right_case_id: string;
  relation: "equal-tuple" | "component-variant";
  varied_component_name: string | null;
  references_distinct: boolean;
  observed_equal: boolean;
  left_hash_sha256: string;
  right_hash_sha256: string;
}>;

export type ConstructionNestedDelegationV1 = Readonly<{
  component_name: string;
  protocol_id: string;
  protocol_sha256: string;
  equality_delegated: boolean;
  hash_delegated: boolean;
}>;

export type ConstructionExtensionEvidenceV1 = Readonly<{
  base_factory_ref: ConstructionFactoryRefV1;
  extension_factory_ref: ConstructionFactoryRefV1;
  added_validators: readonly ConstructionValidatorRefV1[];
  altered_facets: readonly string[];
  cycle_detected: boolean;
}>;

export type ConstructionObservationV1 = Readonly<{
  schema_version: "ConstructionObservation/v1";
  observation_id: string;
  source_kind:
    | "independent-family-fixture"
    | "target-observation"
    | "mutated-construction-observation";
  observer_ref: LockedConstructionObserverRefV1;
  definition_ref: Readonly<{
    definition_id: string;
    path: string;
    sha256: string;
  }>;
  factory_ref: ConstructionFactoryRefV1;
  attempts: readonly ConstructionAttemptV1[];
  equality_probes: readonly ConstructionEqualityProbeV1[];
  nested_delegations: readonly ConstructionNestedDelegationV1[];
  extension: ConstructionExtensionEvidenceV1;
  claim: "transport-observation-only-no-native-runtime-claim";
  collision_freedom_claim: false;
  authority_effect: "none";
  observation_sha256: string;
}>;

export type DeclaredConstructionContractV1 = Readonly<{
  factory_ref: ConstructionFactoryRefV1;
  components: readonly Readonly<{
    component_name: string;
    protocol_id: string;
    protocol_sha256: string;
    nested_value_object: boolean;
  }>[];
  validators: readonly ConstructionValidatorRefV1[];
  cases: readonly Readonly<{
    case_id: string;
    input_class: "valid" | "invalid";
    expected_components: readonly Readonly<{
      component_name: string;
      normalized_value_sha256: string;
    }>[];
    expected_failure_codes: readonly string[];
  }>[];
  equal_probe_ids: readonly string[];
  component_variant_probe_ids: Readonly<Record<string, string>>;
  nested_component_names: readonly string[];
  extension_factory_ref: ConstructionFactoryRefV1;
}>;

export type ConstructionObservationDiagnostic =
  | "CONSTRUCTION_OBSERVER_BINDING_MISMATCH"
  | "CONSTRUCTION_OBSERVER_SELF_ISSUED"
  | "CONSTRUCTION_DEFINITION_BINDING_MISMATCH"
  | "CONSTRUCTION_FACTORY_BINDING_MISMATCH"
  | "CONSTRUCTION_CASE_LEDGER_MISMATCH"
  | "CONSTRUCTION_CASE_CLASS_MISMATCH"
  | "CONSTRUCTION_COMPONENT_PROTOCOL_MISMATCH"
  | "CONSTRUCTION_COMPONENT_VALUE_MISMATCH"
  | "CONSTRUCTION_VALIDATOR_ORDER_MISMATCH"
  | "CONSTRUCTION_FORMATION_ORDER_MISMATCH"
  | "CONSTRUCTION_INVALID_INPUT_FORMED"
  | "CONSTRUCTION_VALID_INPUT_NOT_FORMED"
  | "CONSTRUCTION_TUPLE_INCOMPLETE"
  | "CONSTRUCTION_TUPLE_EXPECTATION_MISMATCH"
  | "CONSTRUCTION_FAILURE_CODE_MISMATCH"
  | "CONSTRUCTION_REFERENCE_IDENTITY_OBSERVED"
  | "CONSTRUCTION_COMPONENT_VARIANT_EQUAL"
  | "CONSTRUCTION_EQUAL_TUPLE_UNEQUAL"
  | "CONSTRUCTION_EQUAL_HASH_INCONGRUENT"
  | "CONSTRUCTION_RECURSIVE_IMMUTABILITY_VIOLATION"
  | "CONSTRUCTION_NESTED_DELEGATION_MISMATCH"
  | "CONSTRUCTION_EXTENSION_BINDING_MISMATCH"
  | "CONSTRUCTION_EXTENSION_NOT_ADDITIVE"
  | "CONSTRUCTION_EXTENSION_CYCLE";

export type ConstructionObservationEvaluationV1 = Readonly<{
  schema_version: "ConstructionObservationEvaluation/v1";
  evaluation_id: string;
  observation_ref: Readonly<{
    observation_id: string;
    observation_sha256: string;
  }>;
  result: "pass" | "fail";
  diagnostics: readonly ConstructionObservationDiagnostic[];
  accounting: Readonly<{
    declared_components: number;
    observed_components_per_valid_case: number;
    declared_validators: number;
    observed_attempts: number;
    equality_probes: number;
  }>;
  claim: "construction-transport-evaluation-no-native-runtime-interception";
  collision_freedom_claim: false;
  authority_effect: "none";
}>;
