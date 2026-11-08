import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {decodeExactCalculation, EXACT_CALCULATION_VERSION} from '../typed-backend/calculation-exact.js';
import {decodeTypedCalculationContract} from '../typed-backend/contracts.js';
import {PYTHON_ENUM_SOURCE_DIGESTS, pythonPortableIdentifier} from './configured-python-enums.js';
import {pythonRelativeModule, pythonSnake} from './configured-python-owned-values.js';
import {CALCULATION_CONTRACT_SHA256} from './configured-calculations.js';
import {CALCULATION_V2_CONTRACT_SHA256} from './configured-calculations-v2.js';
import {renderPythonCalculationBinding, renderPythonCalculationProvider, renderPythonCalculationSupport} from './configured-python-calculation-source.js';
import type {PlannedArtifact} from './contracts.js';

export const PYTHON_CALCULATION_VERSION = 'domainspec.configured-python-calculations-selection/v1-candidate';
export const PYTHON_CALCULATION_PROTOCOL = 'python.bound-calculation/v1';
export const PYTHON_CALCULATION_SOURCE_DIGESTS = Object.freeze({...PYTHON_ENUM_SOURCE_DIGESTS,
  calculation_contract: CALCULATION_CONTRACT_SHA256, exact_calculation_contract: CALCULATION_V2_CONTRACT_SHA256});
export interface PythonCalculationSelection {
  readonly schema_version: typeof PYTHON_CALCULATION_VERSION;
  readonly language: 'python';
  readonly boundary_sha256: string;
  readonly module_root: string;
  readonly roots: readonly string[];
}
export type PythonCalculationSources = Readonly<Record<keyof typeof PYTHON_CALCULATION_SOURCE_DIGESTS, string>>;
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_CALCULATION:' + reason);};
function closed(value: unknown, keys: readonly string[]): void {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('plain data object required');
  const d = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(d).length !== keys.length || Reflect.ownKeys(d).some(k => typeof k !== 'string' || !keys.includes(k)) || Object.values(d).some(p => !Object.hasOwn(p, 'value') || !p.enumerable)) fail('closed data fields required');
}
function roots(value: unknown): string[] {
  if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) return fail('plain roots array required');
  const d: Record<string, PropertyDescriptor> = Object.getOwnPropertyDescriptors(value), length = d.length!.value;
  if (length < 1 || length > 256 || Reflect.ownKeys(d).length !== length + 1) fail('bounded dense roots required');
  const result: string[] = [];
  for (let i = 0; i < length; i++) {
    const p = d[String(i)];
    if (!p || !Object.hasOwn(p, 'value') || !p.enumerable || typeof p.value !== 'string') return fail('inert string roots required');
    result.push(p.value);
  }
  if (new Set(result).size !== result.length) fail('duplicate roots');
  return result.sort();
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;
}

/** Python realization of existing checked v1/v2 contracts. Does not change source
 * admission, interpret generated TypeScript, re-read sources, or publish output. */
export function planConfiguredPythonCalculations(boundary: CompiledCompositionBoundary, selection: PythonCalculationSelection, sources: PythonCalculationSources) {
  assertCompiledCompositionBoundary(boundary);
  closed(selection, ['schema_version', 'language', 'boundary_sha256', 'module_root', 'roots']);
  closed(sources, Object.keys(PYTHON_CALCULATION_SOURCE_DIGESTS));
  if (selection.schema_version !== PYTHON_CALCULATION_VERSION || selection.language !== 'python') fail('unsupported selection');
  if (selection.boundary_sha256 !== boundary.boundary_sha256) fail('stale boundary');
  if (typeof selection.module_root !== 'string') fail('module root required');
  const segments = selection.module_root.split('/'); segments.forEach(pythonPortableIdentifier);
  if (['enum', 'typing', 'types', 'builtins', 'dataclasses', 'collections', 'json', 'sys', 'hashlib', 'weakref'].includes(segments[0]!)) fail('module root shadows standard library');
  const root = segments.map(pythonSnake).join('/'), selected = roots(selection.roots);
  for (const key of Object.keys(PYTHON_CALCULATION_SOURCE_DIGESTS) as (keyof PythonCalculationSources)[])
    if (typeof sources[key] !== 'string' || sha256(sources[key]) !== PYTHON_CALCULATION_SOURCE_DIGESTS[key]) fail('source drift:' + key);
  const cell = JSON.parse(sources.configuration).types.find((t: {kind: string}) => t.kind === 'Calculation');
  if (cell?.role !== 'domain/calculations' || canonicalJson(cell.blocked_by) !== '["DSR-011"]') fail('Calculation configuration');
  const overlay = JSON.parse(sources.python).representation_overlays.find((o: {contract_id: string}) => o.contract_id === 'calculation.profile-representation');
  const protocol = overlay?.candidate_protocols.find((p: {protocol_id: string}) => p.protocol_id === PYTHON_CALCULATION_PROTOCOL);
  const descriptorContract = {return_semantics: 'value', effect_contract: 'none', dependency_contract: 'explicit-only', failure_contract: 'declared', result_consumption: 'complete', primary_callable_count: 1, supporting_exports: 'explicit-only'};
  if (protocol?.form_id !== 'python.calculation-function' || canonicalJson(protocol.descriptor_contract) !== canonicalJson(descriptorContract)) fail('Calculation profile');
  const files = new Map<string, PlannedArtifact>();
  const add = (relative_path: string, content: string): PlannedArtifact => {
    if (files.has(relative_path) && files.get(relative_path)!.content !== content) fail('artifact collision:' + relative_path);
    const artifact = {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)}; files.set(relative_path, artifact);
    const parts = relative_path.split('/');
    for (let i = 1; i < parts.length; i++) {
      const file = parts.slice(0, i).join('/') + '/__init__.py';
      if (!files.has(file)) files.set(file, {relative_path: file, content: '', size_bytes: 0, sha256: sha256('')});
    }
    return artifact;
  };
  const support = add(`${root}/runtime/calculations.py`, renderPythonCalculationSupport());
  const modules = selected.map(selector => {
    const parts = selector.split(':'); if (parts.length !== 2) fail('selector required'); parts.forEach(pythonPortableIdentifier);
    const [feature, node] = parts as [string, string];
    const row = boundary.value_bindings.core_contracts.find(c => c.owner.selector === selector);
    if (!row || row.kind !== 'Calculation') return fail('typed Calculation required:' + selector);
    const exact = (row.contract as {readonly schema_version: unknown}).schema_version === EXACT_CALCULATION_VERSION;
    const contract = exact ? decodeExactCalculation(row.contract) : decodeTypedCalculationContract(row.contract);
    if (contract.inputs.some(p => p.type.kind !== 'scalar' || p.type.name !== 'UInt64')) fail('UInt64 inputs required');
    const relative_path = `${root}/features/${pythonSnake(feature)}/src/${cell.role}/${pythonSnake(node)}.py`;
    const provider_path = relative_path.replace(/\/([^/]+)\.py$/, '/_providers/$1.py');
    const implementation = add(provider_path, renderPythonCalculationProvider(contract, pythonRelativeModule(provider_path, support.relative_path)));
    const callable = 'calculate_' + pythonSnake(node);
    const body = {schema_version: 'domainspec.generated-python-calculation-descriptor/v1-candidate', protocol_id: PYTHON_CALCULATION_PROTOCOL, selector,
      ontology_calculation: contract.ontology_calculation, contract_sha256: sha256(canonicalJson(contract)), source: row.source,
      source_version: contract.schema_version, definition_sha256: exact ? CALCULATION_V2_CONTRACT_SHA256 : CALCULATION_CONTRACT_SHA256,
      inputs: contract.inputs, result: contract.result, division_rounding: contract.division_rounding,
      native_values: {input: 'exact-python-int-or-canonical-decimal-string', output: 'exact-python-int', bool: 'rejected', float: 'rejected'}, ...descriptorContract,
      failures: exact ? JSON.parse(sources.exact_calculation_contract).runtime_contract.failures : JSON.parse(sources.calculation_contract).failures,
      provider: {id: selector + '/python-exact/v1', sha256: implementation.sha256}, runtime: {id: 'python.calculation-arithmetic/v1', sha256: support.sha256}, authority_effect: 'none'};
    const descriptor = {...body, descriptor_sha256: sha256(canonicalJson(body))};
    const provider_import = pythonRelativeModule(relative_path, provider_path);
    add(relative_path, renderPythonCalculationBinding(provider_import, callable, descriptor));
    return {selector, relative_path, import_name: relative_path.slice(0, -3).replaceAll('/', '.'), provider_path, provider_import, callable, descriptor};
  });
  const body = {schema_version: 'domainspec.configured-python-calculations-plan/v1-candidate' as const, selection: {...selection, roots: selected},
    source_digests: PYTHON_CALCULATION_SOURCE_DIGESTS, boundary_sha256: boundary.boundary_sha256, certificate: boundary.certificate,
    modules, artifacts: [...files.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : 1),
    discharged_configuration_prerequisites: ['DSR-011'], authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
