import { canonicalJson, sha256 } from "../input/source-manifest.js";

export type IntegrationNodeKind = "message-contract" | "inbound-endpoint" | "publication" | "request-contract";
export type IntegrationRelationshipId = "reads-payload-from" | "produces-message-contract" | "invokes" | "accepts-request" | "publishes-event";

export interface IntegrationRelationshipSignatureV1 {
  readonly id: IntegrationRelationshipId;
  readonly source_types: readonly string[];
  readonly target_types: readonly string[];
  readonly multiplicity: "one_to_one" | "many_to_one" | "many_to_many";
  readonly validation_obligations: readonly string[];
}

const signatures: readonly IntegrationRelationshipSignatureV1[] = Object.freeze([
  Object.freeze({ id: "reads-payload-from", source_types: Object.freeze(["Mapping"]), target_types: Object.freeze(["Event"]), multiplicity: "many_to_many", validation_obligations: Object.freeze(["reject_non_mapping_source", "reject_non_event_target", "require_mapping_input_agreement"]) }),
  Object.freeze({ id: "produces-message-contract", source_types: Object.freeze(["Mapping"]), target_types: Object.freeze(["message-contract"]), multiplicity: "many_to_one", validation_obligations: Object.freeze(["reject_non_mapping_source", "reject_non_message_contract_target", "require_message_target_agreement"]) }),
  Object.freeze({ id: "invokes", source_types: Object.freeze(["inbound-endpoint"]), target_types: Object.freeze(["Operation"]), multiplicity: "many_to_one", validation_obligations: Object.freeze(["reject_non_inbound_endpoint_source", "reject_non_operation_target", "require_single_invocation_target"]) }),
  Object.freeze({ id: "accepts-request", source_types: Object.freeze(["Operation"]), target_types: Object.freeze(["request-contract"]), multiplicity: "one_to_one", validation_obligations: Object.freeze(["reject_non_operation_source", "reject_non_request_contract_target", "require_request_mapping_agreement"]) }),
  Object.freeze({ id: "publishes-event", source_types: Object.freeze(["publication"]), target_types: Object.freeze(["Event"]), multiplicity: "many_to_one", validation_obligations: Object.freeze(["reject_non_publication_source", "reject_non_event_target", "require_publication_mapping_message_agreement"]) }),
]);

const authorityBody = Object.freeze({
  schema_version: "domainspec.integration-relationship-authority/v1-candidate" as const,
  source_path: "projects/domainspec-v2/definitions/integration-relationships/relationships.yml" as const,
  signature_count: 5 as const,
  signatures,
  domain_emits_relationship: "Entity --emits--> Event" as const,
  publication_relationship: "publication --publishes-event--> Event" as const,
  authority_effect: "none" as const,
});

export const INTEGRATION_RELATIONSHIP_AUTHORITY_SHA256 = sha256(canonicalJson(authorityBody));
export const INTEGRATION_RELATIONSHIP_AUTHORITY_V1 = Object.freeze({ ...authorityBody, authority_sha256: INTEGRATION_RELATIONSHIP_AUTHORITY_SHA256 });

export function integrationRelationshipSignature(id: string): IntegrationRelationshipSignatureV1 | undefined {
  return signatures.find(signature => signature.id === id);
}
