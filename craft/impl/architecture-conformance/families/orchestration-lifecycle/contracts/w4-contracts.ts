import type {ContentRef} from "../../effects-connections/contracts/w3-contracts.js";

export type W4Language = "typescript" | "python" | "rust";

export type W4Binding = Readonly<{
  protocol_id: "domainspec.w4-descriptor-binding/v1";
  concept_ref: ContentRef;
  decision_ref: ContentRef;
  profile_ref: ContentRef;
  provider_ref: ContentRef;
  source_ref: ContentRef;
  fixture_ref: ContentRef;
}>;

type W4DescriptorBase = Readonly<{
  schema_version: "domainspec.w4-descriptor/v1";
  descriptor_id: string;
  language: W4Language;
  binding: W4Binding;
  admission_status: "candidate";
  claim_ceiling: "candidate-local-exact-fixture";
  authority_effect: "none";
}>;

export type TransitionContract = Readonly<{
  from: string;
  trigger: string;
  to: string;
  guard_ids: readonly string[];
  effect_intents: readonly string[];
}>;

export type StateMachineDescriptor = W4DescriptorBase & Readonly<{
  kind: "StateMachine";
  expected_states: readonly string[];
  initial_state: string;
  terminal_states: readonly string[];
  transitions: readonly TransitionContract[];
  invalid_transition_policy: "reject";
  effect_execution: "returned-effect-intents";
}>;

export type WorkflowStepContract = Readonly<{
  step_id: string;
  binding_id: string;
  binding_kind: "Operation" | "Workflow";
  failure_policy: "stop" | "continue" | "compensate";
  compensation_id: string | null;
}>;

export type WorkflowDescriptor = W4DescriptorBase & Readonly<{
  kind: "Workflow";
  scope: "intra-feature" | "cross-feature";
  steps: readonly WorkflowStepContract[];
  ordered_step_ids: readonly string[];
  terminal_outcomes: readonly string[];
  failure_contract_id: string;
  continuation_boundary: "synchronous-return" | "awaited-completion" | "declared-background-handoff";
}>;

export type W4Descriptor = StateMachineDescriptor | WorkflowDescriptor;

export type StateMachineObservation = Readonly<{
  kind: "StateMachine";
  observed_states: readonly string[];
  observed_initial_state: string;
  observed_terminal_states: readonly string[];
  observed_transitions: readonly TransitionContract[];
  executions: readonly Readonly<{
    from: string;
    trigger: string;
    accepted: boolean;
    to: string | null;
    guard_ids: readonly string[];
    effect_intents: readonly string[];
  }>[];
  effects_performed_inline: readonly string[];
}>;

export type WorkflowObservation = Readonly<{
  kind: "Workflow";
  scope: WorkflowDescriptor["scope"];
  observed_steps: readonly WorkflowStepContract[];
  trace: readonly string[];
  terminal_outcome: string;
  failure_contract_id: string;
  failed_step_id: string | null;
  compensations: readonly string[];
  continuation_boundary: WorkflowDescriptor["continuation_boundary"];
  continuation_closed: boolean;
}>;

export type W4Observation = StateMachineObservation | WorkflowObservation;

export type W4FindingCode =
  | "ARCH_W4_BINDING_INVALID"
  | "ARCH_W4_OBSERVER_UNSUPPORTED"
  | "ARCH_W4_OBSERVATION_INCOMPLETE"
  | "ARCH_STATE_SET_DRIFT"
  | "ARCH_STATE_INITIAL_INVALID"
  | "ARCH_STATE_TERMINAL_INVALID"
  | "ARCH_STATE_TRANSITION_DRIFT"
  | "ARCH_STATE_TRANSITION_UNOBSERVED"
  | "ARCH_STATE_INVALID_TRANSITION_ACCEPTED"
  | "ARCH_STATE_INVALID_POLICY_UNOBSERVED"
  | "ARCH_STATE_DIRECTION_DRIFT"
  | "ARCH_STATE_GUARD_DRIFT"
  | "ARCH_STATE_EFFECT_INTENT_DRIFT"
  | "ARCH_STATE_INLINE_EFFECT"
  | "ARCH_WORKFLOW_STEP_DRIFT"
  | "ARCH_WORKFLOW_SCOPE_DRIFT"
  | "ARCH_WORKFLOW_ORDER_DRIFT"
  | "ARCH_WORKFLOW_TERMINAL_DRIFT"
  | "ARCH_WORKFLOW_FAILURE_DRIFT"
  | "ARCH_WORKFLOW_COMPENSATION_DRIFT"
  | "ARCH_WORKFLOW_CONTINUATION_DRIFT"
  | "ARCH_WORKFLOW_CONTINUATION_OPEN";

export type W4Evaluation = Readonly<{
  schema_version: "domainspec.w4-evaluation/v1";
  descriptor_id: string;
  verdict: "pass" | "reject" | "unsupported" | "indeterminate";
  findings: readonly Readonly<{code: W4FindingCode; expected: unknown; observed: unknown}>[];
  authority_effect: "none";
}>;
