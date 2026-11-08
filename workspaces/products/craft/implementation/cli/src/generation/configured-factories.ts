import path from 'node:path';
import {assertCompiledProjectSnapshot, selectCompiledProjectNode, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectFields, compileSelectedProjectFields, PROJECT_FIELD_SELECTION_VERSION, FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {planConfiguredRules, CONFIGURED_RULE_VERSION, NUMERIC_RULE_VERSION, EXACT_RULE_VERSION, EXACT_LITERAL_RULE_VERSION, type RuleConfigurationSources} from './configured-rules.js';
import {EXACT_UINT64_PROFILE} from './exact-uint64.js';
import {STRUCTURED_RULE_VERSION} from './configured-rules.js';
import {ruleFactView} from './configured-rule-fact-view.js';
import {NUMERIC_RULE_VALUE_PROFILE} from './configured-rule-numeric.js';
import type {TypedRuleContract, TypedType} from '../typed-operation/contracts.js';
import {renderConfiguredFactory} from './configured-factory-source.js';
import {renderCollectionSupport} from './configured-collection-source.js';
import {planConfiguredEnums, CONFIGURED_ENUM_VERSION, EXACT_CONFIGURED_ENUM_VERSION} from './configured-enums.js';
import {annotateEnumDefinition, renderEnumComponent, renderEnumValueSupport, type ConfiguredEnumComponentModule} from './configured-enum-component-source.js';
import {composeValueShape, renderConfiguredSum, renderSumSupport, valueDependencies, type ValueShape, type ConfiguredSumModule} from './configured-sum-source.js';
import {renderUInt64Support} from './configured-uint64-source.js';
import {renderExactUInt64Support} from './configured-exact-uint64-source.js';
import type {ConfiguredFieldReference} from './configured-reference-source.js';
import {renderEntitySupport} from './configured-entity-source.js';

// PCR-06 candidate; exact scope and open questions: FACTORY-GENERATION.md.
export const CONFIGURED_FACTORY_VERSION = 'domainspec.configured-factories-selection/v1-candidate';
export const COMPOSED_FACTORY_VERSION = 'domainspec.configured-factories-selection/v2-candidate';
export const COLLECTION_FACTORY_VERSION = 'domainspec.configured-factories-selection/v3-candidate';
export const ENUM_FIELD_FACTORY_VERSION = 'domainspec.configured-factories-selection/v4-candidate';
export const SUM_FIELD_FACTORY_VERSION = 'domainspec.configured-factories-selection/v5-candidate';
export const UINT64_FIELD_FACTORY_VERSION = 'domainspec.configured-factories-selection/v6-candidate';
export const REFERENCE_FIELD_FACTORY_VERSION = 'domainspec.configured-factories-selection/v7-candidate';
export const ENTITY_RULE_PATH_FACTORY_VERSION = 'domainspec.configured-factories-selection/v9-candidate';
export const RULE_COMPOSITION_FACTORY_VERSION = 'domainspec.configured-factories-selection/v10-candidate';
export const EXACT_FACTORY_VERSION = 'domainspec.configured-factories-selection/v11-candidate';
export const STRUCTURED_FACTORY_VERSION = 'domainspec.configured-factories-selection/v12-candidate';
export const STRUCTURED_FACTORY_CONTRACT_SHA256 = '3eeaf28f589af095624fd15b62621d15abc12839aa5b07ccf2f3f6847a452e0f';
export const EXACT_FACTORY_CONTRACT_SHA256 = '9fe79d423a6aaada5a62089953354c79d709f298ded49688983195a96b26fde9';
export const RULE_COMPOSITION_FACTORY_CONTRACT_SHA256 = '76c66c6558998c5ec7a251f7aed86a130a41ed0995c5c60e25438a8d35f5e2c4';
export const ENTITY_RULE_PATH_FACTORY_CONTRACT_SHA256 = '504bc456b793e87091c5133b4dda408f7233f266eb33994d19d04f298500644d';
export const EMBEDDED_ENTITY_FACTORY_VERSION = 'domainspec.configured-factories-selection/v8-candidate';
export const EMBEDDED_ENTITY_FACTORY_CONTRACT_SHA256 = '3725392ffac4dc7644779cfb3580905c86428394b7cf27f13f489fd8193649d7';
export const REFERENCE_FIELD_FACTORY_CONTRACT_SHA256 = '063b6d3228abfdedff01b0f743393ac8138d41af0b592071985a4686e083036f';
export const UINT64_FIELD_FACTORY_CONTRACT_SHA256 = '9b77a5827bef588b8f28cdac0efd65b4f1f39b837d8791b4b5d1cb4c7b990665';
export const SUM_FIELD_FACTORY_CONTRACT_SHA256 = 'f64f0b8bfb57a56cc676737e32e7a727e9c50caf9822f720d0585df7fdc10da2';
export const ENUM_FIELD_FACTORY_CONTRACT_SHA256 = 'a7eedabc1db6145afc50060d5fba762110bee91bd7f3bb7d8f23bf99b7f8d5ab';
export const COLLECTION_FACTORY_CONTRACT_SHA256 = 'd29ea59124cab26b8b416f67dd08cf894be28f4bc006e3b5cc416228e42e79b9';
export const COMPOSED_FACTORY_CONTRACT_SHA256 = '73153298625de85a7b25b5cd66d89e94481bf2fd593c8a4c9b703e586a53c069';
export const SCALAR_FACTORY_CONTRACT_SHA256 = '363017b9bc55ea5948a98d64a232abdc1afb452e8a704bb87e7571ae27bfe70c';
export type FactoryArgument = Readonly<{parameter: string; field: string; path?: never}> | Readonly<{parameter: string; path: readonly string[]; field?: never}>;
export interface FactoryValidatorBinding {
  readonly rule: string;
  readonly arguments: readonly FactoryArgument[];
}
export interface FactoryBinding {
  readonly selector: string;
  readonly base_validators: readonly FactoryValidatorBinding[];
  readonly extensions: readonly Readonly<{id: string; validators: readonly FactoryValidatorBinding[]}>[];
}
export interface ConfiguredFactorySelection {
  readonly schema_version: typeof CONFIGURED_FACTORY_VERSION | typeof COMPOSED_FACTORY_VERSION | typeof COLLECTION_FACTORY_VERSION | typeof ENUM_FIELD_FACTORY_VERSION | typeof SUM_FIELD_FACTORY_VERSION | typeof UINT64_FIELD_FACTORY_VERSION | typeof REFERENCE_FIELD_FACTORY_VERSION | typeof EMBEDDED_ENTITY_FACTORY_VERSION | typeof ENTITY_RULE_PATH_FACTORY_VERSION | typeof RULE_COMPOSITION_FACTORY_VERSION | typeof EXACT_FACTORY_VERSION | typeof STRUCTURED_FACTORY_VERSION;
  readonly rule_selection?: Readonly<{schema_version: typeof NUMERIC_RULE_VERSION | typeof EXACT_RULE_VERSION | typeof EXACT_LITERAL_RULE_VERSION | typeof STRUCTURED_RULE_VERSION; value_profile: typeof NUMERIC_RULE_VALUE_PROFILE | typeof EXACT_UINT64_PROFILE}>;
  readonly language: 'typescript';
  readonly module_root: string;
  readonly field_compilation_sha256: string;
  readonly factories: readonly FactoryBinding[];
}
export interface BoundFactoryValidator extends FactoryValidatorBinding {
  readonly fact_views?: Readonly<Record<string,string>>;
  readonly closure_sha256: string;
  readonly artifact_sha256: string;
  readonly local: string;
}
export interface ConfiguredFactoryModule {
  readonly selector: string;
  readonly kind: 'Entity' | 'Value Object';
  readonly relative_path: string;
  readonly name: string;
  readonly callable: string;
  readonly protocol_id: string;
  readonly fields: readonly Readonly<{name: string; tag: 'String' | 'Bool' | 'ValueObject' | 'Entity' | 'Enum' | 'Sum' | 'UInt64'; identity: boolean;
    value_shape?: ValueShape;
    wrappers?: readonly ('optional' | 'list' | 'set')[];
    component?: Readonly<{selector: string; path: string; symbol: string; local: string; type_symbol: string; type_local: string}>}>[];
  readonly imports: readonly Readonly<{path: string; symbol: string; local: string}>[];
  readonly base_validators: readonly BoundFactoryValidator[];
  readonly extensions: readonly Readonly<{id: string; validators: readonly BoundFactoryValidator[]}>[];
  readonly component_protocol_sha256: string;
  readonly composed?: true;
  readonly collections?: true;
  readonly enum_fields?: true;
  readonly sum_fields?: true;
  readonly uint64_fields?: true;
  readonly exact_uint64?: true;
  readonly reference_bindings?: readonly ConfiguredFieldReference[];
  readonly entity_fields?:true;
}
const reserved = new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul ' + Array.from({length: 9}, (_, i) => `com${i + 1} lpt${i + 1}`).join(' ')).split(' '));
function fail(message: string): never {throw new Error('DS_CONFIGURED_FACTORY:' + message);}
function inert(value: unknown, depth = 0): void {
  if (depth > 32) fail('selection depth');
  if (typeof value === 'string' || typeof value === 'boolean' || value === null) return;
  if (!value || typeof value !== 'object') fail('non-JSON selection');
  if (!Array.isArray(value) && ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('non-JSON prototype');
  for (const key of Reflect.ownKeys(value)) {
    if (Array.isArray(value) && key === 'length') continue;
    const d = Object.getOwnPropertyDescriptor(value, key)!;
    if (typeof key !== 'string' || !('value' in d) || !d.enumerable) fail('non-data selection');
    inert(d.value, depth + 1);
  }
  if (Array.isArray(value) && (value.length > 256 || Object.keys(value).length !== value.length || Array.from({length: value.length}, (_, i) => i).some(i => !Object.hasOwn(value, i)))) fail('invalid selection array');
}
function keys(value: unknown, expected: readonly string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join('|') !== [...expected].sort().join('|')) fail('unknown or missing fields');
}
function list(value: unknown, nonempty = false): asserts value is unknown[] {
  if (!Array.isArray(value) || value.length > 256 || (nonempty && !value.length)) fail('invalid binding list');
}
function portable(id: string): void {
  if (typeof id !== 'string' || !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(id) || reserved.has(id)) fail('unsafe portable identifier:' + id);
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);}
  return value;
}

/** Pure candidate plan: bind fields and generated Rules from the same checked graph.
 * Bindings are implementation selections, not semantic graph relationships.
 */
export function planConfiguredFactories(graph: CompiledProjectGraph, fields: CompiledProjectFields, selection: ConfiguredFactorySelection,
  sources: RuleConfigurationSources & Readonly<{factory_contract: string; enum_provider?: string; field_contract?: string}>) {
  assertCompiledProjectSnapshot(graph); assertCompiledProjectFields(fields);
  // Inspect only the own data descriptor here: old selections must reject exact
  // snapshots before evaluating caller-supplied options (including accessors).
  const requestedVersion = selection && typeof selection === 'object' ? Object.getOwnPropertyDescriptor(selection, 'schema_version')?.value : undefined;
  if (fields.selection.schema_version !== PROJECT_FIELD_SELECTION_VERSION && requestedVersion !== EXACT_FACTORY_VERSION && requestedVersion !== STRUCTURED_FACTORY_VERSION) fail('exact field values require an explicit exact factory realization');
  inert(selection); inert(sources);
  const structuredRules = selection.schema_version === STRUCTURED_FACTORY_VERSION;
  const exactValues = structuredRules || selection.schema_version === EXACT_FACTORY_VERSION;
  if (exactValues && fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('exact factory requires exact checked fields');
  const ruleComposition = exactValues || selection.schema_version === RULE_COMPOSITION_FACTORY_VERSION;
  keys(selection, ['schema_version', 'language', 'module_root', 'field_compilation_sha256', 'factories', ...(ruleComposition ? ['rule_selection'] : [])]);
  if (ruleComposition) {
    keys(selection.rule_selection, ['schema_version', 'value_profile']);
    const rule = selection.rule_selection!;
    const versionMatches = structuredRules ? rule.schema_version === STRUCTURED_RULE_VERSION : exactValues ? rule.schema_version === EXACT_RULE_VERSION || rule.schema_version === EXACT_LITERAL_RULE_VERSION : rule.schema_version === NUMERIC_RULE_VERSION;
    if (!versionMatches || rule.value_profile !== (exactValues ? EXACT_UINT64_PROFILE : NUMERIC_RULE_VALUE_PROFILE)) fail('unsupported Rule selection');
  }
  const exactLiterals = structuredRules || exactValues && selection.rule_selection!.schema_version === EXACT_LITERAL_RULE_VERSION;
  const entityRulePaths = ruleComposition || selection.schema_version === ENTITY_RULE_PATH_FACTORY_VERSION;
  const entityFields = entityRulePaths || selection.schema_version === EMBEDDED_ENTITY_FACTORY_VERSION;
  const referenceFields = entityFields || selection.schema_version === REFERENCE_FIELD_FACTORY_VERSION;
  const uint64Fields = referenceFields || selection.schema_version === UINT64_FIELD_FACTORY_VERSION;
  const sumFields = uint64Fields || selection.schema_version === SUM_FIELD_FACTORY_VERSION;
  const enumFields = sumFields || selection.schema_version === ENUM_FIELD_FACTORY_VERSION;
  keys(sources, ['configuration', 'base', 'typescript', 'factory_contract', ...(enumFields ? ['enum_provider', 'field_contract'] : []), ...(ruleComposition ? ['rule_contract', 'collection_contract', 'predicate_contract', 'numeric_contract'] : []), ...(exactValues ? ['exact_contract'] : []), ...(exactLiterals ? ['literal_contract'] : []), ...(structuredRules ? ['structured_contract'] : [])]);
  const collections = enumFields || selection.schema_version === COLLECTION_FACTORY_VERSION;
  const composed = collections || selection.schema_version === COMPOSED_FACTORY_VERSION;
  const contractHash = structuredRules ? STRUCTURED_FACTORY_CONTRACT_SHA256 : exactValues ? EXACT_FACTORY_CONTRACT_SHA256 : ruleComposition ? RULE_COMPOSITION_FACTORY_CONTRACT_SHA256 : entityRulePaths ? ENTITY_RULE_PATH_FACTORY_CONTRACT_SHA256 : entityFields ? EMBEDDED_ENTITY_FACTORY_CONTRACT_SHA256 : referenceFields ? REFERENCE_FIELD_FACTORY_CONTRACT_SHA256 : uint64Fields ? UINT64_FIELD_FACTORY_CONTRACT_SHA256 : sumFields ? SUM_FIELD_FACTORY_CONTRACT_SHA256 : enumFields ? ENUM_FIELD_FACTORY_CONTRACT_SHA256 : collections ? COLLECTION_FACTORY_CONTRACT_SHA256 : composed ? COMPOSED_FACTORY_CONTRACT_SHA256 : SCALAR_FACTORY_CONTRACT_SHA256;
  if ((!composed && selection.schema_version !== CONFIGURED_FACTORY_VERSION) || selection.language !== 'typescript') fail('unsupported selection');
  if (selection.field_compilation_sha256 !== fields.compilation_sha256 || canonicalJson(fields.certificate) !== canonicalJson(createCompiledProjectCertificate(graph))) fail('stale graph or field binding');
  if (sha256(sources.factory_contract) !== contractHash) fail('factory contract drift');
  const collectionSupport = collections ? {protocol_id: 'typescript.owned-collection-components/v1-candidate',
    sha256: sha256(renderCollectionSupport() + (enumFields ? renderEnumValueSupport() : '') + (sumFields ? renderSumSupport() : '') + (exactValues ? renderExactUInt64Support() : uint64Fields ? renderUInt64Support() : '') + (entityFields ? renderEntitySupport() : '')), placement: 'inline-private'} : undefined;
  if (collections && collectionSupport!.sha256 !== JSON.parse(sources.factory_contract).component_support_sha256) fail('collection support drift');
  if (enumFields && (typeof sources.enum_provider !== 'string' || typeof sources.field_contract !== 'string' ||
    sha256(sources.enum_provider) !== JSON.parse(sources.factory_contract).enum_provider_sha256 ||
    sha256(sources.field_contract) !== (exactValues ? EXACT_FIELD_CONTRACT_SHA256 : FIELD_CONTRACT_SHA256))) fail('Enum provider or field contract drift');
  if (!referenceFields && fields.model.bindings.length) fail('reference bindings unsupported');
  list(selection.factories, true);
  if (new Set(selection.factories.map(f => f.selector)).size !== selection.factories.length) fail('duplicate factory');
  const factoryDeclarations = fields.model.declarations.filter(d => !enumFields || d.kind !== 'Enum');
  if (canonicalJson(selection.factories.map(f => f.selector).sort()) !== canonicalJson(factoryDeclarations.map(d => d.selector).sort())) fail('factory coverage');
  const bindings = new Map(selection.factories.map(f => [f.selector, f]));
  const declarations = new Map(fields.model.declarations.map(d => [d.selector, d]));
  const supportedType = (type: TypedType): boolean => {
    if (type.kind === 'scalar') return type.name === 'String' || type.name === 'Bool' || uint64Fields && type.name === 'UInt64';
    if (type.kind === 'named') return composed && (declarations.get(type.selector)?.kind === 'Value Object' || entityFields && declarations.get(type.selector)?.kind === 'Entity' || enumFields && declarations.get(type.selector)?.kind === 'Enum');
    if (type.kind === 'sum') return sumFields && type.variants.every(v => v.payload === null || supportedType(v.payload));
    return collections && (type.kind === 'optional' || type.kind === 'list' || type.kind === 'set') && supportedType(type.element);
  };
  const roots: string[] = [];
  const sumDeclarations = sumFields ? fields.model.declarations.filter(d => d.kind === 'Enum' && d.contract.variants.some(v => v.payload !== null)) : [];
  for (const d of sumDeclarations) {
    if (d.kind !== 'Enum' || !d.contract.variants.every(v => v.payload === null || supportedType(v.payload))) fail('unsupported sum payload:' + d.selector);
    const [feature, node] = d.selector.split(':') as [string,string]; portable(feature); portable(node);
  }
  for (const declaration of factoryDeclarations) {
    if (declaration.kind !== 'Entity' && declaration.kind !== 'Value Object') fail('unsupported declaration kind:' + declaration.selector);
    if (!declaration.contract.properties.length || declaration.contract.properties.some(p => (!collections && p.cardinality !== 'one') || !supportedType(p.type))) fail('required String/Bool' + (composed ? '/owned Value Object' : '') + (collections ? ' with optional/list/set wrappers' : '') + ' fields only:' + declaration.selector);
    const binding = bindings.get(declaration.selector)!;
    // An Entity may declare no semantic invariants. Exact structural normalization
    // still validates its required fields/identity; never invent a business Rule.
    keys(binding, ['selector', 'base_validators', 'extensions']); list(binding.base_validators, !(structuredRules && declaration.kind === 'Entity')); list(binding.extensions);
    const seen = new Set<string>();
    const check = (v: FactoryValidatorBinding) => {
      keys(v, ['rule', 'arguments']); list(v.arguments);
      if (typeof v.rule !== 'string' || seen.has(v.rule)) fail('duplicate or invalid validator');
      seen.add(v.rule); roots.push(v.rule);
      const node = selectCompiledProjectNode(graph, v.rule);
      if (node.kind !== 'Rule' || node.typed_closure?.schema_version !== 'domainspec.typed-rule-closure/v1') fail('validator must be a typed Rule:' + v.rule);
      const rule = node.typed_closure!.nodes.find(n => n.selector === v.rule)!.typed_contract as TypedRuleContract;
      if (new Set(v.arguments.map(a => a.parameter)).size !== v.arguments.length || canonicalJson(v.arguments.map(a => a.parameter).sort()) !== canonicalJson(rule.parameters.map(p => p.name).sort())) fail('validator parameter coverage:' + v.rule);
      for (const a of v.arguments) {
        const usePath = composed && Object.hasOwn(a, 'path');
        keys(a, ['parameter', usePath ? 'path' : 'field']);
        if (usePath) {list(a.path, true); if (a.path!.length > 32 || a.path!.some(p => typeof p !== 'string')) fail('invalid validator path');}
        const segments = usePath ? a.path! : [a.field!];
        const p = rule.parameters.find(p => p.name === a.parameter)!;
        let field = declaration.contract.properties.find(f => f.name === segments[0]);
        for (const segment of segments.slice(1)) {
          const target = field?.type.kind === 'named' ? declarations.get(field.type.selector) : undefined;
          if (target?.kind !== 'Value Object' && !(entityRulePaths && target?.kind === 'Entity'))
            fail(entityRulePaths ? 'validator path must traverse required owned Entity or Value Object fields' : 'validator path must traverse owned Value Objects');
          field = target.contract.properties.find(f => f.name === segment);
        }
        if (ruleComposition && !structuredRules) {
          const type = field?.type;
          const leaf = type?.kind === 'list' || type?.kind === 'set' ? type.element : type;
          if (leaf?.kind !== 'scalar' || !['String', 'Bool', 'UInt64'].includes(leaf.name)) fail('validator endpoint must be a selected scalar or scalar list/set');
        } else if (!structuredRules && composed && (field?.type.kind !== 'scalar' || !['String', 'Bool'].includes(field.type.name))) fail('validator path must end at scalar');
        if (!field || canonicalJson(p.type) !== canonicalJson(field.type)) fail('validator field/type mismatch:' + v.rule);
      }
    };
    binding.base_validators.forEach(check);
    if (declaration.kind === 'Value Object' && canonicalJson(binding.base_validators.map(v => v.rule).sort()) !== canonicalJson(declaration.invariant_refs)) fail('authored invariant coverage:' + declaration.selector);
    if (new Set(binding.extensions.map(e => e.id)).size !== binding.extensions.length) fail('duplicate extension');
    for (const extension of binding.extensions) {keys(extension, ['id', 'validators']); portable(extension.id); list(extension.validators, true); extension.validators.forEach(check);}
  }
  const ruleSources = {configuration: sources.configuration, base: sources.base, typescript: sources.typescript};
  const enumRoots = enumFields ? fields.model.declarations.filter(d => d.kind === 'Enum' && !sumDeclarations.includes(d)).map(d => d.selector).sort() : [];
  const enumProjection = enumRoots.length ? compileSelectedProjectFields(graph, {
    schema_version: exactValues ? EXACT_PROJECT_FIELD_SELECTION_VERSION : PROJECT_FIELD_SELECTION_VERSION, contract_sha256: exactValues ? EXACT_FIELD_CONTRACT_SHA256 : FIELD_CONTRACT_SHA256,
    graph_sha256: fields.certificate.graph_sha256, roots: enumRoots, bindings: [],
  }, sources.field_contract!) : undefined;
  const enums = enumProjection ? planConfiguredEnums(enumProjection, {schema_version: exactValues ? EXACT_CONFIGURED_ENUM_VERSION : CONFIGURED_ENUM_VERSION,
    language: selection.language, module_root: selection.module_root, field_compilation_sha256: enumProjection.compilation_sha256},
    {...ruleSources, provider: sources.enum_provider!}) : undefined;
  const enumArtifacts = enums?.artifacts.map(a => {
    const module = enums.modules.find(m => m.relative_path === a.relative_path);
    if (!module) return a;
    const content = annotateEnumDefinition(module, a.content);
    return {...a, content, sha256: sha256(content), size_bytes: Buffer.byteLength(content)};
  }) ?? [];
  const enumComponents: ConfiguredEnumComponentModule[] = enums ? enums.modules.map(m => ({
    selector: m.selector, name: m.symbol, members: m.members, relative_path: m.relative_path.replace(/\.ts$/, '.component.ts'),
    definition_path: m.relative_path, definition_sha256: enumArtifacts.find(a => a.relative_path === m.relative_path)!.sha256,
    unannotated_definition_sha256: enums.artifacts.find(a => a.relative_path === m.relative_path)!.sha256,
    definition_import: './' + path.posix.basename(m.relative_path).replace(/\.ts$/, '.js'), contract_sha256: contractHash,
  })) : [];
  // The standalone Rule planner requires a nonempty checked representation root.
  // In a structural-only Entity closure reuse actual typed Rules already in the
  // graph (e.g. an Operation guard); none becomes a factory validator implicitly.
  const representationRoots=roots.length?roots:structuredRules?graph.nodes.filter(n=>n.kind==='Rule'&&(n.body.typed_contract as {schema_version?:string}|undefined)?.schema_version==='domainspec.typed-rule/v2').map(n=>n.selector):roots;
  const rules = planConfiguredRules(graph, {schema_version: ruleComposition ? selection.rule_selection!.schema_version : CONFIGURED_RULE_VERSION,
    ...(ruleComposition ? {value_profile: selection.rule_selection!.value_profile} : {}),
    language: selection.language, module_root: selection.module_root, roots: [...new Set(representationRoots)].sort()},
    {...ruleSources, ...(ruleComposition ? {rule_contract:sources.rule_contract!,collection_contract:sources.collection_contract!,predicate_contract:sources.predicate_contract!,numeric_contract:sources.numeric_contract!} : {}), ...(exactValues ? {exact_contract:sources.exact_contract!} : {}), ...(exactLiterals ? {literal_contract:sources.literal_contract!} : {}), ...(structuredRules ? {structured_contract:sources.structured_contract!,field_contract:sources.field_contract!} : {})});
  const config = JSON.parse(sources.configuration) as {types: Array<{kind: string; role: string; blocked_by: string[]}>};
  const profile = JSON.parse(sources.typescript) as {representation_overlays: Array<{contract_id: string; candidate_protocols: Array<{protocol_id: string}>}>};
  const sumSelectors = new Set(sumDeclarations.map(d => d.selector));
  const makeShape = (type:TypedType, ownerPath:string, prefix:string):ValueShape => composeValueShape(type,prefix,(selector,local) => {
    const d = declarations.get(selector)!;
    if(d.kind !== 'Enum' && d.kind !== 'Value Object' && !(entityFields && d.kind==='Entity')) fail('unsupported owned sum component:' + selector);
    const [feature,node] = selector.split(':') as [string,string]; portable(feature); portable(node);
    const name = node.split('-').map(w => w[0]!.toUpperCase()+w.slice(1)).join('');
    const kind = d.kind === 'Entity' ? 'Entity' as const : d.kind === 'Value Object' ? 'ValueObject' as const : sumSelectors.has(selector) ? 'Sum' as const : 'Enum' as const;
    const target = selection.module_root + '/features/' + feature + '/src/domain/' +
      (kind === 'Entity' ? 'entities/' + node + '.ts' : kind === 'ValueObject' ? 'value-objects/' + node + '.ts' : 'enums/' + node + (kind === 'Sum' ? '.sum.ts' : '.component.ts'));
    const rel = path.posix.relative(path.posix.dirname(ownerPath),target).replace(/\.ts$/,'.js');
    const suffix = kind === 'ValueObject' || kind === 'Entity' ? 'Snapshot' : 'Case';
    return {kind,component:{selector,path:rel.startsWith('.')?rel:'./'+rel,symbol:name+'ValueComponent',local,
      type_symbol:name+suffix,type_local:local+'Type'}};
  },uint64Fields);
  const sumModules:ConfiguredSumModule[] = sumDeclarations.map(d => {
    if(d.kind !== 'Enum')return fail('unsupported sum declaration');
    const cell = config.types.find(c => c.kind === 'Enum');
    if(cell?.role !== 'domain/enums')fail('unsupported sum location');
    const [feature,node] = d.selector.split(':') as [string,string];
    const relative_path = selection.module_root + '/features/' + feature + '/src/domain/enums/' + node + '.sum.ts';
    return {selector:d.selector,relative_path,name:node.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join(''),
      shape:makeShape({kind:'sum',variants:d.contract.variants},relative_path,'payload'),contract_sha256:contractHash,
      ...(uint64Fields ? {uint64_fields:true as const} : {}),...(entityFields ? {entity_fields:true as const} : {}),...(exactValues ? {exact_uint64:true as const} : {})};
  });
  const modules: ConfiguredFactoryModule[] = factoryDeclarations.map(d => {
    if (d.kind === 'Enum') return fail('unsupported Enum');
    const [feature, node] = d.selector.split(':') as [string, string]; portable(feature); portable(node);
    const name = node.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
    const cell = config.types.find(c => c.kind === d.kind)!;
    const role = d.kind === 'Entity' ? 'domain/entities' : 'domain/value-objects';
    if (cell.role !== role || canonicalJson(cell.blocked_by) !== canonicalJson(['DSR-009'])) fail('unsupported factory configuration');
    const protocol_id = d.kind === 'Entity' ? 'typescript.validated-extensible-entity-factory/v1' : 'typescript.owned-value-object-factory/v1';
    const overlay = profile.representation_overlays.find(o => o.contract_id === (d.kind === 'Entity' ? 'entity' : 'value-object') + '.profile-representation');
    if (!overlay?.candidate_protocols.some(p => p.protocol_id === protocol_id)) fail('unselected protocol');
    const relative_path = `${selection.module_root}/features/${feature}/src/${role}/${node}.ts`;
    const referenceBindings:ConfiguredFieldReference[] = referenceFields ? fields.model.bindings.filter(r=>r.owner===d.selector).map((r,index)=>{
      const target=declarations.get(r.target)!;
      if(target.kind==='Enum')return fail('reference target must have fields');
      const [targetFeature,targetNode]=r.target.split(':') as [string,string];
      portable(targetFeature);portable(targetNode);
      const targetName=targetNode.split('-').map(w=>w[0]!.toUpperCase()+w.slice(1)).join('');
      const target_path=`${selection.module_root}/features/${targetFeature}/src/domain/${target.kind==='Entity'?'entities':'value-objects'}/${targetNode}.ts`;
      const rel=path.posix.relative(path.posix.dirname(relative_path),target_path).replace(/\.ts$/,'.js');
      const wrappers:('optional'|'list'|'set')[]=[];
      let type=d.contract.properties.find(p=>p.name===r.field)!.type;
      if(r.kind==='identity-reference')while(type.kind==='optional'||type.kind==='list'||type.kind==='set'){wrappers.push(type.kind);type=type.element;}
      const local=r.target===d.selector?name+'Fields':'referenceTarget'+index+'Fields';
      return {...r,projection:[...r.projection],target_path,target_type:local,wrappers,
        type_import:r.target===d.selector?null:{path:rel.startsWith('.')?rel:'./'+rel,symbol:targetName+'Fields',local}};
    }) : [];
    const b = bindings.get(d.selector)!;
    const selectedRules = [...new Set([...b.base_validators, ...b.extensions.flatMap(e => e.validators)].map(v => v.rule))].sort();
    const imports = selectedRules.map((selector, index) => {
      const m = rules.modules.find(m => m.selector === selector)!;
      const rel = path.posix.relative(path.posix.dirname(relative_path), m.relative_path).replace(/\.ts$/, '.js');
      return {path: rel.startsWith('.') ? rel : './' + rel, symbol: m.callable, local: 'validator' + index};
    });
    const bind = (v: FactoryValidatorBinding): BoundFactoryValidator => {
      const m = rules.modules.find(m => m.selector === v.rule)!;
      const fact_views = structuredRules ? Object.fromEntries(v.arguments.map(a => {
        const segments = a.path ?? [a.field!];
        let field = d.contract.properties.find(p => p.name === segments[0])!;
        for (const segment of segments.slice(1)) {
          const target = field.type.kind === 'named' ? declarations.get(field.type.selector) : undefined;
          if (!target || target.kind === 'Enum') return fail('invalid checked fact path');
          field = target.contract.properties.find(p => p.name === segment)!;
        }
        const source = 'fields' + segments.map((p,i) => (i ? '.fields' : '') + '[' + JSON.stringify(p) + ']').join('');
        return [a.parameter, ruleFactView(field.type,source,fields.model)];
      }).sort(([a],[b]) => a! < b! ? -1 : a! > b! ? 1 : 0)) : undefined;
      return {...v, arguments: v.arguments.map(a => a.path ? {parameter: a.parameter, path: [...a.path]} : {parameter: a.parameter, field: a.field!}).sort((a, b) => a.parameter < b.parameter ? -1 : a.parameter > b.parameter ? 1 : 0),
        ...(fact_views ? {fact_views} : {}),
        local: imports[selectedRules.indexOf(v.rule)]!.local, closure_sha256: m.closure_sha256,
        artifact_sha256: rules.artifacts.find(a => a.relative_path === m.relative_path)!.sha256};
    };
    return {selector: d.selector, kind: d.kind, relative_path, name, callable: `create${name}Factory`, protocol_id,
      fields: [...d.contract.properties].sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0).map((p, index) => {
        let type = p.type;
        const wrappers: ('optional' | 'list' | 'set')[] = [];
        while (type.kind === 'optional' || type.kind === 'list' || type.kind === 'set') {wrappers.push(type.kind); type = type.element;}
        const shape = collections ? {wrappers} : {};
        if (sumFields) {
          const tag = type.kind === 'sum' ? 'Sum' as const : type.kind === 'named' ?
            declarations.get(type.selector)?.kind === 'Entity' ? 'Entity' as const : declarations.get(type.selector)?.kind === 'Value Object' ? 'ValueObject' as const : sumSelectors.has(type.selector) ? 'Sum' as const : 'Enum' as const :
            type.kind === 'scalar' && type.name === 'UInt64' ? 'UInt64' as const : type.kind === 'scalar' && type.name === 'Bool' ? 'Bool' as const : 'String' as const;
          return {name:p.name,tag,identity:p.identity,...shape,value_shape:makeShape(p.type,relative_path,'component'+index)};
        }
        if (type.kind !== 'named') return {name: p.name, tag: type.kind === 'scalar' && type.name === 'Bool' ? 'Bool' as const : 'String' as const, identity: p.identity, ...shape};
        const [childFeature, childNode] = type.selector.split(':') as [string, string];
        const childName = childNode.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
        const enumComponent = enumComponents.find(c => c.selector === type.selector);
        const target = enumComponent?.relative_path ?? `${selection.module_root}/features/${childFeature}/src/domain/value-objects/${childNode}.ts`;
        const rel = path.posix.relative(path.posix.dirname(relative_path), target).replace(/\.ts$/, '.js');
        return {name: p.name, tag: enumComponent ? 'Enum' as const : 'ValueObject' as const, identity: p.identity, ...shape, component: {selector: type.selector,
          path: rel.startsWith('.') ? rel : './' + rel, symbol: childName + 'ValueComponent', local: 'component' + index,
          type_symbol: childName + (enumComponent ? 'Case' : 'Snapshot'), type_local: 'Component' + index + (enumComponent ? 'Case' : 'Snapshot')}};
      }),
      imports, base_validators: b.base_validators.map(bind), extensions: [...b.extensions].sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0).map(e => ({id: e.id, validators: e.validators.map(bind)})), component_protocol_sha256: contractHash,
      ...(referenceFields ? {reference_bindings:referenceBindings} : {}),
      ...(entityFields ? {entity_fields:true as const} : {}),
      ...(composed ? {composed: true as const} : {}), ...(collections ? {collections: true as const} : {}), ...(enumFields ? {enum_fields: true as const} : {}), ...(sumFields ? {sum_fields: true as const} : {}), ...(uint64Fields ? {uint64_fields:true as const} : {}), ...(exactValues ? {exact_uint64:true as const} : {})};
  });
  const artifacts = [...rules.artifacts, ...enumArtifacts, ...sumModules.map(m => {
    const content = renderConfiguredSum(m);
    return {relative_path:m.relative_path,content,sha256:sha256(content),size_bytes:Buffer.byteLength(content)};
  }), ...enumComponents.map(m => {
    const content = renderEnumComponent(m);
    return {relative_path: m.relative_path, content, sha256: sha256(content), size_bytes: Buffer.byteLength(content)};
  }), ...modules.map(m => {
    const content = renderConfiguredFactory(m);
    return {relative_path: m.relative_path, content, sha256: sha256(content), size_bytes: Buffer.byteLength(content)};
  })].sort((a, b) => a.relative_path < b.relative_path ? -1 : a.relative_path > b.relative_path ? 1 : 0);
  const normalized = modules.map(m => ({selector: m.selector,
    base_validators: m.base_validators.map(v => ({rule: v.rule, arguments: v.arguments})),
    extensions: m.extensions.map(e => ({id: e.id, validators: e.validators.map(v => ({rule: v.rule, arguments: v.arguments}))}))}));
  const sumBindings = sumFields ? [...modules.flatMap(m => m.fields.map(f => ({owner:m.selector,field:f.name,shape:f.value_shape!}))),
    ...sumModules.map(m => ({owner:m.selector,field:'$case',shape:m.shape}))].flatMap(owner => valueDependencies(owner.shape).map(dep => {
      const target = [...modules,...sumModules,...enumComponents].find(m => m.selector === dep.component.selector)!;
      return {owner:owner.owner,field:owner.field,value_path:dep.value_path,provider:target.selector,relative_path:target.relative_path,
        artifact_sha256:artifacts.find(a => a.relative_path === target.relative_path)!.sha256};
    })) : [];
  const componentBindings = sumFields ? sumBindings : composed ? modules.flatMap(m => m.fields.flatMap(f => {
    if (!f.component) return [];
    const target = [...modules, ...enumComponents].find(t => t.selector === f.component!.selector)!;
    return [{owner: m.selector, field: f.name, provider: target.selector, relative_path: target.relative_path,
      artifact_sha256: artifacts.find(a => a.relative_path === target.relative_path)!.sha256}];
  })) : [];
  const referenceBindings = referenceFields ? modules.flatMap(m=>(m.reference_bindings??[]).map(r=>({...r,
    target_artifact_sha256:artifacts.find(a=>a.relative_path===r.target_path)!.sha256}))) : [];
  const body = {schema_version: structuredRules ? 'domainspec.configured-factories-plan/v12-candidate' as const : exactValues ? 'domainspec.configured-factories-plan/v11-candidate' as const : ruleComposition ? 'domainspec.configured-factories-plan/v10-candidate' as const : entityRulePaths ? 'domainspec.configured-factories-plan/v9-candidate' as const : entityFields ? 'domainspec.configured-factories-plan/v8-candidate' as const : referenceFields ? 'domainspec.configured-factories-plan/v7-candidate' as const : uint64Fields ? 'domainspec.configured-factories-plan/v6-candidate' as const : sumFields ? 'domainspec.configured-factories-plan/v5-candidate' as const : enumFields ? 'domainspec.configured-factories-plan/v4-candidate' as const : collections ? 'domainspec.configured-factories-plan/v3-candidate' as const : composed ? 'domainspec.configured-factories-plan/v2-candidate' as const : 'domainspec.configured-factories-plan/v1-candidate' as const,
    selection: {...selection, factories: normalized}, certificate: fields.certificate, field_model_sha256: fields.model.model_sha256,
    factory_contract_sha256: contractHash, rule_plan_sha256: rules.plan_sha256, modules, artifacts,
    ...(composed ? {component_bindings: componentBindings} : {}),
    ...(referenceFields ? {reference_bindings:referenceBindings} : {}),
    ...(collectionSupport ? {collection_support: collectionSupport} : {}),
    ...(sumFields ? {sum_modules:sumModules} : {}),
    ...(enumFields ? {enum_components: enumComponents, enum_plan_sha256: enums?.plan_sha256 ?? null,
      enum_field_compilation_sha256: enumProjection?.compilation_sha256 ?? null} : {}),
    input_envelope: structuredRules ? 'structured-rule-factories/v12-candidate' : exactValues ? 'exact-uint64-factories/v11-candidate' : ruleComposition ? 'explicit-scalar-collection-rule-composition/v10-candidate' : entityRulePaths ? 'explicit-owned-entity-rule-paths/v9-candidate' : entityFields ? 'owned-embedded-entities/v8-candidate' : referenceFields ? 'typed-reference-fields/v7-candidate' : uint64Fields ? 'json-safe-uint64-factories/v6-candidate' : sumFields ? 'owned-and-inline-sum-factories/v5-candidate' : enumFields ? 'owned-enum-field-factories/v4-candidate' : collections ? 'owned-optional-list-set-factories/v3-candidate' : composed ? 'required-owned-value-factories/v2-candidate' : 'required-string-bool-factories/v1-candidate', authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
