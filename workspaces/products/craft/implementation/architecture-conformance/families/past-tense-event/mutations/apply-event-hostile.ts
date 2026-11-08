import type {EventRelationAssertion, PastTenseEventObservation} from "../contracts/event-contracts.js";

export type EventHostileMutation = Readonly<{
  hostile_id: string;
  hostile_class: "type-semantic" | "rel-a-evidence" | "s1-cross-boundary";
  mutation: Readonly<Record<string, unknown>>;
}>;

export const applyEventObservationHostile = (
  baseline: PastTenseEventObservation,
  hostile: EventHostileMutation,
): PastTenseEventObservation => {
  if (hostile.hostile_class === "rel-a-evidence") throw new Error("RMT_EVENT_HOSTILE_CLASS_INVALID");
  const durable = hostile.mutation.durable_occurrence;
  return {
    ...baseline,
    ...hostile.mutation,
    durable_occurrence: durable && typeof durable === "object" && !Array.isArray(durable)
      ? {...baseline.durable_occurrence, ...durable as Record<string, unknown>} as PastTenseEventObservation["durable_occurrence"]
      : baseline.durable_occurrence,
  } as PastTenseEventObservation;
};

export const applyEventRelationHostile = (
  baseline: EventRelationAssertion,
  hostile: EventHostileMutation,
): EventRelationAssertion => {
  if (hostile.hostile_class !== "rel-a-evidence") throw new Error("RMT_EVENT_HOSTILE_CLASS_INVALID");
  return {...baseline, ...hostile.mutation} as EventRelationAssertion;
};
