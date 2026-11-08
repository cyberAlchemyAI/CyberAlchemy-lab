import type {
  ConstructionFactoryRefV1,
  ConstructionObservationV1,
  ConstructionValidatorRefV1,
} from "../../../kernel/evidence/construction-observation/index.js";

export const COMPLETE_VALUE_DECISIONS = Object.freeze([
  "validators-before-formation",
  "equal-tuples-equal-and-hash-equally",
  "every-component-participates",
  "recursive-owned-immutability",
  "extension-preserves-contract",
  "exact-component-protocol-identity-and-digest",
  "nested-values-delegate-owned-protocol",
] as const);
export type CompleteValueDecisionId = (typeof COMPLETE_VALUE_DECISIONS)[number];

export const COMPLETE_VALUE_HOSTILE_CLASSES = Object.freeze([
  "reference-identity",
  "partial-tuple-equality",
  "incongruent-hash",
  "mutable-nested-component",
  "per-call-validator-bypass",
  "tuple-changing-extension",
  "component-without-owned-protocol",
  "invalid-input-forms-object",
] as const);
export type CompleteValueHostileClass =
  (typeof COMPLETE_VALUE_HOSTILE_CLASSES)[number];

export type CompleteValueDefinitionV1 = Readonly<{
  schema_version: "CompleteValueDefinition/v1";
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
    normalized_component_values: Readonly<Record<string, string>>;
    expected_failure_codes: readonly string[];
  }>[];
  equality_contract: Readonly<{
    equal_probe: Readonly<{
      probe_id: string;
      left_case_id: string;
      right_case_id: string;
    }>;
    component_variants: readonly Readonly<{
      probe_id: string;
      component_name: string;
      left_case_id: string;
      right_case_id: string;
    }>[];
    collision_freedom_claim: false;
  }>;
  authority_effect: "none";
}>;

export type CompleteValueDenominatorV1 = Readonly<{
  schema_version: "CompleteValueDenominator/v1";
  denominator_id: string;
  owner_definition_ref: Readonly<{
    definition_id: string;
    path: string;
    sha256: string;
  }>;
  portable_contract: Readonly<{
    component_admission: "exact-current-owner-protocol-identity-and-digest";
    validator_order: "base-before-extension-before-formation";
    formation_failure: "structured-failure-no-object";
    equality: "complete-normalized-tuple";
    hash: "same-normalized-complete-tuple-congruent-not-collision-free";
    immutability: "formed-and-recursive-owned-components";
    extension: "additive-validation-only-acyclic";
    evidence_origin: "locked-independent-owner-not-provider";
  }>;
  positive_decisions: readonly CompleteValueDecisionId[];
  semantic_hostile_classes: readonly CompleteValueHostileClass[];
  authority_effect: "none";
  denominator_sha256: string;
}>;

export type CompleteValueFindingCode =
  | "FAMILY_VALUE_TARGET_OBSERVATION_MISSING"
  | "FAMILY_VALUE_DEFINITION_PROVENANCE_MISMATCH"
  | "FAMILY_VALUE_EVIDENCE_NOT_INDEPENDENT"
  | "FAMILY_VALUE_FACTORY_BINDING_MISMATCH"
  | "FAMILY_VALUE_REFERENCE_IDENTITY"
  | "FAMILY_VALUE_PARTIAL_TUPLE_EQUALITY"
  | "FAMILY_VALUE_INCONGRUENT_HASH"
  | "FAMILY_VALUE_MUTABLE_NESTED_COMPONENT"
  | "FAMILY_VALUE_VALIDATOR_BYPASS"
  | "FAMILY_VALUE_TUPLE_CHANGING_EXTENSION"
  | "FAMILY_VALUE_COMPONENT_PROTOCOL_MISMATCH"
  | "FAMILY_VALUE_INVALID_INPUT_FORMED"
  | "FAMILY_VALUE_NESTED_DELEGATION_MISMATCH"
  | "FAMILY_VALUE_CASE_LEDGER_MISMATCH";

export type CompleteValueFindingV1 = Readonly<{
  code: CompleteValueFindingCode;
  decision_id: CompleteValueDecisionId | null;
  case_id: string | null;
  component_name: string | null;
  expected: string | null;
  observed: string | null;
}>;

export type CompleteValueEvaluationV1 = Readonly<{
  schema_version: "CompleteValueEvaluation/v1";
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
  findings: readonly CompleteValueFindingV1[];
  positive_decision_accounting: Readonly<{
    declared: 7;
    passed: number;
    failed: number;
    unaccounted: 0;
  }>;
  hostile_class_accounting: Readonly<{
    declared: 8;
    represented: number;
    unrepresented: number;
  }>;
  portable_claim: "owner-bound-complete-immutable-value-transport-proof";
  native_runtime_claim: false;
  collision_freedom_claim: false;
  authority_effect: "none";
}>;

export const COMPLETE_VALUE_MUTATION_KINDS = Object.freeze([
  "reference-identity",
  "partial-tuple-equality",
  "incongruent-hash",
  "nested-mutation",
  "nested-alias",
  "validator-bypass",
  "tuple-changing-extension",
  "component-protocol-identity-missing",
  "component-protocol-digest-stale",
  "invalid-input-forms-object",
] as const);
export type CompleteValueMutationKind =
  (typeof COMPLETE_VALUE_MUTATION_KINDS)[number];

export const COMPLETE_VALUE_MUTATION_BLUEPRINT = Object.freeze([
  Object.freeze({
    mutation_id: "equality/reference-identity",
    hostile_class: "reference-identity",
    mutation_kind: "reference-identity",
    component_name: null,
  }),
  Object.freeze({
    mutation_id: "equality/partial-currency",
    hostile_class: "partial-tuple-equality",
    mutation_kind: "partial-tuple-equality",
    component_name: "currency",
  }),
  Object.freeze({
    mutation_id: "equality/partial-minor-units",
    hostile_class: "partial-tuple-equality",
    mutation_kind: "partial-tuple-equality",
    component_name: "minor_units",
  }),
  Object.freeze({
    mutation_id: "equality/partial-settlement-account",
    hostile_class: "partial-tuple-equality",
    mutation_kind: "partial-tuple-equality",
    component_name: "settlement_account",
  }),
  Object.freeze({
    mutation_id: "hash/equal-tuple-incongruent",
    hostile_class: "incongruent-hash",
    mutation_kind: "incongruent-hash",
    component_name: null,
  }),
  Object.freeze({
    mutation_id: "nested/mutation",
    hostile_class: "mutable-nested-component",
    mutation_kind: "nested-mutation",
    component_name: "settlement_account",
  }),
  Object.freeze({
    mutation_id: "nested/alias",
    hostile_class: "mutable-nested-component",
    mutation_kind: "nested-alias",
    component_name: "settlement_account",
  }),
  Object.freeze({
    mutation_id: "validators/per-call-bypass",
    hostile_class: "per-call-validator-bypass",
    mutation_kind: "validator-bypass",
    component_name: null,
  }),
  Object.freeze({
    mutation_id: "extension/tuple-change",
    hostile_class: "tuple-changing-extension",
    mutation_kind: "tuple-changing-extension",
    component_name: null,
  }),
  Object.freeze({
    mutation_id: "protocol/missing-identity",
    hostile_class: "component-without-owned-protocol",
    mutation_kind: "component-protocol-identity-missing",
    component_name: "currency",
  }),
  Object.freeze({
    mutation_id: "protocol/stale-digest",
    hostile_class: "component-without-owned-protocol",
    mutation_kind: "component-protocol-digest-stale",
    component_name: "minor_units",
  }),
  Object.freeze({
    mutation_id: "formation/invalid-forms-object",
    hostile_class: "invalid-input-forms-object",
    mutation_kind: "invalid-input-forms-object",
    component_name: null,
  }),
] as const);

export type CompleteValueMutationV1 = Readonly<{
  mutation_id: string;
  hostile_class: CompleteValueHostileClass;
  mutation_kind: CompleteValueMutationKind;
  component_name: string | null;
  expected_finding_codes: readonly CompleteValueFindingCode[];
}>;

export type CompleteValueMutationCatalogueV1 = Readonly<{
  schema_version: "CompleteValueMutationCatalogue/v1";
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  authorship: "independent-family-fixture";
  target_code_may_read_expected_findings: false;
  mutations: readonly CompleteValueMutationV1[];
  authority_effect: "none";
  catalogue_sha256: string;
}>;

export type CompleteValueObservationV1 = ConstructionObservationV1;
