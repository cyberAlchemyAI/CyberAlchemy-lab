import type {
  DeclaredReadLifecycleObservationV1,
  DeclaredReadTargetV1,
  EffectChannelV1,
  LockedEffectObserverRefV1,
} from "../../../kernel/evidence/effect-observation/index.js";

export const READ_MODEL_QUERY_DECISIONS = Object.freeze([
  "exact-declared-read-ledger",
  "exact-closed-result-shape",
  "independent-complete-observation",
  "zero-writes-through-complete-lifecycle",
] as const);

export type ReadModelQueryDecisionId =
  (typeof READ_MODEL_QUERY_DECISIONS)[number];

export type ReadModelScalarV1 = string | number | boolean | null;
export type ReadModelValueKindV1 =
  "string" | "integer" | "boolean" | "nullable-string";

export type ReadModelQueryCaseV1 = Readonly<{
  case_id: string;
  inputs: Readonly<Record<string, ReadModelScalarV1>>;
  expected_result: Readonly<Record<string, ReadModelScalarV1>>;
}>;

export type ReadModelQueryDefinitionV1 = Readonly<{
  schema_version: "ReadModelQueryDefinition/v1";
  definition_id: string;
  status: "candidate-fixture";
  authorship: "owner-authored-admission-input";
  derivation_policy:
    "implementation-and-generated-results-forbidden-as-authority";
  descriptor_ref: Readonly<{
    descriptor_id: string;
    path: string;
    sha256: string;
  }>;
  input_concepts: readonly Readonly<{
    name: string;
    concept_id: string;
    value_kind: "string" | "integer";
    required: true;
  }>[];
  read_targets: readonly Readonly<DeclaredReadTargetV1 & {
    concept_id: string;
  }>[];
  output_concept: Readonly<{
    concept_id: string;
    fields: readonly Readonly<{
      name: string;
      value_kind: ReadModelValueKindV1;
      required: true;
    }>[];
    additional_fields: false;
  }>;
  declared_failures: readonly string[];
  cases: readonly ReadModelQueryCaseV1[];
  authority_effect: "none";
}>;

export type ReadModelQueryDenominatorV1 = Readonly<{
  schema_version: "ReadModelQueryDenominator/v1";
  denominator_id: string;
  owner_definition_ref: Readonly<{
    definition_id: string;
    path: string;
    sha256: string;
  }>;
  portable_contract: Readonly<{
    return_semantics: "exact-owner-authored-read-model";
    dependency_contract: "exact-ordered-declared-read-targets-only";
    effect_contract: "declared-reads-and-zero-observed-writes";
    result_consumption: "complete-through-supported-lifecycle";
    lifecycle_paths: "return-await-cancel-close-dispose-finalizer-quiescence";
    unsupported_coverage: "fail-closed";
    observer_origin: "locked-harness-owned-not-provider";
  }>;
  positive_decisions: readonly ReadModelQueryDecisionId[];
  authority_effect: "none";
  denominator_sha256: string;
}>;

export type ReadModelQueryObservedResultV1 = Readonly<{
  case_id: string;
  input_sha256: string;
  result: Readonly<Record<string, ReadModelScalarV1>>;
  result_sha256: string;
  declared_failure: string | null;
}>;

export type ReadModelQueryObservationV1 = Readonly<{
  schema_version: "ReadModelQueryObservation/v1";
  observation_id: string;
  source_kind:
    "independent-family-fixture" | "target-observation" |
    "mutated-family-observation";
  target: Readonly<{
    target_id: string;
    target_sha256: string;
    language: "family-fixture" | "typescript" | "python" | "rust";
    protocol_id: string;
  }>;
  definition_ref: ReadModelQueryDenominatorV1["owner_definition_ref"];
  binding: Readonly<{
    descriptor_id: string;
    descriptor_sha256: string;
    provider_id: string;
    provider_sha256: string;
  }>;
  observed_result: ReadModelQueryObservedResultV1;
  read_lifecycle_observation: DeclaredReadLifecycleObservationV1;
  authority_effect: "none";
  observation_sha256: string;
}>;

export type ReadModelQueryFindingCode =
  | "FAMILY_QUERY_TARGET_OBSERVATION_MISSING"
  | "FAMILY_QUERY_DEFINITION_PROVENANCE_MISMATCH"
  | "FAMILY_QUERY_BINDING_MISMATCH"
  | "FAMILY_QUERY_READ_LEDGER_MISMATCH"
  | "FAMILY_QUERY_RESULT_SHAPE_MISMATCH"
  | "FAMILY_QUERY_DECLARED_FAILURE_MISMATCH"
  | "FAMILY_QUERY_OBSERVER_NOT_INDEPENDENT"
  | "FAMILY_QUERY_OBSERVATION_COVERAGE_UNSUPPORTED"
  | "FAMILY_QUERY_WRITE_OBSERVED"
  | "FAMILY_QUERY_WRITE_RESTORE_OBSERVED"
  | "FAMILY_QUERY_DEFERRED_WRITE_OBSERVED"
  | "FAMILY_QUERY_RESULT_CONSUMPTION_INCOMPLETE"
  | "FAMILY_QUERY_SOURCE_UNSUPPORTED";

export type ReadModelQueryFindingV1 = Readonly<{
  code: ReadModelQueryFindingCode;
  decision_id: ReadModelQueryDecisionId;
  expected: string | null;
  observed: string | null;
}>;

export type ReadModelQueryEvaluationV1 = Readonly<{
  schema_version: "ReadModelQueryEvaluation/v1";
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
  findings: readonly ReadModelQueryFindingV1[];
  positive_decision_accounting: Readonly<{
    declared: 4;
    passed: number;
    failed: number;
    unaccounted: 0;
  }>;
  portable_claim:
    "owner-bound-exact-read-model-under-declared-observed-lifecycle";
  authority_effect: "none";
}>;

export const READ_MODEL_QUERY_MUTATION_KINDS = Object.freeze([
  "hidden-write",
  "write-then-restore",
  "deferred-lazy-write",
  "undeclared-read",
  "undeclared-result-shape",
  "missing-observation-coverage",
  "unsupported-source",
] as const);

export type ReadModelQueryMutationKind =
  (typeof READ_MODEL_QUERY_MUTATION_KINDS)[number];

export type ReadModelQueryMutationVariant =
  | "default" | "cancel" | "close" | "dispose" | "finalizer" |
  "quiescence";

export type ReadModelQueryMutationV1 = Readonly<{
  mutation_id: string;
  mutation_kind: ReadModelQueryMutationKind;
  variants: readonly ReadModelQueryMutationVariant[];
  expected_finding_codes: readonly ReadModelQueryFindingCode[];
}>;

export type ReadModelQueryMutationCatalogueV1 = Readonly<{
  schema_version: "ReadModelQueryMutationCatalogue/v1";
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  authorship: "independent-family-fixture";
  target_code_may_read_expected_findings: false;
  mutations: readonly ReadModelQueryMutationV1[];
  authority_effect: "none";
  catalogue_sha256: string;
}>;

export type ReadModelQueryEvaluationInputV1 = Readonly<{
  definition: ReadModelQueryDefinitionV1;
  denominator: ReadModelQueryDenominatorV1;
  observation: ReadModelQueryObservationV1 | null;
  locked_observer_ref: LockedEffectObserverRefV1;
  locked_target_ref: Readonly<{target_id: string; target_sha256: string}>;
}>;

export type ReadModelQueryReadTargetV1 = Readonly<{
  target_id: string;
  concept_id: string;
  channel: EffectChannelV1;
}>;
