export type SettlementRequest = Readonly<{requestId: string; playerId: string; amount: number}>;
export type SettlementRecord = Readonly<{id: string; playerId: string; amount: number}>;
export type SettlementResponse = Readonly<{settlementId: string; playerId: string; amount: number}>;
export type SettlementCreated = Readonly<{
  type: "SettlementCreated";
  version: "1";
  occurrenceId: string;
  settlementId: string;
  playerId: string;
  amount: number;
}>;

export const mapSettlementResponse = (record: SettlementRecord): SettlementResponse => Object.freeze({
  settlementId: record.id,
  playerId: record.playerId,
  amount: record.amount,
});

export type SettlementPortV1 = Readonly<{
  completeSettlement: (request: SettlementRequest) => Promise<SettlementResponse>;
  findSettlement: (requestId: string) => Promise<SettlementResponse | null>;
}>;

export const settlementPortV1Members = Object.freeze([
  "Operation:completeSettlement",
  "Query:findSettlement",
] as const);

export const makeSettlementCreated = (record: SettlementRecord): SettlementCreated => Object.freeze({
  type: "SettlementCreated",
  version: "1",
  occurrenceId: `settlement:${record.id}`,
  settlementId: record.id,
  playerId: record.playerId,
  amount: record.amount,
});

export const completeSettlement = async (input: Readonly<{
  request: SettlementRequest;
  existingSettlementId: string | null;
  commitAtomically: (record: SettlementRecord, event: SettlementCreated) => Promise<void>;
}>): Promise<Readonly<{outcome: "settlement-completed"; response: SettlementResponse; event: SettlementCreated}>> => {
  const allowed = input.request.amount > 0 && input.existingSettlementId === null;
  if (!allowed) throw new Error("SETTLEMENT_REJECTED");
  const record = Object.freeze({id: input.request.requestId, playerId: input.request.playerId, amount: input.request.amount});
  const event = makeSettlementCreated(record);
  await input.commitAtomically(record, event);
  return Object.freeze({outcome: "settlement-completed", response: mapSettlementResponse(record), event});
};
