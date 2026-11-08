export type PlayerStatus = "ACTIVE" | "INACTIVE" | "OBSERVATION";

export type PlayerMakeupPolicy = {
  applyProfitFirst: boolean;
  applyRakebackSecond: boolean;
  playerRakebackShare: number;
};

export type Player = {
  id: string;
  principalId?: string | null;
  name: string;
  email: string;
  currentLimit: string;
  status: PlayerStatus;
  bankroll: number;
  makeup: number;
  makeupPolicy?: PlayerMakeupPolicy | null;
  createdAt: Date;
  updatedAt: Date;
};

export type CreatePlayerInput = {
  name: string;
  email: string;
  currentLimit: string;
  principalId?: string;
  initialBankroll?: number;
  makeupPolicy?: PlayerMakeupPolicy;
};
