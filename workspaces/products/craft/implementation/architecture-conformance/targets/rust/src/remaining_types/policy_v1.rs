#[derive(Debug, Copy, Clone, PartialEq, Eq, Hash)]
pub enum SettlementRoutingStrategyId {
    Standard,
    Expedited,
    ManualReview,
}

impl SettlementRoutingStrategyId {
    pub const fn as_wire(self) -> &'static str {
        match self {
            Self::Standard => "settlement.route.standard",
            Self::Expedited => "settlement.route.expedited",
            Self::ManualReview => "settlement.route.manual-review",
        }
    }
}

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
pub struct SettlementRoutingInput {
    pub amount_minor: i64,
    pub expedite_limit_minor: i64,
    pub expedite_requested: bool,
    pub manual_review_required: bool,
}

pub type BoundPolicy<Input, Strategy> = fn(&Input) -> Strategy;

pub const SETTLEMENT_ROUTING_POLICY: BoundPolicy<
    SettlementRoutingInput,
    SettlementRoutingStrategyId,
> = select_settlement_route;

fn select_settlement_route(
    input: &SettlementRoutingInput,
) -> SettlementRoutingStrategyId {
    if input.manual_review_required {
        SettlementRoutingStrategyId::ManualReview
    } else if input.expedite_requested
        && input.amount_minor <= input.expedite_limit_minor
    {
        SettlementRoutingStrategyId::Expedited
    } else {
        SettlementRoutingStrategyId::Standard
    }
}
