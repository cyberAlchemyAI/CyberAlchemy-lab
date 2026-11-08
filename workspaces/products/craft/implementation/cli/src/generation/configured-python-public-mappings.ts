import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {compilePublicMapping} from '../input/compiled-public-mapping.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {PUBLIC_MAPPING_CONTRACT_SHA256,isPublicMappingDefinitionSha256} from '../typed-backend/mapping-public.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {PYTHON_INTERFACE_SOURCE_DIGESTS, PYTHON_INTERFACE_VERSION, planConfiguredPythonInterfaces, type PythonInterfaceSources} from './configured-python-interfaces.js';
import {PUBLIC_BOUNDARY_GENERATION_SHA256} from './configured-public-boundaries.js';
import {pythonPortableIdentifier} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {renderPythonPublicMapping} from './configured-python-public-mapping-source.js';
import {renderPythonMappingBinding} from './configured-python-mapping-source.js';
import {renderPythonValueSupport} from './configured-python-value-source.js';
import {renderPythonFactSupport} from './configured-python-fact-source.js';
import type {PlannedArtifact} from './contracts.js';

export const PYTHON_PUBLIC_MAPPING_VERSION = 'domainspec.configured-python-public-mappings-selection/v1-candidate';
export const PYTHON_PUBLIC_MAPPING_SOURCE_DIGESTS = Object.freeze({...PYTHON_INTERFACE_SOURCE_DIGESTS, public_mapping_contract: PUBLIC_MAPPING_CONTRACT_SHA256, generation_contract: PUBLIC_BOUNDARY_GENERATION_SHA256});
export type PythonPublicMappingSources = Readonly<Record<keyof typeof PYTHON_PUBLIC_MAPPING_SOURCE_DIGESTS, string>>;
export interface PythonPublicMappingSelection {
  readonly schema_version: typeof PYTHON_PUBLIC_MAPPING_VERSION;
  readonly language: 'python';
  readonly boundary_sha256: string;
  readonly field_compilation_sha256: string | null;
  readonly module_root: string;
  readonly roots: readonly string[];
}
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_PUBLIC_MAPPING:' + reason);};
function closed(value: unknown, keys: readonly string[]): void {
  assertInterfaceData(value);
  if (!value || typeof value !== 'object' || Array.isArray(value) || canonicalJson(Object.keys(value).sort()) !== canonicalJson([...keys].sort())) fail('closed fields required');
}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}

/** Non-effectful candidate planner. The public Mapping checker owns endpoint and
 * relation meaning; this adapter selects Python source and package imports only. */
export function planConfiguredPythonPublicMappings(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields | null, selection: PythonPublicMappingSelection, sources: PythonPublicMappingSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); if (fields !== null) assertCompiledProjectFields(fields);
  closed(selection, ['schema_version', 'language', 'boundary_sha256', 'field_compilation_sha256', 'module_root', 'roots']);
  closed(sources, Object.keys(PYTHON_PUBLIC_MAPPING_SOURCE_DIGESTS));
  if (selection.schema_version !== PYTHON_PUBLIC_MAPPING_VERSION || selection.language !== 'python') fail('unsupported selection');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.boundary_sha256 !== boundary.boundary_sha256 || boundary.certificate.graph_sha256 !== certificate.graph_sha256 || selection.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null) ||
      (fields !== null && (fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION || fields.certificate.graph_sha256 !== certificate.graph_sha256))) fail('stale or cross-graph selection');
  if (typeof selection.module_root !== 'string') fail('module root required');
  const segments = selection.module_root.split('/'); segments.forEach(pythonPortableIdentifier);
  if (['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref', 'codecs', 'encodings'].includes(segments[0]!)) fail('module root shadows standard library');
  if (!Array.isArray(selection.roots) || selection.roots.length < 1 || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('unique bounded roots required');
  for (const selector of selection.roots) {if (typeof selector !== 'string' || selector.split(':').length !== 2) fail('qualified selector required'); selector.split(':').forEach(pythonPortableIdentifier);}
  if (typeof sources.public_mapping_contract !== 'string' || !isPublicMappingDefinitionSha256(sha256(sources.public_mapping_contract))) fail('source drift:public_mapping_contract');
  const sourceDigests = {...PYTHON_PUBLIC_MAPPING_SOURCE_DIGESTS, public_mapping_contract: sha256(sources.public_mapping_contract)};
  for (const key of Object.keys(sourceDigests) as (keyof PythonPublicMappingSources)[])
    if (typeof sources[key] !== 'string' || sha256(sources[key]) !== sourceDigests[key]) fail('source drift:' + key);
  const cell = JSON.parse(sources.configuration).types.find((c: {kind: string}) => c.kind === 'Mapping');
  if (cell?.role !== 'application/mappings' || canonicalJson(cell.blocked_by) !== '["DSR-009","DSR-011","DSR-014"]') fail('Mapping configuration');
  const overlay = JSON.parse(sources.python).representation_overlays.find((o: {contract_id: string}) => o.contract_id === 'mapping.profile-representation');
  if (overlay?.candidate_protocols.length !== 1 || overlay.candidate_protocols[0].protocol_id !== 'python.bound-mapping/v1' || overlay.candidate_protocols[0].form_id !== 'python.bound-mapping-function') fail('Mapping profile');
  const roots = [...selection.roots].sort(), root = segments.map(pythonSnake).join('/');
  const mappings = roots.map(selector => compilePublicMapping(graph, boundary, fields, selector, sources.public_mapping_contract));
  const interfaceRoots = [...new Set(mappings.flatMap(m => m.bindings.interface_selectors))].sort();
  const interfaceSources = Object.fromEntries(Object.keys(PYTHON_INTERFACE_SOURCE_DIGESTS).map(k => [k, sources[k as keyof PythonInterfaceSources]])) as unknown as PythonInterfaceSources;
  const interfaces = interfaceRoots.length ? planConfiguredPythonInterfaces(graph, boundary, fields, {...selection, schema_version: PYTHON_INTERFACE_VERSION, roots: interfaceRoots}, interfaceSources) : null;
  const files = new Map<string, PlannedArtifact>(interfaces?.artifacts.map(a => [a.relative_path, a]) ?? []);
  const add = (relative_path: string, content: string) => {
    if (files.has(relative_path) && files.get(relative_path)!.content !== content) fail('artifact collision:' + relative_path);
    const artifact = {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)}; files.set(relative_path, artifact);
    const parts = relative_path.split('/');
    for (let i = 1; i < parts.length; i++) {const file = parts.slice(0, i).join('/') + '/__init__.py'; if (!files.has(file)) files.set(file, {relative_path: file, content: '', size_bytes: 0, sha256: sha256('')});}
    return artifact;
  };
  add(root + '/runtime/values.py', renderPythonValueSupport()); add(root + '/runtime/facts.py', renderPythonFactSupport());
  const modules = mappings.map(mapping => {
    const [feature, node] = mapping.selector.split(':') as [string, string];
    const relative_path = `${root}/features/${pythonSnake(feature)}/src/${cell.role}/${pythonSnake(node)}.py`, provider_path = relative_path.replace(/\/([^/]+)\.py$/, '/_providers/$1.py');
    const imports = mapping.bindings.interface_selectors.map((selector, i) => {
      const api = interfaces?.modules.find(m => m.selector === selector) ?? fail('missing Interface dependency');
      return {selector, alias: '_api' + i, path: pythonRelativeModule(provider_path, api.relative_path), descriptor: api.descriptor, artifact_sha256: api.artifact_sha256};
    });
    const runtimeModule = pythonRelativeModule(provider_path, root + '/runtime/values.py').replace(/\.values$/, '');
    const rendered = renderPythonPublicMapping(mapping, fields, imports, runtimeModule), provider = add(provider_path, rendered.content), callable = 'mapping_' + pythonSnake(node);
    const body = {schema_version: 'domainspec.generated-python-public-mapping-descriptor/v1-candidate', protocol_id: 'python.bound-mapping/v1', selector: mapping.selector,
      mapping_sha256: mapping.mapping_sha256, definition_sha256: PUBLIC_BOUNDARY_GENERATION_SHA256, contract: mapping.contract, bindings: mapping.bindings,
      imports: imports.map(i => ({selector: i.selector, path: i.path, artifact_sha256: i.artifact_sha256, contract_sha256: i.descriptor.contract_sha256})),
      provider_sha256: provider.sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null, graph_sha256: certificate.graph_sha256,
      result_fields: rendered.result_fields, return_semantics: 'field-projection-not-construction', effect_contract: 'pure-explicit-field-projection', invariant_execution: 'not-performed', authority_effect: 'none'};
    const descriptor = {...body, descriptor_sha256: sha256(canonicalJson(body))};
    add(relative_path, renderPythonMappingBinding(pythonRelativeModule(relative_path, provider_path), callable, descriptor));
    return {selector: mapping.selector, relative_path, provider_path, import_name: relative_path.slice(0, -3).replaceAll('/', '.'), callable, descriptor};
  });
  const body = {schema_version: 'domainspec.configured-python-public-mappings-plan/v1-candidate' as const, selection: {...selection, roots}, source_digests: sourceDigests,
    certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null,
    interfaces: interfaces?.modules ?? [], modules, mappings, artifacts: [...files.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1),
    discharged_configuration_prerequisites: ['DSR-009', 'DSR-011'], bounded_prerequisite_evidence: {'DSR-014': 'explicit-projection-bindings-not-parent-completion'}, authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
