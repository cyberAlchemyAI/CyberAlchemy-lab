import type {
  StateMachineObservation,
  W4Descriptor,
  W4FindingCode,
  W4Observation,
  WorkflowObservation,
} from "../contracts/w4-contracts.js";

export type W4HostileCase = Readonly<{
  mutant_id: string;
  observation: W4Observation;
  expected_codes: readonly W4FindingCode[];
}>;

export const buildW4Hostiles = (
  descriptor: W4Descriptor,
  observation: W4Observation,
): readonly W4HostileCase[] => {
  if (descriptor.kind === "StateMachine" && observation.kind === "StateMachine") {
    const base = observation as StateMachineObservation;
    const accepted = base.executions.find((item) => item.accepted) ?? base.executions[0]!;
    return Object.freeze([
      {mutant_id: "state-set-omitted", observation: {...base, observed_states: base.observed_states.slice(0, -1)}, expected_codes: ["ARCH_STATE_SET_DRIFT"]},
      {mutant_id: "state-initial-drift", observation: {...base, observed_initial_state: "settled"}, expected_codes: ["ARCH_STATE_INITIAL_INVALID"]},
      {mutant_id: "state-transition-omitted", observation: {...base, observed_transitions: base.observed_transitions.slice(0, -1)}, expected_codes: ["ARCH_STATE_TRANSITION_DRIFT"]},
      {mutant_id: "state-transition-unobserved", observation: {...base, executions: base.executions.filter((item) => !item.accepted || item.trigger !== "reject")}, expected_codes: ["ARCH_STATE_TRANSITION_UNOBSERVED"]},
      {mutant_id: "state-invalid-policy-unobserved", observation: {...base, executions: base.executions.filter((item) => item.accepted)}, expected_codes: ["ARCH_STATE_INVALID_POLICY_UNOBSERVED"]},
      {mutant_id: "state-invalid-transition-accepted", observation: {...base, executions: [...base.executions, {from: "settled", trigger: "confirm", accepted: true, to: "failed", guard_ids: [], effect_intents: []}]}, expected_codes: ["ARCH_STATE_INVALID_TRANSITION_ACCEPTED"]},
      {mutant_id: "state-direction-drift", observation: {...base, executions: [{...accepted, to: "failed"}, ...base.executions.filter((item) => item !== accepted)]}, expected_codes: ["ARCH_STATE_DIRECTION_DRIFT", "ARCH_STATE_TRANSITION_UNOBSERVED"]},
      {mutant_id: "state-inline-effect", observation: {...base, effects_performed_inline: ["write:settlement"]}, expected_codes: ["ARCH_STATE_INLINE_EFFECT"]},
    ]);
  }
  if (descriptor.kind === "Workflow" && observation.kind === "Workflow") {
    const base = observation as WorkflowObservation;
    return Object.freeze([
      {mutant_id: "workflow-scope-drift", observation: {...base, scope: base.scope === "intra-feature" ? "cross-feature" : "intra-feature"}, expected_codes: ["ARCH_WORKFLOW_SCOPE_DRIFT"]},
      {mutant_id: "workflow-step-omitted", observation: {...base, observed_steps: base.observed_steps.slice(0, -1)}, expected_codes: ["ARCH_WORKFLOW_STEP_DRIFT"]},
      {mutant_id: "workflow-order-inverted", observation: {...base, trace: [...base.trace].reverse()}, expected_codes: ["ARCH_WORKFLOW_ORDER_DRIFT"]},
      {mutant_id: "workflow-terminal-drift", observation: {...base, terminal_outcome: "unknown"}, expected_codes: ["ARCH_WORKFLOW_TERMINAL_DRIFT"]},
      {mutant_id: "workflow-failure-contract-drift", observation: {...base, failure_contract_id: "wrong/v1"}, expected_codes: ["ARCH_WORKFLOW_FAILURE_DRIFT"]},
      {mutant_id: "workflow-compensation-omitted", observation: {...base, trace: ["validate", "decide", "persist"], terminal_outcome: "settlement-failed", failed_step_id: "publish", compensations: []}, expected_codes: ["ARCH_WORKFLOW_COMPENSATION_DRIFT"]},
      {mutant_id: "workflow-compensation-extra", observation: {...base, compensations: ["undeclared-compensation"]}, expected_codes: ["ARCH_WORKFLOW_COMPENSATION_DRIFT"]},
      {mutant_id: "workflow-continuation-boundary-drift", observation: {...base, continuation_boundary: "declared-background-handoff"}, expected_codes: ["ARCH_WORKFLOW_CONTINUATION_DRIFT"]},
      {mutant_id: "workflow-continuation-open", observation: {...base, continuation_closed: false}, expected_codes: ["ARCH_WORKFLOW_CONTINUATION_OPEN"]},
    ]);
  }
  return Object.freeze([]);
};
