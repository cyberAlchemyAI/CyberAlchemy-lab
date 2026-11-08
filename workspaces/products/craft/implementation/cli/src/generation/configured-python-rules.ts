import path from 'node:path';
import {assertCompiledProjectSnapshot, selectCompiledProjectNode, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import type {RuleExpression, TypedRuleContract} from '../typed-operation/contracts.js';
import {PYTHON_ENUM_SOURCE_DIGESTS, pythonPortableIdentifier} from './configured-python-enums.js';
import {STRING_ORDER_RULE_CONTRACT_SHA256, COLLECTION_VALUE_RULE_CONTRACT_SHA256, COLLECTION_PREDICATE_RULE_CONTRACT_SHA256, NUMERIC_RULE_CONTRACT_SHA256, EXACT_RULE_CONTRACT_SHA256, EXACT_LITERAL_RULE_CONTRACT_SHA256} from './configured-rules.js';
import {renderPythonRule} from './configured-python-rule-source.js';
import {renderPythonValueSupport} from './configured-python-value-source.js';
import {renderPythonFactSupport} from './configured-python-fact-source.js';
import {STRUCTURED_RULE_CONTRACT_SHA256} from './configured-rules.js';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../input/compiled-field-model.js';

export const PYTHON_RULE_VERSION = 'domainspec.configured-python-rules-selection/v1-candidate';
export const PYTHON_STRUCTURED_RULE_VERSION = 'domainspec.configured-python-rules-selection/v2-candidate';
export const PYTHON_RULE_SOURCE_DIGESTS = Object.freeze({...PYTHON_ENUM_SOURCE_DIGESTS,
  rule_contract: STRING_ORDER_RULE_CONTRACT_SHA256, collection_contract: COLLECTION_VALUE_RULE_CONTRACT_SHA256,
  predicate_contract: COLLECTION_PREDICATE_RULE_CONTRACT_SHA256, numeric_contract: NUMERIC_RULE_CONTRACT_SHA256,
  exact_contract: EXACT_RULE_CONTRACT_SHA256, literal_contract: EXACT_LITERAL_RULE_CONTRACT_SHA256});
export interface PythonRuleSelection {
  readonly schema_version: typeof PYTHON_RULE_VERSION | typeof PYTHON_STRUCTURED_RULE_VERSION;
  readonly language: 'python';
  readonly module_root: string;
  readonly roots: readonly string[];
}
export type PythonRuleSources = Readonly<Record<keyof typeof PYTHON_RULE_SOURCE_DIGESTS, string>>;
export type PythonStructuredRuleSources = PythonRuleSources & Readonly<{structured_contract: string; field_contract: string}>;
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_RULE:' + reason);};
function closed(value: unknown, keys: readonly string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('inert object required');
  const d = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(d).some(k => typeof k !== 'string') || Object.keys(d).sort().join('|') !== [...keys].sort().join('|') || Object.values(d).some(p => !('value' in p) || !p.enumerable)) fail('closed data fields required');
}
function selectors(value: unknown): asserts value is readonly string[] {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype || !value.length || value.length > 256) return fail('nonempty bounded roots required');
  const d = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(d).length !== value.length + 1) fail('inert roots required');
  for (let i = 0; i < value.length; i++) if (!d[i] || !('value' in d[i]!) || typeof d[i]!.value !== 'string') fail('inert string roots required');
  if (new Set(value).size !== value.length) fail('duplicate roots');
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;
}
function dependencies(e: RuleExpression): string[] {
  if (e.op === 'rule_ref') return [e.selector];
  if (e.op === 'all' || e.op === 'any') return e.terms.flatMap(dependencies);
  if (e.op === 'not') return dependencies(e.term);
  if (e.op === 'unique' || e.op === 'exists' || e.op === 'exactly_one') return dependencies(e.where);
  return [];
}
const snake = (value: string) => value.replaceAll('-', '_');
function relativeModule(from: string, to: string): string {
  const relative = path.posix.relative(path.posix.dirname(from), to).replace(/\.py$/, '').split('/');
  let up = 0; while (relative[0] === '..') {up++; relative.shift();}
  return '.'.repeat(up + 1) + relative.join('.');
}

/** Source-only checked planner. No TS profile, generated TS translation, graph
 * interpreter, source re-read, publication or runtime profile activation. */
export function planConfiguredPythonRules(graph: CompiledProjectGraph, selection: PythonRuleSelection, sources: PythonRuleSources | PythonStructuredRuleSources) {
  assertCompiledProjectSnapshot(graph);
  closed(selection, ['schema_version', 'language', 'module_root', 'roots']);
  const structured = selection.schema_version === PYTHON_STRUCTURED_RULE_VERSION;
  closed(sources, [...Object.keys(PYTHON_RULE_SOURCE_DIGESTS), ...(structured ? ['structured_contract', 'field_contract'] : [])]);
  if ((!structured && selection.schema_version !== PYTHON_RULE_VERSION) || selection.language !== 'python') fail('unsupported selection');
  if (typeof selection.module_root !== 'string') fail('module root required');
  const segments = selection.module_root.split('/'); segments.forEach(pythonPortableIdentifier);
  if (['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref'].includes(segments[0]!)) fail('module root shadows standard library');
  const root = segments.map(snake).join('/');
  selectors(selection.roots);
  for (const key of Object.keys(PYTHON_RULE_SOURCE_DIGESTS) as (keyof PythonRuleSources)[])
    if (typeof sources[key] !== 'string' || sha256(sources[key]) !== PYTHON_RULE_SOURCE_DIGESTS[key]) fail('source drift:' + key);
  const expanded = sources as PythonStructuredRuleSources;
  if (structured && (typeof expanded.structured_contract !== 'string' || sha256(expanded.structured_contract) !== STRUCTURED_RULE_CONTRACT_SHA256 || typeof expanded.field_contract !== 'string' || sha256(expanded.field_contract) !== EXACT_FIELD_CONTRACT_SHA256)) fail('source drift:structured facts');
  const cell = JSON.parse(sources.configuration).types.find((t: {kind: string}) => t.kind === 'Rule');
  if (cell?.role !== 'domain/rules' || cell.blocked_by.length) fail('Rule configuration is not ready');
  const location = JSON.parse(sources.python).constraints.find((c: {constraint_id: string}) => c.constraint_id === 'python.rule-location');
  if (!location) fail('missing Python Rule location');
  const contracts = new Map<string, TypedRuleContract>();
  const dataRoots = new Set<string>();
  for (const selector of [...selection.roots].sort()) {
    const node = selectCompiledProjectNode(graph, selector);
    if (node.kind !== 'Rule' || node.typed_closure?.schema_version !== 'domainspec.typed-rule-closure/v1') fail('selected root must be a typed Rule:' + selector);
    for (const member of node.typed_closure!.nodes) {
      if (structured && ['Entity', 'Value Object', 'Enum'].includes(member.kind)) {dataRoots.add(member.selector); continue;}
      if (member.kind !== 'Rule' || !['domainspec.typed-rule/v1', 'domainspec.typed-rule/v2'].includes(member.typed_contract.schema_version)) fail('structured dependency requires a Python fact adapter:' + member.selector);
      contracts.set(member.selector, member.typed_contract as TypedRuleContract);
    }
  }
  const certificate = createCompiledProjectCertificate(graph);
  const fields = structured && dataRoots.size ? compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256, roots: [...dataRoots].sort(), bindings: []}, expanded.field_contract) : null;
  const entries = [...contracts.keys()].sort().map(selector => {
    const node = graph.nodes.find(n => n.selector === selector)!;
    pythonPortableIdentifier(node.feature_id); pythonPortableIdentifier(node.node_id);
    const leaf = `src/${cell.role}/${snake(node.node_id)}.py`;
    if (!(new RegExp(location.expected)).test(leaf)) fail('Python Rule location mismatch');
    return {selector, relative_path: `${root}/features/${snake(node.feature_id)}/${leaf}`, callable: 'rule_' + snake(node.node_id), closure_sha256: selectCompiledProjectNode(graph, selector).typed_closure!.closure_sha256};
  });
  const modules = entries.map(entry => ({...entry, imports: [...new Set(dependencies(contracts.get(entry.selector)!.expression))].sort().map((selector, i) => {
    const target = entries.find(e => e.selector === selector) ?? fail('missing Rule dependency');
    return {selector, module: relativeModule(entry.relative_path, target.relative_path), symbol: target.callable, local: '_dependency' + i};
  })}));
  const contents = new Map<string, string>();
  const add = (file: string, content: string) => {if (contents.has(file)) fail('native path collision:' + file); contents.set(file, content);};
  for (const module of modules) add(module.relative_path, renderPythonRule(contracts.get(module.selector)!, module.selector, module.callable, module.closure_sha256, relativeModule(module.relative_path, `${root}/runtime.py`), module.imports, structured ? fields?.model ?? null : undefined));
  add(`${root}/runtime/values.py`, renderPythonValueSupport());
  if (structured) add(`${root}/runtime/facts.py`, renderPythonFactSupport());
  for (const file of [...contents.keys()]) for (let dir = path.posix.dirname(file); dir !== '.'; dir = path.posix.dirname(dir)) {
    const init = dir + '/__init__.py'; if (!contents.has(init)) add(init, '');
  }
  const artifacts = [...contents].sort(([a], [b]) => a < b ? -1 : 1).map(([relative_path, content]) => ({relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)}));
  const body = {schema_version: structured ? 'domainspec.configured-python-rules-plan/v2-candidate' : 'domainspec.configured-python-rules-plan/v1-candidate', selection: {...selection, roots: [...selection.roots].sort()}, certificate, source_digests: structured ? {...PYTHON_RULE_SOURCE_DIGESTS, structured_contract: STRUCTURED_RULE_CONTRACT_SHA256, field_contract: EXACT_FIELD_CONTRACT_SHA256} : PYTHON_RULE_SOURCE_DIGESTS, ...(structured ? {field_model_sha256: fields?.model.model_sha256 ?? null} : {}), modules, artifacts, input_envelope: structured ? 'structured-rule-values/v2-candidate' : 'scalar-collection-exact-rule-closures/v1-candidate', authority_effect: 'none'} as const;
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
