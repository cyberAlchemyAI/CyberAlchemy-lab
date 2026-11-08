import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { L1_PATHS } from "./derive.js";
import { readJson } from "./exact-ref.js";
import type { StandalonePayout, StandalonePayoutPorts, StandalonePayoutPrestate } from "./standalone-payout-effects.js";
import {
  assertStandaloneP4Contract,
  loadStandaloneP4Executor,
  P4_STANDALONE_CONTRACT,
  type StandaloneP4Contract,
  type StandaloneP4Executor,
} from "./standalone-p4-runtime.js";
import { L1Error } from "./types.js";

const repoRoot = fileURLToPath(new URL("../../../../../../..", import.meta.url));
type Fixture = {
  readonly expected_values_forbidden: true;
  readonly inputs: { readonly request: { readonly end_date: string } };
};
type SelectedPrestate = {
  readonly expected_effect_values_forbidden: true;
  readonly total_payout: number;
  readonly existing_payout_count_for_end_date: number;
  readonly end_date: string;
};
type Effect = { readonly kind: "write" | "event"; readonly name: "PAYOUT" | "PayoutCreated"; readonly payout: StandalonePayout };

function observe() {
  const effects: Effect[] = [];
  const writes: StandalonePayout[] = [];
  const events: StandalonePayout[] = [];
  const ports: StandalonePayoutPorts = {
    async writePayout(payout) {
      writes.push({ ...payout });
      effects.push({ kind: "write", name: "PAYOUT", payout: { ...payout } });
    },
    async emitPayoutCreated(payout) {
      events.push({ ...payout });
      effects.push({ kind: "event", name: "PayoutCreated", payout: { ...payout } });
    },
  };
  return { effects, writes, events, ports };
}

function assertP4Observation(
  prestate: StandalonePayoutPrestate,
  observed: ReturnType<typeof observe>,
): void {
  expect(observed.effects).toEqual([
    { kind: "write", name: "PAYOUT", payout: { amount: prestate.totalPayout, date: prestate.endDate } },
    { kind: "event", name: "PayoutCreated", payout: { amount: prestate.totalPayout, date: prestate.endDate } },
  ]);
  expect(observed.writes).toHaveLength(1);
  expect(observed.events).toHaveLength(1);
}

describe("candidate-local P4 observed-port effect slice", () => {
  it("executes the selected antecedent with one real write call then one event call", async () => {
    const run = await loadStandaloneP4Executor(repoRoot);
    const fixture = readJson<Fixture>(repoRoot, L1_PATHS.p4Fixture);
    const selected = readJson<SelectedPrestate>(repoRoot,
      "projects/domainspec-v2/development/evolvable-validation-framework/fixtures/SWU-GCP-002-P4/financial-settlement-p4-prestate.v2.json");
    expect(fixture.expected_values_forbidden).toBe(true);
    expect(selected.expected_effect_values_forbidden).toBe(true);
    expect(selected.end_date).toBe(fixture.inputs.request.end_date);
    // Explicit rule prestate; no application settlement calculation is inferred.
    const prestate = {
      totalPayout: selected.total_payout,
      existingPayoutCountForEndDate: selected.existing_payout_count_for_end_date,
      endDate: selected.end_date,
    };
    expect(prestate.totalPayout).toBeGreaterThan(0);
    expect(prestate.existingPayoutCountForEndDate).toBe(0);
    const observed = observe();
    await run(prestate, observed.ports);
    assertP4Observation(prestate, observed);
  });

  it("documents implementation-specific no-op behavior outside the P4 obligation", async () => {
    const run = await loadStandaloneP4Executor(repoRoot);
    for (const prestate of [
      { totalPayout: 0, existingPayoutCountForEndDate: 0, endDate: "2024-01-31" },
      { totalPayout: 1000, existingPayoutCountForEndDate: 1, endDate: "2024-01-31" },
    ]) {
      const observed = observe();
      await run(prestate, observed.ports);
      expect(observed.effects).toEqual([]);
    }
  });

  it("rejects malformed prestates before any port effect", async () => {
    const run = await loadStandaloneP4Executor(repoRoot);
    const valid = { totalPayout: 1000, existingPayoutCountForEndDate: 0, endDate: "2024-01-31" };
    const invalid = [
      { ...valid, totalPayout: Number.NaN },
      { ...valid, totalPayout: Number.POSITIVE_INFINITY },
      { ...valid, totalPayout: 1.5 },
      { ...valid, existingPayoutCountForEndDate: -1 },
      { ...valid, endDate: "2024-02-30" },
    ];
    for (const prestate of invalid) {
      const observed = observe();
      await expect(run(prestate, observed.ports)).rejects.toThrow("invalid P4 payout prestate");
      expect(observed.effects).toEqual([]);
    }
  });

  it("awaits the write before the event and exposes partial failure without claiming atomicity", async () => {
    const run = await loadStandaloneP4Executor(repoRoot);
    const prestate = { totalPayout: 1000, existingPayoutCountForEndDate: 0, endDate: "2024-01-31" };
    const observed = observe();
    await expect(run(prestate, {
      async writePayout() { throw new Error("write failed"); },
      emitPayoutCreated: observed.ports.emitPayoutCreated,
    })).rejects.toThrow("write failed");
    expect(observed.events).toHaveLength(0);

    await expect(run(prestate, {
      writePayout: observed.ports.writePayout,
      async emitPayoutCreated() { throw new Error("event failed"); },
    })).rejects.toThrow("event failed");
    expect(observed.writes).toHaveLength(1);
    expect(observed.events).toHaveLength(0);
  });

  it("rejects executed bad-target variants rather than only altered saved traces", async () => {
    const prestate = { totalPayout: 1000, existingPayoutCountForEndDate: 0, endDate: "2024-01-31" };
    const payout = { amount: prestate.totalPayout, date: prestate.endDate };
    const variants: StandaloneP4Executor[] = [
      async (_pre, ports) => { await ports.writePayout(payout); },
      async (_pre, ports) => { await ports.emitPayoutCreated(payout); await ports.writePayout(payout); },
      async (_pre, ports) => { await ports.writePayout({ ...payout, amount: 999 }); await ports.emitPayoutCreated(payout); },
      async (_pre, ports) => { await ports.writePayout(payout); await ports.emitPayoutCreated(payout); await ports.emitPayoutCreated(payout); },
    ];
    for (const variant of variants) {
      const observed = observe();
      await variant(prestate, observed.ports);
      expect(() => assertP4Observation(prestate, observed)).toThrow();
    }
  });

  it("ignores a target-returned manufactured trace", async () => {
    const prestate = { totalPayout: 1000, existingPayoutCountForEndDate: 0, endDate: "2024-01-31" };
    const fake = (async () => ([
      { kind: "write", name: "PAYOUT", payout: { amount: 1000, date: "2024-01-31" } },
      { kind: "event", name: "PayoutCreated", payout: { amount: 1000, date: "2024-01-31" } },
    ])) as unknown as StandaloneP4Executor;
    const observed = observe();
    await fake(prestate, observed.ports);
    expect(observed.effects).toEqual([]);
    expect(() => assertP4Observation(prestate, observed)).toThrow();
  });

  it("rejects stale or redirected selected runtime bytes", () => {
    const contract = readJson<StandaloneP4Contract>(repoRoot, P4_STANDALONE_CONTRACT);
    for (const runtimeRef of [
      { ...contract.runtime_source_ref, sha256: "0".repeat(64) },
      { ...contract.runtime_source_ref, path: L1_PATHS.p4Semantic },
    ]) {
      try {
        assertStandaloneP4Contract(repoRoot, { ...contract, runtime_source_ref: runtimeRef });
      } catch (error) {
        expect(error).toBeInstanceOf(L1Error);
        expect((error as L1Error).code).toBe("BINDING_DIGEST_STALE");
        continue;
      }
      throw new Error("expected stale or redirected runtime rejection");
    }
  });
});
