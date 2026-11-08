import {
  mintEntityLifecycleConstructionObservationV1,
  type EntityLifecycleConstructionObservationV1,
} from "../../../kernel/evidence/construction-observation/index.js";
import type {
  IdentityLifecycleMutationV1,
  IdentityLifecycleObservationV1,
} from "../contracts/identity-lifecycle-contracts.js";

const bodyOf = (
  observation: IdentityLifecycleObservationV1,
): Omit<EntityLifecycleConstructionObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = observation;
  return body;
};
const remint = (
  observation: IdentityLifecycleObservationV1,
  patch: Partial<Omit<EntityLifecycleConstructionObservationV1,
  "observation_sha256">>,
): IdentityLifecycleObservationV1 =>
  mintEntityLifecycleConstructionObservationV1({
    ...bodyOf(observation),
    ...patch,
    source_kind: "mutated-entity-lifecycle-observation",
  });

export const applyIdentityLifecycleMutant = (
  observation: IdentityLifecycleObservationV1,
  mutation: IdentityLifecycleMutationV1,
): IdentityLifecycleObservationV1 => {
  const kind = mutation.mutation_kind;
  if (kind === "per-call-validator-bypass") {
    return remint(observation, {per_call_validator_supplied: true});
  }
  if (kind === "remove-base-validator") {
    return remint(observation, {extension: {...observation.extension,
      base_validators_preserved: false}});
  }
  if (kind === "replace-identity-resolver") {
    return remint(observation, {extension: {...observation.extension,
      identity_resolver_preserved: false}});
  }
  if (kind === "allow-extension-cycle") {
    return remint(observation, {extension: {...observation.extension,
      cycle_detected: true}});
  }
  if (kind === "invalid-input-forms-snapshot") {
    return remint(observation, {
      validation_failure_probe: {...observation.validation_failure_probe,
        identity_resolution_ordinal:
          observation.validation_failure_probe.validator_trace.length,
        construction_ordinal:
          observation.validation_failure_probe.validator_trace.length + 1,
        result: {...observation.validation_failure_probe.result,
          snapshot_created: true}},
    });
  }
  if (kind === "mutate-constructed-snapshot") {
    const first = observation.snapshots[0]?.snapshot_id;
    return remint(observation, {snapshots: observation.snapshots.map((snapshot) =>
      snapshot.snapshot_id === first
        ? {...snapshot, frozen: false, mutation_observed: true}
        : snapshot)});
  }
  if (kind === "complete-field-equality") {
    return remint(observation, {equality_probes: observation.equality_probes.map(
      (probe) => probe.relation === "same-identity-different-state"
        ? {...probe, observed_equal: false}
        : probe,
    )});
  }
  const exhaustive: never = kind;
  throw new Error(`FAMILY_ENTITY_MUTATION_UNSUPPORTED:${String(exhaustive)}`);
};
