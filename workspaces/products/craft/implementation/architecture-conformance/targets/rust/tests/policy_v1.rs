use domainspec_architecture_conformance_rust::remaining_types::policy_v1::{
    BoundPolicy, SettlementRoutingInput, SettlementRoutingStrategyId,
    SETTLEMENT_ROUTING_POLICY,
};

fn assert_bound_policy(
    policy: BoundPolicy<SettlementRoutingInput, SettlementRoutingStrategyId>,
) -> BoundPolicy<SettlementRoutingInput, SettlementRoutingStrategyId> {
    policy
}

#[test]
fn policy_v1_returns_the_owner_declared_strategy_identities() {
    let policy = assert_bound_policy(SETTLEMENT_ROUTING_POLICY);
    let cases = [
        (5000, 10000, false, false, "settlement.route.standard"),
        (5000, 10000, true, false, "settlement.route.expedited"),
        (5000, 10000, true, true, "settlement.route.manual-review"),
        (15000, 10000, true, false, "settlement.route.standard"),
        (5000, 4000, true, false, "settlement.route.standard"),
    ];
    for (amount, limit, expedite, manual, expected) in cases {
        let selected = policy(&SettlementRoutingInput {
            amount_minor: amount,
            expedite_limit_minor: limit,
            expedite_requested: expedite,
            manual_review_required: manual,
        });
        assert_eq!(selected.as_wire(), expected);
    }
}

#[test]
fn policy_v1_uses_a_copyable_typed_function_item() {
    let first = SETTLEMENT_ROUTING_POLICY;
    let second = first;
    let input = SettlementRoutingInput {
        amount_minor: 5000,
        expedite_limit_minor: 10000,
        expedite_requested: true,
        manual_review_required: false,
    };
    assert_eq!(first(&input), SettlementRoutingStrategyId::Expedited);
    assert_eq!(second(&input), SettlementRoutingStrategyId::Expedited);
}
