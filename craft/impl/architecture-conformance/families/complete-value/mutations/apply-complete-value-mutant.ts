import {
  mintConstructionObservationV1,
  type ConstructionObservationV1,
} from "../../../kernel/evidence/construction-observation/index.js";
import type {
  CompleteValueMutationV1,
  CompleteValueObservationV1,
} from "../contracts/complete-value-contracts.js";

const digest = (character: string): string => character.repeat(64).slice(0, 64);
const bodyOf = (
  observation: CompleteValueObservationV1,
): Omit<ConstructionObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = observation;
  return body;
};
const remint = (
  observation: CompleteValueObservationV1,
  patch: Partial<Omit<ConstructionObservationV1, "observation_sha256">>,
): CompleteValueObservationV1 => mintConstructionObservationV1({
  ...bodyOf(observation),
  ...patch,
  source_kind: "mutated-construction-observation",
});

export const applyCompleteValueMutant = (
  observation: CompleteValueObservationV1,
  mutation: CompleteValueMutationV1,
): CompleteValueObservationV1 => {
  const kind = mutation.mutation_kind;
  if (kind === "reference-identity") {
    return remint(observation, {
      equality_probes: observation.equality_probes.map((probe) =>
        probe.relation === "equal-tuple"
          ? {...probe, references_distinct: false}
          : probe),
    });
  }
  if (kind === "partial-tuple-equality") {
    return remint(observation, {
      equality_probes: observation.equality_probes.map((probe) =>
        probe.relation === "component-variant"
          && probe.varied_component_name === mutation.component_name
          ? {...probe, observed_equal: true}
          : probe),
    });
  }
  if (kind === "incongruent-hash") {
    return remint(observation, {
      equality_probes: observation.equality_probes.map((probe) =>
        probe.relation === "equal-tuple"
          ? {...probe, right_hash_sha256: digest("0")}
          : probe),
    });
  }
  if (kind === "nested-mutation" || kind === "nested-alias") {
    const firstValid = observation.attempts.find(({input_class}) =>
      input_class === "valid")?.case_id;
    return remint(observation, {
      attempts: observation.attempts.map((attempt) =>
        attempt.case_id === firstValid
          ? {
            ...attempt,
            immutability: {
              ...attempt.immutability,
              nested_mutation_observed: kind === "nested-mutation",
              nested_alias_observed: kind === "nested-alias",
            },
          }
          : attempt),
    });
  }
  if (kind === "validator-bypass") {
    return remint(observation, {
      attempts: observation.attempts.map((attempt) => {
        if (attempt.input_class !== "valid") return attempt;
        const trace = attempt.validator_trace.slice(0, -1);
        return {...attempt, validator_trace: trace, formation_ordinal: trace.length};
      }),
    });
  }
  if (kind === "tuple-changing-extension") {
    return remint(observation, {
      extension: {...observation.extension, altered_facets: ["declared-tuple"]},
    });
  }
  if (kind === "component-protocol-identity-missing"
      || kind === "component-protocol-digest-stale") {
    return remint(observation, {
      attempts: observation.attempts.map((attempt) => ({
        ...attempt,
        component_bindings: attempt.component_bindings.map((component) =>
          component.component_name === mutation.component_name
            ? kind === "component-protocol-identity-missing"
              ? {...component, protocol_id: "unsupported.ambient-component/v1"}
              : {...component, protocol_sha256: digest("0")}
            : component),
      })),
    });
  }
  if (kind === "invalid-input-forms-object") {
    const sourceAttempt = observation.attempts.find(({input_class}) =>
      input_class === "valid");
    if (!sourceAttempt || sourceAttempt.normalized_tuple === null) {
      throw new Error("FAMILY_VALUE_MUTATION_REQUIRES_VALID_ATTEMPT");
    }
    return remint(observation, {
      attempts: observation.attempts.map((attempt) =>
        attempt.input_class === "invalid"
          ? {
            ...attempt,
            formation_ordinal: attempt.validator_trace.length,
            result: {status: "formed", object_created: true, failure_codes: []},
            normalized_tuple: sourceAttempt.normalized_tuple,
          }
          : attempt),
    });
  }
  const exhaustive: never = kind;
  throw new Error(`FAMILY_VALUE_MUTATION_UNSUPPORTED:${String(exhaustive)}`);
};
