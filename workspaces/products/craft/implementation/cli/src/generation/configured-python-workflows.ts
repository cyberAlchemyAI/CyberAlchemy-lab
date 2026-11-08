import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertCheckedWorkflowBindings, type CheckedWorkflowBindings} from '../typed-operation/workflow-bindings.js';
import {assertCheckedWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_CONTRACT_SHA256, type CheckedWorkflowRecoveryPolicy} from '../typed-operation/workflow-recovery.js';
import {WORKFLOW_OUTCOME_CONTRACT_SHA256} from '../typed-operation/workflow-outcomes.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {freezeWorkflow, workflowObject} from '../typed-backend/workflow-occurrences.js';
import {planConfiguredPythonOperations, PYTHON_OPERATION_VERSION, type PythonOperationSelection, type PythonOperationSources} from './configured-python-operations.js';
import {WORKFLOW_GENERATION_CONTRACT_SHA256} from './configured-workflows.js';
import {planPythonWorkflowMaterialization} from './python-workflow-materialization.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {renderPythonWorkflow, renderPythonWorkflowBinding} from './configured-python-workflow-source.js';
import type {PlannedArtifact} from './contracts.js';

export const PYTHON_WORKFLOW_VERSION = 'domainspec.configured-python-workflow-selection/v1-candidate';
export interface PythonWorkflowSelection {
  readonly schema_version: typeof PYTHON_WORKFLOW_VERSION; readonly language: 'python'; readonly module_root: string;
  readonly workflow: CheckedWorkflowBindings; readonly policy: CheckedWorkflowRecoveryPolicy;
  readonly actions: PythonOperationSelection['actions']; readonly factories: PythonOperationSelection['factories'];
}
export interface PythonWorkflowSources {
  readonly workflow_contract: string; readonly materialization_contract: string; readonly outcome_contract: string; readonly recovery_contract: string;
  readonly operations: PythonOperationSources;
}
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_WORKFLOW:' + reason);};
function closed(value: unknown, keys: readonly string[]) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('inert object');
  const d = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(d).some(k => typeof k !== 'string' || !keys.includes(k)) || Object.values(d).some(p => !Object.hasOwn(p, 'value') || !p.enumerable)) fail('inert fields');
  workflowObject(value, keys);
}

/** Source-only native orchestration; recovery remains separately prepared data. */
export function planConfiguredPythonWorkflow(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields | null, selection: PythonWorkflowSelection, sources: PythonWorkflowSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); if (fields !== null) assertCompiledProjectFields(fields);
  closed(selection, ['schema_version', 'language', 'module_root', 'workflow', 'policy', 'actions', 'factories']);
  closed(sources, ['workflow_contract', 'materialization_contract', 'outcome_contract', 'recovery_contract', 'operations']);
  if (selection.schema_version !== PYTHON_WORKFLOW_VERSION || selection.language !== 'python') fail('selection');
  const workflow = selection.workflow, policy = selection.policy; assertCheckedWorkflowBindings(workflow); assertCheckedWorkflowRecoveryPolicy(policy);
  if (policy.workflow !== workflow) fail('policy Workflow identity');
  const certificate = createCompiledProjectCertificate(graph);
  if (workflow.certificate.graph_sha256 !== certificate.graph_sha256 || workflow.boundary_sha256 !== boundary.boundary_sha256 || workflow.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null)) fail('stale Workflow');
  for (const [source, hash] of [[sources.workflow_contract, WORKFLOW_GENERATION_CONTRACT_SHA256], [sources.outcome_contract, WORKFLOW_OUTCOME_CONTRACT_SHA256], [sources.recovery_contract, WORKFLOW_RECOVERY_CONTRACT_SHA256]])
    if (typeof source !== 'string' || sha256(source) !== hash) fail('definition drift');
  const operationPlan = planConfiguredPythonOperations(graph, boundary, fields, {schema_version: PYTHON_OPERATION_VERSION, language: 'python', module_root: selection.module_root, actions: selection.actions, factories: selection.factories}, sources.operations);
  const required = new Map([...workflow.steps, ...workflow.compensations].map(s => [s.operation_ref, s.action_sha256]));
  if (operationPlan.modules.length !== required.size || operationPlan.modules.some(m => required.get(m.selector) !== m.descriptor.action_sha256)) fail('exact action closure');
  const material = planPythonWorkflowMaterialization(graph, workflow, fields, sources.materialization_contract, selection.module_root);
  const cell = JSON.parse(sources.operations.rules.configuration).types.find((t: {kind: string}) => t.kind === 'Workflow');
  if (cell?.role !== 'application/workflows' || canonicalJson(cell.blocked_by) !== '["DSR-011","DSR-017"]') fail('Workflow role');
  const overlay = JSON.parse(sources.operations.rules.python).representation_overlays.find((o: {contract_id: string}) => o.contract_id === 'workflow.profile-representation');
  if (overlay?.candidate_protocols.find((p: {protocol_id: string}) => p.protocol_id === 'python.bound-workflow/v1')?.form_id !== 'python.workflow-step-orchestrator') fail('Workflow protocol');
  const [feature, id] = workflow.bindings.selector.split(':') as [string, string];
  const relative_path = `${material.module_root}/features/${pythonSnake(feature)}/src/application/workflows/${pythonSnake(id)}.py`, provider_path = relative_path.replace(/\/([^/]+)\.py$/, '/_providers/$1.py');
  const artifacts = new Map<string, PlannedArtifact>();
  const add = (relative_path: string, content: string) => {
    const prior = artifacts.get(relative_path); if (prior && prior.content !== content) fail('artifact collision:' + relative_path);
    const a = {relative_path, content, sha256: sha256(content), size_bytes: Buffer.byteLength(content)}; artifacts.set(relative_path, a); return a;
  };
  [...operationPlan.artifacts, ...material.artifacts].forEach(a => add(a.relative_path, a.content));
  const imports = [...new Set(workflow.steps.map(s => s.operation_ref))].sort().map((selector, i) => {
    const m = operationPlan.modules.find(m => m.selector === selector)!;
    return {selector, module: pythonRelativeModule(provider_path, m.relative_path), symbol: m.callable, local: '_forward' + i, action_sha256: m.descriptor.action_sha256, descriptor_sha256: m.descriptor.descriptor_sha256};
  });
  const rendered = renderPythonWorkflow(workflow, policy, pythonRelativeModule(provider_path, material.relative_path), imports);
  const provider = add(provider_path, rendered);
  const body = {schema_version: 'domainspec.generated-python-workflow-descriptor/v1-candidate', protocol_id: 'python.bound-workflow/v1', form_id: 'python.workflow-step-orchestrator', primary_callable_count: 1,
    selector: workflow.bindings.selector, workflow_sha256: workflow.workflow_sha256, policy_sha256: policy.policy_sha256,
    contract_sha256: WORKFLOW_GENERATION_CONTRACT_SHA256, material_sha256: material.provider_sha256, provider_sha256: provider.sha256,
    operation_plan_sha256: operationPlan.plan_sha256, operation_imports: imports, compensation_execution: false, publication: false, authority_effect: 'none'};
  const descriptor = freezeWorkflow({...body, descriptor_sha256: sha256(canonicalJson(body))}), callable = 'workflow_' + pythonSnake(id);
  add(relative_path, renderPythonWorkflowBinding(pythonRelativeModule(relative_path, provider_path), callable, descriptor));
  for (const file of [...artifacts.keys()]) {const parts = file.split('/'); for (let i = 1; i < parts.length; i++) {const init = parts.slice(0, i).join('/') + '/__init__.py'; if (!artifacts.has(init)) add(init, '');}}
  const plan = {schema_version: 'domainspec.configured-python-workflow-plan/v1-candidate', selection: {...selection, actions: operationPlan.selection.actions, factories: operationPlan.selection.factories}, certificate,
    operation_plan: operationPlan, materialization: material, modules: [{selector: workflow.bindings.selector, relative_path, provider_path, material_path: material.relative_path, import_name: relative_path.slice(0, -3).replaceAll('/', '.'), callable, descriptor}],
    artifacts: [...artifacts.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none'};
  return freezeWorkflow({...plan, plan_sha256: sha256(canonicalJson(plan))});
}
