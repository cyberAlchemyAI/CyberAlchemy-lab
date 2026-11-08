import type {
  ConstructionFactoryRefV1,
  ConstructionValidatorRefV1,
  LockedConstructionObserverRefV1,
} from "./contracts.js";

export const ENTITY_CONSTRUCTION_ROUTES = Object.freeze([
  "factory",
  "deserialization-reconstruction",
  "lifecycle-transition",
  "language-visible-direct-constructor",
] as const);
export type EntityConstructionRouteV1 =
  (typeof ENTITY_CONSTRUCTION_ROUTES)[number];

export type EntityIdentityComponentV1 = Readonly<{
  component_name: string;
  type_id: string;
  type_sha256: string;
  normalized_value_sha256: string;
}>;

export type EntityLifecycleSnapshotV1 = Readonly<{
  snapshot_id: string;
  entity_case_id: string;
  sequence: number;
  route_id: EntityConstructionRouteV1;
  predecessor_snapshot_id: string | null;
  identity: readonly EntityIdentityComponentV1[];
  state_sha256: string;
  frozen: boolean;
  mutation_observed: boolean;
}>;

export type EntityConstructionRouteTraceV1 = Readonly<{
  route_id: EntityConstructionRouteV1;
  input_class: "valid";
  normalization_ordinal: number | null;
  validator_trace: readonly Readonly<ConstructionValidatorRefV1 & {
    ordinal: number;
    outcome: "pass";
  }>[];
  identity_resolution_ordinal: number | null;
  construction_ordinal: number | null;
  immutability_ordinal: number | null;
  direct_constructor_policy:
    | "not-applicable"
    | "private-inaccessible"
    | "delegating-facade";
  result: Readonly<{
    status: "formed" | "constructor-inaccessible";
    snapshot_created: boolean;
    snapshot_id: string | null;
  }>;
}>;

export type EntityValidationFailureProbeV1 = Readonly<{
  probe_id: string;
  route_id: "factory";
  validator_trace: readonly Readonly<ConstructionValidatorRefV1 & {
    ordinal: number;
    outcome: "pass" | "fail";
  }>[];
  identity_resolution_ordinal: number | null;
  construction_ordinal: number | null;
  result: Readonly<{
    status: "validation-failure";
    snapshot_created: boolean;
    failure_codes: readonly string[];
  }>;
}>;

export type EntityIdentityEqualityProbeV1 = Readonly<{
  probe_id: string;
  left_snapshot_id: string;
  right_snapshot_id: string;
  relation: "same-identity-different-state" | "distinct-identity";
  comparison_basis: "canonical-identity-only";
  observed_equal: boolean;
  left_hash_sha256: string;
  right_hash_sha256: string;
}>;

export type EntityFactoryExtensionEvidenceV1 = Readonly<{
  base_factory_ref: ConstructionFactoryRefV1;
  extension_factory_ref: ConstructionFactoryRefV1;
  base_validators_preserved: boolean;
  added_validators: readonly ConstructionValidatorRefV1[];
  identity_resolver_preserved: boolean;
  altered_facets: readonly string[];
  cycle_detected: boolean;
}>;

export type EntityLifecycleConstructionObservationV1 = Readonly<{
  schema_version: "EntityLifecycleConstructionObservation/v1";
  observation_id: string;
  source_kind:
    | "independent-family-fixture"
    | "target-observation"
    | "mutated-entity-lifecycle-observation";
  observer_ref: LockedConstructionObserverRefV1;
  definition_ref: Readonly<{
    definition_id: string;
    path: string;
    sha256: string;
  }>;
  factory_ref: ConstructionFactoryRefV1;
  route_traces: readonly EntityConstructionRouteTraceV1[];
  validation_failure_probe: EntityValidationFailureProbeV1;
  snapshots: readonly EntityLifecycleSnapshotV1[];
  equality_probes: readonly EntityIdentityEqualityProbeV1[];
  extension: EntityFactoryExtensionEvidenceV1;
  per_call_validator_supplied: boolean;
  claim: "transport-observation-only-no-native-runtime-claim";
  collision_freedom_claim: false;
  authority_effect: "none";
  observation_sha256: string;
}>;

export type DeclaredEntityLifecycleConstructionContractV1 = Readonly<{
  factory_ref: ConstructionFactoryRefV1;
  extension_factory_ref: ConstructionFactoryRefV1;
  identity_components: readonly Readonly<{
    component_name: string;
    type_id: string;
    type_sha256: string;
  }>[];
  validators: readonly ConstructionValidatorRefV1[];
  construction_routes: readonly EntityConstructionRouteV1[];
  direct_constructor_policy: "private-inaccessible-or-delegating-facade";
  snapshots: readonly Readonly<{
    snapshot_id: string;
    entity_case_id: string;
    sequence: number;
    route_id: EntityConstructionRouteV1;
    predecessor_snapshot_id: string | null;
    identity_values: Readonly<Record<string, string>>;
    state_sha256: string;
  }>[];
  equality_probes: readonly Readonly<{
    probe_id: string;
    left_snapshot_id: string;
    right_snapshot_id: string;
    relation: "same-identity-different-state" | "distinct-identity";
    expected_equal: boolean;
  }>[];
  validation_failure: Readonly<{
    probe_id: string;
    expected_failure_codes: readonly string[];
  }>;
}>;

export type EntityLifecycleConstructionDiagnostic =
  | "ENTITY_OBSERVATION_DIGEST_MISMATCH"
  | "ENTITY_OBSERVER_BINDING_MISMATCH"
  | "ENTITY_OBSERVER_SELF_ISSUED"
  | "ENTITY_DEFINITION_BINDING_MISMATCH"
  | "ENTITY_FACTORY_BINDING_MISMATCH"
  | "ENTITY_ROUTE_LEDGER_MISMATCH"
  | "ENTITY_DIRECT_CONSTRUCTOR_BYPASS"
  | "ENTITY_VALIDATOR_BINDING_MISMATCH"
  | "ENTITY_VALIDATOR_ORDER_MISMATCH"
  | "ENTITY_IDENTITY_RESOLUTION_ORDER_MISMATCH"
  | "ENTITY_CONSTRUCTION_ORDER_MISMATCH"
  | "ENTITY_VALID_INPUT_NOT_ONE_SNAPSHOT"
  | "ENTITY_INVALID_INPUT_FORMED_SNAPSHOT"
  | "ENTITY_FAILURE_CODE_MISMATCH"
  | "ENTITY_IDENTITY_COMPONENT_MISMATCH"
  | "ENTITY_IDENTITY_CHANGED_ACROSS_LIFECYCLE"
  | "ENTITY_SNAPSHOT_LEDGER_MISMATCH"
  | "ENTITY_SNAPSHOT_MUTABLE"
  | "ENTITY_IDENTITY_EQUALITY_MISMATCH"
  | "ENTITY_IDENTITY_HASH_INCONGRUENT"
  | "ENTITY_COMPLETE_FIELD_EQUALITY"
  | "ENTITY_EXTENSION_BINDING_MISMATCH"
  | "ENTITY_BASE_VALIDATOR_REMOVED"
  | "ENTITY_IDENTITY_RESOLVER_REPLACED"
  | "ENTITY_EXTENSION_NOT_ADDITIVE"
  | "ENTITY_EXTENSION_CYCLE"
  | "ENTITY_PER_CALL_VALIDATOR_BYPASS";

export type EntityLifecycleConstructionEvaluationV1 = Readonly<{
  schema_version: "EntityLifecycleConstructionEvaluation/v1";
  evaluation_id: string;
  observation_ref: Readonly<{
    observation_id: string;
    observation_sha256: string;
  }>;
  result: "pass" | "fail";
  diagnostics: readonly EntityLifecycleConstructionDiagnostic[];
  accounting: Readonly<{
    typed_identity_components: number;
    declared_validators: number;
    construction_routes: number;
    lifecycle_snapshots: number;
    equality_probes: number;
  }>;
  claim: "entity-lifecycle-transport-evaluation-no-native-runtime-interception";
  collision_freedom_claim: false;
  authority_effect: "none";
}>;
