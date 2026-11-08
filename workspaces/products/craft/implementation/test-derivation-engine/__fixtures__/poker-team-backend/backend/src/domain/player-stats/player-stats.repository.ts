import {
  PlayerStatsSnapshot,
  RecordPlayerStatsInput,
} from "./player-stats.entity";
import { PlayerStatsWindow } from "./player-stats-window.vo";

export type PlayerStatsFilters = {
  fromDate?: string;
  toDate?: string;
  limit?: number;
  cursor?: string;
};

export type PlayerStatsRepository = {
  create(
    data: RecordPlayerStatsInput & { status: string },
  ): Promise<PlayerStatsSnapshot>;
  update(
    id: string,
    data: Partial<Omit<PlayerStatsSnapshot, "id" | "createdAt">>,
  ): Promise<PlayerStatsSnapshot>;
  findByPlayerAndDate(
    playerId: string,
    statDate: string,
  ): Promise<PlayerStatsSnapshot | null>;
  findByPlayerId(
    playerId: string,
    filters?: PlayerStatsFilters,
  ): Promise<{ entries: PlayerStatsSnapshot[]; nextCursor: string | null }>;
  aggregateWindow(
    playerId: string,
    fromDate: string,
    toDate: string,
  ): Promise<
    Omit<
      PlayerStatsWindow,
      "playerId" | "fromDate" | "toDate" | "avgHandsPerDay" | "winrateBbPer100"
    >
  >;
};
