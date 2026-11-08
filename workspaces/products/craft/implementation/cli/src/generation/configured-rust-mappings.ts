import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {compilePublicMapping} from '../input/compiled-public-mapping.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {checkTypedInputMapping, decodeTypedInputMappingContract, TYPED_MAPPING_INPUTS_VERSION} from '../typed-backend/mapping-inputs.js';
import {isPublicMappingDefinitionSha256, PUBLIC_MAPPING_VERSION, type MappingValueType} from '../typed-backend/mapping-public.js';
import type {TypedType, ValueExpression} from '../typed-operation/contracts.js';
import type {PlannedArtifact} from './contracts.js';
import {renderRustExternalPropertyTypes, rustPascal, rustSelectorModule, rustSelectorType, rustSnake, rustString} from './configured-rust-values.js';

export const RUST_MAPPING_SELECTION_VERSION = 'domainspec.configured-rust-mappings-selection/v1-candidate';
export const RUST_MAPPING_PROTOCOL = 'rust.bound-mapping/v1-candidate';
export const RUST_PUBLIC_MAPPING_PROTOCOL = 'rust.public-bound-mapping/v1-candidate';
export const RUST_MAPPING_CONTRACT_SHA256 = '9b8d456e6b592a250bc070f71b9e6d4e36fe48ee73ad317ff08c9970cf3395db';
export interface RustMappingSelection {readonly schema_version: typeof RUST_MAPPING_SELECTION_VERSION; readonly language: 'rust'; readonly module_root: string; readonly roots: readonly string[]; readonly boundary_sha256: string; readonly field_compilation_sha256: string;}
export interface RustMappingSources {readonly rust_contract: string; readonly public_mapping_contract: string;}
type AnyType = TypedType | MappingValueType;
type Scope = ReadonlyMap<string, {type: AnyType; reference: string}>;
function fail(reason: string): never {throw new TypeError('DS_RUST_MAPPING:' + reason);}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}

function rustType(type: AnyType, reference?: (type: Extract<TypedType,{kind:'reference'}>) => TypedType): string {
  if (type.kind === 'scalar') return type.name === 'String' ? 'String' : type.name === 'Bool' ? 'bool' : 'u64';
  if (type.kind === 'named') return rustSelectorType(type.selector);
  if (type.kind === 'reference') return rustType(reference ? reference(type) : fail('reference resolver required'), reference);
  if (type.kind === 'contract') return `crate::application::interfaces::${rustSelectorModule(type.interface_selector)}::${rustPascal(type.contract_id)}`;
  if (type.kind === 'optional') return `Option<${rustType(type.element, reference)}>`;
  if (type.kind === 'list') return `Vec<${rustType(type.element, reference)}>`;
  if (type.kind === 'set') return `std::collections::BTreeSet<${rustType(type.element, reference)}>`;
  return fail('anonymous sum requires an owning declaration');
}

export function rustMappingPath(moduleRoot: string, selector: string): string {return `${moduleRoot}/src/application/mappings/${rustSelectorModule(selector)}.rs`;}

export function planConfiguredRustMappings(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields, selection: RustMappingSelection, sources: RustMappingSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); assertCompiledProjectFields(fields); assertInterfaceData(selection); assertInterfaceData(sources);
  if (Object.keys(sources).sort().join('|') !== 'public_mapping_contract|rust_contract' || sha256(sources.rust_contract) !== RUST_MAPPING_CONTRACT_SHA256 || !isPublicMappingDefinitionSha256(sha256(sources.public_mapping_contract))) fail('contract drift');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.schema_version !== RUST_MAPPING_SELECTION_VERSION || selection.language !== 'rust') fail('unsupported selection');
  if (selection.boundary_sha256 !== boundary.boundary_sha256 || selection.field_compilation_sha256 !== fields.compilation_sha256 || boundary.certificate.graph_sha256 !== certificate.graph_sha256 || fields.certificate.graph_sha256 !== certificate.graph_sha256 || fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('stale or cross-graph inputs');
  if (selection.module_root.split('/').some(part => {try {rustSnake(part); return false;} catch {return true;}})) fail('portable module root required');
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('bounded unique roots required');
  const roots = [...selection.roots].sort(), declarations = new Map(fields.model.declarations.map(row => [row.selector, row])), nodes = new Map(graph.nodes.map(node => [node.selector, node]));
  const referenceType = (type: Extract<TypedType,{kind:'reference'}>):TypedType => {
    const declaration=declarations.get(type.selector);if(declaration?.kind!=='Entity')return fail('reference target must be an Entity:'+type.selector);
    const field=declaration.contract.properties.find(row=>row.name===type.projection[0]&&row.identity);if(!field)return fail('reference projection must select the Entity identity:'+type.selector+'#'+type.projection[0]);
    return field.type;
  };
  const nativeType=(type:AnyType)=>rustType(type,referenceType);
  const property = (type: AnyType, ontology: string): {name: string|null; type: AnyType} => {
    if(type.kind==='reference'){
      const declaration=declarations.get(type.selector);if(declaration?.kind!=='Entity')return fail('reference target must be an Entity:'+type.selector);
      const field=declaration.contract.properties.find(row=>row.name===type.projection[0]&&row.identity);if(!field||field.ontology_property!==ontology)return fail('reference exposes only its identity projection:'+type.selector);
      return {name:null,type:field.type};
    }
    if (type.kind === 'named') {
      const declaration = declarations.get(type.selector); if (!declaration || declaration.kind === 'Enum') return fail('path owner requires checked fields:' + type.selector);
      const field = declaration.contract.properties.find(row => row.ontology_property === ontology) ?? fail('unknown ontology property:' + ontology); return {name: field.name, type: field.type};
    }
    if (type.kind === 'contract') {
      const api = nodes.get(type.interface_selector); if (api?.kind !== 'Interface') return fail('unknown Interface:' + type.interface_selector);
      const contract = (api.body.typed_contract as any).contracts?.find((row: any) => row.contract_id === type.contract_id) ?? fail('unknown public contract:' + type.contract_id);
      const field = contract.fields.find((row: any) => row.ontology_field === ontology) ?? fail('unknown public ontology field:' + ontology); return {name: field.name, type: {...field.type, ...(field.type.kind === 'contract' ? {interface_selector: type.interface_selector} : {})}};
    }
    return fail('path traversal requires named or contract value');
  };
  const expression = (value: ValueExpression, scope: Scope): {type: AnyType; code: string} => {
    if (value.op === 'literal') {
      const type: AnyType = {kind: 'scalar', name: value.type};
      if (value.type === 'String') return {type, code: `String::from(${rustString(String(value.value))})`};
      if (value.type === 'Bool') return {type, code: value.value ? 'true' : 'false'};
      const integer = BigInt(value.value); if (integer < 0n || integer > 18446744073709551615n) return fail('UInt64 literal out of range'); return {type, code: `${integer}u64`};
    }
    if (value.op === 'variant') {
      const owner = [...declarations.values()].find(row => row.kind === 'Enum' && row.contract.variants.some(variant => variant.ontology_variant === value.selector));
      if (!owner || owner.kind !== 'Enum') return fail('unknown Enum variant:' + value.selector);
      const variant = owner.contract.variants.find(row => row.ontology_variant === value.selector)!; if (variant.payload !== null) return fail('payload variant requires explicit payload support');
      return {type: {kind: 'named', selector: owner.selector}, code: `${rustSelectorType(owner.selector)}::${rustPascal(variant.name)}`};
    }
    if (value.op === 'to_set') {
      const inner = expression(value.value, scope); if (inner.type.kind !== 'list') return fail('to_set requires list');
      return {type: {kind: 'set', element: inner.type.element} as AnyType, code: `${inner.code}.into_iter().collect::<std::collections::BTreeSet<_>>()`};
    }
    let current = scope.get(value.root) ?? fail('unknown Mapping input:' + value.root), code = current.reference, type = current.type;
    for (const ontology of value.properties) {
      const next = property(type, ontology);
      // Interface contracts are structural structs with public fields; domain
      // values retain their generated accessor boundary.
      if (next.name !== null) code = type.kind === 'contract' ? `&(${code}).${rustSnake(next.name)}` : `${code}.${rustSnake(next.name)}()`;
      type = next.type;
    }
    return {type, code: `Clone::clone(${code})`};
  };
  const modules = roots.map(selector => {
    const node = nodes.get(selector); if (node?.kind !== 'Mapping') return fail('selected root is not a Mapping:' + selector);
    const schema = (node.body.typed_contract as {schema_version?: string})?.schema_version, publicMapping = schema === PUBLIC_MAPPING_VERSION ? compilePublicMapping(graph, boundary, fields, selector, sources.public_mapping_contract) : null;
    if (schema !== TYPED_MAPPING_INPUTS_VERSION && !publicMapping) fail('Rust Mapping requires typed-mapping/v2 or v3:' + selector);
    const contract = publicMapping?.contract ?? decodeTypedInputMappingContract(node.body.typed_contract), checked = publicMapping?.bindings ?? checkTypedInputMapping(contract as any, fields.model.declarations);
    const name = rustPascal(selector.split(':')[1]!), symbol = rustSnake(selector.split(':')[1]!);
    const inputs = contract.inputs.map(input => ({name: input.name, type: input.type as AnyType})), scope = new Map(inputs.map(input => [input.name, {type: input.type, reference: rustSnake(input.name)}] as const));
    const rawFields = (publicMapping ? (checked as any).fields : (checked as any).bindings) as readonly any[];
    const checkedFields = rawFields.map(binding => ({name: binding.target?.name ?? binding.field.name, type: (binding.target?.type ?? binding.field.type) as AnyType, value: binding.value as ValueExpression, default: binding.default as ValueExpression | null}));
    const target = contract.target as any, publicTotal = publicMapping !== null && contract.total && target.kind === 'contract';
    let external = new Map<string, string>();
    if (!publicTotal && typeof target === 'string') {const declaration = declarations.get(target); if (!declaration || declaration.kind === 'Enum') fail('Mapping target requires fields'); external = new Map(renderRustExternalPropertyTypes(target, declaration.contract.properties));}
    const result = publicTotal ? nativeType(target) : `${name}Projection`, resultFields = checkedFields.map(field => ({...field, native_type: publicTotal ? nativeType(field.type) : external.get(field.name) ?? nativeType(field.type)}));
    const values = resultFields.map(field => {
      const rendered = expression(field.value, scope);
      const lift = (code: string, type: AnyType) => field.type.kind === 'optional' && type.kind !== 'optional' ? `Some(${code})` : code;
      if (field.default === null) return lift(rendered.code, rendered.type);
      if (rendered.type.kind !== 'optional') return fail('default requires optional');
      const fallback = expression(field.default, scope);
      return `${rendered.code}.map(|value| ${lift('value', rendered.type.element)}).unwrap_or_else(|| ${lift(fallback.code, fallback.type)})`;
    });
    const projection = publicTotal ? '' : `#[derive(Clone, Debug, PartialEq, Eq)]\npub struct ${result} {\n${resultFields.map(field => `    pub ${rustSnake(field.name)}: ${field.native_type},`).join('\n')}\n}\n\n`;
    const parameters = inputs.map(input => `${rustSnake(input.name)}: &${nativeType(input.type)}`).join(', '), protocol = publicMapping ? RUST_PUBLIC_MAPPING_PROTOCOL : RUST_MAPPING_PROTOCOL;
    const content = `// Generated DomainSpec Rust Mapping.\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_CONTRACT_SHA256: &str = ${rustString(sha256(canonicalJson(contract)))};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(protocol)};\n\n${projection}pub fn ${symbol}(${parameters}) -> ${result} {\n    ${result} {\n${resultFields.map((field, index) => `        ${rustSnake(field.name)}: ${values[index]},`).join('\n')}\n    }\n}\n`;
    const relative_path = rustMappingPath(selection.module_root, selector);
    return {selector, symbol, relative_path, source_schema: schema, protocol_id: protocol, inputs, target, public_total: publicTotal, result, result_fields: resultFields.map(({value: _value, default: _default, ...field}) => field), contract_sha256: sha256(canonicalJson(contract)), mapping_sha256: publicMapping?.mapping_sha256 ?? null, artifact: artifact(relative_path, content)};
  });
  const body = {schema_version: 'domainspec.configured-rust-mappings-plan/v1-candidate' as const, selection: {...selection, roots}, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256, contract_sha256: RUST_MAPPING_CONTRACT_SHA256, public_mapping_contract_sha256: sha256(sources.public_mapping_contract), protocol_ids: [RUST_MAPPING_PROTOCOL, RUST_PUBLIC_MAPPING_PROTOCOL], modules: modules.map(({artifact: _artifact, ...module}) => module), artifacts: modules.map(module => module.artifact).sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
