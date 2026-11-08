import { describe, expect, it, vi } from "vitest";

import { executeWorkflowRecovery, planWorkflowRecovery, WorkflowRecoveryError } from "./workflow-compensation-v1.js";

const mappings = Object.freeze([
  Object.freeze({ stepId: "reserve", operationId: "release-reservation", dependsOn: Object.freeze([]) }),
  Object.freeze({ stepId: "charge", operationId: "refund-payment", dependsOn: Object.freeze([]) }),
  Object.freeze({ stepId: "persist", operationId: "restore-settlement", dependsOn: Object.freeze([]) }),
]);

const plan = (overrides: Partial<Parameters<typeof planWorkflowRecovery>[0]> = {}) => planWorkflowRecovery({
  workflowId: "settlement-workflow",
  workflowExecutionId: "settlement-run-1",
  failureOccurrenceId: "publish-failure-1",
  failedStepId: "publish",
  completedStepIds: ["reserve", "charge", "persist"],
  orchestratedOperationIds: ["release-reservation", "refund-payment", "restore-settlement"],
  mappings,
  ...overrides,
});

describe("Workflow recovery v1", () => {
  it("separates the not-required Workflow result from Recovery Intent existence", () => {
    expect(plan({ completedStepIds: [], mappings: [] })).toEqual({
      schemaVersion: "domainspec.workflow-recovery-decision/v1",
      workflowEvaluationResult: "not-required",
      recoveryIntent: null,
    });
  });

  it("creates one immutable required intent and reverses completed-step order by default", () => {
    const decision = plan();
    expect(decision.workflowEvaluationResult).toBe("recovery-required");
    expect(decision.recoveryIntent).toMatchObject({
      semanticStatus: "required",
      workflowId: "settlement-workflow",
      workflowExecutionId: "settlement-run-1",
      failureOccurrenceId: "publish-failure-1",
    });
    expect(decision.recoveryIntent?.plan.map(({ operationId }) => operationId)).toEqual([
      "restore-settlement",
      "refund-payment",
      "release-reservation",
    ]);
    expect(decision.recoveryIntent?.intentId).toMatch(/^[a-f0-9]{64}$/);
    expect(decision.recoveryIntent?.planDigest).toMatch(/^[a-f0-9]{64}$/);
    expect(decision.recoveryIntent).toMatchObject({
      completedStepJournalDigest: "4cb1e45d4a5cb20b9625486c7f5ad3cfbbf618d88783231ca7d34f999b58f27f",
      planDigest: "745351ce2d5f9bcb7addce926290c57ac0adf5fe3c7c41a899a551abb3964059",
      intentId: "98c6bdc1708fa2c8bbd0d2663c55aa6604e1fc57dccb0938b5dc507a10b1381e",
    });
    expect(decision.recoveryIntent?.plan.map(({ invocationIdentity }) => invocationIdentity)).toEqual([
      "bbaf6487f752a17045c7be19b0b97b5806df9b685d4a26e02472b9945ceac946",
      "4747d078775519d295004113cd3be9140a74ca77caa5f7108c8422b30626b23f",
      "7377dcb316f57ddde660cc468222cb29973d3095c9d2313e48278de648fc5bb4",
    ]);
  });

  it("honors explicit dependencies before the reverse-completion tie-breaker", () => {
    const decision = plan({
      mappings: [mappings[0]!, mappings[1]!, Object.freeze({ ...mappings[2]!, dependsOn: Object.freeze(["release-reservation"]) })],
    });
    expect(decision.recoveryIntent?.plan.map(({ operationId }) => operationId)).toEqual([
      "refund-payment",
      "release-reservation",
      "restore-settlement",
    ]);
  });

  it("gives repeated uses of one Operation distinct stable invocation identities", () => {
    const input = {
      completedStepIds: ["reserve", "charge"],
      orchestratedOperationIds: ["restore-settlement"],
      mappings: [
        Object.freeze({ stepId: "reserve", operationId: "restore-settlement", dependsOn: Object.freeze([]) }),
        Object.freeze({ stepId: "charge", operationId: "restore-settlement", dependsOn: Object.freeze([]) }),
      ],
    } as const;
    const decision = plan(input);
    const identities = decision.recoveryIntent?.plan.map(({ invocationIdentity }) => invocationIdentity) ?? [];
    expect(identities).toHaveLength(2);
    expect(new Set(identities).size).toBe(2);
    expect(plan(input)).toEqual(decision);
  });

  it("rejects a recovery target without Workflow orchestrates evidence", () => {
    expect(() => plan({ orchestratedOperationIds: ["refund-payment", "restore-settlement"] }))
      .toThrowError(expect.objectContaining({ code: "RECOVERY_OPERATION_NOT_ORCHESTRATED" }));
  });

  it("preflights every exact binding before any invocation", async () => {
    const intent = plan({ completedStepIds: ["reserve", "charge"] }).recoveryIntent!;
    const invoke = vi.fn(async () => Object.freeze({ ok: true as const }));
    await expect(executeWorkflowRecovery(intent, [{
      workflowId: "settlement-workflow",
      operationId: "refund-payment",
      failureContinuation: "retry",
      invoke,
    }])).rejects.toMatchObject<Partial<WorkflowRecoveryError>>({ code: "RECOVERY_BINDING_MISSING" });
    expect(invoke).not.toHaveBeenCalled();
  });

  it("rejects an intent identity that no longer binds its failure and plan", async () => {
    const intent = plan({ completedStepIds: ["reserve"] }).recoveryIntent!;
    await expect(executeWorkflowRecovery({ ...intent, intentId: "0".repeat(64) }, []))
      .rejects.toMatchObject<Partial<WorkflowRecoveryError>>({ code: "RECOVERY_INTENT_ID_MISMATCH" });
  });

  it("invokes exact Operations without inventing a durable terminal disposition", async () => {
    const intent = plan({ completedStepIds: ["reserve", "charge"] }).recoveryIntent!;
    const calls: string[] = [];
    const report = await executeWorkflowRecovery(intent, [...new Set(intent.plan.map(({ operationId }) => operationId))].map((operationId) => ({
      workflowId: "settlement-workflow",
      operationId,
      failureContinuation: "escalate" as const,
      invoke: async (identity: string) => {
        calls.push(`${operationId}:${identity}`);
        return Object.freeze({ ok: true as const });
      },
    })));
    expect(report).toMatchObject({
      outcome: "succeeded",
      recoveryIntentSemanticStatus: "required",
      durableTerminalDisposition: null,
    });
    expect(calls).toHaveLength(2);
    expect(calls.every((call) => /:[a-f0-9]{64}$/.test(call))).toBe(true);
  });

  it("stops at the first failed Operation and preserves its explicit continuation", async () => {
    const intent = plan({ completedStepIds: ["reserve", "charge"] }).recoveryIntent!;
    const report = await executeWorkflowRecovery(intent, [
      {
        workflowId: "settlement-workflow",
        operationId: "refund-payment",
        failureContinuation: "escalate",
        invoke: async () => Object.freeze({ ok: false as const, reason: "gateway-unavailable" }),
      },
      {
        workflowId: "settlement-workflow",
        operationId: "release-reservation",
        failureContinuation: "retry",
        invoke: vi.fn(async () => Object.freeze({ ok: true as const })),
      },
    ]);
    expect(report).toMatchObject({
      outcome: "failed",
      executedPlanOccurrenceIds: [],
      failureContinuation: "escalate",
      reason: "gateway-unavailable",
      recoveryIntentSemanticStatus: "required",
      durableTerminalDisposition: null,
    });
  });

  it("rejects cyclic Operation dependencies", () => {
    expect(() => plan({
      completedStepIds: ["reserve", "charge"],
      mappings: [
        Object.freeze({ stepId: "reserve", operationId: "release-reservation", dependsOn: Object.freeze(["refund-payment"]) }),
        Object.freeze({ stepId: "charge", operationId: "refund-payment", dependsOn: Object.freeze(["release-reservation"]) }),
      ],
    })).toThrowError(expect.objectContaining({ code: "RECOVERY_DEPENDENCY_CYCLE" }));
  });
});
