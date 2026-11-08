import { assertCompiledProjectSnapshot, type CompiledProjectGraph, type CompiledProjectGraphNode } from "../input/project-model.js";
import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { compileApplicationGraphV1, type CompiledApplicationGraphV1 } from "./application-graph-v1.js";
import { planIntegrationProjectV2, type IntegrationGenerationSourceV2 } from "./generation-v2.js";
import type { PersistenceShape } from "./persistence-v2-types.js";
import {compileRequestApplicationGraphV1,assertCompiledRequestApplicationGraphV1,type CompiledRequestApplicationGraphV1} from './application-graph-v1.js';
import {decodeRequestApplicationSourceV1,freezeRequestApplication,requestApplicationFail,type RequestApplicationSourceV1} from './request-application-source-v1.js';
import {assertSelectedReconciledProject,selectedReconciledIdentity,type SelectedReconciledProject} from '../generation/selected-reconciled-project.js';

export const APPLICATION_INTEGRATION_BINDING_VERSION = "domainspec.application-integration-binding/v1-candidate" as const;

export type ApplicationReferenceKind =
  | "data"
  | "public-contract"
  | "field"
  | "interface"
  | "operation"
  | "event"
  | "mapping"
  | "failure";

export const APPLICATION_REFERENCE_KIND_MATRIX: Readonly<Record<ApplicationReferenceKind, readonly string[]>> = Object.freeze({
  data: Object.freeze(["Entity", "Value Object", "Enum", "Sum"]),
  "public-contract": Object.freeze(["Interface"]),
  field: Object.freeze(["Entity", "Value Object"]),
  interface: Object.freeze(["Interface"]),
  operation: Object.freeze(["Operation"]),
  event: Object.freeze(["Event"]),
  mapping: Object.freeze(["Mapping"]),
  failure: Object.freeze(["Operation"]),
});

export interface ApplicationIntegrationReferenceV1 {
  readonly pointer: string;
  readonly reference: string;
  readonly selector: string;
  readonly fragment: string | null;
  readonly reference_kind: ApplicationReferenceKind;
  readonly expected_node_kinds: readonly string[];
  readonly actual_node_kind: string;
}

export interface ApplicationIntegrationBindingV1 {
  readonly schema_version: typeof APPLICATION_INTEGRATION_BINDING_VERSION;
  readonly project_id: string;
  readonly domain_source_manifest_sha256: string;
  readonly integration_source_id: string;
  readonly integration_source_sha256: string;
  readonly integration_semantic_manifest_sha256: string;
  readonly application_graph: CompiledApplicationGraphV1;
  readonly references: readonly ApplicationIntegrationReferenceV1[];
  readonly reference_kind_matrix: typeof APPLICATION_REFERENCE_KIND_MATRIX;
  readonly runtime_guarantees_observed: false;
  readonly claim_ceiling: "formation-and-static-compilation-only";
  readonly authority_effect: "none";
  readonly binding_sha256: string;
}

export class ApplicationIntegrationBindingError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(`${code}:${pointer}:${message}`);
    this.name = "ApplicationIntegrationBindingError";
  }
}

type Candidate = Readonly<{ pointer: string; reference: string; reference_kind: ApplicationReferenceKind }>;
const SELECTOR = /^([a-z][a-z0-9]*(?:-[a-z0-9]+)*):([a-z][a-z0-9]*(?:-[a-z0-9]+)*)(?:#([A-Za-z][A-Za-z0-9_-]*))?$/i;
const bindings = new WeakMap<ApplicationIntegrationBindingV1, string>();

function fail(code: string, pointer: string, message: string): never {
  throw new ApplicationIntegrationBindingError(code, pointer, message);
}

function freeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) freeze(child);
  }
  return value;
}

function add(rows: Candidate[], pointer: string, reference: string | null | undefined, referenceKind: ApplicationReferenceKind): void {
  if (reference !== null && reference !== undefined) rows.push({ pointer, reference, reference_kind: referenceKind });
}

function addKernelReferences(rows: Candidate[], kernel: IntegrationGenerationSourceV2["persistence"]["integration_kernel"], pointer: string, serializationKind: "data" | "event"): void {
  for (const [index, binding] of kernel.integration_bindings.entries()) {
    const kind: ApplicationReferenceKind = binding.concern === "persistence"
      ? "data"
      : binding.concern === "messaging"
        ? binding.direction === "outbound" ? "event" : "operation"
        : binding.direction === "outbound" ? "interface" : "operation";
    add(rows, `${pointer}/integration_bindings/${index}/logical_boundary_ref`, binding.logical_boundary_ref, kind);
  }
  for (const [index, profile] of kernel.serialization_profiles.entries()) {
    add(rows, `${pointer}/serialization_profiles/${index}/logical_type_ref`, profile.logical_type_ref, serializationKind);
  }
  for (const [mappingIndex, mapping] of kernel.failure_mappings.entries()) {
    for (const [caseIndex, item] of mapping.cases.entries()) add(rows, `${pointer}/failure_mappings/${mappingIndex}/cases/${caseIndex}/failure_outcome_ref`, item.failure_outcome_ref, "failure");
    add(rows, `${pointer}/failure_mappings/${mappingIndex}/unknown_failure_outcome_ref`, mapping.unknown_failure_outcome_ref, "failure");
  }
}

function collectReferences(source: IntegrationGenerationSourceV2): readonly Candidate[] {
  const rows: Candidate[] = [];
  addKernelReferences(rows, source.persistence.integration_kernel, "/persistence/integration_kernel", "data");
  addKernelReferences(rows, source.messaging.integration_kernel, "/messaging/integration_kernel", "event");
  addKernelReferences(rows, source.external_api.integration_kernel, "/external_api/integration_kernel", "data");

  for (const [index, binding] of source.persistence.persistence_bindings.entries()) {
    for (const [subjectIndex, reference] of binding.logical_subject_refs.entries()) add(rows, `/persistence/persistence_bindings/${index}/logical_subject_refs/${subjectIndex}`, reference, "data");
  }
  for (const [index, mapping] of source.persistence.persistence_mappings.entries()) {
    for (const [subjectIndex, reference] of mapping.logical_subject_refs.entries()) add(rows, `/persistence/persistence_mappings/${index}/logical_subject_refs/${subjectIndex}`, reference, "data");
    for (const [fieldIndex, field] of mapping.identity_mappings.entries()) add(rows, `/persistence/persistence_mappings/${index}/identity_mappings/${fieldIndex}/logical_property_ref`, field.logical_property_ref, "field");
    for (const [fieldIndex, field] of mapping.field_mappings.entries()) add(rows, `/persistence/persistence_mappings/${index}/field_mappings/${fieldIndex}/logical_property_ref`, field.logical_property_ref, "field");
    for (const [conversionIndex, conversion] of mapping.conversion_rules.entries()) add(rows, `/persistence/persistence_mappings/${index}/conversion_rules/${conversionIndex}/source_shape`, conversion.source_shape, "data");
  }

  for (const [index, message] of source.messaging.message_types.entries()) add(rows, `/messaging/message_types/${index}/logical_payload_ref`, message.logical_payload_ref, "event");
  for (const [index, mapping] of source.messaging.message_mappings.entries()) add(rows, `/messaging/message_mappings/${index}/mapper_ref`, mapping.mapper_ref, "mapping");
  for (const [index, binding] of source.messaging.publication_bindings.entries()) {
    add(rows, `/messaging/publication_bindings/${index}/logical_source_ref`, binding.logical_source_ref, "event");
    add(rows, `/messaging/publication_bindings/${index}/mapper_ref`, binding.mapper_ref, "mapping");
  }
  for (const [index, binding] of source.messaging.subscription_bindings.entries()) {
    add(rows, `/messaging/subscription_bindings/${index}/mapper_ref`, binding.mapper_ref, "mapping");
    add(rows, `/messaging/subscription_bindings/${index}/operation_ref`, binding.operation_ref, "operation");
  }

  for (const [contractIndex, contract] of source.external_api.external_api_contracts.entries()) {
    for (const [roleIndex, role] of contract.consumer_role_refs.entries()) add(rows, `/external_api/external_api_contracts/${contractIndex}/consumer_role_refs/${roleIndex}`, role, "operation");
    for (const [operationIndex, operation] of contract.operations.entries()) {
      add(rows, `/external_api/external_api_contracts/${contractIndex}/operations/${operationIndex}/request_type_ref`, operation.request_type_ref, operation.request_type_ref.includes("#") ? "public-contract" : "data");
      add(rows, `/external_api/external_api_contracts/${contractIndex}/operations/${operationIndex}/result_type_ref`, operation.result_type_ref, operation.result_type_ref.includes("#") ? "public-contract" : "data");
      for (const [failureIndex, failure] of operation.failure_outcome_refs.entries()) add(rows, `/external_api/external_api_contracts/${contractIndex}/operations/${operationIndex}/failure_outcome_refs/${failureIndex}`, failure, "failure");
    }
  }
  for (const [index, mapping] of source.external_api.api_mappings.entries()) add(rows, `/external_api/api_mappings/${index}/mapper_ref`, mapping.mapper_ref, "mapping");
  for (const [index, binding] of source.external_api.inbound_endpoint_bindings.entries()) {
    add(rows, `/external_api/inbound_endpoint_bindings/${index}/request_mapper_ref`, binding.request_mapper_ref, "mapping");
    add(rows, `/external_api/inbound_endpoint_bindings/${index}/operation_ref`, binding.operation_ref, "operation");
    add(rows, `/external_api/inbound_endpoint_bindings/${index}/response_mapper_ref`, binding.response_mapper_ref, "mapping");
  }
  for (const [index, binding] of source.external_api.external_api_bindings.entries()) {
    add(rows, `/external_api/external_api_bindings/${index}/request_mapper_ref`, binding.request_mapper_ref, "mapping");
    add(rows, `/external_api/external_api_bindings/${index}/response_mapper_ref`, binding.response_mapper_ref, "mapping");
  }
  for (const [mappingIndex, mapping] of source.external_api.api_failure_mappings.entries()) {
    for (const [caseIndex, item] of mapping.cases.entries()) add(rows, `/external_api/api_failure_mappings/${mappingIndex}/cases/${caseIndex}/failure_outcome_ref`, item.failure_outcome_ref, "failure");
    add(rows, `/external_api/api_failure_mappings/${mappingIndex}/unknown_fallback_ref`, mapping.unknown_fallback_ref, "failure");
  }
  return Object.freeze(rows.sort((left, right) => left.pointer.localeCompare(right.pointer)));
}

function hasField(node: CompiledProjectGraphNode, fragment: string): boolean {
  const body = node.body as Record<string, unknown>;
  const contract = body.typed_contract as Record<string, unknown> | undefined;
  const properties = contract?.properties;
  if (Array.isArray(properties) && properties.some(value => {
    if (value === null || typeof value !== "object") return false;
    const property = value as Record<string, unknown>;
    return property.name === fragment || property.ontology_property === fragment;
  })) return true;
  const fields = body.fields;
  return Array.isArray(fields) && fields.includes(fragment);
}

type TypedValueType = Readonly<{
  kind?: string;
  name?: string;
  selector?: string;
  interface_selector?: string;
  contract_id?: string;
  element?: TypedValueType;
}>;

type TypedMappingView = Readonly<{
  total: boolean;
  inputs: readonly string[];
  target: string | null;
}>;

function typedMappingView(node: CompiledProjectGraphNode, pointer: string): TypedMappingView {
  const contract = (node.body as Record<string, unknown>).typed_contract as Record<string, unknown> | undefined;
  if (contract === undefined || typeof contract.schema_version !== "string" || typeof contract.total !== "boolean") {
    fail("DS_APPLICATION_BINDING_MAPPING_CONTRACT", pointer, `integration Mapping requires a typed contract:${node.selector}`);
  }
  if (contract.schema_version === "domainspec.typed-mapping/v1") {
    return freeze({ total: contract.total, inputs: Object.freeze([String(contract.source)]), target: String(contract.target) });
  }
  if (contract.schema_version === "domainspec.typed-mapping/v2" || contract.schema_version === "domainspec.typed-mapping/v3") {
    const inputs = Array.isArray(contract.inputs)
      ? contract.inputs.flatMap(item => {
        const type = (item as { readonly type?: TypedValueType }).type;
        return (type?.kind === "named" || type?.kind === "reference") && typeof type.selector === "string" ? [type.selector]
          : type?.kind === "contract" && typeof type.interface_selector === "string" && typeof type.contract_id === "string" ? [`${type.interface_selector}#${type.contract_id}`] : [];
      })
      : [];
    const target = contract.schema_version === "domainspec.typed-mapping/v2"
      ? typeof contract.target === "string" ? contract.target : null
      : (contract.target as { readonly kind?: string; readonly selector?: string } | undefined)?.kind === "named"
        ? (contract.target as { readonly selector: string }).selector
        : (contract.target as TypedValueType | undefined)?.kind === "contract"
          ? `${(contract.target as TypedValueType).interface_selector}#${(contract.target as TypedValueType).contract_id}` : null;
    return freeze({ total: contract.total, inputs: Object.freeze(inputs), target });
  }
  fail("DS_APPLICATION_BINDING_MAPPING_CONTRACT", pointer, `unsupported integration Mapping contract:${String(contract.schema_version)}`);
}

function expectedPersistenceShape(graph: CompiledProjectGraph, type: TypedValueType, pointer: string): PersistenceShape {
  if (type.kind === "scalar") return "scalar";
  if (type.kind === "optional" || type.kind === "list" || type.kind === "set") return type.kind;
  if (type.kind === "sum") return "sum";
  if (type.kind !== "named" || typeof type.selector !== "string") {
    fail("DS_APPLICATION_BINDING_PERSISTENCE_TYPE", pointer, "persistence property has an unsupported typed shape");
  }
  const target = graph.nodes.find(node => node.selector === type.selector);
  if (target?.kind === "Entity") return "entity-reference";
  if (target?.kind === "Value Object") return "value-object";
  if (target?.kind === "Enum") {
    const contract = (target.body as Record<string, unknown>).typed_contract as { readonly schema_version?: string; readonly variants?: readonly { readonly payload?: unknown }[] } | undefined;
    return contract?.schema_version === "domainspec.typed-sum/v1" && contract.variants?.some(variant => variant.payload !== null) ? "sum" : "enum";
  }
  if (target?.kind === "Sum") return "sum";
  fail("DS_APPLICATION_BINDING_PERSISTENCE_TYPE", pointer, `persistence property type does not resolve to a persistable value:${type.selector}`);
}

function validatePersistenceCoverage(graph: CompiledProjectGraph, source: IntegrationGenerationSourceV2): void {
  for (const [mappingIndex, mapping] of source.persistence.persistence_mappings.entries()) {
    const fields = new Map(mapping.field_mappings.map((field, fieldIndex) => [field.logical_property_ref, { field, fieldIndex }]));
    for (const subject of mapping.logical_subject_refs) {
      const node = graph.nodes.find(candidate => candidate.selector === subject)!;
      const contract = (node.body as Record<string, unknown>).typed_contract as { readonly schema_version?: string; readonly properties?: readonly Readonly<{ name: string; type: TypedValueType }>[] } | undefined;
      if (contract?.schema_version !== "domainspec.typed-record/v1" || !Array.isArray(contract.properties)) {
        fail("DS_APPLICATION_BINDING_PERSISTENCE_CONTRACT", `/persistence/persistence_mappings/${mappingIndex}/logical_subject_refs`, `complete persistence coverage requires a typed record:${subject}`);
      }
      for (const property of contract.properties) {
        const reference = `${subject}#${property.name}`;
        const row = fields.get(reference);
        if (row === undefined) {
          fail("DS_APPLICATION_BINDING_PERSISTENCE_COVERAGE", `/persistence/persistence_mappings/${mappingIndex}/field_mappings`, `logical property is not persisted:${reference}`);
        }
        const expected = expectedPersistenceShape(graph, property.type, `/persistence/persistence_mappings/${mappingIndex}/field_mappings/${row.fieldIndex}`);
        if (row.field.logical_shape !== expected) {
          fail("DS_APPLICATION_BINDING_PERSISTENCE_SHAPE", `/persistence/persistence_mappings/${mappingIndex}/field_mappings/${row.fieldIndex}/logical_shape`, `expected ${expected} for ${reference}, received ${row.field.logical_shape}`);
        }
      }
    }
  }
}

function validateMappingContracts(graph: CompiledProjectGraph, source: IntegrationGenerationSourceV2): void {
  const rows = [
    ...source.messaging.message_mappings.map((mapping, index) => ({ mapping, pointer: `/messaging/message_mappings/${index}` })),
    ...source.external_api.api_mappings.map((mapping, index) => ({ mapping, pointer: `/external_api/api_mappings/${index}` })),
  ];
  for (const { mapping, pointer } of rows) {
    const node = graph.nodes.find(candidate => candidate.selector === mapping.mapper_ref)!;
    const contract = typedMappingView(node, `${pointer}/mapper_ref`);
    if (contract.total !== mapping.total) {
      fail("DS_APPLICATION_BINDING_MAPPING_TOTALITY", `${pointer}/total`, `integration totality disagrees with ${mapping.mapper_ref}:${contract.total}`);
    }
  }
  for (const [index, mapping] of source.external_api.api_mappings.entries()) {
    const node = graph.nodes.find(candidate => candidate.selector === mapping.mapper_ref)!;
    const contract = typedMappingView(node, `/external_api/api_mappings/${index}/mapper_ref`);
    if (mapping.direction === "application-to-protocol" && !mapping.source_ref.includes("#result") && SELECTOR.test(mapping.source_ref) && !contract.inputs.includes(mapping.source_ref)) {
      fail("DS_APPLICATION_BINDING_MAPPING_INPUT", `/external_api/api_mappings/${index}/source_ref`, `authored Mapping does not accept ${mapping.source_ref}`);
    }
    if (mapping.direction === "protocol-to-application" && !mapping.target_ref.includes("#request") && SELECTOR.test(mapping.target_ref) && contract.target !== mapping.target_ref) {
      fail("DS_APPLICATION_BINDING_MAPPING_TARGET", `/external_api/api_mappings/${index}/target_ref`, `authored Mapping targets ${String(contract.target)}, not ${mapping.target_ref}`);
    }
  }
}

function resolve(graph: CompiledProjectGraph, candidate: Candidate): ApplicationIntegrationReferenceV1 {
  const match = SELECTOR.exec(candidate.reference);
  if (!match) fail("DS_APPLICATION_BINDING_REFERENCE", candidate.pointer, "expected an exact qualified application selector");
  const selector = `${match[1]}:${match[2]}`;
  const fragment = match[3] ?? null;
  const exact = graph.nodes.filter(node => node.selector === selector);
  if (exact.length === 0) {
    const folded = graph.nodes.filter(node => node.selector.toLowerCase() === selector.toLowerCase());
    fail(folded.length ? "DS_APPLICATION_BINDING_CASE_DRIFT" : "DS_APPLICATION_BINDING_MISSING", candidate.pointer, `unresolved application selector:${candidate.reference}`);
  }
  if (exact.length !== 1) fail("DS_APPLICATION_BINDING_AMBIGUOUS", candidate.pointer, `application selector resolves more than once:${selector}`);
  const node = exact[0]!;
  const expected = APPLICATION_REFERENCE_KIND_MATRIX[candidate.reference_kind];
  if (!expected.includes(node.kind)) fail("DS_APPLICATION_BINDING_WRONG_KIND", candidate.pointer, `expected ${expected.join("|")}, received ${node.kind}:${selector}`);
  if (candidate.reference_kind === "field") {
    if (fragment === null || !hasField(node, fragment)) fail("DS_APPLICATION_BINDING_FIELD", candidate.pointer, `field does not exist:${candidate.reference}`);
  } else if (candidate.reference_kind === "public-contract") {
    const contract = (node.body as Record<string, unknown>).typed_contract as { schema_version?: string; contracts?: readonly { contract_id: string }[] } | undefined;
    if (fragment === null || contract?.schema_version !== "domainspec.typed-interface/v1" || !contract.contracts?.some(c => c.contract_id === fragment)) fail("DS_APPLICATION_BINDING_PUBLIC_CONTRACT", candidate.pointer, `named public contract does not exist:${candidate.reference}`);
  } else if (candidate.reference_kind === "failure") {
    const failure = (node.body as Record<string, unknown>).failure_continuation;
    if (typeof failure !== "string" || failure.length === 0 || (fragment !== null && failure !== fragment)) fail("DS_APPLICATION_BINDING_FAILURE", candidate.pointer, `failure outcome does not exist:${candidate.reference}`);
  } else if (fragment !== null) {
    fail("DS_APPLICATION_BINDING_FRAGMENT", candidate.pointer, `fragment is not valid for ${candidate.reference_kind}`);
  }
  return freeze({ pointer: candidate.pointer, reference: candidate.reference, selector, fragment, reference_kind: candidate.reference_kind, expected_node_kinds: expected, actual_node_kind: node.kind });
}

export function assertApplicationIntegrationBinding(value: unknown): asserts value is ApplicationIntegrationBindingV1 {
  if (value === null || typeof value !== "object" || bindings.get(value as ApplicationIntegrationBindingV1) !== sha256(canonicalJson(value))) {
    fail("DS_APPLICATION_BINDING_SNAPSHOT", "/binding", "binding was not formed by the current process or has changed");
  }
}

export function validateApplicationIntegrationBinding(graph: CompiledProjectGraph, source: IntegrationGenerationSourceV2): ApplicationIntegrationBindingV1 {
  assertCompiledProjectSnapshot(graph);
  const integrationPlan = planIntegrationProjectV2(source, "typescript");
  const references = collectReferences(source).map(candidate => resolve(graph, candidate));
  validatePersistenceCoverage(graph, source);
  validateMappingContracts(graph, source);
  const applicationGraph = compileApplicationGraphV1(graph, source);
  const body = {
    schema_version: APPLICATION_INTEGRATION_BINDING_VERSION,
    project_id: graph.project_id,
    domain_source_manifest_sha256: graph.source_manifest.manifest_sha256,
    integration_source_id: source.source_id,
    integration_source_sha256: sha256(canonicalJson(source)),
    integration_semantic_manifest_sha256: sha256(canonicalJson(integrationPlan.semantic_manifest)),
    application_graph: applicationGraph,
    references: Object.freeze(references),
    reference_kind_matrix: APPLICATION_REFERENCE_KIND_MATRIX,
    runtime_guarantees_observed: false as const,
    claim_ceiling: "formation-and-static-compilation-only" as const,
    authority_effect: "none" as const,
  };
  const result = freeze({ ...body, binding_sha256: sha256(canonicalJson(body)) });
  bindings.set(result, sha256(canonicalJson(result)));
  return result;
}

/** Separate checked request binding; carries no provider or legacy certificate. */
export interface RequestApplicationBindingV1 {
 readonly schema_version:'domainspec.request-application-binding/v1-candidate';
 readonly project_id:string;readonly domain_source_manifest_sha256:string;
 readonly request_source_sha256:string;readonly application_plan_sha256:string;
 readonly source:RequestApplicationSourceV1;readonly application_graph:CompiledRequestApplicationGraphV1;
 readonly references:readonly ApplicationIntegrationReferenceV1[];
 readonly runtime_guarantees_observed:false;readonly authority_effect:'none';readonly claim_ceiling:'formation-and-static-compilation-only';
 readonly binding_sha256:string;
}
const requestBindings=new WeakMap<object,{digest:string;domain:CompiledProjectGraph;plan:SelectedReconciledProject}>();
export function assertRequestApplicationBindingV1(value:unknown):asserts value is RequestApplicationBindingV1 {
 const state=value&&typeof value==='object'?requestBindings.get(value):undefined;
 if(!state||state.digest!==sha256(canonicalJson(value)))return requestApplicationFail('DS_REQUEST_APPLICATION_BINDING_SNAPSHOT','/binding','use the owning request constructor');
 assertCompiledProjectSnapshot(state.domain);assertSelectedReconciledProject(state.plan);assertCompiledRequestApplicationGraphV1((value as RequestApplicationBindingV1).application_graph);
}
export function compileRequestApplicationBindingV1(graph:CompiledProjectGraph,input:unknown,applicationPlan:SelectedReconciledProject):RequestApplicationBindingV1 {
 assertCompiledProjectSnapshot(graph);assertSelectedReconciledProject(applicationPlan);
 const identity=selectedReconciledIdentity(applicationPlan),source=decodeRequestApplicationSourceV1(input);
 if(applicationPlan.selection.language!=='typescript'||identity.project_id!==graph.project_id||identity.source_manifest_sha256!==graph.source_manifest.manifest_sha256)requestApplicationFail('DS_REQUEST_APPLICATION_DOMAIN_JOIN','/plan','registered TypeScript plan must belong to exact domain');
 const application_graph=compileRequestApplicationGraphV1(graph,source);
 const references=source.entries.flatMap((entry,index)=>[
  resolve(graph,{pointer:`/entries/${index}/operation_ref`,reference:entry.operation_ref,reference_kind:'operation'}),
  resolve(graph,{pointer:`/entries/${index}/mapping_ref`,reference:entry.mapping_ref,reference_kind:'mapping'}),
 ]);
 for(const request of application_graph.operation_requests){
  const operation=applicationPlan.selection.operations.find(o=>o.selector===request.operation_ref);
  if(!operation||operation.inputs.length!==1||operation.events.length||operation.reads.length||operation.writes.length)return requestApplicationFail('DS_REQUEST_APPLICATION_OPERATION_UNSUPPORTED',request.request_ref,'one input, zero effect Operation required');
  for(const row of request.bindings){const mapping=application_graph.runtime_bindings.find(m=>m.binding_id===row.mapping_binding_ref)!;
   if(row.parameters.length!==1||row.parameters[0]!.parameter!==operation.inputs[0]!.name||canonicalJson(mapping.result_type)!==canonicalJson(operation.inputs[0]!.type))requestApplicationFail('DS_REQUEST_APPLICATION_REQUEST_TYPE',row.mapping_binding_ref,'Mapping result and Operation input differ');
  }
 }
 const body={schema_version:'domainspec.request-application-binding/v1-candidate' as const,project_id:graph.project_id,domain_source_manifest_sha256:graph.source_manifest.manifest_sha256,request_source_sha256:application_graph.request_source_sha256,application_plan_sha256:applicationPlan.plan_sha256,source,application_graph,references,runtime_guarantees_observed:false as const,authority_effect:'none' as const,claim_ceiling:'formation-and-static-compilation-only' as const};
 const result=freezeRequestApplication({...body,binding_sha256:sha256(canonicalJson(body))});requestBindings.set(result,{digest:sha256(canonicalJson(result)),domain:graph,plan:applicationPlan});return result;
}
