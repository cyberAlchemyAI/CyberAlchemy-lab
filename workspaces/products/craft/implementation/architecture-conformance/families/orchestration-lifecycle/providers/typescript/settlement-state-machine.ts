export const SettlementState = Object.freeze({Pending: "pending", Settled: "settled", Failed: "failed"} as const);
export type SettlementState = typeof SettlementState[keyof typeof SettlementState];
export type SettlementTrigger = "confirm" | "reject";
export type SettlementEffectIntent = "persist-settlement" | "append-settlement-created" | "record-rejection";

export type SettlementTransition = Readonly<{
  accepted: boolean;
  nextState: SettlementState | null;
  guardIds: readonly string[];
  effectIntents: readonly SettlementEffectIntent[];
}>;

export const transitionSettlementLifecycle = (state: SettlementState, trigger: SettlementTrigger): SettlementTransition => {
  if (state === SettlementState.Pending && trigger === "confirm") {
    return Object.freeze({accepted: true, nextState: SettlementState.Settled, guardIds: Object.freeze(["can-settle"]), effectIntents: Object.freeze(["persist-settlement", "append-settlement-created"])});
  }
  if (state === SettlementState.Pending && trigger === "reject") {
    return Object.freeze({accepted: true, nextState: SettlementState.Failed, guardIds: Object.freeze(["can-settle"]), effectIntents: Object.freeze(["record-rejection"])});
  }
  return Object.freeze({accepted: false, nextState: null, guardIds: Object.freeze([]), effectIntents: Object.freeze([])});
};

export const settlementTransitions = Object.freeze([
  Object.freeze({from: "pending", trigger: "confirm", to: "settled", guard_ids: Object.freeze(["can-settle"]), effect_intents: Object.freeze(["persist-settlement", "append-settlement-created"])}),
  Object.freeze({from: "pending", trigger: "reject", to: "failed", guard_ids: Object.freeze(["can-settle"]), effect_intents: Object.freeze(["record-rejection"])}),
] as const);
