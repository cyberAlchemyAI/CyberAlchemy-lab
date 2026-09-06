#[path = "../src/remaining_types/interface_v1.rs"]
mod interface_v1;
use interface_v1::*;

fn binding(id: &str, kind: &str, contract: &str) -> Binding {
    Binding {binding_id:id.into(),kind:kind.into(),public_contract_id:contract.into(),internal_type_ids:Vec::new()}
}
fn mapping(id: &str, direction: &str, map: &str) -> MappingObligation {
    MappingObligation {binding_id:id.into(),direction:direction.into(),mapping_id:map.into()}
}
fn baseline() -> (InterfaceDescriptor, InterfaceObservation) {
    let bindings = vec![binding("completeSettlement","Operation","CompleteSettlement/v1"),binding("findSettlement","Query","FindSettlement/v1")];
    let mappings = vec![mapping("completeSettlement","request","CompleteSettlementRequestMap/v1"),mapping("completeSettlement","response","SettlementResponseMap/v1"),mapping("findSettlement","response","SettlementResponseMap/v1")];
    let descriptor = InterfaceDescriptor {
        contract_id:"SettlementPort".into(),exact_version:"1.2.0".into(),compatibility_direction:"consumer-to-provider".into(),
        inside_boundary:"settlement-domain".into(),outside_boundary:"settlement-consumers".into(),domain_contract_id:"SettlementPort/domain-v1".into(),
        transport_adapter_id:"SettlementHttpAdapter/v1".into(),exposed_bindings:bindings.clone(),mapping_obligations:mappings.clone(),
    };
    let observation = InterfaceObservation {
        version:"1.2.0".into(),compatibility_direction:"consumer-to-provider".into(),inside_boundary:"settlement-domain".into(),outside_boundary:"settlement-consumers".into(),
        domain_contract_id:"SettlementPort/domain-v1".into(),transport_adapter_id:"SettlementHttpAdapter/v1".into(),exposed_bindings:bindings,mapping_obligations:mappings,
        consumer_routes:vec![ConsumerRoute{consumer_id:"settlement-http-client".into(),side:"outside".into(),adapter_id:"SettlementHttpAdapter/v1".into()}],
        compatibility_checks:vec![
            CompatibilityCheck{consumer_version:"1.0.0".into(),provider_version:"1.2.0".into(),accepted:true},
            CompatibilityCheck{consumer_version:"2.0.0".into(),provider_version:"1.2.0".into(),accepted:false},
        ],
    };
    (descriptor, observation)
}

#[test]
fn native_struct_boundary_passes() {
    let (descriptor, observation) = baseline();
    assert_eq!(evaluate_interface(&descriptor, &observation), Vec::<&str>::new());
    assert_ne!(descriptor.domain_contract_id, descriptor.transport_adapter_id);
}

#[test]
fn kills_all_ten_semantic_controls_as_singletons() {
    let (descriptor, baseline) = baseline();
    let mut cases: Vec<(&str, InterfaceObservation)> = Vec::new();
    let mut value = baseline.clone(); value.exposed_bindings.push(binding("adminDelete","Operation","AdminDelete/v1")); cases.push(("RMT_IFACE_UNDECLARED_EXPOSURE",value));
    let mut value = baseline.clone(); value.exposed_bindings.pop(); cases.push(("RMT_IFACE_EXPOSURE_DRIFT",value));
    let mut value = baseline.clone(); value.exposed_bindings[0].internal_type_ids.push("SettlementAggregateInternal".into()); cases.push(("RMT_IFACE_INTERNAL_TYPE_LEAK",value));
    let mut value = baseline.clone(); value.version="0.9.0".into(); value.compatibility_checks=vec![CompatibilityCheck{consumer_version:"0.9.0".into(),provider_version:"0.9.0".into(),accepted:true}]; cases.push(("RMT_IFACE_VERSION_REGRESSION",value));
    let mut value = baseline.clone(); value.compatibility_checks[1].accepted=true; cases.push(("RMT_IFACE_COMPATIBILITY_OVERCLAIM",value));
    let mut value = baseline.clone(); value.compatibility_direction="provider-to-consumer".into(); cases.push(("RMT_IFACE_COMPATIBILITY_DIRECTION_FLIP",value));
    let mut value = baseline.clone(); std::mem::swap(&mut value.inside_boundary,&mut value.outside_boundary); cases.push(("RMT_IFACE_BOUNDARY_CROSSING",value));
    let mut value = baseline.clone(); value.mapping_obligations.pop(); cases.push(("RMT_IFACE_MAPPING_OBLIGATION_MISSING",value));
    let mut value = baseline.clone(); value.transport_adapter_id=value.domain_contract_id.clone(); cases.push(("RMT_IFACE_TRANSPORT_DOMAIN_COLLAPSE",value));
    let mut value = baseline.clone(); value.consumer_routes[0].side="inside".into(); cases.push(("RMT_IFACE_CONSUMER_ROUTE_OUTSIDE",value));
    assert_eq!(cases.len(),10);
    for (expected, observed) in cases { assert_eq!(evaluate_interface(&descriptor,&observed),vec![expected],"{expected}"); }
}
