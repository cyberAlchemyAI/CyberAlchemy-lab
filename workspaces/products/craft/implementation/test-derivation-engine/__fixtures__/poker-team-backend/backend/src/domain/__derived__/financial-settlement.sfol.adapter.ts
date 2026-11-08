import { getDealSplit } from "../deal/deal.service";
import type { Player } from "../player/player.entity";
import type { PlayerRepository } from "../player/player.repository";
import type { PlayerStatsSnapshot } from "../player-stats/player-stats.entity";
import type { PlayerStatsRepository } from "../player-stats/player-stats.repository";
import {
  computeSettlement,
} from "../settlement/settlement.service";
import type {
  SettlementEvent,
  SettlementEventHandler,
} from "../settlement/settlement.events";
import type {
  CreateTransactionInput,
  Transaction,
} from "../transaction/transaction.entity";
import type { TransactionRepository } from "../transaction/transaction.repository";
import { generateSettlementUseCase } from "../../use-cases/financial-settlement/generate-settlement";

type IntegerValue = {
  readonly tag: "integer";
  readonly value: string;
};

type StringValue = {
  readonly tag: "string";
  readonly value: string;
};

type RecordValue = {
  readonly tag: "record";
  readonly declaration_id: string;
  readonly fields: Readonly<Record<string, IntegerValue | StringValue>>;
};

type HarnessRuntime = {
  readonly signal: AbortSignal;
  openResource(resourceId: string): void;
  closeResource(resourceId: string): void;
  recordEffect(
    kind: "write" | "event",
    name: string,
    payload: RecordValue,
  ): void;
};

export type DealSplitMutation =
  | "none"
  | "comparator"
  | "returned-value";

export type PayoutTraceMutation =
  | "none"
  | "missing-write"
  | "missing-event"
  | "wrong-amount"
  | "wrong-date"
  | "wrong-order";

export type PayoutFixture = {
  readonly fixture_id: string;
  readonly inputs: {
    readonly player: {
      readonly id: string;
      readonly name: string;
      readonly email: string;
      readonly current_limit: string;
      readonly status: Player["status"];
      readonly bankroll: number;
      readonly makeup: number;
    };
    readonly stats: readonly {
      readonly id: string;
      readonly player_id: string;
      readonly stat_date: string;
      readonly hands: number;
      readonly profit: number;
      readonly rakeback: number;
      readonly rake: number;
      readonly closing_bankroll: number;
      readonly session_duration: number;
      readonly source_type: PlayerStatsSnapshot["sourceType"];
      readonly status: PlayerStatsSnapshot["status"];
    }[];
    readonly existing_transactions: readonly {
      readonly id: string;
      readonly player_id: string;
      readonly type: Transaction["type"];
      readonly amount: number;
      readonly date: string;
    }[];
    readonly request: {
      readonly player_id: string;
      readonly start_date: string;
      readonly end_date: string;
    };
  };
};

type PayoutResource = {
  readonly player: Player;
  readonly stats: PlayerStatsSnapshot[];
  readonly request: PayoutFixture["inputs"]["request"];
  readonly preTotalPayout: number;
  readonly preExistingPayoutCount: number;
  readonly writes: CreateTransactionInput[];
  readonly events: SettlementEvent[];
  readonly playerRepo: PlayerRepository;
  readonly playerStatsRepo: PlayerStatsRepository;
  readonly transactionRepo: TransactionRepository;
};

export function createDealSplitTarget(input: {
  readonly targetDigest: string;
  readonly runtimeDigest: string;
  readonly mutation?: DealSplitMutation;
}) {
  const mutation = input.mutation ?? "none";
  return {
    target_digest: input.targetDigest,
    runtime_digest: input.runtimeDigest,
    invoke(limit: unknown) {
      if (
        typeof limit !== "object" ||
        limit === null ||
        !("tag" in limit) ||
        !("value" in limit) ||
        limit?.tag !== "integer" ||
        typeof limit.value !== "string" ||
        !/^-?(?:0|[1-9][0-9]*)$/.test(limit.value)
      ) {
        throw new Error("limit_value must be an exact integer");
      }
      const value = Number.parseInt(limit.value, 10);
      const adapted =
        mutation === "comparator" && value >= 100 ? value - 1 : value;
      const actual = getDealSplit(`NL${adapted}`).player;
      const observed =
        mutation === "returned-value" ? actual + 0.1 : actual;
      return exactDecimalRational(observed);
    },
  };
}

export function createPayoutEffectAdapter(input: {
  readonly fixture: PayoutFixture;
  readonly contractId: string;
  readonly adapterDigest: string;
  readonly mutation?: PayoutTraceMutation;
}) {
  const mutation = input.mutation ?? "none";
  return {
    schema_version:
      "domainspec-sfol-effect-harness-adapter/v1" as const,
    adapter_id: `financial-settlement.P4.adapter.${mutation}`,
    adapter_digest: input.adapterDigest,
    contract_id: input.contractId,
    async setup(runtime: HarnessRuntime): Promise<PayoutResource> {
      runtime.openResource("player-repository");
      runtime.openResource("player-stats-repository");
      runtime.openResource("transaction-repository");
      return createResource(input.fixture);
    },
    async capturePreState(resource: PayoutResource) {
      return {
        total_payout: integer(resource.preTotalPayout),
        existing_payout_count: integer(
          resource.preExistingPayoutCount,
        ),
        end_date: stringValue(resource.request.end_date),
      };
    },
    async run(resource: PayoutResource, runtime: HarnessRuntime) {
      const onEvent: SettlementEventHandler = async (event) => {
        resource.events.push(event);
      };
      const useCase = generateSettlementUseCase(
        resource.playerStatsRepo,
        resource.playerRepo,
        resource.transactionRepo,
        undefined,
        onEvent,
      );
      await useCase(
        resource.request.player_id,
        resource.request.start_date,
        resource.request.end_date,
      );

      const captured = capturePayoutEffects(resource);
      for (const effect of mutateEffects(captured, mutation)) {
        runtime.recordEffect(effect.kind, effect.name, effect.payload);
      }
      return null;
    },
    async capturePostState(resource: PayoutResource) {
      return {
        payout_write_count: integer(
          resource.writes.filter((entry) => entry.type === "PAYOUT")
            .length,
        ),
        payout_event_count: integer(
          resource.events.filter(
            (entry) => entry.type === "PayoutCreated",
          ).length,
        ),
      };
    },
    async teardown(
      _resource: PayoutResource,
      runtime: HarnessRuntime,
    ) {
      runtime.closeResource("transaction-repository");
      runtime.closeResource("player-stats-repository");
      runtime.closeResource("player-repository");
    },
  };
}

function createResource(fixture: PayoutFixture): PayoutResource {
  const now = new Date("2024-01-01T00:00:00.000Z");
  const player: Player = {
    id: fixture.inputs.player.id,
    name: fixture.inputs.player.name,
    email: fixture.inputs.player.email,
    currentLimit: fixture.inputs.player.current_limit,
    status: fixture.inputs.player.status,
    bankroll: fixture.inputs.player.bankroll,
    makeup: fixture.inputs.player.makeup,
    createdAt: now,
    updatedAt: now,
  };
  const stats: PlayerStatsSnapshot[] = fixture.inputs.stats.map(
    (entry) => ({
      id: entry.id,
      playerId: entry.player_id,
      statDate: entry.stat_date,
      hands: entry.hands,
      profit: entry.profit,
      rakeback: entry.rakeback,
      rake: entry.rake,
      closingBankroll: entry.closing_bankroll,
      sessionDuration: entry.session_duration,
      sourceType: entry.source_type,
      status: entry.status,
      createdAt: now,
      updatedAt: now,
    }),
  );
  const transactions: Transaction[] =
    fixture.inputs.existing_transactions.map((entry) => ({
      id: entry.id,
      playerId: entry.player_id,
      type: entry.type,
      amount: entry.amount,
      date: entry.date,
      createdAt: now,
    }));
  const writes: CreateTransactionInput[] = [];
  const events: SettlementEvent[] = [];
  const playerRepo: PlayerRepository = {
    async create() {
      return player;
    },
    async findById(id) {
      return id === player.id ? player : null;
    },
    async findAll() {
      return [player];
    },
    async update(id, data) {
      if (id !== player.id) throw new Error("unknown player");
      Object.assign(player, data, { updatedAt: now });
      return player;
    },
  };
  const playerStatsRepo: PlayerStatsRepository = {
    async create() {
      throw new Error("not supported by contained read fixture");
    },
    async update() {
      throw new Error("not supported by contained read fixture");
    },
    async findByPlayerAndDate(playerId, statDate) {
      return (
        stats.find(
          (entry) =>
            entry.playerId === playerId &&
            entry.statDate === statDate,
        ) ?? null
      );
    },
    async findByPlayerId(playerId) {
      return {
        entries: stats.filter(
          (entry) => entry.playerId === playerId,
        ),
        nextCursor: null,
      };
    },
    async aggregateWindow() {
      throw new Error("not used by GenerateSettlement");
    },
  };
  const transactionRepo: TransactionRepository = {
    async create(data) {
      writes.push({ ...data });
      const created: Transaction = {
        ...data,
        id: `captured-${writes.length}`,
        createdAt: now,
      };
      transactions.push(created);
      return created;
    },
    async findByPlayerId(playerId) {
      return transactions.filter(
        (entry) => entry.playerId === playerId,
      );
    },
  };
  const settlement = computeSettlement({
    records: stats.map((entry) => ({
      date: entry.statDate,
      profit: entry.profit,
      rakeback: entry.rakeback,
    })),
    currentLimit: player.currentLimit,
    previousMakeup: player.makeup,
    periodStart: fixture.inputs.request.start_date,
    periodEnd: fixture.inputs.request.end_date,
    policy: player.makeupPolicy ?? undefined,
  });
  return {
    player,
    stats,
    request: fixture.inputs.request,
    preTotalPayout: settlement.totalPayout,
    preExistingPayoutCount: transactions.filter(
      (entry) =>
        entry.type === "PAYOUT" &&
        entry.date === fixture.inputs.request.end_date,
    ).length,
    writes,
    events,
    playerRepo,
    playerStatsRepo,
    transactionRepo,
  };
}

type CapturedEffect = {
  readonly kind: "write" | "event";
  readonly name: "PAYOUT" | "PayoutCreated";
  readonly payload: RecordValue;
};

function capturePayoutEffects(
  resource: PayoutResource,
): CapturedEffect[] {
  const writes: CapturedEffect[] = resource.writes
    .filter((entry) => entry.type === "PAYOUT")
    .map((entry) => ({
      kind: "write",
      name: "PAYOUT",
      payload: payoutPayload(entry.amount, entry.date),
    }));
  const events: CapturedEffect[] = resource.events
    .filter(
      (entry): entry is Extract<
        SettlementEvent,
        { type: "PayoutCreated" }
      > => entry.type === "PayoutCreated",
    )
    .map((entry) => ({
      kind: "event",
      name: "PayoutCreated",
      payload: payoutPayload(entry.amount, entry.date),
    }));
  return [...writes, ...events];
}

function mutateEffects(
  effects: readonly CapturedEffect[],
  mutation: PayoutTraceMutation,
): CapturedEffect[] {
  if (mutation === "missing-write") {
    return effects.filter((effect) => effect.kind !== "write");
  }
  if (mutation === "missing-event") {
    return effects.filter((effect) => effect.kind !== "event");
  }
  if (mutation === "wrong-order") {
    return [...effects].reverse();
  }
  return effects.map((effect) => {
    if (mutation === "wrong-amount" && effect.kind === "write") {
      const amount = effect.payload.fields.amount;
      if (amount?.tag !== "integer") {
        throw new Error("captured payout amount is not an integer");
      }
      return {
        ...effect,
        payload: payoutPayload(
          Number.parseInt(amount.value, 10) + 1,
          readDate(effect.payload),
        ),
      };
    }
    if (mutation === "wrong-date" && effect.kind === "event") {
      const amount = effect.payload.fields.amount;
      if (amount?.tag !== "integer") {
        throw new Error("captured payout amount is not an integer");
      }
      return {
        ...effect,
        payload: payoutPayload(
          Number.parseInt(amount.value, 10),
          "2099-12-31",
        ),
      };
    }
    return effect;
  });
}

function payoutPayload(amount: number, date: string): RecordValue {
  return {
    tag: "record",
    declaration_id: "financial-settlement.PayoutPayload",
    fields: {
      amount: integer(amount),
      date: stringValue(date),
    },
  };
}

function readDate(payload: RecordValue): string {
  const date = payload.fields.date;
  if (date?.tag !== "string") {
    throw new Error("captured payout date is not a string");
  }
  return date.value;
}

function integer(value: number): IntegerValue {
  if (!Number.isSafeInteger(value)) {
    throw new Error(`not an exact integer: ${value}`);
  }
  return { tag: "integer", value: String(value) };
}

function stringValue(value: string): StringValue {
  return { tag: "string", value };
}

function exactDecimalRational(value: number) {
  if (!Number.isFinite(value)) {
    throw new Error("observed deal split is not finite");
  }
  const text = value.toString();
  const [whole, fraction = ""] = text.split(".");
  const denominator = 10 ** fraction.length;
  const numerator =
    Number.parseInt(whole ?? "0", 10) * denominator +
    Math.sign(value || 1) *
      Number.parseInt(fraction.padEnd(fraction.length, "0") || "0", 10);
  const divisor = gcd(Math.abs(numerator), denominator);
  return {
    tag: "rational" as const,
    numerator: String(numerator / divisor),
    denominator: String(denominator / divisor),
  };
}

function gcd(left: number, right: number): number {
  let a = left;
  let b = right;
  while (b !== 0) {
    const next = a % b;
    a = b;
    b = next;
  }
  return a === 0 ? 1 : a;
}
