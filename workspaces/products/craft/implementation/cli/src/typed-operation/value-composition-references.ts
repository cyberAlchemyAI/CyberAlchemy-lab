import { assertCompiledProjectSnapshot, type CompiledProjectGraph } from '../input/project-model.js';
import { assertCompiledCompositionBoundary, type CompiledCompositionBoundary } from '../input/composition-boundary.js';
import { assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields } from '../input/compiled-field-model.js';
import { createCompiledProjectCertificate } from '../compilation/certificate.js';
import { canonicalJson, sha256 } from '../input/source-manifest.js';
import { decodeTypedQueryContract, queryReturnsOptional } from '../typed-backend/contracts.js';
import { decodeTypedInputMappingContract } from '../typed-backend/mapping-inputs.js';
import { decodePublicMapping } from '../typed-backend/mapping-public.js';
import { decodeOperationActionBindings } from './action-bindings.js';
import { decodeOperationValueComposition } from './value-composition.js';
import type { ValueExpression } from './contracts.js';

export const OPERATION_VALUE_COMPOSITION_CONTRACT_SHA256 = 'b66f8dda9f9a699be28eceeb9081779d4eb6cf54abdd4f7507d323302faa36d3';
const fail = (message: string): never => { throw new TypeError('OPERATION_VALUE_REFERENCES:' + message); };
const freeze = <T>(value: T): T => {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
};
const roots = (value: ValueExpression): readonly string[] => value.op === 'path' ? [value.root] : value.op === 'to_set' ? roots(value.value) : [];
const sameSet = (a: readonly string[], b: readonly string[], reason: string): void => {
  if (canonicalJson([...new Set(a)].sort()) !== canonicalJson([...new Set(b)].sort())) fail(reason);
};
const snapshots = new WeakSet<object>();
export type ReferencedOperationValueComposition = ReturnType<typeof compileOperationValueReferences>;
export function assertReferencedOperationValueComposition(value: unknown): asserts value is ReferencedOperationValueComposition {
  if (!value || typeof value !== 'object' || !snapshots.has(value)) fail('unvalidated reference snapshot');
}

/** Reference/coverage stage only. This is not a checked executable action:
 * argument types, partial projections and all effect bindings still need checking.
 */
export function compileOperationValueReferences(
  graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields,
  value: unknown, actionValue: unknown, contractSource: string,
) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); assertCompiledProjectFields(fields);
  if (typeof contractSource !== 'string' || sha256(contractSource) !== OPERATION_VALUE_COMPOSITION_CONTRACT_SHA256) fail('contract drift');
  const certificate = createCompiledProjectCertificate(graph);
  if (boundary.certificate.graph_sha256 !== certificate.graph_sha256 || fields.certificate.graph_sha256 !== certificate.graph_sha256) fail('cross-graph evidence');
  if (fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('exact field profile required');
  const composition = decodeOperationValueComposition(value), action = decodeOperationActionBindings(actionValue);
  if (composition.operation_ref !== action.selector) fail('operation/action mismatch');
  const node = (selector: string, kind?: string) => {
    const result = graph.nodes.find(n => n.selector === selector);
    if (!result || kind && result.kind !== kind || !boundary.domain_graph.nodes.some(n => n.selector === selector)) return fail('missing or wrong-role declaration:' + selector);
    return result;
  };
  const operation = node(composition.operation_ref, 'Operation');
  if (operation.body.typed_contract !== undefined) fail('legacy typed Operation is separate');
  const evidence = (selector: string) => {
    const n = node(selector);
    return { selector, kind: n.kind, body_sha256: sha256(canonicalJson(n.body)) };
  };
  const outgoing = (selector: string, relationship: string) => graph.relationships
    .filter(r => r.relationship === relationship && r.source.feature_id + ':' + r.source.node_id === selector)
    .map(r => r.target.feature_id + ':' + r.target.node_id);
  const entity = (selector: string): void => {
    node(selector, 'Entity');
    if (!fields.model.declarations.some(d => d.selector === selector && d.kind === 'Entity')) fail('missing Entity field declaration:' + selector);
  };
  const names = [...action.inputs.map(p => p.name), ...action.reads.map(r => r.parameter), ...action.events.map(e => e.parameter), ...composition.bindings.map(b => b.name)];
  if (new Set(names).size !== names.length) fail('value root collision');
  // Event inputs are opaque construction inputs, not Query/Mapping values.
  const valueRoots = new Set([...action.inputs.map(p => p.name), ...action.reads.map(r => r.parameter), ...composition.bindings.map(b => b.name)]);
  const slots = new Map<string, { target: string; mode: 'entity' | 'collection' }>();
  const register = (slot: string, target: string, mode: 'entity' | 'collection') => {
    entity(target);
    const prior = slots.get(slot);
    if (prior && (prior.target !== target || prior.mode !== mode)) fail('source slot ownership conflict:' + slot);
    slots.set(slot, { target, mode });
  };
  action.reads.forEach(r => register(r.slot, r.target, 'entity'));
  const connections = composition.bindings.map(binding => {
    const n = node(binding.selector, binding.kind === 'query' ? 'Query' : 'Mapping');
    for (const argument of binding.arguments) for (const root of roots(argument.value)) if (!valueRoots.has(root)) fail('unknown or opaque value root:' + root);
    if (binding.kind === 'query') {
      const contract = decodeTypedQueryContract(n.body.typed_contract);
      sameSet(binding.arguments.map(a => a.parameter), contract.inputs.map(p => p.name), 'Query argument coverage');
      if (binding.absence === 'require-present' && !queryReturnsOptional(contract)) fail('require-present needs optional Query');
      sameSet(outgoing(binding.selector, 'reads'), [contract.source], 'Query source relationship mismatch');
      register(binding.source_slot, contract.source, 'collection');
      return { binding, contract, source: evidence(binding.selector), contract_sha256: sha256(canonicalJson(contract)), query_source: evidence(contract.source) };
    }
    const raw = n.body.typed_contract as { schema_version?: unknown } | undefined;
    // Legacy Mapping v1 has no named-input contract; do not invent one here.
    const contract = raw?.schema_version === 'domainspec.typed-mapping/v2' ? decodeTypedInputMappingContract(raw)
      : raw?.schema_version === 'domainspec.typed-mapping/v3' ? decodePublicMapping(raw) : fail('named-input Mapping contract required');
    sameSet(binding.arguments.map(a => a.parameter), contract.inputs.map(p => p.name), 'Mapping argument coverage');
    const target = typeof contract.target === 'string' ? contract.target : contract.target.kind === 'named' ? contract.target.selector : contract.target.interface_selector;
    node(target);
    sameSet(outgoing(binding.selector, 'maps'), [target], 'Mapping target relationship mismatch');
    return { binding, contract, source: evidence(binding.selector), contract_sha256: sha256(canonicalJson(contract)), mapping_target: evidence(target) };
  });
  const declared = operation.body.reads;
  if (!Array.isArray(declared) || declared.some(s => typeof s !== 'string') || new Set(declared).size !== declared.length) fail('invalid Operation read slots');
  sameSet(declared as string[], [...slots.keys()], 'Operation read slot coverage');
  sameSet(outgoing(operation.selector, 'reads'), [...slots.values()].map(s => s.target), 'Operation read relationship coverage');
  const body = {
    schema_version: 'domainspec.operation-value-references/v1-candidate' as const,
    composition, action, contract_sha256: OPERATION_VALUE_COMPOSITION_CONTRACT_SHA256,
    certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256,
    operation: evidence(operation.selector), connections,
    source_slots: [...slots.entries()].sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([slot, ownership]) => ({ slot, ...ownership })),
    validation_stage: 'references-only' as const, execution: 'not-performed' as const, authority_effect: 'none' as const,
  };
  const result = freeze({ ...body, references_sha256: sha256(canonicalJson(body)) }); snapshots.add(result); return result;
}
