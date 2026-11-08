import type {
  StrategyMembershipEvaluationInputV1,
  StrategyMembershipMutationV1,
} from "../contracts/strategy-selection-contracts.js";

export const applyStrategyMembershipMutant = (
  input: StrategyMembershipEvaluationInputV1,
  mutation: StrategyMembershipMutationV1,
): StrategyMembershipEvaluationInputV1 => {
  const mutated = structuredClone(input) as any;
  switch (mutation.mutation_kind) {
    case "empty-set":
      mutated.catalogue.members = [];
      break;
    case "duplicate-strategy-id":
      mutated.catalogue.members[1].strategy_id = mutated.catalogue.members[0].strategy_id;
      break;
    case "unknown-strategy":
      mutated.observation.strategy_id = "settlement.route.unknown";
      break;
    case "foreign-catalogue":
      mutated.observation.catalogue_ref.catalogue_id = "strategy-catalogue.foreign/v1";
      break;
    case "stable-id-content-drift":
      mutated.catalogue.members[0].purpose = `${mutated.catalogue.members[0].purpose} drift`;
      break;
    case "implementation-owned-catalogue":
      mutated.catalogue.authorship = "implementation-observed";
      break;
    case "executable-member":
      mutated.catalogue.members[0].executable = true;
      break;
    case "stale-descriptor-digest":
      mutated.catalogue.descriptor_ref.sha256 = "not-a-sha256";
      break;
    case "stale-denominator-digest":
      mutated.denominator.denominator_sha256 = "0".repeat(64);
      break;
    case "missing-current-membership":
      mutated.observation.membership = "missing";
      break;
  }
  return mutated as StrategyMembershipEvaluationInputV1;
};
