#[path = "../../fixtures/can_settle_payout.rs"]
mod outcome_function_rule;

pub use outcome_function_rule::CanSettlePayoutInput as RuleV1Input;

pub const RULE_V1_DELEGATE_PROVIDER_ID: &str = "rust-rule-v1";
pub const RULE_V1_DELEGATE_REALIZATION_ID: &str = "rule.rust.function-v1";

pub fn evaluate_rule_v1(input: &RuleV1Input<'_>) -> bool {
    outcome_function_rule::can_settle_payout(input)
}
