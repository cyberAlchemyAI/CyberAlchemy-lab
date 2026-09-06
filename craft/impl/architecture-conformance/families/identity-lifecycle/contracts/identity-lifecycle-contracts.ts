import type {
  ConstructionFactoryRefV1,
  ConstructionValidatorRefV1,
  EntityConstructionRouteV1,
  EntityLifecycleConstructionObservationV1,
} from "../../../kernel/evidence/construction-observation/index.js";

export const IDENTITY_LIFECYCLE_POSITIVE_OBLIGATIONS = Object.freeze([
  "validators-before-construction",
  "valid-input-one-immutable-snapshot",
  "lifecycle-transition-preserves-identity",
  "same-identity-different-state-equal",
  "distinct-identities-remain-distinct",
] as const);
export type IdentityLifecyclePositiveObligation =
  (typeof IDENTITY_LIFECYCLE_POSITIVE_OBLIGATIONS)[number];

export const IDENTITY_LIFECYCLE_HOSTILE_CLASSES = Object.freeze([
  "per-call-always-true-validator-bypass",
  "remove-base-validator",
  "replace-identity-resolver",
  "allow-extension-cycle",
  "invalid-input-forms-snapshot",
  "mutate-constructed-snapshot",
  "complete-field-equality",
] as const);
export type IdentityLifecycleHostileClass =
  (typeof IDENTITY_LIFECYCLE_HOSTILE_CLASSES)[number];

export type IdentityLifecycleDefinitionV1 = Readonly<{
  schema_version: "IdentityLifecycleDefinition/v1";
  definition_id: string;
  status: "candidate-fixture";
  authorship: "owner-authored-admission-input";
  derivation_policy: "implementation-and-generated-results-forbidden-as-authority";
  descriptor_ref: Readonly<{
    descriptor_id: string;
    path: string;
    sha256: string;
  }>;
  concept_id: string;
  factories: Readonly<{
    base: ConstructionFactoryRefV1;
    extension: ConstructionFactoryRefV1;
  }>;
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
  extension_policy: Readonly<{
    mode: "additive-only";
    cycle_policy: "acyclic";
    base_validators_preserved: true;
    identity_resolver_preserved: true;
  }>;
  authority_effect: "none";
}>;

export type IdentityLifecycleDenominatorV1 = Readonly<{
  schema_version: "IdentityLifecycleDenominator/v1";
  denominator_id: string;
  owner_definition_ref: Readonly<{
    definition_id: string;
    path: string;
    sha256: string;
  }>;
  portable_contract: Readonly<{
    identity: "one-or-more-exact-typed-components-stable-across-snapshots";
    equality_and_hash: "canonical-identity-only";
    validator_order: "owner-bound-base-then-extension-before-identity-and-construction";
    formation_failure: "structured-failure-no-snapshot";
    lifecycle: "ordered-immutable-snapshot-sequence";
    extension: "additive-only-acyclic-preserves-base-and-identity";
    routes: "exact-four-with-direct-constructor-inaccessible-or-delegating";
    evidence_origin: "locked-independent-owner-not-provider";
  }>;
  positive_obligations: readonly IdentityLifecyclePositiveObligation[];
  semantic_hostile_classes: readonly IdentityLifecycleHostileClass[];
  construction_routes: readonly EntityConstructionRouteV1[];
  authority_effect: "none";
  denominator_sha256: string;
}>;

export type IdentityLifecycleFindingCode =
  | "FAMILY_ENTITY_TARGET_OBSERVATION_MISSING"
  | "FAMILY_ENTITY_DEFINITION_PROVENANCE_MISMATCH"
  | "FAMILY_ENTITY_EVIDENCE_NOT_INDEPENDENT"
  | "FAMILY_ENTITY_FACTORY_BINDING_MISMATCH"
  | "FAMILY_ENTITY_ROUTE_CONVERGENCE_MISMATCH"
  | "FAMILY_ENTITY_VALIDATOR_BYPASS"
  | "FAMILY_ENTITY_BASE_VALIDATOR_REMOVED"
  | "FAMILY_ENTITY_IDENTITY_RESOLVER_REPLACED"
  | "FAMILY_ENTITY_EXTENSION_CYCLE"
  | "FAMILY_ENTITY_INVALID_INPUT_FORMED_SNAPSHOT"
  | "FAMILY_ENTITY_MUTABLE_SNAPSHOT"
  | "FAMILY_ENTITY_COMPLETE_FIELD_EQUALITY"
  | "FAMILY_ENTITY_IDENTITY_STABILITY_MISMATCH"
  | "FAMILY_ENTITY_IDENTITY_EQUALITY_OR_HASH_MISMATCH"
  | "FAMILY_ENTITY_OBSERVATION_INTEGRITY_MISMATCH"
  | "FAMILY_ENTITY_SNAPSHOT_LEDGER_MISMATCH";

export type IdentityLifecycleFindingV1 = Readonly<{
  code: IdentityLifecycleFindingCode;
  obligation_id: IdentityLifecyclePositiveObligation | null;
  expected: string | null;
  observed: string | null;
}>;

export type IdentityLifecycleEvaluationV1 = Readonly<{
  schema_version: "IdentityLifecycleEvaluation/v1";
  evaluation_id: string;
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  observation_ref: Readonly<{
    observation_id: string | null;
    observation_sha256: string | null;
  }>;
  verdict: "pass" | "fail";
  findings: readonly IdentityLifecycleFindingV1[];
  positive_obligation_accounting: Readonly<{
    declared: 5;
    passed: number;
    failed: number;
    unaccounted: 0;
  }>;
  hostile_class_accounting: Readonly<{
    declared: 7;
    represented: number;
    unrepresented: number;
  }>;
  construction_route_accounting: Readonly<{
    declared: 4;
    observed: number;
    conforming: number;
    unaccounted: number;
  }>;
  portable_claim: "owner-bound-stable-identity-lifecycle-transport-proof";
  native_runtime_claim: false;
  collision_freedom_claim: false;
  authority_effect: "none";
}>;

export const IDENTITY_LIFECYCLE_MUTATION_BLUEPRINT = Object.freeze([
  Object.freeze({mutation_id: "validators/per-call-always-true",
    hostile_class: "per-call-always-true-validator-bypass",
    mutation_kind: "per-call-validator-bypass"}),
  Object.freeze({mutation_id: "extension/remove-base-validator",
    hostile_class: "remove-base-validator",
    mutation_kind: "remove-base-validator"}),
  Object.freeze({mutation_id: "identity/replace-resolver",
    hostile_class: "replace-identity-resolver",
    mutation_kind: "replace-identity-resolver"}),
  Object.freeze({mutation_id: "extension/allow-cycle",
    hostile_class: "allow-extension-cycle",
    mutation_kind: "allow-extension-cycle"}),
  Object.freeze({mutation_id: "formation/invalid-forms-snapshot",
    hostile_class: "invalid-input-forms-snapshot",
    mutation_kind: "invalid-input-forms-snapshot"}),
  Object.freeze({mutation_id: "lifecycle/mutate-snapshot",
    hostile_class: "mutate-constructed-snapshot",
    mutation_kind: "mutate-constructed-snapshot"}),
  Object.freeze({mutation_id: "equality/complete-fields",
    hostile_class: "complete-field-equality",
    mutation_kind: "complete-field-equality"}),
] as const);
export type IdentityLifecycleMutationKind =
  (typeof IDENTITY_LIFECYCLE_MUTATION_BLUEPRINT)[number]["mutation_kind"];

export type IdentityLifecycleMutationV1 = Readonly<{
  mutation_id: string;
  hostile_class: IdentityLifecycleHostileClass;
  mutation_kind: IdentityLifecycleMutationKind;
  expected_finding_codes: readonly IdentityLifecycleFindingCode[];
}>;

export type IdentityLifecycleMutationCatalogueV1 = Readonly<{
  schema_version: "IdentityLifecycleMutationCatalogue/v1";
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  authorship: "independent-family-fixture";
  target_code_may_read_expected_findings: false;
  mutations: readonly IdentityLifecycleMutationV1[];
  authority_effect: "none";
  catalogue_sha256: string;
}>;

export type IdentityLifecycleObservationV1 =
  EntityLifecycleConstructionObservationV1;
