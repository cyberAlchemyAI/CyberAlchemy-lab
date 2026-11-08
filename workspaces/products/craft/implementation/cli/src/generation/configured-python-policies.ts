import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {decodeTypedRulePolicyContract, checkTypedRulePolicy, TYPED_POLICY_RULES_VERSION, type TypedRulePolicyContract} from '../typed-backend/policy-rules.js';
import type {TypedRuleContract} from '../typed-operation/contracts.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {pythonPortableIdentifier} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {planConfiguredPythonRules, PYTHON_STRUCTURED_RULE_VERSION, type PythonStructuredRuleSources} from './configured-python-rules.js';
import {POLICY_CONTRACT_SHA256} from './configured-policies.js';
import {renderPythonPolicy, renderPythonPolicyBinding} from './configured-python-policy-source.js';
import type {PlannedArtifact} from './contracts.js';

export const PYTHON_POLICY_VERSION = 'domainspec.configured-python-policies-selection/v1-candidate';
export const PYTHON_POLICY_PROTOCOL = 'python.bound-policy/v1';
export interface PythonPolicySelection {
  readonly schema_version: typeof PYTHON_POLICY_VERSION;
  readonly language: 'python';
  readonly rule_selection: typeof PYTHON_STRUCTURED_RULE_VERSION;
  readonly boundary_sha256: string;
  readonly field_compilation_sha256: string | null;
  readonly module_root: string;
  readonly roots: readonly string[];
}
export interface PythonPolicySources {readonly policy_contract: string; readonly rules: PythonStructuredRuleSources;}
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_POLICY:' + reason);};
function closed(value: unknown, keys: readonly string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('plain data object required');
  const d = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(d).length !== keys.length || Reflect.ownKeys(d).some(k => typeof k !== 'string' || !keys.includes(k)) || Object.values(d).some(p => !Object.hasOwn(p, 'value') || !p.enumerable)) fail('closed data fields required');
}
function selectedRoots(value: unknown): string[] {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) return fail('plain roots required');
  const d: Record<string, PropertyDescriptor> = Object.getOwnPropertyDescriptors(value), length = d.length!.value;
  if (length < 1 || length > 256 || Reflect.ownKeys(d).length !== length + 1) fail('bounded dense roots required');
  const result: string[] = [];
  for (let i = 0; i < length; i++) {const p = d[String(i)]; if (!p || !Object.hasOwn(p, 'value') || !p.enumerable || typeof p.value !== 'string') return fail('inert roots required'); result.push(p.value);}
  if (new Set(result).size !== result.length) fail('duplicate roots'); return result.sort();
}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}

/** Explicit Rule-backed Policy selection; scalar-only policies need no data root. */
export function planConfiguredPythonPolicies(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields | null, selection: PythonPolicySelection, sources: PythonPolicySources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); if (fields !== null) assertCompiledProjectFields(fields);
  closed(selection, ['schema_version', 'language', 'rule_selection', 'boundary_sha256', 'field_compilation_sha256', 'module_root', 'roots']);
  closed(sources, ['policy_contract', 'rules']);
  closed(sources.rules, ['configuration', 'base', 'python', 'rule_contract', 'collection_contract', 'predicate_contract', 'numeric_contract', 'exact_contract', 'literal_contract', 'structured_contract', 'field_contract']);
  if (selection.schema_version !== PYTHON_POLICY_VERSION || selection.language !== 'python' || selection.rule_selection !== PYTHON_STRUCTURED_RULE_VERSION) fail('unsupported selection');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.boundary_sha256 !== boundary.boundary_sha256 || boundary.certificate.graph_sha256 !== certificate.graph_sha256 || selection.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null) || fields && fields.certificate.graph_sha256 !== certificate.graph_sha256) fail('stale or cross-graph selection');
  if (fields && fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('exact checked fields required');
  if (typeof selection.module_root !== 'string') fail('module root required');
  const segments = selection.module_root.split('/'); segments.forEach(pythonPortableIdentifier);
  if (['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref', 'codecs', 'encodings'].includes(segments[0]!)) fail('module root shadows standard library');
  if (typeof sources.policy_contract !== 'string' || sha256(sources.policy_contract) !== POLICY_CONTRACT_SHA256) fail('source drift:policy_contract');
  const root = segments.map(pythonSnake).join('/'), roots = selectedRoots(selection.roots), contracts = new Map<string, TypedRulePolicyContract>();
  for (const selector of roots) {
    const parts = selector.split(':'); if (parts.length !== 2) fail('selector required'); parts.forEach(pythonPortableIdentifier);
    const node = graph.nodes.find(n => n.selector === selector);
    if (node?.kind !== 'Policy' || (node.body.typed_contract as {schema_version?: string})?.schema_version !== TYPED_POLICY_RULES_VERSION) fail('typed Policy v2 required; explicitly extract legacy predicates into named Rules:' + selector);
    const c = decodeTypedRulePolicyContract(node!.body.typed_contract);
    if (!c.inputs.length || new Set([...c.cases.map(c => c.target), c.default_target]).size < 2) fail('Policy requires explicit inputs and distinct strategies; sensitivity needs behavioral witnesses');
    contracts.set(selector, c);
  }
  const ruleRoots = [...new Set([...contracts.values()].flatMap(c => c.cases.map(c => c.rule.selector)))].sort();
  const rulePlan = planConfiguredPythonRules(graph, {schema_version: selection.rule_selection, language: 'python', module_root: selection.module_root, roots: ruleRoots}, sources.rules);
  const cell = JSON.parse(sources.rules.configuration).types.find((t: {kind: string}) => t.kind === 'Policy');
  if (cell?.role !== 'domain/policies' || canonicalJson(cell.blocked_by) !== '["DSR-011","DSR-015"]') fail('Policy configuration');
  const overlay = JSON.parse(sources.rules.python).representation_overlays.find((o: {contract_id: string}) => o.contract_id === 'policy.profile-representation');
  if (overlay?.candidate_protocols.find((p: {protocol_id: string}) => p.protocol_id === PYTHON_POLICY_PROTOCOL)?.form_id !== 'python.policy-selector-function') fail('Policy profile');
  const rules = graph.nodes.filter(n => n.kind === 'Rule' && n.body.typed_contract).map(n => ({selector: n.selector, contract: n.body.typed_contract as TypedRuleContract}));
  const artifacts = new Map<string, PlannedArtifact>(rulePlan.artifacts.map(a => [a.relative_path, a]));
  const add = (relative_path: string, content: string): PlannedArtifact => {
    if (artifacts.has(relative_path)) fail('artifact collision:' + relative_path);
    const a = {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)}; artifacts.set(relative_path, a);
    const parts = relative_path.split('/');
    for (let i = 1; i < parts.length; i++) {const file = parts.slice(0, i).join('/') + '/__init__.py'; if (!artifacts.has(file)) artifacts.set(file, {relative_path: file, content: '', size_bytes: 0, sha256: sha256('')});}
    return a;
  };
  const modules = roots.map(selector => {
    const contract = contracts.get(selector)!; checkTypedRulePolicy(contract, fields?.model.declarations ?? [], rules);
    const [feature, node] = selector.split(':') as [string, string];
    const relative_path = `${root}/features/${pythonSnake(feature)}/src/${cell.role}/${pythonSnake(node)}.py`, provider_path = relative_path.replace(/\/([^/]+)\.py$/, '/_providers/$1.py');
    const imports = [...new Set(contract.cases.map(c => c.rule.selector))].sort().map((selector, i) => {
      const m = rulePlan.modules.find(m => m.selector === selector) ?? fail('missing Rule module');
      return {selector, module: pythonRelativeModule(provider_path, m.relative_path), symbol: m.callable, local: '_condition' + i};
    });
    const catalogue = [...new Set([...contract.cases.map(c => c.target), contract.default_target])].sort().map(selector => {
      const node = graph.nodes.find(n => n.selector === selector) ?? fail('unknown strategy'), bound = boundary.domain_graph.nodes.find(n => n.selector === selector) ?? fail('unbound strategy');
      if (!['Operation', 'Calculation'].includes(node.kind)) fail('invalid strategy kind');
      return {selector, kind: node.kind, source: bound.source, body_sha256: sha256(canonicalJson(node.body))};
    });
    const evidence = boundary.value_bindings.core_contracts.find(c => c.owner.selector === selector && c.kind === 'Policy') ?? fail('unbound Policy');
    const runtimeModule = pythonRelativeModule(provider_path, `${root}/runtime/values.py`).replace(/\.values$/, '');
    const provider = add(provider_path, renderPythonPolicy(contract, fields?.model ?? null, imports, runtimeModule)), callable = 'policy_' + pythonSnake(node);
    const body = {schema_version: 'domainspec.generated-python-policy-descriptor/v1-candidate', protocol_id: PYTHON_POLICY_PROTOCOL, selector, ontology_policy: contract.ontology_policy, source: evidence.source, contract_sha256: sha256(canonicalJson(contract)),
      inputs: contract.inputs, cases: contract.cases, default_target: contract.default_target, catalogue, strategy_set_sha256: sha256(canonicalJson(catalogue)), rule_plan_sha256: rulePlan.plan_sha256,
      rule_dependencies: imports.map(i => {const m = rulePlan.modules.find(m => m.selector === i.selector)!; return {selector: i.selector, closure_sha256: m.closure_sha256, path: m.relative_path, sha256: artifacts.get(m.relative_path)!.sha256};}),
      field_model_sha256: fields?.model.model_sha256 ?? null, return_semantics: 'strategy', effect_contract: 'none', dependency_contract: 'explicit-inputs-only', result_consumption: 'complete', primary_callable_count: 1,
      evaluation: 'ordered-first-true-otherwise-default', failures: ['POLICY_INPUT', 'RULE_INPUT'], provider: {sha256: provider.sha256}, authority_effect: 'none'};
    const descriptor = {...body, descriptor_sha256: sha256(canonicalJson(body))}, provider_import = pythonRelativeModule(relative_path, provider_path);
    add(relative_path, renderPythonPolicyBinding(provider_import, callable, descriptor));
    return {selector, relative_path, provider_path, provider_import, import_name: relative_path.slice(0, -3).replaceAll('/', '.'), callable, imports, descriptor};
  });
  const body = {schema_version: 'domainspec.configured-python-policies-plan/v1-candidate', selection: {...selection, roots}, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null,
    source_digests: {policy_contract: POLICY_CONTRACT_SHA256, rules: rulePlan.source_digests}, rule_plan: rulePlan, modules, artifacts: [...artifacts.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
