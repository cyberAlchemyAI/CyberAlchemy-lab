import {loadCompiledProjectGraph, assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_CONTRACT_SHA256, COMPOSITION_BOUNDARY_VERSION} from '../input/composition-boundary.js';
import {compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION} from '../input/compiled-field-model.js';
import {compileOperationActionBindings} from '../typed-operation/action-bindings.js';
import {compileWorkflowBindings, WORKFLOW_BINDINGS_VERSION} from '../typed-operation/workflow-bindings.js';
import {selectWorkflowRecoveryPolicy, WORKFLOW_RECOVERY_CONTRACT_SHA256, WORKFLOW_RECOVERY_POLICY_VERSION} from '../typed-operation/workflow-recovery.js';
import {decodeWorkflowOccurrences, workflowOperationRefs} from '../typed-backend/workflow-occurrences.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {decodeReconciledRustSelection, failRustProject as fail, freezeRustProject as freeze} from './reconciled-rust-selection.js';
import {getReconciledSource as source, getReconciledSourceCapsule} from './reconciled-sources.js';
import {planConfiguredRustEnums, RUST_ENUM_SELECTION_VERSION} from './configured-rust-enums.js';
import {planConfiguredRustRules, RUST_RULE_SELECTION_VERSION} from './configured-rust-rules.js';
import {planConfiguredRustFactories, RUST_FACTORY_SELECTION_VERSION} from './configured-rust-factories.js';
import {planConfiguredRustCalculations, RUST_CALCULATION_SELECTION_VERSION} from './configured-rust-calculations.js';
import {planConfiguredRustQueries, RUST_QUERY_SELECTION_VERSION} from './configured-rust-queries.js';
import {planConfiguredRustMappings, RUST_MAPPING_SELECTION_VERSION} from './configured-rust-mappings.js';
import {planConfiguredRustPolicies, RUST_POLICY_SELECTION_VERSION} from './configured-rust-policies.js';
import {planConfiguredRustEvents, RUST_EVENT_SELECTION_VERSION} from './configured-rust-events.js';
import {planConfiguredRustOperations, RUST_OPERATION_SELECTION_VERSION} from './configured-rust-operations.js';
import {planConfiguredRustStateMachines, RUST_STATE_MACHINE_SELECTION_VERSION} from './configured-rust-state-machines.js';
import {planConfiguredRustWorkflow, RUST_WORKFLOW_SELECTION_VERSION} from './configured-rust-workflows.js';
import {planConfiguredRustInterfaces, RUST_INTERFACE_SELECTION_VERSION} from './configured-rust-interfaces.js';
import {rustSnake} from './configured-rust-values.js';
import type {PlannedArtifact} from './contracts.js';

export const RUST_PROJECT_DEFINITION_SHA256 = '376246591954a4bf79b4f314355096006f31cc158a393c80cea9787d0c511864';
const checked = new WeakSet<object>();
export type ReconciledRustProjectPlan = ReturnType<typeof planCompiledReconciledRustProject>;
export function assertReconciledRustProjectPlan(value: unknown): asserts value is ReconciledRustProjectPlan {if (!value || typeof value !== 'object' || !checked.has(value)) fail('registered Rust project required');}

/** One checked graph, explicit bindings, one deterministic dependency-free Cargo crate. */
export function planCompiledReconciledRustProject(graph: CompiledProjectGraph, value: unknown) {
  assertCompiledProjectSnapshot(graph); const selection = decodeReconciledRustSelection(value);
  if (sha256(source('rust_project')) !== RUST_PROJECT_DEFINITION_SHA256) fail('project definition drift');
  if (graph.compositions?.length) fail('Rust cross-project composition adapters are not yet implemented');
  const supported = new Set(['Entity', 'Value Object', 'Enum', 'Rule', 'Calculation', 'Policy', 'Query', 'Operation', 'Workflow', 'State Machine', 'Mapping', 'Event', 'Interface']);
  if (!graph.nodes.length || graph.nodes.some(node => !supported.has(node.kind))) fail('nonempty supported metatype project required');
  const roots = (kind: string) => graph.nodes.filter(node => node.kind === kind).map(node => node.selector).sort();
  const exact = (actual: readonly string[], expected: readonly string[]) => {if (new Set(actual).size !== actual.length || canonicalJson([...actual].sort()) !== canonicalJson([...expected].sort())) fail('exact authored binding coverage');};
  exact(selection.factories.map(row => row.selector), [...roots('Entity'), ...roots('Value Object')]); exact(selection.operations.map(row => row.selector), roots('Operation')); exact(selection.workflows.map(row => row.selector), roots('Workflow'));
  const certificate = createCompiledProjectCertificate(graph), boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, source('composition'));
  const dataRoots = [...roots('Entity'), ...roots('Value Object'), ...roots('Enum')].sort(); if (!dataRoots.length) fail('Rust project requires declared domain values');
  const fields = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: dataRoots, bindings: selection.field_bindings}, source('field'));
  const moduleRoot = selection.module_root, bound = {language: 'rust' as const, module_root: moduleRoot, boundary_sha256: boundary.boundary_sha256}, typed = {...bound, field_compilation_sha256: fields.compilation_sha256};
  const files = new Map<string, PlannedArtifact>(), represented = new Map<string, string>(), requests: {kind: string; child_plan_sha256: string}[] = [];
  const add = (kind: string, child: {plan_sha256: string; artifacts: readonly PlannedArtifact[]; modules?: readonly {selector: string; relative_path: string}[]}) => {
    for (const row of child.artifacts) {const prior = files.get(row.relative_path); if (prior && (prior.content !== row.content || prior.sha256 !== row.sha256)) fail('conflicting generated artifact:' + row.relative_path); files.set(row.relative_path, row);}
    for (const module of child.modules ?? []) {const prior = represented.get(module.selector); if (prior && prior !== module.relative_path) fail('multiple native realizations:' + module.selector); represented.set(module.selector, module.relative_path);}
    requests.push({kind, child_plan_sha256: child.plan_sha256});
  };
  const ruleRoots = roots('Rule');
  const rules = planConfiguredRustRules(graph, fields, {schema_version: RUST_RULE_SELECTION_VERSION, language: 'rust', module_root: moduleRoot, roots: ruleRoots, field_compilation_sha256: fields.compilation_sha256}, source('rust_rule'));
  add('Rule', rules);
  const enumRoots = roots('Enum'); if (enumRoots.length) add('Enum', planConfiguredRustEnums(fields, {schema_version: RUST_ENUM_SELECTION_VERSION, language: 'rust', module_root: moduleRoot, roots: enumRoots, field_compilation_sha256: fields.compilation_sha256}, source('rust_enum')));
  add('Entity+Value Object', planConfiguredRustFactories(graph, fields, rules, {schema_version: RUST_FACTORY_SELECTION_VERSION, language: 'rust', module_root: moduleRoot, field_compilation_sha256: fields.compilation_sha256, factories: selection.factories}, source('rust_factory')));
  const calculationRoots = roots('Calculation'); if (calculationRoots.length) add('Calculation', planConfiguredRustCalculations(graph, {schema_version: RUST_CALCULATION_SELECTION_VERSION, language: 'rust', module_root: moduleRoot, roots: calculationRoots}, source('rust_calculation')));
  const queryRoots = roots('Query'); if (queryRoots.length) add('Query', planConfiguredRustQueries(boundary, fields, {schema_version: RUST_QUERY_SELECTION_VERSION, ...typed, roots: queryRoots}, source('rust_query')));
  const interfaceRoots = roots('Interface'); if (interfaceRoots.length) add('Interface', planConfiguredRustInterfaces(graph, boundary, fields, {schema_version: RUST_INTERFACE_SELECTION_VERSION, ...typed, roots: interfaceRoots}, {rust_contract: source('rust_interface'), interface_contract: source('interface'), version_contract: source('interface_version')}));
  const mappingRoots = roots('Mapping'); if (mappingRoots.length) add('Mapping', planConfiguredRustMappings(graph, boundary, fields, {schema_version: RUST_MAPPING_SELECTION_VERSION, ...typed, roots: mappingRoots}, {rust_contract: source('rust_mapping'), public_mapping_contract: source('public_mapping_value_object')}));
  const policyRoots = roots('Policy'); if (policyRoots.length) add('Policy', planConfiguredRustPolicies(graph, boundary, fields, {schema_version: RUST_POLICY_SELECTION_VERSION, ...typed, rule_selection: RUST_RULE_SELECTION_VERSION, roots: policyRoots}, {rust_contract: source('rust_policy'), rule_contract: source('rust_rule')}));
  const eventRoots = roots('Event'); if (eventRoots.length) add('Event', planConfiguredRustEvents(graph, boundary, {schema_version: RUST_EVENT_SELECTION_VERSION, ...bound, roots: eventRoots}, source('rust_event')));
  const actions = selection.operations.map(row => compileOperationActionBindings(graph, boundary, fields, row, source('operation_action')));
  const operationSources = {rust_contract: source('rust_operation'), rule_contract: source('rust_rule'), factory_contract: source('rust_factory'), event_contract: source('rust_event')};
  add('Operation', planConfiguredRustOperations(graph, boundary, fields, {schema_version: RUST_OPERATION_SELECTION_VERSION, ...typed, actions, factories: selection.factories}, operationSources));
  const stateMachineRoots = roots('State Machine'); if (stateMachineRoots.length) add('State Machine', planConfiguredRustStateMachines(graph, boundary, fields, {schema_version: RUST_STATE_MACHINE_SELECTION_VERSION, ...typed, roots: stateMachineRoots}, {rust_contract: source('rust_state_machine'), rule_contract: source('rust_rule')}));
  for (const authored of selection.workflows) {
    const occurrence = decodeWorkflowOccurrences(graph.nodes.find(node => node.selector === authored.selector)!.body.typed_contract), refs = workflowOperationRefs(occurrence), used = actions.filter(action => refs.includes(action.bindings.selector));
    const steps = authored.steps.map(call => {const ref = occurrence.steps.find(row => row.step_id === call.step_id)?.operation_ref, action = used.find(row => row.bindings.selector === ref) ?? fail('unknown step action'); return {...call, action_sha256: action.action_sha256};});
    const compensations = authored.compensations.map(call => {const ref = occurrence.compensations.find(row => row.compensation_id === call.compensation_id)?.operation_ref, action = used.find(row => row.bindings.selector === ref) ?? fail('unknown compensation action'); return {...call, action_sha256: action.action_sha256};});
    const {recovery, ...bindings} = authored, workflow = compileWorkflowBindings(graph, boundary, fields, used, {...bindings, schema_version: WORKFLOW_BINDINGS_VERSION, steps, compensations}, source('workflow_binding'));
    const policy = selectWorkflowRecoveryPolicy(workflow, {schema_version: WORKFLOW_RECOVERY_POLICY_VERSION, workflow_sha256: workflow.workflow_sha256, contract_sha256: WORKFLOW_RECOVERY_CONTRACT_SHA256, ...recovery}, source('workflow_recovery'));
    add('Workflow', planConfiguredRustWorkflow(graph, boundary, fields, {schema_version: RUST_WORKFLOW_SELECTION_VERSION, language: 'rust', module_root: moduleRoot, workflow, policy, actions: used, factories: selection.factories}, {rust_contract: source('rust_workflow'), outcome_contract: source('workflow_outcome'), recovery_contract: source('workflow_recovery'), operations: operationSources}));
  }
  if (graph.nodes.some(node => !represented.has(node.selector))) fail('every project node needs one native realization:' + graph.nodes.filter(node => !represented.has(node.selector)).map(node => node.selector).join(','));
  const addSupport = (relative_path: string, content: string) => {if (files.has(relative_path)) fail('support artifact collision:' + relative_path); files.set(relative_path, {relative_path, content, sha256: sha256(content), size_bytes: Buffer.byteLength(content)});};
  const roles = ['domain/types', 'domain/rules', 'domain/calculations', 'domain/policies', 'domain/events', 'domain/state_machines', 'application/queries', 'application/mappings', 'application/operations', 'application/workflows', 'application/interfaces'];
  for (const role of roles) {const prefix = `${moduleRoot}/src/${role}/`, moduleNames = [...files.keys()].filter(file => file.startsWith(prefix) && file.endsWith('.rs') && !file.endsWith('/mod.rs')).map(file => file.slice(prefix.length, -3)).sort(); if (moduleNames.length) addSupport(`${prefix}mod.rs`, moduleNames.map(name => `pub mod ${name};`).join('\n') + '\n');}
  const domainRoles = roles.filter(role => role.startsWith('domain/')).map(role => role.split('/')[1]!).filter(role => files.has(`${moduleRoot}/src/domain/${role}/mod.rs`));
  const applicationRoles = roles.filter(role => role.startsWith('application/')).map(role => role.split('/')[1]!).filter(role => files.has(`${moduleRoot}/src/application/${role}/mod.rs`));
  addSupport(`${moduleRoot}/src/domain/mod.rs`, domainRoles.map(role => `pub mod ${role};`).join('\n') + '\n'); addSupport(`${moduleRoot}/src/application/mod.rs`, applicationRoles.map(role => `pub mod ${role};`).join('\n') + '\n');
  addSupport(`${moduleRoot}/src/lib.rs`, 'pub mod domain;\npub mod application;\n');
  const packageName = graph.project_id, libraryName = rustSnake(packageName); addSupport(`${moduleRoot}/Cargo.toml`, `[package]\nname = ${JSON.stringify(packageName)}\nversion = "0.0.0"\nedition = "2024"\npublish = false\n\n[lib]\nname = ${JSON.stringify(libraryName)}\npath = "src/lib.rs"\n`);
  addSupport(`${moduleRoot}/Cargo.lock`, `# This file is automatically @generated by Cargo.\n# It is not intended for manual editing.\nversion = 4\n\n[[package]]\nname = ${JSON.stringify(packageName)}\nversion = "0.0.0"\n`);
  const artifacts = [...files.values()].sort((left, right) => left.relative_path < right.relative_path ? -1 : 1), accounting = [...supported].sort().map(kind => ({kind, selectors: roots(kind), count: roots(kind).length}));
  const body = {schema_version: 'domainspec.reconciled-rust-project-plan/v1-candidate' as const, selection, definition_sha256: RUST_PROJECT_DEFINITION_SHA256, source_capsule_sha256: getReconciledSourceCapsule().capsule_sha256, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256, semantic_sources: graph.source_manifest, checking_scope: 'whole-project' as const, node_selectors: graph.nodes.map(node => node.selector).sort(), metatype_accounting: accounting, requests, modules: [...represented].sort(([left], [right]) => left < right ? -1 : 1).map(([selector, relative_path]) => ({selector, kind: graph.nodes.find(node => node.selector === selector)!.kind, relative_path})), artifacts, cargo: {manifest_path: `${moduleRoot}/Cargo.toml`, library_path: `${moduleRoot}/src/lib.rs`, package_name: packageName, library_name: libraryName, dependency_count: 0}, authority_effect: 'none' as const, output_effect: 'none' as const};
  const plan = freeze({...body, plan_sha256: sha256(canonicalJson(body))}); checked.add(plan); return plan;
}

export function planReconciledRustProject(sourceRoot: string, selection: unknown): ReconciledRustProjectPlan {
  decodeReconciledRustSelection(selection); const graph = loadCompiledProjectGraph(sourceRoot), result = planCompiledReconciledRustProject(graph, selection); if (loadCompiledProjectGraph(sourceRoot).source_manifest.manifest_sha256 !== graph.source_manifest.manifest_sha256) fail('source changed during planning'); return result;
}

/** A Rust node view retains the whole crate because native module compilation is
 * the project checking boundary; roots narrow intent, not semantic compilation. */
export function selectReconciledRustArtifacts(plan: ReconciledRustProjectPlan, roots: readonly string[] | null = null) {
  assertReconciledRustProjectPlan(plan);
  if (roots !== null && (!Array.isArray(roots) || !roots.length || roots.length > 256 || new Set(roots).size !== roots.length || roots.some(selector => !plan.node_selectors.includes(selector)))) fail('unique existing node roots required');
  const body = {schema_version: 'domainspec.reconciled-rust-artifact-view/v1-candidate' as const, project_plan_sha256: plan.plan_sha256, roots: roots === null ? plan.node_selectors : [...roots].sort(), modules: plan.modules, artifacts: plan.artifacts, checking_scope: 'whole-project' as const, authority_effect: 'none' as const};
  return freeze({...body, view_sha256: sha256(canonicalJson(body))});
}
