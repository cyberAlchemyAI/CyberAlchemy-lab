import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertReconciledPythonProjectPlan, getPythonWorkflowVerificationContext, getPythonOperationVerificationContext, getPythonEventVerificationContext, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createBoundWorkflowExecutionReference} from './reconciled-workflow-execution-reference.js';
import {createWorkflowSemanticCases, isWorkflowCasesCapacity} from './reconciled-workflow-cases.js';
import {workflowVerificationDefinitions} from './reconciled-workflow-controls.js';
import {createPythonOwnedValueContext} from './reconciled-python-value-context.js';

export function createPythonWorkflowControls(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledPythonProjectPlan) {
  assertCompiledProjectSnapshot(graph); assertReconciledPythonProjectPlan(plan);
  const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_WORKFLOW_CONTROLS:' + reason);};
  if (node.kind !== 'Workflow' || !graph.nodes.includes(node) || canonicalJson(createCompiledProjectCertificate(graph)) !== canonicalJson(plan.certificate)) fail('graph/plan identity');
  const context = getPythonWorkflowVerificationContext(plan).find(c => c.workflow.bindings.selector === node.selector) ?? fail('checked Workflow missing');
  const {workflow, policy, actions, materialization, operation_plan_sha256} = context, module = context.modules[0]!;
  if (module.descriptor.workflow_sha256 !== workflow.workflow_sha256 || module.descriptor.policy_sha256 !== policy.policy_sha256 ||
      module.descriptor.operation_plan_sha256 !== operation_plan_sha256 || module.descriptor.material_sha256 !== materialization.provider_sha256) fail('native binding');
  const operation_modules = getPythonOperationVerificationContext(plan).modules.filter(m => actions.some(a => a.bindings.selector === m.selector));
  if (operation_modules.length !== actions.length || operation_modules.some(m => actions.find(a => a.bindings.selector === m.selector)!.action_sha256 !== m.descriptor.action_sha256)) fail('native action closure');
  try {
    const d = workflowVerificationDefinitions();
    const oracle = createBoundWorkflowExecutionReference(graph, workflow, policy, actions, plan.selection.factories,
      {execution: d.execution, values: d.values, outcomes: d.outcomes}, 'native-explicit');
    const shared = createWorkflowSemanticCases(graph, oracle, plan.selection.factories, selector => createPythonOwnedValueContext(selector, graph, plan), d.cases);
    const cases = [...shared.cases];
    for (const step of workflow.steps) for (const phase of ['begin', 'read', 'commit', 'rollback']) {
      const source = cases.find(c => c.mode === 'workflow' && JSON.parse((c.expected as {value: string}).value).port_trace.some((s: string) =>
        phase === 'read' ? s.startsWith(step.step_id + ':read:') && s.endsWith('-rejected') : s === step.step_id + ':' + phase + '-rejected'));
      if (source) cases.push({...source, id: 'native-cancel-' + step.step_id + '-' + phase, mode: 'workflow-native-cancel',
        values: [canonicalJson({...JSON.parse(source.values[0]!), cancel: {step_id: step.step_id, phase}})]});
    }
    const event_selectors = new Set([...actions.flatMap(a => a.events.map(e => e.target)), ...workflow.event_inputs.map(e => e.event_ref)]);
    const event_modules = getPythonEventVerificationContext(plan).filter(m => event_selectors.has(m.selector));
    const selectors = new Set([node.selector, ...actions.map(a => a.bindings.selector), ...actions.flatMap(a => a.guards.map(g => g.selector)),
      ...event_modules.map(m => m.selector), ...event_modules.flatMap(m => m.descriptor.references.map(r => r.selector))]);
    const row = {selector: node.selector, kind: 'Workflow' as const, state: 'ready' as const, adapter: 'python-workflow' as const,
      module, workflow, policy: {policy_sha256: policy.policy_sha256}, actions, materialization, operation_plan_sha256, operation_modules, event_modules,
      contract_sha256: sha256(canonicalJson({bindings: workflow.bindings, policy_sha256: policy.policy_sha256})), recipes: shared.recipes,
      cases: [{id: 'binding', mode: 'workflow-descriptor', format: 'string' as const, values: [], expected: {kind: 'value' as const, value: canonicalJson(module.descriptor)}}, ...cases],
      coverage: shared.coverage, search: shared.search,
      nodes: Object.fromEntries(graph.nodes.filter(n => selectors.has(n.selector)).map(n => [n.selector, {kind: n.kind, body: n.body}]))};
    if (row.cases.length > 4096 || Buffer.byteLength(canonicalJson(row)) > 8388608) return {selector: node.selector, kind: 'Workflow' as const, state: 'not_evaluable' as const, reason: 'bounded native Workflow whole control capacity exceeded'};
    return row;
  } catch (error) {
    if (isWorkflowCasesCapacity(error)) return {selector: node.selector, kind: 'Workflow' as const, state: 'not_evaluable' as const, reason: error.message};
    throw error;
  }
}
