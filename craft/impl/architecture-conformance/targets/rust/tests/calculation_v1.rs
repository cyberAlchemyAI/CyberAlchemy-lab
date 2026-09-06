use domainspec_architecture_conformance_rust::remaining_types::calculation_v1::{
    BoundCalculation, NetSettlementInput, NET_SETTLEMENT,
};

fn assert_bound_calculation(
    calculation: BoundCalculation<NetSettlementInput, i64>,
) -> BoundCalculation<NetSettlementInput, i64> {
    calculation
}

#[test]
fn calculation_v1_returns_the_owner_declared_values() {
    let calculation = assert_bound_calculation(NET_SETTLEMENT);
    let cases = [
        (125000, 2500, 122500),
        (5000, 0, 5000),
        (0, 0, 0),
        (1000000000, 125000, 999875000),
    ];
    for (gross_amount_minor, fee_amount_minor, expected) in cases {
        let input = NetSettlementInput {
            gross_amount_minor,
            fee_amount_minor,
        };
        assert_eq!(calculation(&input), expected);
    }
}

#[test]
fn calculation_v1_is_a_copyable_function_item_binding() {
    let first = NET_SETTLEMENT;
    let second = first;
    let input = NetSettlementInput {
        gross_amount_minor: 10,
        fee_amount_minor: 3,
    };
    assert_eq!(first(&input), 7);
    assert_eq!(second(&input), 7);
}
