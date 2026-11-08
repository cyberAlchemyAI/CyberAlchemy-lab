export type SettlementGeneratedEvent = {
  type: "SettlementGenerated";
  playerId: string;
  periodStart: string;
  periodEnd: string;
  totalProfit: number;
  totalRakeback: number;
  previousMakeup: number;
  newMakeup: number;
  totalPayout: number;
  occurredAt: Date;
};

export type PayoutCreatedEvent = {
  type: "PayoutCreated";
  playerId: string;
  date: string;
  amount: number;
  occurredAt: Date;
};

export type SettlementEvent = SettlementGeneratedEvent | PayoutCreatedEvent;

export type SettlementEventHandler = (
  event: SettlementEvent,
) => void | Promise<void>;
