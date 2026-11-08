#[path = "../src/remaining_types/rule_v1.rs"]
mod rule_v1;

use rule_v1::{
    evaluate_rule_v1, RuleV1Input, RULE_V1_DELEGATE_PROVIDER_ID,
    RULE_V1_DELEGATE_REALIZATION_ID,
};

#[test]
fn rule_v1_delegates_all_declared_cases_as_booleans() {
    let cases = [
        (RuleV1Input {
            request_id: "request-001",
            amount: 12500,
            existing_settlement_id: None,
        }, true),
        (RuleV1Input {
            request_id: "request-002",
            amount: 12500,
            existing_settlement_id: Some("settlement-001"),
        }, false),
        (RuleV1Input {
            request_id: "request-003",
            amount: 0,
            existing_settlement_id: None,
        }, false),
    ];
    for (input, expected) in cases {
        assert_eq!(evaluate_rule_v1(&input), expected);
        assert_eq!(evaluate_rule_v1(&input), expected);
    }
}

#[test]
fn rule_v1_declares_the_existing_rust_provider_as_delegate() {
    assert_eq!(RULE_V1_DELEGATE_PROVIDER_ID, "rust-rule-v1");
    assert_eq!(
        RULE_V1_DELEGATE_REALIZATION_ID,
        "rule.rust.function-v1",
    );
}

#[test]
fn rule_v1_source_has_no_ambient_effect_or_operation_call() {
    let source = include_str!("../src/remaining_types/rule_v1.rs");
    for forbidden in [
        "std::fs", "std::net", "std::process", "std::thread", "unsafe {",
        "complete_settlement_operation(",
    ] {
        assert!(!source.contains(forbidden), "forbidden source: {forbidden}");
    }
    assert!(source.contains("outcome_function_rule::can_settle_payout(input)"));
}
