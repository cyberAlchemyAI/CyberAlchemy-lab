import {readFileSync} from "node:fs";
import {describe, expect, it} from "vitest";
import type {StateMachineDescriptor, W4Binding, WorkflowDescriptor} from "../contracts/w4-contracts.js";
import {evaluateW4} from "./evaluate-w4.js";
import {buildW4Hostiles} from "../hostiles/w4-hostiles.js";
import {SettlementState, settlementTransitions, transitionSettlementLifecycle} from "../providers/typescript/settlement-state-machine.js";
import {runSettlementWorkflow} from "../providers/typescript/settlement-workflow.js";

const digest = "a".repeat(64);
const binding: W4Binding = {
  protocol_id: "domainspec.w4-descriptor-binding/v1",
  concept_ref: {id: "DS-D1", sha256: digest}, decision_ref: {id: "W4-A", sha256: digest},
  profile_ref: {id: "typescript-strict", sha256: digest}, provider_ref: {id: "typescript-provider", sha256: digest},
  source_ref: {id: "fixture-source", sha256: digest}, fixture_ref: {id: "fixture", sha256: digest},
};
const base = {schema_version: "domainspec.w4-descriptor/v1" as const, language: "typescript" as const, binding, admission_status: "candidate" as const, claim_ceiling: "candidate-local-exact-fixture" as const, authority_effect: "none" as const};

const stateMachine: StateMachineDescriptor = {...base, descriptor_id: "state-machine.settlement", kind: "StateMachine", expected_states: ["pending", "settled", "failed"], initial_state: "pending", terminal_states: ["settled", "failed"], transitions: settlementTransitions, invalid_transition_policy: "reject", effect_execution: "returned-effect-intents"};
const stateObservation = {kind: "StateMachine" as const, observed_states: stateMachine.expected_states, observed_initial_state: "pending", observed_terminal_states: ["settled", "failed"], observed_transitions: stateMachine.transitions, executions: [{from: "pending", trigger: "confirm", accepted: true, to: "settled", guard_ids: ["can-settle"], effect_intents: ["persist-settlement", "append-settlement-created"]}, {from: "pending", trigger: "reject", accepted: true, to: "failed", guard_ids: ["can-settle"], effect_intents: ["record-rejection"]}, {from: "settled", trigger: "confirm", accepted: false, to: null, guard_ids: [], effect_intents: []}], effects_performed_inline: []};

const workflow: WorkflowDescriptor = {...base, descriptor_id: "workflow.complete-settlement", kind: "Workflow", scope: "intra-feature", steps: [
  {step_id: "validate", binding_id: "validate-settlement", binding_kind: "Operation", failure_policy: "stop", compensation_id: null},
  {step_id: "decide", binding_id: "decide-settlement", binding_kind: "Operation", failure_policy: "stop", compensation_id: null},
  {step_id: "persist", binding_id: "persist-settlement", binding_kind: "Operation", failure_policy: "compensate", compensation_id: "rollback-settlement"},
  {step_id: "publish", binding_id: "publish-settlement-created", binding_kind: "Operation", failure_policy: "stop", compensation_id: null},
], ordered_step_ids: ["validate", "decide", "persist", "publish"], terminal_outcomes: ["settlement-completed", "settlement-failed"], failure_contract_id: "settlement-workflow-failure/v1", continuation_boundary: "awaited-completion"};
const workflowObservation = {kind: "Workflow" as const, scope: "intra-feature" as const, observed_steps: workflow.steps, trace: workflow.ordered_step_ids, terminal_outcome: "settlement-completed", failure_contract_id: workflow.failure_contract_id, failed_step_id: null, compensations: [], continuation_boundary: "awaited-completion" as const, continuation_closed: true};

describe("W4 orchestration and lifecycle", () => {
  it("evaluates repository-authored descriptors and observations", () => {
    const descriptors = JSON.parse(readFileSync(new URL("../fixtures/financial-settlement/descriptors.json", import.meta.url), "utf8")) as {descriptors: import("../contracts/w4-contracts.js").W4Descriptor[]};
    const observations = JSON.parse(readFileSync(new URL("../fixtures/financial-settlement/observations.json", import.meta.url), "utf8")) as {observations: import("../contracts/w4-contracts.js").W4Observation[]};
    expect(descriptors.descriptors.map((descriptor, index) => evaluateW4(descriptor, observations.observations[index] ?? null).verdict)).toEqual(["pass", "pass"]);
  });

  it("passes the exact state graph and rejects invalid accepted transitions", () => {
    expect(evaluateW4(stateMachine, stateObservation).verdict).toBe("pass");
    const hostile = {...stateObservation, executions: [...stateObservation.executions, {from: "settled", trigger: "reject", accepted: true, to: "failed", guard_ids: [], effect_intents: []}]};
    expect(evaluateW4(stateMachine, hostile).findings[0]?.code).toBe("ARCH_STATE_INVALID_TRANSITION_ACCEPTED");
  });

  it("rejects reversed transition direction, missing guard, effect drift, and inline I/O", () => {
    const hostile = {...stateObservation, executions: [{from: "pending", trigger: "confirm", accepted: true, to: "failed", guard_ids: [], effect_intents: ["record-rejection"]}], effects_performed_inline: ["write:settlement"]};
    expect(evaluateW4(stateMachine, hostile).findings.map(({code}) => code)).toEqual(["ARCH_STATE_TRANSITION_UNOBSERVED", "ARCH_STATE_INVALID_POLICY_UNOBSERVED", "ARCH_STATE_DIRECTION_DRIFT", "ARCH_STATE_GUARD_DRIFT", "ARCH_STATE_EFFECT_INTENT_DRIFT", "ARCH_STATE_INLINE_EFFECT"]);
  });

  it("keeps the TypeScript reducer pure and rejects terminal transitions", () => {
    expect(transitionSettlementLifecycle(SettlementState.Pending, "confirm")).toEqual({accepted: true, nextState: "settled", guardIds: ["can-settle"], effectIntents: ["persist-settlement", "append-settlement-created"]});
    expect(transitionSettlementLifecycle(SettlementState.Pending, "reject")).toEqual({accepted: true, nextState: "failed", guardIds: ["can-settle"], effectIntents: ["record-rejection"]});
    expect(transitionSettlementLifecycle(SettlementState.Settled, "confirm").accepted).toBe(false);
  });

  it("rejects reordered or missing workflow semantics", () => {
    const hostile = {...workflowObservation, trace: [...workflowObservation.trace].reverse(), terminal_outcome: "unknown", failure_contract_id: "wrong", continuation_closed: false};
    expect(evaluateW4(workflow, hostile).findings.map(({code}) => code)).toEqual(["ARCH_WORKFLOW_TERMINAL_DRIFT", "ARCH_WORKFLOW_FAILURE_DRIFT", "ARCH_WORKFLOW_ORDER_DRIFT", "ARCH_WORKFLOW_CONTINUATION_OPEN"]);
  });

  it("runs the exact workflow and compensates completed steps in reverse order", async () => {
    const calls: string[] = [];
    const success = await runSettlementWorkflow(["validate", "decide", "persist", "publish"].map((stepId) => ({stepId: stepId as "validate" | "decide" | "persist" | "publish", run: async () => {calls.push(stepId);}, ...(stepId === "persist" ? {compensationId: "rollback-settlement", compensate: async () => {calls.push("undo-persist");}} : {})})));
    expect(success).toMatchObject({outcome: "settlement-completed", trace: ["validate", "decide", "persist", "publish"]});
    const failed = await runSettlementWorkflow([
      {stepId: "validate", run: async () => {}},
      {stepId: "decide", run: async () => {}},
      {stepId: "persist", run: async () => {}, compensationId: "rollback-settlement", compensate: async () => {calls.push("undo-persist");}},
      {stepId: "publish", run: async () => {throw new Error("publication failed");}},
    ]);
    expect(failed).toMatchObject({outcome: "settlement-failed", failedStepId: "publish", compensations: ["rollback-settlement"]});
  });

  it("rejects duplicate or extra workflow steps before performing work", async () => {
    const calls: string[] = [];
    await expect(runSettlementWorkflow([
      {stepId: "validate", run: async () => {calls.push("validate");}},
      {stepId: "decide", run: async () => {calls.push("decide");}},
      {stepId: "persist", run: async () => {calls.push("persist");}, compensationId: "rollback-settlement", compensate: async () => {}},
      {stepId: "persist", run: async () => {calls.push("duplicate");}, compensationId: "rollback-settlement", compensate: async () => {}},
      {stepId: "publish", run: async () => {calls.push("publish");}},
    ])).rejects.toThrow("ARCH_WORKFLOW_STEP_SET_INVALID");
    expect(calls).toEqual([]);
  });

  it("rejects graph/provider disagreement and omitted declared compensation", () => {
    const graphDrift = {...stateObservation, observed_states: ["pending", "settled"], observed_transitions: stateObservation.observed_transitions.slice(0, 1)};
    expect(evaluateW4(stateMachine, graphDrift).findings.map(({code}) => code)).toEqual(["ARCH_STATE_SET_DRIFT", "ARCH_STATE_TRANSITION_DRIFT"]);
    const failedWorkflow = {...workflowObservation, trace: ["validate", "decide", "persist"], terminal_outcome: "settlement-failed", failed_step_id: "publish", compensations: []};
    expect(evaluateW4(workflow, failedWorkflow).findings.map(({code}) => code)).toEqual(["ARCH_WORKFLOW_COMPENSATION_DRIFT"]);
  });

  it("kills every independently authored W4 hostile", () => {
    for (const [descriptor, observation] of [[stateMachine, stateObservation], [workflow, workflowObservation]] as const) {
      for (const hostile of buildW4Hostiles(descriptor, observation)) {
        const result = evaluateW4(descriptor, hostile.observation);
        expect(result.verdict, hostile.mutant_id).toBe("reject");
        expect(result.findings.map(({code}) => code), hostile.mutant_id).toEqual(expect.arrayContaining(hostile.expected_codes));
      }
    }
  });

  it("never turns absent or mismatched evidence into pass", () => {
    expect(evaluateW4(workflow, null).verdict).toBe("unsupported");
    expect(evaluateW4(workflow, stateObservation).verdict).toBe("indeterminate");
  });
});
