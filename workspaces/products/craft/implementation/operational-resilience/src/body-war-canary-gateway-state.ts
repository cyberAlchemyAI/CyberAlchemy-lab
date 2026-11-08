import {
  GATEWAY_SCHEMA_VERSION,
  type ControlTransition,
  type GatewayControlAction,
  type GatewayState,
} from "./body-war-canary-gateway-types.js";

const isUtc = (value: string): boolean => /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value) && Number.isFinite(Date.parse(value));
const validTarget = (value: string): boolean => /^http:\/\/[a-z0-9-]+:\d{2,5}$/.test(value);

export function initialGatewayState(stableTarget: string, at: string): GatewayState {
  if (!validTarget(stableTarget)) throw new Error("GATEWAY_STABLE_TARGET_INVALID");
  if (!isUtc(at)) throw new Error("GATEWAY_TRANSITION_TIME_INVALID");
  return Object.freeze({
    schema_version: GATEWAY_SCHEMA_VERSION,
    generation: 0,
    stable_target: stableTarget,
    candidate_target: null,
    stable_weight: 100,
    candidate_weight: 0,
    candidate_fault_active: false,
    last_transition_at: at,
    authority_effect: "none",
  });
}

function conflict(state: GatewayState, code: string): ControlTransition {
  return { status: "conflict", code, state };
}

export function applyGatewayControl(
  state: GatewayState,
  expectedGeneration: number,
  action: GatewayControlAction,
  at: string,
): ControlTransition {
  if (!Number.isSafeInteger(expectedGeneration) || expectedGeneration < 0 || state.generation !== expectedGeneration) return conflict(state, "GATEWAY_GENERATION_CONFLICT");
  if (!isUtc(at) || Date.parse(at) < Date.parse(state.last_transition_at)) return conflict(state, "GATEWAY_TRANSITION_TIME_INVALID");
  if (!Number.isSafeInteger(state.generation + 1)) return conflict(state, "GATEWAY_GENERATION_EXHAUSTED");
  const common = { ...state, generation: state.generation + 1, last_transition_at: at };
  if (action.kind === "install-candidate") {
    if (state.candidate_target !== null || state.candidate_weight !== 0 || state.stable_weight !== 100 || state.candidate_fault_active) return conflict(state, "GATEWAY_CANDIDATE_INSTALL_ILLEGAL_STATE");
    if (!validTarget(action.target) || action.target === state.stable_target) return conflict(state, "GATEWAY_CANDIDATE_TARGET_INVALID");
    return { status: "applied", before: state, after: Object.freeze({ ...common, candidate_target: action.target, stable_weight: 90 as const, candidate_weight: 10 as const }) };
  }
  if (action.kind === "set-candidate-fault") {
    if (state.candidate_target === null || state.candidate_weight !== 10 || state.stable_weight !== 90) return conflict(state, "GATEWAY_FAULT_WITHOUT_ACTIVE_CANDIDATE");
    if (state.candidate_fault_active === action.active) return conflict(state, "GATEWAY_NOOP_TRANSITION");
    return { status: "applied", before: state, after: Object.freeze({ ...common, candidate_fault_active: action.active }) };
  }
  if (state.candidate_target === null && state.candidate_weight === 0 && state.stable_weight === 100 && !state.candidate_fault_active) return conflict(state, "GATEWAY_ROLLBACK_ALREADY_STABLE_ONLY");
  return {
    status: "applied",
    before: state,
    after: Object.freeze({ ...common, stable_weight: 100 as const, candidate_weight: 0 as const, candidate_target: null, candidate_fault_active: false }),
  };
}
