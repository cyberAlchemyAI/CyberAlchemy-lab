export type RuleInputValue = string | number | boolean | null;

export type RuleDefinitionV1 = Readonly<{
  schema_version: "RuleDefinition/v1";
  rule_id: string;
  concept_id: string;
  input_fields: readonly Readonly<{
    name: string;
    value_type: "string" | "number" | "boolean" | "nullable-string";
  }>[];
  output_type: "boolean";
  determinism: "required";
  effects: "forbidden";
  definition_sha256: string;
  authority_ref: string;
  authority_status: "candidate-fixture" | "owner-issued";
  authority_effect: "none";
}>;

export type RuleBindingV1 = Readonly<{
  schema_version: "RuleBinding/v1";
  binding_id: string;
  rule_ref: Readonly<{
    rule_id: string;
    definition_sha256: string;
  }>;
  target_id: "typescript" | "python" | "rust";
  realization_id: string;
  source_ref: Readonly<{
    path: string;
    sha256: string;
    origin: "handwritten-candidate-fixture";
  }>;
  symbol_name: string;
  current: boolean;
  binding_sha256: string;
  authority_effect: "none";
}>;

export type RuleCaseV1 = Readonly<{
  case_id: string;
  input: Readonly<Record<string, RuleInputValue>>;
  expected_outcome: boolean;
}>;

export type RuleCaseCatalogueV1 = Readonly<{
  schema_version: "RuleCaseCatalogue/v1";
  rule_ref: Readonly<{ rule_id: string; definition_sha256: string }>;
  cases: readonly RuleCaseV1[];
  catalogue_sha256: string;
  owner_ref: "rule-case-owner";
  authority_effect: "none";
}>;

export type RuleObligationCode =
  | "RULE_BINDING_MISSING"
  | "RULE_BINDING_STALE"
  | "RULE_OUTCOME_MISSING"
  | "RULE_OUTCOME_MISMATCH"
  | "RULE_OUTCOME_NON_BOOLEAN"
  | "RULE_OUTCOME_DUPLICATE"
  | "RULE_OUTCOME_UNEXPECTED"
  | "RULE_EFFECT_OBSERVED"
  | "RULE_OBSERVATION_UNSUPPORTED";

export type RuleObligationCatalogueV1 = Readonly<{
  schema_version: "RuleObligationCatalogue/v1";
  rule_ref: Readonly<{ rule_id: string; definition_sha256: string }>;
  case_catalogue_sha256: string;
  obligations: readonly Readonly<{
    obligation_id: string;
    kind: "binding-current" | "case-outcome-exact" | "effect-free";
    case_id: string | null;
    expected_outcome: boolean | null;
    failure_code: RuleObligationCode;
  }>[];
  catalogue_sha256: string;
  owner_ref: "rule-obligation-owner";
  authority_effect: "none";
}>;

export type RuleSemanticMutantV1 = Readonly<{
  mutation_id: string;
  defect: "wrong-result" | "bypass-check" | "observable-effect";
  case_id: string;
  expected_finding_code: RuleObligationCode;
}>;

export type RuleMutationCatalogueV1 = Readonly<{
  schema_version: "RuleMutationCatalogue/v1";
  rule_ref: Readonly<{ rule_id: string; definition_sha256: string }>;
  mutations: readonly RuleSemanticMutantV1[];
  catalogue_sha256: string;
  owner_ref: "rule-mutation-owner";
  authority_effect: "none";
}>;

export type RuleCaseObservationV1 = Readonly<{
  case_id: string;
  outcome: boolean | string | number | null;
  observed_effect_count: number;
}>;

export type RuleObservationV1 = Readonly<{
  schema_version: "RuleObservation/v1";
  binding_id: string | null;
  source_sha256: string | null;
  symbol_name: string | null;
  case_observations: readonly RuleCaseObservationV1[];
  unsupported: readonly string[];
  observation_sha256: string;
  authority_effect: "none";
}>;

export type RuleEvaluationV1 = Readonly<{
  schema_version: "RuleEvaluation/v1";
  evaluation_id: string;
  verdict: "pass" | "fail";
  findings: readonly Readonly<{
    code: RuleObligationCode;
    case_id: string | null;
    expected: boolean | null;
    observed: boolean | string | number | null;
  }>[];
  authority_effect: "none";
}>;
