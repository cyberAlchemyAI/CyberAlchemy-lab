import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import {
  completeSettlementOperation,
  classifyOperationS1Residue,
  type CompleteSettlementOperationPorts,
} from "./operation-v1.js";

const here = dirname(fileURLToPath(import.meta.url));

const ports = (
  allowed: boolean,
  calls: string[],
  failWrite = false,
): CompleteSettlementOperationPorts => Object.freeze({
  guard: async (guardId) => {
    calls.push(`guard:${guardId}`);
    return {allowed};
  },
  read: async (targetId, settlementId) => {
    calls.push(`read:${targetId}`);
    return targetId === "settlement.read.settlement-by-id"
      ? {settlement_id: settlementId}
      : {account_id: "account-001"};
  },
  beginAtomic: async () => {
    calls.push("atomic:begin");
    return {
      write: async (targetId) => {
        calls.push(`write:${targetId}`);
        if (failWrite) throw new Error("write-failed");
      },
      commit: async () => {
        calls.push("atomic:commit");
      },
      rollback: async () => {
        calls.push("atomic:rollback");
      },
    };
  },
  externalEffect: async (targetId, event) => {
    calls.push(`effect:${targetId}`);
    calls.push(`event:${event.event_type}`);
  },
  close: async (_closure, failureCode) => {
    if (failureCode !== null) calls.push("outcome:failure");
    calls.push("continuation:close");
  },
});

describe("TypeScript complete-settlement Operation target", () => {
  it("runs guard, reads, atomic writes, commit, event, and closure in order", async () => {
    const calls: string[] = [];
    const result = await completeSettlementOperation({
      settlement_id: "settlement-001",
      expected_state_version: 7,
    }, ports(true, calls));
    calls.push("outcome:success");
    expect(calls).toEqual([
      "guard:rule.can-settle-payout",
      "read:settlement.read.settlement-by-id",
      "read:settlement.read.payout-account",
      "atomic:begin",
      "write:settlement.write.payout-record",
      "write:settlement.write.settlement-status",
      "atomic:commit",
      "effect:event-store.append.PayoutCreated",
      "event:PayoutCreated",
      "continuation:close",
      "outcome:success",
    ]);
    expect(result).toEqual({
      kind: "success",
      value: {
        settlement_id: "settlement-001",
        payout_id: "account-001:settlement-001",
        status: "committed",
      },
      failure_code: null,
      exactly_once_distributed_delivery_claimed: false,
    });
  });

  it("forms no transition and returns no success value after guard rejection", async () => {
    const calls: string[] = [];
    const result = await completeSettlementOperation({
      settlement_id: "settlement-001",
      expected_state_version: 6,
    }, ports(false, calls));
    expect(calls).toEqual([
      "guard:rule.can-settle-payout",
      "outcome:failure",
      "continuation:close",
    ]);
    expect(result).toEqual({
      kind: "failure",
      value: null,
      failure_code: "guard-rejected",
      exactly_once_distributed_delivery_claimed: false,
    });
  });

  it("rolls back a failed write and never emits an event or success value", async () => {
    const calls: string[] = [];
    const result = await completeSettlementOperation({
      settlement_id: "settlement-001",
      expected_state_version: 7,
    }, ports(true, calls, true));
    expect(calls).toContain("atomic:rollback");
    expect(calls.some((entry) => entry.startsWith("effect:"))).toBe(false);
    expect(result).toMatchObject({
      kind: "failure",
      value: null,
      failure_code: "write-failed",
    });
  });

  it("contains no ambient dependency or exactly-once delivery claim", async () => {
    const source = await readFile(resolve(here, "operation-v1.ts"), "utf8");
    expect(source).not.toMatch(/\b(?:Date|Math\.random|process|globalThis|fetch|require|eval)\b/u);
    expect(source).toContain(
      "exactly_once_distributed_delivery_claimed: false",
    );
    expect(source).not.toContain(
      "exactly_once_distributed_delivery_claimed: true",
    );
  });

  it("classifies all five S1 residues from native observations", async()=>{const expected={"before-state-write-failure.json":"RMT_S1_BEFORE_STATE_WRITE_FAILURE","between-state-and-outbox-failure.json":"RMT_S1_STATE_OUTBOX_ATOMICITY_BREACH","missing-member.json":"RMT_S1_MISSING_MEMBER","mixed-commit.json":"RMT_S1_MIXED_COMMIT","rollback-after-commit.json":"RMT_S1_ROLLBACK_AFTER_COMMIT"} as const;for(const [file,code] of Object.entries(expected)){const fixture=JSON.parse(await readFile(resolve(here,`../../families/state-changing-action/hostiles/${file}`),"utf8"));expect(classifyOperationS1Residue({...fixture.baseline,...fixture.mutation})).toBe(code);}});

  it("rejects an incoherent S1 residue rather than accepting its label",async()=>{const fixture=JSON.parse(await readFile(resolve(here,"../../families/state-changing-action/hostiles/before-state-write-failure.json"),"utf8"));expect(()=>classifyOperationS1Residue({...fixture.baseline,...fixture.mutation,transaction_aborted:false})).toThrow("RMT_OP_S1_RESIDUE_INCOHERENT");});
});
