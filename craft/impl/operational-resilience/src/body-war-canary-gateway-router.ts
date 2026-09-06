import type { GatewayState, RouteDecision, SequenceAudit } from "./body-war-canary-gateway-types.js";

export function routeGatewayRequest(state: GatewayState, sequence: number): RouteDecision {
  if (!Number.isSafeInteger(sequence) || sequence < 1) throw new Error("GATEWAY_SEQUENCE_INVALID");
  const candidate = state.candidate_weight === 10 && state.candidate_target !== null && sequence % 10 === 0;
  if (!candidate) return { sequence, cohort: "stable", target: state.stable_target, action: "forward" };
  return {
    sequence,
    cohort: "candidate",
    target: state.candidate_target as string,
    action: state.candidate_fault_active ? "inject-503" : "forward",
  };
}

export function auditGatewaySequence(state: GatewayState, first: number, count: number): SequenceAudit {
  if (!Number.isSafeInteger(first) || first < 1 || !Number.isSafeInteger(count) || count < 1 || count > 900) throw new Error("GATEWAY_AUDIT_RANGE_INVALID");
  const decisions = Array.from({ length: count }, (_, index) => routeGatewayRequest(state, first + index));
  const stable = decisions.filter((row) => row.cohort === "stable");
  const candidate = decisions.filter((row) => row.cohort === "candidate");
  const candidateFaults = candidate.filter((row) => row.action === "inject-503").length;
  const forwardedCandidate = candidate.length - candidateFaults;
  return Object.freeze({
    first_sequence: first,
    last_sequence: first + count - 1,
    stable_selected: stable.length,
    candidate_selected: candidate.length,
    stable_injected_fault_count: 0,
    candidate_injected_fault_count: candidateFaults,
    forwarded_stable: stable.length,
    forwarded_candidate: forwardedCandidate,
    accounting_equal: stable.length + candidate.length === count && stable.length + candidateFaults + forwardedCandidate === count,
  });
}
