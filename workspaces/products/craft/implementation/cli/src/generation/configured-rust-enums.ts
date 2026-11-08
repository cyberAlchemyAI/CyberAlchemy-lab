import {assertCompiledProjectFields, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import type {PlannedArtifact} from './contracts.js';
import {renderRustOwnedType, rustPascal, rustSelectorModule, rustSnake, rustString} from './configured-rust-values.js';

export const RUST_ENUM_SELECTION_VERSION = 'domainspec.configured-rust-enums-selection/v1-candidate';
export const RUST_ENUM_PROTOCOL = 'rust.nominal-enum-explicit-wire/v1';
export const RUST_ALGEBRAIC_SUM_PROTOCOL = 'rust.owned-algebraic-sum/v1-candidate';
export const RUST_ENUM_CONTRACT_SHA256 = '03fdd1f2300c17a6297bc3c09e7702f16f43f684b038383bc7a771bf8b19ca35';

export interface RustEnumSelection {
  readonly schema_version: typeof RUST_ENUM_SELECTION_VERSION;
  readonly language: 'rust';
  readonly module_root: string;
  readonly field_compilation_sha256: string;
  readonly roots: readonly string[];
}

function fail(reason: string): never {throw new TypeError('DS_RUST_ENUM:' + reason);}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function inert(value: unknown, depth = 0): void {
  if (depth > 32) fail('selection depth');
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return;
  if (!value || typeof value !== 'object' || ![Object.prototype, null, Array.prototype].includes(Object.getPrototypeOf(value))) fail('inert data required');
  for (const key of Reflect.ownKeys(value)) {if (Array.isArray(value) && key === 'length') continue; const descriptor = Object.getOwnPropertyDescriptor(value, key)!; if (typeof key !== 'string' || !('value' in descriptor) || !descriptor.enumerable) fail('inert enumerable fields required'); inert(descriptor.value, depth + 1);}
}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}

export function rustEnumPath(moduleRoot: string, selector: string): string {
  return `${moduleRoot}/src/domain/types/${rustSelectorModule(selector)}.rs`;
}

/** Native Rust Enum realization. Payload decoding is deliberately outside this
 * bounded protocol; unit variants receive explicit total emit/fallible parse. */
export function planConfiguredRustEnums(fields: CompiledProjectFields, selection: RustEnumSelection, contractSource: string) {
  assertCompiledProjectFields(fields); assertInterfaceData(selection); inert(selection); inert(contractSource);
  if (sha256(contractSource) !== RUST_ENUM_CONTRACT_SHA256) fail('contract drift');
  if (selection.schema_version !== RUST_ENUM_SELECTION_VERSION || selection.language !== 'rust' || fields.compilation_sha256 !== selection.field_compilation_sha256) fail('stale or unsupported selection');
  const rootParts = selection.module_root.split('/'); if (!rootParts.length || rootParts.some(part => {try {rustSnake(part); return false;} catch {return true;}})) fail('portable module root required');
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('bounded unique roots required');
  const declarations = new Map(fields.model.declarations.map(row => [row.selector, row]));
  const modules = selection.roots.map(selector => {
    const declaration = declarations.get(selector); if (!declaration || declaration.kind !== 'Enum') return fail('selected root is not a checked Enum:' + selector);
    const name = rustPascal(selector.split(':')[1]!), ordinal = {value: 0};
    const variants = declaration.contract.variants.map(variant => ({variant, payload: variant.payload === null ? null : renderRustOwnedType(variant.payload, name, ordinal)}));
    const support = [...new Set(variants.flatMap(row => row.payload?.support ?? []))].sort();
    const definitions = [...new Set(variants.flatMap(row => row.payload?.definitions ?? []))];
    const members = variants.map(({variant, payload}) => `    ${rustPascal(variant.name)}${payload ? `(${payload.type})` : ''},`).join('\n');
    const unit = variants.every(row => row.payload === null), functionName = rustSnake(selector.split(':')[1]!);
    const error = unit ? `\n#[derive(Clone, Debug, PartialEq, Eq)]\npub struct ${name}WireError {\n    pub code: &'static str,\n    pub enum_selector: &'static str,\n    pub wire_value: String,\n}\n` : '';
    const wire = unit ? `\npub fn emit_${functionName}(value: ${name}) -> &'static str {\n    match value {\n${variants.map(({variant}) => `        ${name}::${rustPascal(variant.name)} => ${rustString(variant.name)},`).join('\n')}\n    }\n}\n\npub fn parse_${functionName}(wire: &str) -> Result<${name}, ${name}WireError> {\n    match wire {\n${variants.map(({variant}) => `        ${rustString(variant.name)} => Ok(${name}::${rustPascal(variant.name)}),`).join('\n')}\n        unknown => Err(${name}WireError { code: "DOMAINSPEC_ENUM_UNKNOWN_WIRE", enum_selector: DOMAINSPEC_SELECTOR, wire_value: unknown.to_owned() }),\n    }\n}\n` : `\npub fn ${functionName}_variant(value: &${name}) -> &'static str {\n    match value {\n${variants.map(({variant, payload}) => `        ${name}::${rustPascal(variant.name)}${payload ? '(_)' : ''} => ${rustString(variant.name)},`).join('\n')}\n    }\n}\n`;
    const protocol_id = unit ? RUST_ENUM_PROTOCOL : RUST_ALGEBRAIC_SUM_PROTOCOL;
    const content = `// Generated DomainSpec Rust Enum.\n${support.map(item => `use ${item};`).join('\n')}${support.length ? '\n\n' : ''}pub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_CONTRACT_SHA256: &str = ${rustString(sha256(canonicalJson(declaration.contract)))};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(protocol_id)};\n\n${definitions.join('\n\n')}${definitions.length ? '\n\n' : ''}#[derive(${unit ? 'Copy, ' : ''}Clone, Debug, PartialEq, Eq, Hash)]\npub enum ${name} {\n${members}\n}\n${error}${wire}`;
    const relative_path = rustEnumPath(selection.module_root, selector);
    return {selector, kind: declaration.kind, relative_path, symbol: name, unit, protocol_id, variants: variants.map(({variant, payload}) => ({name: variant.name, ontology_variant: variant.ontology_variant, payload: variant.payload, native_payload: payload?.type ?? null})), contract_sha256: sha256(canonicalJson(declaration.contract)), artifact: artifact(relative_path, content)};
  });
  const body = {schema_version: 'domainspec.configured-rust-enums-plan/v1-candidate' as const, selection: {...selection, roots: [...selection.roots]}, field_compilation_sha256: fields.compilation_sha256, contract_sha256: RUST_ENUM_CONTRACT_SHA256, protocol_ids: [RUST_ENUM_PROTOCOL, RUST_ALGEBRAIC_SUM_PROTOCOL], modules: modules.map(({artifact: _artifact, ...module}) => module), artifacts: modules.map(module => module.artifact).sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
