import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from './project-model.js';
import {compileFieldReferenceModel, fieldValueKey, FIELD_MODEL_VERSION, FIELD_VALUE_PROFILE, EXACT_FIELD_MODEL_VERSION, EXACT_FIELD_VALUE_PROFILE, type FieldReferenceModel} from './field-reference-model.js';
import {decodeTypedRecordContract, decodeTypedSumContract, type TypedType} from '../typed-operation/contracts.js';
import {createCompiledProjectCertificate, type CompiledProjectCertificateV1} from '../compilation/certificate.js';
import {canonicalJson, sha256} from './source-manifest.js';

// Opt-in candidate integration. Boundaries and open questions: COMPILED-FIELD-REPORT.md
// in development/reconciliation-v1/contracts. No graph-schema or default-generator change.
export const PROJECT_FIELD_SELECTION_VERSION = 'domainspec.project-field-selection/v1-candidate';
export const FIELD_CONTRACT_SHA256 = '9a012a5a669936620e71a6d8e41457b9ef975dd53703c629c26e000ff1d4262d';
export const EXACT_PROJECT_FIELD_SELECTION_VERSION = 'domainspec.project-field-selection/v2-candidate';
export const EXACT_FIELD_CONTRACT_SHA256 = '42b57f2517f6c7dcf24492acb76099def9f75926976df47a7b78d559640ea227';
export interface ProjectFieldSelection {
  readonly schema_version: typeof PROJECT_FIELD_SELECTION_VERSION | typeof EXACT_PROJECT_FIELD_SELECTION_VERSION;
  readonly contract_sha256: typeof FIELD_CONTRACT_SHA256 | typeof EXACT_FIELD_CONTRACT_SHA256;
  readonly graph_sha256: string;
  readonly roots: readonly string[];
  readonly bindings: FieldReferenceModel['bindings'];
}
export interface CompiledProjectFields {
  readonly schema_version: 'domainspec.compiled-project-fields/v1-candidate' | 'domainspec.compiled-project-fields/v2-candidate';
  readonly selection: ProjectFieldSelection;
  readonly certificate: CompiledProjectCertificateV1;
  readonly model: FieldReferenceModel;
  readonly invariant_references: readonly string[];
  readonly unselected_node_selectors: readonly string[];
  readonly invariant_execution: 'not-performed';
  readonly authority_effect: 'none';
  readonly compilation_sha256: string;
}
export class CompiledFieldError extends Error {
  constructor(readonly code: string, readonly pointer: string) {super(`${code}:${pointer}`); this.name = 'CompiledFieldError';}
}
function fail(code: string, pointer: string): never {throw new CompiledFieldError(code, pointer);}
function object(value: unknown, keys: readonly string[], pointer: string): Record<string, unknown> {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) fail('PROJECT_FIELD_SELECTION', pointer);
  if (Object.keys(value).sort().join('|') !== [...keys].sort().join('|')) fail('PROJECT_FIELD_SELECTION', pointer);
  return value as Record<string, unknown>;
}
const selectorPattern = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*:[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const namePattern = /^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$/;
function identifier(value: unknown, pattern: RegExp): string {
  if (typeof value !== 'string' || !pattern.test(value)) fail('PROJECT_FIELD_SELECTION', '/identifier');
  return value;
}
function dependencies(type: TypedType): string[] {
  if (type.kind === 'named' || type.kind === 'reference') return [type.selector];
  if (type.kind === 'scalar') return [];
  if (type.kind === 'sum') return type.variants.flatMap(v => v.payload ? dependencies(v.payload) : []);
  return dependencies(type.element);
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze);Object.freeze(value);}
  return value;
}
const snapshots = new WeakSet<object>();

/** Compile data declarations from one unchanged checked graph; metadata cannot redefine them. */
export function compileSelectedProjectFields(graph: CompiledProjectGraph, selection: unknown, contractSource: string): CompiledProjectFields {
  assertCompiledProjectSnapshot(graph);
  const raw = object(selection, ['schema_version', 'contract_sha256', 'graph_sha256', 'roots', 'bindings'], '/selection');
  const exactValues = raw.schema_version === EXACT_PROJECT_FIELD_SELECTION_VERSION;
  if (!exactValues && raw.schema_version !== PROJECT_FIELD_SELECTION_VERSION) fail('PROJECT_FIELD_VERSION', '/selection/schema_version');
  const contractSha256 = exactValues ? EXACT_FIELD_CONTRACT_SHA256 : FIELD_CONTRACT_SHA256;
  const modelVersion = exactValues ? EXACT_FIELD_MODEL_VERSION : FIELD_MODEL_VERSION;
  const valueProfile = exactValues ? EXACT_FIELD_VALUE_PROFILE : FIELD_VALUE_PROFILE;
  if (typeof contractSource !== 'string' || sha256(contractSource) !== contractSha256 || raw.contract_sha256 !== contractSha256) fail('PROJECT_FIELD_CONTRACT', '/selection/contract_sha256');
  const contract = JSON.parse(contractSource) as {input_schema_version: string; value_profile: string};
  if (contract.input_schema_version !== modelVersion || contract.value_profile !== valueProfile) fail('PROJECT_FIELD_CONTRACT', '/contract');
  const certificate = createCompiledProjectCertificate(graph);
  if (raw.graph_sha256 !== certificate.graph_sha256) fail('PROJECT_FIELD_STALE', '/selection/graph_sha256');
  if (!Array.isArray(raw.roots) || !raw.roots.length || raw.roots.length > 256 || new Set(raw.roots).size !== raw.roots.length) fail('PROJECT_FIELD_ROOTS', '/selection/roots');
  const roots = raw.roots.map(s => identifier(s, selectorPattern)).sort();
  if (!Array.isArray(raw.bindings) || raw.bindings.length > 1024) fail('PROJECT_FIELD_SELECTION', '/selection/bindings');
  // Copy only closed JSON fields before inspecting dependencies; the core model
  // independently checks reference semantics and duplicate bindings.
  const bindings: FieldReferenceModel['bindings'] = raw.bindings.map((entry, i) => {
    const b = object(entry, ['owner', 'field', 'kind', 'target', 'projection'], `/bindings/${i}`);
    if (b.kind !== 'identity-reference' && b.kind !== 'field-projection') fail('PROJECT_FIELD_SELECTION', `/bindings/${i}/kind`);
    if (!Array.isArray(b.projection) || !b.projection.length || b.projection.length > 16) fail('PROJECT_FIELD_SELECTION', `/bindings/${i}/projection`);
    return {owner: identifier(b.owner, selectorPattern), field: identifier(b.field, namePattern), kind: b.kind,
      target: identifier(b.target, selectorPattern), projection: b.projection.map(s => identifier(s, namePattern))};
  });
  const nodes = new Map(graph.nodes.map(n => [n.selector, n]));
  const selected = new Set<string>(), invariants = new Set<string>();
  const declarations: unknown[] = [];
  const queue = [...roots];
  while (queue.length) {
    const selector = queue.shift()!;
    if (selected.has(selector)) continue;
    if (selected.size >= 256) fail('PROJECT_FIELD_LIMIT', '/declarations');
    const node = nodes.get(selector) ?? fail('PROJECT_FIELD_MISSING', selector);
    if (!['Entity', 'Value Object', 'Enum'].includes(node.kind)) fail('PROJECT_FIELD_KIND', selector);
    if (!node.body.typed_contract) fail('PROJECT_FIELD_UNTYPED', selector);
    selected.add(selector);
    const typed = node.kind === 'Enum' ? decodeTypedSumContract(node.body.typed_contract) : decodeTypedRecordContract(node.body.typed_contract);
    const types = typed.schema_version === 'domainspec.typed-record/v1' ? typed.properties.map(p => p.type) : typed.variants.flatMap(v => v.payload ? [v.payload] : []);
    const invariant_refs = node.kind === 'Value Object' ? node.body.invariant_refs : [];
    if (!Array.isArray(invariant_refs)) fail('PROJECT_FIELD_INVARIANT', selector);
    for (const ref of invariant_refs) {
      if (typeof ref !== 'string' || nodes.get(ref)?.kind !== 'Rule') fail('PROJECT_FIELD_INVARIANT', selector);
      invariants.add(ref);
    }
    declarations.push({selector, kind: node.kind, contract: typed, invariant_refs});
    queue.push(...types.flatMap(dependencies).sort(), ...bindings.filter(b => b.owner === selector).map(b => b.target).sort());
  }
  for (const b of bindings) if (!selected.has(b.owner)) fail('PROJECT_FIELD_UNUSED_BINDING', `${b.owner}#${b.field}`);
  const model = compileFieldReferenceModel({schema_version: modelVersion, value_profile: valueProfile, declarations, bindings});
  const normalized: ProjectFieldSelection = {schema_version: exactValues ? EXACT_PROJECT_FIELD_SELECTION_VERSION : PROJECT_FIELD_SELECTION_VERSION, contract_sha256: contractSha256,
    graph_sha256: certificate.graph_sha256, roots, bindings: model.bindings};
  const body = {schema_version: exactValues ? 'domainspec.compiled-project-fields/v2-candidate' as const : 'domainspec.compiled-project-fields/v1-candidate' as const, selection: normalized, certificate: structuredClone(certificate), model,
    invariant_references: [...invariants].sort(), unselected_node_selectors: graph.nodes.map(n => n.selector).filter(s => !selected.has(s)).sort(),
    invariant_execution: 'not-performed' as const, authority_effect: 'none' as const};
  const result = freeze({...body, compilation_sha256: sha256(canonicalJson(body))});
  snapshots.add(result);
  return result;
}

/** Require the immutable, locally checked snapshot, not a structurally similar object. */
export function assertCompiledProjectFields(fields: CompiledProjectFields): void {
  if (!snapshots.has(fields)) fail('PROJECT_FIELD_UNCHECKED', '/fields');
}

/** Evaluate only the selected candidate's structural/value semantics, never its invariants. */
export function compiledFieldValueKey(fields: CompiledProjectFields, selector: string, value: unknown): string {
  assertCompiledProjectFields(fields);
  return fieldValueKey(fields.model, selector, value);
}
