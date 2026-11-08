import { getDealSplit } from "../deal/deal.service";
import {
  applyMakeupPolicy,
  MakeupPolicy,
} from "../makeup/makeup-policy.service";

type SettlementRecord = {
  date: string;
  profit: number;
  rakeback: number;
};

type SettlementTransaction = {
  type: string;
  date: string;
};

export type ComputeSettlementInput = {
  records: SettlementRecord[];
  currentLimit: string;
  previousMakeup: number;
  periodStart: string;
  periodEnd: string;
  policy?: MakeupPolicy;
};

export type SettlementComputation = {
  totalProfit: number;
  totalRakeback: number;
  netProfit: number;
  newMakeup: number;
  appliedFromProfit: number;
  appliedFromRakeback: number;
  playerProfitShare: number;
  playerRakebackShare: number;
  totalPayout: number;
};

export const filterRecordsByPeriod = (
  records: SettlementRecord[],
  startDate: string,
  endDate: string,
): SettlementRecord[] => {
  const start = new Date(startDate);
  const end = new Date(endDate);

  return records.filter((item) => {
    const date = new Date(item.date);
    return date >= start && date <= end;
  });
};

export const computeSettlement = (
  input: ComputeSettlementInput,
): SettlementComputation => {
  const relevantRecords = filterRecordsByPeriod(
    input.records,
    input.periodStart,
    input.periodEnd,
  );

  const totalProfit = relevantRecords.reduce(
    (sum, item) => sum + item.profit,
    0,
  );
  const totalRakeback = relevantRecords.reduce(
    (sum, item) => sum + item.rakeback,
    0,
  );

  const deal = getDealSplit(input.currentLimit);
  const policyResult = applyMakeupPolicy({
    previousDebt: input.previousMakeup,
    totalProfit,
    totalRakeback,
    dealPlayerShare: deal.player,
    policy: input.policy,
  });

  return {
    totalProfit,
    totalRakeback,
    netProfit: totalProfit + totalRakeback - input.previousMakeup,
    newMakeup: policyResult.newDebt,
    appliedFromProfit: policyResult.appliedFromProfit,
    appliedFromRakeback: policyResult.appliedFromRakeback,
    playerProfitShare: policyResult.playerProfitShare,
    playerRakebackShare: policyResult.playerRakebackShare,
    totalPayout: policyResult.totalPayout,
  };
};

export type DecideSettlementSideEffectsInput = {
  existingTransactions: SettlementTransaction[];
  periodEnd: string;
  totalAppliedMakeup: number;
  totalPayout: number;
};

export type SettlementSideEffectsDecision = {
  shouldCreateMakeupAppliedEvent: boolean;
  shouldCreatePayoutEvent: boolean;
};

export const decideSettlementSideEffects = (
  input: DecideSettlementSideEffectsInput,
): SettlementSideEffectsDecision => {
  const hasExistingMakeupAppliedEvent = input.existingTransactions.some(
    (item) => item.type === "MAKEUP_APPLIED" && item.date === input.periodEnd,
  );

  const hasExistingPayoutEvent = input.existingTransactions.some(
    (item) => item.type === "PAYOUT" && item.date === input.periodEnd,
  );

  return {
    shouldCreateMakeupAppliedEvent:
      input.totalAppliedMakeup > 0 && !hasExistingMakeupAppliedEvent,
    shouldCreatePayoutEvent: input.totalPayout > 0 && !hasExistingPayoutEvent,
  };
};
