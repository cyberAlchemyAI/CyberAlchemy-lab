import {assertInterfaceData} from '../typed-backend/interface.js';
import {canonicalJson} from '../input/source-manifest.js';
import {decodeOperationActionBindings, type OperationActionBindings} from '../typed-operation/action-bindings.js';
import {decodeWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../typed-operation/workflow-bindings.js';
import type {ProjectFieldSelection} from '../input/compiled-field-model.js';
import type {FactoryBinding} from './configured-factories.js';
import type {ReconciledWorkflowBinding} from './reconciled-project.js';
import {RESOLVED_ARTIFACT_LAYOUT} from './resolved-artifact-plan.js';
import {pythonPortableIdentifier} from './configured-python-enums.js';

export const RECONCILED_PYTHON_COMPILATION_VERSION = 'domainspec.reconciled-python-compilation/v1-candidate';
export const RECONCILED_PYTHON_PROFILE = 'domainspec.reconciled-python/v1-candidate';
export interface ReconciledPythonSelection {
  readonly schema_version: typeof RECONCILED_PYTHON_COMPILATION_VERSION;
  readonly profile_id: typeof RECONCILED_PYTHON_PROFILE;
  readonly language: 'python';
  readonly module_root: string;
  readonly layout_version: typeof RESOLVED_ARTIFACT_LAYOUT;
  readonly field_bindings: ProjectFieldSelection['bindings'];
  readonly factories: readonly FactoryBinding[];
  readonly operations: readonly OperationActionBindings[];
  readonly workflows: readonly ReconciledWorkflowBinding[];
}
export const failPythonProject = (message: string): never => {throw new TypeError('DS_RECONCILED_PYTHON:' + message);};
export function freezePythonProject<T>(v: T): T {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freezePythonProject); Object.freeze(v);} return v;}
function closed(v: unknown, keys: readonly string[]): Record<string, unknown> {
  if (!v || typeof v !== 'object' || Array.isArray(v) || canonicalJson(Object.keys(v).sort()) !== canonicalJson([...keys].sort())) failPythonProject('closed selection fields');
  return v as Record<string, unknown>;
}
export function decodeReconciledPythonSelection(value: unknown): ReconciledPythonSelection {
  assertInterfaceData(value);
  const row = closed(value, ['schema_version', 'profile_id', 'language', 'module_root', 'layout_version', 'field_bindings', 'factories', 'operations', 'workflows']);
  if (row.schema_version !== RECONCILED_PYTHON_COMPILATION_VERSION || row.profile_id !== RECONCILED_PYTHON_PROFILE || row.language !== 'python' || row.layout_version !== RESOLVED_ARTIFACT_LAYOUT) failPythonProject('explicit Python selection required');
  if (typeof row.module_root !== 'string' || row.module_root.length > 256) failPythonProject('bounded module root');
  (row.module_root as string).split('/').forEach(pythonPortableIdentifier);
  for (const key of ['field_bindings', 'factories', 'operations', 'workflows']) if (!Array.isArray(row[key]) || (row[key] as unknown[]).length > 256) failPythonProject('bounded binding array:' + key);
  for (const factory of row.factories as unknown[]) {const f = closed(factory, ['selector', 'base_validators', 'extensions']); if (typeof f.selector !== 'string' || !Array.isArray(f.base_validators) || !Array.isArray(f.extensions)) failPythonProject('authored factory binding');}
  const operations = (row.operations as unknown[]).map(decodeOperationActionBindings);
  const workflows = (row.workflows as unknown[]).map(value => {
    const w = closed(value, ['selector', 'inputs', 'event_inputs', 'steps', 'compensations', 'result', 'recovery']);
    const recovery = closed(w.recovery, ['dependency_semantics', 'tie_break']);
    if (recovery.dependency_semantics !== 'needed-compensations-only' || recovery.tie_break !== 'reverse-completion') failPythonProject('explicit recovery semantics');
    const calls = (value: unknown, id: string) => {if (!Array.isArray(value)) return failPythonProject('authored calls'); return value.map(v => ({...closed(v, [id, 'arguments', 'events']), action_sha256: '0'.repeat(64)}));};
    const checked = decodeWorkflowBindings({schema_version: WORKFLOW_BINDINGS_VERSION, selector: w.selector, inputs: w.inputs, event_inputs: w.event_inputs, steps: calls(w.steps, 'step_id'), compensations: calls(w.compensations, 'compensation_id'), result: w.result});
    const strip = <T extends {action_sha256: string}>(call: T) => {const {action_sha256, ...body} = call; return body;};
    return {selector: checked.selector, inputs: checked.inputs, event_inputs: checked.event_inputs, steps: checked.steps.map(strip), compensations: checked.compensations.map(strip), result: checked.result, recovery: {dependency_semantics: 'needed-compensations-only' as const, tie_break: 'reverse-completion' as const}};
  });
  return freezePythonProject({...structuredClone(row), operations, workflows} as unknown as ReconciledPythonSelection);
}
