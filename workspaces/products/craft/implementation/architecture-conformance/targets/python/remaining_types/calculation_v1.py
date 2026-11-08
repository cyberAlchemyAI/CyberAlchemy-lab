def calculate_net_settlement(
    gross_amount_minor: int,
    fee_amount_minor: int,
) -> int:
    return gross_amount_minor - fee_amount_minor
