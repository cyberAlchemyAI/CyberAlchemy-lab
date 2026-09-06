import {readdirSync, readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {describe, expect, it} from "vitest";
import type {EventRelationAssertion, EventS1Observation, PastTenseEventObservation} from "../contracts/event-contracts.js";
import {decodePastTenseEventObservation} from "../decoder/decode-event-observation.js";
import {eventRelationAssertion, settlementEventDescriptor, settlementEventObservation} from "../fixtures/settlement-event.js";
import {applyEventObservationHostile, applyEventRelationHostile, type EventHostileMutation} from "../mutations/apply-event-hostile.js";
import {evaluateEventRelation, evaluatePastTenseEvent} from "./evaluate-event.js";

type BaseExpected = readonly [string, "type-semantic" | "rel-a-evidence", string];
type S1Expected = readonly [string, "s1-cross-boundary", string, "RMT-EVENT-002", "RMT-EVENT-006" | "RMT-EVENT-007", string, string, string];
type Hostile = EventHostileMutation & Readonly<{
  expected_code: string;
  fixture_owner_swu?: string;
  proof_owner_swu?: string;
  category?: string;
  required_observation?: string;
  required_outcome?: string;
  non_noop_required?: boolean;
}>;

const baseMap = Object.freeze({
  "non-past-tense.json": ["event/non-past-tense", "type-semantic", "RMT_EVENT_NON_PAST_TENSE"],
  "mutable-payload.json": ["event/mutable-payload", "type-semantic", "RMT_EVENT_MUTABLE_PAYLOAD"],
  "unstable-occurrence-id.json": ["event/unstable-occurrence-id", "type-semantic", "RMT_EVENT_UNSTABLE_OCCURRENCE_ID"],
  "reused-occurrence-id.json": ["event/reused-occurrence-id", "type-semantic", "RMT_EVENT_REUSED_OCCURRENCE_ID"],
  "checkpoint-missing.json": ["event/checkpoint-missing", "type-semantic", "RMT_EVENT_CHECKPOINT_MISSING"],
  "checkpoint-duplicate.json": ["event/checkpoint-duplicate", "type-semantic", "RMT_EVENT_CHECKPOINT_DUPLICATE"],
  "publish-before-commit.json": ["event/publish-before-commit", "type-semantic", "RMT_EVENT_PUBLISH_BEFORE_COMMIT"],
  "exactly-once-overclaim.json": ["event/exactly-once-overclaim", "type-semantic", "RMT_EVENT_EXACTLY_ONCE_OVERCLAIM"],
  "consumer-overclaim.json": ["event/consumer-overclaim", "type-semantic", "RMT_EVENT_CONSUMER_OVERCLAIM"],
  "schema-version-drift.json": ["event/schema-version-drift", "type-semantic", "RMT_EVENT_SCHEMA_VERSION_DRIFT"],
  "relation-owner-evidence-stale.json": ["event/relation-owner-evidence-stale", "rel-a-evidence", "RMT_RELATION_OWNER_EVIDENCE_STALE"],
  "relation-source-endpoint-mismatch.json": ["event/relation-source-endpoint-mismatch", "rel-a-evidence", "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH"],
  "relation-target-endpoint-mismatch.json": ["event/relation-target-endpoint-mismatch", "rel-a-evidence", "RMT_RELATION_TARGET_ENDPOINT_MISMATCH"],
  "materialized-without-exact-assertion.json": ["event/materialized-without-exact-assertion", "rel-a-evidence", "RMT_RELATION_ASSERTION_REQUIRED"],
} satisfies Readonly<Record<string, BaseExpected>>);

const s1Map = Object.freeze({
  "after-outbox-before-publish-failure.json": ["s1/after-outbox-before-publish-failure", "s1-cross-boundary", "RMT_S1_AFTER_OUTBOX_BEFORE_PUBLISH_FAILURE", "RMT-EVENT-002", "RMT-EVENT-006", "fault-matrix:S1-F03", "committed outbox occurrence and absent publication attempt", "durable state and occurrence preserved"],
  "send-failure.json": ["s1/send-failure", "s1-cross-boundary", "RMT_S1_SEND_FAILURE", "RMT-EVENT-002", "RMT-EVENT-006", "fault-matrix:S1-F04", "failed publication attempt for committed occurrence", "retry same occurrence without durable rollback"],
  "success-ack-timeout.json": ["s1/success-ack-timeout", "s1-cross-boundary", "RMT_S1_ACKNOWLEDGEMENT_AMBIGUOUS", "RMT-EVENT-002", "RMT-EVENT-006", "fault-matrix:S1-F05", "successful send with ambiguous acknowledgement", "idempotent retry or reconcile using same occurrence"],
  "duplicate-reordered-delivery.json": ["s1/duplicate-reordered-delivery", "s1-cross-boundary", "RMT_S1_DUPLICATE_REORDERED_DELIVERY", "RMT-EVENT-002", "RMT-EVENT-006", "fault-matrix:S1-F06", "duplicate or reordered delivery trace", "idempotent consume or stable rejection without history rewrite"],
  "poison-occurrence.json": ["s1/poison-occurrence", "s1-cross-boundary", "RMT_S1_POISON_OCCURRENCE", "RMT-EVENT-002", "RMT-EVENT-006", "fault-matrix:S1-F07", "unpublishable or unconsumable committed occurrence", "quarantine or forward handling with durable history preserved"],
  "recovery-replay.json": ["s1/recovery-replay", "s1-cross-boundary", "RMT_S1_RECOVERY_REPLAY_MISMATCH", "RMT-EVENT-002", "RMT-EVENT-007", "fault-matrix:S1-F08", "fresh-process restart and outbox recovery", "same committed occurrence identity and outcome"],
  "future-version.json": ["s1/future-version", "s1-cross-boundary", "RMT_S1_FUTURE_VERSION", "RMT-EVENT-002", "RMT-EVENT-006", "decode-contract", "future occurrence schema version", "closed rejection with stable code"],
  "occurrence-reuse.json": ["s1/occurrence-reuse", "s1-cross-boundary", "RMT_S1_OCCURRENCE_REUSE", "RMT-EVENT-002", "RMT-EVENT-006", "identity-contract", "same occurrence identity for a distinct durable fact", "reject identity reuse"],
  "non-idempotent-retry.json": ["s1/non-idempotent-retry", "s1-cross-boundary", "RMT_S1_NON_IDEMPOTENT_RETRY", "RMT-EVENT-002", "RMT-EVENT-007", "retry-contract", "retry changes occurrence identity or duplicates consumer effect", "reject non-idempotent retry"],
} satisfies Readonly<Record<string, S1Expected>>);

const hostileCataloguePath = "projects/domainspec-v2/development/refinement-runs/20260814T193343Z-active-meta-type-implementations/refreshes/20260821T023424Z-wp-rmt-002-integrated-reuse-refresh/staged/HOSTILE-CATALOGUE.json";
const hostileDir = fileURLToPath(new URL("../hostiles/", import.meta.url));
const hostileFiles = [...Object.keys(baseMap), ...Object.keys(s1Map)].sort();
const load = (filename: string): Hostile => JSON.parse(readFileSync(fileURLToPath(new URL(`../hostiles/${filename}`, import.meta.url)), "utf8")) as Hostile;
const exactS1FixtureKeys = ["hostile_id", "hostile_class", "expected_code", "fixture_owner_swu", "proof_owner_swu", "category", "required_observation", "required_outcome", "non_noop_required", "mutation"].sort();
const assertExactS1FixtureShape = (value: Hostile): void => {
  if (JSON.stringify(Object.keys(value).sort()) !== JSON.stringify(exactS1FixtureKeys) || value.non_noop_required !== true) throw new Error("RMT_EVENT_S1_FIXTURE_SHAPE_INVALID");
};

const assertRequiredResidue = (s1: EventS1Observation): void => {
  switch (s1.scenario) {
    case "after-outbox-before-publish-failure": expect(s1).toMatchObject({transaction_committed: true, state_preserved: true, outbox_occurrence_present: true, publication_attempted: false, publication_attempt_id: null}); break;
    case "send-failure": expect(s1).toMatchObject({transaction_committed: true, state_preserved: true, outbox_occurrence_present: true, publication_attempted: true, publication_succeeded: false, retry_occurrence_id: s1.occurrence_id, durable_rollback: false}); break;
    case "success-ack-timeout": expect(s1).toMatchObject({transaction_committed: true, state_preserved: true, publication_succeeded: true, acknowledgement_ambiguous: true, retry_occurrence_id: s1.occurrence_id, reconciliation: "idempotent-retry"}); break;
    case "duplicate-reordered-delivery": expect(s1).toMatchObject({consumer_effect_count: 1, idempotent_consume: true, history_rewritten: false}); expect(new Set(s1.delivery_trace).size).toBeLessThan(s1.delivery_trace.length); break;
    case "poison-occurrence": expect(s1).toMatchObject({transaction_committed: true, outbox_occurrence_present: true, handling: "quarantine", durable_history_preserved: true}); break;
    case "recovery-replay": expect(s1).toMatchObject({fresh_process_restart: true, outbox_recovered: true, prior_occurrence_id: s1.occurrence_id, recovered_occurrence_id: s1.occurrence_id, prior_outcome: "committed", recovered_outcome: "committed"}); break;
    case "future-version": expect(s1).toMatchObject({supported_schema_version: 1, decode_status: "rejected", closed_decode: true}); expect(s1.occurrence_schema_version).toBeGreaterThan(s1.supported_schema_version); break;
    case "occurrence-reuse": expect(s1.existing_fact_fingerprint).not.toBe(s1.distinct_fact_fingerprint); expect(s1).toMatchObject({reused_occurrence_id: s1.occurrence_id, reuse_rejected: true}); break;
    case "non-idempotent-retry": expect(s1.retry_occurrence_id).not.toBe(s1.original_occurrence_id); expect(s1).toMatchObject({original_occurrence_id: s1.occurrence_id, consumer_effect_count: 2, retry_rejected: true}); break;
  }
};

const incoherent = (s1: EventS1Observation): EventS1Observation => {
  switch (s1.scenario) {
    case "after-outbox-before-publish-failure": return {...s1, state_preserved: false} as EventS1Observation;
    case "send-failure": return {...s1, durable_rollback: true} as EventS1Observation;
    case "success-ack-timeout": return {...s1, retry_occurrence_id: "settlement:req-2"} as EventS1Observation;
    case "duplicate-reordered-delivery": return {...s1, history_rewritten: true} as EventS1Observation;
    case "poison-occurrence": return {...s1, durable_history_preserved: false} as EventS1Observation;
    case "recovery-replay": return {...s1, recovered_occurrence_id: "settlement:req-2"} as EventS1Observation;
    case "future-version": return {...s1, closed_decode: false} as EventS1Observation;
    case "occurrence-reuse": return {...s1, reuse_rejected: false} as EventS1Observation;
    case "non-idempotent-retry": return {...s1, retry_occurrence_id: s1.original_occurrence_id, consumer_effect_count: 1} as EventS1Observation;
  }
};

describe("past-tense Event family", () => {
  it("passes the W3-derived S1 durable occurrence extension", () => {
    expect(evaluatePastTenseEvent(settlementEventDescriptor, settlementEventObservation())).toMatchObject({verdict: "pass", findings: [], authority_effect: "none"});
  });

  it("binds the exact 10 semantic, 4 REL-A, and 9 frozen S1 controls with no extras", () => {
    expect(readdirSync(hostileDir).sort()).toEqual(hostileFiles);
    expect(hostileFiles).toHaveLength(23);
    expect(Object.values(baseMap).filter(([, kind]) => kind === "type-semantic")).toHaveLength(10);
    expect(Object.values(baseMap).filter(([, kind]) => kind === "rel-a-evidence")).toHaveLength(4);
    expect(Object.keys(s1Map)).toHaveLength(9);
    const frozen = JSON.parse(readFileSync(hostileCataloguePath, "utf8")).cross_type_controls.filter((entry: {fixture_owner_swu: string}) => entry.fixture_owner_swu === "RMT-EVENT-002");
    const projected = frozen.map((entry: Record<string, unknown>) => [entry.hostile_id, entry.hostile_class, entry.expected_code, entry.fixture_owner_swu, entry.proof_owner_swu, entry.category, entry.required_observation, entry.required_outcome]);
    expect(projected).toEqual(Object.values(s1Map));
    expect(frozen.every((entry: {non_noop_required: boolean}) => entry.non_noop_required)).toBe(true);
  });

  it("kills every control as a semantic non-noop singleton without expected-code oracle input", () => {
    for (const [filename, expected] of Object.entries(baseMap)) {
      const hostile = load(filename);
      expect([hostile.hostile_id, hostile.hostile_class, hostile.expected_code], filename).toEqual(expected);
      const result = hostile.hostile_class === "type-semantic"
        ? evaluatePastTenseEvent(settlementEventDescriptor, applyEventObservationHostile(settlementEventObservation(), hostile))
        : evaluateEventRelation(applyEventRelationHostile(eventRelationAssertion(), hostile) as EventRelationAssertion);
      expect(result.findings.map(({code}) => code), hostile.hostile_id).toEqual([expected[2]]);
    }
    for (const [filename, expected] of Object.entries(s1Map)) {
      const hostile = load(filename);
      assertExactS1FixtureShape(hostile);
      expect([hostile.hostile_id, hostile.hostile_class, hostile.expected_code, hostile.fixture_owner_swu, hostile.proof_owner_swu, hostile.category, hostile.required_observation, hostile.required_outcome], filename).toEqual(expected);
      const baseline = settlementEventObservation();
      const mutated = decodePastTenseEventObservation(applyEventObservationHostile(baseline, {...hostile, expected_code: "IGNORED-ORACLE"}));
      expect(mutated).not.toEqual(baseline);
      expect(mutated.s1_observation).not.toBeNull();
      assertRequiredResidue(mutated.s1_observation!);
      expect(evaluatePastTenseEvent(settlementEventDescriptor, mutated).findings.map(({code}) => code)).toEqual([expected[2]]);
      expect(() => evaluatePastTenseEvent(settlementEventDescriptor, {...mutated, s1_observation: incoherent(mutated.s1_observation!)})).toThrowError("RMT_EVENT_S1_OBSERVATION_INVALID");
    }
    const stale = {...load("send-failure.json"), stale_fixture_key: true};
    expect(() => assertExactS1FixtureShape(stale)).toThrowError("RMT_EVENT_S1_FIXTURE_SHAPE_INVALID");
  });

  it("rejects open or malformed S1 observation shapes before semantic evaluation", () => {
    const hostile = load("future-version.json");
    const mutated = applyEventObservationHostile(settlementEventObservation(), hostile);
    expect(() => decodePastTenseEventObservation({...mutated, s1_observation: {...mutated.s1_observation!, extra: true}})).toThrowError("RMT_EVENT_S1_DECODE_INVALID");
    expect(() => decodePastTenseEventObservation({...mutated, unexpected: true})).toThrowError("RMT_EVENT_OBSERVATION_DECODE_INVALID");
  });
});
