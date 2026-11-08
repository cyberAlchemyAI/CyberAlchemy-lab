import path from 'node:path';
import {assertCompiledProjectSnapshot, selectCompiledProjectNode, type CompiledProjectGraph} from '../input/project-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import type {TypedRuleContract, TypedType, RuleExpression, ValueExpression} from '../typed-operation/contracts.js';
import type {PlannedArtifact} from './contracts.js';
import {PROFILED_SOURCE_DIGESTS} from './profiled-project.js';
import {collectionPredicateSource} from './configured-rule-predicates.js';
import {numericRuleSupport, NUMERIC_RULE_VALUE_PROFILE} from './configured-rule-numeric.js';
import {exactRuleSupport} from './configured-rule-exact.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import {compileSelectedProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256} from '../input/compiled-field-model.js';
import {renderStructuredRule} from './configured-rule-values.js';

// PCR-06 first slice. Current input limits and open questions: RULE-GENERATION.md
// in development/reconciliation-v1/profile-compiler-reconciliation.
export const CONFIGURED_RULE_VERSION = 'domainspec.configured-rules-selection/v1-candidate';
export const STRING_ORDER_RULE_VERSION = 'domainspec.configured-rules-selection/v2-candidate';
export const STRING_ORDER_RULE_CONTRACT_SHA256 = 'dbd1052e7aa56cc689d8598a067631322cf534867d45ebcb77b02ab58c81a658';
export const COLLECTION_VALUE_RULE_VERSION = 'domainspec.configured-rules-selection/v3-candidate';
export const COLLECTION_VALUE_RULE_CONTRACT_SHA256 = '02e15e5c84a5ee60895ec4891aa328b8a2960b1d69d7bc45fcdeccbdb4c6b4ba';
export const COLLECTION_PREDICATE_RULE_VERSION = 'domainspec.configured-rules-selection/v4-candidate';
export const COLLECTION_PREDICATE_RULE_CONTRACT_SHA256 = '3c2d6624daee52f173b0bcd63834b9eac1e0a2e5411b677305ef55bad569feab';
export const NUMERIC_RULE_VERSION = 'domainspec.configured-rules-selection/v5-candidate';
export const NUMERIC_RULE_CONTRACT_SHA256 = '4612175e85b443bf8b7e1f920b4a3225220f54bb2a6114b8f41a52bbb2e97d1e';
export const EXACT_RULE_VERSION = 'domainspec.configured-rules-selection/v6-candidate';
export const EXACT_RULE_CONTRACT_SHA256 = 'b9637fbec3f540a549c5cc5f393b55275896d1026c57cd239396bdad13807f06';
export const EXACT_LITERAL_RULE_VERSION = 'domainspec.configured-rules-selection/v7-candidate';
export const EXACT_LITERAL_RULE_CONTRACT_SHA256 = 'b89f26b8e82f501b94c625fd027ff088d2c130ccbd0b19c8cf792ea88b4e7381';
export const STRUCTURED_RULE_VERSION = 'domainspec.configured-rules-selection/v8-candidate';
export const STRUCTURED_RULE_CONTRACT_SHA256 = 'dbb0b403c041a453382b84f24ad1d0e26e66150380286c74a3dcbfc8dc818d59';
export const RULE_CONFIGURATION_SHA256 = '9ac018e42080483f373219049b466d8a515cb3e7748181ea8e635b1162af8317';
export interface ConfiguredRuleSelection {
  readonly schema_version: typeof CONFIGURED_RULE_VERSION | typeof STRING_ORDER_RULE_VERSION | typeof COLLECTION_VALUE_RULE_VERSION | typeof COLLECTION_PREDICATE_RULE_VERSION | typeof NUMERIC_RULE_VERSION | typeof EXACT_RULE_VERSION | typeof EXACT_LITERAL_RULE_VERSION | typeof STRUCTURED_RULE_VERSION;
  readonly value_profile?: typeof NUMERIC_RULE_VALUE_PROFILE | typeof EXACT_UINT64_PROFILE;
  readonly language: 'typescript';
  readonly module_root: string;
  readonly roots: readonly string[];
}
export interface RuleConfigurationSources {
  readonly configuration: string;
  readonly base: string;
  readonly typescript: string;
  readonly rule_contract?: string;
  readonly collection_contract?: string;
  readonly predicate_contract?: string;
  readonly numeric_contract?: string;
  readonly exact_contract?: string;
  readonly literal_contract?: string;
  readonly structured_contract?: string;
  readonly field_contract?: string;
}
export interface ConfiguredRuleModule {
  readonly selector: string;
  readonly relative_path: string;
  readonly callable: string;
  readonly closure_sha256: string;
  readonly imports: readonly Readonly<{selector: string; path: string; symbol: string; local: string}>[];
}
export interface ConfiguredRulesPlan {
  readonly field_model_sha256?: string | null;
  readonly schema_version: 'domainspec.configured-rules-plan/v1-candidate' | 'domainspec.configured-rules-plan/v2-candidate' | 'domainspec.configured-rules-plan/v3-candidate' | 'domainspec.configured-rules-plan/v4-candidate' | 'domainspec.configured-rules-plan/v5-candidate' | 'domainspec.configured-rules-plan/v6-candidate' | 'domainspec.configured-rules-plan/v7-candidate' | 'domainspec.configured-rules-plan/v8-candidate';
  readonly selection: ConfiguredRuleSelection;
  readonly configuration_source_sha256: string;
  readonly configuration_value_sha256: string;
  readonly profile_digests: typeof PROFILED_SOURCE_DIGESTS;
  readonly certificate: ReturnType<typeof createCompiledProjectCertificate>;
  readonly modules: readonly ConfiguredRuleModule[];
  readonly artifacts: readonly PlannedArtifact[];
  readonly input_envelope: 'string-bool-direct-rule-refs/v1-candidate' | 'string-order-direct-rule-refs/v2-candidate' | 'scalar-collection-rule-values/v3-candidate' | 'scalar-collection-rule-predicates/v4-candidate' | 'json-safe-numeric-rules/v5-candidate' | 'exact-uint64-rule-inputs/v6-candidate' | 'exact-uint64-rule-literals/v7-candidate' | 'structured-rule-values/v8-candidate';
  readonly authority_effect: 'none';
  readonly plan_sha256: string;
}
const fail = (message: string): never => { throw new Error('DS_CONFIGURED_RULE:' + message); };
// PCR-05 portable naming policy; parity is exercised against its location preview.
const reserved = new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul ' + Array.from({length: 9}, (_, i) => `com${i + 1} lpt${i + 1}`).join(' ')).split(' '));
function keys(value: unknown, expected: readonly string[]): asserts value is Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join('|') !== [...expected].sort().join('|')) fail('unknown or missing fields');
}
const pascal = (s: string) => s.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
const quote = JSON.stringify;
const freeze = <T>(value: T): T => {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.values(value).forEach(freeze); Object.freeze(value);
  }
  return value;
};

function dependencies(expression: RuleExpression): string[] {
  if (expression.op === 'rule_ref') return [expression.selector];
  if (expression.op === 'all' || expression.op === 'any') return expression.terms.flatMap(dependencies);
  if (expression.op === 'not') return dependencies(expression.term);
  if (expression.op === 'exists' || expression.op === 'exactly_one' || expression.op === 'unique') return dependencies(expression.where);
  return [];
}
function valueSource(value: ValueExpression, parameters: TypedRuleContract['parameters']): string {
  if (value.op === 'literal' && (value.type === 'String' || value.type === 'Bool')) return quote(value.value);
  if (value.op === 'path' && value.properties.length === 0) {
    const index = parameters.findIndex(p => p.name === value.root);
    if (index >= 0) return `p${index}`;
  }
  return fail('unsupported value; only String/Bool literals and direct parameter paths');
}
function directScalar(value: ValueExpression, parameters: TypedRuleContract['parameters']): string | null {
  if (value.op === 'literal' && (value.type === 'String' || value.type === 'Bool')) return value.type;
  if (value.op === 'path' && value.properties.length === 0) {
    const parameter = parameters.find(p => p.name === value.root);
    if (!parameter || parameter.type.kind !== 'scalar') return null;
    return parameter.type.name;
  }
  return null;
}
function expressionSource(expression: RuleExpression, rule: TypedRuleContract, imports: ConfiguredRuleModule['imports'], stringOrder: boolean, collectionValues: boolean): string {
  if (expression.op === 'all' || expression.op === 'any') {
    if (!expression.terms.length) return expression.op === 'all' ? 'true' : 'false';
    return '(' + expression.terms.map(e => expressionSource(e, rule, imports, stringOrder, collectionValues)).join(expression.op === 'all' ? ' && ' : ' || ') + ')';
  }
  if (expression.op === 'not') return `!(${expressionSource(expression.term, rule, imports, stringOrder, collectionValues)})`;
  if (expression.op === 'eq') {
    if (collectionValues && (directScalar(expression.left, rule.parameters) === null || directScalar(expression.right, rule.parameters) === null))
      return fail('collection operators unsupported in v3');
    return `(${valueSource(expression.left, rule.parameters)} === ${valueSource(expression.right, rule.parameters)})`;
  }
  if (expression.op === 'lt') {
    if (!stringOrder || directScalar(expression.left, rule.parameters) !== 'String' || directScalar(expression.right, rule.parameters) !== 'String')
      return fail('unsupported lt; v2 accepts direct String operands only');
    return `(${valueSource(expression.left, rule.parameters)} < ${valueSource(expression.right, rule.parameters)})`;
  }
  if (expression.op === 'rule_ref') {
    const dependency = imports.find(i => i.selector === expression.selector);
    if (!dependency) return fail('unplanned Rule reference:' + expression.selector);
    const args = [...expression.arguments].sort((a, b) => a.parameter < b.parameter ? -1 : a.parameter > b.parameter ? 1 : 0);
    // Computed literal keys avoid special __proto__ object-literal behavior.
    return `${dependency.local}({${args.map(a => `[${quote(a.parameter)}]:${valueSource(a.value, rule.parameters)}`).join(',')}})`;
  }
  return fail('unsupported operator:' + expression.op);
}
type ScalarCollectionType = Readonly<{kind:'list'|'set';element:Readonly<{kind:'scalar';name:'String'|'Bool'|'UInt64'}>}>;
const scalarCollection = (type: TypedType, numeric=false): type is ScalarCollectionType =>
  (type.kind === 'list' || type.kind === 'set') && type.element.kind === 'scalar' && (type.element.name === 'String' || type.element.name === 'Bool' || numeric && type.element.name === 'UInt64');
const nativeScalar = (name:string, exact=false) => name === 'Bool' ? 'boolean' : name === 'UInt64' ? exact ? 'bigint' : 'number' : 'string';
const inputScalar = (name:string, exact=false) => name === 'UInt64' && exact ? 'RuleUInt64Input' : nativeScalar(name);
const parameterType = (type: TypedType, numeric=false, exact=false): string => type.kind === 'scalar' ? inputScalar(type.name,exact) :
  scalarCollection(type,numeric) ? `readonly ${inputScalar(type.element.name,exact)}[]` : fail('unsupported collection parameter type');
const collectionSupport = `type RuleScalar = string|boolean;
const normalizeRuleCollection = <T extends RuleScalar>(input:unknown,element:'string'|'boolean',unique:boolean):readonly T[]=>{
  if(!Array.isArray(input)||Object.getPrototypeOf(input)!==Array.prototype) throw new TypeError('RULE_INPUT');
  const descriptors:Record<string,PropertyDescriptor>=Object.getOwnPropertyDescriptors(input),length=descriptors.length?.value;
  if(!Number.isSafeInteger(length)||length<0||Reflect.ownKeys(descriptors).length!==length+1) throw new TypeError('RULE_INPUT');
  const values:T[]=[];
  for(let i=0;i<length;i++){const d=descriptors[String(i)];if(!d||!Object.hasOwn(d,'value')||!d.enumerable||typeof d.value!==element) throw new TypeError('RULE_INPUT');values.push(d.value as T);}
  if(unique){if(new Set(values).size!==values.length) throw new TypeError('RULE_INPUT');values.sort((a,b)=>{const ka=typeof a==='string'?'S'+a:a?'B1':'B0',kb=typeof b==='string'?'S'+b:b?'B1':'B0';return ka<kb?-1:ka>kb?1:0;});}
  return Object.freeze(values);
};
`;
function render(rule: TypedRuleContract, module: ConfiguredRuleModule, stringOrder: boolean, collectionValues: boolean, collectionPredicates: boolean, numeric:boolean, exact:boolean): string {
  if (rule.parameters.some(p => p.type.kind === 'scalar' ? !['String', 'Bool', ...(numeric ? ['UInt64'] : [])].includes(p.type.name) : !collectionValues || !scalarCollection(p.type,numeric))) fail('unsupported parameter type; String/Bool' + (collectionValues ? ' and scalar list/set only' : ' only'));
  const types = rule.parameters.map(p => `readonly ${quote(p.name)}:${parameterType(p.type,numeric,exact)}`).join(';');
  const checks = rule.parameters.map(p => p.type.kind === 'scalar' && p.type.name !== 'UInt64' ? `typeof descriptors[${quote(p.name)}]?.value !== ${quote(nativeScalar(p.type.name))}` :
    `!Object.hasOwn(descriptors[${quote(p.name)}]??{},'value') || descriptors[${quote(p.name)}]?.enumerable !== true`);
  const locals = rule.parameters.map((p, i) => {
    if (p.type.kind === 'scalar' && p.type.name === 'UInt64') return `  const p${i} = normalizeRuleUInt64(descriptors[${quote(p.name)}]!.value);`;
    if (p.type.kind === 'scalar') return `  const p${i} = descriptors[${quote(p.name)}]!.value as ${parameterType(p.type)};`;
    if (!scalarCollection(p.type,numeric)) return fail('unsupported collection parameter type');
    const element = nativeScalar(p.type.element.name,exact);
    return `  const p${i} = normalizeRuleCollection<${element}>(descriptors[${quote(p.name)}]!.value,${quote(element)},${p.type.kind === 'set'});`;
  }).join('\n');
  return module.imports.map(i => `import { ${i.symbol} as ${i.local} } from ${quote(i.path)};\n`).join('') + (exact ? exactRuleSupport : numeric ? numericRuleSupport : collectionValues ? collectionSupport : '') +
    `// domainspec-rule: ${quote(module.selector)}; closure: ${module.closure_sha256}\n` +
    `export const ${module.callable} = (parameters:Readonly<{${types}}>):boolean => {\n` +
    `  if (parameters === null || typeof parameters !== 'object' || Array.isArray(parameters)) throw new TypeError('RULE_INPUT');\n` +
    `  const descriptors = Object.getOwnPropertyDescriptors(parameters);\n` +
    `  if (Reflect.ownKeys(parameters).length !== ${rule.parameters.length}${checks.length ? ' || ' + checks.join(' || ') : ''}) throw new TypeError('RULE_INPUT');\n` +
    locals + '\n' + `  return ${collectionPredicates ? collectionPredicateSource(rule, module.imports,numeric,exact) : expressionSource(rule.expression, rule, module.imports, stringOrder, collectionValues)};\n};\n`;
}

/** Pure artifact planning from a checked graph and exact PCR-05 source selection.
 * No source reread, old-renderer rewriting, dynamic AST interpreter or activation.
 */
export function planConfiguredRules(graph: CompiledProjectGraph, selection: ConfiguredRuleSelection, sources: RuleConfigurationSources): ConfiguredRulesPlan {
  assertCompiledProjectSnapshot(graph);
  const structuredValues = selection.schema_version === STRUCTURED_RULE_VERSION;
  const exactLiterals = structuredValues || selection.schema_version === EXACT_LITERAL_RULE_VERSION;
  const exact = exactLiterals || selection.schema_version === EXACT_RULE_VERSION;
  const numeric = exact || selection.schema_version === NUMERIC_RULE_VERSION;
  keys(selection, ['schema_version', 'language', 'module_root', 'roots', ...(numeric ? ['value_profile'] : [])]);
  if (numeric && selection.value_profile !== (exact ? EXACT_UINT64_PROFILE : NUMERIC_RULE_VALUE_PROFILE)) fail('unsupported numeric value profile');
  const collectionPredicates = numeric || selection.schema_version === COLLECTION_PREDICATE_RULE_VERSION;
  const collectionValues = collectionPredicates || selection.schema_version === COLLECTION_VALUE_RULE_VERSION;
  const stringOrder = collectionValues || selection.schema_version === STRING_ORDER_RULE_VERSION;
  keys(sources, ['configuration', 'base', 'typescript', ...(stringOrder ? ['rule_contract'] : []), ...(collectionValues ? ['collection_contract'] : []), ...(collectionPredicates ? ['predicate_contract'] : []), ...(numeric ? ['numeric_contract'] : []), ...(exact ? ['exact_contract'] : []), ...(exactLiterals ? ['literal_contract'] : []), ...(structuredValues ? ['structured_contract', 'field_contract'] : [])]);
  if ((!stringOrder && selection.schema_version !== CONFIGURED_RULE_VERSION) || selection.language !== 'typescript') fail('unsupported selection');
  if (typeof selection.module_root !== 'string' || !/^[a-z][a-z0-9-]*(?:\/[a-z][a-z0-9-]*)*$/.test(selection.module_root)) fail('unsafe module root');
  if (selection.module_root.split('/').some(p => reserved.has(p))) fail('reserved module root');
  for (const key of ['configuration', 'base', 'typescript'] as const) {
    const expected = key === 'configuration' ? RULE_CONFIGURATION_SHA256 : PROFILED_SOURCE_DIGESTS[key];
    if (typeof sources[key] !== 'string' || sha256(sources[key]) !== expected) fail('source drift:' + key);
  }
  if (stringOrder && (typeof sources.rule_contract !== 'string' || sha256(sources.rule_contract) !== STRING_ORDER_RULE_CONTRACT_SHA256)) fail('source drift:rule_contract');
  if (collectionValues && (typeof sources.collection_contract !== 'string' || sha256(sources.collection_contract) !== COLLECTION_VALUE_RULE_CONTRACT_SHA256)) fail('source drift:collection_contract');
  if (collectionPredicates && (typeof sources.predicate_contract !== 'string' || sha256(sources.predicate_contract) !== COLLECTION_PREDICATE_RULE_CONTRACT_SHA256)) fail('source drift:predicate_contract');
  if (numeric && (typeof sources.numeric_contract !== 'string' || sha256(sources.numeric_contract) !== NUMERIC_RULE_CONTRACT_SHA256)) fail('source drift:numeric_contract');
  if (exact && (typeof sources.exact_contract !== 'string' || sha256(sources.exact_contract) !== EXACT_RULE_CONTRACT_SHA256)) fail('source drift:exact_contract');
  if (exactLiterals && (typeof sources.literal_contract !== 'string' || sha256(sources.literal_contract) !== EXACT_LITERAL_RULE_CONTRACT_SHA256)) fail('source drift:literal_contract');
  if (structuredValues && (typeof sources.structured_contract !== 'string' || sha256(sources.structured_contract) !== STRUCTURED_RULE_CONTRACT_SHA256 || typeof sources.field_contract !== 'string' || sha256(sources.field_contract) !== EXACT_FIELD_CONTRACT_SHA256)) fail('source drift:structured values');
  const config = JSON.parse(sources.configuration) as {types: Array<{kind: string; role: string; blocked_by: string[]}>};
  const cell = config.types.find(t => t.kind === 'Rule');
  if (!cell || cell.blocked_by.length || cell.role !== 'domain/rules') return fail('Rule configuration is not ready');
  const profile = JSON.parse(sources.typescript) as {constraints: Array<{constraint_id: string; expected: string}>};
  const location = profile.constraints.find(c => c.constraint_id === 'typescript.rule-location');
  if (!location) return fail('missing Rule location constraint');
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.some(s => typeof s !== 'string') || new Set(selection.roots).size !== selection.roots.length) fail('roots must be a nonempty unique selector set');
  const roots = [...selection.roots].sort();
  const contracts = new Map<string, TypedRuleContract>();
  const dataRoots = new Set<string>();
  const closures = new Map<string, string>();
  for (const root of roots) {
    const node = selectCompiledProjectNode(graph, root);
    if (node.kind !== 'Rule' || node.typed_closure?.schema_version !== 'domainspec.typed-rule-closure/v1') fail('selected root is not a typed Rule:' + root);
    for (const member of node.typed_closure!.nodes) {
      if (member.typed_contract.schema_version === 'domainspec.typed-rule/v2' && !exactLiterals) fail('typed Rule v2 requires exact-literal selection:' + member.selector);
      if (structuredValues && ['Entity', 'Value Object', 'Enum'].includes(member.kind)) {dataRoots.add(member.selector);continue;}
      if (member.kind !== 'Rule' || (member.typed_contract.schema_version !== 'domainspec.typed-rule/v1' && member.typed_contract.schema_version !== 'domainspec.typed-rule/v2')) fail('unsupported named/record/collection dependency:' + member.selector);
      contracts.set(member.selector, member.typed_contract as TypedRuleContract);
    }
  }
  const fields = structuredValues && dataRoots.size ? compileSelectedProjectFields(graph, {
    schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256,
    graph_sha256: createCompiledProjectCertificate(graph).graph_sha256, roots: [...dataRoots].sort(), bindings: [],
  }, sources.field_contract!) : null;
  const modules: ConfiguredRuleModule[] = [];
  const identifiers = new Map([...contracts.keys()].sort().map(selector => {
    const node = graph.nodes.find(n => n.selector === selector)!;
    for (const id of [node.feature_id, node.node_id]) {
      if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(id) || reserved.has(id)) fail('unsupported portable identifier:' + id);
    }
    const closure = selectCompiledProjectNode(graph, selector).typed_closure!;
    closures.set(selector, closure.closure_sha256);
    const relative = `src/${cell.role}/${node.node_id}.ts`;
    if (!new RegExp(location.expected).test(relative)) fail('profile path mismatch');
    return [selector, {relative_path: `${selection.module_root}/features/${node.feature_id}/${relative}`, callable: 'rule' + pascal(node.node_id)}];
  }));
  for (const [selector, entry] of identifiers) {
    const rule = contracts.get(selector)!;
    const imports = [...new Set(dependencies(rule.expression))].sort().map((dependency, i) => {
      const target = identifiers.get(dependency);
      if (!target) return fail('missing dependency module:' + dependency);
      const relative = path.posix.relative(path.posix.dirname(entry.relative_path), target.relative_path).replace(/\.ts$/, '.js');
      return {selector: dependency, path: relative.startsWith('.') ? relative : './' + relative, symbol: target.callable, local: `dependency${i}`};
    });
    modules.push({selector, ...entry, closure_sha256: closures.get(selector)!, imports});
  }
  const artifacts = modules.map(module => {
    const content = structuredValues ? renderStructuredRule(contracts.get(module.selector)!, module, fields?.model??null) : render(contracts.get(module.selector)!, module, stringOrder, collectionValues, collectionPredicates,numeric,exact);
    return {relative_path: module.relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};
  });
  const body = {schema_version: structuredValues ? 'domainspec.configured-rules-plan/v8-candidate' as const : exactLiterals ? 'domainspec.configured-rules-plan/v7-candidate' as const : exact ? 'domainspec.configured-rules-plan/v6-candidate' as const : numeric ? 'domainspec.configured-rules-plan/v5-candidate' as const : collectionPredicates ? 'domainspec.configured-rules-plan/v4-candidate' as const : collectionValues ? 'domainspec.configured-rules-plan/v3-candidate' as const : stringOrder ? 'domainspec.configured-rules-plan/v2-candidate' as const : 'domainspec.configured-rules-plan/v1-candidate' as const,
    selection: {...selection, roots}, configuration_source_sha256: RULE_CONFIGURATION_SHA256,
    configuration_value_sha256: sha256(canonicalJson(config)), profile_digests: PROFILED_SOURCE_DIGESTS,
    certificate: createCompiledProjectCertificate(graph), modules, artifacts,
    ...(structuredValues ? {field_model_sha256: fields?.model.model_sha256??null} : {}),
    input_envelope: structuredValues ? 'structured-rule-values/v8-candidate' as const : exactLiterals ? 'exact-uint64-rule-literals/v7-candidate' as const : exact ? 'exact-uint64-rule-inputs/v6-candidate' as const : numeric ? 'json-safe-numeric-rules/v5-candidate' as const : collectionPredicates ? 'scalar-collection-rule-predicates/v4-candidate' as const : collectionValues ? 'scalar-collection-rule-values/v3-candidate' as const : stringOrder ? 'string-order-direct-rule-refs/v2-candidate' as const : 'string-bool-direct-rule-refs/v1-candidate' as const, authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
