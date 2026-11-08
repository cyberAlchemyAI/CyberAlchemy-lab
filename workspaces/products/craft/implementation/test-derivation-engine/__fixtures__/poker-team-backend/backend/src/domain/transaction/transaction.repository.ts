import { CreateTransactionInput, Transaction } from "./transaction.entity";

export type TransactionRepository = {
  create(data: CreateTransactionInput): Promise<Transaction>;
  findByPlayerId(playerId: string): Promise<Transaction[]>;
  createSettlementEventIfAbsent?(data: CreateTransactionInput): Promise<boolean>;
};
