import { RELATIONSHIP_AUTHORITY_SHA256, assertCompiledProjectSnapshot, type CompiledProjectGraph, type CompiledProjectGraphNode } from "../input/project-model.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import type { TypedType } from "../typed-operation/contracts.js";
import { decodePublicMapping, type MappingValueType } from "../typed-backend/mapping-public.js";
import { compileMessagingCompositionV2 } from "./messaging-v2.js";
import { compileExternalApiCompositionV2 } from "./external-api-v2.js";
import { planIntegrationProjectV2, type IntegrationGenerationSourceV2 } from "./generation-v2.js";
import { INTEGRATION_RELATIONSHIP_AUTHORITY_SHA256, integrationRelationshipSignature, type IntegrationNodeKind, type IntegrationRelationshipId } from "./integration-relationship-authority-v1.js";
import {decodeRequestApplicationSourceV1,type RequestApplicationSourceV1} from './request-application-source-v1.js';

export const COMPILED_APPLICATION_GRAPH_VERSION = "domainspec.compiled-application-graph/v1-candidate" as const;

export interface CompiledApplicationGraphNodeV1 {
  readonly node_id: string;
  readonly node_kind: string;
  readonly node_origin: "domain" | "integration";
  readonly source_pointer: string;
  readonly semantic_sha256: string;
}

export interface CompiledApplicationGraphEdgeV1 {
  readonly edge_id: string;
  readonly relationship: string;
  readonly relationship_authority: "domain" | "integration";
  readonly source_node_id: string;
  readonly target_node_id: string;
  readonly source_pointer: string;
}

export interface CompiledRuntimeMappingInputV1 {
  readonly parameter: string;
  readonly value_type: MappingValueType;
  readonly source: Readonly<{
    kind: "direct-value" | "entity-identity" | "event-identity-reference" | "message-body" | "protocol-body" | "operation-result";
    reference: string;
    path: readonly string[];
  }>;
}

export interface CompiledRuntimeMappingBindingV1 {
  readonly binding_id: string;
  readonly binding_kind: "mapping";
  readonly mapping_ref: string;
  readonly direction: "logical-to-message" | "message-to-application" | "application-to-protocol" | "protocol-to-application";
  readonly source_ref: string;
  readonly target_ref: string;
  readonly inputs: readonly CompiledRuntimeMappingInputV1[];
  readonly result_type: MappingValueType;
  readonly total: boolean;
  readonly source_pointer: string;
}

export interface CompiledOperationRequestContractV1 {
  readonly request_ref: string;
  readonly operation_ref: string;
  readonly mapping_binding_refs: readonly string[];
  readonly source_refs: readonly string[];
  readonly bindings: readonly Readonly<{
    mapping_binding_ref: string;
    source_ref: string;
    parameters: readonly Readonly<{
      parameter: string;
      source: Readonly<{ kind: "mapping-result" | "source-body"; path: readonly string[] }>;
    }>[];
  }>[];
}

export interface CompiledApplicationGraphV1 {
  readonly schema_version: typeof COMPILED_APPLICATION_GRAPH_VERSION;
  readonly project_id: string;
  readonly domain_source_manifest_sha256: string;
  readonly integration_source_sha256: string;
  readonly domain_relationship_authority_sha256: string;
  readonly integration_relationship_authority_sha256: string;
  readonly nodes: readonly CompiledApplicationGraphNodeV1[];
  readonly edges: readonly CompiledApplicationGraphEdgeV1[];
  readonly runtime_bindings: readonly CompiledRuntimeMappingBindingV1[];
  readonly operation_requests: readonly CompiledOperationRequestContractV1[];
  readonly runtime_guarantees_observed: false;
  readonly authority_effect: "none";
  readonly graph_sha256: string;
}

export class ApplicationGraphError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(`${code}:${pointer}:${message}`);
    this.name = "ApplicationGraphError";
  }
}

const snapshots = new WeakMap<CompiledApplicationGraphV1, string>();
const fail = (code: string, pointer: string, message: string): never => { throw new ApplicationGraphError(code, pointer, message); };
const freeze = <T>(value: T): T => {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) freeze(child);
  }
  return value;
};

function domainNode(graph: CompiledProjectGraph, selector: string, expectedKind: string, pointer: string): CompiledProjectGraphNode {
  const matches = graph.nodes.filter(node => node.selector === selector);
  if (matches.length !== 1) fail("DS_APPLICATION_GRAPH_ENDPOINT", pointer, `expected one domain endpoint:${selector}`);
  const node = matches[0]!;
  if (node.kind !== expectedKind) fail("DS_APPLICATION_GRAPH_ENDPOINT_KIND", pointer, `expected ${expectedKind}, received ${node.kind}:${selector}`);
  return node;
}

function mappingNamedInputs(node: CompiledProjectGraphNode): readonly string[] {
  const contract = (node.body as Record<string, unknown>).typed_contract as Record<string, unknown> | undefined;
  if (contract?.schema_version === "domainspec.typed-mapping/v1") return Object.freeze([String(contract.source)]);
  if (contract?.schema_version === "domainspec.typed-mapping/v2" || contract?.schema_version === "domainspec.typed-mapping/v3") {
    const inputs = Array.isArray(contract.inputs) ? contract.inputs : [];
    return Object.freeze(inputs.flatMap(input => {
      const type = (input as { readonly type?: { readonly kind?: string; readonly selector?: string } }).type;
      return (type?.kind === "named" || type?.kind === "reference") && typeof type.selector === "string" ? [type.selector] : [];
    }).sort());
  }
  return fail("DS_APPLICATION_GRAPH_MAPPING_CONTRACT", `/domain/nodes/${node.selector}`, `integration Mapping requires a typed contract:${node.selector}`);
}

function runtimeMappingContract(node: CompiledProjectGraphNode, pointer: string): Readonly<{ inputs: readonly Readonly<{ name: string; type: MappingValueType }>[]; result_type: MappingValueType; total: boolean }> {
  const contract = (node.body as Record<string, unknown>).typed_contract as Record<string, unknown> | undefined;
  if (contract?.schema_version === "domainspec.typed-mapping/v3") {
    const publicContract = decodePublicMapping(contract);
    return freeze({ inputs: publicContract.inputs.map(input => ({ name: input.name, type: input.type })), result_type: publicContract.target, total: publicContract.total });
  }
  if (contract?.schema_version !== "domainspec.typed-mapping/v2" || !Array.isArray(contract.inputs) || typeof contract.target !== "string" || typeof contract.total !== "boolean") {
    return fail("DS_APPLICATION_GRAPH_RUNTIME_MAPPING_CONTRACT", pointer, `runtime integration requires a typed Mapping v2 or v3 contract:${node.selector}`);
  }
  const inputs = contract.inputs.map((input, index) => {
    const value = input as { readonly name?: unknown; readonly type?: unknown };
    if (typeof value.name !== "string" || value.type === null || typeof value.type !== "object") fail("DS_APPLICATION_GRAPH_RUNTIME_MAPPING_CONTRACT", `${pointer}/inputs/${index}`, "runtime Mapping input is incomplete");
    const name = value.name as string;
    return freeze({ name, type: structuredClone(value.type) as TypedType });
  });
  return freeze({ inputs: freeze(inputs), result_type: freeze({ kind: "named" as const, selector: contract.target }), total: contract.total });
}

function runtimeInputSource(graph: CompiledProjectGraph, sourceRef: string, input: Readonly<{ name: string; type: MappingValueType }>, sourcePath: readonly string[], pointer: string): CompiledRuntimeMappingInputV1["source"] {
  if (input.type.kind === "named" && input.type.selector === sourceRef) return freeze({ kind: "direct-value" as const, reference: sourceRef, path: freeze([]) });
  if (input.type.kind === "contract" && `${input.type.interface_selector}#${input.type.contract_id}` === sourceRef) return freeze({ kind: "direct-value" as const, reference: sourceRef, path: freeze([]) });
  const sourceNode = graph.nodes.find(node => node.selector === sourceRef);
  const assertIdentityReference = (type: Extract<TypedType,{kind:'reference'}>) => {
    const target=graph.nodes.find(node=>node.selector===type.selector);
    const contract=(target?.body as Record<string,unknown>|undefined)?.typed_contract as {readonly schema_version?:string;readonly properties?:readonly {readonly name?:string;readonly identity?:boolean}[]}|undefined;
    if(target?.kind!=="Entity"||contract?.schema_version!=="domainspec.typed-record/v1"||type.projection.length!==1||!contract.properties?.some(field=>field.name===type.projection[0]&&field.identity))fail("DS_APPLICATION_GRAPH_RUNTIME_MAPPING_SOURCE",pointer,`invalid Entity identity reference:${type.selector}#${type.projection.join('.')}`);
  };
  if(sourceNode?.kind==="Entity"&&input.type.kind==="reference"&&input.type.selector===sourceRef){
    assertIdentityReference(input.type);
    return freeze({kind:"entity-identity" as const,reference:sourceRef,path:freeze([...input.type.projection])});
  }
  if (sourceNode?.kind === "Event" && input.type.kind === "reference") {
    const inputSelector = input.type.selector;
    assertIdentityReference(input.type);
    const payload = (sourceNode.body as Record<string, unknown>).payload;
    const matches = Array.isArray(payload) ? payload.filter(field => {
      const value = field as { readonly field_id?: unknown; readonly type_ref?: { readonly kind?: unknown; readonly selector?: unknown } };
      return value.type_ref?.kind === "reference" && value.type_ref.selector === inputSelector;
    }) : [];
    if (matches.length !== 1) fail("DS_APPLICATION_GRAPH_RUNTIME_MAPPING_SOURCE", pointer, `expected one Event payload source for ${input.name}:${inputSelector}`);
    return freeze({ kind: "event-identity-reference" as const, reference: sourceRef, path: freeze([String((matches[0] as { readonly field_id: string }).field_id)]) });
  }
  if (sourceRef.startsWith("message-type:")) return freeze({ kind: "message-body" as const, reference: sourceRef, path: freeze([...sourcePath]) });
  if ((sourceRef.startsWith("provider-operation:") || sourceRef.startsWith("protocol-operation:")) && (sourceRef.endsWith("#request") || sourceRef.endsWith("#response"))) return freeze({ kind: "protocol-body" as const, reference: sourceRef, path: freeze([...sourcePath]) });
  if (sourceRef.endsWith("#result")) return freeze({ kind: "operation-result" as const, reference: sourceRef, path: freeze([]) });
  return fail("DS_APPLICATION_GRAPH_RUNTIME_MAPPING_SOURCE", pointer, `cannot bind Mapping input ${input.name} from ${sourceRef}`);
}

type RuntimeMappingSource = {
  readonly messaging: Pick<IntegrationGenerationSourceV2["messaging"], "message_mappings">;
  readonly external_api: Pick<IntegrationGenerationSourceV2["external_api"], "api_mappings">;
};

function runtimeMappingBindings(graph: CompiledProjectGraph, source: RuntimeMappingSource): readonly CompiledRuntimeMappingBindingV1[] {
  const rows = [
    ...source.messaging.message_mappings.map((mapping, index) => ({ mapping, pointer: `/messaging/message_mappings/${index}` })),
    ...source.external_api.api_mappings.map((mapping, index) => ({ mapping, pointer: `/external_api/api_mappings/${index}` })),
  ].map(({ mapping, pointer }) => {
    const node = domainNode(graph, mapping.mapper_ref, "Mapping", `${pointer}/mapper_ref`);
    const contract = runtimeMappingContract(node, `${pointer}/mapper_ref`);
    if (mapping.total !== contract.total) fail("DS_APPLICATION_GRAPH_MAPPING_TOTALITY", `${pointer}/total`, "integration totality differs from its typed Mapping");
    const declaredPaths = mapping.input_paths ?? [];
    const operationRequest = (mapping.direction === "message-to-application" || mapping.direction === "protocol-to-application") && mapping.target_ref.endsWith("#request");
    if (operationRequest) {
      const expected = contract.inputs.map(input => input.name).sort();
      const actual = declaredPaths.map(input => input.parameter).sort();
      if (canonicalJson(actual) !== canonicalJson(expected)) fail("DS_APPLICATION_GRAPH_REQUEST_MAPPING_INPUT", `${pointer}/input_paths`, "request Mapping input paths must cover its exact parameters");
    } else if (declaredPaths.length) fail("DS_APPLICATION_GRAPH_REQUEST_MAPPING_INPUT", `${pointer}/input_paths`, "input paths are only valid for Operation Request mappings");
    const inputs = contract.inputs.map((input, index) => freeze({ parameter: input.name, value_type: input.type, source: runtimeInputSource(graph, mapping.source_ref, input, declaredPaths.find(row => row.parameter === input.name)?.path ?? [], `${pointer}/source_ref/inputs/${index}`) }));
    return freeze({ binding_id: mapping.mapping_id, binding_kind: "mapping" as const, mapping_ref: mapping.mapper_ref, direction: mapping.direction, source_ref: mapping.source_ref, target_ref: mapping.target_ref, inputs: freeze(inputs), result_type: contract.result_type, total: contract.total, source_pointer: pointer });
  }).sort((left, right) => left.binding_id.localeCompare(right.binding_id));
  assertUnique(rows.map(row => row.binding_id), "DS_APPLICATION_GRAPH_RUNTIME_BINDING_DUPLICATE", "/runtime_bindings");
  return freeze(rows);
}

function operationRequestContracts(graph: CompiledProjectGraph, source: RuntimeMappingSource, bindings: readonly CompiledRuntimeMappingBindingV1[]): readonly CompiledOperationRequestContractV1[] {
  const groups = new Map<string, CompiledRuntimeMappingBindingV1[]>();
  for (const binding of bindings.filter(row => (row.direction === "message-to-application" || row.direction === "protocol-to-application") && row.target_ref.endsWith("#request"))) {
    const rows = groups.get(binding.target_ref) ?? [];
    rows.push(binding);
    groups.set(binding.target_ref, rows);
  }
  return freeze([...groups].sort(([left], [right]) => left.localeCompare(right)).map(([requestRef, rows]) => {
    const operationRef = requestRef.slice(0, -"#request".length);
    domainNode(graph, operationRef, "Operation", `/runtime_bindings/${rows[0]!.binding_id}/target_ref`);
    return freeze({
      request_ref: requestRef,
      operation_ref: operationRef,
      mapping_binding_refs: freeze(rows.map(row => row.binding_id).sort()),
      source_refs: freeze([...new Set(rows.map(row => row.source_ref))].sort()),
      bindings: freeze(rows.map(row => {
        const authored = [
          ...source.messaging.message_mappings,
          ...source.external_api.api_mappings,
        ].find(mapping => mapping.mapping_id === row.binding_id) ?? fail("DS_APPLICATION_GRAPH_REQUEST_COMPOSITION", row.source_pointer, "Operation Request mapping is missing");
        const parameters = authored.request_parameters ?? fail("DS_APPLICATION_GRAPH_REQUEST_COMPOSITION", row.source_pointer, "Operation Request parameters are missing");
        return freeze({ mapping_binding_ref: row.binding_id, source_ref: row.source_ref, parameters: freeze(structuredClone(parameters)) });
      }).sort((left, right) => left.mapping_binding_ref.localeCompare(right.mapping_binding_ref))),
    });
  }));
}

function eventPayloadReferences(node: CompiledProjectGraphNode): readonly string[] {
  const payload = (node.body as Record<string, unknown>).payload;
  if (!Array.isArray(payload)) return Object.freeze([]);
  return Object.freeze(payload.flatMap(field => {
    const type = (field as { readonly type_ref?: { readonly kind?: string; readonly selector?: string } }).type_ref;
    return type?.kind === "reference" && typeof type.selector === "string" ? [type.selector] : [];
  }).sort());
}

function integrationNode(nodeId: string, nodeKind: IntegrationNodeKind, sourcePointer: string, semantic: unknown): CompiledApplicationGraphNodeV1 {
  return freeze({ node_id: nodeId, node_kind: nodeKind, node_origin: "integration" as const, source_pointer: sourcePointer, semantic_sha256: sha256(canonicalJson(semantic)) });
}

function integrationEdge(edgeId: string, relationship: IntegrationRelationshipId, sourceNodeId: string, targetNodeId: string, sourcePointer: string): CompiledApplicationGraphEdgeV1 {
  const signature = integrationRelationshipSignature(relationship)!;
  if (!signature) fail("DS_APPLICATION_GRAPH_RELATIONSHIP", sourcePointer, `unknown integration relationship:${relationship}`);
  return freeze({ edge_id: edgeId, relationship, relationship_authority: "integration" as const, source_node_id: sourceNodeId, target_node_id: targetNodeId, source_pointer: sourcePointer });
}

function assertUnique(values: readonly string[], code: string, pointer: string): void {
  if (new Set(values).size !== values.length) fail(code, pointer, "duplicate canonical identity");
}

export function assertCompiledApplicationGraph(value: unknown): asserts value is CompiledApplicationGraphV1 {
  if (value === null || typeof value !== "object" || snapshots.get(value as CompiledApplicationGraphV1) !== sha256(canonicalJson(value))) {
    fail("DS_APPLICATION_GRAPH_SNAPSHOT", "/application_graph", "graph was not compiled by the current process or has changed");
  }
}

/** Bounded messaging join using the same runtime rules as the whole application.
 * This is not a complete application graph or evidence of transport execution. */
export function compileMessagingRuntimeBindingsV1(graph: CompiledProjectGraph, input: unknown) {
  assertCompiledProjectSnapshot(graph);
  const authored = structuredClone(input) as IntegrationGenerationSourceV2["messaging"];
  const messaging = compileMessagingCompositionV2(authored);
  // Preserve authored array locations: normalized composition order is not a source pointer.
  const source: RuntimeMappingSource = { messaging: authored, external_api: { api_mappings: [] } };
  const runtime_bindings = runtimeMappingBindings(graph, source);
  const operation_requests = operationRequestContracts(graph, source, runtime_bindings);
  const body = { schema_version: "domainspec.messaging-runtime-bindings/v1-candidate", domain_source_manifest_sha256: graph.source_manifest.manifest_sha256,
    messaging_source_sha256: sha256(canonicalJson(authored)), messaging_composition_digest: messaging.composition_digest, runtime_bindings, operation_requests, runtime_delivery_observed: false, authority_effect: "none" };
  return freeze({ ...body, binding_sha256: sha256(canonicalJson(body)) });
}

/** Shares the whole-application Mapping rules without implying an HTTP call/listener. */
export function compileExternalApiRuntimeBindingsV1(graph: CompiledProjectGraph, input: unknown) {
  assertCompiledProjectSnapshot(graph);
  const authored = structuredClone(input) as IntegrationGenerationSourceV2["external_api"];
  const externalApi = compileExternalApiCompositionV2(authored);
  const source: RuntimeMappingSource = { messaging: { message_mappings: [] }, external_api: authored };
  const runtime_bindings = runtimeMappingBindings(graph, source);
  const operation_requests = operationRequestContracts(graph, source, runtime_bindings);
  const body = { schema_version: "domainspec.external-api-runtime-bindings/v1-candidate", domain_source_manifest_sha256: graph.source_manifest.manifest_sha256,
    external_api_source_sha256: sha256(canonicalJson(authored)), external_api_composition_digest: externalApi.composition_digest, runtime_bindings, operation_requests, runtime_calls_observed: false, authority_effect: "none" };
  return freeze({ ...body, binding_sha256: sha256(canonicalJson(body)) });
}

export function compileApplicationGraphV1(graph: CompiledProjectGraph, source: IntegrationGenerationSourceV2): CompiledApplicationGraphV1 {
  assertCompiledProjectSnapshot(graph);
  planIntegrationProjectV2(source, "typescript");
  const nodes: CompiledApplicationGraphNodeV1[] = graph.nodes.map(node => freeze({
    node_id: node.selector,
    node_kind: node.kind,
    node_origin: "domain" as const,
    source_pointer: `/domain/nodes/${node.selector}`,
    semantic_sha256: sha256(canonicalJson({ kind: node.kind, body: node.body })),
  }));
  const edges: CompiledApplicationGraphEdgeV1[] = graph.relationships.map(edge => freeze({
    edge_id: `domain:${edge.scope}:${edge.source.feature_id}:${edge.edge_id}`,
    relationship: edge.relationship,
    relationship_authority: "domain" as const,
    source_node_id: `${edge.source.feature_id}:${edge.source.node_id}`,
    target_node_id: `${edge.target.feature_id}:${edge.target.node_id}`,
    source_pointer: `/domain/relationships/${edge.scope}/${edge.source.feature_id}/${edge.edge_id}`,
  }));
  const runtimeBindings = runtimeMappingBindings(graph, source);
  const operationRequests = operationRequestContracts(graph, source, runtimeBindings);

  const messageTypes = new Map(source.messaging.message_types.map((message, index) => {
    const nodeId = `message-contract:${message.message_type_id}`;
    nodes.push(integrationNode(nodeId, "message-contract", `/messaging/message_types/${index}`, message));
    return [message.message_type_id, { nodeId, message, index }] as const;
  }));

  for (const [index, mapping] of source.messaging.message_mappings.entries()) {
    if (mapping.direction !== "logical-to-message") continue;
    const mapper = domainNode(graph, mapping.mapper_ref, "Mapping", `/messaging/message_mappings/${index}/mapper_ref`);
    const event = domainNode(graph, mapping.source_ref, "Event", `/messaging/message_mappings/${index}/source_ref`);
    const message = messageTypes.get(mapping.target_ref);
    if (!message) fail("DS_APPLICATION_GRAPH_MESSAGE_TARGET", `/messaging/message_mappings/${index}/target_ref`, `message contract is unresolved:${mapping.target_ref}`);
    const payloadReferences = eventPayloadReferences(event);
    if (!mappingNamedInputs(mapper).some(selector => payloadReferences.includes(selector))) fail("DS_APPLICATION_GRAPH_MAPPING_INPUT", `/messaging/message_mappings/${index}/source_ref`, `Mapping inputs do not agree with Event payload:${mapping.source_ref}`);
    edges.push(integrationEdge(`integration:message-mapping:${mapping.mapping_id}:input`, "reads-payload-from", mapping.mapper_ref, mapping.source_ref, `/messaging/message_mappings/${index}`));
    edges.push(integrationEdge(`integration:message-mapping:${mapping.mapping_id}:output`, "produces-message-contract", mapping.mapper_ref, message!.nodeId, `/messaging/message_mappings/${index}`));
  }

  for (const [index, publication] of source.messaging.publication_bindings.entries()) {
    const nodeId = `publication:${publication.binding_id}`;
    nodes.push(integrationNode(nodeId, "publication", `/messaging/publication_bindings/${index}`, publication));
    domainNode(graph, publication.logical_source_ref, "Event", `/messaging/publication_bindings/${index}/logical_source_ref`);
    const message = messageTypes.get(publication.message_type_ref);
    if (!message || message.message.logical_payload_ref !== publication.logical_source_ref) fail("DS_APPLICATION_GRAPH_PUBLICATION_MESSAGE", `/messaging/publication_bindings/${index}/message_type_ref`, "Publication Event and Message Contract payload disagree");
    const outbound = source.messaging.message_mappings.find(mapping => mapping.mapper_ref === publication.mapper_ref && mapping.direction === "logical-to-message");
    if (!outbound || outbound.source_ref !== publication.logical_source_ref || outbound.target_ref !== publication.message_type_ref) fail("DS_APPLICATION_GRAPH_PUBLICATION_MAPPING", `/messaging/publication_bindings/${index}/mapper_ref`, "Publication, Mapping, Event, and Message Contract do not close");
    edges.push(integrationEdge(`integration:publication:${publication.binding_id}:event`, "publishes-event", nodeId, publication.logical_source_ref, `/messaging/publication_bindings/${index}`));
  }

  for (const [index, endpoint] of source.external_api.inbound_endpoint_bindings.entries()) {
    const endpointNodeId = `inbound-endpoint:${endpoint.binding_id}`;
    const requestNodeId = `request-contract:${endpoint.binding_id}`;
    const requestMapping = source.external_api.api_mappings.find(mapping => mapping.mapper_ref === endpoint.request_mapper_ref && mapping.direction === "protocol-to-application");
    const responseMapping = source.external_api.api_mappings.find(mapping => mapping.mapper_ref === endpoint.response_mapper_ref && mapping.direction === "application-to-protocol");
    if (!requestMapping || requestMapping.source_ref !== `${endpoint.protocol_operation_ref}#request` || requestMapping.target_ref !== `${endpoint.operation_ref}#request`) fail("DS_APPLICATION_GRAPH_REQUEST_MAPPING", `/external_api/inbound_endpoint_bindings/${index}/request_mapper_ref`, "Inbound endpoint request Mapping does not close");
    if (!responseMapping || responseMapping.source_ref !== `${endpoint.operation_ref}#result` || responseMapping.target_ref !== `${endpoint.protocol_operation_ref}#response`) fail("DS_APPLICATION_GRAPH_RESPONSE_MAPPING", `/external_api/inbound_endpoint_bindings/${index}/response_mapper_ref`, "Inbound endpoint response Mapping does not close");
    domainNode(graph, endpoint.request_mapper_ref, "Mapping", `/external_api/inbound_endpoint_bindings/${index}/request_mapper_ref`);
    domainNode(graph, endpoint.response_mapper_ref, "Mapping", `/external_api/inbound_endpoint_bindings/${index}/response_mapper_ref`);
    domainNode(graph, endpoint.operation_ref, "Operation", `/external_api/inbound_endpoint_bindings/${index}/operation_ref`);
    nodes.push(integrationNode(endpointNodeId, "inbound-endpoint", `/external_api/inbound_endpoint_bindings/${index}`, endpoint));
    nodes.push(integrationNode(requestNodeId, "request-contract", `/external_api/api_mappings/${source.external_api.api_mappings.indexOf(requestMapping!)}`, requestMapping!));
    edges.push(integrationEdge(`integration:inbound-endpoint:${endpoint.binding_id}:operation`, "invokes", endpointNodeId, endpoint.operation_ref, `/external_api/inbound_endpoint_bindings/${index}`));
    edges.push(integrationEdge(`integration:inbound-endpoint:${endpoint.binding_id}:request`, "accepts-request", endpoint.operation_ref, requestNodeId, `/external_api/inbound_endpoint_bindings/${index}`));
  }

  nodes.sort((left, right) => left.node_id.localeCompare(right.node_id));
  edges.sort((left, right) => left.edge_id.localeCompare(right.edge_id));
  assertUnique(nodes.map(node => node.node_id), "DS_APPLICATION_GRAPH_NODE_DUPLICATE", "/nodes");
  assertUnique(edges.map(edge => edge.edge_id), "DS_APPLICATION_GRAPH_EDGE_DUPLICATE", "/edges");
  const nodeKinds = new Map(nodes.map(node => [node.node_id, node.node_kind]));
  for (const edge of edges.filter(edge => edge.relationship_authority === "integration")) {
    const signature = integrationRelationshipSignature(edge.relationship)!;
    if (!signature.source_types.includes(nodeKinds.get(edge.source_node_id) ?? "") || !signature.target_types.includes(nodeKinds.get(edge.target_node_id) ?? "")) fail("DS_APPLICATION_GRAPH_ENDPOINT_KIND", edge.source_pointer, `relationship endpoints violate ${edge.relationship}`);
  }
  const body = freeze({
    schema_version: COMPILED_APPLICATION_GRAPH_VERSION,
    project_id: graph.project_id,
    domain_source_manifest_sha256: graph.source_manifest.manifest_sha256,
    integration_source_sha256: sha256(canonicalJson(source)),
    domain_relationship_authority_sha256: RELATIONSHIP_AUTHORITY_SHA256,
    integration_relationship_authority_sha256: INTEGRATION_RELATIONSHIP_AUTHORITY_SHA256,
    nodes: freeze(nodes),
    edges: freeze(edges),
    runtime_bindings: runtimeBindings,
    operation_requests: operationRequests,
    runtime_guarantees_observed: false as const,
    authority_effect: "none" as const,
  });
  const result = freeze({ ...body, graph_sha256: sha256(canonicalJson(body)) });
  snapshots.set(result, sha256(canonicalJson(result)));
  return result;
}

/** Distinct request carrier owned here; never a legacy whole-graph certificate.
 * It retains the same domain and integration relationship signatures. */
export interface CompiledRequestApplicationGraphV1 extends Omit<CompiledApplicationGraphV1,'schema_version'|'integration_source_sha256'> {
 readonly schema_version:'domainspec.compiled-request-application-graph/v1-candidate';
 readonly request_source_sha256:string;
}
const requestSnapshots=new WeakMap<object,{digest:string;domain:CompiledProjectGraph}>();
export function assertCompiledRequestApplicationGraphV1(value:unknown):asserts value is CompiledRequestApplicationGraphV1 {
 const state=value&&typeof value==='object'?requestSnapshots.get(value):undefined;
 if(!state||state.digest!==sha256(canonicalJson(value)))return fail('DS_REQUEST_APPLICATION_GRAPH_SNAPSHOT','/application_graph','use the registered request constructor');
 assertCompiledProjectSnapshot(state.domain);
}
export function compileRequestApplicationGraphV1(graph:CompiledProjectGraph,input:RequestApplicationSourceV1):CompiledRequestApplicationGraphV1 {
 assertCompiledProjectSnapshot(graph);const source=decodeRequestApplicationSourceV1(input);
 const nodes:CompiledApplicationGraphNodeV1[]=graph.nodes.map(node=>freeze({node_id:node.selector,node_kind:node.kind,node_origin:'domain' as const,source_pointer:`/domain/nodes/${node.selector}`,semantic_sha256:sha256(canonicalJson({kind:node.kind,body:node.body}))}));
 const edges:CompiledApplicationGraphEdgeV1[]=graph.relationships.map(edge=>freeze({edge_id:`domain:${edge.scope}:${edge.source.feature_id}:${edge.edge_id}`,relationship:edge.relationship,relationship_authority:'domain' as const,source_node_id:`${edge.source.feature_id}:${edge.source.node_id}`,target_node_id:`${edge.target.feature_id}:${edge.target.node_id}`,source_pointer:`/domain/relationships/${edge.scope}/${edge.source.feature_id}/${edge.edge_id}`}));
 const runtime_bindings:CompiledRuntimeMappingBindingV1[]=[],groups=new Map<string,CompiledRuntimeMappingBindingV1[]>();
 for(const [index,entry]of source.entries.entries()){
  const at='/entries/'+index,mapper=domainNode(graph,entry.mapping_ref,'Mapping',at+'/mapping_ref');domainNode(graph,entry.operation_ref,'Operation',at+'/operation_ref');
  const contract=runtimeMappingContract(mapper,at+'/mapping_ref');
  if(!contract.total)fail('DS_REQUEST_APPLICATION_MAPPING_TOTALITY',at,'request requires a total Mapping');
  if(canonicalJson(contract.inputs.map(i=>i.name).sort())!==canonicalJson(entry.mapping_arguments.map(i=>i.parameter).sort()))fail('DS_REQUEST_APPLICATION_MAPPING_ARGUMENTS',at,'exact Mapping input coverage required');
  const binding_id=`request-mapping:${source.source_id}:${entry.id}`,source_ref=`protocol-operation:${source.source_id}:${entry.id}#request`,request_ref=entry.operation_ref+'#request';
  const binding=freeze({binding_id,binding_kind:'mapping' as const,mapping_ref:entry.mapping_ref,direction:'protocol-to-application' as const,source_ref,target_ref:request_ref,inputs:contract.inputs.map(i=>freeze({parameter:i.name,value_type:i.type,source:{kind:'protocol-body' as const,reference:source_ref,path:[...entry.mapping_arguments.find(arg=>arg.parameter===i.name)!.path]}})),result_type:contract.result_type,total:true,source_pointer:at});
  runtime_bindings.push(binding);const rows=groups.get(request_ref)??[];rows.push(binding);groups.set(request_ref,rows);
  const endpointId=`inbound-endpoint:${source.source_id}:${entry.id}`;
  nodes.push(integrationNode(endpointId,'inbound-endpoint',at,entry));
  edges.push(integrationEdge(`integration:${source.source_id}:${entry.id}:invokes`,'invokes',endpointId,entry.operation_ref,at));
 }
 const operation_requests:CompiledOperationRequestContractV1[]=[...groups].sort(([a],[b])=>a.localeCompare(b)).map(([request_ref,rows])=>{
  const operation_ref=request_ref.slice(0,-'#request'.length),requestId=`request-contract:${source.source_id}:${operation_ref}`;
  nodes.push(integrationNode(requestId,'request-contract',rows[0]!.source_pointer,{request_ref,bindings:rows.map(r=>r.binding_id)}));
  edges.push(integrationEdge(`integration:${source.source_id}:${operation_ref}:accepts`,'accepts-request',operation_ref,requestId,rows[0]!.source_pointer));
  return freeze({request_ref,operation_ref,mapping_binding_refs:rows.map(r=>r.binding_id).sort(),source_refs:rows.map(r=>r.source_ref).sort(),bindings:rows.map(row=>{
   const entry=source.entries[Number(row.source_pointer.split('/').at(-1))]!;
   return {mapping_binding_ref:row.binding_id,source_ref:row.source_ref,parameters:[{parameter:entry.request_parameter,source:{kind:'mapping-result' as const,path:[]}}]};
  }).sort((a,b)=>a.mapping_binding_ref.localeCompare(b.mapping_binding_ref))});
 });
 nodes.sort((a,b)=>a.node_id.localeCompare(b.node_id));edges.sort((a,b)=>a.edge_id.localeCompare(b.edge_id));runtime_bindings.sort((a,b)=>a.binding_id.localeCompare(b.binding_id));
 assertUnique(nodes.map(n=>n.node_id),'DS_APPLICATION_GRAPH_NODE_DUPLICATE','/nodes');assertUnique(edges.map(e=>e.edge_id),'DS_APPLICATION_GRAPH_EDGE_DUPLICATE','/edges');assertUnique(runtime_bindings.map(r=>r.binding_id),'DS_APPLICATION_GRAPH_RUNTIME_BINDING_DUPLICATE','/runtime_bindings');
 const kinds=new Map(nodes.map(n=>[n.node_id,n.node_kind]));
 for(const edge of edges){if(!kinds.has(edge.source_node_id)||!kinds.has(edge.target_node_id))fail('DS_REQUEST_APPLICATION_EDGE',edge.source_pointer,'unresolved graph endpoint');if(edge.relationship_authority==='integration'){const signature=integrationRelationshipSignature(edge.relationship)!;if(!signature.source_types.includes(kinds.get(edge.source_node_id)!)||!signature.target_types.includes(kinds.get(edge.target_node_id)!))fail('DS_APPLICATION_GRAPH_ENDPOINT_KIND',edge.source_pointer,'relationship signature differs');}}
 const body={schema_version:'domainspec.compiled-request-application-graph/v1-candidate' as const,project_id:graph.project_id,domain_source_manifest_sha256:graph.source_manifest.manifest_sha256,request_source_sha256:sha256(canonicalJson(source)),domain_relationship_authority_sha256:RELATIONSHIP_AUTHORITY_SHA256,integration_relationship_authority_sha256:INTEGRATION_RELATIONSHIP_AUTHORITY_SHA256,nodes,edges,runtime_bindings,operation_requests,runtime_guarantees_observed:false as const,authority_effect:'none' as const};
 const result=freeze({...body,graph_sha256:sha256(canonicalJson(body))});requestSnapshots.set(result,{domain:graph,digest:sha256(canonicalJson(result))});return result;
}
