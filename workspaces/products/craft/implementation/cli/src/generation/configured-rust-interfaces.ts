import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData, checkInterfacePublicClosure, decodeNamedInterface, NAMED_INTERFACE_DEFINITION_SHA256, type InterfacePublicType} from '../typed-backend/interface.js';
import {INTERFACE_VERSION_POLICY_DEFINITION_SHA256} from '../typed-backend/interface-version-policy.js';
import {rustPascal, rustSelectorModule, rustSelectorType, rustSnake, rustString} from './configured-rust-values.js';
import type {PlannedArtifact} from './contracts.js';

export const RUST_INTERFACE_SELECTION_VERSION = 'domainspec.configured-rust-interfaces-selection/v1-candidate';
export const RUST_INTERFACE_PROTOCOL = 'rust.bound-interface/v1-candidate';
export const RUST_INTERFACE_CONTRACT_SHA256 = 'c45725bfcd7e958f47736d2d20b9f8e8ace83719d8fbc2e147463d82c025f359';
export interface RustInterfaceSelection {readonly schema_version: typeof RUST_INTERFACE_SELECTION_VERSION; readonly language: 'rust'; readonly module_root: string; readonly roots: readonly string[]; readonly boundary_sha256: string; readonly field_compilation_sha256: string | null;}
export interface RustInterfaceSources {readonly rust_contract: string; readonly interface_contract: string; readonly version_contract: string;}
function fail(reason: string): never {throw new TypeError('DS_RUST_INTERFACE:' + reason);}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
export function rustInterfacePath(root: string, selector: string): string {return `${root}/src/application/interfaces/${rustSelectorModule(selector)}.rs`;}

export function planConfiguredRustInterfaces(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields | null, selection: RustInterfaceSelection, sources: RustInterfaceSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); if (fields) assertCompiledProjectFields(fields); assertInterfaceData(selection); assertInterfaceData(sources);
  if (Object.keys(sources).sort().join('|') !== 'interface_contract|rust_contract|version_contract' || sha256(sources.rust_contract) !== RUST_INTERFACE_CONTRACT_SHA256 || sha256(sources.interface_contract) !== NAMED_INTERFACE_DEFINITION_SHA256 || sha256(sources.version_contract) !== INTERFACE_VERSION_POLICY_DEFINITION_SHA256) fail('contract drift');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.schema_version !== RUST_INTERFACE_SELECTION_VERSION || selection.language !== 'rust' || selection.boundary_sha256 !== boundary.boundary_sha256 || selection.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null) || boundary.certificate.graph_sha256 !== certificate.graph_sha256 || fields && (fields.certificate.graph_sha256 !== certificate.graph_sha256 || fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION)) fail('unsupported or stale selection');
  selection.module_root.split('/').forEach(rustSnake);
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('bounded unique roots required');
  const modules = [...selection.roots].sort().map(selector => {
    const node = graph.nodes.find(row => row.selector === selector); if (node?.kind !== 'Interface' || !node.body.typed_contract) return fail('typed Interface required:' + selector);
    const contract = decodeNamedInterface(node.body.typed_contract); checkInterfacePublicClosure(contract, fields?.model.declarations ?? []);
    for (const operation of contract.operations) {const target = graph.nodes.find(row => row.selector === operation.operation_ref); if (!target || target.kind !== 'Operation' && target.kind !== 'Query') fail('Interface operation reference must resolve:' + operation.operation_ref);}
    const definitions: string[] = [], used = new Set<string>();
    const type = (value: InterfacePublicType, hint: string): string => {
      if (value.kind === 'scalar') return value.name === 'String' ? 'String' : value.name === 'Bool' ? 'bool' : 'u64';
      if (value.kind === 'named') return rustSelectorType(value.selector);
      if (value.kind === 'contract') return rustPascal(value.contract_id);
      if (value.kind === 'optional') return `Option<${type(value.element, hint + 'Value')}>`;
      if (value.kind === 'list') return `Vec<${type(value.element, hint + 'Item')}>`;
      if (value.kind === 'set') return `std::collections::BTreeSet<${type(value.element, hint + 'Item')}>`;
      if (value.kind !== 'sum') return fail('unsupported public type');
      let name = hint; for (let i = 2; used.has(name); i++) name = hint + i; used.add(name);
      const variants = value.variants.map(variant => `    ${rustPascal(variant.name)}${variant.payload ? `(${type(variant.payload, name + rustPascal(variant.name))})` : ''},`).join('\n');
      definitions.push(`#[derive(Clone, Debug, PartialEq, Eq)]\npub enum ${name} {\n${variants}\n}`); return name;
    };
    const structs = [...contract.contracts].sort((left, right) => left.contract_id < right.contract_id ? -1 : 1).map(publicContract => {
      const name = rustPascal(publicContract.contract_id); used.add(name);
      const fields = [...publicContract.fields].sort((left, right) => left.name < right.name ? -1 : 1).map(field => `    pub ${rustSnake(field.name)}: ${type(field.type, name + rustPascal(field.name))},`).join('\n');
      return `#[derive(Clone, Debug, PartialEq, Eq)]\npub struct ${name} {\n${fields}\n}`;
    });
    const operations = [...contract.operations].sort((left, right) => left.operation_id < right.operation_id ? -1 : 1).map(operation => ({...operation, request_type: type(operation.request, rustPascal(operation.operation_id) + 'Request'), result_type: type(operation.result, rustPascal(operation.operation_id) + 'Result')}));
    const traitName = rustPascal(selector.split(':')[1]!) + 'Provider';
    const methods = operations.map(operation => `    async fn ${rustSnake(operation.operation_id)}(&self, request: ${operation.request_type}) -> Result<${operation.result_type}, InterfaceError>;`).join('\n');
    const mode = contract.version_policy.mode, provider = contract.version_policy.provider_version;
    const comparison = mode === 'exact' ? '' : `fn number_le(left: &str, right: &str) -> bool { left.len() < right.len() || left.len() == right.len() && left <= right }\n`;
    const version = `fn parse_version(value: &str) -> Option<[&str; 3]> {\n    let mut parts = value.split('.'); let result = [parts.next()?, parts.next()?, parts.next()?];\n    if parts.next().is_some() || result.iter().any(|part| part.is_empty() || part.len() > 64 || !part.bytes().all(|byte| byte.is_ascii_digit()) || part.len() > 1 && part.starts_with('0')) { None } else { Some(result) }\n}\n${comparison}pub fn accepts_consumer_version(value: &str) -> bool {\n    let Some(candidate) = parse_version(value) else { return false; }; let provider = parse_version(${rustString(provider)}).expect("generated provider version");\n    ${mode === 'exact' ? 'candidate == provider' : 'candidate[0] == provider[0] && (number_le(candidate[1], provider[1]) && (candidate[1].len() != provider[1].len() || candidate[1] != provider[1]) || candidate[1] == provider[1] && number_le(candidate[2], provider[2]))'}\n}`;
    const content = `// Generated DomainSpec Rust Interface.\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(RUST_INTERFACE_PROTOCOL)};\npub const PROVIDER_VERSION: &str = ${rustString(provider)};\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub struct InterfaceError;\n\n${definitions.join('\n\n')}${definitions.length ? '\n\n' : ''}${structs.join('\n\n')}\n\n#[allow(async_fn_in_trait)]\npub trait ${traitName} {\n${methods}\n}\n\n${version}\n`;
    const relative_path = rustInterfacePath(selection.module_root, selector); return {selector, relative_path, provider_trait: traitName, operation_dependencies: operations.map(operation => operation.operation_ref), artifact: artifact(relative_path, content), contract_sha256: sha256(canonicalJson(contract))};
  });
  const body = {schema_version: 'domainspec.configured-rust-interfaces-plan/v1-candidate' as const, selection: {...selection, roots: [...selection.roots].sort()}, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null, contract_sha256: RUST_INTERFACE_CONTRACT_SHA256, protocol_id: RUST_INTERFACE_PROTOCOL, modules: modules.map(({artifact: _artifact, ...module}) => module), artifacts: modules.map(module => module.artifact), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
