export type SettlementState = {
  payouts: string[];
  events: string[];
};

export type CompleteSettlementInput = Readonly<{
  requestId: string;
  amount: number;
}>;

// Handwritten candidate fixture. The factory binds and proves this Operation; it did not generate it.
export const completeSettlement = (
  state: SettlementState,
  input: CompleteSettlementInput,
): void => {
  state.payouts.push(input.requestId);
  state.events.push(`PayoutCreated:${input.requestId}`);
};
