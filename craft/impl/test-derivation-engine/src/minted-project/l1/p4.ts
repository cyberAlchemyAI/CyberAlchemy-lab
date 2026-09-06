import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

import { repositoryRoot } from "./exact-ref.js";
import { fail, P4_IDENTITY, type P4Effect, type P4Execution } from "./types.js";

type TaggedScalar = { readonly tag: "integer" | "string"; readonly value: string };
type TaggedRecord = {
  readonly tag: "record";
  readonly declaration_id: string;
  readonly fields: Readonly<Record<string, TaggedScalar>>;
};

export type P4FixtureDocument = {
  readonly schema_version: "evf.financial-settlement-p4-input/v1";
  readonly fixture_id: "evf.l1.financial-settlement.p4.fixture.v1";
  readonly inputs: {
    readonly player: Readonly<Record<string, unknown>>;
    readonly stats: readonly Readonly<Record<string, unknown>>[];
    readonly existing_transactions: readonly Readonly<Record<string, unknown>>[];
    readonly request: {
      readonly player_id: string;
      readonly start_date: string;
      readonly end_date: string;
    };
  };
  readonly expected_values_forbidden: true;
};

type P4Adapter = {
  setup(runtime: P4Harness): Promise<unknown>;
  capturePreState(resource: unknown): Promise<{
    readonly total_payout: TaggedScalar;
    readonly existing_payout_count: TaggedScalar;
    readonly end_date: TaggedScalar;
  }>;
  run(resource: unknown, runtime: P4Harness): Promise<unknown>;
  capturePostState(resource: unknown): Promise<{
    readonly payout_write_count: TaggedScalar;
    readonly payout_event_count: TaggedScalar;
  }>;
  teardown(resource: unknown, runtime: P4Harness): Promise<void>;
};

const adapterModuleUrl = pathToFileURL(resolve(
  repositoryRoot(),
  "validation/poker-team/backend/src/domain/__derived__/financial-settlement.sfol.adapter.ts",
)).href;
const { createPayoutEffectAdapter } = await import(adapterModuleUrl) as {
  createPayoutEffectAdapter(input: {
    readonly fixture: P4FixtureDocument;
    readonly contractId: string;
    readonly adapterDigest: string;
  }): P4Adapter;
};

function integer(value: TaggedScalar | undefined, field: string): number {
  if (!value || value.tag !== "integer" || !/^-?(?:0|[1-9][0-9]*)$/u.test(value.value)) {
    fail("OBSERVATION_TAMPERED", "execution", `${field} is not an exact integer observation`);
  }
  const parsed = Number.parseInt(value.value, 10);
  if (!Number.isSafeInteger(parsed)) {
    fail("OBSERVATION_TAMPERED", "execution", `${field} exceeds the safe integer range`);
  }
  return parsed;
}

function string(value: TaggedScalar | undefined, field: string): string {
  if (!value || value.tag !== "string" || value.value.length === 0) {
    fail("OBSERVATION_TAMPERED", "execution", `${field} is not a string observation`);
  }
  return value.value;
}

class P4Harness {
  readonly controller = new AbortController();
  readonly effects: P4Effect[] = [];
  readonly opened: string[] = [];
  readonly closed: string[] = [];

  get signal(): AbortSignal {
    return this.controller.signal;
  }

  openResource(resourceId: string): void {
    if (this.opened.includes(resourceId)) {
      fail("OBSERVATION_TAMPERED", "execution", `resource opened twice: ${resourceId}`);
    }
    this.opened.push(resourceId);
  }

  closeResource(resourceId: string): void {
    if (!this.opened.includes(resourceId) || this.closed.includes(resourceId)) {
      fail("OBSERVATION_TAMPERED", "execution", `invalid resource close: ${resourceId}`);
    }
    this.closed.push(resourceId);
  }

  recordEffect(kind: "write" | "event", name: string, payload: TaggedRecord): void {
    if (payload.tag !== "record" || payload.declaration_id !== "financial-settlement.PayoutPayload") {
      fail("OBSERVATION_TAMPERED", "execution", "effect payload is not the admitted payout record");
    }
    if (
      (kind === "write" && name !== "PAYOUT") ||
      (kind === "event" && name !== "PayoutCreated")
    ) {
      fail("P4_EFFECT_ORDER_MISMATCH", "execution", `unexpected effect identity: ${kind}:${name}`);
    }
    this.effects.push({
      sequence: this.effects.length,
      kind,
      name: name as P4Effect["name"],
      amount: integer(payload.fields.amount, "effect.amount"),
      date: string(payload.fields.date, "effect.date"),
    });
  }
}

export function validateP4Effects(
  effects: readonly P4Effect[],
  expectedAmount: number,
  expectedDate: string,
): void {
  const writes = effects.filter((effect) => effect.kind === "write");
  const events = effects.filter((effect) => effect.kind === "event");
  if (writes.length === 0) fail("P4_WRITE_MISSING", "execution", "P4 PAYOUT write is absent");
  if (events.length === 0) fail("P4_EVENT_MISSING", "execution", "P4 PayoutCreated event is absent");
  if (writes.length !== 1 || events.length !== 1 || effects.length !== 2) {
    fail("P4_EFFECT_CARDINALITY_MISMATCH", "execution", "P4 effect cardinality is not exactly one write and one event");
  }
  const write = writes[0]!;
  const event = events[0]!;
  if (
    effects[0] !== write ||
    effects[1] !== event ||
    write.sequence !== 0 ||
    event.sequence !== 1 ||
    write.name !== "PAYOUT" ||
    event.name !== "PayoutCreated"
  ) {
    fail("P4_EFFECT_ORDER_MISMATCH", "execution", "P4 effects are not ordered write then event");
  }
  if (write.amount !== expectedAmount) {
    fail("P4_WRITE_AMOUNT_MISMATCH", "execution", "P4 write amount differs from totalPayout");
  }
  if (event.amount !== expectedAmount) {
    fail("P4_EVENT_AMOUNT_MISMATCH", "execution", "P4 event amount differs from totalPayout");
  }
  if (write.date !== expectedDate) {
    fail("P4_WRITE_DATE_MISMATCH", "execution", "P4 write date differs from endDate");
  }
  if (event.date !== expectedDate) {
    fail("P4_EVENT_DATE_MISMATCH", "execution", "P4 event date differs from endDate");
  }
}

export async function runP4(fixture: P4FixtureDocument): Promise<P4Execution> {
  if (fixture.expected_values_forbidden !== true || fixture.fixture_id !== "evf.l1.financial-settlement.p4.fixture.v1") {
    fail("FIXTURE_DIGEST_STALE", "binding", "P4 fixture identity or oracle boundary is invalid");
  }
  const harness = new P4Harness();
  const adapter = createPayoutEffectAdapter({
    fixture,
    contractId: P4_IDENTITY.obligation_id,
    adapterDigest: "2936fa5a9fa3f87070d8bd030a465da76eefe2bfbef47f591aee5668ca0aa46f",
  });
  const resource = await adapter.setup(harness);
  const pre = await adapter.capturePreState(resource);
  const totalPayout = integer(pre.total_payout, "pre.total_payout");
  const existingPayoutCount = integer(pre.existing_payout_count, "pre.existing_payout_count");
  const endDate = string(pre.end_date, "pre.end_date");
  if (totalPayout <= 0 || existingPayoutCount !== 0) {
    fail("FIXTURE_DIGEST_STALE", "binding", "P4 fixture does not satisfy the selected antecedent");
  }
  let execution: Omit<P4Execution, "resources"> | undefined;
  try {
    await adapter.run(resource, harness);
    const post = await adapter.capturePostState(resource);
    const payoutWriteCount = integer(post.payout_write_count, "post.payout_write_count");
    const payoutEventCount = integer(post.payout_event_count, "post.payout_event_count");
    validateP4Effects(harness.effects, totalPayout, endDate);
    if (payoutWriteCount !== 1 || payoutEventCount !== 1) {
      fail("P4_EFFECT_CARDINALITY_MISMATCH", "execution", "post-state payout counts are not one and one");
    }
    execution = {
      schema_version: "evf.financial-settlement-p4-execution/v1",
      execution_id: P4_IDENTITY.execution_id,
      fixture_id: "evf.l1.financial-settlement.p4.fixture.v1",
      antecedent: {
        total_payout: totalPayout,
        existing_payout_count: existingPayoutCount,
        end_date: endDate,
      },
      post: { payout_write_count: payoutWriteCount, payout_event_count: payoutEventCount },
      effects: [...harness.effects],
      status: "pass",
    };
  } finally {
    await adapter.teardown(resource, harness);
  }
  if (
    harness.opened.length !== 3 ||
    harness.closed.length !== 3 ||
    [...harness.opened].sort().some((resourceId, index) => resourceId !== [...harness.closed].sort()[index])
  ) {
    fail("OBSERVATION_TAMPERED", "execution", "P4 runtime resources were not closed exactly");
  }
  return {
    ...execution!,
    resources: { opened: [...harness.opened], closed: [...harness.closed] },
  };
}

export function validateP4Execution(execution: P4Execution): void {
  validateP4Effects(
    execution.effects,
    execution.antecedent.total_payout,
    execution.antecedent.end_date,
  );
  if (execution.post.payout_write_count !== 1 || execution.post.payout_event_count !== 1) {
    fail("P4_EFFECT_CARDINALITY_MISMATCH", "execution", "P4 post-state count is invalid");
  }
}

export function mutateP4Execution(execution: P4Execution, mutantId: string): P4Execution {
  type MutableEffect = {
    sequence: number;
    kind: "write" | "event";
    name: "PAYOUT" | "PayoutCreated";
    amount: number;
    date: string;
  };
  const clone = structuredClone(execution) as unknown as Omit<P4Execution, "effects"> & { effects: MutableEffect[] };
  const write = clone.effects.find((effect) => effect.kind === "write")!;
  const event = clone.effects.find((effect) => effect.kind === "event")!;
  switch (mutantId) {
    case "P4-M01-missing-write":
      clone.effects = clone.effects.filter((effect) => effect.kind !== "write");
      break;
    case "P4-M02-missing-event":
      clone.effects = clone.effects.filter((effect) => effect.kind !== "event");
      break;
    case "P4-M03-wrong-write-amount":
      write.amount += 1;
      break;
    case "P4-M04-wrong-event-amount":
      event.amount += 1;
      break;
    case "P4-M05-wrong-write-date":
      write.date = "2099-12-30";
      break;
    case "P4-M06-wrong-event-date":
      event.date = "2099-12-31";
      break;
    case "P4-M07-event-before-write":
      clone.effects = [{ ...event, sequence: 0 }, { ...write, sequence: 1 }];
      break;
    case "P4-M08-extra-effect":
      clone.effects = [...clone.effects, { ...event, sequence: 2 }];
      break;
    default:
      fail("TARGET_BASELINE_DRIFT", "mutation", `unknown P4 observation mutant: ${mutantId}`);
  }
  return clone as P4Execution;
}
