import type { ProofStateName } from "../contracts/architecture-proof-receipt.js";

export type ProofState = Readonly<{
  current: ProofStateName;
  history: readonly ProofStateName[];
  diagnostics: readonly string[];
}>;

const nextState: Readonly<Partial<Record<ProofStateName, ProofStateName>>> = {
  prepared: "generated",
  generated: "compiled",
  compiled: "observed",
  observed: "evaluated",
  evaluated: "mutation-killed",
  "mutation-killed": "replayed",
  replayed: "proof-complete",
};

export const createProofState = (): ProofState => Object.freeze({
  current: "prepared",
  history: Object.freeze(["prepared"] as const),
  diagnostics: Object.freeze([]),
});

export const advanceProofState = (state: ProofState, requested: ProofStateName): ProofState => {
  if (state.current === "blocked") return state;
  if (nextState[state.current] !== requested) {
    return Object.freeze({
      current: "blocked" as const,
      history: Object.freeze([...state.history, "blocked" as const]),
      diagnostics: Object.freeze([
        ...state.diagnostics,
        `ARCH_PROOF_STATE_TRANSITION_INVALID:${state.current}->${requested}`,
      ]),
    });
  }
  return Object.freeze({
    current: requested,
    history: Object.freeze([...state.history, requested]),
    diagnostics: state.diagnostics,
  });
};
