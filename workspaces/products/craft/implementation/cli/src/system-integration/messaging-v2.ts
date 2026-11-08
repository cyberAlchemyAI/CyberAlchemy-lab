import { canonicalJson, sha256 } from "../input/source-manifest.js";
import { compileIntegrationKernelV2, validateIntegrationKernelV2 } from "./kernel-v2.js";
import type {
  AcknowledgementBoundaryV1,
  CompiledMessagingCompositionV2,
  DeduplicationPolicyV1,
  DeliveryPolicyV2,
  LegacyMessagingProjectionV2,
  MessageChannelV2,
  MessageMappingV1,
  MessageTypeV1,
  MessagingCompositionV2,
  OrderingPolicyV1,
  ProducerAcceptanceBoundaryV1,
  PublicationBindingV1,
  SubscriptionBindingV1,
} from "./messaging-v2-types.js";

const REF = /^[A-Za-z][A-Za-z0-9]*(?:[-.:/#][A-Za-z0-9]+)*$/;
type UnknownRecord = Record<string, unknown>;

export class MessagingCompositionError extends Error {
  readonly exitCode = 22;
  constructor(readonly code: string, readonly pointer: string, message: string) {
    super(message);
    this.name = "MessagingCompositionError";
  }
}

function fail(code: string, pointer: string, message: string): never { throw new MessagingCompositionError(code, pointer, message); }
function object(value: unknown, pointer: string): asserts value is UnknownRecord { if (value === null || typeof value !== "object" || Array.isArray(value)) fail("MESSAGING_SCHEMA", pointer, "expected object"); }
function exact(value: unknown, fields: readonly string[], pointer: string): asserts value is UnknownRecord { object(value, pointer); if (canonicalJson(Object.keys(value).sort()) !== canonicalJson([...fields].sort())) fail("MESSAGING_SCHEMA", pointer, "unexpected or missing member"); }
function ref(value: unknown, pointer: string): string { if (typeof value !== "string" || !REF.test(value)) fail("MESSAGING_REFERENCE", pointer, "invalid reference"); return value; }
function text(value: unknown, pointer: string): string { if (typeof value !== "string" || !value.trim()) fail("MESSAGING_SCHEMA", pointer, "expected non-empty text"); return value; }
function bool(value: unknown, pointer: string): boolean { if (typeof value !== "boolean") fail("MESSAGING_SCHEMA", pointer, "expected boolean"); return value; }
function integer(value: unknown, pointer: string, minimum = 1): number { if (!Number.isSafeInteger(value) || (value as number) < minimum) fail("MESSAGING_SCHEMA", pointer, `expected integer >= ${minimum}`); return value as number; }
function oneOf<T extends string>(value: unknown, allowed: readonly T[], pointer: string): T { if (!allowed.includes(value as T)) fail("MESSAGING_SCHEMA", pointer, `expected one of:${allowed.join(",")}`); return value as T; }
function records(value: unknown, pointer: string, allowEmpty = true): readonly unknown[] { if (!Array.isArray(value) || (!allowEmpty && value.length === 0)) fail("MESSAGING_SCHEMA", pointer, "expected record array"); return value; }
function refs(value: unknown, pointer: string, allowEmpty = true): readonly string[] { if (!Array.isArray(value) || (!allowEmpty && value.length === 0)) fail("MESSAGING_SCHEMA", pointer, "expected reference array"); const result = value.map((item, index) => ref(item, `${pointer}/${index}`)); if (new Set(result).size !== result.length) fail("MESSAGING_DUPLICATE", pointer, "duplicate reference"); return Object.freeze([...result].sort()); }
function nullableRef(value: unknown, pointer: string): string | null { return value === null ? null : ref(value, pointer); }
function nullableInteger(value: unknown, pointer: string): number | null { return value === null ? null : integer(value, pointer); }
function identities<T>(values: readonly T[], select: (value: T) => string, pointer: string): ReadonlyMap<string, T> { const result = new Map<string, T>(); for (const value of values) { const id = select(value); if (result.has(id)) fail("MESSAGING_DUPLICATE", pointer, `duplicate identity:${id}`); result.set(id, value); } return result; }
function freeze<T>(value: T): T { if (value !== null && typeof value === "object" && !Object.isFrozen(value)) { Object.freeze(value); for (const child of Object.values(value as Record<string, unknown>)) freeze(child); } return value; }
function member(value: unknown, pointer: string): string { if (typeof value !== "string" || !/^[A-Za-z][A-Za-z0-9_]*$/.test(value)) fail("MESSAGING_SCHEMA", pointer, "invalid member name"); return value; }
function pathMembers(value: unknown, pointer: string): readonly string[] { if (!Array.isArray(value) || value.length > 64) fail("MESSAGING_SCHEMA", pointer, "expected bounded member path"); return Object.freeze(value.map((item, index) => member(item, `${pointer}/${index}`))); }
function inputPaths(value: unknown, pointer: string) {
  const rows = records(value, pointer, false).map((entry, index) => { const p = `${pointer}/${index}`; exact(entry, ["parameter", "path"], p); return Object.freeze({ parameter: member(entry.parameter, `${p}/parameter`), path: pathMembers(entry.path, `${p}/path`) }); });
  identities(rows, item => item.parameter, pointer); return Object.freeze(rows);
}
function requestParameters(value: unknown, pointer: string) {
  const rows = records(value, pointer, false).map((entry, index) => {
    const p = `${pointer}/${index}`; exact(entry, ["parameter", "source"], p); object(entry.source, `${p}/source`); exact(entry.source, ["kind", "path"], `${p}/source`);
    const kind = oneOf(entry.source.kind, ["mapping-result", "source-body"] as const, `${p}/source/kind`);
    return Object.freeze({ parameter: member(entry.parameter, `${p}/parameter`), source: Object.freeze({ kind, path: pathMembers(entry.source.path, `${p}/source/path`) }) });
  });
  identities(rows, item => item.parameter, pointer);
  if (!rows.some(item => item.source.kind === "mapping-result")) fail("MESSAGING_REQUEST_COMPOSITION", pointer, "request must include a Mapping result");
  return Object.freeze(rows);
}

function messageType(value: unknown, pointer: string): MessageTypeV1 {
  exact(value, ["message_type_id", "message_kind", "logical_payload_ref", "serialization_profile_ref", "version"], pointer);
  return Object.freeze({ message_type_id: ref(value.message_type_id, `${pointer}/message_type_id`), message_kind: oneOf(value.message_kind, ["event-notification", "command-request", "query-request", "query-response", "integration-document"] as const, `${pointer}/message_kind`), logical_payload_ref: ref(value.logical_payload_ref, `${pointer}/logical_payload_ref`), serialization_profile_ref: ref(value.serialization_profile_ref, `${pointer}/serialization_profile_ref`), version: ref(value.version, `${pointer}/version`) });
}

function messageMapping(value: unknown, pointer: string): MessageMappingV1 {
  object(value, pointer);
  const direction = oneOf(value.direction, ["logical-to-message", "message-to-application"] as const, `${pointer}/direction`);
  const target = ref(value.target_ref, `${pointer}/target_ref`);
  const request = direction === "message-to-application" && target.endsWith("#request");
  exact(value, request ? ["mapping_id", "mapper_ref", "direction", "source_ref", "target_ref", "total", "input_paths", "request_parameters"] : ["mapping_id", "mapper_ref", "direction", "source_ref", "target_ref", "total"], pointer);
  return Object.freeze({ mapping_id: ref(value.mapping_id, `${pointer}/mapping_id`), mapper_ref: ref(value.mapper_ref, `${pointer}/mapper_ref`), direction, source_ref: ref(value.source_ref, `${pointer}/source_ref`), target_ref: target, total: bool(value.total, `${pointer}/total`), ...(request ? { input_paths: inputPaths(value.input_paths, `${pointer}/input_paths`), request_parameters: requestParameters(value.request_parameters, `${pointer}/request_parameters`) } : {}) });
}

function channel(value: unknown, pointer: string): MessageChannelV2 {
  object(value, pointer);
  const kind = oneOf(value.channel_kind, ["queue", "topic", "stream", "dead-letter"] as const, `${pointer}/channel_kind`);
  const common = { channel_id: ref(value.channel_id, `${pointer}/channel_id`), accepted_message_type_refs: refs(value.accepted_message_type_refs, `${pointer}/accepted_message_type_refs`, false), owner_ref: ref(value.owner_ref, `${pointer}/owner_ref`), lifecycle_policy_ref: ref(value.lifecycle_policy_ref, `${pointer}/lifecycle_policy_ref`), provider_name: value.provider_name === null ? null : text(value.provider_name, `${pointer}/provider_name`) };
  if (kind === "queue") { exact(value, ["channel_id", "channel_kind", "accepted_message_type_refs", "owner_ref", "lifecycle_policy_ref", "provider_name", "consumption_model"], pointer); if (value.consumption_model !== "competing-consumers") fail("MESSAGING_CHANNEL_COLLAPSE", `${pointer}/consumption_model`, "queue requires competing consumers"); return Object.freeze({ ...common, channel_kind: "queue", consumption_model: "competing-consumers" }); }
  if (kind === "topic") { exact(value, ["channel_id", "channel_kind", "accepted_message_type_refs", "owner_ref", "lifecycle_policy_ref", "provider_name", "consumption_model"], pointer); if (value.consumption_model !== "fan-out-subscriptions") fail("MESSAGING_CHANNEL_COLLAPSE", `${pointer}/consumption_model`, "topic requires fan-out subscriptions"); return Object.freeze({ ...common, channel_kind: "topic", consumption_model: "fan-out-subscriptions" }); }
  if (kind === "stream") { exact(value, ["channel_id", "channel_kind", "accepted_message_type_refs", "owner_ref", "lifecycle_policy_ref", "provider_name", "consumption_model", "cursor_model_ref", "ordering_scope_ref"], pointer); if (value.consumption_model !== "retained-log") fail("MESSAGING_CHANNEL_COLLAPSE", `${pointer}/consumption_model`, "stream requires retained log"); return Object.freeze({ ...common, channel_kind: "stream", consumption_model: "retained-log", cursor_model_ref: ref(value.cursor_model_ref, `${pointer}/cursor_model_ref`), ordering_scope_ref: ref(value.ordering_scope_ref, `${pointer}/ordering_scope_ref`) }); }
  exact(value, ["channel_id", "channel_kind", "accepted_message_type_refs", "owner_ref", "lifecycle_policy_ref", "provider_name", "source_channel_ref", "terminal_failure_classes", "retention_policy_ref", "redrive_policy_ref"], pointer);
  return Object.freeze({ ...common, channel_kind: "dead-letter", source_channel_ref: ref(value.source_channel_ref, `${pointer}/source_channel_ref`), terminal_failure_classes: refs(value.terminal_failure_classes, `${pointer}/terminal_failure_classes`, false), retention_policy_ref: ref(value.retention_policy_ref, `${pointer}/retention_policy_ref`), redrive_policy_ref: ref(value.redrive_policy_ref, `${pointer}/redrive_policy_ref`) });
}

function deliveryPolicy(value: unknown, pointer: string): DeliveryPolicyV2 {
  exact(value, ["policy_id", "guarantee", "retry_schedule_ref", "max_attempts", "lease_or_visibility_ref", "terminal_disposition", "dead_letter_channel_ref"], pointer);
  const result = Object.freeze({ policy_id: ref(value.policy_id, `${pointer}/policy_id`), guarantee: oneOf(value.guarantee, ["at-most-once", "at-least-once"] as const, `${pointer}/guarantee`), retry_schedule_ref: nullableRef(value.retry_schedule_ref, `${pointer}/retry_schedule_ref`), max_attempts: nullableInteger(value.max_attempts, `${pointer}/max_attempts`), lease_or_visibility_ref: nullableRef(value.lease_or_visibility_ref, `${pointer}/lease_or_visibility_ref`), terminal_disposition: oneOf(value.terminal_disposition, ["drop", "dead-letter", "retain"] as const, `${pointer}/terminal_disposition`), dead_letter_channel_ref: nullableRef(value.dead_letter_channel_ref, `${pointer}/dead_letter_channel_ref`) });
  if (result.guarantee === "at-least-once" && (result.max_attempts === null || result.lease_or_visibility_ref === null)) fail("MESSAGING_DELIVERY", pointer, "at-least-once requires attempts and lease/visibility");
  if ((result.terminal_disposition === "dead-letter") !== (result.dead_letter_channel_ref !== null)) fail("MESSAGING_DELIVERY", pointer, "dead-letter disposition and channel must agree");
  return result;
}

function producerBoundary(value: unknown, pointer: string): ProducerAcceptanceBoundaryV1 {
  exact(value, ["boundary_id", "publication_binding_ref", "condition", "observation_boundary", "claim_ceiling"], pointer);
  if (value.claim_ceiling !== "provider-accepted") fail("MESSAGING_ACCEPTANCE_CLAIM", `${pointer}/claim_ceiling`, "producer acceptance cannot claim delivery or application completion");
  return Object.freeze({ boundary_id: ref(value.boundary_id, `${pointer}/boundary_id`), publication_binding_ref: ref(value.publication_binding_ref, `${pointer}/publication_binding_ref`), condition: oneOf(value.condition, ["provider-accepted", "transport-persisted"] as const, `${pointer}/condition`), observation_boundary: ref(value.observation_boundary, `${pointer}/observation_boundary`), claim_ceiling: "provider-accepted" });
}

function acknowledgementBoundary(value: unknown, pointer: string): AcknowledgementBoundaryV1 {
  exact(value, ["boundary_id", "subscription_binding_ref", "condition", "failure_before_ack", "failure_after_ack", "evidence_boundary"], pointer);
  return Object.freeze({ boundary_id: ref(value.boundary_id, `${pointer}/boundary_id`), subscription_binding_ref: ref(value.subscription_binding_ref, `${pointer}/subscription_binding_ref`), condition: oneOf(value.condition, ["consumer-handler-returned", "application-committed"] as const, `${pointer}/condition`), failure_before_ack: ref(value.failure_before_ack, `${pointer}/failure_before_ack`), failure_after_ack: ref(value.failure_after_ack, `${pointer}/failure_after_ack`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`) });
}

function orderingPolicy(value: unknown, pointer: string): OrderingPolicyV1 {
  exact(value, ["policy_id", "mode", "key_expression", "observation_boundary", "disorder_handling"], pointer);
  const mode = oneOf(value.mode, ["unordered", "key-ordered", "globally-ordered"] as const, `${pointer}/mode`);
  const keyExpression = value.key_expression === null ? null : text(value.key_expression, `${pointer}/key_expression`);
  if ((mode === "key-ordered") !== (keyExpression !== null)) fail("MESSAGING_ORDERING", `${pointer}/key_expression`, "only key-ordered mode has a key expression");
  return Object.freeze({ policy_id: ref(value.policy_id, `${pointer}/policy_id`), mode, key_expression: keyExpression, observation_boundary: ref(value.observation_boundary, `${pointer}/observation_boundary`), disorder_handling: oneOf(value.disorder_handling, ["reject", "buffer", "accept-and-observe"] as const, `${pointer}/disorder_handling`) });
}

function deduplicationPolicy(value: unknown, pointer: string): DeduplicationPolicyV1 {
  exact(value, ["policy_id", "key_expression", "owner_ref", "retention_window_ref", "transaction_binding_ref", "duplicate_outcome"], pointer);
  return Object.freeze({ policy_id: ref(value.policy_id, `${pointer}/policy_id`), key_expression: text(value.key_expression, `${pointer}/key_expression`), owner_ref: ref(value.owner_ref, `${pointer}/owner_ref`), retention_window_ref: ref(value.retention_window_ref, `${pointer}/retention_window_ref`), transaction_binding_ref: nullableRef(value.transaction_binding_ref, `${pointer}/transaction_binding_ref`), duplicate_outcome: oneOf(value.duplicate_outcome, ["ignore", "return-recorded-result", "reject"] as const, `${pointer}/duplicate_outcome`) });
}

function publicationBinding(value: unknown, pointer: string): PublicationBindingV1 {
  exact(value, ["binding_id", "integration_binding_ref", "producer_contract_ref", "logical_source_ref", "message_type_ref", "mapper_ref", "channel_ref", "delivery_policy_ref", "producer_acceptance_boundary_ref", "provider_realization_ref", "failure_mapping_ref", "evidence_boundary", "authority_effect"], pointer);
  if (value.authority_effect !== "none") fail("MESSAGING_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ binding_id: ref(value.binding_id, `${pointer}/binding_id`), integration_binding_ref: ref(value.integration_binding_ref, `${pointer}/integration_binding_ref`), producer_contract_ref: ref(value.producer_contract_ref, `${pointer}/producer_contract_ref`), logical_source_ref: ref(value.logical_source_ref, `${pointer}/logical_source_ref`), message_type_ref: ref(value.message_type_ref, `${pointer}/message_type_ref`), mapper_ref: ref(value.mapper_ref, `${pointer}/mapper_ref`), channel_ref: ref(value.channel_ref, `${pointer}/channel_ref`), delivery_policy_ref: ref(value.delivery_policy_ref, `${pointer}/delivery_policy_ref`), producer_acceptance_boundary_ref: ref(value.producer_acceptance_boundary_ref, `${pointer}/producer_acceptance_boundary_ref`), provider_realization_ref: ref(value.provider_realization_ref, `${pointer}/provider_realization_ref`), failure_mapping_ref: ref(value.failure_mapping_ref, `${pointer}/failure_mapping_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), authority_effect: "none" });
}

function subscriptionBinding(value: unknown, pointer: string): SubscriptionBindingV1 {
  exact(value, ["binding_id", "integration_binding_ref", "channel_ref", "subscription_id", "message_type_ref", "mapper_ref", "operation_ref", "acknowledgement_boundary_ref", "delivery_policy_ref", "ordering_policy_ref", "deduplication_policy_ref", "failure_mapping_ref", "provider_realization_ref", "evidence_boundary", "authority_effect"], pointer);
  if (value.authority_effect !== "none") fail("MESSAGING_AUTHORITY", `${pointer}/authority_effect`, "authority growth forbidden");
  return Object.freeze({ binding_id: ref(value.binding_id, `${pointer}/binding_id`), integration_binding_ref: ref(value.integration_binding_ref, `${pointer}/integration_binding_ref`), channel_ref: ref(value.channel_ref, `${pointer}/channel_ref`), subscription_id: ref(value.subscription_id, `${pointer}/subscription_id`), message_type_ref: ref(value.message_type_ref, `${pointer}/message_type_ref`), mapper_ref: ref(value.mapper_ref, `${pointer}/mapper_ref`), operation_ref: ref(value.operation_ref, `${pointer}/operation_ref`), acknowledgement_boundary_ref: ref(value.acknowledgement_boundary_ref, `${pointer}/acknowledgement_boundary_ref`), delivery_policy_ref: ref(value.delivery_policy_ref, `${pointer}/delivery_policy_ref`), ordering_policy_ref: ref(value.ordering_policy_ref, `${pointer}/ordering_policy_ref`), deduplication_policy_ref: ref(value.deduplication_policy_ref, `${pointer}/deduplication_policy_ref`), failure_mapping_ref: ref(value.failure_mapping_ref, `${pointer}/failure_mapping_ref`), provider_realization_ref: ref(value.provider_realization_ref, `${pointer}/provider_realization_ref`), evidence_boundary: text(value.evidence_boundary, `${pointer}/evidence_boundary`), authority_effect: "none" });
}

export function validateMessagingCompositionV2(value: unknown): MessagingCompositionV2 {
  exact(value, ["schema_version", "composition_id", "integration_kernel", "message_types", "message_mappings", "channels", "delivery_policies", "producer_acceptance_boundaries", "acknowledgement_boundaries", "ordering_policies", "deduplication_policies", "publication_bindings", "subscription_bindings", "runtime_delivery_observed", "authority_effect"], "/");
  if (value.schema_version !== "domainspec.messaging-composition/v2-candidate") fail("MESSAGING_SCHEMA", "/schema_version", "unsupported schema");
  if (value.runtime_delivery_observed !== false) fail("MESSAGING_RUNTIME_CLAIM", "/runtime_delivery_observed", "formation is not delivery evidence");
  if (value.authority_effect !== "none") fail("MESSAGING_AUTHORITY", "/authority_effect", "authority growth forbidden");
  const kernel = validateIntegrationKernelV2(value.integration_kernel);
  const messages = records(value.message_types, "/message_types", false).map((entry, index) => messageType(entry, `/message_types/${index}`)).sort((a, b) => a.message_type_id.localeCompare(b.message_type_id));
  const mappings = records(value.message_mappings, "/message_mappings", false).map((entry, index) => messageMapping(entry, `/message_mappings/${index}`)).sort((a, b) => a.mapping_id.localeCompare(b.mapping_id));
  const channels = records(value.channels, "/channels", false).map((entry, index) => channel(entry, `/channels/${index}`)).sort((a, b) => a.channel_id.localeCompare(b.channel_id));
  const deliveries = records(value.delivery_policies, "/delivery_policies", false).map((entry, index) => deliveryPolicy(entry, `/delivery_policies/${index}`)).sort((a, b) => a.policy_id.localeCompare(b.policy_id));
  const producers = records(value.producer_acceptance_boundaries, "/producer_acceptance_boundaries", false).map((entry, index) => producerBoundary(entry, `/producer_acceptance_boundaries/${index}`)).sort((a, b) => a.boundary_id.localeCompare(b.boundary_id));
  const acknowledgements = records(value.acknowledgement_boundaries, "/acknowledgement_boundaries", false).map((entry, index) => acknowledgementBoundary(entry, `/acknowledgement_boundaries/${index}`)).sort((a, b) => a.boundary_id.localeCompare(b.boundary_id));
  const orderings = records(value.ordering_policies, "/ordering_policies", false).map((entry, index) => orderingPolicy(entry, `/ordering_policies/${index}`)).sort((a, b) => a.policy_id.localeCompare(b.policy_id));
  const deduplications = records(value.deduplication_policies, "/deduplication_policies", false).map((entry, index) => deduplicationPolicy(entry, `/deduplication_policies/${index}`)).sort((a, b) => a.policy_id.localeCompare(b.policy_id));
  const publications = records(value.publication_bindings, "/publication_bindings", false).map((entry, index) => publicationBinding(entry, `/publication_bindings/${index}`)).sort((a, b) => a.binding_id.localeCompare(b.binding_id));
  const subscriptions = records(value.subscription_bindings, "/subscription_bindings", false).map((entry, index) => subscriptionBinding(entry, `/subscription_bindings/${index}`)).sort((a, b) => a.binding_id.localeCompare(b.binding_id));
  const messageById = identities(messages, item => item.message_type_id, "/message_types");
  identities(mappings, item => item.mapping_id, "/message_mappings");
  const mappingByMapperRef = identities(mappings, item => item.mapper_ref, "/message_mappings");
  const channelById = identities(channels, item => item.channel_id, "/channels");
  const deliveryById = identities(deliveries, item => item.policy_id, "/delivery_policies");
  const producerById = identities(producers, item => item.boundary_id, "/producer_acceptance_boundaries");
  const ackById = identities(acknowledgements, item => item.boundary_id, "/acknowledgement_boundaries");
  const orderingById = identities(orderings, item => item.policy_id, "/ordering_policies");
  const dedupById = identities(deduplications, item => item.policy_id, "/deduplication_policies");
  const publicationById = identities(publications, item => item.binding_id, "/publication_bindings");
  const subscriptionById = identities(subscriptions, item => item.binding_id, "/subscription_bindings");
  const integrationById = identities(kernel.integration_bindings, item => item.binding_id, "/integration_kernel/integration_bindings");
  const serializationById = identities(kernel.serialization_profiles, item => item.profile_id, "/integration_kernel/serialization_profiles");
  const realizationById = identities(kernel.provider_realizations, item => item.realization_id, "/integration_kernel/provider_realizations");
  const failureById = identities(kernel.failure_mappings, item => item.mapping_id, "/integration_kernel/failure_mappings");
  for (const message of messages) if (!serializationById.has(message.serialization_profile_ref)) fail("MESSAGING_REFERENCE_UNRESOLVED", "/message_types", `serialization unresolved:${message.serialization_profile_ref}`);
  for (const item of channels) { for (const accepted of item.accepted_message_type_refs) if (!messageById.has(accepted)) fail("MESSAGING_REFERENCE_UNRESOLVED", "/channels", `message type unresolved:${accepted}`); if (item.channel_kind === "dead-letter") { const source = channelById.get(item.source_channel_ref); if (!source || source.channel_kind === "dead-letter") fail("MESSAGING_CHANNEL_COLLAPSE", "/channels", `dead-letter source invalid:${item.source_channel_ref}`); } }
  for (const item of deliveries) if (item.dead_letter_channel_ref !== null && channelById.get(item.dead_letter_channel_ref)?.channel_kind !== "dead-letter") fail("MESSAGING_REFERENCE_UNRESOLVED", "/delivery_policies", `dead-letter channel unresolved:${item.dead_letter_channel_ref}`);
  for (const binding of publications) {
    const integration = integrationById.get(binding.integration_binding_ref); const message = messageById.get(binding.message_type_ref); const mapping = mappingByMapperRef.get(binding.mapper_ref); const channelValue = channelById.get(binding.channel_ref); const boundary = producerById.get(binding.producer_acceptance_boundary_ref);
    if (!integration || integration.concern !== "messaging" || integration.direction === "inbound") fail("MESSAGING_REFERENCE_UNRESOLVED", "/publication_bindings", `outbound messaging integration unresolved:${binding.integration_binding_ref}`);
    if (!message || !mapping || mapping.direction !== "logical-to-message" || mapping.source_ref !== binding.logical_source_ref || mapping.target_ref !== message.message_type_id || mapping.mapper_ref !== binding.mapper_ref) fail("MESSAGING_GRAPH_COLLAPSE", "/publication_bindings", `Event -> Mapping -> Message edge invalid:${binding.binding_id}`);
    if (message.logical_payload_ref !== binding.logical_source_ref || !channelValue?.accepted_message_type_refs.includes(message.message_type_id)) fail("MESSAGING_GRAPH_COLLAPSE", "/publication_bindings", `Message -> Channel edge invalid:${binding.binding_id}`);
    if (!deliveryById.has(binding.delivery_policy_ref) || boundary?.publication_binding_ref !== binding.binding_id || !realizationById.has(binding.provider_realization_ref) || !failureById.has(binding.failure_mapping_ref)) fail("MESSAGING_REFERENCE_UNRESOLVED", "/publication_bindings", `publication reference unresolved:${binding.binding_id}`);
  }
  for (const binding of subscriptions) {
    const integration = integrationById.get(binding.integration_binding_ref); const message = messageById.get(binding.message_type_ref); const mapping = mappingByMapperRef.get(binding.mapper_ref); const channelValue = channelById.get(binding.channel_ref); const boundary = ackById.get(binding.acknowledgement_boundary_ref);
    if (!integration || integration.concern !== "messaging" || integration.direction === "outbound") fail("MESSAGING_REFERENCE_UNRESOLVED", "/subscription_bindings", `inbound messaging integration unresolved:${binding.integration_binding_ref}`);
    if (!message || !mapping || mapping.direction !== "message-to-application" || mapping.source_ref !== message.message_type_id || mapping.target_ref !== `${binding.operation_ref}#request` || mapping.mapper_ref !== binding.mapper_ref) fail("MESSAGING_GRAPH_COLLAPSE", "/subscription_bindings", `Channel -> Mapping -> Operation Request edge invalid:${binding.binding_id}`);
    if (!channelValue?.accepted_message_type_refs.includes(message.message_type_id) || boundary?.subscription_binding_ref !== binding.binding_id || !deliveryById.has(binding.delivery_policy_ref) || !orderingById.has(binding.ordering_policy_ref) || !dedupById.has(binding.deduplication_policy_ref) || !realizationById.has(binding.provider_realization_ref) || !failureById.has(binding.failure_mapping_ref)) fail("MESSAGING_REFERENCE_UNRESOLVED", "/subscription_bindings", `subscription reference unresolved:${binding.binding_id}`);
  }
  for (const boundary of producers) if (!publicationById.has(boundary.publication_binding_ref)) fail("MESSAGING_REFERENCE_UNRESOLVED", "/producer_acceptance_boundaries", `publication unresolved:${boundary.publication_binding_ref}`);
  for (const boundary of acknowledgements) if (!subscriptionById.has(boundary.subscription_binding_ref)) fail("MESSAGING_REFERENCE_UNRESOLVED", "/acknowledgement_boundaries", `subscription unresolved:${boundary.subscription_binding_ref}`);
  return freeze({ schema_version: "domainspec.messaging-composition/v2-candidate", composition_id: ref(value.composition_id, "/composition_id"), integration_kernel: kernel, message_types: Object.freeze(messages), message_mappings: Object.freeze(mappings), channels: Object.freeze(channels), delivery_policies: Object.freeze(deliveries), producer_acceptance_boundaries: Object.freeze(producers), acknowledgement_boundaries: Object.freeze(acknowledgements), ordering_policies: Object.freeze(orderings), deduplication_policies: Object.freeze(deduplications), publication_bindings: Object.freeze(publications), subscription_bindings: Object.freeze(subscriptions), runtime_delivery_observed: false, authority_effect: "none" });
}

export function compileMessagingCompositionV2(value: unknown): CompiledMessagingCompositionV2 {
  const composition = validateMessagingCompositionV2(value);
  const compiled = { ...composition, integration_kernel: compileIntegrationKernelV2(composition.integration_kernel) };
  return freeze({ ...compiled, composition_digest: sha256(canonicalJson(compiled)) });
}

export function projectLegacyMessagingV1(value: unknown): LegacyMessagingProjectionV2 {
  exact(value, ["schema_version", "binding_set_id", "profile_id", "subject_ref", "dependency_contracts", "persistence_bindings", "transaction_guarantee_bindings", "failure_outcome_bindings", "durable_workflow_runtime_bindings", "transport_bindings", "message_channels", "delivery_policies", "transport_failure_policies", "authority_effect"], "/");
  if (value.schema_version !== "domainspec.system-integration-binding-set/v1" || value.authority_effect !== "none") fail("MESSAGING_LEGACY_SCHEMA", "/", "unsupported legacy binding set");
  const eventRefs: string[] = []; const operationRefs: string[] = [];
  for (const [index, entry] of records(value.transport_bindings, "/transport_bindings").entries()) {
    const pointer = `/transport_bindings/${index}`;
    exact(entry, ["binding_id", "mode", "direction", "operation_ref", "event_ref", "channel_ref", "delivery_policy_ref", "failure_policy_ref", "envelope_profile_ref", "evidence_boundary"], pointer);
    if (entry.mode !== "message" || entry.direction !== "publish-subscribe" || entry.envelope_profile_ref !== "envelope:domainspec-event-json-v1") fail("MESSAGING_LEGACY_SCHEMA", pointer, "only the narrow v1 transport form is projectable");
    eventRefs.push(ref(entry.event_ref, `${pointer}/event_ref`)); operationRefs.push(ref(entry.operation_ref, `${pointer}/operation_ref`));
  }
  for (const [index, entry] of records(value.message_channels, "/message_channels").entries()) { const pointer = `/message_channels/${index}`; exact(entry, ["channel_id", "purpose", "allowed_event_refs", "publisher_operation_refs", "consumer_operation_refs", "evidence_boundary"], pointer); oneOf(entry.purpose, ["delivery", "dead-letter"] as const, `${pointer}/purpose`); refs(entry.allowed_event_refs, `${pointer}/allowed_event_refs`, false); refs(entry.publisher_operation_refs, `${pointer}/publisher_operation_refs`); refs(entry.consumer_operation_refs, `${pointer}/consumer_operation_refs`); }
  for (const [index, entry] of records(value.delivery_policies, "/delivery_policies").entries()) { const pointer = `/delivery_policies/${index}`; exact(entry, ["policy_id", "semantics", "acknowledgement_boundary", "ordering_scope", "visibility_timeout_seconds", "retention_seconds", "max_receive_count", "dead_letter_channel_ref", "deduplication_owner_ref", "evidence_boundary"], pointer); if (entry.semantics !== "at-least-once" || entry.acknowledgement_boundary !== "provider-accepted" || entry.ordering_scope !== "none") fail("MESSAGING_LEGACY_SCHEMA", pointer, "legacy policy exceeds its narrow form"); integer(entry.visibility_timeout_seconds, `${pointer}/visibility_timeout_seconds`); integer(entry.retention_seconds, `${pointer}/retention_seconds`); integer(entry.max_receive_count, `${pointer}/max_receive_count`); }
  return freeze({ schema_version: "domainspec.messaging-legacy-projection/v2-candidate", source_schema_version: "domainspec.binding-set/v1-candidate", source_digest: sha256(canonicalJson(value)), retained_event_refs: Object.freeze([...new Set(eventRefs)].sort()), retained_operation_refs: Object.freeze([...new Set(operationRefs)].sort()), channel_classification: "legacy-undifferentiated", producer_acceptance: "provider-accepted-unclassified", message_types_inferred: false, subscriptions_inferred: false, consumer_acknowledgement_inferred: false, application_commit_inferred: false, exactly_once_inferred: false, authority_effect: "none" });
}
