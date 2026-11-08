import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {compileSelectedProjectFields, EXACT_FIELD_CONTRACT_SHA256, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import type {PlannedArtifact} from './contracts.js';
import {planConfiguredPythonEnums, resolvePythonEnumContext, PYTHON_ENUM_SELECTION_VERSION, PYTHON_ENUM_SOURCE_DIGESTS, pythonPortableIdentifier, type PythonEnumSources} from './configured-python-enums.js';
import {renderPythonValueSupport} from './configured-python-value-source.js';
import {createPythonOwnedValues, pythonSymbol as symbol, pythonSnake as snake} from './configured-python-owned-values.js';

export const PYTHON_ALGEBRAIC_ENUM_VERSION = 'domainspec.configured-python-algebraic-enums-selection/v1-candidate';
export interface PythonAlgebraicEnumSelection {
  readonly schema_version: typeof PYTHON_ALGEBRAIC_ENUM_VERSION;
  readonly language: 'python';
  readonly module_root: string;
  readonly field_compilation_sha256: string;
}
const fail = (reason: string): never => {throw new TypeError('DS_PYTHON_SUM:' + reason);};
function closed(value: unknown, keys: readonly string[]) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail('inert object');
  const d = Object.getOwnPropertyDescriptors(value);
  if (Reflect.ownKeys(d).some(k => typeof k !== 'string') || Object.keys(d).sort().join('|') !== [...keys].sort().join('|') || Object.values(d).some(x => !('value' in x) || !x.enumerable)) fail('closed data fields');
}
function freeze<T>(v: T): T {if (v && typeof v === 'object' && !Object.isFrozen(v)) {Object.values(v).forEach(freeze);Object.freeze(v);}return v;}

/** Static Python algebraic Enum closure. Records must go through validated
 * factories, not an unvalidated data-class fallback. R10-PYTHON.md owns scope. */
export function planConfiguredPythonAlgebraicEnums(graph: CompiledProjectGraph, fields: CompiledProjectFields, selection: PythonAlgebraicEnumSelection, sources: PythonEnumSources & {readonly field_contract: string}) {
  assertCompiledProjectSnapshot(graph);
  closed(selection, ['schema_version', 'language', 'module_root', 'field_compilation_sha256']);
  closed(sources, ['configuration', 'base', 'python', 'field_contract']);
  if (selection.schema_version !== PYTHON_ALGEBRAIC_ENUM_VERSION) fail('selection version');
  const plainSources = {configuration: sources.configuration, base: sources.base, python: sources.python};
  const plainSelection = {...selection, schema_version: PYTHON_ENUM_SELECTION_VERSION} as const;
  const {root, role} = resolvePythonEnumContext(fields, plainSelection, plainSources);
  if (sha256(sources.field_contract) !== EXACT_FIELD_CONTRACT_SHA256 || canonicalJson(fields.certificate) !== canonicalJson(createCompiledProjectCertificate(graph))) fail('stale graph or field contract');
  for (const d of fields.model.declarations) {
    if (d.kind !== 'Enum') fail('record dependency requires a validated Python factory:' + d.selector);
    d.selector.split(':').forEach(pythonPortableIdentifier);
  }
  const plain = fields.model.declarations.filter(d => d.kind === 'Enum' && d.contract.variants.every(v => v.payload === null));
  const sums = fields.model.declarations.filter(d => d.kind === 'Enum' && d.contract.variants.some(v => v.payload !== null));
  const plainFields = plain.length ? compileSelectedProjectFields(graph, {schema_version: EXACT_PROJECT_FIELD_SELECTION_VERSION, contract_sha256: EXACT_FIELD_CONTRACT_SHA256, graph_sha256: fields.certificate.graph_sha256, roots: plain.map(d => d.selector), bindings: []}, sources.field_contract) : null;
  const plainPlan = plainFields ? planConfiguredPythonEnums(plainFields, {...plainSelection, field_compilation_sha256: plainFields.compilation_sha256}, plainSources) : null;
  const target = (selector: string) => {
    const [feature, node] = selector.split(':') as [string, string];
    return `${root}/features/${snake(feature)}/src/${role}/${snake(node)}${plain.some(d => d.selector === selector) ? '' : '_sum'}.py`;
  };
  const support = `${root}/runtime/values.py`;
  const artifacts = new Map<string, PlannedArtifact>();
  const add = (relative_path: string, content: string) => {
    const prior = artifacts.get(relative_path);if (prior && prior.content !== content) fail('conflicting artifact:' + relative_path);
    artifacts.set(relative_path, {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)});
  };
  for (const a of plainPlan?.artifacts ?? []) add(a.relative_path, a.content);
  const modules = sums.map(d => {
    if (d.kind !== 'Enum') return fail('Enum declaration');
    const [, node] = d.selector.split(':') as [string, string];
    const name = symbol(node), file = target(d.selector), contract = sha256(canonicalJson(d.contract));
    const values = createPythonOwnedValues(d.selector, file, contract, fields.model, target);
    const shape = values.render({kind: 'sum', variants: d.contract.variants}, true);
    const content = values.prelude(support) + `\n\n${name}Case = ${shape.type}\n${name}ValueComponent = ${shape.expression}\n\n\ndef create_${snake(node)}(value: dict[str, object]) -> ${name}Case:\n    return ${name}ValueComponent.normalize(value)\n`;
    add(file, content);
    return {selector: d.selector, relative_path: file, name, callable: 'create_' + snake(node), dependencies: [...values.imports.values()].map(({selector, path}) => ({selector, path})), contract_sha256: contract};
  });
  if (sums.length) add(support, renderPythonValueSupport());
  for (const file of [...artifacts.keys()]) {
    const parts = file.split('/');for (let i = 1; i < parts.length; i++) add(parts.slice(0, i).join('/') + '/__init__.py', '');
  }
  const body = {schema_version: 'domainspec.configured-python-algebraic-enums-plan/v1-candidate', selection: {...selection}, certificate: fields.certificate,
    field_compilation_sha256: fields.compilation_sha256, source_digests: {...PYTHON_ENUM_SOURCE_DIGESTS, field_contract: EXACT_FIELD_CONTRACT_SHA256},
    modules, plain_modules: plainPlan?.modules ?? [], artifacts: [...artifacts.values()].sort((a, b) => a.relative_path < b.relative_path ? -1 : a.relative_path > b.relative_path ? 1 : 0),
    output_effect: 'none', authority_effect: 'none'};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
