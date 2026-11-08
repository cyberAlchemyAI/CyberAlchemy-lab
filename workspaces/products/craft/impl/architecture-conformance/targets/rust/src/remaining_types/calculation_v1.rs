#[derive(Debug, Copy, Clone, PartialEq, Eq)]
pub struct NetSettlementInput {
    pub gross_amount_minor: i64,
    pub fee_amount_minor: i64,
}

pub type BoundCalculation<Input, Output> = fn(&Input) -> Output;

pub const NET_SETTLEMENT: BoundCalculation<NetSettlementInput, i64> =
    calculate_net_settlement;

fn calculate_net_settlement(input: &NetSettlementInput) -> i64 {
    input.gross_amount_minor - input.fee_amount_minor
}
