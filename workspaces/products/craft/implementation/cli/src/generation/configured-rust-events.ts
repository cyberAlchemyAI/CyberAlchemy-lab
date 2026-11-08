import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph, type FieldSpec} from '../input/project-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import type {PlannedArtifact} from './contracts.js';
import type {EventSource} from './configured-event-source.js';
import {rustPascal, rustSelectorModule, rustSnake, rustString} from './configured-rust-values.js';
import {eventReferenceIdentity} from './event-reference-identity.js';

export const RUST_EVENT_SELECTION_VERSION = 'domainspec.configured-rust-events-selection/v1-candidate';
export const RUST_EVENT_PROTOCOL = 'rust.bound-event/v1-candidate';
export const RUST_EVENT_CONTRACT_SHA256 = '9c854c3ef098265a952a50ce1d1aa2ee31edf1ee39fcc86ed37de3e3d3de1cc1';
export interface RustEventSelection {readonly schema_version: typeof RUST_EVENT_SELECTION_VERSION; readonly language: 'rust'; readonly module_root: string; readonly roots: readonly string[]; readonly boundary_sha256: string;}
function fail(reason: string): never {throw new TypeError('DS_RUST_EVENT:' + reason);}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
function referenceName(selector: string): string {const [feature, node, ...rest] = selector.split(':'); if (!feature || !node || rest.length) return fail('qualified reference required'); return `EventRefF${feature.length}${rustPascal(feature)}N${node.length}${rustPascal(node)}`;}
function baseType(field: FieldSpec): string {
  if (field.type_ref.kind === 'reference') return referenceName(field.type_ref.selector);
  return ({string: 'String', boolean: 'bool', integer: 'i64', decimal: 'f64', timestamp: 'String', uuid: 'String'} as const)[field.type_ref.name];
}
const rustType = (field: FieldSpec) => field.required ? baseType(field) : `Option<${baseType(field)}>`;
function validation(field: FieldSpec, code: string, error: string): string {
  if (field.type_ref.kind === 'reference' || field.type_ref.name === 'string' || field.type_ref.name === 'boolean' || field.type_ref.name === 'integer') return '';
  const condition = field.type_ref.name === 'decimal' ? '!value.is_finite()' : 'value.is_empty()';
  return field.required ? `    { let value = &${code}; if ${condition} { return Err(${error}::${field.type_ref.name === 'decimal' ? 'InvalidDecimal' : 'InvalidText'}); } }\n` : `    if let Some(value) = &${code} && ${condition} { return Err(${error}::${field.type_ref.name === 'decimal' ? 'InvalidDecimal' : 'InvalidText'}); }\n`;
}
function moved(field: FieldSpec, code: string): string {
  if (field.type_ref.kind !== 'reference' && field.type_ref.name === 'decimal') return field.required ? `if ${code} == 0.0 { 0.0 } else { ${code} }` : `${code}.map(|value| if value == 0.0 { 0.0 } else { value })`;
  return code;
}
export function rustEventPath(moduleRoot: string, selector: string): string {return `${moduleRoot}/src/domain/events/${rustSelectorModule(selector)}.rs`;}

export function planConfiguredRustEvents(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, selection: RustEventSelection, contractSource: string) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); assertInterfaceData(selection); assertInterfaceData(contractSource);
  if (sha256(contractSource) !== RUST_EVENT_CONTRACT_SHA256) fail('contract drift');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.schema_version !== RUST_EVENT_SELECTION_VERSION || selection.language !== 'rust' || selection.boundary_sha256 !== boundary.boundary_sha256 || boundary.certificate.graph_sha256 !== certificate.graph_sha256) fail('unsupported or stale selection');
  if (selection.module_root.split('/').some(part => {try {rustSnake(part); return false;} catch {return true;}})) fail('portable module root required');
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('bounded unique roots required');
  const roots = [...selection.roots].sort(), nodes = new Map(graph.nodes.map(node => [node.selector, node]));
  const modules = roots.map(selector => {
    const node = nodes.get(selector), bound = boundary.domain_graph.nodes.find(row => row.selector === selector); if (node?.kind !== 'Event' || bound?.kind !== 'Event') return fail('selected root is not a bound Event:' + selector);
    const source = structuredClone(node.body) as unknown as EventSource; if (!source.occurrence_id.required) fail('occurrence identity must be required');
    const payload = [...source.payload].sort((left, right) => left.field_id < right.field_id ? -1 : left.field_id > right.field_id ? 1 : 0), names = [source.occurrence_id, ...payload].map(field => rustSnake(field.field_id));
    if (new Set(names).size !== names.length) fail('Rust field name collision');
    const references = [...new Set([source.occurrence_id, ...payload].flatMap(field => field.type_ref.kind === 'reference' ? [field.type_ref.selector] : []))].sort();
    const identities=new Map(references.map(reference=>[reference,eventReferenceIdentity(graph,reference,fail)]));
    const name = rustPascal(selector.split(':')[1]!), input = `${name}Input`, occurrenceInput = `${name}OccurrenceInput`, payloadInput = `${name}PayloadInput`, occurrence = `${name}Occurrence`, payloadName = `${name}Payload`, value = `${name}Event`, error = `${name}EventError`, symbol = `create_${rustSnake(selector.split(':')[1]!)}`;
    const referenceDefinitions = references.map(reference => {const ref = referenceName(reference),identity=identities.get(reference)!; return identity.scalar==='UInt64'
      ? `#[derive(Clone, Debug, PartialEq, Eq, Hash)]\npub struct ${ref}(u64);\n\nimpl ${ref} {\n    pub const fn new(value: u64) -> Self { Self(value) }\n    pub const fn value(&self) -> u64 { self.0 }\n}`
      : `#[derive(Clone, Debug, PartialEq, Eq, Hash)]\npub struct ${ref}(String);\n\nimpl ${ref} {\n    pub fn new(value: String) -> Result<Self, ${error}> { if value.is_empty() { Err(${error}::InvalidText) } else { Ok(Self(value)) } }\n    pub fn as_str(&self) -> &str { &self.0 }\n}`;}).join('\n\n');
    const inputTime = source.occurred_at_policy === 'required' ? '    pub occurred_at: String,\n' : '';
    const timeParameter = source.occurred_at_policy === 'generated' ? `, clock: &impl Fn() -> String` : '';
    const timeValidation = source.occurred_at_policy === 'required' ? '    if input.occurred_at.is_empty() { return Err(' + error + '::InvalidText); }\n' : '';
    const timeValue = source.occurred_at_policy === 'required' ? 'input.occurred_at' : `{ let value = clock(); if value.is_empty() { return Err(${error}::InvalidText); } value }`;
    const validations = validation(source.occurrence_id, `input.occurrence.${rustSnake(source.occurrence_id.field_id)}`, error) + payload.map(field => validation(field, `input.payload.${rustSnake(field.field_id)}`, error)).join('');
    const content = `// Generated DomainSpec Rust Event.\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_CONTRACT_SHA256: &str = ${rustString(sha256(canonicalJson(source)))};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(RUST_EVENT_PROTOCOL)};\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub enum ${error} { InvalidText, InvalidDecimal }\n\nimpl ${error} { pub const fn code(self) -> &'static str { match self { Self::InvalidText => \"DOMAINSPEC_EVENT_TEXT\", Self::InvalidDecimal => \"DOMAINSPEC_EVENT_DECIMAL\" } } }\n\n${referenceDefinitions}${referenceDefinitions ? '\n\n' : ''}#[derive(Clone, Debug)]\npub struct ${occurrenceInput} { pub ${rustSnake(source.occurrence_id.field_id)}: ${rustType(source.occurrence_id)} }\n\n#[derive(Clone, Debug)]\npub struct ${payloadInput} {\n${payload.map(field => `    pub ${rustSnake(field.field_id)}: ${rustType(field)},`).join('\n')}\n}\n\n#[derive(Clone, Debug)]\npub struct ${input} {\n    pub occurrence: ${occurrenceInput},\n${inputTime}    pub payload: ${payloadInput},\n}\n\n#[derive(Clone, Debug, PartialEq)]\npub struct ${occurrence} { ${rustSnake(source.occurrence_id.field_id)}: ${rustType(source.occurrence_id)} }\n\nimpl ${occurrence} { pub fn ${rustSnake(source.occurrence_id.field_id)}(&self) -> &${rustType(source.occurrence_id)} { &self.${rustSnake(source.occurrence_id.field_id)} } }\n\n#[derive(Clone, Debug, PartialEq)]\npub struct ${payloadName} {\n${payload.map(field => `    ${rustSnake(field.field_id)}: ${rustType(field)},`).join('\n')}\n}\n\nimpl ${payloadName} {\n${payload.map(field => `    pub fn ${rustSnake(field.field_id)}(&self) -> &${rustType(field)} { &self.${rustSnake(field.field_id)} }`).join('\n')}\n}\n\n#[derive(Clone, Debug, PartialEq)]\npub struct ${value} { occurrence: ${occurrence}, occurred_at: String, payload: ${payloadName} }\n\nimpl ${value} {\n    pub const fn event_type(&self) -> &'static str { ${rustString(source.event_type)} }\n    pub const fn version(&self) -> &'static str { ${rustString(source.version)} }\n    pub fn occurrence(&self) -> &${occurrence} { &self.occurrence }\n    pub fn occurred_at(&self) -> &str { &self.occurred_at }\n    pub fn payload(&self) -> &${payloadName} { &self.payload }\n}\n\npub fn ${symbol}(input: ${input}${timeParameter}) -> Result<${value}, ${error}> {\n${timeValidation}${validations}    let occurred_at = ${timeValue};\n    Ok(${value} {\n        occurrence: ${occurrence} { ${rustSnake(source.occurrence_id.field_id)}: ${moved(source.occurrence_id, `input.occurrence.${rustSnake(source.occurrence_id.field_id)}`)} },\n        occurred_at,\n        payload: ${payloadName} {\n${payload.map(field => `            ${rustSnake(field.field_id)}: ${moved(field, `input.payload.${rustSnake(field.field_id)}`)},`).join('\n')}\n        },\n    })\n}\n`;
    const relative_path = rustEventPath(selection.module_root, selector);
    return {selector, symbol, input, value, error, relative_path, event_type: source.event_type, version: source.version, occurred_at_policy: source.occurred_at_policy, occurrence_id: source.occurrence_id, payload, references, contract_sha256: sha256(canonicalJson(source)), artifact: artifact(relative_path, content)};
  });
  const body = {schema_version: 'domainspec.configured-rust-events-plan/v1-candidate' as const, selection: {...selection, roots}, certificate, boundary_sha256: boundary.boundary_sha256, contract_sha256: RUST_EVENT_CONTRACT_SHA256, protocol_id: RUST_EVENT_PROTOCOL, modules: modules.map(({artifact: _artifact, ...module}) => module), artifacts: modules.map(module => module.artifact).sort((left, right) => left.relative_path < right.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
