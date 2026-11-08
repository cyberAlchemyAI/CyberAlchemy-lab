import { describe, expect, it, vi } from "vitest";
import {
  evaluateSettlementWorkflowComposition,
  makeSettlementWorkflowComposition,
  type NamedSettlementOperation,
  type SettlementWorkflowOperationId,
} from "./workflow-v1.composition.js";

const operation = (operationId: SettlementWorkflowOperationId) => {
  const invoke = vi.fn(async () => undefined);
  return {
    binding: { operationId, invoke } satisfies NamedSettlementOperation,
    invoke,
  };
};

describe("TypeScript Workflow v1 composition boundary", () => {
  it("binds named child and forward-recovery Operations without invoking them", () => {
    const validate = operation("validate-settlement");
    const decide = operation("decide-settlement");
    const persist = operation("persist-settlement");
    const publish = operation("publish-settlement-created");
    const recover = operation("forward-recover-settlement");
    const composition = makeSettlementWorkflowComposition({
      validateSettlement: validate.binding,
      decideSettlement: decide.binding,
      persistSettlement: persist.binding,
      publishSettlementCreated: publish.binding,
      forwardRecoverSettlement: recover.binding,
    });

    const result = evaluateSettlementWorkflowComposition(composition);

    expect(result.architecture).toMatchObject({
      compensationCallableId: "forward-recover-settlement",
      recoveryIntents: ["forward-recover-settlement"],
      compensationExecutorOwner: "external-runtime",
      compensationExecution: false,
      directEffectExecution: false,
      suppliedAtCompositionRoot: true,
    });
    expect(result.architecture.recoveryIntentsWithPlans).toEqual([
      expect.objectContaining({
        workflowExecutionId: "post-commit-publication-failure",
        failureOccurrenceId: "post-commit-publication-failure-failure",
        failedStepId: "publish",
        semanticStatus: "required",
        plan: [expect.objectContaining({
          stepId: "persist",
          operationId: "forward-recover-settlement",
        })],
      }),
    ]);
    for (const invoke of [
      validate.invoke,
      decide.invoke,
      persist.invoke,
      publish.invoke,
      recover.invoke,
    ]) {
      expect(invoke).not.toHaveBeenCalled();
    }
  });

  it("rejects a callable bound under the wrong Operation identity", () => {
    const binding = operation("validate-settlement").binding;
    expect(() =>
      makeSettlementWorkflowComposition({
        validateSettlement: binding,
        decideSettlement: operation("decide-settlement").binding,
        persistSettlement: operation("persist-settlement").binding,
        publishSettlementCreated: operation("publish-settlement-created").binding,
        forwardRecoverSettlement: binding,
      }),
    ).toThrowError("RMT_WF_COMPOSITION_BINDING_INVALID:forwardRecoverSettlement");
  });
});
