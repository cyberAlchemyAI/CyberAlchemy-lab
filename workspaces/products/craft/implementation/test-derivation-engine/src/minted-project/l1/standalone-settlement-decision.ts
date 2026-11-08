/**
 * Candidate-local R4 decision runtime. This is not the missing poker-team
 * application service and observes no writes or events.
 */
export type SettlementDecisionInput = Readonly<{
  existingTransactions: readonly Readonly<{ type: string; date: string }>[];
  periodEnd: string;
  totalAppliedMakeup: number;
  totalPayout: number;
}>;

export function decideStandaloneMakeupApplied(
  input: SettlementDecisionInput,
): boolean {
  const hasSameDateMakeupApplied = input.existingTransactions.some(
    (entry) => entry.type === "MAKEUP_APPLIED" && entry.date === input.periodEnd,
  );
  return input.totalAppliedMakeup > 0 && !hasSameDateMakeupApplied;
}
