import { createHash } from "node:crypto";

export const WORKFLOW_RECOVERY_RESULTS = Object.freeze(["not-required", "recovery-required"] as const);
export const RECOVERY_INTENT_STATUSES = Object.freeze(["required", "satisfied", "unresolved"] as const);

export type WorkflowRecoveryResult = (typeof WORKFLOW_RECOVERY_RESULTS)[number];
export type RecoveryIntentStatus = (typeof RECOVERY_INTENT_STATUSES)[number];
export type RecoveryFailureContinuation = "retry" | "escalate" | "terminal-failure";

export type RecoveryOperationMapping = Readonly<{
  stepId: string;
  operationId: string | null;
  dependsOn: readonly string[];
}>;

export type RecoveryPlanEntry = Readonly<{
  planOccurrenceId: string;
  stepId: string;
  operationId: string;
  dependsOn: readonly string[];
  invocationIdentity: string;
}>;

export type RecoveryIntent = Readonly<{
  schemaVersion: "domainspec.workflow-recovery-intent/v2";
  intentId: string;
  workflowId: string;
  workflowExecutionId: string;
  failureOccurrenceId: string;
  failedStepId: string;
  completedStepJournalDigest: string;
  planDigest: string;
  semanticStatus: "required";
  plan: readonly RecoveryPlanEntry[];
}>;

export type WorkflowRecoveryDecision = Readonly<{
  schemaVersion: "domainspec.workflow-recovery-decision/v1";
  workflowEvaluationResult: WorkflowRecoveryResult;
  recoveryIntent: RecoveryIntent | null;
}>;

export type RecoveryOperationBinding = Readonly<{
  workflowId: string;
  operationId: string;
  failureContinuation: RecoveryFailureContinuation;
  invoke: (invocationIdentity: string) => Promise<Readonly<{ ok: true }> | Readonly<{ ok: false; reason: string }>>;
}>;

export type RecoveryInvocationReport = Readonly<{
  schemaVersion: "domainspec.workflow-recovery-in-process-report/v1";
  outcome: "succeeded" | "failed";
  executedPlanOccurrenceIds: readonly string[];
  failedPlanOccurrenceId: string | null;
  failureContinuation: RecoveryFailureContinuation | null;
  reason: string | null;
  recoveryIntentSemanticStatus: "required";
  durableTerminalDisposition: null;
}>;

export class WorkflowRecoveryError extends Error {
  constructor(readonly code: string, message: string) {
    super(message);
    this.name = "WorkflowRecoveryError";
  }
}

function reject(code: string, message: string): never {
  throw new WorkflowRecoveryError(code, message);
}

function requireIdentity(value: string, label: string): void {
  if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(value)) {
    reject("RECOVERY_IDENTITY_INVALID", `${label}:${value}`);
  }
}

function sha256(value: string): string {
  return createHash("sha256").update(value).digest("hex");
}

function journalMaterial(completedStepIds: readonly string[]): string {
  return ["domainspec.workflow-completed-step-journal/v1", ...completedStepIds].join("\n");
}

function planMaterial(plan: readonly Omit<RecoveryPlanEntry, "invocationIdentity">[]): string {
  return [
    "domainspec.workflow-recovery-plan/v1",
    ...plan.map((entry) => [entry.planOccurrenceId, entry.stepId, entry.operationId, entry.dependsOn.join(",")].join("|")),
  ].join("\n");
}

function invocationIdentity(intentId: string, planDigest: string, operationId: string, planOccurrenceId: string): string {
  return sha256([
    "domainspec.compensation-invocation-identity/v1",
    intentId,
    planDigest,
    operationId,
    planOccurrenceId,
  ].join("\n"));
}

export function planWorkflowRecovery(input: Readonly<{
  workflowId: string;
  workflowExecutionId: string;
  failureOccurrenceId: string;
  failedStepId: string;
  completedStepIds: readonly string[];
  orchestratedOperationIds: readonly string[];
  mappings: readonly RecoveryOperationMapping[];
}>): WorkflowRecoveryDecision {
  requireIdentity(input.workflowId, "workflowId");
  requireIdentity(input.workflowExecutionId, "workflowExecutionId");
  requireIdentity(input.failureOccurrenceId, "failureOccurrenceId");
  requireIdentity(input.failedStepId, "failedStepId");
  if (new Set(input.completedStepIds).size !== input.completedStepIds.length) {
    reject("RECOVERY_COMPLETED_STEP_DUPLICATE", "completed step IDs must be unique");
  }

  const orchestrated = new Set<string>();
  for (const operationId of input.orchestratedOperationIds) {
    requireIdentity(operationId, "orchestratedOperationId");
    if (orchestrated.has(operationId)) reject("RECOVERY_ORCHESTRATION_DUPLICATE", operationId);
    orchestrated.add(operationId);
  }

  const mappings = new Map<string, RecoveryOperationMapping>();
  for (const mapping of input.mappings) {
    requireIdentity(mapping.stepId, "mapping.stepId");
    if (mappings.has(mapping.stepId)) reject("RECOVERY_MAPPING_DUPLICATE", mapping.stepId);
    if (mapping.operationId !== null) requireIdentity(mapping.operationId, "mapping.operationId");
    if (new Set(mapping.dependsOn).size !== mapping.dependsOn.length) {
      reject("RECOVERY_DEPENDENCY_DUPLICATE", mapping.stepId);
    }
    for (const dependency of mapping.dependsOn) requireIdentity(dependency, "mapping.dependsOn");
    mappings.set(mapping.stepId, mapping);
  }

  const selected = input.completedStepIds.map((stepId, completionIndex) => {
    requireIdentity(stepId, "completedStepId");
    const mapping = mappings.get(stepId);
    if (!mapping || mapping.operationId === null) return null;
    if (!orchestrated.has(mapping.operationId)) {
      reject("RECOVERY_OPERATION_NOT_ORCHESTRATED", `${input.workflowId}:${mapping.operationId}`);
    }
    return {
      planOccurrenceId: `${stepId}-${mapping.operationId}-${completionIndex + 1}`,
      stepId,
      operationId: mapping.operationId,
      dependencyOperationIds: Object.freeze([...mapping.dependsOn]),
    };
  }).filter((entry): entry is NonNullable<typeof entry> => entry !== null).reverse();

  if (selected.length === 0) {
    return Object.freeze({
      schemaVersion: "domainspec.workflow-recovery-decision/v1",
      workflowEvaluationResult: "not-required",
      recoveryIntent: null,
    });
  }

  const occurrencesByOperation = new Map<string, typeof selected>();
  for (const entry of selected) {
    const current = occurrencesByOperation.get(entry.operationId) ?? [];
    occurrencesByOperation.set(entry.operationId, [...current, entry]);
  }

  const pending = selected.map((entry) => {
    const dependsOn = entry.dependencyOperationIds.map((dependency) => {
      const occurrences = occurrencesByOperation.get(dependency) ?? [];
      if (dependency === entry.operationId || occurrences.length !== 1) {
        reject(
          occurrences.length > 1 ? "RECOVERY_DEPENDENCY_AMBIGUOUS" : "RECOVERY_DEPENDENCY_INVALID",
          `${entry.operationId}:depends-on:${dependency}`,
        );
      }
      return occurrences[0]!.planOccurrenceId;
    });
    return Object.freeze({
      planOccurrenceId: entry.planOccurrenceId,
      stepId: entry.stepId,
      operationId: entry.operationId,
      dependsOn: Object.freeze(dependsOn),
    });
  });

  const ordered: Array<(typeof pending)[number]> = [];
  const remaining = [...pending];
  const emitted = new Set<string>();
  while (remaining.length > 0) {
    const index = remaining.findIndex((entry) => entry.dependsOn.every((dependency) => emitted.has(dependency)));
    if (index < 0) reject("RECOVERY_DEPENDENCY_CYCLE", "recovery Operation dependency graph is cyclic");
    const [next] = remaining.splice(index, 1);
    if (!next) reject("RECOVERY_PLAN_INTERNAL", "missing selected recovery Operation");
    ordered.push(next);
    emitted.add(next.planOccurrenceId);
  }

  const completedStepJournalDigest = sha256(journalMaterial(input.completedStepIds));
  const planDigest = sha256(planMaterial(ordered));
  const intentId = sha256([
    "domainspec.workflow-recovery-intent/v2",
    input.workflowExecutionId,
    input.failureOccurrenceId,
    input.failedStepId,
    completedStepJournalDigest,
    planDigest,
  ].join("\n"));
  const plan = Object.freeze(ordered.map((entry) => Object.freeze({
    ...entry,
    invocationIdentity: invocationIdentity(intentId, planDigest, entry.operationId, entry.planOccurrenceId),
  })));

  return Object.freeze({
    schemaVersion: "domainspec.workflow-recovery-decision/v1",
    workflowEvaluationResult: "recovery-required",
    recoveryIntent: Object.freeze({
      schemaVersion: "domainspec.workflow-recovery-intent/v2",
      intentId,
      workflowId: input.workflowId,
      workflowExecutionId: input.workflowExecutionId,
      failureOccurrenceId: input.failureOccurrenceId,
      failedStepId: input.failedStepId,
      completedStepJournalDigest,
      planDigest,
      semanticStatus: "required",
      plan,
    }),
  });
}

function verifyIntent(intent: RecoveryIntent): void {
  if (intent.schemaVersion !== "domainspec.workflow-recovery-intent/v2") reject("RECOVERY_INTENT_SCHEMA_INVALID", intent.schemaVersion);
  if (intent.semanticStatus !== "required") reject("RECOVERY_INTENT_NOT_EXECUTABLE", intent.semanticStatus);
  const occurrences = new Set<string>();
  const emitted = new Set<string>();
  const planForDigest: Array<Omit<RecoveryPlanEntry, "invocationIdentity">> = [];
  for (const entry of intent.plan) {
    requireIdentity(entry.planOccurrenceId, "planOccurrenceId");
    requireIdentity(entry.operationId, "plan.operationId");
    if (occurrences.has(entry.planOccurrenceId)) reject("RECOVERY_PLAN_OCCURRENCE_DUPLICATE", entry.planOccurrenceId);
    if (entry.dependsOn.some((dependency) => !emitted.has(dependency))) reject("RECOVERY_PLAN_ORDER_INVALID", entry.planOccurrenceId);
    occurrences.add(entry.planOccurrenceId);
    emitted.add(entry.planOccurrenceId);
    planForDigest.push(Object.freeze({
      planOccurrenceId: entry.planOccurrenceId,
      stepId: entry.stepId,
      operationId: entry.operationId,
      dependsOn: entry.dependsOn,
    }));
  }
  const observedPlanDigest = sha256(planMaterial(planForDigest));
  if (observedPlanDigest !== intent.planDigest) reject("RECOVERY_PLAN_DIGEST_MISMATCH", observedPlanDigest);
  const observedIntentId = sha256([
    "domainspec.workflow-recovery-intent/v2",
    intent.workflowExecutionId,
    intent.failureOccurrenceId,
    intent.failedStepId,
    intent.completedStepJournalDigest,
    intent.planDigest,
  ].join("\n"));
  if (observedIntentId !== intent.intentId) reject("RECOVERY_INTENT_ID_MISMATCH", observedIntentId);
  for (const entry of intent.plan) {
    const expected = invocationIdentity(intent.intentId, intent.planDigest, entry.operationId, entry.planOccurrenceId);
    if (entry.invocationIdentity !== expected) reject("RECOVERY_INVOCATION_IDENTITY_MISMATCH", entry.planOccurrenceId);
  }
}

export async function executeWorkflowRecovery(
  intent: RecoveryIntent,
  bindings: readonly RecoveryOperationBinding[],
): Promise<RecoveryInvocationReport> {
  verifyIntent(intent);
  const requiredOperationIds = new Set(intent.plan.map(({ operationId }) => operationId));
  const registry = new Map<string, RecoveryOperationBinding>();
  for (const binding of bindings) {
    requireIdentity(binding.operationId, "binding.operationId");
    if (binding.workflowId !== intent.workflowId) reject("RECOVERY_BINDING_WORKFLOW_MISMATCH", `${binding.workflowId}:${binding.operationId}`);
    if (!requiredOperationIds.has(binding.operationId)) reject("RECOVERY_BINDING_UNDECLARED", binding.operationId);
    if (registry.has(binding.operationId)) reject("RECOVERY_BINDING_DUPLICATE", binding.operationId);
    registry.set(binding.operationId, binding);
  }
  for (const operationId of requiredOperationIds) {
    if (!registry.has(operationId)) reject("RECOVERY_BINDING_MISSING", operationId);
  }

  const executed: string[] = [];
  for (const entry of intent.plan) {
    const binding = registry.get(entry.operationId);
    if (!binding) reject("RECOVERY_BINDING_MISSING", entry.operationId);
    let outcome: Awaited<ReturnType<RecoveryOperationBinding["invoke"]>>;
    try {
      outcome = await binding.invoke(entry.invocationIdentity);
    } catch (error) {
      outcome = Object.freeze({ ok: false, reason: error instanceof Error ? error.message : "recovery-operation-threw" });
    }
    if (!outcome.ok) {
      return Object.freeze({
        schemaVersion: "domainspec.workflow-recovery-in-process-report/v1",
        outcome: "failed",
        executedPlanOccurrenceIds: Object.freeze([...executed]),
        failedPlanOccurrenceId: entry.planOccurrenceId,
        failureContinuation: binding.failureContinuation,
        reason: outcome.reason,
        recoveryIntentSemanticStatus: "required",
        durableTerminalDisposition: null,
      });
    }
    executed.push(entry.planOccurrenceId);
  }

  return Object.freeze({
    schemaVersion: "domainspec.workflow-recovery-in-process-report/v1",
    outcome: "succeeded",
    executedPlanOccurrenceIds: Object.freeze(executed),
    failedPlanOccurrenceId: null,
    failureContinuation: null,
    reason: null,
    recoveryIntentSemanticStatus: "required",
    durableTerminalDisposition: null,
  });
}
