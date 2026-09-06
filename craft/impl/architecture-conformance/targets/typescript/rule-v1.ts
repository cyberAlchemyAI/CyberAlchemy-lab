import {
  canSettlePayout,
  type CanSettlePayoutInput,
} from "../../realizations/rule/typescript/bound-arrow-function-v1/fixtures/can-settle-payout.js";

export type RuleV1Input = CanSettlePayoutInput;

export const RULE_V1_DELEGATE = Object.freeze({
  rule_id: "can-settle-payout",
  realization_id: "rule.typescript.bound-arrow-function-v1",
  provider_id: "typescript-rule-v1",
  authority_effect: "none",
} as const);

export const evaluateRuleV1 = (input: RuleV1Input): boolean =>
  canSettlePayout(input);
