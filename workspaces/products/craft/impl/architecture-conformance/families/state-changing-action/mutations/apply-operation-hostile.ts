import type {
  OperationHostileId,
  OperationS1ResidueV1,
  StateChangingActionObservationV1,
} from "../contracts/state-changing-action-contracts.js";
import {mintStateChangingActionObservationV1} from
  "../providers/decode-state-changing-action.js";

const bodyOf = (
  observation: StateChangingActionObservationV1,
): Omit<StateChangingActionObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = observation;
  return body;
};

const mutateRelation = (
  observation: StateChangingActionObservationV1,
  mutate: (
    relation: StateChangingActionObservationV1["relation_assertions"][number],
  ) => StateChangingActionObservationV1["relation_assertions"][number],
): StateChangingActionObservationV1 => mintStateChangingActionObservationV1({
  ...bodyOf(observation),
  source_kind: "mutated-family-observation",
  relation_assertions: observation.relation_assertions.map((relation, index) =>
    index === 0 ? mutate(relation) : relation),
});

export const applyOperationS1Mutation = (
  baseline: OperationS1ResidueV1,
  mutation: Readonly<Partial<OperationS1ResidueV1>>,
): OperationS1ResidueV1 => Object.freeze({...baseline, ...mutation});

export const applyOperationHostile = (
  observation: StateChangingActionObservationV1,
  hostileId: OperationHostileId,
): StateChangingActionObservationV1 => {
  const body = bodyOf(observation);
  if (hostileId === "op/undeclared-write") {
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      write_attempts: [...observation.write_attempts,
        "settlement.write.undeclared-audit-row"],
    });
  }
  if (hostileId === "op/undeclared-effect") {
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      external_effect_attempts: [...observation.external_effect_attempts,
        "network.send.undeclared-webhook"],
    });
  }
  if (hostileId === "op/guard-bypass") {
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      transition_started: true,
    });
  }
  if (hostileId === "op/order-swap") {
    const trace = [...observation.trace];
    [trace[2], trace[4]] = [trace[4]!, trace[2]!];
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      trace,
    });
  }
  if (hostileId === "op/atomicity-removed") {
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      atomicity: {...observation.atomicity, mode: "best-effort"},
    });
  }
  if (hostileId === "op/success-failure-collapse") {
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      outcome: {
        ...observation.outcome,
        value: {
          settlement_id: "settlement-001",
          payout_id: "payout-forbidden-after-rejection",
          status: "committed",
        },
      },
    });
  }
  if (hostileId === "op/emitted-before-commit") {
    const commitOrdinal = observation.trace.indexOf("atomic:commit");
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      emitted_events: observation.emitted_events.map((event) => ({
        ...event,
        trace_ordinal: Math.max(0, commitOrdinal - 1),
      })),
    });
  }
  if (hostileId === "op/continuation-mismatch") {
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      continuation: {
        ...observation.continuation,
        closure: `${observation.continuation.closure}-mismatch`,
      },
    });
  }
  if (hostileId === "op/read-set-drift") {
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      read_attempts: [...observation.read_attempts,
        "settlement.read.undeclared-audit-log"],
    });
  }
  if (hostileId === "op/output-contract-overclaim") {
    return mintStateChangingActionObservationV1({
      ...body,
      source_kind: "mutated-family-observation",
      outcome: {
        ...observation.outcome,
        exactly_once_distributed_delivery_claimed: true,
      },
    });
  }
  if (hostileId === "op/relation-owner-evidence-stale") {
    return mutateRelation(observation, (relation) => ({
      ...relation,
      owner_evidence_sha256: "0".repeat(64),
    }));
  }
  if (hostileId === "op/relation-source-endpoint-mismatch") {
    return mutateRelation(observation, (relation) => ({
      ...relation,
      source_type: "architecture.QueryImplementation",
    }));
  }
  if (hostileId === "op/relation-target-endpoint-mismatch") {
    return mutateRelation(observation, (relation) => ({
      ...relation,
      target_type: "architecture.MappingImplementation",
    }));
  }
  if (hostileId === "op/materialized-without-exact-assertion") {
    return mutateRelation(observation, (relation) => ({
      ...relation,
      exact_assertion: false,
    }));
  }
  const exhaustive: never = hostileId;
  throw new Error(`RMT_OP_HOSTILE_UNSUPPORTED:${String(exhaustive)}`);
};
