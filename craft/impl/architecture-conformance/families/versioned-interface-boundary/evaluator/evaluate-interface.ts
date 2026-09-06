import type {
  InterfaceEvaluation,
  InterfaceFindingCode,
  InterfaceRelationAssertion,
  MappingObligation,
  VersionedInterfaceDescriptor,
  VersionedInterfaceObservation,
} from "../contracts/interface-contracts.js";

type Finding = InterfaceEvaluation["findings"][number];
const finding = (code: InterfaceFindingCode, expected: unknown, observed: unknown): Finding => ({code, expected, observed});
const key = (value: unknown): string => JSON.stringify(value);
const sameSet = (left: readonly unknown[], right: readonly unknown[]): boolean => {
  const a = left.map(key).sort();
  const b = right.map(key).sort();
  return a.length === new Set(a).size && b.length === new Set(b).size && key(a) === key(b);
};
const major = (version: string): number | null => {
  const match = /^(0|[1-9]\d*)(?:\.\d+){0,2}$/.exec(version);
  return match ? Number(match[1]) : null;
};

export const evaluateVersionedInterface = (
  descriptor: VersionedInterfaceDescriptor,
  observed: VersionedInterfaceObservation,
): InterfaceEvaluation => {
  const findings: Finding[] = [];
  const declaredIds = new Set(descriptor.exposed_bindings.map(({binding_id}) => binding_id));
  const observedIds = new Set(observed.exposed_bindings.map(({binding_id}) => binding_id));
  const extras = [...observedIds].filter((id) => !declaredIds.has(id));
  if (extras.length > 0) findings.push(finding("RMT_IFACE_UNDECLARED_EXPOSURE", [], extras));
  if (extras.length === 0 && !sameSet(
    descriptor.exposed_bindings,
    observed.exposed_bindings.map(({internal_type_ids: _internal, ...binding}) => binding),
  )) {
    findings.push(finding("RMT_IFACE_EXPOSURE_DRIFT", descriptor.exposed_bindings, observed.exposed_bindings));
  }
  const leaked = observed.exposed_bindings.flatMap(({binding_id, internal_type_ids}) =>
    internal_type_ids.map((type_id) => ({binding_id, type_id})),
  );
  if (leaked.length > 0) findings.push(finding("RMT_IFACE_INTERNAL_TYPE_LEAK", [], leaked));

  const expectedMajor = major(descriptor.exact_version);
  const versionRegressed = observed.compatibility_checks.some(({provider_version}) => {
    const providerMajor = major(provider_version);
    return providerMajor === null || expectedMajor === null || providerMajor < expectedMajor;
  });
  if (observed.version !== descriptor.exact_version || versionRegressed) {
    findings.push(finding("RMT_IFACE_VERSION_REGRESSION", descriptor.exact_version, {
      version: observed.version,
      provider_versions: observed.compatibility_checks.map(({provider_version}) => provider_version),
    }));
  }
  if (observed.compatibility_direction !== descriptor.compatibility_direction) {
    findings.push(finding("RMT_IFACE_COMPATIBILITY_DIRECTION_FLIP", descriptor.compatibility_direction, observed.compatibility_direction));
  }
  const overclaims = observed.compatibility_checks.filter(({consumer_version, provider_version, accepted}) =>
    accepted && major(consumer_version) !== major(provider_version),
  );
  if (overclaims.length > 0) findings.push(finding("RMT_IFACE_COMPATIBILITY_OVERCLAIM", "same-major-only", overclaims));

  if (observed.inside_boundary !== descriptor.inside_boundary
      || observed.outside_boundary !== descriptor.outside_boundary
      || observed.inside_boundary === observed.outside_boundary) {
    findings.push(finding("RMT_IFACE_BOUNDARY_CROSSING", [descriptor.inside_boundary, descriptor.outside_boundary], [observed.inside_boundary, observed.outside_boundary]));
  }
  const missingMappings = descriptor.mapping_obligations.filter((expected: MappingObligation) =>
    !observed.mapping_obligations.some((actual) => key(actual) === key(expected)),
  );
  if (missingMappings.length > 0) findings.push(finding("RMT_IFACE_MAPPING_OBLIGATION_MISSING", missingMappings, observed.mapping_obligations));
  if (observed.domain_contract_id === observed.transport_adapter_id
      || observed.domain_contract_id !== descriptor.domain_contract_id
      || observed.transport_adapter_id !== descriptor.transport_adapter_id) {
    findings.push(finding("RMT_IFACE_TRANSPORT_DOMAIN_COLLAPSE", [descriptor.domain_contract_id, descriptor.transport_adapter_id], [observed.domain_contract_id, observed.transport_adapter_id]));
  }
  const insideRoutes = observed.consumer_routes.filter(({side}) => side !== "outside");
  if (insideRoutes.length > 0) findings.push(finding("RMT_IFACE_CONSUMER_ROUTE_OUTSIDE", "outside", insideRoutes));

  return Object.freeze({
    schema_version: "domainspec.versioned-interface-evaluation/v1",
    descriptor_id: descriptor.descriptor_id,
    verdict: findings.length === 0 ? "pass" : "reject",
    findings: Object.freeze(findings),
    authority_effect: "none",
  });
};

const endpointTypes = (contractId: InterfaceRelationAssertion["contract_id"]): Readonly<{source: readonly string[]; target: readonly string[]}> =>
  contractId === "interface/exposes"
    ? {source: ["architecture.InterfaceImplementation"], target: ["architecture.OperationImplementation", "architecture.QueryImplementation"]}
    : {source: ["architecture.AdapterImplementation"], target: ["architecture.InterfaceImplementation"]};

export const evaluateInterfaceRelation = (assertion: InterfaceRelationAssertion): InterfaceEvaluation => {
  const findings: Finding[] = [];
  const allowed = endpointTypes(assertion.contract_id);
  if (assertion.owner_evidence_sha256 !== assertion.current_owner_evidence_sha256) {
    findings.push(finding("RMT_RELATION_OWNER_EVIDENCE_STALE", assertion.current_owner_evidence_sha256, assertion.owner_evidence_sha256));
  }
  if (!allowed.source.includes(assertion.source_type)) {
    findings.push(finding("RMT_RELATION_SOURCE_ENDPOINT_MISMATCH", allowed.source, assertion.source_type));
  }
  if (!allowed.target.includes(assertion.target_type)) {
    findings.push(finding("RMT_RELATION_TARGET_ENDPOINT_MISMATCH", allowed.target, assertion.target_type));
  }
  if (assertion.mode === "materialized" && !assertion.exact_assertion_id) {
    findings.push(finding("RMT_RELATION_ASSERTION_REQUIRED", "non-empty exact assertion id", assertion.exact_assertion_id));
  }
  return Object.freeze({
    schema_version: "domainspec.versioned-interface-evaluation/v1",
    descriptor_id: assertion.contract_id,
    verdict: findings.length === 0 ? "pass" : "reject",
    findings: Object.freeze(findings),
    authority_effect: "none",
  });
};
