import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {MappingControls} from './reconciled-mapping-controls.js';
import type {SemanticCase} from './reconciled-semantic-controls.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {createWorkflowBinding, SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256} from './reconciled-workflow-binding.js';
import {createWorkflowCases, isWorkflowCasesCapacity, WORKFLOW_CASES_DEFINITION_SHA256} from './reconciled-workflow-cases.js';
import {WORKFLOW_CONTROLS_DEFINITION_SHA256} from './reconciled-workflow-outcome-reference.js';
import {WORKFLOW_VALUES_DEFINITION_SHA256} from './reconciled-workflow-value-reference.js';
import {WORKFLOW_EXECUTION_DEFINITION_SHA256} from './reconciled-workflow-execution-reference.js';
import {WORKFLOW_EFFECT_AUDIT_DEFINITION_SHA256} from './reconciled-workflow-effect-audit.js';
import {WORKFLOW_ORCHESTRATION_DEFINITION_SHA256} from './reconciled-workflow-orchestration-audit.js';

export const SEMANTIC_WORKFLOW_DEFINITION_SHA256 = 'ff1eb6b45e799aac5afa4cb604aec194d94e61058626d3789080683ac4526287';
export interface WorkflowControls extends Omit<MappingControls, 'kind' | 'adapter' | 'native_imports'> {
  readonly kind: 'Workflow'; readonly adapter: 'workflow'; readonly provider_path: string;
  readonly workflow_steps: readonly {step_id: string; operation_ref: string}[];
  readonly native_imports: readonly {relative_path: string; imports: readonly {specifier: string; target_path: string | null}[]}[];
  readonly coverage: Readonly<Record<string, string>>;
  readonly search: Readonly<{attempts: number; success_case_id: string}>;
}
export function workflowVerificationDefinitions() {
  const values = {
    binding: getReconciledSource('semantic_workflow_binding'), outcomes: getReconciledSource('semantic_workflow_outcomes'),
    values: getReconciledSource('semantic_workflow_values'), execution: getReconciledSource('semantic_workflow_execution'),
    cases: getReconciledSource('semantic_workflow_cases'), effects: getReconciledSource('workflow_effect_audit'),
    orchestration: getReconciledSource('workflow_orchestration_audit'), public: getReconciledSource('semantic_workflow_controls')
  };
  const pins = {binding: SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256, outcomes: WORKFLOW_CONTROLS_DEFINITION_SHA256,
    values: WORKFLOW_VALUES_DEFINITION_SHA256, execution: WORKFLOW_EXECUTION_DEFINITION_SHA256, cases: WORKFLOW_CASES_DEFINITION_SHA256,
    effects: WORKFLOW_EFFECT_AUDIT_DEFINITION_SHA256, orchestration: WORKFLOW_ORCHESTRATION_DEFINITION_SHA256, public: SEMANTIC_WORKFLOW_DEFINITION_SHA256};
  for (const key of Object.keys(values) as (keyof typeof values)[]) if (sha256(values[key]) !== pins[key]) throw new TypeError('WORKFLOW_CONTROLS:definition drift:' + key);
  return Object.freeze(values);
}
export function createWorkflowControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledProjectPlan): WorkflowControls | Readonly<{selector: string; kind: 'Workflow'; state: 'not_evaluable'; reason: string}> {
  try {
    const definitions = workflowVerificationDefinitions(), binding = createWorkflowBinding(node, graph, plan, definitions.binding);
    const {binding: bindingSource, execution, values, outcomes} = definitions;
    const control = createWorkflowCases(node, graph, plan, {binding: bindingSource, execution, values, outcomes}, definitions.cases);
    const descriptor: SemanticCase = {id: 'binding', mode: 'workflow-descriptor', format: 'string', values: [], expected: {kind: 'value', value: canonicalJson(binding.descriptor)}};
    const row: WorkflowControls = {
      selector: node.selector, kind: 'Workflow', state: 'ready', adapter: 'workflow',
      contract_sha256: sha256(canonicalJson({bindings: binding.workflow.bindings, policy_sha256: binding.policy.policy_sha256})),
      relative_path: binding.relative_path, callable: binding.callable, provider_path: binding.provider_path, module_paths: binding.module_paths,
      native_imports: binding.native_imports, workflow_steps: binding.workflow.steps.map(s => ({step_id: s.step_id, operation_ref: s.operation_ref})),
      names: [...binding.workflow.bindings.inputs.map(i => i.name), ...binding.workflow.event_inputs.map(e => e.name)],
      cases: [descriptor, ...control.cases], recipes: control.recipes, coverage: control.coverage, search: control.search
    };
    if (row.cases.length > 4096 || Buffer.byteLength(canonicalJson(row)) > 8388608) return {selector: node.selector, kind: 'Workflow', state: 'not_evaluable', reason: 'bounded Workflow whole control capacity exceeded'};
    return freezeWorkflow(row);
  } catch (error) {
    if (isWorkflowCasesCapacity(error)) return {selector: node.selector, kind: 'Workflow', state: 'not_evaluable', reason: error.message};
    throw error;
  }
}
