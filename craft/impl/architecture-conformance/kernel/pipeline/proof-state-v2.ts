import type { ProofAccountingV2 } from "../contracts/proof-accounting-v2.js";

export type ProofStateNameV2 =
  | "prepared"
  | "providers-validated"
  | "positive-evaluated"
  | "mutations-evaluated"
  | "accounted"
  | "evidence-written"
  | "replayed"
  | "proof-complete"
  | "blocked";

export type ProofStateV2 = Readonly<{
  schema_version: "ProofState/v2";
  proof_id: string;
  current: ProofStateNameV2;
  history: readonly ProofStateNameV2[];
  diagnostics: readonly string[];
  authority_effect: "none";
}>;

const nextState: Readonly<
  Partial<Record<ProofStateNameV2, ProofStateNameV2>>
> = Object.freeze({
  prepared: "providers-validated",
  "providers-validated": "positive-evaluated",
  "positive-evaluated": "mutations-evaluated",
  "mutations-evaluated": "accounted",
  accounted: "evidence-written",
  "evidence-written": "replayed",
  replayed: "proof-complete",
});

export const createProofStateV2 = (proofId: string): ProofStateV2 => {
  if (proofId.length === 0) {
    throw Object.assign(new Error("FACTORY_PROOF_ID_INVALID"), {
      code: "FACTORY_PROOF_ID_INVALID",
    });
  }
  return Object.freeze({
    schema_version: "ProofState/v2" as const,
    proof_id: proofId,
    current: "prepared" as const,
    history: Object.freeze(["prepared" as const]),
    diagnostics: Object.freeze([]),
    authority_effect: "none" as const,
  });
};

const block = (state: ProofStateV2, diagnostics: readonly string[]): ProofStateV2 =>
  Object.freeze({
    ...state,
    current: "blocked" as const,
    history: Object.freeze([...state.history, "blocked" as const]),
    diagnostics: Object.freeze([...state.diagnostics, ...diagnostics]),
  });

export const advanceProofStateV2 = (
  state: ProofStateV2,
  requested: ProofStateNameV2,
  accounting?: ProofAccountingV2,
): ProofStateV2 => {
  if (state.current === "blocked" || state.current === "proof-complete") {
    return state;
  }
  if (nextState[state.current] !== requested) {
    return block(state, [
      `FACTORY_PROOF_STATE_TRANSITION_INVALID:${state.current}->${requested}`,
    ]);
  }
  if (requested === "accounted" &&
      (accounting === undefined || accounting.result !== "pass")) {
    return block(state, [
      "FACTORY_PROOF_ACCOUNTING_INCOMPLETE",
      ...(accounting?.diagnostics ?? []),
    ]);
  }
  return Object.freeze({
    ...state,
    current: requested,
    history: Object.freeze([...state.history, requested]),
  });
};
