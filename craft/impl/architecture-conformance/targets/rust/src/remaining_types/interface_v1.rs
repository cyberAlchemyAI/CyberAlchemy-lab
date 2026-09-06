//! Candidate-local native Rust witness for the WP-RMT-002 Interface slice.

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Binding {
    pub binding_id: String,
    pub kind: String,
    pub public_contract_id: String,
    pub internal_type_ids: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MappingObligation {
    pub binding_id: String,
    pub direction: String,
    pub mapping_id: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CompatibilityCheck {
    pub consumer_version: String,
    pub provider_version: String,
    pub accepted: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ConsumerRoute {
    pub consumer_id: String,
    pub side: String,
    pub adapter_id: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct InterfaceDescriptor {
    pub contract_id: String,
    pub exact_version: String,
    pub compatibility_direction: String,
    pub inside_boundary: String,
    pub outside_boundary: String,
    pub domain_contract_id: String,
    pub transport_adapter_id: String,
    pub exposed_bindings: Vec<Binding>,
    pub mapping_obligations: Vec<MappingObligation>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct InterfaceObservation {
    pub version: String,
    pub compatibility_direction: String,
    pub inside_boundary: String,
    pub outside_boundary: String,
    pub domain_contract_id: String,
    pub transport_adapter_id: String,
    pub exposed_bindings: Vec<Binding>,
    pub mapping_obligations: Vec<MappingObligation>,
    pub consumer_routes: Vec<ConsumerRoute>,
    pub compatibility_checks: Vec<CompatibilityCheck>,
}

fn major(version: &str) -> Option<u64> {
    let parts: Vec<_> = version.split('.').collect();
    if !(1..=3).contains(&parts.len()) || parts.iter().any(|part| part.is_empty() || !part.chars().all(|c| c.is_ascii_digit())) {
        return None;
    }
    parts[0].parse().ok()
}

pub fn evaluate_interface(descriptor: &InterfaceDescriptor, observed: &InterfaceObservation) -> Vec<&'static str> {
    let mut findings = Vec::new();
    let declared_ids: Vec<_> = descriptor.exposed_bindings.iter().map(|item| &item.binding_id).collect();
    let actual_ids: Vec<_> = observed.exposed_bindings.iter().map(|item| &item.binding_id).collect();
    let has_extra = actual_ids.iter().any(|id| !declared_ids.contains(id));
    if has_extra { findings.push("RMT_IFACE_UNDECLARED_EXPOSURE"); }
    let stripped: Vec<_> = observed.exposed_bindings.iter().map(|item| Binding {
        binding_id: item.binding_id.clone(), kind: item.kind.clone(), public_contract_id: item.public_contract_id.clone(), internal_type_ids: Vec::new(),
    }).collect();
    let expected_stripped: Vec<_> = descriptor.exposed_bindings.iter().map(|item| Binding {
        binding_id: item.binding_id.clone(), kind: item.kind.clone(), public_contract_id: item.public_contract_id.clone(), internal_type_ids: Vec::new(),
    }).collect();
    if !has_extra && stripped != expected_stripped { findings.push("RMT_IFACE_EXPOSURE_DRIFT"); }
    if observed.exposed_bindings.iter().any(|item| !item.internal_type_ids.is_empty()) { findings.push("RMT_IFACE_INTERNAL_TYPE_LEAK"); }
    let expected_major = major(&descriptor.exact_version);
    if observed.version != descriptor.exact_version || observed.compatibility_checks.iter().any(|item| {
        let provider_major = major(&item.provider_version);
        provider_major.is_none() || expected_major.is_none() || provider_major < expected_major
    }) { findings.push("RMT_IFACE_VERSION_REGRESSION"); }
    if observed.compatibility_direction != descriptor.compatibility_direction { findings.push("RMT_IFACE_COMPATIBILITY_DIRECTION_FLIP"); }
    if observed.compatibility_checks.iter().any(|item| item.accepted && major(&item.consumer_version) != major(&item.provider_version)) {
        findings.push("RMT_IFACE_COMPATIBILITY_OVERCLAIM");
    }
    if observed.inside_boundary != descriptor.inside_boundary || observed.outside_boundary != descriptor.outside_boundary
        || observed.inside_boundary == observed.outside_boundary { findings.push("RMT_IFACE_BOUNDARY_CROSSING"); }
    if descriptor.mapping_obligations.iter().any(|item| !observed.mapping_obligations.contains(item)) {
        findings.push("RMT_IFACE_MAPPING_OBLIGATION_MISSING");
    }
    if observed.domain_contract_id == observed.transport_adapter_id || observed.domain_contract_id != descriptor.domain_contract_id
        || observed.transport_adapter_id != descriptor.transport_adapter_id { findings.push("RMT_IFACE_TRANSPORT_DOMAIN_COLLAPSE"); }
    if observed.consumer_routes.iter().any(|route| route.side != "outside") { findings.push("RMT_IFACE_CONSUMER_ROUTE_OUTSIDE"); }
    findings
}
