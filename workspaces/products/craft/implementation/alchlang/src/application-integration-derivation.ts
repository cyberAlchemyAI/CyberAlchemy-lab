import { CompilationRejected } from "./model.js";
import { digest, json, symbol } from "./domainspec-profile.js";
import { parseDomainSource } from "./parser.js";
import type { ApplicationFormalSource } from "./formal-claim.js";
import type { ApplicationDeclaration, ApplicationMappingDeclaration, ApplicationType } from "./application-source.js";
import type { DomainSpecCompiler } from "./domainspec-cli.js";

type Obj = Record<string, any>;
type IntegrationCompiler = Pick<DomainSpecCompiler,
  "compilePersistenceComposition" | "compileMessagingComposition" | "compileExternalApiComposition" | "integrationDefinitionPackSha256">;

const REFERENCE_PACK = "domainspec.reference-postgresql16-nats-http/v1-candidate";
const fail = (code: string, path: string, message: string): never => {
  throw new CompilationRejected([{ code, path, message }]);
};
const equal = (left: unknown, right: unknown) => json(left) === json(right);
const frozen = <T>(value: T): T => {
  if (value && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    Object.values(value as Record<string, unknown>).forEach(frozen);
  }
  return value;
};

function sourceModel(source: string): ApplicationFormalSource {
  const parsed = parseDomainSource(source);
  if (parsed.source_profile !== "application-v1") fail("APPLICATION_INTEGRATION_DERIVATION_PROFILE", "$", "application-v1 source required");
  return parsed.carrier as unknown as ApplicationFormalSource;
}

function declaration(model: ApplicationFormalSource, id: string, kind?: ApplicationDeclaration["kind"]): ApplicationDeclaration {
  const selected = model.declarations.find(item => item.id === id);
  if (!selected) fail("APPLICATION_INTEGRATION_DERIVATION_REFERENCE", `$declarations/${id}`, `expected declared ${kind ?? "value"}`);
  const result = selected!;
  if (kind !== undefined && result.kind !== kind) fail("APPLICATION_INTEGRATION_DERIVATION_REFERENCE", `$declarations/${id}`, `expected declared ${kind}`);
  return result;
}

function typeForName(model: ApplicationFormalSource, name: string): ApplicationType {
  const parts = name.split(".");
  if (parts.length === 2) {
    const boundary = declaration(model, parts[0]!, "interface");
    if (boundary.kind !== "interface" || !boundary.contracts.some(contract => contract.id === parts[1])) {
      return fail("APPLICATION_INTEGRATION_DERIVATION_TYPE", `$types/${name}`, "unknown Interface contract");
    }
    return { kind: "public-contract", interface: parts[0]!, contract: parts[1]! };
  }
  if (parts.length === 1) return { kind: "declaration", ref: name };
  return fail("APPLICATION_INTEGRATION_DERIVATION_TYPE", `$types/${name}`, "qualified type must be Interface.Contract");
}

function mappingTargetType(model: ApplicationFormalSource, mapping: ApplicationMappingDeclaration): ApplicationType {
  return typeForName(model, mapping.target);
}

function operationOutcome(model: ApplicationFormalSource, id: string, path: string): string {
  declaration(model, id, "operation");
  return `${symbol(model.domain_id)}:${symbol(id)}`;
}

function referencePackFailureOutcome(model: ApplicationFormalSource): string {
  const operations = [...new Set(model.integrations.filter(item => item.kind === "persistence").flatMap(item => item.operations.map(operation => operation.ref)))];
  if (operations.length !== 1) fail("APPLICATION_INTEGRATION_DERIVATION_FAILURE", "$integrations/provider-pack",
    `reference provider pack requires exactly one authored persistence write Operation to own provider failure continuation; found ${operations.length}`);
  return operationOutcome(model, operations[0]!, "$integrations/provider-pack");
}

function selectMapping(model: ApplicationFormalSource, input: ApplicationType, target: ApplicationType, role: string): ApplicationMappingDeclaration {
  const matches = model.declarations.filter((item): item is ApplicationMappingDeclaration => item.kind === "mapping"
    && item.inputs.some(parameter => equal(parameter.type, input)) && equal(mappingTargetType(model, item), target));
  if (matches.length !== 1) fail("APPLICATION_INTEGRATION_DERIVATION_MAPPING", `$integrations/${role}`, `expected exactly one Mapping from ${json(input).trim()} to ${json(target).trim()}; found ${matches.length}`);
  return matches[0]!;
}

function shape(model: ApplicationFormalSource, type: ApplicationType): string {
  if (type.kind === "scalar") return "scalar";
  if (type.kind === "reference") return "entity-reference";
  if (type.kind === "sum") return "sum";
  if (type.kind === "optional" || type.kind === "list" || type.kind === "set") return type.kind;
  if (type.kind === "declaration") {
    const kind = declaration(model, type.ref).kind;
    if (kind === "value-object" || kind === "enum") return kind;
  }
  return fail("APPLICATION_INTEGRATION_DERIVATION_SHAPE", "$persistence", "reference provider pack cannot derive this persistence shape");
}

function storage(logical: string): { storage_shape: string; collection_semantics: string } {
  if (logical === "scalar" || logical === "enum" || logical === "sum") return { storage_shape: "scalar", collection_semantics: "not-applicable" };
  if (logical === "entity-reference") return { storage_shape: "foreign-key", collection_semantics: "not-applicable" };
  if (logical === "value-object") return { storage_shape: "embedded", collection_semantics: "not-applicable" };
  if (logical === "optional") return { storage_shape: "nullable", collection_semantics: "not-applicable" };
  if (logical === "list") return { storage_shape: "array", collection_semantics: "ordered" };
  if (logical === "set") return { storage_shape: "array", collection_semantics: "unique-unordered" };
  return fail("APPLICATION_INTEGRATION_DERIVATION_SHAPE", "$persistence", `unsupported logical shape ${logical}`);
}

function kernel(definition: string, id: string, values: {
  bindings: Obj[]; profiles: Obj[]; realizations: Obj[]; serializations?: Obj[]; failures: Obj[];
}) {
  return {
    schema_version: "domainspec.integration-kernel/v2-candidate", kernel_id: id,
    definition_pack_sha256: definition, integration_bindings: values.bindings,
    provider_profiles: values.profiles, provider_realizations: values.realizations,
    serialization_profiles: values.serializations ?? [], failure_mappings: values.failures,
    runtime_receipts: [], runtime_guarantees_observed: false, authority_effect: "none",
  };
}

function derivePersistence(source: string, model: ApplicationFormalSource, compiler: IntegrationCompiler) {
  const domain = symbol(model.domain_id), rows = model.integrations.filter(item => item.kind === "persistence");
  if (!rows.length) fail("APPLICATION_INTEGRATION_DERIVATION_COVERAGE", "$persistence", "authored persistence declaration required");
  const profile = "provider-profile:postgresql-v1", realization = `provider-realization:${domain}-postgresql`;
  const resource = `resource:${domain}-database`, packFailureOutcome = referencePackFailureOutcome(model);
  const bindings: Obj[] = [], mappings: Obj[] = [], transactions: Obj[] = [], failures: Obj[] = [], choices: Obj = {};
  for (const row of rows) {
    const id = symbol(row.id), selectedEntity = declaration(model, row.entity.ref, "entity");
    if (selectedEntity.kind !== "entity") fail("APPLICATION_INTEGRATION_DERIVATION_ENTITY", `$line:${row.source_line}`, "stored value must be an Entity");
    const entity = selectedEntity as Extract<ApplicationDeclaration, { kind: "entity" | "value-object" }>;
    if (!entity.identity) fail("APPLICATION_INTEGRATION_DERIVATION_ENTITY", `$line:${row.source_line}`, "stored Entity requires an explicit identity");
    const identityName = entity.identity!;
    const entityRef = `${domain}:${symbol(entity.id)}`, table = symbol(entity.id, "_");
    const integrationId = `binding:${id}-persistence`, bindingId = `persistence-binding:${id}`;
    const mappingId = `persistence-mapping:${id}`, transactionId = `transaction-binding:${id}`;
    const contract = `contract:${id}-store`, failure = `failure-mapping:${id}-persistence`;
    const failureOutcome = packFailureOutcome;
    bindings.push({ binding_id: integrationId, concern: "persistence", direction: "bidirectional", logical_boundary_ref: entityRef,
      contract_ref: contract, provider_realization_ref: realization, policy_refs: [transactionId], serialization_profile_ref: null,
      failure_mapping_ref: failure, evidence_boundary: "derived-formation-only-no-database-contact", authority_effect: "none" });
    const fieldMappings = entity.fields.map(field => {
      const logical = shape(model, field.type), physical = `physical:${table}/${symbol(field.name, "_")}`;
      return { logical_property_ref: `${entityRef}#${symbol(field.name, "_")}`, logical_shape: logical, physical_field_ref: physical,
        ...storage(logical), conversion_ref: null };
    });
    const identity = fieldMappings.find(field => field.logical_property_ref === `${entityRef}#${symbol(identityName, "_")}`)!;
    mappings.push({ mapping_id: mappingId, logical_subject_refs: [entityRef],
      physical_models: [{ model_id: `physical-model:${table}`, model_kind: "relational-table", physical_name: table, version: "v1" }],
      identity_mappings: [{ logical_property_ref: identity.logical_property_ref, physical_field_ref: identity.physical_field_ref, conversion_ref: null }],
      field_mappings: fieldMappings, relation_mappings: [], index_mappings: [], conversion_rules: [], version: "v1", authority_effect: "none" });
    transactions.push({ binding_id: transactionId, unit_of_work_contract_ref: `contract:${id}-unit-of-work`, persistence_binding_refs: [bindingId],
      participant_refs: [`participant:${table}-row`, "participant:outbox-row"], atomicity_scope: row.transaction.scope,
      local_commit_boundary_ref: `commit-boundary:${domain}-database`, selected_guarantees: ["atomicity", "durability", "rollback-restoration"],
      implementation_profile_ref: profile, failure_mapping_ref: failure, evidence_boundary: "declared-local-commit-boundary-no-runtime-proof",
      runtime_guarantees_observed: false, authority_effect: "none" });
    failures.push({ mapping_id: failure, boundary_ref: contract, cases: [
      { provider_failure_matcher: "postgresql:connection-unavailable", failure_outcome_ref: failureOutcome, outcome_class: "retryable" },
      { provider_failure_matcher: "postgresql:unique-violation", failure_outcome_ref: failureOutcome, outcome_class: "non-retryable" }],
      unknown_failure_outcome_ref: failureOutcome, continuation_owner_ref: `owner:${symbol(model.owner)}`,
      evidence_boundary: "classification-only", authority_effect: "none" });
    choices[row.id] = { persistence_binding_ref: bindingId, transaction_binding_ref: transactionId };
  }
  const composition = {
    schema_version: "domainspec.persistence-composition/v2-candidate", composition_id: `persistence-composition:${domain}-derived-v1`,
    integration_kernel: kernel(compiler.integrationDefinitionPackSha256, `integration-kernel:${domain}-persistence-derived-v1`, {
      bindings, profiles: [{ profile_id: profile, concern: "persistence", provider_kind: "postgresql", capability_set: ["local-transaction", "typed-query"],
        configuration_schema_ref: "schema:postgresql-configuration-v1", secret_slot_refs: ["credential-slot:database-url"], compatibility_constraints: ["postgresql:version-16-or-newer"], authority_effect: "none" }],
      realizations: [{ realization_id: realization, provider_profile_ref: profile, adapter_ref: `adapter:${domain}-postgresql`, resource_ref: resource,
        configuration_ref: `configuration:${domain}-postgresql`, credential_binding_ref: `credential-binding:${domain}-database`, deployment_ref: null,
        evidence_boundary: "configuration-reference-only", runtime_observed: false, authority_effect: "none" }],
      failures,
    }), persistence_bindings: rows.map((row, index) => {
      const id = symbol(row.id); return { binding_id: `persistence-binding:${id}`, integration_binding_ref: bindings[index]!.binding_id,
        logical_subject_refs: mappings[index]!.logical_subject_refs, dependency_contract_ref: bindings[index]!.contract_ref,
        adapter_ref: `adapter:${domain}-postgresql`, resource_ref: resource, implementation_profile_ref: profile,
        logical_physical_mapping_ref: mappings[index]!.mapping_id, evidence_boundary: "typed-derived-formation-only", authority_effect: "none" };
    }), persistence_mappings: mappings, transaction_guarantees: transactions, migrations: [], runtime_guarantees_observed: false, authority_effect: "none",
  };
  compiler.compilePersistenceComposition(composition);
  return { schema_version: "alchlang.application-persistence/v1-candidate", source_sha256: digest(source), composition, declarations: choices };
}

function deriveMessaging(source: string, model: ApplicationFormalSource, compiler: IntegrationCompiler) {
  const domain = symbol(model.domain_id), owner = `owner:${symbol(model.owner)}`;
  const packFailureOutcome = referencePackFailureOutcome(model);
  const rows = model.integrations.filter(item => item.kind === "publication" || item.kind === "subscription");
  const publications = rows.filter(item => item.kind === "publication"), subscriptions = rows.filter(item => item.kind === "subscription");
  if (!publications.length || !subscriptions.length) fail("APPLICATION_INTEGRATION_DERIVATION_COVERAGE", "$messaging", "reference application requires authored publication and subscription declarations");
  const messageNames = [...new Set(rows.map(item => item.message.ref))];
  const messageIds = Object.fromEntries(messageNames.map(name => [name, `message-type:${symbol(name)}-v1`]));
  const primary = new Map<string, "queue" | "topic" | "stream">();
  for (const row of rows) {
    const prior = primary.get(row.channel.ref);
    if (prior && prior !== row.channel.kind) fail("APPLICATION_INTEGRATION_DERIVATION_CHANNEL", `$line:${row.channel.source_line}`, "channel alias has conflicting kinds");
    primary.set(row.channel.ref, row.channel.kind);
  }
  const channelId = (name: string, kind: string) => `channel:${symbol(name)}-${kind}`;
  const channelIds: Obj = Object.fromEntries([...primary].map(([name, kind]) => [name, channelId(name, kind)]));
  for (const row of subscriptions) channelIds[row.dead_letter.ref] = channelId(row.dead_letter.ref, "dead-letter");
  const eventForMessage = new Map<string, string>();
  for (const row of publications) {
    const event = `${domain}:${symbol(row.event.ref)}`, prior = eventForMessage.get(row.message.ref);
    if (prior && prior !== event) fail("APPLICATION_INTEGRATION_DERIVATION_MESSAGE", `$line:${row.source_line}`, "one message alias cannot collapse distinct Events");
    eventForMessage.set(row.message.ref, event);
  }
  for (const name of messageNames) if (!eventForMessage.has(name)) fail("APPLICATION_INTEGRATION_DERIVATION_MESSAGE", `$messages/${name}`, "subscription message requires one authored publication source");
  const profile = "provider-profile:broker-v1", realization = `provider-realization:${domain}-broker`;
  const serialization = messageNames.map(name => ({ profile_id: `serialization:${symbol(name)}-json-v1`, logical_type_ref: eventForMessage.get(name)!, format: "json", schema_ref: `schema:${symbol(name)}-json-v1`, version: "v1", compatibility_policy: "backward", encoding_options: { canonical_keys: true }, authority_effect: "none" }));
  const messageTypes = messageNames.map(name => ({ message_type_id: messageIds[name], message_kind: "event-notification", logical_payload_ref: eventForMessage.get(name), serialization_profile_ref: `serialization:${symbol(name)}-json-v1`, version: "v1" }));
  const deadForChannel = new Map<string, string>();
  for (const row of subscriptions) {
    const prior = deadForChannel.get(row.channel.ref);
    if (prior && prior !== row.dead_letter.ref) fail("APPLICATION_INTEGRATION_DERIVATION_CHANNEL", `$line:${row.source_line}`, "one channel cannot derive conflicting dead-letter destinations");
    deadForChannel.set(row.channel.ref, row.dead_letter.ref);
  }
  const accepted = (channel: string) => [...new Set(rows.filter(item => item.channel.ref === channel).map(item => messageIds[item.message.ref]))];
  const channels: Obj[] = [...primary].map(([name, kind]) => ({ channel_id: channelIds[name], channel_kind: kind, accepted_message_type_refs: accepted(name), owner_ref: owner,
    lifecycle_policy_ref: `lifecycle:${symbol(name)}`, provider_name: null,
    ...(kind === "queue" ? { consumption_model: "competing-consumers" } : kind === "topic" ? { consumption_model: "fan-out-subscriptions" }
      : { consumption_model: "retained-log", cursor_model_ref: `cursor:${symbol(name)}`, ordering_scope_ref: `ordering:${symbol(name)}` }) }));
  for (const row of subscriptions) if (!channels.some(channel => channel.channel_id === channelIds[row.dead_letter.ref])) channels.push({
    channel_id: channelIds[row.dead_letter.ref], channel_kind: "dead-letter", accepted_message_type_refs: [messageIds[row.message.ref]], owner_ref: owner,
    lifecycle_policy_ref: `lifecycle:${symbol(row.dead_letter.ref)}`, provider_name: null, source_channel_ref: channelIds[row.channel.ref],
    terminal_failure_classes: ["integration:invalid-message", "integration:max-attempts"], retention_policy_ref: "retention:bounded",
    redrive_policy_ref: "redrive:operator-approved",
  });
  const deliveryFor = (channel: string) => `delivery:${symbol(channel)}`;
  const deliveries = [...primary].map(([name]) => ({ policy_id: deliveryFor(name), guarantee: "at-least-once", retry_schedule_ref: "retry:bounded-exponential", max_attempts: 5,
    lease_or_visibility_ref: "visibility:bounded", terminal_disposition: deadForChannel.has(name) ? "dead-letter" : "retain",
    dead_letter_channel_ref: deadForChannel.has(name) ? channelIds[deadForChannel.get(name)!] : null }));
  const integrationBindings: Obj[] = [], messageMappings: Obj[] = [], publicationBindings: Obj[] = [], subscriptionBindings: Obj[] = [], failures: Obj[] = [];
  const producerBoundaries: Obj[] = [], acknowledgements: Obj[] = [], orderings: Obj[] = [], deduplications: Obj[] = [], choices: Obj = {};
  for (const row of publications) {
    const id = symbol(row.id), bindingId = `publication:${id}`, integrationId = `binding:${id}`, mapper = `${domain}:${symbol(row.mapping.ref)}`;
    const mapping = declaration(model, row.mapping.ref, "mapping"); if (mapping.kind !== "mapping") throw new Error("unreachable");
    const acceptance = `acceptance:${id}`, failure = `failure-mapping:${id}-broker`;
    const failureOutcome = packFailureOutcome;
    integrationBindings.push({ binding_id: integrationId, concern: "messaging", direction: "outbound", logical_boundary_ref: `${domain}:${symbol(row.event.ref)}`,
      contract_ref: `contract:${id}-publisher`, provider_realization_ref: realization, policy_refs: [deliveryFor(row.channel.ref)],
      serialization_profile_ref: `serialization:${symbol(row.message.ref)}-json-v1`, failure_mapping_ref: failure, evidence_boundary: "derived-formation-only", authority_effect: "none" });
    messageMappings.push({ mapping_id: `message-mapping:${id}`, mapper_ref: mapper, direction: "logical-to-message", source_ref: `${domain}:${symbol(row.event.ref)}`,
      target_ref: messageIds[row.message.ref], total: mapping.total });
    publicationBindings.push({ binding_id: bindingId, integration_binding_ref: integrationId, producer_contract_ref: `contract:${id}-publisher`, logical_source_ref: `${domain}:${symbol(row.event.ref)}`,
      message_type_ref: messageIds[row.message.ref], mapper_ref: mapper, channel_ref: channelIds[row.channel.ref], delivery_policy_ref: deliveryFor(row.channel.ref),
      producer_acceptance_boundary_ref: acceptance, provider_realization_ref: realization, failure_mapping_ref: failure,
      evidence_boundary: "provider-acceptance-is-not-delivery", authority_effect: "none" });
    producerBoundaries.push({ boundary_id: acceptance, publication_binding_ref: bindingId, condition: "provider-accepted", observation_boundary: `boundary:${id}-publish-response`, claim_ceiling: "provider-accepted" });
    failures.push({ mapping_id: failure, boundary_ref: `contract:${id}-publisher`, cases: [
      { provider_failure_matcher: "broker:throttled", failure_outcome_ref: failureOutcome, outcome_class: "retryable" },
      { provider_failure_matcher: "broker:invalid-message", failure_outcome_ref: failureOutcome, outcome_class: "non-retryable" }],
      unknown_failure_outcome_ref: failureOutcome, continuation_owner_ref: owner, evidence_boundary: "classification-only", authority_effect: "none" });
    choices[row.id] = { binding_ref: bindingId };
  }
  for (const row of subscriptions) {
    const id = symbol(row.id), bindingId = `subscription:${id}`, integrationId = `binding:${id}`, mapper = `${domain}:${symbol(row.mapping.ref)}`;
    const mapping = declaration(model, row.mapping.ref, "mapping"); if (mapping.kind !== "mapping") throw new Error("unreachable");
    const ack = `ack:${id}`, ordering = `ordering:${id}`, dedup = `dedup:${id}`, failure = `failure-mapping:${id}-broker`;
    const failureOutcome = packFailureOutcome;
    integrationBindings.push({ binding_id: integrationId, concern: "messaging", direction: "inbound", logical_boundary_ref: `${domain}:${symbol(row.operation.ref)}`,
      contract_ref: null, provider_realization_ref: realization, policy_refs: [ack, deliveryFor(row.channel.ref), ordering, dedup],
      serialization_profile_ref: `serialization:${symbol(row.message.ref)}-json-v1`, failure_mapping_ref: failure, evidence_boundary: "derived-formation-only", authority_effect: "none" });
    messageMappings.push({ mapping_id: `message-mapping:${id}`, mapper_ref: mapper, direction: "message-to-application", source_ref: messageIds[row.message.ref],
      target_ref: `${domain}:${symbol(row.operation.ref)}#request`, total: mapping.total,
      input_paths: mapping.inputs.map(input => ({ parameter: symbol(input.name, "_"), path: [symbol(input.name, "_")] })),
      request_parameters: [{ parameter: "request", source: { kind: "mapping-result", path: [] } }] });
    subscriptionBindings.push({ binding_id: bindingId, integration_binding_ref: integrationId, channel_ref: channelIds[row.channel.ref], subscription_id: id,
      message_type_ref: messageIds[row.message.ref], mapper_ref: mapper, operation_ref: `${domain}:${symbol(row.operation.ref)}`, acknowledgement_boundary_ref: ack,
      delivery_policy_ref: deliveryFor(row.channel.ref), ordering_policy_ref: ordering, deduplication_policy_ref: dedup, failure_mapping_ref: failure,
      provider_realization_ref: realization, evidence_boundary: "formation-only-no-consumption-claim", authority_effect: "none" });
    acknowledgements.push({ boundary_id: ack, subscription_binding_ref: bindingId, condition: row.acknowledge.condition,
      failure_before_ack: "failure:transport-redelivery", failure_after_ack: "failure:application-recovery", evidence_boundary: "authored-acknowledgement-only" });
    orderings.push({ policy_id: ordering, mode: "unordered", key_expression: null, observation_boundary: `boundary:${id}-delivery`, disorder_handling: "accept-and-observe" });
    deduplications.push({ policy_id: dedup, key_expression: `message.${row.deduplicate.key_path.join(".")}`, owner_ref: owner,
      retention_window_ref: "retention:bounded", transaction_binding_ref: null, duplicate_outcome: "return-recorded-result" });
    failures.push({ mapping_id: failure, boundary_ref: `boundary:${id}-consumer`, cases: [
      { provider_failure_matcher: "broker:throttled", failure_outcome_ref: failureOutcome, outcome_class: "retryable" },
      { provider_failure_matcher: "broker:invalid-message", failure_outcome_ref: failureOutcome, outcome_class: "non-retryable" }],
      unknown_failure_outcome_ref: failureOutcome, continuation_owner_ref: owner, evidence_boundary: "classification-only", authority_effect: "none" });
    choices[row.id] = { binding_ref: bindingId };
  }
  const composition = { schema_version: "domainspec.messaging-composition/v2-candidate", composition_id: `messaging-composition:${domain}-derived-v1`,
    integration_kernel: kernel(compiler.integrationDefinitionPackSha256, `integration-kernel:${domain}-messaging-derived-v1`, {
      bindings: integrationBindings, profiles: [{ profile_id: profile, concern: "messaging", provider_kind: "managed-broker", capability_set: ["dead-letter", "topic"],
        configuration_schema_ref: "schema:broker-configuration-v1", secret_slot_refs: [], compatibility_constraints: ["broker:topic-support"], authority_effect: "none" }],
      realizations: [{ realization_id: realization, provider_profile_ref: profile, adapter_ref: `adapter:${domain}-broker`, resource_ref: `resource:${domain}-broker`,
        configuration_ref: `configuration:${domain}-broker`, credential_binding_ref: null, deployment_ref: null, evidence_boundary: "configuration-reference-only", runtime_observed: false, authority_effect: "none" }],
      serializations: serialization,
      failures,
    }), message_types: messageTypes, message_mappings: messageMappings, channels, delivery_policies: deliveries,
    producer_acceptance_boundaries: producerBoundaries, acknowledgement_boundaries: acknowledgements, ordering_policies: orderings,
    deduplication_policies: deduplications, publication_bindings: publicationBindings, subscription_bindings: subscriptionBindings,
    runtime_delivery_observed: false, authority_effect: "none" };
  compiler.compileMessagingComposition(composition);
  return { schema_version: "alchlang.application-messaging/v1-candidate", source_sha256: digest(source), composition, declarations: choices,
    messages: messageIds, channels: channelIds };
}

function deriveExternalApi(source: string, model: ApplicationFormalSource, compiler: IntegrationCompiler) {
  const domain = symbol(model.domain_id), owner = `owner:${symbol(model.owner)}`;
  const packFailureOutcome = referencePackFailureOutcome(model);
  const inbound = model.integrations.filter(item => item.kind === "inbound-endpoint"), outbound = model.integrations.filter(item => item.kind === "outbound-call");
  if (!inbound.length || !outbound.length) fail("APPLICATION_INTEGRATION_DERIVATION_COVERAGE", "$external-api", "reference application requires authored inbound and outbound API declarations");
  const clientProfile = "provider-profile:http-client-v1", serverProfile = "provider-profile:http-server-v1";
  const client = `provider-realization:${domain}-http-client`, server = `provider-realization:${domain}-http-server`;
  const kernelBindings: Obj[] = [], apiMappings: Obj[] = [], inboundBindings: Obj[] = [], outboundBindings: Obj[] = [];
  const auth: Obj[] = [], resilience: Obj[] = [], webhooks: Obj[] = [], failures: Obj[] = [], choices: Obj = {}, externalApis: Obj = {}, contractRefs: Obj = {};
  const contractsByAlias = new Map<string, Obj>();
  const usedMappers = new Set<string>();
  const addMapping = (mapping: ApplicationMappingDeclaration, value: Obj) => {
    const mapper = `${domain}:${symbol(mapping.id)}`;
    if (usedMappers.has(mapper)) fail("APPLICATION_INTEGRATION_DERIVATION_MAPPING", `$mappings/${mapping.id}`, "one API Mapping cannot represent multiple protocol directions");
    usedMappers.add(mapper); apiMappings.push({ mapping_id: `api-mapping:${symbol(mapping.id)}`, mapper_ref: mapper, total: mapping.total, ...value });
    return mapper;
  };
  for (const row of inbound) {
    const id = symbol(row.id), operation = declaration(model, row.operation.ref, "operation"); if (operation.kind !== "operation") throw new Error("unreachable");
    const requestType = typeForName(model, row.request.ref), responseType = typeForName(model, row.response.ref);
    const requestMap = selectMapping(model, requestType, operation.input, `${row.id}/request`);
    const responseMap = selectMapping(model, operation.output, responseType, `${row.id}/response`);
    const bindingId = `inbound-endpoint:${id}`, integrationId = `binding:${id}-endpoint`, protocol = `protocol-operation:${id}`, authId = `authentication:${id}`;
    const inboundFailure = `failure-mapping:${id}-http-inbound`, failureOutcome = packFailureOutcome;
    const requestMapper = addMapping(requestMap, { direction: "protocol-to-application", source_ref: `${protocol}#request`, target_ref: `${domain}:${symbol(row.operation.ref)}#request`,
      input_paths: requestMap.inputs.map(input => ({ parameter: symbol(input.name, "_"), path: [] })), request_parameters: [{ parameter: "request", source: { kind: "mapping-result", path: [] } }] });
    const responseMapper = addMapping(responseMap, { direction: "application-to-protocol", source_ref: `${domain}:${symbol(row.operation.ref)}#result`, target_ref: `${protocol}#response` });
    kernelBindings.push({ binding_id: integrationId, concern: "external-api", direction: "inbound", logical_boundary_ref: `${domain}:${symbol(row.operation.ref)}`, contract_ref: null,
      provider_realization_ref: server, policy_refs: [`verification:${id}-signature`, `replay:${id}`], serialization_profile_ref: null,
      failure_mapping_ref: inboundFailure, evidence_boundary: "derived-formation-only-no-listener", authority_effect: "none" });
    inboundBindings.push({ binding_id: bindingId, integration_binding_ref: integrationId, protocol_operation_ref: protocol, request_mapper_ref: requestMapper,
      operation_ref: `${domain}:${symbol(row.operation.ref)}`, response_mapper_ref: responseMapper, authentication_binding_ref: authId,
      failure_mapping_ref: inboundFailure, provider_realization_ref: server, evidence_boundary: "verification-before-mapping", authority_effect: "none" });
    auth.push({ binding_id: authId, integration_boundary_ref: bindingId, scheme: "signed-request", credential_slot_refs: ["credential-slot:webhook-signing-secret"],
      credential_provider_ref: "credential-provider:runtime-secret-store", rotation_policy_ref: "rotation:webhook-secret", evidence_boundary: "references-only", contains_secret_values: false, authority_effect: "none" });
    webhooks.push({ binding_id: `webhook:${id}`, inbound_endpoint_binding_ref: bindingId, sender_verification_ref: `verification:${id}-signature`, replay_protection_ref: `replay:${id}`,
      external_event_id_expression: "request.headers.eventId", acknowledgement_policy: "ack-after-application-commit", application_completion_inferred: false, authority_effect: "none" });
    failures.push({ mapping_id: inboundFailure, boundary_ref: bindingId, cases: [
      { provider_failure_matcher: "webhook:invalid-signature", failure_outcome_ref: failureOutcome, outcome_class: "non-retryable" }],
      unknown_failure_outcome_ref: failureOutcome, continuation_owner_ref: owner, evidence_boundary: "classification-only", authority_effect: "none" });
    choices[row.id] = { binding_ref: bindingId };
  }
  for (const row of outbound) {
    const id = symbol(row.id), operation = declaration(model, row.operation.ref, "operation"); if (operation.kind !== "operation") throw new Error("unreachable");
    const requestType = typeForName(model, row.request.ref), responseType = typeForName(model, row.response.ref);
    if (requestType.kind !== "public-contract") fail("APPLICATION_INTEGRATION_DERIVATION_TYPE", `$line:${row.source_line}`, "outbound request must name an Interface contract");
    if (responseType.kind !== "public-contract") fail("APPLICATION_INTEGRATION_DERIVATION_TYPE", `$line:${row.source_line}`, "outbound response must name an Interface contract");
    const requestContract = requestType as Extract<ApplicationType, { kind: "public-contract" }>;
    const responseContract = responseType as Extract<ApplicationType, { kind: "public-contract" }>;
    if (requestContract.interface !== responseContract.interface) {
      fail("APPLICATION_INTEGRATION_DERIVATION_TYPE", `$line:${row.source_line}`, "outbound request and response must name contracts on one Interface");
    }
    const requestMap = selectMapping(model, requestContract, requestContract, `${row.id}/request`);
    const responseMap = selectMapping(model, responseContract, responseContract, `${row.id}/response`);
    const decisionMap = row.decision_mapping ? declaration(model, row.decision_mapping.ref, "mapping") : null;
    if (decisionMap && (decisionMap.kind !== "mapping" || decisionMap.inputs.length !== 1
      || !equal(decisionMap.inputs[0]!.type, responseType) || !equal(mappingTargetType(model, decisionMap), operation.input))) {
      fail("APPLICATION_INTEGRATION_DERIVATION_DECISION_MAPPING", `$line:${row.decision_mapping!.source_line}`,
        "decision Mapping must project the declared provider response into the existing Operation input type");
    }
    const contractId = `contract:${symbol(row.external_api.ref)}`, operationId = id, providerOperation = `provider-operation:${id}`;
    const requestRef = `${domain}:${symbol(requestContract.interface)}#${symbol(requestContract.contract)}`, resultRef = `${domain}:${symbol(responseContract.interface)}#${symbol(responseContract.contract)}`;
    contractRefs[row.request.ref] = requestRef; contractRefs[row.response.ref] = resultRef;
    let contract = contractsByAlias.get(row.external_api.ref);
    if (!contract) {
      contract = { contract_id: contractId, concern: "external-api", consumer_role_refs: [], operations: [], authority_effect: "none" };
      contractsByAlias.set(row.external_api.ref, contract); externalApis[row.external_api.ref] = { contract_ref: contractId, interface_ref: requestContract.interface };
    } else if (externalApis[row.external_api.ref].interface_ref !== requestContract.interface) {
      fail("APPLICATION_INTEGRATION_DERIVATION_API", `$line:${row.source_line}`, "external API alias cannot collapse distinct Interface boundaries");
    }
    contract.consumer_role_refs.push(`${domain}:${symbol(row.operation.ref)}`);
    const operationFailure = packFailureOutcome;
    contract.operations.push({ operation_id: operationId, request_type_ref: requestRef, result_type_ref: resultRef,
      failure_outcome_refs: [operationFailure], safety: "unsafe" });
    const requestMapper = addMapping(requestMap, { direction: "application-to-protocol", source_ref: requestRef, target_ref: `${providerOperation}#request` });
    const responseMapper = addMapping(responseMap, { direction: "protocol-to-application", source_ref: `${providerOperation}#response`, target_ref: resultRef });
    const bindingId = `external-api-binding:${id}`, integrationId = `binding:${id}-api`, policy = `resilience:${id}`, apiFailure = `api-failure-mapping:${id}`;
    const outboundFailure = `failure-mapping:${id}-http-outbound`;
    kernelBindings.push({ binding_id: integrationId, concern: "external-api", direction: "outbound", logical_boundary_ref: `${domain}:${symbol(requestContract.interface)}`, contract_ref: contractId,
      provider_realization_ref: client, policy_refs: [policy], serialization_profile_ref: null, failure_mapping_ref: outboundFailure,
      evidence_boundary: "derived-formation-only-no-http-call", authority_effect: "none" });
    resilience.push({ policy_id: policy, timeout_ms: 3000, max_attempts: 1, backoff_ref: null, concurrency_policy_ref: null, circuit_policy_ref: null,
      retry_safety: "retry-forbidden", idempotency_key_expression: null, evidence_boundary: "reference-pack-single-attempt" });
    outboundBindings.push({ binding_id: bindingId, integration_binding_ref: integrationId, external_api_contract_ref: contractId, contract_operation_ref: `${contractId}#${operationId}`,
      provider_operation_ref: providerOperation, request_mapper_ref: requestMapper, response_mapper_ref: responseMapper, authentication_binding_ref: null,
      resilience_policy_ref: policy, failure_mapping_ref: apiFailure, provider_realization_ref: client, evidence_boundary: "formation-only-no-http-call", authority_effect: "none" });
    choices[row.id] = { binding_ref: bindingId,
      ...(decisionMap ? { decision_mapper_ref: `${domain}:${symbol(decisionMap.id)}` } : {}) };
    failures.push({ mapping_id: outboundFailure, boundary_ref: contractId, cases: [
      { provider_failure_matcher: "http:timeout", failure_outcome_ref: operationFailure, outcome_class: "retryable" },
      { provider_failure_matcher: "http:unauthorized", failure_outcome_ref: operationFailure, outcome_class: "non-retryable" },
      { provider_failure_matcher: "http:malformed-response", failure_outcome_ref: operationFailure, outcome_class: "non-retryable" }],
      unknown_failure_outcome_ref: operationFailure, continuation_owner_ref: owner, evidence_boundary: "classification-only", authority_effect: "none" });
  }
  const apiFailures = outbound.map((row, index) => {
    const binding = outboundBindings[index]!, outcome = packFailureOutcome;
    return { mapping_id: binding.failure_mapping_ref, external_api_contract_ref: binding.external_api_contract_ref,
      kernel_failure_mapping_ref: kernelBindings.find(item => item.binding_id === binding.integration_binding_ref)!.failure_mapping_ref, cases: [
        { category: "timeout", matcher_ref: "http:timeout", failure_outcome_ref: outcome },
        { category: "authentication", matcher_ref: "http:unauthorized", failure_outcome_ref: outcome },
        { category: "malformed-response", matcher_ref: "http:malformed-response", failure_outcome_ref: outcome }],
      unknown_fallback_ref: outcome, evidence_boundary: "translation-only", authority_effect: "none" };
  });
  const composition = { schema_version: "domainspec.external-api-composition/v2-candidate", composition_id: `external-api-composition:${domain}-derived-v1`,
    integration_kernel: kernel(compiler.integrationDefinitionPackSha256, `integration-kernel:${domain}-api-derived-v1`, {
      bindings: kernelBindings, profiles: [
        { profile_id: clientProfile, concern: "external-api", provider_kind: "http-client", capability_set: ["json", "tls"], configuration_schema_ref: "schema:http-client-v1", secret_slot_refs: [], compatibility_constraints: ["http:version-1-or-2"], authority_effect: "none" },
        { profile_id: serverProfile, concern: "external-api", provider_kind: "http-server", capability_set: ["signed-webhook", "tls"], configuration_schema_ref: "schema:http-server-v1", secret_slot_refs: ["credential-slot:webhook-signing-secret"], compatibility_constraints: ["http:version-1-or-2"], authority_effect: "none" }],
      realizations: [
        { realization_id: client, provider_profile_ref: clientProfile, adapter_ref: `adapter:${domain}-http-client`, resource_ref: `resource:${domain}-external-api`, configuration_ref: `configuration:${domain}-external-api`, credential_binding_ref: null, deployment_ref: null, evidence_boundary: "configuration-reference-only", runtime_observed: false, authority_effect: "none" },
        { realization_id: server, provider_profile_ref: serverProfile, adapter_ref: `adapter:${domain}-http-server`, resource_ref: `resource:${domain}-inbound-http`, configuration_ref: `configuration:${domain}-inbound-http`, credential_binding_ref: `credential-binding:${domain}-webhook`, deployment_ref: null, evidence_boundary: "configuration-reference-only", runtime_observed: false, authority_effect: "none" }],
      failures,
    }), external_api_contracts: [...contractsByAlias.values()], api_mappings: apiMappings, authentication_bindings: auth,
    resilience_policies: resilience, api_failure_mappings: apiFailures, inbound_endpoint_bindings: inboundBindings,
    external_api_bindings: outboundBindings, webhook_bindings: webhooks, runtime_calls_observed: false, authority_effect: "none" };
  compiler.compileExternalApiComposition(composition);
  return { schema_version: "alchlang.application-external-api/v1-candidate", source_sha256: digest(source), composition, declarations: choices,
    external_apis: externalApis, contract_refs: contractRefs };
}

/** Derive internal reference-pack contracts from authored logical declarations. */
export function deriveApplicationIntegrationBindings(source: string, runtimeProfile: string, compiler: IntegrationCompiler) {
  const model = sourceModel(source);
  const profile = model.runtime_profiles?.find(item => item.id === runtimeProfile);
  if (!profile) fail("APPLICATION_INTEGRATION_DERIVATION_RUNTIME", "$runtime", "selected authored runtime profile is missing");
  const selectedProfile = profile!;
  if (selectedProfile.pack_id !== REFERENCE_PACK) fail("APPLICATION_INTEGRATION_DERIVATION_PACK", `$line:${selectedProfile.source_line}`, "no internal-contract derivation exists for the selected provider pack");
  const result = { persistence: derivePersistence(source, model, compiler), messaging: deriveMessaging(source, model, compiler), externalApi: deriveExternalApi(source, model, compiler),
    trace: { schema_version: "alchlang.application-integration-derivation-trace/v1-candidate", source_sha256: digest(source), runtime_profile: runtimeProfile,
      provider_pack: selectedProfile.pack_id, derivation: "authored-logical-input-plus-selected-reference-pack", runtime_guarantees_observed: false, authority_effect: "none" } };
  return frozen(result);
}
