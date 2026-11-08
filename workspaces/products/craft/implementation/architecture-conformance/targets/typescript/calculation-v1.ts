export const calculateNetSettlement = (
  input: Readonly<{
    gross_amount_minor: number;
    fee_amount_minor: number;
  }>,
): number => input.gross_amount_minor - input.fee_amount_minor;
