import {assertCompiledProjectSnapshot, selectCompiledProjectNode, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectFields, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {decodeTypedRuleContract, type TypedType} from '../typed-operation/contracts.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import type {FactoryBinding, FactoryValidatorBinding} from './configured-factories.js';
import type {PlannedArtifact} from './contracts.js';
import type {planConfiguredRustRules} from './configured-rust-rules.js';
import {renderRustOwnedType, rustPascal, rustSelectorModule, rustSnake, rustString} from './configured-rust-values.js';

export const RUST_FACTORY_SELECTION_VERSION = 'domainspec.configured-rust-factories-selection/v1-candidate';
export const RUST_ENTITY_PROTOCOL = 'rust.validated-extensible-entity-factory/v1';
export const RUST_VALUE_OBJECT_PROTOCOL = 'rust.owned-value-object-factory/v1';
export const RUST_FACTORY_CONTRACT_SHA256 = '574e6c2a501195add3a8511f5baff755370268b579f171eae40a4460d4f4150f';
export interface RustFactorySelection {readonly schema_version: typeof RUST_FACTORY_SELECTION_VERSION; readonly language: 'rust'; readonly module_root: string; readonly field_compilation_sha256: string; readonly factories: readonly FactoryBinding[];}
type RulePlan = ReturnType<typeof planConfiguredRustRules>;
type RecordDeclaration = Extract<CompiledProjectFields['model']['declarations'][number], {kind: 'Entity' | 'Value Object'}>;
type BoundValidator = Readonly<{selector: string; expression: string; closure_sha256: string}>;
function fail(reason: string): never {throw new TypeError('DS_RUST_FACTORY:' + reason);}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
const artifact = (relative_path: string, content: string): PlannedArtifact => ({relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)});
const same = (left: TypedType, right: TypedType) => canonicalJson(left) === canonicalJson(right);
const ruleFunction = (selector: string) => `crate::domain::rules::${rustSelectorModule(selector)}::${rustSnake(selector.split(':')[1]!)}`;
const typePath = (root: string, selector: string) => `${root}/src/domain/types/${rustSelectorModule(selector)}.rs`;
function keys(value: unknown, expected: readonly string[]): void {if (!value || typeof value !== 'object' || Array.isArray(value) || canonicalJson(Object.keys(value).sort()) !== canonicalJson([...expected].sort())) fail('closed fields required');}

export function planConfiguredRustFactories(graph: CompiledProjectGraph, fields: CompiledProjectFields, rules: RulePlan, selection: RustFactorySelection, contractSource: string) {
  assertCompiledProjectSnapshot(graph); assertCompiledProjectFields(fields); assertInterfaceData(selection);
  if (sha256(contractSource) !== RUST_FACTORY_CONTRACT_SHA256) fail('contract drift');
  if (selection.schema_version !== RUST_FACTORY_SELECTION_VERSION || selection.language !== 'rust' || selection.field_compilation_sha256 !== fields.compilation_sha256) fail('stale or unsupported selection');
  selection.module_root.split('/').forEach(rustSnake);
  if (!rules || rules.schema_version !== 'domainspec.configured-rust-rules-plan/v1-candidate' || rules.selection.module_root !== selection.module_root || rules.field_compilation_sha256 !== fields.compilation_sha256) fail('current Rust Rule plan required');
  const declarations = new Map(fields.model.declarations.map(row => [row.selector, row])), records = [...declarations.values()].filter((row): row is RecordDeclaration => row.kind !== 'Enum');
  if (!Array.isArray(selection.factories) || !selection.factories.length || selection.factories.length > 256 || canonicalJson(selection.factories.map(row => row.selector).sort()) !== canonicalJson(records.map(row => row.selector).sort())) fail('complete factory coverage');
  const bindingMap: ReadonlyMap<string, FactoryBinding> = new Map(selection.factories.map(binding => [binding.selector, binding])); if (bindingMap.size !== selection.factories.length) fail('duplicate factory');
  const ruleContracts = new Map(graph.nodes.filter(node => node.kind === 'Rule').map(node => [node.selector, decodeTypedRuleContract(node.body.typed_contract)]));
  const ruleModules = new Map(rules.modules.map(module => [module.selector, module]));
  const endpoint = (owner: typeof records[number], argument: FactoryValidatorBinding['arguments'][number]) => {
    const segments = 'path' in argument ? argument.path! : [argument.field!]; if (!segments.length || segments.length > 32) return fail('validator path');
    let declaration = owner, property = declaration.contract.properties.find(row => row.name === segments[0]), code = `&input.${rustSnake(segments[0]!)}`;
    if (!property) return fail('unknown validator field');
    for (const segment of segments.slice(1)) {
      if (property.type.kind !== 'named') return fail('validator path requires named value');
      const next = declarations.get(property.type.selector); if (!next || next.kind === 'Enum') return fail('validator path requires owned record');
      declaration = next; property = declaration.contract.properties.find(row => row.name === segment); if (!property) return fail('unknown nested validator field');
      code = `${code}.${rustSnake(segment)}()`;
    }
    return {type: property.type, code};
  };
  const modules = records.map(declaration => {
    const binding = bindingMap.get(declaration.selector)!; keys(binding, ['selector', 'base_validators', 'extensions']);
    if (!Array.isArray(binding.base_validators) || !binding.base_validators.length || !Array.isArray(binding.extensions)) return fail('validator bindings required');
    const seenRules = new Set<string>();
    const compile = (validator: FactoryValidatorBinding): BoundValidator => {
      keys(validator, ['rule', 'arguments']);
      const contract = ruleContracts.get(validator.rule), module = ruleModules.get(validator.rule); if (!contract || !module) return fail('validator missing from Rust Rule plan:' + validator.rule);
      if (seenRules.has(validator.rule)) return fail('duplicate validator:' + validator.rule); seenRules.add(validator.rule);
      const supplied = new Map(validator.arguments.map(argument => [argument.parameter, argument])); if (supplied.size !== contract.parameters.length || contract.parameters.some(parameter => !supplied.has(parameter.name))) return fail('validator argument coverage');
      const args = contract.parameters.map(parameter => {const value = endpoint(declaration, supplied.get(parameter.name)!); if (!same(value.type, parameter.type)) return fail('validator argument type'); return value.code;});
      return {selector: validator.rule, expression: `${ruleFunction(validator.rule)}(${args.join(', ')})`, closure_sha256: module.contract_sha256};
    };
    const base = binding.base_validators.map(compile); if (declaration.kind === 'Value Object' && canonicalJson(base.map(row => row.selector).sort()) !== canonicalJson(declaration.invariant_refs)) return fail('Value Object invariant coverage');
    const extensionIds = new Set<string>();
    const extensions: {id: string; validators: BoundValidator[]}[] = binding.extensions.map(extension => {keys(extension, ['id', 'validators']); rustSnake(extension.id); if (extensionIds.has(extension.id) || !extension.validators.length) return fail('duplicate or empty extension'); extensionIds.add(extension.id); return {id: extension.id, validators: extension.validators.map(compile)};});
    const name = rustPascal(declaration.selector.split(':')[1]!), input = name + 'Input', factory = name + 'Factory', error = name + 'ValidationError', ordinal = {value: 0};
    const properties = declaration.contract.properties.map(property => ({property, rendered: renderRustOwnedType(property.type, name, ordinal)}));
    const support = [...new Set([...(extensions.length ? ['std::collections::BTreeSet'] : []), ...(declaration.kind === 'Entity' ? ['std::hash::{Hash, Hasher}'] : []), ...properties.flatMap(row => row.rendered.support)])].sort();
    const definitions = [...new Set(properties.flatMap(row => row.rendered.definitions))];
    const fieldLines = properties.map(({property, rendered}) => `    ${rustSnake(property.name)}: ${rendered.type},`).join('\n');
    const inputLines = properties.map(({property, rendered}) => `    pub ${rustSnake(property.name)}: ${rendered.type},`).join('\n');
    const getters = properties.map(({property, rendered}) => `    pub fn ${rustSnake(property.name)}(&self) -> &${rendered.type} { &self.${rustSnake(property.name)} }`).join('\n\n');
    const moves = properties.map(({property}) => `            ${rustSnake(property.name)}: input.${rustSnake(property.name)},`).join('\n');
    const identity = declaration.kind === 'Entity' ? declaration.contract.properties.find(property => property.identity)! : null;
    const equality = declaration.kind === 'Entity' ? `\nimpl PartialEq for ${name} { fn eq(&self, other: &Self) -> bool { self.${rustSnake(identity!.name)} == other.${rustSnake(identity!.name)} } }\nimpl Eq for ${name} {}\nimpl Hash for ${name} { fn hash<H: Hasher>(&self, state: &mut H) { self.${rustSnake(identity!.name)}.hash(state); } }\n` : '';
    const derives = declaration.kind === 'Entity' ? 'Clone, Debug' : 'Clone, Debug, PartialEq, Eq, Hash';
    const enable = extensions.map(extension => `    pub fn with_${rustSnake(extension.id)}(mut self) -> Self { self.extensions.insert(${rustString(extension.id)}); self }`).join('\n\n');
    const checks = [...base.map(row => ({...row, condition: null as string | null})), ...extensions.flatMap(extension => extension.validators.map(row => ({...row, condition: extension.id})))].map(row => `${row.condition ? `        if self.extensions.contains(${rustString(row.condition)}) && !${row.expression}` : `        if !${row.expression}`} { failures.push(${rustString(row.selector)}); }`).join('\n');
    const valueChecks = checks.replaceAll('&input.', '&value.');
    const references = fields.model.bindings.filter(row => row.owner === declaration.selector);
    const referenceConst = `pub const DOMAINSPEC_FIELD_BINDINGS: &[(&str, &str, &str, &str)] = &[\n${references.map(row => `    (${rustString(row.field)}, ${rustString(row.kind)}, ${rustString(row.target)}, ${rustString(row.projection.join('.'))}),`).join('\n')}\n];\n`;
    const factoryBody = extensions.length ? ` { extensions: BTreeSet<&'static str> }` : ';';
    const factoryValue = extensions.length ? `${factory}::default()` : factory;
    const content = `// Generated DomainSpec Rust owned factory.\n${support.map(item => `use ${item};`).join('\n')}\n\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(declaration.selector)};\npub const DOMAINSPEC_CONTRACT_SHA256: &str = ${rustString(sha256(canonicalJson(declaration.contract)))};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(declaration.kind === 'Entity' ? RUST_ENTITY_PROTOCOL : RUST_VALUE_OBJECT_PROTOCOL)};\n${referenceConst}\n${definitions.join('\n\n')}${definitions.length ? '\n\n' : ''}#[derive(Clone, Debug)]\npub struct ${input} {\n${inputLines}\n}\n\n#[derive(${derives})]\npub struct ${name} {\n${fieldLines}\n}\n\nimpl ${name} {\n${getters}\n}\n${equality}\n#[derive(Clone, Debug, PartialEq, Eq)]\npub struct ${error} { pub failures: Vec<&'static str> }\n\n#[derive(Clone, Debug, Default)]\npub struct ${factory}${factoryBody}\n\nimpl ${factory} {\n${enable}\n\n    pub fn create(&self, input: ${input}) -> Result<${name}, ${error}> {\n        let mut failures = Vec::new();\n${checks}\n        if !failures.is_empty() { return Err(${error} { failures }); }\n        Ok(${name} {\n${moves}\n        })\n    }\n}\n\npub fn create_${rustSnake(declaration.selector.split(':')[1]!)}_factory() -> ${factory} { ${factoryValue} }\n`;
    const validatedContent = content.replace('\n}\n\npub fn create_', `\n\n    pub fn validate(&self, value: &${name}) -> Result<(), ${error}> {\n        let mut failures = Vec::new();\n${valueChecks}\n        if failures.is_empty() { Ok(()) } else { Err(${error} { failures }) }\n    }\n}\n\npub fn create_`);
    const relative_path = typePath(selection.module_root, declaration.selector);
    return {selector: declaration.selector, kind: declaration.kind, symbol: name, input_symbol: input, factory_symbol: factory, callable: `create_${rustSnake(declaration.selector.split(':')[1]!)}_factory`, relative_path, protocol_id: declaration.kind === 'Entity' ? RUST_ENTITY_PROTOCOL : RUST_VALUE_OBJECT_PROTOCOL, contract_sha256: sha256(canonicalJson(declaration.contract)), base_validators: base.map(row => row.selector), extensions: extensions.map(row => ({id: row.id, validators: row.validators.map(validator => validator.selector)})), identity_field: identity?.name ?? null, field_bindings: references, artifact: artifact(relative_path, validatedContent)};
  });
  const body = {schema_version: 'domainspec.configured-rust-factories-plan/v1-candidate' as const, selection: {...selection, factories: structuredClone(selection.factories)}, field_compilation_sha256: fields.compilation_sha256, rule_plan_sha256: rules.plan_sha256, contract_sha256: RUST_FACTORY_CONTRACT_SHA256, modules: modules.map(({artifact: _artifact, ...row}) => row), artifacts: modules.map(row => row.artifact).sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
