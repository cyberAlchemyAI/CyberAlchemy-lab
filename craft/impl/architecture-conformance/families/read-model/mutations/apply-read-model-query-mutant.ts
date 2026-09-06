import {
  mintDeclaredReadLifecycleObservationV1,
  mintEffectObservationV1,
  type DeclaredReadLifecycleObservationV1,
  type EffectObservationV1,
} from "../../../kernel/evidence/effect-observation/index.js";
import type {
  ReadModelQueryMutationV1,
  ReadModelQueryMutationVariant,
  ReadModelQueryObservationV1,
} from "../contracts/read-model-contracts.js";
import {
  mintReadModelQueryObservationV1,
  sha256ReadModelQueryValue,
} from "../providers/decode-read-model.js";

const withoutEffectDigest = (
  value: EffectObservationV1,
): Omit<EffectObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = value;
  return body;
};
const withoutLifecycleDigest = (
  value: DeclaredReadLifecycleObservationV1,
): Omit<DeclaredReadLifecycleObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = value;
  return body;
};
const withoutObservationDigest = (
  value: ReadModelQueryObservationV1,
): Omit<ReadModelQueryObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = value;
  return body;
};
const updateLifecycle = (
  observation: ReadModelQueryObservationV1,
  mutate: (
    body: Omit<DeclaredReadLifecycleObservationV1, "observation_sha256">,
  ) => Omit<DeclaredReadLifecycleObservationV1, "observation_sha256">,
): ReadModelQueryObservationV1 => mintReadModelQueryObservationV1({
  ...withoutObservationDigest(observation),
  source_kind: "mutated-family-observation",
  read_lifecycle_observation: mintDeclaredReadLifecycleObservationV1(mutate(
    withoutLifecycleDigest(observation.read_lifecycle_observation),
  )),
});
const updateEffect = (
  observation: ReadModelQueryObservationV1,
  mutate: (
    body: Omit<EffectObservationV1, "observation_sha256">,
  ) => Omit<EffectObservationV1, "observation_sha256">,
): ReadModelQueryObservationV1 => updateLifecycle(observation, (lifecycle) => ({
  ...lifecycle,
  source_kind: "mutated-declared-read-observation",
  effect_observation: mintEffectObservationV1(mutate(
    withoutEffectDigest(lifecycle.effect_observation),
  )),
}));

export const applyReadModelQueryMutant = (
  observation: ReadModelQueryObservationV1,
  mutation: ReadModelQueryMutationV1,
  variant: ReadModelQueryMutationVariant = mutation.variants[0] ?? "default",
): ReadModelQueryObservationV1 => {
  if (!mutation.variants.includes(variant)) {
    throw new Error(`FAMILY_QUERY_MUTATION_VARIANT_UNDECLARED:${variant}`);
  }
  if (mutation.mutation_kind === "hidden-write") {
    return updateEffect(observation, (effect) => ({
      ...effect,
      source_kind: "mutated-effect-observation",
      channels: effect.channels.map((entry) => entry.channel === "filesystem"
        ? {...entry, write_count: 1}
        : entry),
    }));
  }
  if (mutation.mutation_kind === "write-then-restore") {
    return updateLifecycle(observation, (lifecycle) => ({
      ...lifecycle,
      source_kind: "mutated-declared-read-observation",
      write_then_restore_observed: true,
    }));
  }
  if (mutation.mutation_kind === "deferred-lazy-write") {
    return updateLifecycle(observation, (lifecycle) => ({
      ...lifecycle,
      source_kind: "mutated-declared-read-observation",
      declared_read_attempts: lifecycle.declared_read_attempts.map(
        (attempt, index) => index === lifecycle.declared_read_attempts.length - 1
          ? {...attempt, lifecycle_path: variant === "default" ? "return" : variant}
          : attempt,
      ),
      effect_observation: mintEffectObservationV1({
        ...withoutEffectDigest(lifecycle.effect_observation),
        source_kind: "mutated-effect-observation",
        channels: lifecycle.effect_observation.channels.map((entry) =>
          entry.channel === "delayed-lazy"
            ? {...entry, deferred_count: 1}
            : entry),
      }),
    }));
  }
  if (mutation.mutation_kind === "undeclared-read") {
    return updateLifecycle(observation, (lifecycle) => ({
      ...lifecycle,
      source_kind: "mutated-declared-read-observation",
      declared_read_attempts: lifecycle.declared_read_attempts.map((attempt, index) =>
        index === lifecycle.declared_read_attempts.length - 1
          ? {...attempt, target_id: "settlement.read.undeclared-audit-log"}
          : attempt),
    }));
  }
  if (mutation.mutation_kind === "undeclared-result-shape") {
    const result = {
      ...observation.observed_result.result,
      internal_debug_marker: "leaked",
    };
    return mintReadModelQueryObservationV1({
      ...withoutObservationDigest(observation),
      source_kind: "mutated-family-observation",
      observed_result: {
        ...observation.observed_result,
        result,
        result_sha256: sha256ReadModelQueryValue(result),
      },
    });
  }
  if (mutation.mutation_kind === "missing-observation-coverage") {
    return updateLifecycle(observation, (lifecycle) => ({
      ...lifecycle,
      source_kind: "mutated-declared-read-observation",
      lifecycle_paths: lifecycle.lifecycle_paths.map((entry) =>
        entry.lifecycle_path === variant
          ? {...entry, coverage: "unsupported" as const}
          : entry),
      effect_observation: variant === "quiescence"
        ? mintEffectObservationV1({
          ...withoutEffectDigest(lifecycle.effect_observation),
          source_kind: "mutated-effect-observation",
          quiescence: {observed: false, pending_count: 0},
        })
        : lifecycle.effect_observation,
    }));
  }
  if (mutation.mutation_kind === "unsupported-source") {
    return updateLifecycle(observation, (lifecycle) => ({
      ...lifecycle,
      source_kind: "mutated-declared-read-observation",
      source_support: "unsupported-dynamic-or-generated",
    }));
  }
  const exhaustive: never = mutation.mutation_kind;
  throw new Error(`FAMILY_QUERY_MUTATION_UNSUPPORTED:${String(exhaustive)}`);
};
