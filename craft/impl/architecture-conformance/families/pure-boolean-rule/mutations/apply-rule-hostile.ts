import type {
  PureBooleanRuleProfileV1,
  RuleHostileFixtureV1,
} from "../contracts/pure-boolean-rule-contracts.js";

const fail = (code: string): never => {
  throw Object.assign(new Error(code), {code});
};
export const applyRuleHostile = (
  profile: PureBooleanRuleProfileV1,
  fixture: RuleHostileFixtureV1,
): PureBooleanRuleProfileV1 => {
  const mutation = fixture.mutation;
  switch (mutation.path) {
    case "output_type":
      return Object.freeze({...profile, output_type: mutation.value}) as
        PureBooleanRuleProfileV1;
    case "state_mutation_count":
      return Object.freeze({...profile, state_mutation_count: mutation.value}) as
        PureBooleanRuleProfileV1;
    case "external_effects":
      return Object.freeze({...profile, external_effects: mutation.value}) as
        PureBooleanRuleProfileV1;
    case "enforces_edges":
      return Object.freeze({...profile, enforces_edges: mutation.value}) as
        PureBooleanRuleProfileV1;
    case "inverse_enforces_edge":
      return Object.freeze({...profile, enforces_edges: Object.freeze([
        Object.freeze({
          source_type: "architecture.OperationImplementation" as const,
          target_type: "architecture.RuleImplementation" as const,
        }),
      ])});
    case "observed_dependencies":
      return Object.freeze({...profile, observed_dependencies: mutation.value}) as
        PureBooleanRuleProfileV1;
    case "operation_invocation_count":
      return Object.freeze({...profile, operation_invocation_count: mutation.value}) as
        PureBooleanRuleProfileV1;
    case "evaluation_order":
      return Object.freeze({...profile, evaluation_order: mutation.value}) as
        PureBooleanRuleProfileV1;
    case "stable_input_binding":
      return Object.freeze({...profile, stable_input_binding: mutation.value}) as
        PureBooleanRuleProfileV1;
    case "exception_policy":
      return Object.freeze({...profile, exception_policy: mutation.value}) as
        PureBooleanRuleProfileV1;
    case "relation_evidence.owner_status":
      return Object.freeze({...profile, relation_evidence: Object.freeze({
        ...profile.relation_evidence,
        owner_status: mutation.value,
      })}) as PureBooleanRuleProfileV1;
    case "relation_evidence.observed_source_type":
      return Object.freeze({...profile, relation_evidence: Object.freeze({
        ...profile.relation_evidence,
        observed_source_type: mutation.value,
      })}) as PureBooleanRuleProfileV1;
    case "relation_evidence.observed_target_type":
      return Object.freeze({...profile, relation_evidence: Object.freeze({
        ...profile.relation_evidence,
        observed_target_type: mutation.value,
      })}) as PureBooleanRuleProfileV1;
    case "relation_evidence.assertion_present":
      return Object.freeze({...profile, relation_evidence: Object.freeze({
        ...profile.relation_evidence,
        assertion_present: mutation.value,
      })}) as PureBooleanRuleProfileV1;
    default:
      return fail("RMT_RULE_HOSTILE_MUTATION_UNKNOWN");
  }
};
