import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectFields, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {decodeTypedRuleContract, type RuleExpression, type TypedRuleContract, type TypedType, type ValueExpression} from '../typed-operation/contracts.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import type {PlannedArtifact} from './contracts.js';
import {rustPascal, rustSelectorModule, rustSelectorType, rustSnake, rustString} from './configured-rust-values.js';

export const RUST_RULE_SELECTION_VERSION = 'domainspec.configured-rust-rules-selection/v1-candidate';
export const RUST_RULE_PROTOCOL = 'rust.bound-rule/v1-candidate';
export const RUST_RULE_CONTRACT_SHA256 = '9272b1abdc2af0c2a8e0cc3ad36804d772e609a0121d00ee87de54acdab0d5bf';
export interface RustRuleSelection {readonly schema_version: typeof RUST_RULE_SELECTION_VERSION; readonly language: 'rust'; readonly module_root: string; readonly roots: readonly string[]; readonly field_compilation_sha256: string | null;}
type Mode = 'borrowed' | 'owned' | 'copy';
type Rendered = {code: string; type: TypedType; mode: Mode};
function fail(reason: string): never {throw new TypeError('DS_RUST_RULE:' + reason);}
const same = (a: TypedType, b: TypedType) => canonicalJson(a) === canonicalJson(b);
const isCopy = (type: TypedType) => type.kind === 'scalar' && type.name !== 'String';
const borrowed = (value: Rendered) => value.mode === 'borrowed' ? value.code : `&(${value.code})`;
const artifact = (relative_path: string, content: string): PlannedArtifact => ({relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)});
function rustType(type: TypedType): string {
  if (type.kind === 'scalar') return type.name === 'String' ? 'String' : type.name === 'Bool' ? 'bool' : 'u64';
  if (type.kind === 'named') return rustSelectorType(type.selector);
  if (type.kind === 'optional') return `Option<${rustType(type.element)}>`;
  if (type.kind === 'list') return `Vec<${rustType(type.element)}>`;
  if (type.kind === 'set') return `BTreeSet<${rustType(type.element)}>`;
  return fail('anonymous sum parameters require a named declaration');
}
function functionPath(selector: string): string {return `crate::domain::rules::${rustSelectorModule(selector)}::${rustSnake(selector.split(':')[1]!)}`;}
function rulePath(root: string, selector: string): string {return `${root}/src/domain/rules/${rustSelectorModule(selector)}.rs`;}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}

export function planConfiguredRustRules(graph: CompiledProjectGraph, fields: CompiledProjectFields | null, selection: RustRuleSelection, contractSource: string) {
  assertCompiledProjectSnapshot(graph); if (fields) assertCompiledProjectFields(fields); assertInterfaceData(selection);
  if (sha256(contractSource) !== RUST_RULE_CONTRACT_SHA256) fail('contract drift');
  if (selection.schema_version !== RUST_RULE_SELECTION_VERSION || selection.language !== 'rust' || selection.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null)) fail('stale or unsupported selection');
  selection.module_root.split('/').forEach(rustSnake);
  if (!Array.isArray(selection.roots) || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length || selection.roots.length === 0 && graph.nodes.some(node => node.kind === 'Rule')) fail('bounded unique roots required');
  const declarations = new Map(fields?.model.declarations.map(row => [row.selector, row]) ?? []);
  const properties = new Map([...declarations.values()].flatMap(row => row.kind === 'Enum' ? [] : row.contract.properties.map(property => [property.ontology_property, {owner: row.selector, property}] as const)));
  const rules = new Map<string, TypedRuleContract>();
  for (const node of graph.nodes) if (node.kind === 'Rule') rules.set(node.selector, decodeTypedRuleContract(node.body.typed_contract));
  const modules = selection.roots.map(selector => {
    const contract = rules.get(selector) ?? fail('selected root is not a typed Rule:' + selector);
    const symbol = rustSnake(selector.split(':')[1]!);
    const renderValue = (value: ValueExpression, scopes: ReadonlyMap<string, TypedType>): Rendered => {
      if (value.op === 'literal') {
        if (value.type === 'String') return {code: `String::from(${rustString(String(value.value))})`, type: {kind: 'scalar', name: 'String'}, mode: 'owned'};
        if (value.type === 'Bool') return {code: value.value ? 'true' : 'false', type: {kind: 'scalar', name: 'Bool'}, mode: 'copy'};
        const integer = BigInt(value.value); if (integer < 0n || integer > 18446744073709551615n) return fail('UInt64 literal out of range');
        return {code: integer.toString() + 'u64', type: {kind: 'scalar', name: 'UInt64'}, mode: 'copy'};
      }
      if (value.op === 'variant') {
        const [owner] = [...declarations].filter(([, declaration]) => declaration.kind === 'Enum' && declaration.contract.variants.some(variant => variant.ontology_variant === value.selector));
        if (!owner) return fail('unknown or payload variant:' + value.selector);
        const declaration = owner[1]; if (declaration.kind !== 'Enum') return fail('variant owner');
        const variant = declaration.contract.variants.find(row => row.ontology_variant === value.selector)!; if (variant.payload !== null) return fail('payload variant cannot be a value literal');
        return {code: `${rustSelectorType(owner[0])}::${rustPascal(variant.name)}`, type: {kind: 'named', selector: owner[0]}, mode: 'owned'};
      }
      if (value.op === 'to_set') {
        const source = renderValue(value.value, scopes); if (source.type.kind !== 'list') return fail('to_set requires list');
        return {code: `${source.code}.iter().cloned().collect::<BTreeSet<_>>()`, type: {kind: 'set', element: source.type.element}, mode: 'owned'};
      }
      let type = scopes.get(value.root); if (!type) return fail('unknown path root:' + value.root);
      let code = rustSnake(value.root), mode: Mode = 'borrowed';
      for (const ontologyProperty of value.properties) {
        const found = properties.get(ontologyProperty); if (!found || type.kind !== 'named' || type.selector !== found.owner) return fail('property owner mismatch:' + ontologyProperty);
        code += `.${rustSnake(found.property.name)}()`; type = found.property.type; mode = 'borrowed';
      }
      return {code, type, mode: value.properties.length && isCopy(type) ? 'borrowed' : mode};
    };
    const render = (expression: RuleExpression, scopes: ReadonlyMap<string, TypedType>): string => {
      if (expression.op === 'all' || expression.op === 'any') return '(' + expression.terms.map(term => render(term, scopes)).join(expression.op === 'all' ? ' && ' : ' || ') + ')';
      if (expression.op === 'not') return `!(${render(expression.term, scopes)})`;
      if (expression.op === 'eq' || expression.op === 'lt' || expression.op === 'set_equal' || expression.op === 'contains') {
        const left = renderValue(expression.left, scopes), right = renderValue(expression.right, scopes);
        if (expression.op === 'contains') {if (left.type.kind !== 'set' || !same(left.type.element, right.type)) return fail('contains type mismatch'); return `${left.code}.contains(${borrowed(right)})`;}
        if (!same(left.type, right.type)) return fail(expression.op + ' type mismatch');
        return `${borrowed(left)} ${expression.op === 'lt' ? '<' : '=='} ${borrowed(right)}`;
      }
      if (expression.op === 'rule_ref') {
        const target = rules.get(expression.selector) ?? fail('unavailable Rule reference:' + expression.selector), supplied = new Map(expression.arguments.map(argument => [argument.parameter, argument.value]));
        if (supplied.size !== target.parameters.length || target.parameters.some(parameter => !supplied.has(parameter.name))) return fail('Rule argument coverage:' + expression.selector);
        const values = target.parameters.map(parameter => {const value = renderValue(supplied.get(parameter.name)!, scopes); if (!same(value.type, parameter.type)) return fail('Rule argument type:' + expression.selector); return borrowed(value);});
        return `${functionPath(expression.selector)}(${values.join(', ')})`;
      }
      if (expression.op !== 'exists' && expression.op !== 'exactly_one' && expression.op !== 'unique') return fail('unsupported Rule operator');
      const collection = renderValue(expression.collection, scopes); if (collection.type.kind !== 'list' && collection.type.kind !== 'set') return fail(expression.op + ' collection required');
      const nested = new Map(scopes); nested.set(expression.binding, collection.type.element); const binding = rustSnake(expression.binding), predicate = render(expression.where, nested);
      if (expression.op === 'exists') return `${collection.code}.iter().any(|${binding}| ${predicate})`;
      if (expression.op === 'exactly_one') return `${collection.code}.iter().filter(|${binding}| ${predicate}).count() == 1`;
      if (expression.where.op !== 'eq' || canonicalJson(expression.where.left) !== canonicalJson(expression.where.right) || expression.where.left.op !== 'path') return fail('unique requires identical path equality');
      const key = renderValue(expression.where.left, nested); return `${collection.code}.iter().map(|${binding}| ${isCopy(key.type) ? `*${key.code}` : `${key.code}.clone()`}).collect::<BTreeSet<_>>().len() == ${collection.code}.len()`;
    };
    const scopes = new Map(contract.parameters.map(parameter => [parameter.name, parameter.type]));
    const parameters = contract.parameters.map(parameter => `${rustSnake(parameter.name)}: &${rustType(parameter.type)}`).join(', ');
    const expression = render(contract.expression, scopes);
    const needsSet = canonicalJson(contract).includes('"set"') || canonicalJson(contract).includes('"to_set"') || canonicalJson(contract).includes('"unique"');
    const content = `// Generated DomainSpec Rust Rule.\n${needsSet ? 'use std::collections::BTreeSet;\n\n' : ''}pub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_CONTRACT_SHA256: &str = ${rustString(sha256(canonicalJson(contract)))};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(RUST_RULE_PROTOCOL)};\n\npub fn ${symbol}(${parameters}) -> bool {\n    ${expression}\n}\n`;
    const relative_path = rulePath(selection.module_root, selector);
    return {selector, symbol, relative_path, contract_sha256: sha256(canonicalJson(contract)), artifact: artifact(relative_path, content)};
  });
  const body = {schema_version: 'domainspec.configured-rust-rules-plan/v1-candidate' as const, selection: {...selection, roots: [...selection.roots]}, field_compilation_sha256: fields?.compilation_sha256 ?? null, contract_sha256: RUST_RULE_CONTRACT_SHA256, protocol_id: RUST_RULE_PROTOCOL, modules: modules.map(({artifact: _artifact, ...row}) => row), artifacts: modules.map(row => row.artifact).sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
