import path from 'node:path';
import {assertCompiledProjectSnapshot, selectCompiledProjectNode, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledProjectFields, compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import type {TypedRuleContract, TypedType} from '../typed-operation/contracts.js';
import {type FactoryBinding, type FactoryValidatorBinding, STRUCTURED_FACTORY_CONTRACT_SHA256, REFERENCE_FIELD_FACTORY_CONTRACT_SHA256} from './configured-factories.js';
import {planConfiguredPythonRules, PYTHON_STRUCTURED_RULE_VERSION, PYTHON_RULE_SOURCE_DIGESTS, type PythonStructuredRuleSources} from './configured-python-rules.js';
import {planConfiguredPythonEnums, resolvePythonEnumContext, PYTHON_ENUM_SELECTION_VERSION, pythonPortableIdentifier, pythonStringLiteral as q} from './configured-python-enums.js';
import {createPythonOwnedValues, pythonField, pythonRelativeModule, pythonSnake, pythonSymbol} from './configured-python-owned-values.js';
import {renderPythonFactorySupport} from './configured-python-factory-source.js';
import {renderPythonReferenceSupport} from './configured-python-reference-source.js';

export const PYTHON_FACTORY_VERSION = 'domainspec.configured-python-factories-selection/v1-candidate';
export const PYTHON_REFERENCE_FACTORY_VERSION = 'domainspec.configured-python-factories-selection/v2-candidate';
export interface PythonFactorySelection {
  readonly schema_version: typeof PYTHON_FACTORY_VERSION | typeof PYTHON_REFERENCE_FACTORY_VERSION;
  readonly language: 'python';
  readonly module_root: string;
  readonly field_compilation_sha256: string;
  readonly factories: readonly FactoryBinding[];
}
export type PythonFactorySources = PythonStructuredRuleSources & Readonly<{factory_contract: string; reference_contract?: string}>;
function fail(reason: string): never {throw new TypeError('DS_PYTHON_FACTORY:' + reason);}
function inert(value: unknown, depth = 0): void {
  if (depth > 32) fail('selection depth');
  if (typeof value === 'string' || typeof value === 'boolean' || value === null) return;
  if (!value || typeof value !== 'object') fail('inert selection required');
  if (![Object.prototype, null, Array.prototype].includes(Object.getPrototypeOf(value))) fail('inert prototype required');
  for (const key of Reflect.ownKeys(value)) {
    if (Array.isArray(value) && key === 'length') continue;
    const d = Object.getOwnPropertyDescriptor(value, key)!;
    if (typeof key !== 'string' || !('value' in d) || !d.enumerable) fail('inert data fields required');
    inert(d.value, depth + 1);
  }
  if (Array.isArray(value) && (value.length > 256 || Object.keys(value).length !== value.length || Array.from({length: value.length}, (_, i) => i).some(i => !Object.hasOwn(value, i)))) fail('invalid selection array');
}
function keys(value: unknown, names: string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join('|') !== names.sort().join('|')) fail('closed fields required');
}
function list(value: unknown, nonempty = false): void {if (!Array.isArray(value) || (nonempty && !value.length)) fail('invalid binding list');}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
const tuple = (items: string[]) => '(' + items.join(', ') + (items.length ? ',' : '') + ')';

/** Generates complete owned data closure and definition-bound Rule factories.
 * Reference binding realization remains explicit, not an implicit dereference. */
export function planConfiguredPythonFactories(graph: CompiledProjectGraph, fields: CompiledProjectFields, selection: PythonFactorySelection, sources: PythonFactorySources) {
  assertCompiledProjectSnapshot(graph); assertCompiledProjectFields(fields);
  inert(selection); inert(sources);
  keys(selection, ['schema_version', 'language', 'module_root', 'field_compilation_sha256', 'factories']);
  const references = selection.schema_version === PYTHON_REFERENCE_FACTORY_VERSION;
  keys(sources, [...Object.keys(PYTHON_RULE_SOURCE_DIGESTS), 'structured_contract', 'field_contract', 'factory_contract', ...(references ? ['reference_contract'] : [])]);
  if ((!references && selection.schema_version !== PYTHON_FACTORY_VERSION) || selection.language !== 'python') fail('unsupported selection');
  if (fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION || fields.compilation_sha256 !== selection.field_compilation_sha256 || canonicalJson(fields.certificate) !== canonicalJson(createCompiledProjectCertificate(graph))) fail('exact current checked fields required');
  if (sha256(sources.field_contract) !== EXACT_FIELD_CONTRACT_SHA256 || sha256(sources.factory_contract) !== STRUCTURED_FACTORY_CONTRACT_SHA256) fail('factory source drift');
  if (!references && fields.model.bindings.length) fail('reference bindings require a Python reference adapter');
  if (references && (typeof sources.reference_contract !== 'string' || sha256(sources.reference_contract) !== REFERENCE_FIELD_FACTORY_CONTRACT_SHA256)) fail('reference source drift');
  const {root} = resolvePythonEnumContext(fields, {schema_version: PYTHON_ENUM_SELECTION_VERSION, language: 'python', module_root: selection.module_root, field_compilation_sha256: fields.compilation_sha256}, {configuration: sources.configuration, base: sources.base, python: sources.python});
  const profile = JSON.parse(sources.python), config = JSON.parse(sources.configuration);
  const protocolIds = {'Entity': 'python.validated-extensible-entity-factory/v1', 'Value Object': 'python.owned-value-object-factory/v1'};
  for (const [kind, protocol_id] of Object.entries(protocolIds)) {
    const overlay = profile.representation_overlays.find((o: {contract_id: string}) => o.contract_id === (kind === 'Entity' ? 'entity' : 'value-object') + '.profile-representation');
    if (!overlay?.candidate_protocols.some((p: {protocol_id: string}) => p.protocol_id === protocol_id)) fail('missing Python factory protocol:' + kind);
    const role = config.types.find((t: {kind: string}) => t.kind === kind);
    // The frozen catalogue names DSR-009; the exact checked field snapshot above
    // discharges that construction dependency without changing profile status.
    if (role?.role !== (kind === 'Entity' ? 'domain/entities' : 'domain/value-objects') || canonicalJson(role.blocked_by) !== canonicalJson(['DSR-009'])) fail('factory role not ready');
  }
  const declarations = new Map(fields.model.declarations.map(d => [d.selector, d]));
  const records = fields.model.declarations.filter(d => d.kind !== 'Enum');
  for (const d of declarations.values()) d.selector.split(':').forEach(pythonPortableIdentifier);
  list(selection.factories, true);
  if (!records.length || canonicalJson(selection.factories.map(f => f.selector).sort()) !== canonicalJson(records.map(d => d.selector).sort())) fail('factory coverage');
  const bindings = new Map(selection.factories.map(f => [f.selector, f]));
  const roots: string[] = [];
  function endpoint(owner: typeof records[number], argument: FactoryValidatorBinding['arguments'][number]): {type: TypedType; code: string} {
    const segments = 'path' in argument ? argument.path! : [argument.field!];
    if (!Array.isArray(segments) || !segments.length || segments.length > 32 || segments.some(s => typeof s !== 'string')) fail('invalid validator path');
    let field = owner.contract.properties.find(p => p.name === segments[0]);
    let code = 'fields.' + pythonField(segments[0]!);
    for (const segment of segments.slice(1)) {
      const d = field?.type.kind === 'named' ? declarations.get(field.type.selector) : undefined;
      if (!d || d.kind === 'Enum') fail('validator path must traverse required owned Entity or Value Object');
      field = d.contract.properties.find(p => p.name === segment); code += '.fields.' + pythonField(segment);
    }
    if (!field) fail('unknown validator field'); return {type: field.type, code};
  }
  for (const d of records) {
    const binding = bindings.get(d.selector)!; keys(binding, ['selector', 'base_validators', 'extensions']); list(binding.base_validators, true); list(binding.extensions);
    const seen = new Set<string>();
    const check = (v: FactoryValidatorBinding) => {
      keys(v, ['rule', 'arguments']); list(v.arguments);
      if (typeof v.rule !== 'string' || seen.has(v.rule)) fail('duplicate or invalid validator'); seen.add(v.rule); roots.push(v.rule);
      const node = selectCompiledProjectNode(graph, v.rule);
      if (node.kind !== 'Rule' || node.typed_closure?.schema_version !== 'domainspec.typed-rule-closure/v1') fail('validator must be a typed Rule');
      const rule = node.typed_closure!.nodes.find(n => n.selector === v.rule)!.typed_contract as TypedRuleContract;
      if (new Set(v.arguments.map(a => a.parameter)).size !== v.arguments.length || canonicalJson(v.arguments.map(a => a.parameter).sort()) !== canonicalJson(rule.parameters.map(p => p.name).sort())) fail('validator parameter coverage');
      for (const a of v.arguments) {
        keys(a, ['parameter', 'path' in a ? 'path' : 'field']);
        const field = endpoint(d, a), parameter = rule.parameters.find(p => p.name === a.parameter)!;
        if (canonicalJson(field.type) !== canonicalJson(parameter.type)) fail('validator field/type mismatch');
      }
    };
    binding.base_validators.forEach(check);
    if (d.kind === 'Value Object' && canonicalJson(binding.base_validators.map(v => v.rule).sort()) !== canonicalJson(d.invariant_refs)) fail('authored invariant coverage');
    if (new Set(binding.extensions.map(e => e.id)).size !== binding.extensions.length) fail('duplicate extension');
    for (const e of binding.extensions) {keys(e, ['id', 'validators']); pythonPortableIdentifier(e.id); list(e.validators, true); e.validators.forEach(check);}
  }
  const {factory_contract, reference_contract, ...ruleSources} = sources;
  const rules = planConfiguredPythonRules(graph, {schema_version: PYTHON_STRUCTURED_RULE_VERSION, language: 'python', module_root: selection.module_root, roots: [...new Set(roots)].sort()}, ruleSources);
  const plain = fields.model.declarations.filter(d => d.kind === 'Enum' && d.contract.variants.every(v => v.payload === null));
  const target = (selector: string) => {
    const d = declarations.get(selector) ?? fail('missing selected provider');
    const [feature, node] = selector.split(':') as [string, string];
    const role = d.kind === 'Entity' ? 'entities' : d.kind === 'Value Object' ? 'value_objects' : 'enums';
    return `${root}/features/${pythonSnake(feature)}/src/domain/${role}/${pythonSnake(node)}${d.kind === 'Enum' && !plain.includes(d) ? '_sum' : ''}.py`;
  };
  const artifacts = new Map<string, {relative_path: string; content: string; size_bytes: number; sha256: string}>();
  const add = (relative_path: string, content: string) => {const prior = artifacts.get(relative_path); if (prior && prior.content !== content) fail('conflicting artifact:' + relative_path); artifacts.set(relative_path, {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)});};
  rules.artifacts.forEach(a => add(a.relative_path, a.content));
  if (plain.length) {
    const projection = compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: fields.certificate.graph_sha256, roots: plain.map(d => d.selector), bindings: []}, sources.field_contract);
    const plan = planConfiguredPythonEnums(projection, {schema_version: PYTHON_ENUM_SELECTION_VERSION, language: 'python', module_root: selection.module_root, field_compilation_sha256: projection.compilation_sha256}, {configuration: sources.configuration, base: sources.base, python: sources.python});
    plan.artifacts.forEach(a => add(a.relative_path, a.content));
  }
  const support = `${root}/runtime/values.py`, factorySupport = `${root}/runtime/factories.py`;
  const modules = records.map(d => {
    const file = target(d.selector), node = d.selector.split(':')[1]!, name = pythonSymbol(node), binding = bindings.get(d.selector)!;
    const contract = sha256(canonicalJson({contract: d.contract, factory_contract: STRUCTURED_FACTORY_CONTRACT_SHA256, python: PYTHON_RULE_SOURCE_DIGESTS.python}));
    const values = createPythonOwnedValues(d.selector, file, contract, fields.model, target);
    const properties = [...d.contract.properties].sort((a, b) => a.name < b.name ? -1 : 1);
    const shapes = properties.map(p => values.render(p.type));
    const fieldBindings = references ? fields.model.bindings.filter(b => b.owner === d.selector) : [];
    const annotations = properties.map((p, i) => {
      const index = fieldBindings.findIndex(b => b.field === p.name);
      // The checked model proves the exact projected endpoint type and wrappers.
      // Python Annotated retains that type plus the qualified reference binding
      // without importing a target factory or inventing an indexed type operator.
      return index < 0 ? shapes[i]!.type : `_Annotated[${shapes[i]!.type}, ${name}FieldBindings[${index}]]`;
    });
    const referencePrelude = references ? `\nfrom typing import Annotated as _Annotated\nfrom ${pythonRelativeModule(file, `${root}/runtime/references.py`)} import FieldBinding as _FieldBinding\n\n${name}FieldBindings = ${tuple(fieldBindings.map(b => `_FieldBinding(${q(b.owner)}, ${q(b.field)}, ${q(b.kind)}, ${q(b.target)}, ${tuple(b.projection.map(q))})`))}\n` : '';
    const selected = [...new Set([...binding.base_validators, ...binding.extensions.flatMap(e => e.validators)].map(v => v.rule))].sort();
    const imports = selected.map((selector, i) => {const m = rules.modules.find(m => m.selector === selector)!; return {...m, local: '_rule' + i, module: pythonRelativeModule(file, m.relative_path)};});
    const bound = (v: FactoryValidatorBinding) => {
      const m = imports.find(m => m.selector === v.rule)!;
      const arguments_ = [...v.arguments].sort((a, b) => a.parameter < b.parameter ? -1 : 1);
      const views = arguments_.map(a => {const e = endpoint(d, a); return q(a.parameter) + ': ' + values.fact(e.type, e.code);});
      const artifact = rules.artifacts.find(a => a.relative_path === m.relative_path)!;
      return {rule: v.rule, arguments: arguments_, closure_sha256: m.closure_sha256, artifact_sha256: artifact.sha256,
        source: `_Validator(${q(v.rule)}, ${q(m.closure_sha256)}, ${q(artifact.sha256)}, lambda fields: ${m.local}({${views.join(', ')}}))`};
    };
    const base = binding.base_validators.map(bound), extensions = [...binding.extensions].sort((a, b) => a.id < b.id ? -1 : 1).map(e => ({id: e.id, validators: e.validators.map(bound)}));
    const keyFields = d.kind === 'Entity' ? properties.filter(p => p.identity) : properties;
    const callable = 'create_' + pythonSnake(node) + '_factory';
    const content = values.prelude(support) + `\nfrom ${pythonRelativeModule(file, factorySupport)} import OwnedSnapshot as _OwnedSnapshot, Validator as _Validator, factory_provider as _factory_provider, invalid_fact as _invalid_fact\n` + imports.map(i => `from ${i.module} import ${i.callable} as ${i.local}\n`).join('') + referencePrelude +
      `\nPROTOCOL_ID = ${q(protocolIds[d.kind])}\nCOMPONENT_PROTOCOL_ID = "python.owned-value-component/v1"\nCOMPONENT_CONTRACT_SHA256 = ${q(contract)}\n\n@_dataclass(frozen=True, slots=True)\nclass ${name}Fields:\n${properties.map((p, i) => `    ${pythonField(p.name)}: ${annotations[i]}\n`).join('')}\n@_dataclass(frozen=True, slots=True, eq=False, init=False, weakref_slot=True)\nclass ${name}Snapshot(_OwnedSnapshot):\n    fields: ${name}Fields\n\n    def __init__(self, *args, **kwargs):\n        raise TypeError("SNAPSHOT_CONSTRUCTION_REQUIRES_FACTORY")\n` +
      (d.kind === 'Entity' ? `\n    @property\n    def identity(self):\n        return ${tuple(keyFields.map(p => 'self.fields.' + pythonField(p.name)))}\n` : '') +
      `\n${callable}, ${name}ValueComponent = _factory_provider(\n    ${name}Snapshot, ${name}Fields,\n    ${tuple(properties.map((p, i) => `(${q(p.name)}, ${q(pythonField(p.name))}, ${shapes[i]!.expression}, ${p.type.kind === 'optional' ? 'True' : 'False'})`))},\n    ${tuple(keyFields.map(p => q(p.name)))}, ${q(d.selector)}, COMPONENT_CONTRACT_SHA256,\n    ${tuple(base.map(v => v.source))},\n    {${extensions.map(e => q(e.id) + ': ' + tuple(e.validators.map(v => v.source))).join(', ')}}, ${d.kind === 'Entity' ? 'True' : 'False'},\n)\n`;
    add(file, content);
    const receipt = ({source, ...v}: typeof base[number]) => v;
    return {selector: d.selector, kind: d.kind, relative_path: file, callable, protocol_id: protocolIds[d.kind], component_contract_sha256: contract,
      fields: properties.map(p => ({name: p.name, native_name: pythonField(p.name), type: p.type, identity: p.identity})), ...(references ? {field_bindings: fieldBindings.map(b => ({...b, projection: [...b.projection]}))} : {}), dependencies: [...values.imports.values()].map(({selector, path}) => ({selector, path})), base_validators: base.map(receipt), extensions: extensions.map(e => ({id: e.id, validators: e.validators.map(receipt)}))};
  });
  for (const d of fields.model.declarations) if (d.kind === 'Enum' && !plain.includes(d)) {
    const file = target(d.selector), node = d.selector.split(':')[1]!, name = pythonSymbol(node), contract = sha256(canonicalJson(d.contract));
    const values = createPythonOwnedValues(d.selector, file, contract, fields.model, target), shape = values.render({kind: 'sum', variants: d.contract.variants}, true);
    add(file, values.prelude(support) + `\n\n${name}Case = ${shape.type}\n${name}ValueComponent = ${shape.expression}\n\ndef create_${pythonSnake(node)}(value: dict[str, object]) -> ${name}Case:\n    return ${name}ValueComponent.normalize(value)\n`);
  }
  add(factorySupport, renderPythonFactorySupport());
  if (references) add(`${root}/runtime/references.py`, renderPythonReferenceSupport());
  for (const file of [...artifacts.keys()]) for (let dir = path.posix.dirname(file); dir !== '.'; dir = path.posix.dirname(dir)) if (!artifacts.has(dir + '/__init__.py')) add(dir + '/__init__.py', '');
  const normalized = modules.map(m => ({selector: m.selector, base_validators: m.base_validators.map(v => ({rule: v.rule, arguments: v.arguments})), extensions: m.extensions.map(e => ({id: e.id, validators: e.validators.map(v => ({rule: v.rule, arguments: v.arguments}))}))}));
  // Resolve artifact identities after emission, never as circular content hashes.
  const referenceBindings = references ? fields.model.bindings.map(b => ({...b, projection: [...b.projection], target_path: target(b.target), target_artifact_sha256: artifacts.get(target(b.target))!.sha256})) : [];
  const body = {schema_version: references ? 'domainspec.configured-python-factories-plan/v2-candidate' : 'domainspec.configured-python-factories-plan/v1-candidate', selection: {...selection, factories: normalized}, certificate: fields.certificate, field_compilation_sha256: fields.compilation_sha256,
    rule_plan_sha256: rules.plan_sha256, source_digests: {...rules.source_digests, factory_contract: STRUCTURED_FACTORY_CONTRACT_SHA256, ...(references ? {reference_contract: REFERENCE_FIELD_FACTORY_CONTRACT_SHA256} : {})}, modules, ...(references ? {reference_bindings: referenceBindings} : {}), artifacts: [...artifacts.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none'} as const;
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
