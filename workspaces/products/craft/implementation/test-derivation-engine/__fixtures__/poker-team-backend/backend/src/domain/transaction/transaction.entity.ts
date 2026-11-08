export type TransactionType =
  | "SANGRIA"
  | "REPOSICAO"
  | "PAYOUT"
  | "MAKEUP_ADJUSTMENT"
  | "MAKEUP_APPLIED";

export type Transaction = {
  id: string;
  playerId: string;
  type: TransactionType;
  amount: number;
  date: string;
  metadata?: Record<string, unknown>;
  createdAt: Date;
};

export type CreateTransactionInput = {
  playerId: string;
  type: TransactionType;
  amount: number;
  date: string;
  metadata?: Record<string, unknown>;
};
