pub const SETTLEMENT_BY_ID_TARGET: &str =
    "settlement.read.settlement-by-id";
pub const PAYOUT_BY_SETTLEMENT_TARGET: &str =
    "settlement.read.payout-by-settlement";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CompleteSettlementInput<'a> {
    pub settlement_id: &'a str,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SettlementRecord {
    pub settlement_id: String,
    pub settlement_status: String,
    pub gross_amount_minor: i64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PayoutRecord {
    pub payout_id: String,
    pub payout_status: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CompleteSettlementView {
    pub settlement_id: String,
    pub settlement_status: String,
    pub gross_amount_minor: i64,
    pub payout_id: String,
    pub payout_status: String,
}

pub trait CompleteSettlementReadPort {
    fn read_settlement_by_id(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> SettlementRecord;

    fn read_payout_by_settlement(
        &mut self,
        target_id: &'static str,
        settlement_id: &str,
    ) -> PayoutRecord;
}

pub type BoundQuery = for<'a> fn(
    &CompleteSettlementInput<'a>,
    &mut dyn CompleteSettlementReadPort,
) -> CompleteSettlementView;

pub const COMPLETE_SETTLEMENT_QUERY: BoundQuery = read_complete_settlement;

fn read_complete_settlement(
    input: &CompleteSettlementInput<'_>,
    reads: &mut dyn CompleteSettlementReadPort,
) -> CompleteSettlementView {
    let settlement = reads.read_settlement_by_id(
        SETTLEMENT_BY_ID_TARGET,
        input.settlement_id,
    );
    let payout = reads.read_payout_by_settlement(
        PAYOUT_BY_SETTLEMENT_TARGET,
        input.settlement_id,
    );
    CompleteSettlementView {
        settlement_id: settlement.settlement_id,
        settlement_status: settlement.settlement_status,
        gross_amount_minor: settlement.gross_amount_minor,
        payout_id: payout.payout_id,
        payout_status: payout.payout_status,
    }
}
