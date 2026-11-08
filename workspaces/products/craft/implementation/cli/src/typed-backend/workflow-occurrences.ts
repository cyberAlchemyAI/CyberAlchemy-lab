export const WORKFLOW_OCCURRENCES_VERSION = 'domainspec.workflow-occurrences/v1' as const;
export const WORKFLOW_OCCURRENCE_DEFINITION_SHA256 = '44e7e7bae39d0694b771639706a0c6471aed3a9139d0df0232a19f1c6b31ec7d';
export interface WorkflowOccurrences {
  readonly schema_version: typeof WORKFLOW_OCCURRENCES_VERSION;
  readonly ontology_workflow: string;
  readonly steps: readonly Readonly<{step_id: string; operation_ref: string}>[];
  readonly compensations: readonly Readonly<{compensation_id: string; for_step: string; operation_ref: string; depends_on: readonly string[]}>[];
}
export const workflowFail = (reason: string): never => {throw Object.assign(new TypeError('MTCLI_WORKFLOW_OCCURRENCE: ' + reason), {code: 'MTCLI_WORKFLOW_OCCURRENCE'});};
export const freezeWorkflow = <T>(v: T): T => {
  if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freezeWorkflow); Object.freeze(v);} return v;
};
export function assertWorkflowData(value: unknown): void {
  let nodes = 0;
  const visit = (v: unknown, depth: number): void => {
    if (++nodes > 20000 || depth > 64) workflowFail('data limit');
    if (v === null || typeof v === 'string' || typeof v === 'boolean' || typeof v === 'number' && Number.isFinite(v)) return;
    if (!v || typeof v !== 'object') workflowFail('plain JSON data required');
    const array = Array.isArray(v), proto = Object.getPrototypeOf(v);
    if (array ? proto !== Array.prototype : proto !== Object.prototype && proto !== null) workflowFail('plain data required');
    const d = Object.getOwnPropertyDescriptors(v), keys = Reflect.ownKeys(d);
    if (keys.length > 2048) workflowFail('data limit');
    if (array) {
      const length = d.length!.value;
      if (length > 1024 || keys.length !== length + 1) workflowFail('bounded dense array required');
      for (let i = 0; i < length; i++) if (!Object.hasOwn(d, String(i))) workflowFail('dense array required');
    }
    for (const key of keys) {
      if (array && key === 'length') continue;
      const row = d[key as string];
      if (typeof key !== 'string' || !row || !Object.hasOwn(row, 'value') || !row.enumerable) workflowFail('inert data required');
      visit(row!.value, depth + 1);
    }
  };
  visit(value, 0);
}
export function workflowObject(value: unknown, keys: readonly string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== keys.length || keys.some(k => !Object.hasOwn(value, k))) workflowFail('closed fields required');
  return value as Record<string, unknown>;
}
export function workflowList(value: unknown, min = 0): readonly unknown[] {
  if (!Array.isArray(value) || value.length < min || value.length > 128) workflowFail('array limit');
  return value as readonly unknown[];
}
const local = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const selector = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const ontology = /^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+(?:#[A-Za-z][A-Za-z0-9_]*)?$/;
function identifier(value: unknown, pattern: RegExp): string {
  return typeof value === 'string' && value.length <= 256 && pattern.exec(value)?.[0] === value ? value : workflowFail('invalid identifier');
}
function unique(ids: readonly string[], context: string): void {if (new Set(ids).size !== ids.length) workflowFail('duplicate ' + context);}

/** Occurrence source validation only; no callable typing or execution. */
export function decodeWorkflowOccurrences(value: unknown): WorkflowOccurrences {
  assertWorkflowData(value);
  const c = workflowObject(value, ['schema_version', 'ontology_workflow', 'steps', 'compensations']);
  if (c.schema_version !== WORKFLOW_OCCURRENCES_VERSION) workflowFail('unsupported version');
  const steps = workflowList(c.steps, 1).map(v => {
    const s = workflowObject(v, ['step_id', 'operation_ref']);
    return {step_id: identifier(s.step_id, local), operation_ref: identifier(s.operation_ref, selector)};
  });
  unique(steps.map(s => s.step_id), 'step identity');
  const stepIds = new Set(steps.map(s => s.step_id));
  const compensations = workflowList(c.compensations).map(v => {
    const r = workflowObject(v, ['compensation_id', 'for_step', 'operation_ref', 'depends_on']);
    const depends_on = workflowList(r.depends_on).map(v => identifier(v, local)); unique(depends_on, 'dependency');
    const for_step = identifier(r.for_step, local);
    if (!stepIds.has(for_step)) workflowFail('unknown compensated step: ' + for_step);
    return {compensation_id: identifier(r.compensation_id, local), for_step, operation_ref: identifier(r.operation_ref, selector), depends_on};
  });
  unique(compensations.map(c => c.compensation_id), 'compensation identity');
  unique(compensations.map(c => c.for_step), 'compensation for step');
  const byId = new Map(compensations.map(c => [c.compensation_id, c]));
  const active = new Set<string>(), done = new Set<string>();
  const visit = (id: string): void => {
    if (active.has(id)) workflowFail('cyclic compensation dependency: ' + id);
    if (done.has(id)) return;
    const c = byId.get(id) ?? workflowFail('unknown compensation dependency: ' + id);
    active.add(id); c.depends_on.forEach(visit); active.delete(id); done.add(id);
  };
  compensations.forEach(c => visit(c.compensation_id));
  return freezeWorkflow({schema_version: WORKFLOW_OCCURRENCES_VERSION, ontology_workflow: identifier(c.ontology_workflow, ontology), steps, compensations});
}

export function workflowOperationRefs(contract: WorkflowOccurrences): readonly string[] {
  return Object.freeze([...new Set([...contract.steps, ...contract.compensations].map(s => s.operation_ref))].sort());
}
