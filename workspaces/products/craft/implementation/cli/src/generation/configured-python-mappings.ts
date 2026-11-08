import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {decodeTypedMappingContract} from '../typed-backend/contracts.js';
import {decodeTypedInputMappingContract, TYPED_MAPPING_INPUTS_VERSION} from '../typed-backend/mapping-inputs.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {PYTHON_ENUM_SOURCE_DIGESTS, pythonPortableIdentifier} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {MAPPING_CONTRACT_SHA256} from './configured-mappings.js';
import {renderPythonMapping, renderPythonMappingBinding} from './configured-python-mapping-source.js';
import {renderPythonValueSupport} from './configured-python-value-source.js';
import {renderPythonFactSupport} from './configured-python-fact-source.js';
import type {PlannedArtifact} from './contracts.js';

export const PYTHON_MAPPING_VERSION = 'domainspec.configured-python-mappings-selection/v1-candidate';
export const PYTHON_MAPPING_PROTOCOL = 'python.bound-mapping/v1';
export const PYTHON_MAPPING_SOURCE_DIGESTS = Object.freeze({...PYTHON_ENUM_SOURCE_DIGESTS, mapping_contract: MAPPING_CONTRACT_SHA256, field_contract: EXACT_FIELD_CONTRACT_SHA256});
export interface PythonMappingSelection {
  readonly schema_version: typeof PYTHON_MAPPING_VERSION;
  readonly language: 'python';
  readonly boundary_sha256: string;
  readonly field_compilation_sha256: string;
  readonly module_root: string;
  readonly roots: readonly string[];
}
export type PythonMappingSources = Readonly<Record<keyof typeof PYTHON_MAPPING_SOURCE_DIGESTS, string>>;
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_MAPPING:' + reason);};
function closed(value: unknown, keys: readonly string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('plain data object required');
  const d = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(d).length !== keys.length || Reflect.ownKeys(d).some(k => typeof k !== 'string' || !keys.includes(k)) || Object.values(d).some(p => !Object.hasOwn(p, 'value') || !p.enumerable)) fail('closed data fields required');
}
function roots(value: unknown): string[] {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) return fail('plain roots required');
  const d: Record<string, PropertyDescriptor> = Object.getOwnPropertyDescriptors(value), length = d.length!.value;
  if (length < 1 || length > 256 || Reflect.ownKeys(d).length !== length + 1) fail('bounded dense roots required');
  const result: string[] = [];
  for (let i = 0; i < length; i++) {const p = d[String(i)]; if (!p || !Object.hasOwn(p, 'value') || !p.enumerable || typeof p.value !== 'string') return fail('inert roots required'); result.push(p.value);}
  if (new Set(result).size !== result.length) fail('duplicate roots'); return result.sort();
}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}

/** Domain Mapping v1/v2 only. Public v3 remains an explicit Interface dependency,
 * never flattened into domain records. Plans are source-only and non-effectful. */
export function planConfiguredPythonMappings(boundary: CompiledCompositionBoundary, fields: CompiledProjectFields, selection: PythonMappingSelection, sources: PythonMappingSources) {
  assertCompiledCompositionBoundary(boundary); assertCompiledProjectFields(fields);
  closed(selection, ['schema_version', 'language', 'boundary_sha256', 'field_compilation_sha256', 'module_root', 'roots']);
  closed(sources, Object.keys(PYTHON_MAPPING_SOURCE_DIGESTS));
  if (selection.schema_version !== PYTHON_MAPPING_VERSION || selection.language !== 'python') fail('unsupported selection');
  if (selection.boundary_sha256 !== boundary.boundary_sha256 || selection.field_compilation_sha256 !== fields.compilation_sha256 || fields.certificate.graph_sha256 !== boundary.certificate.graph_sha256) fail('stale or cross-graph selection');
  if (fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('exact checked fields required');
  if (typeof selection.module_root !== 'string') fail('module root required');
  const segments = selection.module_root.split('/'); segments.forEach(pythonPortableIdentifier);
  if (['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref', 'codecs', 'encodings'].includes(segments[0]!)) fail('module root shadows standard library');
  const root = segments.map(pythonSnake).join('/'), selected = roots(selection.roots);
  for (const key of Object.keys(PYTHON_MAPPING_SOURCE_DIGESTS) as (keyof PythonMappingSources)[])
    if (typeof sources[key] !== 'string' || sha256(sources[key]) !== PYTHON_MAPPING_SOURCE_DIGESTS[key]) fail('source drift:' + key);
  const cell = JSON.parse(sources.configuration).types.find((t: {kind: string}) => t.kind === 'Mapping');
  if (cell?.role !== 'application/mappings' || canonicalJson(cell.blocked_by) !== '["DSR-009","DSR-011","DSR-014"]') fail('Mapping configuration');
  const overlay = JSON.parse(sources.python).representation_overlays.find((o: {contract_id: string}) => o.contract_id === 'mapping.profile-representation');
  const protocol = overlay?.candidate_protocols.find((p: {protocol_id: string}) => p.protocol_id === PYTHON_MAPPING_PROTOCOL);
  if (protocol?.form_id !== 'python.bound-mapping-function') fail('Mapping profile');
  const files = new Map<string, PlannedArtifact>();
  const add = (relative_path: string, content: string): PlannedArtifact => {
    if (files.has(relative_path) && files.get(relative_path)!.content !== content) fail('artifact collision:' + relative_path);
    const artifact = {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)}; files.set(relative_path, artifact);
    const parts = relative_path.split('/');
    for (let i = 1; i < parts.length; i++) {const file = parts.slice(0, i).join('/') + '/__init__.py'; if (!files.has(file)) files.set(file, {relative_path: file, content: '', size_bytes: 0, sha256: sha256('')});}
    return artifact;
  };
  const runtime = [add(`${root}/runtime/values.py`, renderPythonValueSupport()), add(`${root}/runtime/facts.py`, renderPythonFactSupport())];
  const modules = selected.map(selector => {
    const parts = selector.split(':'); if (parts.length !== 2) fail('selector required'); parts.forEach(pythonPortableIdentifier);
    const [feature, node] = parts as [string, string], row = boundary.value_bindings.core_contracts.find(c => c.owner.selector === selector);
    if (!row || row.kind !== 'Mapping') return fail('typed Mapping required:' + selector);
    const version = (row.contract as {schema_version: string}).schema_version;
    if (version === 'domainspec.typed-mapping/v3') fail('public Mapping v3 requires the Python Interface adapter');
    const contract = version === TYPED_MAPPING_INPUTS_VERSION ? decodeTypedInputMappingContract(row.contract) : decodeTypedMappingContract(row.contract);
    const relative_path = `${root}/features/${pythonSnake(feature)}/src/${cell.role}/${pythonSnake(node)}.py`, provider_path = relative_path.replace(/\/([^/]+)\.py$/, '/_providers/$1.py');
    const runtimeModule = pythonRelativeModule(provider_path, `${root}/runtime/values.py`).replace(/\.values$/, '');
    const rendered = renderPythonMapping(contract, fields.model, runtimeModule), implementation = add(provider_path, rendered.content);
    const callable = 'mapping_' + pythonSnake(node), provider_import = pythonRelativeModule(relative_path, provider_path);
    const body = {schema_version: 'domainspec.generated-python-mapping-descriptor/v1-candidate', protocol_id: PYTHON_MAPPING_PROTOCOL, selector,
      ontology_mapping: contract.ontology_mapping, source_schema: contract.schema_version, contract_sha256: sha256(canonicalJson(contract)), source: row.source, inputs: rendered.inputs,
      target: {selector: contract.target, kind: rendered.target_kind, fields: rendered.result_fields}, total: contract.total, field_model_sha256: fields.model.model_sha256,
      fields: contract.fields, default_semantics: version === TYPED_MAPPING_INPUTS_VERSION ? 'explicit-nullish-fallback' : 'absent-source-property-only',
      native_values: 'python.immutable-typed-read-facts/v1-candidate', return_semantics: 'field-projection-not-construction', effect_contract: 'pure-explicit-values', dependency_contract: 'declared-inputs-only', result_consumption: 'complete', primary_callable_count: 1,
      failures: ['MAPPING_INPUT', 'MAPPING_REQUIRED_VALUE'], provider: {id: selector + '/python-exact/v1', sha256: implementation.sha256}, runtime: runtime.map(a => ({id: a.relative_path.split('/').at(-1)!, sha256: a.sha256})), authority_effect: 'none'};
    const descriptor = {...body, descriptor_sha256: sha256(canonicalJson(body))}; add(relative_path, renderPythonMappingBinding(provider_import, callable, descriptor));
    return {selector, relative_path, import_name: relative_path.slice(0, -3).replaceAll('/', '.'), provider_path, provider_import, callable, descriptor};
  });
  const body = {schema_version: 'domainspec.configured-python-mappings-plan/v1-candidate' as const, selection: {...selection, roots: selected},
    source_digests: PYTHON_MAPPING_SOURCE_DIGESTS, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256,
    certificate: boundary.certificate, modules, artifacts: [...files.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1),
    discharged_configuration_prerequisites: ['DSR-009', 'DSR-011'], bounded_prerequisite_evidence: {'DSR-014': 'explicit-typed-inputs-and-target-bindings-not-parent-completion'}, authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
