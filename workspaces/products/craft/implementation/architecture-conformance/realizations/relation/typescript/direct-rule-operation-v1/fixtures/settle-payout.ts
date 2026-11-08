import {
  canSettlePayout,
  type CanSettlePayoutInput,
} from "../../../../rule/typescript/bound-arrow-function-v1/fixtures/can-settle-payout.js";
import {
  completeSettlement,
  type SettlementState,
} from "../../../../operation/typescript/state-event-arrow-v1/fixtures/complete-settlement.js";

type RulePort = typeof canSettlePayout;
type OperationPort = typeof completeSettlement;

// Handwritten composition fixture. Optional ports expose observation seams; defaults stay direct imports.
export const settlePayout = (
  state: SettlementState,
  input: CanSettlePayoutInput,
  rule: RulePort = canSettlePayout,
  operation: OperationPort = completeSettlement,
): boolean => {
  if (!rule(input)) return false;
  operation(state, input);
  return true;
};
