export type SettlementResult = {
  playerId: string;
  periodStart: string;
  periodEnd: string;
  totalProfit: number;
  totalRakeback: number;
  netProfit: number;
  previousMakeup: number;
  newMakeup: number;
  playerProfitShare: number;
  playerRakebackShare: number;
  totalPayout: number;
};
