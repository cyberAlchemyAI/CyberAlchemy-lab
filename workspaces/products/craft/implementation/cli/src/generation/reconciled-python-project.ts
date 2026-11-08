import {assertCompiledProjectSnapshot, loadCompiledProjectGraph, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_VERSION, COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../input/composition-boundary.js';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {compileOperationActionBindings} from '../typed-operation/action-bindings.js';
import {compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../typed-operation/workflow-bindings.js';
import {selectWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_POLICY_VERSION, WORKFLOW_RECOVERY_CONTRACT_SHA256} from '../typed-operation/workflow-recovery.js';
import {decodeWorkflowOccurrences, workflowOperationRefs} from '../typed-backend/workflow-occurrences.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {getReconciledSource as source, getReconciledSourceCapsule} from './reconciled-sources.js';
import {decodeReconciledPythonSelection, failPythonProject as fail, freezePythonProject as freeze} from './reconciled-python-selection.js';
import {reconciledPythonSources} from './reconciled-python-sources.js';
import {resolvePythonModules, selectPythonModuleClosure} from './resolved-python-modules.js';
import {pythonSnake} from './configured-python-owned-values.js';
import {planConfiguredPythonFactories, PYTHON_FACTORY_VERSION, PYTHON_REFERENCE_FACTORY_VERSION} from './configured-python-factories.js';
import {planConfiguredPythonAlgebraicEnums, PYTHON_ALGEBRAIC_ENUM_VERSION} from './configured-python-algebraic-enums.js';
import {planConfiguredPythonRules, PYTHON_STRUCTURED_RULE_VERSION} from './configured-python-rules.js';
import {planConfiguredPythonCalculations, PYTHON_CALCULATION_VERSION} from './configured-python-calculations.js';
import {planConfiguredPythonQueries, PYTHON_QUERY_VERSION} from './configured-python-queries.js';
import {planConfiguredPythonMappings, PYTHON_MAPPING_VERSION} from './configured-python-mappings.js';
import {planConfiguredPythonPolicies, PYTHON_POLICY_VERSION} from './configured-python-policies.js';
import {planConfiguredPythonEvents, PYTHON_EVENT_VERSION} from './configured-python-events.js';
import {EVENT_VALUE_PROFILE} from './configured-events.js';
import {planConfiguredPythonOperations, PYTHON_OPERATION_VERSION} from './configured-python-operations.js';
import {planConfiguredPythonWorkflow, PYTHON_WORKFLOW_VERSION} from './configured-python-workflows.js';
import {planConfiguredPythonStateMachines, PYTHON_STATE_MACHINE_VERSION} from './configured-python-state-machines.js';
import {planConfiguredPythonInterfaces, PYTHON_INTERFACE_VERSION} from './configured-python-interfaces.js';
import {planConfiguredPythonPublicMappings, PYTHON_PUBLIC_MAPPING_VERSION} from './configured-python-public-mappings.js';
import type {PlannedArtifact} from './contracts.js';

export const PYTHON_PROJECT_DEFINITION_SHA256 = '3519dd88ec21dc9d7cbaf2e480f5cf9ed9911345f1ebc054a78c225768f80888';
const checked = new WeakSet<object>();
type FactoryModules = ReturnType<typeof planConfiguredPythonFactories>['modules'];
const factoryContexts = new WeakMap<object, FactoryModules>();
export function getPythonFactoryVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return factoryContexts.get(plan)!;
}
type CalculationPlan = ReturnType<typeof planConfiguredPythonCalculations>;
const calculationContexts = new WeakMap<object, Readonly<{modules: CalculationPlan['modules']; contracts: Readonly<Record<string, unknown>>; support_path: string}> | null>();
type QueryModules = ReturnType<typeof planConfiguredPythonQueries>['modules'];
type MappingModules = ReturnType<typeof planConfiguredPythonMappings>['modules'];
type RuleModules = ReturnType<typeof planConfiguredPythonRules>['modules'];
type PolicyModules = ReturnType<typeof planConfiguredPythonPolicies>['modules'];
type EventModules = ReturnType<typeof planConfiguredPythonEvents>['modules'];
type OperationPlan = ReturnType<typeof planConfiguredPythonOperations>;
type WorkflowPlan = ReturnType<typeof planConfiguredPythonWorkflow>;
type WorkflowContext = Readonly<{modules: WorkflowPlan['modules']; workflow: WorkflowPlan['selection']['workflow']; policy: WorkflowPlan['selection']['policy']; actions: WorkflowPlan['selection']['actions'];
  operation_plan_sha256: string; materialization: Pick<WorkflowPlan['materialization'], 'module_root' | 'relative_path' | 'descriptor' | 'provider_sha256'>}>;
const workflowContexts = new WeakMap<object, readonly WorkflowContext[]>();
export function getPythonWorkflowVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return workflowContexts.get(plan)!;
}
const operationContexts = new WeakMap<object, Readonly<{modules: OperationPlan['modules']; actions: OperationPlan['selection']['actions']}>>();
export function getPythonOperationVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return operationContexts.get(plan)!;
}
const eventContexts = new WeakMap<object, EventModules>();
type StateMachineModules = ReturnType<typeof planConfiguredPythonStateMachines>['modules'];
const stateMachineContexts = new WeakMap<object, StateMachineModules>();
type InterfaceModules = ReturnType<typeof planConfiguredPythonInterfaces>['modules'];
const interfaceContexts = new WeakMap<object, InterfaceModules>();
type PublicMappingPlan = ReturnType<typeof planConfiguredPythonPublicMappings>;
const publicMappingContexts = new WeakMap<object, Readonly<{modules: PublicMappingPlan['modules']; mappings: PublicMappingPlan['mappings']}>>();
export function getPythonPublicMappingVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return publicMappingContexts.get(plan)!;
}
export function getPythonInterfaceVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return interfaceContexts.get(plan)!;
}
export function getPythonStateMachineVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return stateMachineContexts.get(plan)!;
}
export function getPythonEventVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return eventContexts.get(plan)!;
}
const decisionContexts = new WeakMap<object, Readonly<{rules: RuleModules; policies: PolicyModules}>>();
export function getPythonDecisionVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return decisionContexts.get(plan)!;
}
const dataContexts = new WeakMap<object, Readonly<{queries: QueryModules; mappings: MappingModules; model: CompiledProjectFields['model'] | null; runtime_dir: string}>>();
export function getPythonDataVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return dataContexts.get(plan)!;
}
/** Private source-bound metadata only: no copied artifacts or plan serialization. */
export function getPythonCalculationVerificationContext(plan: ReconciledPythonProjectPlan) {
  assertReconciledPythonProjectPlan(plan);
  return calculationContexts.get(plan) ?? null;
}
export type ReconciledPythonProjectPlan = ReturnType<typeof planCompiledReconciledPythonProject>;
export function assertReconciledPythonProjectPlan(value: unknown): asserts value is ReconciledPythonProjectPlan {
  if (!value || typeof value !== 'object' || !checked.has(value)) fail('registered Python project required');
}

/** One checked graph, existing domain meaning, native Python adapters only. */
export function planCompiledReconciledPythonProject(graph: CompiledProjectGraph, value: unknown) {
  assertCompiledProjectSnapshot(graph);
  const selection = decodeReconciledPythonSelection(value);
  if (sha256(source('python_project')) !== PYTHON_PROJECT_DEFINITION_SHA256) fail('project definition drift');
  if (graph.compositions?.length) fail('Python cross-project composition adapters are not yet implemented');
  const known = new Set(['Entity', 'Value Object', 'Enum', 'Rule', 'Calculation', 'Policy', 'Query', 'Operation', 'Workflow', 'State Machine', 'Mapping', 'Event', 'Interface']);
  if (!graph.nodes.length || graph.nodes.some(n => !known.has(n.kind))) fail('nonempty supported metatype project required');
  const roots = (kind: string) => graph.nodes.filter(n => n.kind === kind).map(n => n.selector).sort();
  const exact = (actual: readonly string[], expected: readonly string[]) => {if (new Set(actual).size !== actual.length || canonicalJson([...actual].sort()) !== canonicalJson([...expected].sort())) fail('exact authored binding coverage');};
  exact(selection.factories.map(f => f.selector), [...roots('Entity'), ...roots('Value Object')]);
  exact(selection.operations.map(o => o.selector), roots('Operation')); exact(selection.workflows.map(w => w.selector), roots('Workflow'));
  const certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, source('composition'));
  const dataRoots = [...roots('Entity'), ...roots('Value Object'), ...roots('Enum')].sort();
  if (!dataRoots.length && selection.field_bindings.length) fail('field bindings without declarations');
  const fields = dataRoots.length ? compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: dataRoots, bindings: selection.field_bindings}, source('field')) : null;
  const layout = {language: 'python' as const, module_root: selection.module_root};
  const bound = {...layout, boundary_sha256: boundary.boundary_sha256}, typed = {...bound, field_compilation_sha256: fields?.compilation_sha256 ?? null};
  const sources = reconciledPythonSources();
  const files = new Map<string, PlannedArtifact>(), owners = new Map<string, Set<string>>();
  const requests: {kind: string; selection: unknown; child_plan_sha256: string}[] = [];
  const collectOwners = (v: unknown): void => {
    if (!v || typeof v !== 'object') return;
    const row = v as Record<string, unknown>;
    if (typeof row.selector === 'string' && graph.nodes.some(n => n.selector === row.selector)) for (const key of ['relative_path', 'provider_path', 'material_path', 'definition_path']) {
      const p = row[key]; if (typeof p === 'string' && files.has(p)) {const set = owners.get(p) ?? new Set<string>(); set.add(row.selector); owners.set(p, set);}
    }
    Object.values(row).forEach(collectOwners);
  };
  const add = (kind: string, child: {selection: unknown; plan_sha256: string; artifacts: readonly PlannedArtifact[]}) => {
    for (const a of child.artifacts) {const prior = files.get(a.relative_path); if (prior && (prior.content !== a.content || prior.sha256 !== a.sha256)) fail('conflicting generated artifact:' + a.relative_path); files.set(a.relative_path, a);}
    collectOwners(child); requests.push({kind, selection: child.selection, child_plan_sha256: child.plan_sha256});
  };
  let factoryModules: FactoryModules = [];
  if (fields) {
    if (selection.factories.length) {
      const child = planConfiguredPythonFactories(graph, fields, {schema_version: fields.model.bindings.length ? PYTHON_REFERENCE_FACTORY_VERSION : PYTHON_FACTORY_VERSION, ...layout, field_compilation_sha256: fields.compilation_sha256, factories: selection.factories}, {...sources.factories, ...(fields.model.bindings.length ? {reference_contract: source('reference_factory')} : {})});
      add('factories', child); factoryModules = child.modules;
    }
    else add('algebraic-enums', planConfiguredPythonAlgebraicEnums(graph, fields, {schema_version: PYTHON_ALGEBRAIC_ENUM_VERSION, ...layout, field_compilation_sha256: fields.compilation_sha256}, {...sources.common, field_contract: source('field')}));
    // Factory planners also emit Enum closure; those modules are not repeated in
    // factory metadata, so bind their canonical adapter paths explicitly.
    for (const d of fields.model.declarations) if (d.kind === 'Enum') {
      const [feature, node] = d.selector.split(':') as [string, string];
      const p = selection.module_root.split('/').map(pythonSnake).join('/') + '/features/' + pythonSnake(feature) + '/src/domain/enums/' + pythonSnake(node) + (d.contract.variants.some(v => v.payload !== null) ? '_sum' : '') + '.py';
      if (!files.has(p)) fail('missing generated Enum:' + d.selector); owners.set(p, new Set([d.selector]));
    }
  }
  let ruleModules: RuleModules = [], policyModules: PolicyModules = [];
  if (roots('Rule').length) {
    const child = planConfiguredPythonRules(graph, {schema_version: PYTHON_STRUCTURED_RULE_VERSION, ...layout, roots: roots('Rule')}, sources.rules);
    add('rules', child); ruleModules = child.modules;
  }
  let calculationContext: ReturnType<typeof getPythonCalculationVerificationContext> = null;
  if (roots('Calculation').length) {
    const child = planConfiguredPythonCalculations(boundary, {schema_version: PYTHON_CALCULATION_VERSION, ...bound, roots: roots('Calculation')}, {...sources.common, calculation_contract: source('calculation_v1'), exact_calculation_contract: source('calculation_v2')});
    add('calculations', child);
    calculationContext = freeze({modules: child.modules, contracts: Object.fromEntries(boundary.value_bindings.core_contracts.filter(c => c.kind === 'Calculation').map(c => [c.owner.selector, c.contract])), support_path: child.artifacts.find(a => a.relative_path.endsWith('/runtime/calculations.py'))!.relative_path});
  }
  const domainMappings = graph.nodes.filter(n => n.kind === 'Mapping' && (n.body.typed_contract as {schema_version?: string}|undefined)?.schema_version !== 'domainspec.typed-mapping/v3').map(n => n.selector).sort();
  let queryModules: QueryModules = [], mappingModules: MappingModules = [];
  if (roots('Query').length || domainMappings.length) {
    if (!fields) return fail('Query/domain Mapping requires actual domain fields');
    const exact = {...bound, field_compilation_sha256: fields.compilation_sha256};
    if (roots('Query').length) {
      const child = planConfiguredPythonQueries(boundary, fields, {schema_version: PYTHON_QUERY_VERSION, ...exact, roots: roots('Query')}, {...sources.common, query_contract: source('query'), field_contract: source('field')});
      add('queries', child); queryModules = child.modules;
    }
    if (domainMappings.length) {
      const child = planConfiguredPythonMappings(boundary, fields, {schema_version: PYTHON_MAPPING_VERSION, ...exact, roots: domainMappings}, {...sources.common, mapping_contract: source('mapping'), field_contract: source('field')});
      add('mappings', child); mappingModules = child.modules;
    }
  }
  if (roots('Policy').length) {
    const child = planConfiguredPythonPolicies(graph, boundary, fields, {schema_version: PYTHON_POLICY_VERSION, ...typed, rule_selection: PYTHON_STRUCTURED_RULE_VERSION, roots: roots('Policy')}, {policy_contract: source('policy'), rules: sources.rules});
    add('policies', child); policyModules = child.modules;
  }
  let eventModules: EventModules = [];
  if (roots('Event').length) {
    const child = planConfiguredPythonEvents(graph, boundary, {schema_version: PYTHON_EVENT_VERSION, ...bound, value_profile: EVENT_VALUE_PROFILE, roots: roots('Event')}, sources.events);
    add('events', child); eventModules = child.modules;
  }
  const actions = selection.operations.map(a => compileOperationActionBindings(graph, boundary, fields, a, source('operation_action')));
  let operationModules: OperationPlan['modules'] = [];
  if (actions.length) {
    const child = planConfiguredPythonOperations(graph, boundary, fields, {schema_version: PYTHON_OPERATION_VERSION, ...layout, actions, factories: selection.factories}, sources.operations);
    add('operations', child); operationModules = child.modules;
  }
  const workflows: WorkflowContext[] = [];
  for (const authored of selection.workflows) {
    const declared = decodeWorkflowOccurrences(graph.nodes.find(n => n.selector === authored.selector)!.body.typed_contract);
    const refs = workflowOperationRefs(declared), used = actions.filter(a => refs.includes(a.bindings.selector));
    const steps = authored.steps.map(call => {const ref = declared.steps.find(s => s.step_id === call.step_id)?.operation_ref; const action = used.find(a => a.bindings.selector === ref) ?? fail('unknown step action'); return {...call, action_sha256: action.action_sha256};});
    const compensations = authored.compensations.map(call => {const ref = declared.compensations.find(s => s.compensation_id === call.compensation_id)?.operation_ref; const action = used.find(a => a.bindings.selector === ref) ?? fail('unknown compensation action'); return {...call, action_sha256: action.action_sha256};});
    const {recovery, ...bindings} = authored;
    const workflow = compileWorkflowBindings(graph, boundary, fields, used, {...bindings, schema_version: WORKFLOW_BINDINGS_VERSION, steps, compensations}, source('workflow_binding'));
    const policy = selectWorkflowRecoveryPolicy(workflow, {schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256, contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, ...recovery}, source('workflow_recovery'));
    const child = planConfiguredPythonWorkflow(graph, boundary, fields, {schema_version: PYTHON_WORKFLOW_VERSION, ...layout, workflow, policy, actions: used, factories: selection.factories}, sources.workflows);
    add('workflow', child);
    const {module_root, relative_path, descriptor, provider_sha256} = child.materialization;
    workflows.push({modules: child.modules, workflow, policy, actions: used, operation_plan_sha256: child.operation_plan.plan_sha256,
      materialization: {module_root, relative_path, descriptor, provider_sha256}});
  }
  let stateMachineModules: StateMachineModules = [];
  if (roots('State Machine').length) {
    const child = planConfiguredPythonStateMachines(graph, boundary, fields, {schema_version: PYTHON_STATE_MACHINE_VERSION, ...typed, roots: roots('State Machine')}, {state_machine_contract: source('state_machine'), rules: sources.rules});
    add('state-machines', child); stateMachineModules = child.modules;
  }
  let interfaceModules: InterfaceModules = [];
  if (roots('Interface').length) {
    const child = planConfiguredPythonInterfaces(graph, boundary, fields, {schema_version: PYTHON_INTERFACE_VERSION, ...typed, roots: roots('Interface')}, sources.interfaces);
    add('interfaces', child); interfaceModules = child.modules;
  }
  const publicMappings = roots('Mapping').filter(s => !domainMappings.includes(s));
  let publicMappingContext: Readonly<{modules: PublicMappingPlan['modules']; mappings: PublicMappingPlan['mappings']}> = {modules: [], mappings: []};
  if (publicMappings.length) {
    const child = planConfiguredPythonPublicMappings(graph, boundary, fields, {schema_version: PYTHON_PUBLIC_MAPPING_VERSION, ...typed, roots: publicMappings}, sources.publicMappings);
    add('public-mappings', child); publicMappingContext = {modules: child.modules, mappings: child.mappings};
  }
  const artifacts = [...files.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1);
  const modules = resolvePythonModules(artifacts, selection.module_root.split('/').map(pythonSnake).join('/')).map(m => {
    const qualified_selectors = [...(owners.get(m.relative_path) ?? [])].sort();
    return {...m, qualified_selectors, metatypes: [...new Set(qualified_selectors.map(s => graph.nodes.find(n => n.selector === s)!.kind))].sort()};
  });
  const represented = new Set(modules.flatMap(m => m.qualified_selectors));
  if (graph.nodes.some(n => !represented.has(n.selector))) fail('every project node needs a native realization');
  const body = {schema_version: 'domainspec.reconciled-python-project-plan/v1-candidate' as const, selection, definition_sha256: PYTHON_PROJECT_DEFINITION_SHA256, source_capsule_sha256: getReconciledSourceCapsule().capsule_sha256,
    certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null, semantic_sources: graph.source_manifest, checking_scope: 'whole-project' as const,
    node_selectors: graph.nodes.map(n => n.selector).sort(), requests, modules, artifacts, authority_effect: 'none' as const, output_effect: 'none' as const};
  const plan = freeze({...body, plan_sha256: sha256(canonicalJson(body))}); checked.add(plan); calculationContexts.set(plan, calculationContext);
  dataContexts.set(plan, freeze({queries: queryModules, mappings: mappingModules, model: fields?.model ?? null, runtime_dir: selection.module_root.split('/').map(pythonSnake).join('/') + '/runtime'}));
  decisionContexts.set(plan, freeze({rules: ruleModules, policies: policyModules}));
  factoryContexts.set(plan, factoryModules);
  eventContexts.set(plan, eventModules);
  stateMachineContexts.set(plan, stateMachineModules);
  interfaceContexts.set(plan, interfaceModules);
  publicMappingContexts.set(plan, freeze(publicMappingContext));
  operationContexts.set(plan, freeze({modules: operationModules, actions}));
  workflowContexts.set(plan, freeze(workflows));
  return plan;
}

export function planReconciledPythonProject(sourceRoot: string, selection: unknown): ReconciledPythonProjectPlan {
  decodeReconciledPythonSelection(selection);
  const graph = loadCompiledProjectGraph(sourceRoot), result = planCompiledReconciledPythonProject(graph, selection);
  if (loadCompiledProjectGraph(sourceRoot).source_manifest.manifest_sha256 !== graph.source_manifest.manifest_sha256) fail('source changed during planning');
  return result;
}

export function selectReconciledPythonArtifacts(plan: ReconciledPythonProjectPlan, roots: readonly string[] | null = null) {
  assertReconciledPythonProjectPlan(plan); assertInterfaceData(roots);
  if (roots !== null && (!Array.isArray(roots) || !roots.length || roots.length > 256 || new Set(roots).size !== roots.length || roots.some(s => !plan.node_selectors.includes(s)))) fail('unique existing node roots required');
  const modules = roots === null ? plan.modules : selectPythonModuleClosure(plan.modules, plan.modules.filter(m => m.qualified_selectors.some(s => roots.includes(s))).map(m => m.relative_path));
  const paths = new Set(modules.map(m => m.relative_path));
  const body = {schema_version: 'domainspec.reconciled-python-artifact-view/v1-candidate' as const, project_plan_sha256: plan.plan_sha256, roots: roots === null ? plan.node_selectors : [...roots].sort(), modules, artifacts: plan.artifacts.filter(a => paths.has(a.relative_path)), checking_scope: 'whole-project' as const, authority_effect: 'none' as const};
  return freeze({...body, view_sha256: sha256(canonicalJson(body))});
}
