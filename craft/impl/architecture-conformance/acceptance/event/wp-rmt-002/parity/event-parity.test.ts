import {existsSync, readFileSync, readdirSync, rmdirSync} from "node:fs";
import {describe, expect, it} from "vitest";
import type {FactoryNodeProviderV1} from "../../../../factory/contracts/factory-node-provider-v1.js";
import {eventPythonV1Provider} from "../../../../factory/registry/providers/event-python-v1.js";
import {eventRustV1Provider} from "../../../../factory/registry/providers/event-rust-v1.js";
import {eventTypeScriptV1Provider} from "../../../../factory/registry/providers/event-typescript-v1.js";
import {makeSettlementEventCase, makeSettlementEventS1Case} from "../../../../targets/typescript/event-v1.js";

const cargoRoot = "projects/domainspec-v2/development/remaining-meta-types/runs/event/cargo-target";
const hostileRoot = "projects/domainspec-v2/impl/architecture-conformance/families/past-tense-event/hostiles";
const providers = [eventTypeScriptV1Provider, eventPythonV1Provider, eventRustV1Provider] as const;
const owner006 = ["after-outbox-before-publish-failure", "send-failure", "success-ack-timeout", "duplicate-reordered-delivery", "poison-occurrence", "future-version", "occurrence-reuse"] as const;
const baseSemantic = ["non-past-tense", "mutable-payload", "unstable-occurrence-id", "reused-occurrence-id", "checkpoint-missing", "checkpoint-duplicate", "publish-before-commit", "exactly-once-overclaim", "consumer-overclaim", "schema-version-drift"] as const;
const load = (name: string) => JSON.parse(readFileSync(`${hostileRoot}/${name}.json`, "utf8"));
const execute = async (provider: FactoryNodeProviderV1, eventCase: unknown) => provider.execute({raw_inputs: {event_case: JSON.stringify(eventCase)}} as never);
const rejectByAll = async (eventCase: unknown): Promise<void> => {
  const rejected = await Promise.all(providers.map(async provider => {
    try { await execute(provider, eventCase); return false; }
    catch (error) { expect(error).toBeInstanceOf(Error); return true; }
  }));
  expect(rejected).toEqual([true, true, true]);
};
const cleanupRoot = (): void => {
  if (existsSync(cargoRoot)) {
    expect(readdirSync(cargoRoot)).toEqual([]);
    rmdirSync(cargoRoot);
  }
  expect(existsSync(cargoRoot)).toBe(false);
};

describe("WP-RMT-002 Event direct-provider parity", () => {
  it("matches positive semantics across two publication attempts and rejects incoherent durable handles", async () => {
    expect(existsSync(cargoRoot), "pre-existing transient root is preserved and blocks this proof").toBe(false);
    const runAttempt = async (attempt: string) => Promise.all(providers.map(provider => execute(provider, makeSettlementEventCase(attempt))));
    const first = await runAttempt("publish:req-1:1");
    const retry = await runAttempt("publish:req-1:2");
    expect(first.map(({provider_id}) => provider_id)).toEqual(["event-typescript-v1", "event-python-v1", "event-rust-v1"]);
    for (const results of [first, retry]) {
      const outputs = results.map((result: any) => result.semantic_output);
      expect(outputs[1].portable).toEqual(outputs[0].portable);
      expect(outputs[2].portable).toEqual(outputs[0].portable);
      expect(outputs.map(({native_evidence}: any) => native_evidence.language)).toEqual(["typescript", "python", "rust"]);
      expect(new Set(outputs.map(({native_evidence}: any) => native_evidence.mechanism)).size).toBe(3);
      expect(outputs.some((output: any) => "native_sha256" in output)).toBe(false);
    }
    for (let index = 0; index < 3; index++) {
      const firstPortable = (first[index] as any).semantic_output.portable;
      const retryPortable = (retry[index] as any).semantic_output.portable;
      expect(retryPortable.occurrence_id).toBe(firstPortable.occurrence_id);
      expect(retryPortable.durable_occurrence.publication_attempt_id).not.toBe(firstPortable.durable_occurrence.publication_attempt_id);
      expect(retryPortable.distributed_exactly_once_claim).toBe(false);
    }
    const baseline = makeSettlementEventCase();
    await rejectByAll({...baseline, observation: {...baseline.observation, durable_occurrence: {...baseline.observation.durable_occurrence, occurrence_id: "other"}}});
    cleanupRoot();
  }, 120_000);

  it("closes the exact seven EVENT-006 S1 controls and rejects incoherent fault/decode/identity/retry inputs", async () => {
    expect(existsSync(cargoRoot), "pre-existing transient root is preserved and blocks this proof").toBe(false);
    for (const name of owner006) {
      const hostile = load(name);
      expect(hostile).toMatchObject({hostile_id: `s1/${name}`, hostile_class: "s1-cross-boundary", proof_owner_swu: "RMT-EVENT-006", non_noop_required: true});
      const results = await Promise.all(providers.map(provider => execute(provider, makeSettlementEventS1Case(hostile))));
      const outputs = results.map((result: any) => result.semantic_output);
      expect(outputs[1].portable, name).toEqual(outputs[0].portable);
      expect(outputs[2].portable, name).toEqual(outputs[0].portable);
      expect(outputs[0].portable).toMatchObject({result: "reject", diagnostic_code: hostile.expected_code, scenario: name, occurrence_id: "settlement:req-1", required_residue: hostile.mutation.s1_observation, distributed_exactly_once_claim: false, authority_effect: "none"});
      expect(new Set(outputs.map(({native_evidence}: any) => native_evidence.mechanism)).size).toBe(3);
    }
    const send = makeSettlementEventS1Case(load("send-failure"));
    await rejectByAll({...send, observation: {...send.observation, s1_observation: {...send.observation.s1_observation!, durable_rollback: true}}});
    const future = makeSettlementEventS1Case(load("future-version"));
    await rejectByAll({...future, observation: {...future.observation, s1_observation: {...future.observation.s1_observation!, closed_decode: false}}});
    const reuse = makeSettlementEventS1Case(load("occurrence-reuse"));
    await rejectByAll({...reuse, observation: {...reuse.observation, s1_observation: {...reuse.observation.s1_observation!, reuse_rejected: false}}});
    const retry = makeSettlementEventS1Case(load("non-idempotent-retry"));
    await rejectByAll({...retry, observation: {...retry.observation, s1_observation: {...retry.observation.s1_observation!, retry_occurrence_id: "settlement:req-1", consumer_effect_count: 1}}});
    cleanupRoot();
  }, 120_000);

  it("replays all ten base semantic controls through every provider with stable codes", async () => {
    expect(existsSync(cargoRoot)).toBe(false);
    for (const name of baseSemantic) {
      const hostile = load(name);
      const baseline = makeSettlementEventCase();
      const eventCase = {...baseline, observation: {...baseline.observation, ...hostile.mutation}};
      const messages = await Promise.all(providers.map(async provider => {
        try { await execute(provider, eventCase); return "accepted"; }
        catch (error) { return error instanceof Error ? error.message : String(error); }
      }));
      expect(messages.every(message => message.includes(hostile.expected_code)), hostile.hostile_id).toBe(true);
    }
    expect(existsSync(cargoRoot)).toBe(false);
  });
});
