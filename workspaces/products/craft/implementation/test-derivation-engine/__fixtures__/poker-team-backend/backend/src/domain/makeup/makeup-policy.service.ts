export type MakeupPolicy = {
  applyProfitFirst: boolean;
  applyRakebackSecond: boolean;
  playerRakebackShare: number;
};

export type ApplyMakeupPolicyInput = {
  previousDebt: number;
  totalProfit: number;
  totalRakeback: number;
  dealPlayerShare: number;
  policy?: MakeupPolicy;
};

export type ApplyMakeupPolicyResult = {
  newDebt: number;
  appliedFromProfit: number;
  appliedFromRakeback: number;
  remainingProfit: number;
  remainingRakeback: number;
  playerProfitShare: number;
  playerRakebackShare: number;
  totalPayout: number;
};

export const DEFAULT_MAKEUP_POLICY: MakeupPolicy = {
  applyProfitFirst: true,
  applyRakebackSecond: true,
  playerRakebackShare: 0.5,
};

export const validateMakeupPolicyShape = (input: {
  applyProfitFirst: unknown;
  applyRakebackSecond: unknown;
  playerRakebackShare: unknown;
}): void => {
  if (
    typeof input.applyProfitFirst !== "boolean" ||
    typeof input.applyRakebackSecond !== "boolean" ||
    typeof input.playerRakebackShare !== "number" ||
    !Number.isFinite(input.playerRakebackShare)
  ) {
    throw new Error("Invalid policy shape");
  }
};

export const resolveEffectiveMakeupPolicy = (
  override?: Partial<MakeupPolicy> | null,
): MakeupPolicy => {
  return {
    applyProfitFirst:
      typeof override?.applyProfitFirst === "boolean"
        ? override.applyProfitFirst
        : DEFAULT_MAKEUP_POLICY.applyProfitFirst,
    applyRakebackSecond:
      typeof override?.applyRakebackSecond === "boolean"
        ? override.applyRakebackSecond
        : DEFAULT_MAKEUP_POLICY.applyRakebackSecond,
    playerRakebackShare: clampRate(
      override?.playerRakebackShare ??
        DEFAULT_MAKEUP_POLICY.playerRakebackShare,
    ),
  };
};

const toMoneyInt = (value: number): number => Math.round(value);

const clampRate = (value: number): number => {
  if (!Number.isFinite(value)) {
    return 0;
  }

  return Math.max(0, Math.min(1, value));
};

export const applyMakeupPolicy = (
  input: ApplyMakeupPolicyInput,
): ApplyMakeupPolicyResult => {
  const policy = resolveEffectiveMakeupPolicy(input.policy);

  let debt = toMoneyInt(Math.max(0, input.previousDebt));
  let remainingProfit = toMoneyInt(input.totalProfit);
  let remainingRakeback = toMoneyInt(input.totalRakeback);
  const dealPlayerShare = clampRate(input.dealPlayerShare);
  let appliedFromProfit = 0;
  let appliedFromRakeback = 0;

  if (remainingProfit < 0) {
    debt = toMoneyInt(debt + Math.abs(remainingProfit));
    remainingProfit = 0;
  }

  if (remainingRakeback < 0) {
    debt = toMoneyInt(debt + Math.abs(remainingRakeback));
    remainingRakeback = 0;
  }

  if (policy.applyProfitFirst && debt > 0 && remainingProfit > 0) {
    appliedFromProfit = toMoneyInt(Math.min(remainingProfit, debt));
    debt = toMoneyInt(debt - appliedFromProfit);
    remainingProfit = toMoneyInt(remainingProfit - appliedFromProfit);
  }

  if (policy.applyRakebackSecond && debt > 0 && remainingRakeback > 0) {
    appliedFromRakeback = toMoneyInt(Math.min(remainingRakeback, debt));
    debt = toMoneyInt(debt - appliedFromRakeback);
    remainingRakeback = toMoneyInt(remainingRakeback - appliedFromRakeback);
  }

  const playerProfitShare = toMoneyInt(remainingProfit * dealPlayerShare);
  const playerRakebackShare = toMoneyInt(
    remainingRakeback * policy.playerRakebackShare,
  );
  const totalPayout = toMoneyInt(playerProfitShare + playerRakebackShare);

  return {
    newDebt: toMoneyInt(debt),
    appliedFromProfit,
    appliedFromRakeback,
    remainingProfit: toMoneyInt(remainingProfit),
    remainingRakeback: toMoneyInt(remainingRakeback),
    playerProfitShare,
    playerRakebackShare,
    totalPayout,
  };
};
