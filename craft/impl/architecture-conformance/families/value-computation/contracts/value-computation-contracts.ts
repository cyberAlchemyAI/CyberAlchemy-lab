import type {
  EffectObservationV1,
} from "../../../kernel/evidence/effect-observation/index.js";

export const VALUE_COMPUTATION_DECISIONS = Object.freeze([
  "target-observation-present",
  "owner-definition-provenance",
  "exact-descriptor-provider-binding",
  "exact-case-value",
  "non-boolean-value",
  "fresh-process-determinism",
  "independent-observer-binding",
  "complete-effect-perimeter",
  "zero-forbidden-effects",
  "complete-result-consumption",
  "quiescence-after-consumption",
] as const);

export type ValueComputationDecisionId =
  (typeof VALUE_COMPUTATION_DECISIONS)[number];

export type CalculationValueV1 = string | number | null;

export type ValueComputationCaseV1 = Readonly<{
  case_id: string;
  inputs: Readonly<Record<string, CalculationValueV1>>;
  expected_value: CalculationValueV1;
}>;

export type ValueComputationDefinitionV1 = Readonly<{
  schema_version: "ValueComputationDefinition/v1";
  definition_id: string;
  status: "candidate-fixture";
  authorship: "owner-authored-admission-input";
  derivation_policy: "implementation-and-generated-results-forbidden-as-authority";
  descriptor_ref: Readonly<{
    descriptor_id: string;
    path: string;
    sha256: string;
  }>;
  input_concepts: readonly Readonly<{
    name: string;
    concept_id: string;
    value_kind: "integer" | "string";
  }>[];
  output_concept: Readonly<{
    concept_id: string;
    value_kind: "integer" | "string";
    boolean_forbidden: true;
  }>;
  cases: readonly ValueComputationCaseV1[];
  authority_effect: "none";
}>;

export type ValueComputationDenominatorV1 = Readonly<{
  schema_version: "ValueComputationDenominator/v1";
  denominator_id: string;
  owner_definition_ref: Readonly<{
    definition_id: string;
    path: string;
    sha256: string;
  }>;
  portable_contract: Readonly<{
    return_semantics: "declared-non-boolean-value";
    dependency_contract: "explicit-only";
    effect_contract: "zero-observed-forbidden-effects";
    determinism: "equal-results-across-two-fresh-processes";
    result_consumption: "complete-before-close";
    quiescence: "required-after-consumption";
    observer_origin: "locked-harness-owned-not-provider";
  }>;
  positive_decisions: readonly ValueComputationDecisionId[];
  authority_effect: "none";
  denominator_sha256: string;
}>;

export type ValueComputationObservedCaseV1 = Readonly<{
  case_id: string;
  input_sha256: string;
  result_kind: "number" | "string" | "null" | "boolean";
  result_value: CalculationValueV1 | boolean;
  result_sha256: string;
  fresh_process_result_sha256: string;
  process_isolation: "separate-process" | "same-process";
}>;

export type ValueComputationObservationV1 = Readonly<{
  schema_version: "ValueComputationObservation/v1";
  observation_id: string;
  source_kind: "independent-family-fixture" | "target-observation" | "mutated-family-observation";
  target: Readonly<{
    target_id: string;
    language: "family-fixture" | "typescript" | "python" | "rust";
    protocol_id: string;
  }>;
  definition_ref: ValueComputationDenominatorV1["owner_definition_ref"];
  binding: Readonly<{
    descriptor_id: string;
    descriptor_sha256: string;
    provider_id: string;
    provider_sha256: string;
  }>;
  cases: readonly ValueComputationObservedCaseV1[];
  effect_observation: EffectObservationV1;
  authority_effect: "none";
  observation_sha256: string;
}>;

export type ValueComputationFindingCode =
  | "FAMILY_CALC_TARGET_OBSERVATION_MISSING"
  | "FAMILY_CALC_DEFINITION_PROVENANCE_MISMATCH"
  | "FAMILY_CALC_BINDING_MISMATCH"
  | "FAMILY_CALC_CASE_MISSING"
  | "FAMILY_CALC_CASE_UNEXPECTED"
  | "FAMILY_CALC_VALUE_MISMATCH"
  | "FAMILY_CALC_BOOLEAN_VALUE"
  | "FAMILY_CALC_NONDETERMINISTIC"
  | "FAMILY_CALC_OBSERVER_NOT_INDEPENDENT"
  | "FAMILY_CALC_EFFECT_CHANNEL_UNSUPPORTED"
  | "FAMILY_CALC_AMBIENT_READ_OBSERVED"
  | "FAMILY_CALC_EFFECT_WRITE_OBSERVED"
  | "FAMILY_CALC_DEFERRED_OR_ESCAPE_OBSERVED"
  | "FAMILY_CALC_RESULT_INCOMPLETE"
  | "FAMILY_CALC_MUTABLE_OUTPUT_OBSERVED"
  | "FAMILY_CALC_QUIESCENCE_VIOLATION";

export type ValueComputationFindingV1 = Readonly<{
  code: ValueComputationFindingCode;
  decision_id: ValueComputationDecisionId;
  case_id: string | null;
  expected: string | null;
  observed: string | null;
}>;

export type ValueComputationEvaluationV1 = Readonly<{
  schema_version: "ValueComputationEvaluation/v1";
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
  findings: readonly ValueComputationFindingV1[];
  positive_decision_accounting: Readonly<{
    declared: number;
    passed: number;
    failed: number;
    unaccounted: 0;
  }>;
  portable_claim: "owner-bound-deterministic-zero-effect-value-under-declared-perimeter";
  authority_effect: "none";
}>;

export const VALUE_COMPUTATION_MUTATION_KINDS = Object.freeze([
  "boolean-output",
  "wrong-value",
  "same-process-repeat",
  "nondeterministic-repeat",
  "self-issued-observer",
  "unsupported-effect-channel",
  "ambient-read",
  "state-write",
  "incomplete-result",
  "delayed-effect",
  "non-quiescent",
  "mutable-output",
  "stale-binding",
] as const);

export type ValueComputationMutationKind =
  (typeof VALUE_COMPUTATION_MUTATION_KINDS)[number];

export type ValueComputationMutationV1 = Readonly<{
  mutation_id: string;
  mutation_kind: ValueComputationMutationKind;
  expected_finding_codes: readonly ValueComputationFindingCode[];
}>;

export type ValueComputationMutationCatalogueV1 = Readonly<{
  schema_version: "ValueComputationMutationCatalogue/v1";
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  authorship: "independent-family-fixture";
  target_code_may_read_expected_findings: false;
  mutations: readonly ValueComputationMutationV1[];
  authority_effect: "none";
  catalogue_sha256: string;
}>;
