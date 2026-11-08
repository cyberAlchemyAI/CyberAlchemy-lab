import { readFileSync } from "node:fs";
import path from "node:path";
import { loadDomainSpecCompiler } from "../../src/domainspec-cli.js";
import { executableFixture } from "./application-executable-fixture.js";
import { digest } from "../../src/domainspec-profile.js";

export async function persistenceFixture() {
  const compiler = await loadDomainSpecCompiler();
  const source = executableFixture().source + `query FindOrder:
  source candidate Order
  output optional<Order>
  where EligibleOrder
  bind order <- candidate
persistence Orders:
  stores Order
  serves FindOrder
  accepts-writes-from SubmitOrder
  transaction local
`;
  // Reuse the backend's explicit formation-only provider fixture; no database is contacted.
  const composition = JSON.parse(readFileSync(path.resolve(compiler.binding.package_root, "../system-integration/fixtures/persistence-composition-v2/commerce-postgresql.json"), "utf8"));
  composition.persistence_bindings[0].logical_subject_refs = ["commerce:order"];
  const mapping = composition.persistence_mappings[0];
  mapping.logical_subject_refs = ["commerce:order"];
  mapping.physical_models = mapping.physical_models.filter((p: any) => p.model_id === "physical-model:orders");
  mapping.identity_mappings = mapping.identity_mappings.filter((p: any) => p.logical_property_ref === "commerce:order#id");
  mapping.field_mappings = ["id", "accepted"].map(field => ({ logical_property_ref: "commerce:order#" + field, logical_shape: "scalar", physical_field_ref: "physical:orders/" + field, storage_shape: "scalar", collection_semantics: "not-applicable", conversion_ref: null }));
  mapping.relation_mappings = []; mapping.index_mappings = []; mapping.conversion_rules = [];
  composition.migrations = [];
  const binding = { schema_version: "alchlang.application-persistence/v1-candidate", source_sha256: digest(source), composition,
    declarations: { Orders: { persistence_binding_ref: "persistence-binding:orders", transaction_binding_ref: "transaction-binding:submit-order" } } };
  return { compiler, source, binding };
}

export async function messagingFixture() {
  const compiler = await loadDomainSpecCompiler();
  const source = executableFixture().source + `event OrderSubmitted:
  event-type order-submitted
  version 1
  occurrence-id eventId String
  occurred-at required
  orderId -> Order.id
mapping OrderToMessage:
  input payload Order
  target Order
  total true
  field id <- payload.id
  field accepted <- payload.accepted
mapping MessageToOrder:
  input payload Order
  target Order
  total true
  field id <- payload.id
  field accepted <- payload.accepted
publication PublishOrder:
  event OrderSubmitted
    -> map OrderToMessage
    -> message OrderMessage
    -> topic OrderEvents
subscription ConsumeOrder:
  topic OrderEvents
    -> message OrderMessage
    -> map MessageToOrder
    -> operation SubmitOrder
  acknowledge after application-commit
  deduplicate by messageId
  failure -> dead-letter FailedOrders
`;
  const composition = JSON.parse(readFileSync(path.resolve(compiler.binding.package_root, "../system-integration/fixtures/messaging-composition-v2/order-submitted-topic.json"), "utf8"));
  composition.channels = composition.channels.filter((c: any) => ["topic", "dead-letter"].includes(c.channel_kind));
  composition.publication_bindings[0].mapper_ref = "commerce:order-to-message";
  composition.subscription_bindings[0].mapper_ref = "commerce:message-to-order";
  composition.subscription_bindings[0].operation_ref = "commerce:submit-order";
  composition.integration_kernel.integration_bindings[1].logical_boundary_ref = "commerce:submit-order";
  composition.message_mappings[0].mapper_ref = "commerce:order-to-message";
  composition.message_mappings[1].mapper_ref = "commerce:message-to-order";
  composition.message_mappings[1].target_ref = "commerce:submit-order#request";
  const binding = { schema_version: "alchlang.application-messaging/v1-candidate", source_sha256: digest(source), composition,
    declarations: { PublishOrder: { binding_ref: "publication:order-submitted" }, ConsumeOrder: { binding_ref: "subscription:billing-order" } },
    messages: { OrderMessage: "message-type:order-submitted-v1" }, channels: { OrderEvents: "channel:order-events-topic", FailedOrders: "channel:order-events-dead-letter" } };
  return { source, compiler, binding };
}

export async function externalApiFixture() {
  const compiler = await loadDomainSpecCompiler();
  const source = executableFixture().source + `interface OrderApi:
  kind external
  version 1.0.0
  compatibility exact
  contract SubmitRequest:
    id UInt64
    accepted Bool
  contract Summary:
    id UInt64
    accepted Bool
  exposes SubmitOrder:
    request SubmitRequest
    result Summary
mapping RequestToOrder:
  input payload OrderApi.SubmitRequest
  target Order
  total true
  field id <- payload.id
  field accepted <- payload.accepted
mapping OrderToSummary:
  input result Order
  target OrderApi.Summary
  total true
  field id <- result.id
  field accepted <- result.accepted
mapping ProviderRequest:
  input request OrderApi.SubmitRequest
  target OrderApi.SubmitRequest
  total true
  field id <- request.id
  field accepted <- request.accepted
mapping ProviderResponse:
  input result OrderApi.Summary
  target OrderApi.Summary
  total true
  field id <- result.id
  field accepted <- result.accepted
inbound-endpoint SubmitHttp:
  HTTP POST "/orders"
    -> request OrderApi.SubmitRequest
    -> operation SubmitOrder
    -> response OrderApi.Summary
outbound-call ProviderCall:
  operation SubmitOrder
    -> request OrderApi.SubmitRequest
    -> external-api PaymentGateway
    -> response OrderApi.Summary
`;
  const composition = JSON.parse(readFileSync(path.resolve(compiler.binding.package_root, "../system-integration/fixtures/external-api-composition-v2/payments-http.json"), "utf8"));
  const inbound = composition.inbound_endpoint_bindings[0], outbound = composition.external_api_bindings[0];
  const oldOperation = inbound.operation_ref;
  inbound.operation_ref = "commerce:submit-order";
  inbound.request_mapper_ref = "commerce:request-to-order";
  inbound.response_mapper_ref = "commerce:order-to-summary";
  outbound.request_mapper_ref = "commerce:provider-request";
  outbound.response_mapper_ref = "commerce:provider-response";
  composition.integration_kernel.integration_bindings.find((b: any) => b.binding_id === inbound.integration_binding_ref).logical_boundary_ref = inbound.operation_ref;
  const contract = composition.external_api_contracts[0];
  composition.integration_kernel.integration_bindings.find((b: any) => b.binding_id === outbound.integration_binding_ref).logical_boundary_ref = "commerce:order-api";
  contract.consumer_role_refs = ["commerce:submit-order"];
  contract.operations[0].request_type_ref = "commerce:order-api#submit-request";
  contract.operations[0].result_type_ref = "commerce:order-api#summary";
  const [outReq, outRes, inReq, inRes] = composition.api_mappings;
  outReq.mapper_ref = outbound.request_mapper_ref; outReq.source_ref = contract.operations[0].request_type_ref;
  outRes.mapper_ref = outbound.response_mapper_ref; outRes.target_ref = contract.operations[0].result_type_ref;
  inReq.mapper_ref = inbound.request_mapper_ref; inReq.target_ref = inReq.target_ref.replace(oldOperation, inbound.operation_ref);
  inRes.mapper_ref = inbound.response_mapper_ref; inRes.source_ref = inRes.source_ref.replace(oldOperation, inbound.operation_ref);
  const binding = { schema_version: "alchlang.application-external-api/v1-candidate", source_sha256: digest(source), composition,
    declarations: { SubmitHttp: { binding_ref: inbound.binding_id }, ProviderCall: { binding_ref: outbound.binding_id } },
    external_apis: { PaymentGateway: { contract_ref: contract.contract_id, interface_ref: "OrderApi" } },
    contract_refs: { "OrderApi.SubmitRequest": contract.operations[0].request_type_ref, "OrderApi.Summary": contract.operations[0].result_type_ref } };
  return { compiler, source, binding };
}
