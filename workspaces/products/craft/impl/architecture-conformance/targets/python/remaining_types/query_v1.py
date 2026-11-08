def read_complete_settlement(input_data, read):
    settlement = read(
        "settlement.read.settlement-by-id",
        input_data["settlement_id"],
    )
    payout = read(
        "settlement.read.payout-by-settlement",
        input_data["settlement_id"],
    )
    return {
        "settlement_id": input_data["settlement_id"],
        "settlement_status": settlement["settlement_status"],
        "gross_amount_minor": settlement["gross_amount_minor"],
        "payout_id": payout["payout_id"],
        "payout_status": payout["payout_status"],
    }
