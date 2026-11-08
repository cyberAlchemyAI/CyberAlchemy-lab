import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, EXACT_FIELD_CONTRACT_SHA256, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertInterfaceData, decodeNamedInterface, checkInterfacePublicClosure, NAMED_INTERFACE_DEFINITION_SHA256} from '../typed-backend/interface.js';
import {INTERFACE_VERSION_POLICY_DEFINITION_SHA256} from '../typed-backend/interface-version-policy.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {PYTHON_ENUM_SOURCE_DIGESTS, pythonPortableIdentifier} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {renderPythonInterface} from './configured-python-interface-source.js';
import {renderPythonValueSupport} from './configured-python-value-source.js';
import {renderPythonFactSupport} from './configured-python-fact-source.js';
import type {PlannedArtifact} from './contracts.js';

export const PYTHON_INTERFACE_VERSION = 'domainspec.configured-python-interfaces-selection/v1-candidate';
export const PYTHON_INTERFACE_PROTOCOL = 'python.bound-interface/v1';
export const PYTHON_INTERFACE_SOURCE_DIGESTS = Object.freeze({...PYTHON_ENUM_SOURCE_DIGESTS,
  interface_contract: NAMED_INTERFACE_DEFINITION_SHA256, version_contract: INTERFACE_VERSION_POLICY_DEFINITION_SHA256, field_contract: EXACT_FIELD_CONTRACT_SHA256});
export type PythonInterfaceSources = Readonly<Record<keyof typeof PYTHON_INTERFACE_SOURCE_DIGESTS, string>>;
export interface PythonInterfaceSelection {
  readonly schema_version: typeof PYTHON_INTERFACE_VERSION;
  readonly language: 'python';
  readonly boundary_sha256: string;
  readonly field_compilation_sha256: string | null;
  readonly module_root: string;
  readonly roots: readonly string[];
}
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_INTERFACE:' + reason);};
function closed(value: unknown, keys: readonly string[]): void {
  assertInterfaceData(value);
  if (!value || typeof value !== 'object' || Array.isArray(value) || canonicalJson(Object.keys(value).sort()) !== canonicalJson([...keys].sort())) fail('closed data fields required');
}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}

/** Pure source-only planner. Empty/minimal public contracts need no fabricated
 * field model. Named domain values require their exact checked closure. */
export function planConfiguredPythonInterfaces(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields | null, selection: PythonInterfaceSelection, sources: PythonInterfaceSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary);
  if (fields !== null) assertCompiledProjectFields(fields);
  closed(selection, ['schema_version', 'language', 'boundary_sha256', 'field_compilation_sha256', 'module_root', 'roots']);
  closed(sources, Object.keys(PYTHON_INTERFACE_SOURCE_DIGESTS));
  if (selection.schema_version !== PYTHON_INTERFACE_VERSION || selection.language !== 'python') fail('unsupported selection');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.boundary_sha256 !== boundary.boundary_sha256 || boundary.certificate.graph_sha256 !== certificate.graph_sha256 || selection.field_compilation_sha256 !== (fields?.compilation_sha256 ?? null) ||
      (fields !== null && (fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION || fields.certificate.graph_sha256 !== certificate.graph_sha256))) fail('stale or cross-graph selection');
  if (typeof selection.module_root !== 'string') fail('module root required');
  const segments = selection.module_root.split('/'); segments.forEach(pythonPortableIdentifier);
  if (['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref', 'codecs', 'encodings'].includes(segments[0]!)) fail('module root shadows standard library');
  if (!Array.isArray(selection.roots) || selection.roots.length < 1 || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('unique bounded roots required');
  for (const selector of selection.roots) {
    if (typeof selector !== 'string' || selector.split(':').length !== 2) fail('qualified selector required');
    selector.split(':').forEach(pythonPortableIdentifier);
  }
  for (const key of Object.keys(PYTHON_INTERFACE_SOURCE_DIGESTS) as (keyof PythonInterfaceSources)[])
    if (typeof sources[key] !== 'string' || sha256(sources[key]) !== PYTHON_INTERFACE_SOURCE_DIGESTS[key]) fail('source drift:' + key);
  const cell = JSON.parse(sources.configuration).types.find((c: {kind: string}) => c.kind === 'Interface');
  if (cell?.role !== 'application/interfaces' || canonicalJson(cell.blocked_by) !== '["DSR-009","DSR-011"]') fail('Interface configuration');
  const overlay = JSON.parse(sources.python).representation_overlays.find((o: {contract_id: string}) => o.contract_id === 'interface.profile-representation');
  if (overlay?.candidate_protocols.length !== 1 || overlay.candidate_protocols[0].protocol_id !== PYTHON_INTERFACE_PROTOCOL || overlay.candidate_protocols[0].form_id !== 'python.bound-interface-protocol') fail('Interface profile');
  const root = segments.map(pythonSnake).join('/'), roots = [...selection.roots].sort(), files = new Map<string, PlannedArtifact>();
  const add = (relative_path: string, content: string): PlannedArtifact => {
    if (files.has(relative_path)) fail('artifact collision:' + relative_path);
    const artifact = {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)}; files.set(relative_path, artifact);
    const parts = relative_path.split('/');
    for (let i = 1; i < parts.length; i++) {const file = parts.slice(0, i).join('/') + '/__init__.py'; if (!files.has(file)) files.set(file, {relative_path: file, content: '', size_bytes: 0, sha256: sha256('')});}
    return artifact;
  };
  const runtime = [add(`${root}/runtime/values.py`, renderPythonValueSupport()), add(`${root}/runtime/facts.py`, renderPythonFactSupport())];
  const modules = roots.map(selector => {
    const node = graph.nodes.find(n => n.selector === selector);
    if (!node || node.kind !== 'Interface' || node.body.typed_contract === undefined) return fail('typed Interface required:' + selector);
    const contract = decodeNamedInterface(node.body.typed_contract);
    checkInterfacePublicClosure(contract, fields?.model.declarations ?? []);
    const sourcePath = `specs/${node.feature_id}/nodes/${node.node_id}.json`;
    const source = graph.source_manifest.sources.find(s => s.relative_path === sourcePath) ?? fail('missing source evidence');
    const relative_path = `${root}/features/${pythonSnake(node.feature_id)}/src/${cell.role}/${pythonSnake(node.node_id)}.py`;
    const body = {schema_version: 'domainspec.generated-python-interface-descriptor/v1-candidate', protocol_id: PYTHON_INTERFACE_PROTOCOL, selector,
      definition_sha256: NAMED_INTERFACE_DEFINITION_SHA256, version_definition_sha256: INTERFACE_VERSION_POLICY_DEFINITION_SHA256, graph_sha256: certificate.graph_sha256,
      source: {relative_path: sourcePath, sha256: source.sha256}, field_compilation_sha256: fields?.compilation_sha256 ?? null,
      contract_sha256: sha256(canonicalJson(contract)), contract, effect_contract: 'structural-interface-and-pure-shape-normalizers',
      invariant_execution: 'not-performed', transport_execution: 'not-performed', member_execution: 'not-performed',
      runtime: runtime.map(a => ({id: a.relative_path.split('/').at(-1)!, sha256: a.sha256})), authority_effect: 'none'};
    const descriptor = {...body, descriptor_sha256: sha256(canonicalJson(body))};
    const runtimeModule = pythonRelativeModule(relative_path, `${root}/runtime/values.py`).replace(/\.values$/, '');
    const artifact = add(relative_path, renderPythonInterface(selector, contract, fields?.model ?? null, runtimeModule, descriptor).content);
    return {selector, relative_path, import_name: relative_path.slice(0, -3).replaceAll('/', '.'), artifact_sha256: artifact.sha256, descriptor};
  });
  const body = {schema_version: 'domainspec.configured-python-interfaces-plan/v1-candidate' as const, selection: {...selection, roots},
    source_digests: PYTHON_INTERFACE_SOURCE_DIGESTS, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields?.compilation_sha256 ?? null,
    modules, artifacts: [...files.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), discharged_configuration_prerequisites: ['DSR-009', 'DSR-011'], authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
