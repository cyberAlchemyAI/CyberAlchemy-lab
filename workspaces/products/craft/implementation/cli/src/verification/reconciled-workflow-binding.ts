import path from 'node:path';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../input/composition-boundary.js';
import {compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../typed-operation/workflow-bindings.js';
import {selectWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_POLICY_VERSION, WORKFLOW_RECOVERY_CONTRACT_SHA256} from '../typed-operation/workflow-recovery.js';
import {decodeWorkflowOccurrences, workflowOperationRefs, freezeWorkflow} from '../typed-backend/workflow-occurrences.js';
import {planConfiguredOperations, CONFIGURED_OPERATION_VERSION} from '../generation/configured-operations.js';
import {WORKFLOW_GENERATION_CONTRACT_SHA256} from '../generation/configured-workflows.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createOperationBinding} from './reconciled-operation-binding.js';

export const SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256 = '7eb375db34a5163f85b2085228c53c8e7820069fc9821522faa1115bdc2e4ae6';
const fail = (message: string): never => {throw new TypeError('WORKFLOW_BINDING:' + message);};
const equal = (a: unknown, b: unknown, message: string) => {if (canonicalJson(a) !== canonicalJson(b)) fail(message);};

/** Metadata binding only: expected execution belongs to the independent references.
 * Rebuilding the Operation dependency plan supplies its aggregate hash, not behavior.
 */
export function createWorkflowBinding(node: CompiledProjectGraph['nodes'][number], graph: CompiledProjectGraph, plan: ReconciledProjectPlan, definition: string) {
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plan);
  if (typeof definition !== 'string' || sha256(definition) !== SEMANTIC_WORKFLOW_BINDING_DEFINITION_SHA256) fail('definition drift');
  if (node.kind !== 'Workflow' || !graph.nodes.includes(node)) fail('source Workflow required');
  const certificate = createCompiledProjectCertificate(graph);
  equal(plan.resolved.certificate, certificate, 'cross-graph plan');
  const authored = plan.selection.workflows.find(w => w.selector === node.selector) ?? fail('authored Workflow missing');
  const declared = decodeWorkflowOccurrences(node.body.typed_contract), refs = workflowOperationRefs(declared);
  const operations = refs.map(selector => createOperationBinding(graph.nodes.find(n => n.selector === selector) ?? fail('Operation missing'), graph, plan));
  const fields = operations[0]?.fields ?? null, actions = operations.map(o => o.action);
  const source = getReconciledSource;
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, source('composition'));
  const actionHash = (selector: string) => operations.find(o => o.action.bindings.selector === selector)?.action.action_sha256 ?? fail('source action missing');
  const {recovery, ...bindings} = authored;
  const workflow = compileWorkflowBindings(graph, boundary, fields, actions, {...bindings, schema_version: WORKFLOW_BINDINGS_VERSION,
    steps: authored.steps.map(call => ({...call, action_sha256: actionHash(declared.steps.find(s => s.step_id === call.step_id)?.operation_ref ?? fail('source step missing'))})),
    compensations: authored.compensations.map(call => ({...call, action_sha256: actionHash(declared.compensations.find(s => s.compensation_id === call.compensation_id)?.operation_ref ?? fail('source compensation missing'))}))
  }, source('workflow_binding'));
  const policy = selectWorkflowRecoveryPolicy(workflow, {schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256, contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, ...recovery}, source('workflow_recovery'));
  const selected = plan.resolved.requests.filter(r => r.kind === 'workflows').map(r => r.selection as unknown as {workflow: typeof workflow; policy: typeof policy; actions: typeof actions}).filter(s => s.workflow.bindings.selector === node.selector);
  if (selected.length !== 1) fail('exact selected Workflow missing');
  equal(selected[0]!.workflow, workflow, 'selected Workflow mismatch'); equal(selected[0]!.policy, policy, 'selected recovery mismatch');
  const orderedActions = (rows: typeof actions) => [...rows].sort((a, b) => a.bindings.selector < b.bindings.selector ? -1 : a.bindings.selector > b.bindings.selector ? 1 : 0);
  equal(orderedActions(selected[0]!.actions), orderedActions(actions), 'selected action closure mismatch');

  const common = {configuration: source('configuration'), base: source('base'), typescript: source('typescript')};
  const rules = {...common, rule_contract: source('rule'), collection_contract: source('rule_collection'), predicate_contract: source('rule_predicate'), numeric_contract: source('rule_numeric'), exact_contract: source('rule_exact'), literal_contract: source('rule_literal'), structured_contract: source('rule_structured'), field_contract: source('field')};
  const operationPlan = planConfiguredOperations(graph, boundary, fields, {schema_version: CONFIGURED_OPERATION_VERSION, language: 'typescript', module_root: plan.selection.module_root, actions, factories: plan.selection.factories}, {
    operation_contract: source('operation'), factory_contract: source('factory'), enum_provider: source('enum_provider'), rules, events: {...common, event_contract: source('event')}
  });
  // A dependency planner never substitutes for independently checked Operation meaning.
  for (const operation of operations) {
    const module = operationPlan.modules.find(m => m.selector === operation.action.bindings.selector) ?? fail('dependency module missing');
    equal(module.descriptor, operation.descriptor, 'dependency descriptor mismatch');
    if (module.callable !== operation.callable || module.relative_path !== operation.relative_path) fail('dependency callable mismatch');
  }
  const role = JSON.parse(source('configuration')).types.find((t: {kind: string}) => t.kind === 'Workflow').role;
  const relative_path = plan.selection.module_root + '/features/' + node.feature_id + '/src/' + role + '/' + node.node_id + '.ts';
  const provider_path = relative_path.replace(/\.ts$/, '.provider.ts'), material_path = relative_path.replace(/\.ts$/, '.material.ts');
  const callable = 'workflow' + node.node_id.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
  const ownPaths = [relative_path, provider_path, material_path];
  const artifact = (p: string) => {
    const a = plan.resolved.artifacts.find(a => a.relative_path === p) ?? fail('artifact missing:' + p);
    if (a.sha256 !== sha256(a.content) || a.size_bytes !== Buffer.byteLength(a.content)) fail('artifact byte drift:' + p);
    return a;
  };
  const forward = [...new Set(workflow.steps.map(s => s.operation_ref))].sort().map(s => operations.find(o => o.action.bindings.selector === s)!);
  const allowed = new Set([...ownPaths, ...forward.flatMap(o => o.module_paths)]);
  const paths = new Set<string>();
  const visit = (p: string): void => {
    if (paths.has(p)) return;
    if (!allowed.has(p)) fail('foreign forward dependency:' + p);
    paths.add(p); const a = artifact(p);
    const m = plan.resolved.modules.find(m => m.relative_path === p) ?? fail('native module missing:' + p);
    if (m.sha256 !== a.sha256) fail('module byte drift:' + p);
    if (ownPaths.includes(p)) equal(m.qualified_selectors, [node.selector], 'Workflow module ownership');
    if (p === relative_path && !m.exports.some(e => e.name === callable && e.kind === 'value')) fail('callable identity');
    for (const i of m.imports) {
      if (i.target_path === null) {
        if (p !== provider_path || i.specifier !== 'node:crypto' || canonicalJson(i.names) !== '["createHash"]' || i.namespace || i.type_only || i.reexport || i.dependency !== 'node-standard-library') fail('external native dependency');
      } else {
        if (i.target_sha256 !== artifact(i.target_path).sha256) fail('import byte drift');
        visit(i.target_path);
      }
    }
  };
  visit(relative_path);
  equal([...paths].sort(), [...allowed].sort(), 'exact forward closure');
  const rel = (target: string) => {const p = path.posix.relative(path.posix.dirname(provider_path), target).replace(/\.ts$/, '.js'); return p.startsWith('.') ? p : './' + p;};
  const imports = forward.map((o, i) => ({selector: o.action.bindings.selector, path: rel(o.relative_path), symbol: o.callable, local: 'forward' + i, action_sha256: o.action.action_sha256, descriptor_sha256: o.descriptor.descriptor_sha256}));
  const providerImports = plan.resolved.modules.find(m => m.relative_path === provider_path)!.imports;
  for (const o of forward) {
    const rows = providerImports.filter(i => i.target_path === o.relative_path && !i.type_only && !i.reexport);
    if (rows.length !== 1 || rows[0]!.namespace || canonicalJson(rows[0]!.names) !== canonicalJson([o.callable])) fail('forward callable import');
  }
  const descriptor = {schema_version: 'domainspec.generated-workflow-descriptor/v1-candidate', protocol_id: 'typescript.bound-workflow/v1', form_id: 'typescript.workflow-step-orchestrator', primary_callable_count: 1,
    selector: node.selector, workflow_sha256: workflow.workflow_sha256, policy_sha256: policy.policy_sha256, contract_sha256: WORKFLOW_GENERATION_CONTRACT_SHA256,
    material_sha256: artifact(material_path).sha256, provider_sha256: artifact(provider_path).sha256, operation_plan_sha256: operationPlan.plan_sha256, operation_imports: imports,
    compensation_execution: false, publication: false, authority_effect: 'none'};
  return freezeWorkflow({workflow, policy, fields, operations, descriptor: {...descriptor, descriptor_sha256: sha256(canonicalJson(descriptor))}, callable, relative_path, provider_path, material_path,
    module_paths: [...paths].sort(), native_imports: [...paths].sort().map(relative_path => ({relative_path, imports: plan.resolved.modules.find(m => m.relative_path === relative_path)!.imports.map(i => ({specifier: i.specifier, target_path: i.target_path}))}))});
}
