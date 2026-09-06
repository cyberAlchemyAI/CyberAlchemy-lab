// Handwritten candidate fixture. The factory binds and proves this Rule; it did not generate it.
pub struct CanSettlePayoutInput<'a> {
    pub request_id: &'a str,
    pub amount: i64,
    pub existing_settlement_id: Option<&'a str>,
}

pub fn can_settle_payout(input: &CanSettlePayoutInput<'_>) -> bool {
    input.amount > 0 && input.existing_settlement_id == None
}
