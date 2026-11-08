import path from 'node:path';
import {assertCompiledProjectFields, PROJECT_FIELD_SELECTION_VERSION, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {PROFILED_SOURCE_DIGESTS} from './profiled-project.js';
import type {PlannedArtifact} from './contracts.js';

// PCR-06 plain Enum slice. Boundaries and open questions: ENUM-GENERATION.md
// in development/reconciliation-v1/profile-compiler-reconciliation.
export const CONFIGURED_ENUM_VERSION = 'domainspec.configured-enums-selection/v1-candidate';
export const EXACT_CONFIGURED_ENUM_VERSION = 'domainspec.configured-enums-selection/v2-candidate';
export const ENUM_CONFIGURATION_SHA256 = '9ac018e42080483f373219049b466d8a515cb3e7748181ea8e635b1162af8317';
export const ENUM_PROVIDER_SHA256 = '378e09358713b431e4a24e664e484feae0122462e47aabfa653ae21a17315fcc';
export interface ConfiguredEnumSelection {
  readonly schema_version: typeof CONFIGURED_ENUM_VERSION | typeof EXACT_CONFIGURED_ENUM_VERSION;
  readonly language: 'typescript';
  readonly module_root: string;
  readonly field_compilation_sha256: string;
}
export interface EnumConfigurationSources {
  readonly configuration: string;
  readonly base: string;
  readonly typescript: string;
  readonly provider: string;
}
export interface ConfiguredEnumModule {
  readonly selector: string;
  readonly relative_path: string;
  readonly symbol: string;
  readonly provider_import: string;
  readonly members: readonly Readonly<{name: string; wire_value: string; ontology_variant: string}>[];
}
export interface ConfiguredEnumsPlan {
  readonly schema_version: 'domainspec.configured-enums-plan/v1-candidate' | 'domainspec.configured-enums-plan/v2-candidate';
  readonly selection: ConfiguredEnumSelection;
  readonly source_digests: Readonly<Record<keyof EnumConfigurationSources, string>>;
  readonly certificate: CompiledProjectFields['certificate'];
  readonly model_sha256: string;
  readonly modules: readonly ConfiguredEnumModule[];
  readonly runtime_support: Readonly<{relative_path: string; protocol_id: string; provider_source_path: string; sha256: string}>;
  readonly artifacts: readonly PlannedArtifact[];
  readonly input_envelope: 'plain-enum-variant-name-wire/v1-candidate';
  readonly authority_effect: 'none';
  readonly plan_sha256: string;
}
const fail = (message: string): never => {throw new Error('DS_CONFIGURED_ENUM:' + message);};
const reserved = new Set(('as async await break case catch class const continue crate debugger def default del do else enum except export extends false finally fn for from function global if impl import in interface is lambda let loop match mod move mut new nonlocal null package pass private protected pub public raise ref return self static struct super switch this throw trait true try type typeof unsafe use var void while with yield con prn aux nul ' + Array.from({length: 9}, (_, i) => `com${i + 1} lpt${i + 1}`).join(' ')).split(' '));
function keys(value: unknown, expected: readonly string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return fail('unknown or missing fields');
  const descriptors = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(value).some(k => typeof k !== 'string') || Object.keys(descriptors).sort().join('|') !== [...expected].sort().join('|') || Object.values(descriptors).some(d => !('value' in d) || !d.enumerable)) fail('unknown or missing fields');
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);}
  return value;
}

/** Plan every declaration in the explicitly selected checked model. No filtering,
 * invariant execution, source reread, file writes or default-compiler activation.
 */
export function planConfiguredEnums(fields: CompiledProjectFields, selection: ConfiguredEnumSelection, sources: EnumConfigurationSources): ConfiguredEnumsPlan {
  assertCompiledProjectFields(fields);
  const requestedVersion = selection && typeof selection === 'object' ? Object.getOwnPropertyDescriptor(selection, 'schema_version')?.value : undefined;
  if (fields.selection.schema_version !== PROJECT_FIELD_SELECTION_VERSION && requestedVersion !== EXACT_CONFIGURED_ENUM_VERSION) fail('exact field values require an explicit exact Enum realization');
  keys(selection, ['schema_version', 'language', 'module_root', 'field_compilation_sha256']);
  keys(sources, ['configuration', 'base', 'typescript', 'provider']);
  const exactValues = selection.schema_version === EXACT_CONFIGURED_ENUM_VERSION;
  if ((!exactValues && selection.schema_version !== CONFIGURED_ENUM_VERSION) || selection.language !== 'typescript') fail('unsupported selection');
  if (exactValues && fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('exact Enum selection requires exact checked fields');
  if (selection.field_compilation_sha256 !== fields.compilation_sha256) fail('stale field compilation');
  if (typeof selection.module_root !== 'string' || !/^[a-z][a-z0-9-]*(?:\/[a-z][a-z0-9-]*)*$/.test(selection.module_root)) fail('unsafe module root');
  if (selection.module_root.split('/').some(p => reserved.has(p))) fail('reserved module root');
  const source_digests = {configuration: ENUM_CONFIGURATION_SHA256, base: PROFILED_SOURCE_DIGESTS.base, typescript: PROFILED_SOURCE_DIGESTS.typescript, provider: ENUM_PROVIDER_SHA256};
  for (const key of ['configuration', 'base', 'typescript', 'provider'] as const) {
    if (typeof sources[key] !== 'string' || sha256(sources[key]) !== source_digests[key]) fail('source drift:' + key);
  }
  const config = JSON.parse(sources.configuration) as {types: Array<{kind: string; role: string; blocked_by: string[]}>};
  const cell = config.types.find(t => t.kind === 'Enum');
  // DSR-009 is selected as candidate evidence, not cleared from the frozen configuration.
  if (!cell || cell.role !== 'domain/enums' || canonicalJson(cell.blocked_by) !== canonicalJson(['DSR-009'])) return fail('unsupported Enum configuration');
  const profile = JSON.parse(sources.typescript) as {representation_overlays: Array<{contract_id: string; activation_binding: {protocol_id: string}; candidate_protocols: Array<{protocol_id: string; status: string; runtime_provider: {module_path: string; provider_sha256: string}}>}>};
  const overlay = profile.representation_overlays.find(o => o.contract_id === 'enum.profile-representation');
  const protocol = overlay?.candidate_protocols.find(p => p.protocol_id === overlay.activation_binding.protocol_id);
  if (!protocol || protocol.protocol_id !== 'typescript.owned-const-object-enum/v1' || protocol.status !== 'active' || protocol.runtime_provider.provider_sha256 !== ENUM_PROVIDER_SHA256) return fail('unselected Enum provider');
  const runtime_support = {relative_path: `${selection.module_root}/runtime/enum.ts`, protocol_id: protocol.protocol_id,
    provider_source_path: protocol.runtime_provider.module_path, sha256: ENUM_PROVIDER_SHA256};
  const modules: ConfiguredEnumModule[] = fields.model.declarations.map(d => {
    if (d.kind !== 'Enum') return fail('unsupported declaration kind:' + d.selector);
    if (d.contract.variants.some(v => v.payload !== null)) fail('payload-bearing sum unsupported:' + d.selector);
    const [feature, node] = d.selector.split(':') as [string, string];
    for (const id of [feature, node]) if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(id) || reserved.has(id)) fail('unsupported portable identifier:' + id);
    const symbol = node.split('-').map(w => w[0]!.toUpperCase() + w.slice(1)).join('');
    if (symbol === 'EnumValue') fail('provider symbol collision:' + symbol);
    const relative_path = `${selection.module_root}/features/${feature}/src/${cell.role}/${node}.ts`;
    const relative = path.posix.relative(path.posix.dirname(relative_path), runtime_support.relative_path).replace(/\.ts$/, '.js');
    const members = d.contract.variants.map(v => ({name: v.name, wire_value: v.name, ontology_variant: v.ontology_variant})).sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
    return {selector: d.selector, relative_path, symbol, provider_import: relative.startsWith('.') ? relative : './' + relative, members};
  });
  const artifact = (relative_path: string, content: string): PlannedArtifact => ({relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)});
  const artifacts = [...modules.map(m => artifact(m.relative_path,
    `import {defineEnum} from ${JSON.stringify(m.provider_import)};\n` +
    `import type {EnumValue} from ${JSON.stringify(m.provider_import)};\n` +
    `export const ${m.symbol} = defineEnum({${m.members.map(v => `${JSON.stringify(v.name)}:${JSON.stringify(v.wire_value)}`).join(',')}} as const);\n` +
    `export type ${m.symbol} = EnumValue<typeof ${m.symbol}>;\n`)), artifact(runtime_support.relative_path, sources.provider)];
  const body = {schema_version: exactValues ? 'domainspec.configured-enums-plan/v2-candidate' as const : 'domainspec.configured-enums-plan/v1-candidate' as const, selection: {...selection}, source_digests,
    certificate: fields.certificate, model_sha256: fields.model.model_sha256, modules, runtime_support, artifacts,
    input_envelope: 'plain-enum-variant-name-wire/v1-candidate' as const, authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
