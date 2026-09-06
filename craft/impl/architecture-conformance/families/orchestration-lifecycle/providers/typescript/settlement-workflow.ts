export type WorkflowStepId = "validate" | "decide" | "persist" | "publish";
export type WorkflowStep = Readonly<{stepId: WorkflowStepId; run: () => Promise<void>; compensationId?: string; compensate?: () => Promise<void>}>;
export type WorkflowResult = Readonly<{outcome: "settlement-completed" | "settlement-failed"; trace: readonly WorkflowStepId[]; failedStepId: WorkflowStepId | null; compensations: readonly string[]}>;

export const settlementWorkflowStepIds = Object.freeze(["validate", "decide", "persist", "publish"] as const);

const validateSettlementWorkflowSteps = (steps: readonly WorkflowStep[]): ReadonlyMap<WorkflowStepId, WorkflowStep> => {
  const ids = steps.map(({stepId}) => stepId);
  for (const stepId of settlementWorkflowStepIds) {
    if (!ids.includes(stepId)) throw new Error(`ARCH_WORKFLOW_STEP_MISSING:${stepId}`);
  }
  if (steps.length !== settlementWorkflowStepIds.length || new Set(ids).size !== ids.length
      || ids.some((stepId) => !settlementWorkflowStepIds.includes(stepId))) {
    throw new Error("ARCH_WORKFLOW_STEP_SET_INVALID");
  }
  for (const step of steps) {
    const compensationValid = step.stepId === "persist"
      ? step.compensationId === "rollback-settlement" && typeof step.compensate === "function"
      : step.compensationId === undefined && step.compensate === undefined;
    if (!compensationValid) throw new Error(`ARCH_WORKFLOW_COMPENSATION_CONTRACT_INVALID:${step.stepId}`);
  }
  return new Map(steps.map((step) => [step.stepId, step]));
};

export const runSettlementWorkflow = async (steps: readonly WorkflowStep[]): Promise<WorkflowResult> => {
  const byId = validateSettlementWorkflowSteps(steps);
  const trace: WorkflowStepId[] = [];
  const completed: WorkflowStep[] = [];
  try {
    for (const stepId of settlementWorkflowStepIds) {
      const step = byId.get(stepId);
      if (!step) throw new Error(`ARCH_WORKFLOW_STEP_MISSING:${stepId}`);
      await step.run();
      trace.push(stepId);
      completed.push(step);
    }
    return Object.freeze({outcome: "settlement-completed", trace: Object.freeze(trace), failedStepId: null, compensations: Object.freeze([])});
  } catch (error) {
    const compensations: string[] = [];
    for (const step of [...completed].reverse()) {
      if (step.compensate) {
        if (!step.compensationId) throw new Error(`ARCH_WORKFLOW_COMPENSATION_ID_MISSING:${step.stepId}`);
        await step.compensate();
        compensations.push(step.compensationId);
      }
    }
    const failedStepId = settlementWorkflowStepIds.find((stepId) => !trace.includes(stepId)) ?? null;
    return Object.freeze({outcome: "settlement-failed", trace: Object.freeze(trace), failedStepId, compensations: Object.freeze(compensations)});
  }
};
