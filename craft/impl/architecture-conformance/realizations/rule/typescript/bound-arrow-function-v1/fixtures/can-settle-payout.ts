export type CanSettlePayoutInput = Readonly<{
  requestId: string;
  amount: number;
  existingSettlementId: string | null;
}>;

// Handwritten candidate fixture. The factory binds and proves this Rule; it did not generate it.
export const canSettlePayout = (input: CanSettlePayoutInput): boolean =>
  input.amount > 0 && input.existingSettlementId === null;
