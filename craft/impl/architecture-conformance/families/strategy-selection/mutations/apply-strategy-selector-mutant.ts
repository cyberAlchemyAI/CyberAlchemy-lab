import {
  EFFECT_CHANNELS,
  mintEffectObservationV1,
  type EffectObservationV1,
} from "../../../kernel/evidence/effect-observation/index.js";
import type {
  StrategyExecutionObservationV1,
  StrategySelectionMutationV1,
  StrategySelectionObservationV1,
} from "../contracts/strategy-selection-contracts.js";
import {
  mintStrategyExecutionObservationV1,
  mintStrategySelectionObservationV1,
  sha256SelectedStrategyIdentity,
} from "../providers/decode-strategy-selector.js";

const digest = (character: string): string => character.repeat(64).slice(0, 64);
const withoutEffectDigest = (
  value: EffectObservationV1,
): Omit<EffectObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = value;
  return body;
};
const withoutExecutionDigest = (
  value: StrategyExecutionObservationV1,
): Omit<StrategyExecutionObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = value;
  return body;
};
const withoutObservationDigest = (
  value: StrategySelectionObservationV1,
): Omit<StrategySelectionObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = value;
  return body;
};
const updateEffect = (
  observation: StrategySelectionObservationV1,
  mutate: (
    body: Omit<EffectObservationV1, "observation_sha256">,
  ) => Omit<EffectObservationV1, "observation_sha256">,
): StrategySelectionObservationV1 => mintStrategySelectionObservationV1({
  ...withoutObservationDigest(observation),
  source_kind: "mutated-family-observation",
  effect_observation: mintEffectObservationV1(mutate(
    withoutEffectDigest(observation.effect_observation),
  )),
});
const updateExecution = (
  observation: StrategySelectionObservationV1,
  mutate: (
    body: Omit<StrategyExecutionObservationV1, "observation_sha256">,
  ) => Omit<StrategyExecutionObservationV1, "observation_sha256">,
): StrategySelectionObservationV1 => mintStrategySelectionObservationV1({
  ...withoutObservationDigest(observation),
  source_kind: "mutated-family-observation",
  strategy_execution_observation: mintStrategyExecutionObservationV1(mutate(
    withoutExecutionDigest(observation.strategy_execution_observation),
  )),
});

export const applyStrategySelectorMutant = (
  observation: StrategySelectionObservationV1,
  mutation: StrategySelectionMutationV1,
): StrategySelectionObservationV1 => {
  const body = withoutObservationDigest(observation);
  const first = observation.cases[0];
  if (!first || !observation.cases[1]) {
    throw new Error("FAMILY_POLICY_SELECTOR_MUTATION_REQUIRES_CASES");
  }
  if (mutation.mutation_kind === "boolean-return") {
    return mintStrategySelectionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      cases: observation.cases.map((item, index) => index === 0
        ? {
          ...item,
          selected_kind: "boolean",
          selected_strategy_id: true,
          selected_sha256: sha256SelectedStrategyIdentity(true),
        }
        : item),
    });
  }
  if (mutation.mutation_kind === "unknown-strategy") {
    const unknown = "settlement.route.unknown";
    return mintStrategySelectionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      cases: observation.cases.map((item, index) => index === 0
        ? {
          ...item,
          selected_kind: "strategy-id",
          selected_strategy_id: unknown,
          selected_sha256: sha256SelectedStrategyIdentity(unknown),
        }
        : item),
    });
  }
  if (mutation.mutation_kind === "foreign-catalogue") {
    return mintStrategySelectionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      catalogue_ref: {...body.catalogue_ref, catalogue_sha256: digest("f")},
    });
  }
  if (mutation.mutation_kind === "ignored-selection-input") {
    return mintStrategySelectionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      cases: observation.cases.map((item, index) => index === 1
        ? {
          ...item,
          selected_kind: first.selected_kind,
          selected_strategy_id: first.selected_strategy_id,
          selected_sha256: first.selected_sha256,
        }
        : item),
    });
  }
  if (mutation.mutation_kind === "missing-case") {
    return mintStrategySelectionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      cases: observation.cases.slice(1),
    });
  }
  if (mutation.mutation_kind === "self-issued-effect-observer") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      observer_ref: {
        ...effect.observer_ref,
        owner_ref: effect.observer_ref.provider_id,
      },
    }));
  }
  if (mutation.mutation_kind === "unsupported-effect-channel") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      channels: effect.channels.map((entry) => entry.channel === "network"
        ? {...entry, coverage: "unsupported"}
        : entry),
    }));
  }
  if (mutation.mutation_kind === "ambient-read") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      channels: effect.channels.map((entry) => entry.channel === "environment"
        ? {...entry, read_count: 1}
        : entry),
    }));
  }
  if (mutation.mutation_kind === "state-write") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      channels: effect.channels.map((entry) => entry.channel === "global-cache"
        ? {...entry, write_count: 1}
        : entry),
    }));
  }
  if (mutation.mutation_kind === "delayed-effect") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      channels: effect.channels.map((entry) => entry.channel === "delayed-lazy"
        ? {...entry, deferred_count: 1}
        : entry),
    }));
  }
  if (mutation.mutation_kind === "incomplete-result") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      result: {...effect.result, consumption: "incomplete"},
    }));
  }
  if (mutation.mutation_kind === "non-quiescent") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      quiescence: {observed: true, pending_count: 1},
    }));
  }
  if (mutation.mutation_kind === "self-issued-execution-trap") {
    return updateExecution(observation, (execution) => ({
      ...execution,
      source_kind: "mutated-strategy-execution-trap",
      observer_ref: {
        ...execution.observer_ref,
        owner_ref: execution.observer_ref.provider_id,
      },
    }));
  }
  if (mutation.mutation_kind === "partial-execution-trap") {
    return updateExecution(observation, (execution) => ({
      ...execution,
      source_kind: "mutated-strategy-execution-trap",
      coverage: "partial",
      covered_strategy_ids: execution.covered_strategy_ids.slice(1),
    }));
  }
  if (mutation.mutation_kind === "strategy-execution-attempt") {
    return updateExecution(observation, (execution) => ({
      ...execution,
      source_kind: "mutated-strategy-execution-trap",
      attempt_count: 1,
      attempted_strategy_ids: [String(first.selected_strategy_id)],
      completion_count: 1,
    }));
  }
  if (mutation.mutation_kind === "stale-definition-binding") {
    return mintStrategySelectionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      definition_ref: {...body.definition_ref, definition_sha256: digest("d")},
    });
  }
  const exhaustive: never = mutation.mutation_kind;
  throw new Error(`FAMILY_POLICY_SELECTOR_MUTATION_UNSUPPORTED:${String(exhaustive)}`);
};

export const requiredStrategySelectorEffectChannels = (): typeof EFFECT_CHANNELS =>
  EFFECT_CHANNELS;
