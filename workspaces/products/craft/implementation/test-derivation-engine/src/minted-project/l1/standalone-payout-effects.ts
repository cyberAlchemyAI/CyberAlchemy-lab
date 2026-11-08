export type StandalonePayoutPrestate = Readonly<{
  totalPayout: number;
  existingPayoutCountForEndDate: number;
  endDate: string;
}>;

export type StandalonePayout = Readonly<{ amount: number; date: string }>;

export type StandalonePayoutPorts = Readonly<{
  writePayout(payout: StandalonePayout): Promise<void>;
  emitPayoutCreated(payout: StandalonePayout): Promise<void>;
}>;

/** Candidate P4 rule slice. The ports, not this function, own observations. */
export async function executeStandalonePayoutEffects(
  prestate: StandalonePayoutPrestate,
  ports: StandalonePayoutPorts,
): Promise<void> {
  if (!Number.isSafeInteger(prestate.totalPayout) ||
      !Number.isSafeInteger(prestate.existingPayoutCountForEndDate) ||
      prestate.existingPayoutCountForEndDate < 0 ||
      !/^\d{4}-\d{2}-\d{2}$/.test(prestate.endDate) ||
      Number.isNaN(Date.parse(`${prestate.endDate}T00:00:00.000Z`)) ||
      new Date(`${prestate.endDate}T00:00:00.000Z`).toISOString().slice(0, 10) !== prestate.endDate) {
    throw new TypeError("invalid P4 payout prestate");
  }
  if (prestate.totalPayout <= 0 || prestate.existingPayoutCountForEndDate !== 0) return;
  const payout = { amount: prestate.totalPayout, date: prestate.endDate };
  await ports.writePayout(payout);
  await ports.emitPayoutCreated(payout);
}
