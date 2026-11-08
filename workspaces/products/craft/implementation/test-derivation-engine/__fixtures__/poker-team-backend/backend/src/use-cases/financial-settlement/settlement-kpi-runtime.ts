let previewInvocations = 0;
let settlementInvocations = 0;

const currentRatio = (): number => {
  if (settlementInvocations === 0) {
    return 1;
  }

  return previewInvocations / settlementInvocations;
};

export const markSettlementPreviewInvocation = (): number => {
  previewInvocations += 1;
  return currentRatio();
};

export const markSettlementInvocation = (): number => {
  settlementInvocations += 1;
  return currentRatio();
};
