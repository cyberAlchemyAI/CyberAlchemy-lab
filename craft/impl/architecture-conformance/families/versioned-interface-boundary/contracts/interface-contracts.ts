export type InterfaceBindingKind = "Operation" | "Query";

export type InterfaceBinding = Readonly<{
  binding_id: string;
  kind: InterfaceBindingKind;
  public_contract_id: string;
}>;

export type MappingObligation = Readonly<{
  binding_id: string;
  direction: "request" | "response";
  mapping_id: string;
}>;

export type VersionedInterfaceDescriptor = Readonly<{
  schema_version: "domainspec.versioned-interface-boundary/v1";
  descriptor_id: string;
  contract_id: string;
  exact_version: string;
  compatibility_policy_id: "same-major-backward-compatible/v1";
  compatibility_direction: "consumer-to-provider";
  inside_boundary: string;
  outside_boundary: string;
  domain_contract_id: string;
  transport_adapter_id: string;
  exposed_bindings: readonly InterfaceBinding[];
  mapping_obligations: readonly MappingObligation[];
  consumer_routes: readonly Readonly<{
    consumer_id: string;
    side: "outside";
    adapter_id: string;
  }>[];
  admission_status: "candidate";
  authority_effect: "none";
}>;

export type VersionedInterfaceObservation = Readonly<{
  contract_id: string;
  version: string;
  compatibility_policy_id: string;
  compatibility_direction: "consumer-to-provider" | "provider-to-consumer";
  inside_boundary: string;
  outside_boundary: string;
  domain_contract_id: string;
  transport_adapter_id: string;
  exposed_bindings: readonly Readonly<InterfaceBinding & {internal_type_ids: readonly string[]}>[];
  mapping_obligations: readonly MappingObligation[];
  consumer_routes: readonly Readonly<{
    consumer_id: string;
    side: "outside" | "inside";
    adapter_id: string;
  }>[];
  compatibility_checks: readonly Readonly<{
    consumer_version: string;
    provider_version: string;
    accepted: boolean;
  }>[];
}>;

export type InterfaceRelationAssertion = Readonly<{
  contract_id: "interface/exposes" | "interface/implemented-by-adapter";
  mode: "blueprint-only" | "materialized";
  owner_evidence_sha256: string;
  current_owner_evidence_sha256: string;
  source_type: string;
  target_type: string;
  exact_assertion_id: string | null;
}>;

export type InterfaceFindingCode =
  | "RMT_IFACE_UNDECLARED_EXPOSURE"
  | "RMT_IFACE_EXPOSURE_DRIFT"
  | "RMT_IFACE_INTERNAL_TYPE_LEAK"
  | "RMT_IFACE_VERSION_REGRESSION"
  | "RMT_IFACE_COMPATIBILITY_OVERCLAIM"
  | "RMT_IFACE_COMPATIBILITY_DIRECTION_FLIP"
  | "RMT_IFACE_BOUNDARY_CROSSING"
  | "RMT_IFACE_MAPPING_OBLIGATION_MISSING"
  | "RMT_IFACE_TRANSPORT_DOMAIN_COLLAPSE"
  | "RMT_IFACE_CONSUMER_ROUTE_OUTSIDE"
  | "RMT_RELATION_OWNER_EVIDENCE_STALE"
  | "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"
  | "RMT_RELATION_TARGET_ENDPOINT_MISMATCH"
  | "RMT_RELATION_ASSERTION_REQUIRED";

export type InterfaceEvaluation = Readonly<{
  schema_version: "domainspec.versioned-interface-evaluation/v1";
  descriptor_id: string;
  verdict: "pass" | "reject";
  findings: readonly Readonly<{code: InterfaceFindingCode; expected: unknown; observed: unknown}>[];
  authority_effect: "none";
}>;
