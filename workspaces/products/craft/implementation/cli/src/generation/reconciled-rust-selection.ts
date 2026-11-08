import {assertInterfaceData} from '../typed-backend/interface.js';
import {canonicalJson} from '../input/source-manifest.js';
import {decodeOperationActionBindings, type OperationActionBindings} from '../typed-operation/action-bindings.js';
import {decodeWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../typed-operation/workflow-bindings.js';
import type {ProjectFieldSelection} from '../input/compiled-field-model.js';
import type {FactoryBinding} from './configured-factories.js';
import type {ReconciledWorkflowBinding} from './reconciled-project.js';
import {RESOLVED_ARTIFACT_LAYOUT} from './resolved-artifact-plan.js';
import {rustSnake} from './configured-rust-values.js';

export const RECONCILED_RUST_COMPILATION_VERSION = 'domainspec.reconciled-rust-compilation/v1-candidate';
export const RECONCILED_RUST_PROFILE = 'domainspec.reconciled-rust/v1-candidate';
export interface ReconciledRustSelection {
  readonly schema_version: typeof RECONCILED_RUST_COMPILATION_VERSION;
  readonly profile_id: typeof RECONCILED_RUST_PROFILE;
  readonly language: 'rust';
  readonly module_root: string;
  readonly layout_version: typeof RESOLVED_ARTIFACT_LAYOUT;
  readonly field_bindings: ProjectFieldSelection['bindings'];
  readonly factories: readonly FactoryBinding[];
  readonly operations: readonly OperationActionBindings[];
  readonly workflows: readonly ReconciledWorkflowBinding[];
}
export const failRustProject = (message: string): never => {throw new TypeError('DS_RECONCILED_RUST:' + message);};
export function freezeRustProject<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freezeRustProject); Object.freeze(value);} return value;}
function closed(value: unknown, keys: readonly string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || canonicalJson(Object.keys(value).sort()) !== canonicalJson([...keys].sort())) failRustProject('closed selection fields');
  return value as Record<string, unknown>;
}
export function decodeReconciledRustSelection(value: unknown): ReconciledRustSelection {
  assertInterfaceData(value);
  const row = closed(value, ['schema_version', 'profile_id', 'language', 'module_root', 'layout_version', 'field_bindings', 'factories', 'operations', 'workflows']);
  if (row.schema_version !== RECONCILED_RUST_COMPILATION_VERSION || row.profile_id !== RECONCILED_RUST_PROFILE || row.language !== 'rust' || row.layout_version !== RESOLVED_ARTIFACT_LAYOUT) failRustProject('explicit Rust selection required');
  if (typeof row.module_root !== 'string' || row.module_root.length > 256) failRustProject('bounded module root');
  (row.module_root as string).split('/').forEach(rustSnake);
  for (const key of ['field_bindings', 'factories', 'operations', 'workflows']) if (!Array.isArray(row[key]) || (row[key] as unknown[]).length > 256) failRustProject('bounded binding array:' + key);
  for (const factory of row.factories as unknown[]) {const item = closed(factory, ['selector', 'base_validators', 'extensions']); if (typeof item.selector !== 'string' || !Array.isArray(item.base_validators) || !Array.isArray(item.extensions)) failRustProject('authored factory binding');}
  const operations = (row.operations as unknown[]).map(decodeOperationActionBindings);
  const workflows = (row.workflows as unknown[]).map(value => {
    const workflow = closed(value, ['selector', 'inputs', 'event_inputs', 'steps', 'compensations', 'result', 'recovery']);
    const recovery = closed(workflow.recovery, ['dependency_semantics', 'tie_break']);
    if (recovery.dependency_semantics !== 'needed-compensations-only' || recovery.tie_break !== 'reverse-completion') failRustProject('explicit recovery semantics');
    const calls = (input: unknown, id: string) => {if (!Array.isArray(input)) return failRustProject('authored calls'); return input.map(call => ({...closed(call, [id, 'arguments', 'events']), action_sha256: '0'.repeat(64)}));};
    const checked = decodeWorkflowBindings({schema_version: WORKFLOW_BINDINGS_VERSION, selector: workflow.selector, inputs: workflow.inputs, event_inputs: workflow.event_inputs, steps: calls(workflow.steps, 'step_id'), compensations: calls(workflow.compensations, 'compensation_id'), result: workflow.result});
    const strip = <T extends {action_sha256: string}>(call: T) => {const {action_sha256, ...body} = call; return body;};
    return {selector: checked.selector, inputs: checked.inputs, event_inputs: checked.event_inputs, steps: checked.steps.map(strip), compensations: checked.compensations.map(strip), result: checked.result, recovery: {dependency_semantics: 'needed-compensations-only' as const, tie_break: 'reverse-completion' as const}};
  });
  return freezeRustProject({...structuredClone(row), operations, workflows} as unknown as ReconciledRustSelection);
}

