# Handwritten candidate fixture. The factory binds and proves this Rule; it did not generate it.
def can_settle_payout(
    input: dict[str, str | int | None],
) -> bool:
    return input["amount"] > 0 and input["existingSettlementId"] is None
