export type PlayerStatsWindow = {
  playerId: string;
  fromDate: string;
  toDate: string;
  totalHands: number;
  totalProfit: number;
  totalRakeback: number;
  totalRake: number;
  totalSessionMinutes: number;
  sessionCount: number;
  avgHandsPerDay: number;
  winrateBbPer100: number | null;
};
