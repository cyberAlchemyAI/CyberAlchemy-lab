import type {
  StateMachineDescriptor,
  StateMachineObservation,
  W4Descriptor,
  W4Evaluation,
  W4FindingCode,
  W4Observation,
  WorkflowDescriptor,
  WorkflowObservation,
} from "../contracts/w4-contracts.js";

type Finding = W4Evaluation["findings"][number];
const SHA256 = /^[a-f0-9]{64}$/;
const same = (left: unknown, right: unknown): boolean => JSON.stringify(left) === JSON.stringify(right);
const finding = (code: W4FindingCode, expected: unknown, observed: unknown): Finding => ({code, expected, observed});
const sameStringSet = (left: readonly string[], right: readonly string[]): boolean =>
  left.length === new Set(left).size
    && right.length === new Set(right).size
    && same([...left].sort(), [...right].sort());
const sameObjectSet = (left: readonly unknown[], right: readonly unknown[]): boolean =>
  sameStringSet(left.map((item) => JSON.stringify(item)), right.map((item) => JSON.stringify(item)));

const validateBinding = (descriptor: W4Descriptor): Finding[] => {
  const refs = Object.values(descriptor.binding).filter((value): value is {id: string; sha256: string} =>
    typeof value === "object" && value !== null && "id" in value && "sha256" in value,
  );
  return descriptor.binding.protocol_id === "domainspec.w4-descriptor-binding/v1"
    && refs.length === 6
    && refs.every((ref) => ref.id.length > 0 && SHA256.test(ref.sha256))
    ? []
    : [finding("ARCH_W4_BINDING_INVALID", "six exact content-addressed refs", descriptor.binding)];
};

const evaluateStateMachine = (descriptor: StateMachineDescriptor, observed: StateMachineObservation): Finding[] => {
  const findings: Finding[] = [];
  if (!sameStringSet(descriptor.expected_states, observed.observed_states)) findings.push(finding("ARCH_STATE_SET_DRIFT", descriptor.expected_states, observed.observed_states));
  if (!descriptor.expected_states.includes(descriptor.initial_state) || descriptor.initial_state !== observed.observed_initial_state) findings.push(finding("ARCH_STATE_INITIAL_INVALID", descriptor.initial_state, observed.observed_initial_state));
  if (!descriptor.terminal_states.every((state) => descriptor.expected_states.includes(state)) || !sameStringSet(descriptor.terminal_states, observed.observed_terminal_states)) findings.push(finding("ARCH_STATE_TERMINAL_INVALID", descriptor.terminal_states, observed.observed_terminal_states));
  if (!sameObjectSet(descriptor.transitions, observed.observed_transitions)) findings.push(finding("ARCH_STATE_TRANSITION_DRIFT", descriptor.transitions, observed.observed_transitions));
  const uncoveredTransitions = descriptor.transitions.filter((transition) => !observed.executions.some((execution) =>
    execution.accepted && execution.from === transition.from && execution.trigger === transition.trigger
      && execution.to === transition.to && same(execution.guard_ids, transition.guard_ids)
      && same(execution.effect_intents, transition.effect_intents),
  ));
  if (uncoveredTransitions.length > 0) findings.push(finding("ARCH_STATE_TRANSITION_UNOBSERVED", descriptor.transitions, uncoveredTransitions));
  const invalidRejectionObserved = observed.executions.some((execution) =>
    !execution.accepted && !descriptor.transitions.some(({from, trigger}) => from === execution.from && trigger === execution.trigger),
  );
  if (descriptor.invalid_transition_policy === "reject" && !invalidRejectionObserved) {
    findings.push(finding("ARCH_STATE_INVALID_POLICY_UNOBSERVED", "at least one rejected undeclared transition", observed.executions));
  }
  for (const execution of observed.executions) {
    const transition = descriptor.transitions.find(({from, trigger}) => from === execution.from && trigger === execution.trigger);
    if (!transition && execution.accepted) findings.push(finding("ARCH_STATE_INVALID_TRANSITION_ACCEPTED", "reject", execution));
    if (transition && (execution.to !== transition.to || !execution.accepted)) findings.push(finding("ARCH_STATE_DIRECTION_DRIFT", transition.to, execution));
    if (transition && !same(execution.guard_ids, transition.guard_ids)) findings.push(finding("ARCH_STATE_GUARD_DRIFT", transition.guard_ids, execution.guard_ids));
    if (transition && !same(execution.effect_intents, transition.effect_intents)) findings.push(finding("ARCH_STATE_EFFECT_INTENT_DRIFT", transition.effect_intents, execution.effect_intents));
  }
  if (descriptor.effect_execution === "returned-effect-intents" && observed.effects_performed_inline.length > 0) {
    findings.push(finding("ARCH_STATE_INLINE_EFFECT", [], observed.effects_performed_inline));
  }
  return findings;
};

const evaluateWorkflow = (descriptor: WorkflowDescriptor, observed: WorkflowObservation): Finding[] => {
  const findings: Finding[] = [];
  if (descriptor.scope !== observed.scope) findings.push(finding("ARCH_WORKFLOW_SCOPE_DRIFT", descriptor.scope, observed.scope));
  if (!sameObjectSet(descriptor.steps, observed.observed_steps)) findings.push(finding("ARCH_WORKFLOW_STEP_DRIFT", descriptor.steps, observed.observed_steps));
  if (!descriptor.terminal_outcomes.includes(observed.terminal_outcome)) findings.push(finding("ARCH_WORKFLOW_TERMINAL_DRIFT", descriptor.terminal_outcomes, observed.terminal_outcome));
  if (descriptor.failure_contract_id !== observed.failure_contract_id) findings.push(finding("ARCH_WORKFLOW_FAILURE_DRIFT", descriptor.failure_contract_id, observed.failure_contract_id));
  const failedIndex = observed.failed_step_id === null ? -1 : descriptor.ordered_step_ids.indexOf(observed.failed_step_id);
  const isFailure = observed.terminal_outcome.endsWith("failed");
  if ((isFailure && failedIndex < 0) || (!isFailure && observed.failed_step_id !== null)) findings.push(finding("ARCH_WORKFLOW_FAILURE_DRIFT", isFailure ? "declared failed step" : null, observed.failed_step_id));
  const expectedTrace = failedIndex < 0 ? descriptor.ordered_step_ids : descriptor.ordered_step_ids.slice(0, failedIndex);
  if (!same(expectedTrace, observed.trace)) findings.push(finding("ARCH_WORKFLOW_ORDER_DRIFT", expectedTrace, observed.trace));
  const completedIds = isFailure ? expectedTrace : [];
  const requiredCompensations = completedIds
    .map((stepId) => descriptor.steps.find(({step_id}) => step_id === stepId))
    .filter((step) => step?.failure_policy === "compensate" && step.compensation_id)
    .reverse()
    .map((step) => step!.compensation_id!);
  if (!same(requiredCompensations, observed.compensations)) {
    findings.push(finding("ARCH_WORKFLOW_COMPENSATION_DRIFT", requiredCompensations, observed.compensations));
  }
  if (descriptor.continuation_boundary !== observed.continuation_boundary) findings.push(finding("ARCH_WORKFLOW_CONTINUATION_DRIFT", descriptor.continuation_boundary, observed.continuation_boundary));
  if (!observed.continuation_closed) findings.push(finding("ARCH_WORKFLOW_CONTINUATION_OPEN", true, false));
  return findings;
};

export const evaluateW4 = (descriptor: W4Descriptor, observation: W4Observation | null): W4Evaluation => {
  let findings = validateBinding(descriptor);
  let verdict: W4Evaluation["verdict"] = "pass";
  if (observation === null) {
    verdict = "unsupported";
    findings = [...findings, finding("ARCH_W4_OBSERVER_UNSUPPORTED", descriptor.kind, null)];
  } else if (descriptor.kind !== observation.kind) {
    verdict = "indeterminate";
    findings = [...findings, finding("ARCH_W4_OBSERVATION_INCOMPLETE", descriptor.kind, observation.kind)];
  } else {
    if (descriptor.kind === "StateMachine") findings = [...findings, ...evaluateStateMachine(descriptor, observation as StateMachineObservation)];
    if (descriptor.kind === "Workflow") findings = [...findings, ...evaluateWorkflow(descriptor, observation as WorkflowObservation)];
    verdict = findings.length === 0 ? "pass" : "reject";
  }
  return Object.freeze({
    schema_version: "domainspec.w4-evaluation/v1",
    descriptor_id: descriptor.descriptor_id,
    verdict,
    findings: Object.freeze(findings.map((item) => Object.freeze({...item}))),
    authority_effect: "none",
  });
};
