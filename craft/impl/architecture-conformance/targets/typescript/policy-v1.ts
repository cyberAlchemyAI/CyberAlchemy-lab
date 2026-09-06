type SettlementRoutingStrategyId =
  | "settlement.route.standard"
  | "settlement.route.expedited"
  | "settlement.route.manual-review";

export const selectSettlementRoute = (
  input: Readonly<{
    amount_minor: number;
    expedite_limit_minor: number;
    expedite_requested: boolean;
    manual_review_required: boolean;
  }>,
): SettlementRoutingStrategyId => input.manual_review_required
  ? "settlement.route.manual-review"
  : input.expedite_requested && input.amount_minor <= input.expedite_limit_minor
    ? "settlement.route.expedited"
    : "settlement.route.standard";
