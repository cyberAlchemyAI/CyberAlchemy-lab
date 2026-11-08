import {
  evaluateWorkflowCase,
  makeSettlementWorkflowCase,
  type WorkflowCase,
} from "./workflow-v1.js";
import {
  planWorkflowRecovery,
  type RecoveryIntent,
  type RecoveryOperationMapping,
} from "./workflow-compensation-v1.js";

export type SettlementWorkflowOperationId =
  | "validate-settlement"
  | "decide-settlement"
  | "persist-settlement"
  | "publish-settlement-created"
  | "forward-recover-settlement";

export interface NamedSettlementOperation {
  readonly operationId: SettlementWorkflowOperationId;
  invoke(input: unknown): Promise<unknown>;
}

export interface SettlementWorkflowBindings {
  readonly validateSettlement: NamedSettlementOperation;
  readonly decideSettlement: NamedSettlementOperation;
  readonly persistSettlement: NamedSettlementOperation;
  readonly publishSettlementCreated: NamedSettlementOperation;
  readonly forwardRecoverSettlement: NamedSettlementOperation;
}

export interface SettlementWorkflowComposition {
  readonly workflowCase: WorkflowCase;
  readonly bindings: SettlementWorkflowBindings;
}

const EXPECTED_BINDINGS = Object.freeze({
  validateSettlement: "validate-settlement",
  decideSettlement: "decide-settlement",
  persistSettlement: "persist-settlement",
  publishSettlementCreated: "publish-settlement-created",
  forwardRecoverSettlement: "forward-recover-settlement",
} as const);

const ARCHITECTURE_CONTINUATIONS = Object.freeze({
  stop: 'failure_policy:"stop"',
  continue: 'result:"pass"',
  retry: "stop-and-return-structured-outcome",
  compensate: "recovery_intents",
  terminal: "terminal_outcome",
});

const SETTLEMENT_RECOVERY_MAPPINGS: readonly RecoveryOperationMapping[] = Object.freeze([
  Object.freeze({ stepId: "validate", operationId: null, dependsOn: Object.freeze([]) }),
  Object.freeze({ stepId: "decide", operationId: null, dependsOn: Object.freeze([]) }),
  Object.freeze({ stepId: "persist", operationId: "forward-recover-settlement", dependsOn: Object.freeze([]) }),
]);

// Composition binds named Operations; it does not acquire their execution authority.
export const makeSettlementWorkflowComposition = (
  bindings: SettlementWorkflowBindings,
): SettlementWorkflowComposition => {
  for (const [bindingName, expectedId] of Object.entries(EXPECTED_BINDINGS)) {
    const binding = bindings[bindingName as keyof SettlementWorkflowBindings];
    if (binding.operationId !== expectedId) {
      throw new Error(`RMT_WF_COMPOSITION_BINDING_INVALID:${bindingName}`);
    }
  }
  return Object.freeze({
    workflowCase: makeSettlementWorkflowCase(),
    bindings: Object.freeze({ ...bindings }),
  });
};

export const evaluateSettlementWorkflowComposition = (
  composition: SettlementWorkflowComposition,
) => {
  const evaluation = evaluateWorkflowCase(composition.workflowCase);
  const recoveryIntents = evaluation.portable.scenarios.flatMap(
    (scenario) => scenario.recovery_intents,
  );
  const recoveryIntentsWithPlans: readonly RecoveryIntent[] = Object.freeze(
    evaluation.portable.scenarios.flatMap((scenario) => {
      if (scenario.failed_step_id === null) return [];
      const decision = planWorkflowRecovery({
        workflowId: "settlement-workflow",
        workflowExecutionId: scenario.scenario_id,
        failureOccurrenceId: `${scenario.scenario_id}-failure`,
        failedStepId: scenario.failed_step_id,
        completedStepIds: scenario.trace,
        orchestratedOperationIds: Object.values(EXPECTED_BINDINGS),
        mappings: SETTLEMENT_RECOVERY_MAPPINGS,
      });
      return decision.recoveryIntent === null ? [] : [decision.recoveryIntent];
    }),
  );
  return Object.freeze({
    ...evaluation,
    architecture: Object.freeze({
      continuationSelectors: ARCHITECTURE_CONTINUATIONS,
      compensationCallableId:
        composition.bindings.forwardRecoverSettlement.operationId,
      recoveryIntents: Object.freeze([...recoveryIntents]),
      recoveryIntentsWithPlans,
      compensationExecutorOwner: "external-runtime" as const,
      compensationExecution: false as const,
      directEffectExecution: false as const,
      suppliedAtCompositionRoot: true as const,
    }),
  });
};
