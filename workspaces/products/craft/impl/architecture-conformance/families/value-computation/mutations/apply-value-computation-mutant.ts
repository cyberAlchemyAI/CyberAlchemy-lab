import {
  EFFECT_CHANNELS,
  mintEffectObservationV1,
  type EffectObservationV1,
} from "../../../kernel/evidence/effect-observation/index.js";
import {
  type ValueComputationMutationV1,
  type ValueComputationObservationV1,
} from "../contracts/value-computation-contracts.js";
import {
  mintValueComputationObservationV1,
  sha256CalculationValue,
} from "../providers/decode-value-computation.js";

const digest = (character: string): string => character.repeat(64).slice(0, 64);
const withoutEffectDigest = (
  observation: EffectObservationV1,
): Omit<EffectObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = observation;
  return body;
};
const withoutObservationDigest = (
  observation: ValueComputationObservationV1,
): Omit<ValueComputationObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = observation;
  return body;
};
const updateEffect = (
  observation: ValueComputationObservationV1,
  mutate: (body: Omit<EffectObservationV1, "observation_sha256">) =>
  Omit<EffectObservationV1, "observation_sha256">,
): ValueComputationObservationV1 => mintValueComputationObservationV1({
  ...withoutObservationDigest(observation),
  source_kind: "mutated-family-observation",
  effect_observation: mintEffectObservationV1(mutate(
    withoutEffectDigest(observation.effect_observation),
  )),
});

export const applyValueComputationMutant = (
  observation: ValueComputationObservationV1,
  mutation: ValueComputationMutationV1,
): ValueComputationObservationV1 => {
  const body = withoutObservationDigest(observation);
  const first = observation.cases[0];
  if (!first) throw new Error("FAMILY_CALC_MUTATION_REQUIRES_CASE");
  if (mutation.mutation_kind === "boolean-output") {
    return mintValueComputationObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      cases: observation.cases.map((item, index) => index === 0
        ? {
          ...item,
          result_kind: "boolean",
          result_value: true,
          result_sha256: sha256CalculationValue(true),
          fresh_process_result_sha256: sha256CalculationValue(true),
        }
        : item),
    });
  }
  if (mutation.mutation_kind === "wrong-value") {
    const wrong = typeof first.result_value === "number" ? first.result_value + 1 : "wrong";
    return mintValueComputationObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      cases: observation.cases.map((item, index) => index === 0
        ? {
          ...item,
          result_kind: typeof wrong as "number" | "string",
          result_value: wrong,
          result_sha256: sha256CalculationValue(wrong),
          fresh_process_result_sha256: sha256CalculationValue(wrong),
        }
        : item),
    });
  }
  if (mutation.mutation_kind === "same-process-repeat") {
    return mintValueComputationObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      cases: observation.cases.map((item, index) => index === 0
        ? {...item, process_isolation: "same-process"}
        : item),
    });
  }
  if (mutation.mutation_kind === "nondeterministic-repeat") {
    return mintValueComputationObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      cases: observation.cases.map((item, index) => index === 0
        ? {...item, fresh_process_result_sha256: digest("d")}
        : item),
    });
  }
  if (mutation.mutation_kind === "self-issued-observer") {
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
      channels: effect.channels.map((item) => item.channel === "environment"
        ? {...item, coverage: "unsupported"}
        : item),
    }));
  }
  if (mutation.mutation_kind === "ambient-read") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      channels: effect.channels.map((item) => item.channel === "clock"
        ? {...item, read_count: 1}
        : item),
    }));
  }
  if (mutation.mutation_kind === "state-write") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      channels: effect.channels.map((item) => item.channel === "global-cache"
        ? {...item, write_count: 1}
        : item),
    }));
  }
  if (mutation.mutation_kind === "incomplete-result") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      result: {...effect.result, consumption: "incomplete"},
    }));
  }
  if (mutation.mutation_kind === "delayed-effect") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      channels: effect.channels.map((item) => item.channel === "delayed-lazy"
        ? {...item, deferred_count: 1}
        : item),
    }));
  }
  if (mutation.mutation_kind === "non-quiescent") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      quiescence: {observed: true, pending_count: 1},
    }));
  }
  if (mutation.mutation_kind === "mutable-output") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      result: {...effect.result, mutable_alias_observed: true},
    }));
  }
  if (mutation.mutation_kind === "stale-binding") {
    return mintValueComputationObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      binding: {...body.binding, provider_sha256: digest("e")},
    });
  }
  const exhaustive: never = mutation.mutation_kind;
  throw new Error(`FAMILY_CALC_MUTATION_UNSUPPORTED:${String(exhaustive)}`);
};

export const requiredEffectChannels = (): typeof EFFECT_CHANNELS => EFFECT_CHANNELS;
