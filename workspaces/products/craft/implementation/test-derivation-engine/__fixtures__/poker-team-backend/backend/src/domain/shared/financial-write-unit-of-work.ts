import { PlayerRepository } from "../player/player.repository";
import { TransactionRepository } from "../transaction/transaction.repository";

export type FinancialWriteContext = {
  playerRepo: PlayerRepository;
  transactionRepo: TransactionRepository;
};

export type FinancialWriteUnitOfWork = {
  runInTransaction<T>(work: (context: FinancialWriteContext) => Promise<T>): Promise<T>;
};
