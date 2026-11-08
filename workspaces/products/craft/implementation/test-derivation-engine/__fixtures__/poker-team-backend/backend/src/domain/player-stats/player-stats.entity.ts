export type StatsSourceType = "MANUAL" | "IMPORT" | "API";

export type StatsRecordStatus = "RECORDED" | "CORRECTED";

export type PlayerStatsSnapshot = {
  id: string;
  playerId: string;
  statDate: string; // YYYY-MM-DD
  hands: number;
  profit: number;
  rakeback: number;
  rake: number;
  closingBankroll: number;
  sessionDuration: number;
  sourceType: StatsSourceType;
  status: StatsRecordStatus;
  createdAt: Date;
  updatedAt: Date;
};

export type RecordPlayerStatsInput = {
  playerId: string;
  statDate: string;
  hands: number;
  profit: number;
  rakeback: number;
  rake: number;
  closingBankroll: number;
  sessionDuration: number;
  sourceType: StatsSourceType;
};
