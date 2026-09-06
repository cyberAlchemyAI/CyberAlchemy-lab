export const readCompleteSettlement = async (
  input: Readonly<{settlement_id: string}>,
  read: (
    target_id:
      | "settlement.read.settlement-by-id"
      | "settlement.read.payout-by-settlement",
    settlement_id: string,
  ) => Promise<Readonly<{
    settlement_status: string;
    gross_amount_minor: number;
    payout_id: string;
    payout_status: string;
  }>>,
): Promise<Readonly<{
  settlement_id: string;
  settlement_status: string;
  gross_amount_minor: number;
  payout_id: string;
  payout_status: string;
}>> => {
  const settlement = await read(
    "settlement.read.settlement-by-id",
    input.settlement_id,
  );
  const payout = await read(
    "settlement.read.payout-by-settlement",
    input.settlement_id,
  );
  return {
    settlement_id: input.settlement_id,
    settlement_status: settlement.settlement_status,
    gross_amount_minor: settlement.gross_amount_minor,
    payout_id: payout.payout_id,
    payout_status: payout.payout_status,
  };
};
