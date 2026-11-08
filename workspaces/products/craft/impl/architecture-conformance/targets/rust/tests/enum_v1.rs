use domainspec_architecture_conformance_rust::remaining_types::enum_v1::{
    emit_shipment_priority, parse_shipment_priority, shipment_priority_member_id,
    ShipmentPriority, SHIPMENT_PRIORITY_ENUM_ID, UNKNOWN_WIRE_ERROR_CODE,
};
use std::collections::HashSet;
use std::fmt::Debug;
use std::hash::Hash;

fn assert_required_traits<T: Debug + Copy + Clone + PartialEq + Eq + Hash>() {}

fn exhaustive_native_key(value: ShipmentPriority) -> &'static str {
    match value {
        ShipmentPriority::Deferred => "Deferred",
        ShipmentPriority::Expedited => "Expedited",
        ShipmentPriority::Normal => "Normal",
    }
}

#[test]
fn enum_v1_has_exact_unit_variants_and_required_traits() {
    assert_required_traits::<ShipmentPriority>();
    let values = [
        ShipmentPriority::Deferred,
        ShipmentPriority::Expedited,
        ShipmentPriority::Normal,
    ];
    assert_eq!(
        values.map(exhaustive_native_key),
        ["Deferred", "Expedited", "Normal"]
    );
    assert_eq!(HashSet::from(values).len(), 3);
}

#[test]
fn enum_v1_emits_and_parses_the_owner_bound_mapping() {
    let cases = [
        (
            ShipmentPriority::Deferred,
            "priority.deferred",
            "deferred",
        ),
        (
            ShipmentPriority::Expedited,
            "priority.expedited",
            "expedited",
        ),
        (ShipmentPriority::Normal, "priority.normal", "normal"),
    ];
    for (member, member_id, wire_value) in cases {
        assert_eq!(shipment_priority_member_id(member), member_id);
        assert_eq!(emit_shipment_priority(member), wire_value);
        assert_eq!(parse_shipment_priority(wire_value), Ok(member));
    }
}

#[test]
fn enum_v1_returns_a_structured_unknown_wire_error() {
    let wire_value = "__unknown_shipment_priority__";
    let error = parse_shipment_priority(wire_value).expect_err("unknown wire must fail");
    assert_eq!(error.code, UNKNOWN_WIRE_ERROR_CODE);
    assert_eq!(error.enum_id, SHIPMENT_PRIORITY_ENUM_ID);
    assert_eq!(error.wire_value, wire_value);
}
