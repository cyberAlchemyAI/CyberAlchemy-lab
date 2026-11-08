import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {checkTypedRulePolicy, decodeTypedRulePolicyContract, TYPED_POLICY_RULES_VERSION} from '../typed-backend/policy-rules.js';
import {decodeTypedRuleContract, type TypedRuleContract, type TypedType, type ValueExpression} from '../typed-operation/contracts.js';
import type {PlannedArtifact} from './contracts.js';
import {planConfiguredRustRules, RUST_RULE_SELECTION_VERSION} from './configured-rust-rules.js';
import {rustPascal, rustSelectorModule, rustSelectorType, rustSnake, rustString} from './configured-rust-values.js';

export const RUST_POLICY_SELECTION_VERSION = 'domainspec.configured-rust-policies-selection/v1-candidate';
export const RUST_POLICY_PROTOCOL = 'rust.bound-policy/v1-candidate';
export const RUST_POLICY_CONTRACT_SHA256 = 'bdafb20355aa47c992719fd6d0205d78a406d74e27729e561ec274805fb579f9';
export interface RustPolicySelection {readonly schema_version: typeof RUST_POLICY_SELECTION_VERSION; readonly language: 'rust'; readonly rule_selection: typeof RUST_RULE_SELECTION_VERSION; readonly module_root: string; readonly roots: readonly string[]; readonly boundary_sha256: string; readonly field_compilation_sha256: string;}
export interface RustPolicySources {readonly rust_contract: string; readonly rule_contract: string;}
function fail(reason: string): never {throw new TypeError('DS_RUST_POLICY:' + reason);}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
function rustType(type: TypedType): string {
  if (type.kind === 'scalar') return type.name === 'String' ? 'String' : type.name === 'Bool' ? 'bool' : 'u64';
  if (type.kind === 'named') return rustSelectorType(type.selector);
  if (type.kind === 'optional') return `Option<${rustType(type.element)}>`;
  if (type.kind === 'list') return `Vec<${rustType(type.element)}>`;
  if (type.kind === 'set') return `std::collections::BTreeSet<${rustType(type.element)}>`;
  return fail('anonymous sum Policy inputs require a named declaration');
}
function targetVariant(selector: string): string {
  const [feature, node, ...rest] = selector.split(':'); if (!feature || !node || rest.length) return fail('qualified target required');
  return `F${feature.length}${rustPascal(feature)}N${node.length}${rustPascal(node)}`;
}
export function rustPolicyPath(moduleRoot: string, selector: string): string {return `${moduleRoot}/src/domain/policies/${rustSelectorModule(selector)}.rs`;}

export function planConfiguredRustPolicies(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields, selection: RustPolicySelection, sources: RustPolicySources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); assertCompiledProjectFields(fields); assertInterfaceData(selection); assertInterfaceData(sources);
  if (Object.keys(sources).sort().join('|') !== 'rule_contract|rust_contract' || sha256(sources.rust_contract) !== RUST_POLICY_CONTRACT_SHA256) fail('contract drift');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.schema_version !== RUST_POLICY_SELECTION_VERSION || selection.language !== 'rust' || selection.rule_selection !== RUST_RULE_SELECTION_VERSION) fail('unsupported selection');
  if (selection.boundary_sha256 !== boundary.boundary_sha256 || selection.field_compilation_sha256 !== fields.compilation_sha256 || boundary.certificate.graph_sha256 !== certificate.graph_sha256 || fields.certificate.graph_sha256 !== certificate.graph_sha256 || fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('stale or cross-graph inputs');
  if (selection.module_root.split('/').some(part => {try {rustSnake(part); return false;} catch {return true;}})) fail('portable module root required');
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('bounded unique roots required');
  const roots = [...selection.roots].sort(), nodes = new Map(graph.nodes.map(node => [node.selector, node])), declarations = new Map(fields.model.declarations.map(row => [row.selector, row]));
  const contracts = new Map<string, ReturnType<typeof decodeTypedRulePolicyContract>>();
  for (const selector of roots) {
    const node = nodes.get(selector), evidence = boundary.value_bindings.core_contracts.find(row => row.owner.selector === selector);
    if (node?.kind !== 'Policy' || evidence?.kind !== 'Policy' || (node.body.typed_contract as {schema_version?: string})?.schema_version !== TYPED_POLICY_RULES_VERSION) fail('selected root is not a bound typed Policy v2:' + selector);
    contracts.set(selector, decodeTypedRulePolicyContract(node.body.typed_contract));
  }
  const ruleContracts = [...nodes.values()].filter(node => node.kind === 'Rule').map(node => ({selector: node.selector, contract: decodeTypedRuleContract(node.body.typed_contract)}));
  for (const contract of contracts.values()) checkTypedRulePolicy(contract, fields.model.declarations, ruleContracts);
  const ruleRoots = [...new Set([...contracts.values()].flatMap(contract => contract.cases.map(row => row.rule.selector)))].sort();
  const rules = planConfiguredRustRules(graph, fields, {schema_version: selection.rule_selection, language: 'rust', module_root: selection.module_root, roots: ruleRoots, field_compilation_sha256: fields.compilation_sha256}, sources.rule_contract);
  const properties = new Map([...declarations.values()].flatMap(row => row.kind === 'Enum' ? [] : row.contract.properties.map(property => [property.ontology_property, {owner: row.selector, property}] as const)));
  const ruleBySelector = new Map<string, TypedRuleContract>(ruleContracts.map(row => [row.selector, row.contract]));
  const modules = roots.map(selector => {
    const contract = contracts.get(selector)!, name = rustPascal(selector.split(':')[1]!), strategy = `${name}Strategy`, symbol = rustSnake(selector.split(':')[1]!);
    const scope = new Map(contract.inputs.map(input => [input.name, input.type]));
    const value = (expression: ValueExpression): {type: TypedType; reference: string} => {
      if (expression.op === 'literal') {
        const type: TypedType = {kind: 'scalar', name: expression.type};
        if (expression.type === 'String') return {type, reference: `&String::from(${rustString(String(expression.value))})`};
        if (expression.type === 'Bool') return {type, reference: expression.value ? '&true' : '&false'};
        const integer = BigInt(expression.value); if (integer < 0n || integer > 18446744073709551615n) return fail('UInt64 literal out of range'); return {type, reference: `&${integer}u64`};
      }
      if (expression.op === 'variant') {
        const owner = [...declarations.values()].find(row => row.kind === 'Enum' && row.contract.variants.some(variant => variant.ontology_variant === expression.selector));
        if (!owner || owner.kind !== 'Enum') return fail('unknown Enum variant'); const variant = owner.contract.variants.find(row => row.ontology_variant === expression.selector)!; if (variant.payload !== null) return fail('payload variant argument unsupported');
        return {type: {kind: 'named', selector: owner.selector}, reference: `&${rustSelectorType(owner.selector)}::${rustPascal(variant.name)}`};
      }
      if (expression.op === 'to_set') {const inner = value(expression.value); if (inner.type.kind !== 'list') return fail('to_set requires list'); return {type: {kind: 'set', element: inner.type.element}, reference: `&(${inner.reference}.iter().cloned().collect::<std::collections::BTreeSet<_>>())`};}
      let type = scope.get(expression.root) ?? fail('unknown Policy input:' + expression.root), reference = rustSnake(expression.root);
      for (const ontology of expression.properties) {const found = properties.get(ontology); if (!found || type.kind !== 'named' || type.selector !== found.owner) return fail('property owner mismatch:' + ontology); reference += `.${rustSnake(found.property.name)}()`; type = found.property.type;}
      return {type, reference};
    };
    const targets = [...new Set([...contract.cases.map(row => row.target), contract.default_target])].sort();
    for (const target of targets) {const node = nodes.get(target); if (!node || !['Operation', 'Calculation'].includes(node.kind)) fail('invalid strategy target:' + target);}
    const cases = contract.cases.map(row => {
      const rule = ruleBySelector.get(row.rule.selector) ?? fail('missing Rule:' + row.rule.selector), supplied = new Map(row.rule.arguments.map(argument => [argument.parameter, argument.value]));
      const call = rule.parameters.map(parameter => value(supplied.get(parameter.name) ?? fail('missing Rule argument')).reference).join(', ');
      return {target: row.target, rule: row.rule.selector, call: `crate::domain::rules::${rustSelectorModule(row.rule.selector)}::${rustSnake(row.rule.selector.split(':')[1]!)}(${call})`};
    });
    const content = `// Generated DomainSpec Rust Policy.\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_CONTRACT_SHA256: &str = ${rustString(sha256(canonicalJson(contract)))};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(RUST_POLICY_PROTOCOL)};\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash)]\npub enum ${strategy} {\n${targets.map(target => `    ${targetVariant(target)},`).join('\n')}\n}\n\nimpl ${strategy} {\n    pub const fn selector(self) -> &'static str {\n        match self {\n${targets.map(target => `            Self::${targetVariant(target)} => ${rustString(target)},`).join('\n')}\n        }\n    }\n}\n\npub fn ${symbol}(${contract.inputs.map(input => `${rustSnake(input.name)}: &${rustType(input.type)}`).join(', ')}) -> ${strategy} {\n${cases.map(row => `    if ${row.call} { return ${strategy}::${targetVariant(row.target)}; }`).join('\n')}\n    ${strategy}::${targetVariant(contract.default_target)}\n}\n`;
    const relative_path = rustPolicyPath(selection.module_root, selector);
    return {selector, symbol, strategy, relative_path, inputs: contract.inputs, targets, cases: cases.map(({call: _call, ...row}) => row), default_target: contract.default_target, contract_sha256: sha256(canonicalJson(contract)), artifact: artifact(relative_path, content)};
  });
  const artifacts = [...rules.artifacts, ...modules.map(module => module.artifact)].sort((left, right) => left.relative_path < right.relative_path ? -1 : 1);
  const body = {schema_version: 'domainspec.configured-rust-policies-plan/v1-candidate' as const, selection: {...selection, roots}, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256, contract_sha256: RUST_POLICY_CONTRACT_SHA256, protocol_id: RUST_POLICY_PROTOCOL, rule_plan_sha256: rules.plan_sha256, rule_dependencies: rules.modules, modules: modules.map(({artifact: _artifact, ...module}) => module), artifacts, authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
