import {assertCompiledProjectSnapshot, type CompiledProjectGraph, type FieldSpec, type InterfaceOperationSpec} from './project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {canonicalJson, sha256} from './source-manifest.js';

export const INTERFACE_MAPPING_SCOPES_DEFINITION_SHA256 = '995555a8db94d8d31c59d096596a8f3c41b698959f7eadb5c6e3336528a53035';
interface Endpoint {
  readonly interface_selector: string;
  readonly operation_id: string;
  readonly operation_ref: string;
  readonly side: 'request' | 'result';
  readonly field: FieldSpec;
  readonly source: Readonly<{relative_path: string; sha256: string; pointer: string}>;
}
const compare = (a: unknown, b: unknown): number => {
  const x = canonicalJson(a), y = canonicalJson(b);
  return x < y ? -1 : x > y ? 1 : 0;
};
function freeze<T>(value: T): T {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
  return value;
}

/** Read-only legacy-field inspection. Does not infer migration or flatten endpoints. */
export function inspectInterfaceMappingScopes(graph: CompiledProjectGraph) {
  assertCompiledProjectSnapshot(graph);
  const certificate = createCompiledProjectCertificate(graph);
  const source = (feature: string, node: string, pointer: string) => {
    const relative_path = `specs/${feature}/nodes/${node}.json`;
    const entry = graph.source_manifest.sources.find(s => s.relative_path === relative_path);
    if (!entry) throw new Error('MTCLI_INTERFACE_MAPPING_SCOPE: missing source evidence');
    return {relative_path, sha256: entry.sha256, pointer};
  };
  const interfaces = new Map<string, Map<string, Endpoint[]>>();
  for (const node of graph.nodes.filter(n => n.kind === 'Interface')) {
    if (node.body.typed_contract !== undefined) throw new Error('MTCLI_INTERFACE_MAPPING_SCOPE: unsupported typed Interface');
    const fields = new Map<string, Endpoint[]>();
    for (const [i, operation] of (node.body.operations as readonly InterfaceOperationSpec[]).entries()) {
      for (const side of ['request', 'result'] as const) {
        for (const [j, field] of operation[side].entries()) {
          const candidates = fields.get(field.field_id) ?? [];
          candidates.push({interface_selector: node.selector, operation_id: operation.operation_id,
            operation_ref: operation.operation_ref, side, field: structuredClone(field),
            source: source(node.feature_id, node.node_id, `/body/operations/${i}/${side}/${j}`)});
          fields.set(field.field_id, candidates);
        }
      }
    }
    fields.forEach(candidates => candidates.sort(compare));
    interfaces.set(node.selector, fields);
  }
  const ambiguities = [...interfaces].flatMap(([interface_selector, fields]) => [...fields]
    .filter(([, candidates]) => candidates.length > 1)
    .map(([field_id, candidates]) => ({interface_selector, field_id, candidates,
      differing_declarations: new Set(candidates.map(c => canonicalJson({type_ref: c.field.type_ref, required: c.field.required}))).size > 1}))).sort(compare);
  const uses: Array<Readonly<{mapping_selector: string; endpoint_role: 'source' | 'target';
    interface_selector: string; field_id: string; candidates: readonly Endpoint[];
    scope: 'resolved' | 'ambiguous'; source: Endpoint['source']}>> = [];
  const uninspected_typed_mappings: string[] = [];
  let legacy_mapping_count = 0;
  for (const node of graph.nodes.filter(n => n.kind === 'Mapping')) {
    if (node.body.typed_contract !== undefined) {uninspected_typed_mappings.push(node.selector); continue;}
    legacy_mapping_count += 1;
    const bindings = node.body.fields as readonly {source_field: string | null; target_field: string}[];
    for (const [i, binding] of bindings.entries()) {
      for (const endpoint_role of ['source', 'target'] as const) {
        const selector = node.body[endpoint_role] as string, fields = interfaces.get(selector);
        const field_id = binding[`${endpoint_role}_field`];
        if (!fields || field_id === null) continue;
        const candidates = fields.get(field_id);
        if (!candidates?.length) throw new Error('MTCLI_INTERFACE_MAPPING_SCOPE: missing checked endpoint field');
        uses.push({mapping_selector: node.selector, endpoint_role, interface_selector: selector, field_id,
          candidates, scope: candidates.length === 1 ? 'resolved' : 'ambiguous',
          source: source(node.feature_id, node.node_id, `/body/fields/${i}/${endpoint_role}_field`)});
      }
    }
  }
  uses.sort(compare);
  const body = {schema_version: 'domainspec.interface-mapping-scopes/v1-candidate' as const,
    definition_sha256: INTERFACE_MAPPING_SCOPES_DEFINITION_SHA256,
    graph_sha256: certificate.graph_sha256, source_manifest_sha256: certificate.source_manifest_sha256,
    interface_count: interfaces.size, legacy_mapping_count,
    endpoint_count: [...interfaces.values()].reduce((n, fields) => n + [...fields.values()].reduce((m, candidates) => m + candidates.length, 0), 0),
    ambiguities, uses, uninspected_typed_mappings: uninspected_typed_mappings.sort(),
    migration_performed: false as const, authority_effect: 'none' as const};
  return freeze({...body, report_sha256: sha256(canonicalJson(body))});
}
