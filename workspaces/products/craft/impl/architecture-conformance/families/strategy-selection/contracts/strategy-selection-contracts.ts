export const STRATEGY_MEMBERSHIP_DECISIONS = Object.freeze([
  "owner-catalogue-provenance",
  "non-empty-strategy-set",
  "unique-stable-strategy-identities",
  "data-only-strategy-members",
  "exact-content-addressed-set",
  "current-catalogue-binding",
  "exact-current-membership",
  "membership-not-selection-or-execution",
] as const);

export type StrategyMembershipDecisionId =
  (typeof STRATEGY_MEMBERSHIP_DECISIONS)[number];

export type StrategyMemberV1 = Readonly<{
  strategy_id: string;
  purpose: string;
  eligibility_facts: readonly string[];
  executable: false;
}>;

export type StrategyCatalogueV1 = Readonly<{
  schema_version: "StrategyCatalogue/v1";
  catalogue_id: string;
  catalogue_status: "candidate-fixture";
  authorship: "owner-authored-admission-input";
  derivation_policy: "implementation-and-generated-members-forbidden-as-authority";
  descriptor_ref: Readonly<{
    descriptor_id: string;
    path: string;
    sha256: string;
  }>;
  set_id: string;
  members: readonly StrategyMemberV1[];
  member_order_semantics: "none";
  membership_contract: Readonly<{
    identity: "stable-strategy-id";
    set: "closed-current-content-addressed";
    member_authority: "data-only-no-callable-authority";
    selection: "not-proven-by-membership";
    execution: "not-proven-by-membership";
  }>;
  authority_effect: "none";
  catalogue_sha256: string;
}>;

export type StrategyMembershipDenominatorV1 = Readonly<{
  schema_version: "StrategyMembershipDenominator/v1";
  denominator_id: string;
  owner_catalogue_ref: Readonly<{
    catalogue_id: string;
    path: string;
    sha256: string;
    catalogue_sha256: string;
  }>;
  portable_contract: Readonly<{
    membership: "exact-current-set-membership";
    strategy_identity: "stable-data-only-id";
    selection_claim: "none";
    execution_claim: "none";
  }>;
  positive_decisions: readonly StrategyMembershipDecisionId[];
  authority_effect: "none";
  denominator_sha256: string;
}>;

export type StrategyMembershipObservationV1 = Readonly<{
  schema_version: "StrategyMembershipObservation/v1";
  observation_id: string;
  source_kind: "independent-owner-membership" | "mutated-family-observation";
  catalogue_ref: Readonly<{
    catalogue_id: string;
    catalogue_sha256: string;
  }>;
  strategy_id: string;
  membership: "member" | "missing";
  selection_claim: "none" | "selected";
  execution_claim: "none" | "executable";
  authority_effect: "none";
  observation_sha256: string;
}>;

export type StrategyMembershipFindingCode =
  | "FAMILY_POLICY_CATALOGUE_PROVENANCE_INVALID"
  | "FAMILY_POLICY_STRATEGY_SET_EMPTY"
  | "FAMILY_POLICY_STRATEGY_ID_DUPLICATE"
  | "FAMILY_POLICY_EXECUTABLE_MEMBER_FORBIDDEN"
  | "FAMILY_POLICY_STRATEGY_SET_DIGEST_STALE"
  | "FAMILY_POLICY_DESCRIPTOR_BINDING_STALE"
  | "FAMILY_POLICY_DENOMINATOR_BINDING_STALE"
  | "FAMILY_POLICY_FOREIGN_CATALOGUE"
  | "FAMILY_POLICY_UNKNOWN_STRATEGY"
  | "FAMILY_POLICY_CURRENT_MEMBERSHIP_MISSING"
  | "FAMILY_POLICY_MEMBERSHIP_COLLAPSE";

export type StrategyMembershipFindingV1 = Readonly<{
  code: StrategyMembershipFindingCode;
  decision_id: StrategyMembershipDecisionId;
  expected: string | null;
  observed: string | null;
}>;

export type StrategyMembershipEvaluationV1 = Readonly<{
  schema_version: "StrategyMembershipEvaluation/v1";
  evaluation_id: string;
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  observation_ref: Readonly<{
    observation_id: string;
    observation_sha256: string;
  }>;
  verdict: "pass" | "fail";
  findings: readonly StrategyMembershipFindingV1[];
  positive_decision_accounting: Readonly<{
    declared: number;
    passed: number;
    failed: number;
    unaccounted: 0;
  }>;
  portable_claim: "owner-bound-current-data-only-strategy-membership";
  authority_effect: "none";
}>;

export const STRATEGY_MEMBERSHIP_MUTATION_KINDS = Object.freeze([
  "empty-set",
  "duplicate-strategy-id",
  "unknown-strategy",
  "foreign-catalogue",
  "stable-id-content-drift",
  "implementation-owned-catalogue",
  "executable-member",
  "stale-descriptor-digest",
  "stale-denominator-digest",
  "missing-current-membership",
] as const);

export type StrategyMembershipMutationKind =
  (typeof STRATEGY_MEMBERSHIP_MUTATION_KINDS)[number];

export type StrategyMembershipMutationV1 = Readonly<{
  mutation_id: string;
  mutation_kind: StrategyMembershipMutationKind;
  expected_finding_codes: readonly StrategyMembershipFindingCode[];
}>;

export type StrategyMembershipMutationCatalogueV1 = Readonly<{
  schema_version: "StrategyMembershipMutationCatalogue/v1";
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  authorship: "independent-family-fixture";
  target_code_may_read_expected_findings: false;
  mutations: readonly StrategyMembershipMutationV1[];
  authority_effect: "none";
  catalogue_sha256: string;
}>;

export type StrategyMembershipEvaluationInputV1 = Readonly<{
  catalogue: StrategyCatalogueV1;
  denominator: StrategyMembershipDenominatorV1;
  observation: StrategyMembershipObservationV1;
}>;

export const STRATEGY_SELECTION_DECISIONS = Object.freeze([
  "owner-selector-definition-provenance",
  "exact-current-catalogue-binding",
  "explicit-input-facts-only",
  "complete-owner-case-coverage",
  "input-sensitive-branch-selection",
  "strategy-identity-not-boolean",
  "owner-declared-strategy-identity",
  "independent-effect-observer-binding",
  "complete-effect-perimeter",
  "zero-forbidden-effects",
  "complete-result-consumption",
  "quiescence-after-selection",
  "independent-strategy-execution-trap",
  "zero-selected-strategy-execution",
] as const);

export type StrategySelectionDecisionId =
  (typeof STRATEGY_SELECTION_DECISIONS)[number];

export type StrategySelectionInputValueV1 = string | number | boolean | null;

export type StrategySelectionCaseV1 = Readonly<{
  case_id: string;
  inputs: Readonly<Record<string, StrategySelectionInputValueV1>>;
  expected_strategy_id: string;
  expected_branch_id: string;
}>;

export type StrategySelectionDefinitionV1 = Readonly<{
  schema_version: "StrategySelectionDefinition/v1";
  definition_id: string;
  status: "candidate-fixture";
  authorship: "owner-authored-admission-input";
  derivation_policy: "implementation-and-generated-selections-forbidden-as-authority";
  descriptor_ref: Readonly<{
    descriptor_id: string;
    path: string;
    sha256: string;
  }>;
  catalogue_ref: Readonly<{
    catalogue_id: string;
    path: string;
    sha256: string;
    catalogue_sha256: string;
  }>;
  input_facts: readonly Readonly<{
    name: string;
    value_kind: "integer" | "boolean" | "string";
    required: true;
  }>[];
  branch_contract: Readonly<{
    return_semantics: "one-current-strategy-identity";
    dependency_contract: "explicit-inputs-only";
    boolean_forbidden: true;
    selected_strategy_execution: "forbidden-during-selection";
  }>;
  cases: readonly StrategySelectionCaseV1[];
  sensitivity_pairs: readonly Readonly<{
    left_case_id: string;
    right_case_id: string;
    changed_input_fact: string;
  }>[];
  authority_effect: "none";
  definition_sha256: string;
}>;

export type StrategySelectionDenominatorV1 = Readonly<{
  schema_version: "StrategySelectionDenominator/v1";
  denominator_id: string;
  owner_definition_ref: Readonly<{
    definition_id: string;
    path: string;
    sha256: string;
    definition_sha256: string;
  }>;
  owner_catalogue_ref: StrategySelectionDefinitionV1["catalogue_ref"];
  portable_contract: Readonly<{
    return_semantics: "current-strategy-identity";
    dependency_contract: "explicit-inputs-only";
    effect_contract: "zero-observed-forbidden-effects";
    strategy_execution: "zero-attempts-during-selection";
    result_consumption: "complete-before-close";
    quiescence: "required-after-selection";
    observer_origin: "locked-harness-owned-not-provider";
  }>;
  positive_decisions: readonly StrategySelectionDecisionId[];
  authority_effect: "none";
  denominator_sha256: string;
}>;

export type StrategySelectionObservedCaseV1 = Readonly<{
  case_id: string;
  input_sha256: string;
  selected_kind: "strategy-id" | "boolean";
  selected_strategy_id: string | boolean;
  selected_sha256: string;
  branch_id: string;
  consumed_input_facts: readonly string[];
}>;

export type LockedStrategyExecutionObserverRefV1 = Readonly<{
  role: "independent-strategy-execution-observer";
  observer_id: string;
  observer_sha256: string;
  owner_ref: string;
  provider_id: string;
  provider_sha256: string;
}>;

export type LockedStrategySelectorTargetRefV1 = Readonly<{
  target_id: string;
  target_sha256: string;
}>;

export type StrategyExecutionObservationV1 = Readonly<{
  schema_version: "StrategyExecutionObservation/v1";
  observation_id: string;
  source_kind: "independent-owner-trap" | "mutated-strategy-execution-trap";
  observer_ref: LockedStrategyExecutionObserverRefV1;
  target_ref: LockedStrategySelectorTargetRefV1;
  catalogue_ref: Readonly<{
    catalogue_id: string;
    catalogue_sha256: string;
  }>;
  coverage: "all-owner-declared-strategies" | "partial";
  covered_strategy_ids: readonly string[];
  attempt_count: number;
  attempted_strategy_ids: readonly string[];
  completion_count: number;
  authority_effect: "none";
  observation_sha256: string;
}>;

export type StrategySelectionObservationV1 = Readonly<{
  schema_version: "StrategySelectionObservation/v1";
  observation_id: string;
  source_kind: "independent-family-fixture" | "target-observation" |
  "mutated-family-observation";
  target: Readonly<{
    target_id: string;
    target_sha256: string;
    language: "family-fixture" | "typescript" | "python" | "rust";
    protocol_id: string;
  }>;
  definition_ref: StrategySelectionDenominatorV1["owner_definition_ref"];
  catalogue_ref: Readonly<{
    catalogue_id: string;
    catalogue_sha256: string;
  }>;
  binding: Readonly<{
    descriptor_id: string;
    descriptor_sha256: string;
    provider_id: string;
    provider_sha256: string;
  }>;
  cases: readonly StrategySelectionObservedCaseV1[];
  effect_observation: EffectObservationV1;
  strategy_execution_observation: StrategyExecutionObservationV1;
  authority_effect: "none";
  observation_sha256: string;
}>;

export type StrategySelectionFindingCode =
  | "FAMILY_POLICY_SELECTOR_DEFINITION_PROVENANCE_INVALID"
  | "FAMILY_POLICY_SELECTOR_DEFINITION_BINDING_STALE"
  | "FAMILY_POLICY_SELECTOR_CATALOGUE_BINDING_STALE"
  | "FAMILY_POLICY_SELECTOR_INPUT_CONTRACT_INVALID"
  | "FAMILY_POLICY_SELECTOR_CASE_MISSING"
  | "FAMILY_POLICY_SELECTOR_CASE_UNEXPECTED"
  | "FAMILY_POLICY_SELECTOR_INPUT_MISMATCH"
  | "FAMILY_POLICY_SELECTOR_BRANCH_MISMATCH"
  | "FAMILY_POLICY_SELECTOR_INPUT_IGNORED"
  | "FAMILY_POLICY_SELECTOR_BOOLEAN_COLLAPSE"
  | "FAMILY_POLICY_SELECTOR_UNKNOWN_STRATEGY"
  | "FAMILY_POLICY_SELECTOR_OBSERVER_NOT_INDEPENDENT"
  | "FAMILY_POLICY_SELECTOR_EFFECT_PERIMETER_INCOMPLETE"
  | "FAMILY_POLICY_SELECTOR_AMBIENT_READ_OBSERVED"
  | "FAMILY_POLICY_SELECTOR_EFFECT_WRITE_OBSERVED"
  | "FAMILY_POLICY_SELECTOR_DEFERRED_OR_ESCAPE_OBSERVED"
  | "FAMILY_POLICY_SELECTOR_RESULT_INCOMPLETE"
  | "FAMILY_POLICY_SELECTOR_MUTABLE_OUTPUT_OBSERVED"
  | "FAMILY_POLICY_SELECTOR_QUIESCENCE_VIOLATION"
  | "FAMILY_POLICY_SELECTOR_EXECUTION_TRAP_NOT_INDEPENDENT"
  | "FAMILY_POLICY_SELECTOR_EXECUTION_TRAP_INCOMPLETE"
  | "FAMILY_POLICY_SELECTOR_STRATEGY_EXECUTION_OBSERVED";

export type StrategySelectionFindingV1 = Readonly<{
  code: StrategySelectionFindingCode;
  decision_id: StrategySelectionDecisionId;
  case_id: string | null;
  expected: string | null;
  observed: string | null;
}>;

export type StrategySelectionEvaluationV1 = Readonly<{
  schema_version: "StrategySelectionEvaluation/v1";
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
  findings: readonly StrategySelectionFindingV1[];
  positive_decision_accounting: Readonly<{
    declared: number;
    passed: number;
    failed: number;
    unaccounted: 0;
  }>;
  portable_claim: "owner-bound-input-sensitive-zero-effect-strategy-identity-selection-without-strategy-execution";
  authority_effect: "none";
}>;

export const STRATEGY_SELECTION_MUTATION_KINDS = Object.freeze([
  "boolean-return",
  "unknown-strategy",
  "foreign-catalogue",
  "ignored-selection-input",
  "missing-case",
  "self-issued-effect-observer",
  "unsupported-effect-channel",
  "ambient-read",
  "state-write",
  "delayed-effect",
  "incomplete-result",
  "non-quiescent",
  "self-issued-execution-trap",
  "partial-execution-trap",
  "strategy-execution-attempt",
  "stale-definition-binding",
] as const);

export type StrategySelectionMutationKind =
  (typeof STRATEGY_SELECTION_MUTATION_KINDS)[number];

export type StrategySelectionMutationV1 = Readonly<{
  mutation_id: string;
  mutation_kind: StrategySelectionMutationKind;
  expected_finding_codes: readonly StrategySelectionFindingCode[];
}>;

export type StrategySelectionMutationCatalogueV1 = Readonly<{
  schema_version: "StrategySelectionMutationCatalogue/v1";
  denominator_ref: Readonly<{
    denominator_id: string;
    denominator_sha256: string;
  }>;
  authorship: "independent-family-fixture";
  target_code_may_read_expected_findings: false;
  mutations: readonly StrategySelectionMutationV1[];
  authority_effect: "none";
  catalogue_sha256: string;
}>;

export type StrategySelectionEvaluationInputV1 = Readonly<{
  catalogue: StrategyCatalogueV1;
  definition: StrategySelectionDefinitionV1;
  denominator: StrategySelectionDenominatorV1;
  observation: StrategySelectionObservationV1 | null;
  locked_effect_observer_ref: LockedEffectObserverRefV1;
  locked_execution_observer_ref: LockedStrategyExecutionObserverRefV1;
  locked_selector_target_ref: LockedStrategySelectorTargetRefV1;
}>;
import type {
  EffectObservationV1,
  LockedEffectObserverRefV1,
} from "../../../kernel/evidence/effect-observation/index.js";
