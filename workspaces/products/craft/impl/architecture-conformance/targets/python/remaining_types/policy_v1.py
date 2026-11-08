from typing import Literal, TypedDict


SettlementRoutingStrategyId = Literal[
    "settlement.route.standard",
    "settlement.route.expedited",
    "settlement.route.manual-review",
]


class SettlementRoutingInput(TypedDict):
    amount_minor: int
    expedite_limit_minor: int
    expedite_requested: bool
    manual_review_required: bool


def select_settlement_route(
    input_data: SettlementRoutingInput,
) -> SettlementRoutingStrategyId:
    return (
        "settlement.route.manual-review"
        if input_data["manual_review_required"]
        else "settlement.route.expedited"
        if input_data["expedite_requested"]
        and input_data["amount_minor"] <= input_data["expedite_limit_minor"]
        else "settlement.route.standard"
    )
