import type {
  InterfaceRelationAssertion,
  VersionedInterfaceDescriptor,
  VersionedInterfaceObservation,
} from "../contracts/interface-contracts.js";

export const settlementInterfaceDescriptor: VersionedInterfaceDescriptor = Object.freeze({
  schema_version: "domainspec.versioned-interface-boundary/v1",
  descriptor_id: "interface.settlement-port-v1",
  contract_id: "SettlementPort",
  exact_version: "1.2.0",
  compatibility_policy_id: "same-major-backward-compatible/v1",
  compatibility_direction: "consumer-to-provider",
  inside_boundary: "settlement-domain",
  outside_boundary: "settlement-consumers",
  domain_contract_id: "SettlementPort/domain-v1",
  transport_adapter_id: "SettlementHttpAdapter/v1",
  exposed_bindings: Object.freeze([
    Object.freeze({binding_id: "completeSettlement", kind: "Operation" as const, public_contract_id: "CompleteSettlement/v1"}),
    Object.freeze({binding_id: "findSettlement", kind: "Query" as const, public_contract_id: "FindSettlement/v1"}),
  ]),
  mapping_obligations: Object.freeze([
    Object.freeze({binding_id: "completeSettlement", direction: "request" as const, mapping_id: "CompleteSettlementRequestMap/v1"}),
    Object.freeze({binding_id: "completeSettlement", direction: "response" as const, mapping_id: "SettlementResponseMap/v1"}),
    Object.freeze({binding_id: "findSettlement", direction: "response" as const, mapping_id: "SettlementResponseMap/v1"}),
  ]),
  consumer_routes: Object.freeze([
    Object.freeze({consumer_id: "settlement-http-client", side: "outside" as const, adapter_id: "SettlementHttpAdapter/v1"}),
  ]),
  admission_status: "candidate",
  authority_effect: "none",
});

export const settlementInterfaceObservation = (): VersionedInterfaceObservation => ({
  contract_id: "SettlementPort",
  version: "1.2.0",
  compatibility_policy_id: "same-major-backward-compatible/v1",
  compatibility_direction: "consumer-to-provider",
  inside_boundary: "settlement-domain",
  outside_boundary: "settlement-consumers",
  domain_contract_id: "SettlementPort/domain-v1",
  transport_adapter_id: "SettlementHttpAdapter/v1",
  exposed_bindings: settlementInterfaceDescriptor.exposed_bindings.map((binding) => ({...binding, internal_type_ids: []})),
  mapping_obligations: settlementInterfaceDescriptor.mapping_obligations.map((item) => ({...item})),
  consumer_routes: settlementInterfaceDescriptor.consumer_routes.map((route) => ({...route})),
  compatibility_checks: [
    {consumer_version: "1.0.0", provider_version: "1.2.0", accepted: true},
    {consumer_version: "1.3.0", provider_version: "1.2.0", accepted: true},
    {consumer_version: "2.0.0", provider_version: "1.2.0", accepted: false},
  ],
});

export const interfaceRelationAssertion = (
  contract_id: InterfaceRelationAssertion["contract_id"] = "interface/exposes",
): InterfaceRelationAssertion => ({
  contract_id,
  mode: "blueprint-only",
  owner_evidence_sha256: "a".repeat(64),
  current_owner_evidence_sha256: "a".repeat(64),
  source_type: contract_id === "interface/exposes" ? "architecture.InterfaceImplementation" : "architecture.AdapterImplementation",
  target_type: contract_id === "interface/exposes" ? "architecture.OperationImplementation" : "architecture.InterfaceImplementation",
  exact_assertion_id: null,
});
