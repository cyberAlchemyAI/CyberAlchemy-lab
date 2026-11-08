import type {CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectSnapshot} from '../input/project-model.js';
import {assertReconciledProjectPlan, type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {assertReconciledPythonProjectPlan, type ReconciledPythonProjectPlan} from '../generation/reconciled-python-project.js';
import {assertReconciledRustProjectPlan, type ReconciledRustProjectPlan} from '../generation/reconciled-rust-project.js';
import {getReconciledSource, getReconciledSourceCapsule} from '../generation/reconciled-sources.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';

export const CROSS_LANGUAGE_REALIZATION_MATRIX_SHA256 = 'a902442f93c1c232d21fabb3cb51042149462752084faecf8395d2929dbd9f9d';
const languages = ['typescript', 'python', 'rust'] as const;
const requiredObservations = ['native-compile-or-import', 'independent-native-surface', 'normalized-positive-behavior', 'normalized-hostile-behavior', 'language-specific-negative-control'] as const;
const registered = new WeakSet<object>();
const fail = (reason: string): never => {throw new TypeError('DS_REALIZATION_MATRIX:' + reason);};
const same = (left: unknown, right: unknown, reason: string) => {if (canonicalJson(left) !== canonicalJson(right)) fail(reason);};

const generationContracts: Record<string, Record<typeof languages[number], readonly string[]>> = {
  'Entity': {typescript: ['factory'], python: ['factory', 'python'], rust: ['rust_factory']},
  'Value Object': {typescript: ['factory'], python: ['factory', 'python'], rust: ['rust_factory']},
  'Enum': {typescript: ['standalone_sum', 'factory'], python: ['standalone_sum', 'python'], rust: ['rust_enum']},
  'Rule': {typescript: ['rule'], python: ['rule', 'python'], rust: ['rust_rule']},
  'Calculation': {typescript: ['calculation_v1', 'calculation_v2'], python: ['calculation_v1', 'calculation_v2', 'python'], rust: ['rust_calculation']},
  'Query': {typescript: ['query'], python: ['query', 'python'], rust: ['rust_query']},
  'Mapping': {typescript: ['mapping', 'public_mapping'], python: ['mapping', 'public_mapping', 'python'], rust: ['rust_mapping']},
  'Policy': {typescript: ['policy'], python: ['policy', 'python'], rust: ['rust_policy']},
  'Event': {typescript: ['event'], python: ['event', 'python'], rust: ['rust_event']},
  'Operation': {typescript: ['operation', 'operation_action'], python: ['operation', 'operation_action', 'python'], rust: ['rust_operation']},
  'State Machine': {typescript: ['state_machine'], python: ['state_machine', 'python'], rust: ['rust_state_machine']},
  'Workflow': {typescript: ['workflow', 'workflow_outcome', 'workflow_recovery'], python: ['workflow', 'workflow_outcome', 'workflow_recovery', 'python'], rust: ['rust_workflow']},
  'Interface': {typescript: ['interface', 'interface_version'], python: ['interface', 'interface_version', 'python'], rust: ['rust_interface']},
};
const requestKinds: Record<string, Record<typeof languages[number], readonly string[]>> = {
  'Entity': {typescript: ['factories'], python: ['factories'], rust: ['Entity+Value Object']},
  'Value Object': {typescript: ['factories'], python: ['factories'], rust: ['Entity+Value Object']},
  'Enum': {typescript: ['factories', 'algebraic-enums'], python: ['factories', 'algebraic-enums'], rust: ['Enum']},
  'Rule': {typescript: ['rules'], python: ['rules'], rust: ['Rule']},
  'Calculation': {typescript: ['calculations-v1', 'calculations-v2'], python: ['calculations'], rust: ['Calculation']},
  'Query': {typescript: ['queries'], python: ['queries'], rust: ['Query']},
  'Mapping': {typescript: ['mappings', 'public-boundaries'], python: ['mappings', 'public-mappings'], rust: ['Mapping']},
  'Policy': {typescript: ['policies'], python: ['policies'], rust: ['Policy']},
  'Event': {typescript: ['events'], python: ['events'], rust: ['Event']},
  'Operation': {typescript: ['operations'], python: ['operations'], rust: ['Operation']},
  'State Machine': {typescript: ['state-machines'], python: ['state-machines'], rust: ['State Machine']},
  'Workflow': {typescript: ['workflows'], python: ['workflow'], rust: ['Workflow']},
  'Interface': {typescript: ['public-boundaries'], python: ['interfaces'], rust: ['Interface']},
};

type Language = typeof languages[number];
type Request = {kind: string; child_plan_sha256: string};
type Module = {relative_path: string; qualified_selectors?: readonly string[]; selector?: string};
function inventory(language: Language, typescript: ReconciledProjectPlan, python: ReconciledPythonProjectPlan, rust: ReconciledRustProjectPlan): {requests: readonly Request[]; modules: readonly Module[]; plan_sha256: string} {
  if (language === 'typescript') return {requests: typescript.resolved.requests, modules: typescript.resolved.modules, plan_sha256: typescript.plan_sha256};
  if (language === 'python') return {requests: python.requests, modules: python.modules, plan_sha256: python.plan_sha256};
  return {requests: rust.requests, modules: rust.modules, plan_sha256: rust.plan_sha256};
}

/** Construct complete accounting only. No cell is passed until a separate fresh
 * executor supplies every required observation class. */
export function createReconciledRealizationMatrix(graph: CompiledProjectGraph, plans: {typescript: ReconciledProjectPlan; python: ReconciledPythonProjectPlan; rust: ReconciledRustProjectPlan}) {
  assertCompiledProjectSnapshot(graph); assertReconciledProjectPlan(plans.typescript); assertReconciledPythonProjectPlan(plans.python); assertReconciledRustProjectPlan(plans.rust);
  if (sha256(getReconciledSource('realization_matrix')) !== CROSS_LANGUAGE_REALIZATION_MATRIX_SHA256) fail('definition drift');
  const certificates = [plans.typescript.resolved.certificate, plans.python.certificate, plans.rust.certificate]; certificates.forEach(certificate => same(certificate, certificates[0], 'plans do not share one graph certificate'));
  [plans.typescript.resolved.semantic_sources, plans.python.semantic_sources, plans.rust.semantic_sources].forEach(manifest => same(manifest, graph.source_manifest, 'plans do not share source identity'));
  const configuration = JSON.parse(getReconciledSource('configuration')) as {types: {kind: string; role: string; input: unknown; obligations: string[]}[]};
  if (!Array.isArray(configuration.types) || configuration.types.length !== 13 || new Set(configuration.types.map(row => row.kind)).size !== 13) fail('exact 13-type configuration required');
  if (graph.nodes.length < 13 || configuration.types.some(type => !graph.nodes.some(node => node.kind === type.kind))) fail('all 13 metatypes require an actual selected node');
  const capsule = new Map(getReconciledSourceCapsule().sources.map(row => [row.id, row]));
  const cells = configuration.types.flatMap(type => languages.map(language => {
    const native = inventory(language, plans.typescript, plans.python, plans.rust), selectors = graph.nodes.filter(node => node.kind === type.kind).map(node => node.selector).sort();
    const kinds = requestKinds[type.kind]?.[language] ?? fail('missing request mapping:' + type.kind + ':' + language), requests = native.requests.filter(row => kinds.includes(row.kind));
    if (!requests.length) fail('missing generator plan:' + type.kind + ':' + language);
    const modules = native.modules.filter(module => module.selector ? selectors.includes(module.selector) : module.qualified_selectors?.some(selector => selectors.includes(selector))).map(module => module.relative_path).sort();
    if (!modules.length) fail('missing native ownership:' + type.kind + ':' + language);
    const ids = generationContracts[type.kind]?.[language] ?? fail('missing generation contracts:' + type.kind + ':' + language);
    const contracts = ids.map(id => {const source = capsule.get(id as Parameters<typeof getReconciledSource>[0]) ?? fail('unselected contract:' + id); return {id, sha256: source.sha256};});
    return {cell_id: type.kind + '/' + language, metatype: type.kind, language, role: type.role, supported_input: type.input, normalized_obligations: [...type.obligations], selectors, generation_contracts: contracts, generator_plan_sha256s: [...new Set(requests.map(row => row.child_plan_sha256))].sort(), module_paths: modules, required_observations: requiredObservations, qualification_state: 'not-executed' as const};
  }));
  if (cells.length !== 39 || new Set(cells.map(cell => cell.cell_id)).size !== 39) fail('exact 39 unique cells required');
  const body = {schema_version: 'domainspec.cross-language-realization-matrix/v1-candidate' as const, definition_sha256: CROSS_LANGUAGE_REALIZATION_MATRIX_SHA256, source_manifest_sha256: graph.source_manifest.manifest_sha256, graph_sha256: certificates[0]!.graph_sha256, plan_sha256s: Object.fromEntries(languages.map(language => [language, inventory(language, plans.typescript, plans.python, plans.rust).plan_sha256])), denominators: {metatype_count: 13, language_count: 3, cell_count: 39, executed_cell_count: 0}, cells, claim_scope: 'closed-qualification-input-only' as const, authority_effect: 'none' as const};
  const result = Object.freeze({...body, matrix_sha256: sha256(canonicalJson(body))}); registered.add(result); return result;
}

export type ReconciledRealizationMatrix = ReturnType<typeof createReconciledRealizationMatrix>;
export function renderReconciledRealizationMatrix(value: ReconciledRealizationMatrix): string {if (!value || typeof value !== 'object' || !registered.has(value)) fail('registered matrix required'); return canonicalJson(value) + '\n';}
