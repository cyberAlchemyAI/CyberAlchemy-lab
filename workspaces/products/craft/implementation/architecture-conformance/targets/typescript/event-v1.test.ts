import {readFileSync} from "node:fs";
import {describe, expect, it} from "vitest";
import type {EventHostileMutation} from "../../families/past-tense-event/mutations/apply-event-hostile.js";
import {evaluateEventCase, makeSettlementEventCase, makeSettlementEventS1Case} from "./event-v1.js";

const hostileRoot = "projects/domainspec-v2/impl/architecture-conformance/families/past-tense-event/hostiles";
const s1Names = ["after-outbox-before-publish-failure", "send-failure", "success-ack-timeout", "duplicate-reordered-delivery", "poison-occurrence", "recovery-replay", "future-version", "occurrence-reuse", "non-idempotent-retry"] as const;

describe("TypeScript Event v1 target", () => {
  it("reuses W3 and closes S1 durable occurrence semantics across retry attempts", () => {
    const first = evaluateEventCase(makeSettlementEventCase("publish:req-1:1"));
    const retry = evaluateEventCase(makeSettlementEventCase("publish:req-1:2"));
    expect(first.portable).toMatchObject({result: "pass", meta_type: "Event", event_name: "SettlementCreated", tense: "past", payload_immutable: true, occurrence_id: "settlement:req-1", persistence_checkpoint: "durable-outbox-append", publication_is_separate_from_commit: true, distributed_exactly_once_claim: false, semantic_plan_epoch_id: "WP-RMT-002/S1/2026-08-16", authority_effect: "none"});
    expect(retry.portable).toMatchObject({result: "pass", occurrence_id: "settlement:req-1"});
    if (first.portable.result !== "pass" || retry.portable.result !== "pass") throw new Error("positive portable expected");
    expect(retry.portable.durable_occurrence.publication_attempt_id).not.toBe(first.portable.durable_occurrence.publication_attempt_id);
    expect(Object.keys(first.portable.durable_occurrence).sort()).toEqual(["acknowledgement_state", "consumption_observation", "delivery_observation", "occurrence_id", "persistence_checkpoint", "publication_attempt_id"]);
  });

  it("derives all nine native S1 singleton diagnostics and residue without an oracle", () => {
    for (const name of s1Names) {
      const hostile = JSON.parse(readFileSync(`${hostileRoot}/${name}.json`, "utf8")) as EventHostileMutation & {expected_code: string};
      const result = evaluateEventCase(makeSettlementEventS1Case({...hostile, expected_code: "IGNORED"}));
      expect(result.portable).toMatchObject({schema_version: "domainspec.event-s1-portable-result/v1", result: "reject", diagnostic_code: hostile.expected_code, scenario: name, occurrence_id: "settlement:req-1", distributed_exactly_once_claim: false, authority_effect: "none"});
      expect((result.portable as {required_residue: unknown}).required_residue).toBeTruthy();
    }
  });

  it("rejects incoherent durable handles, open S1 input, and W3 publication before durability", () => {
    const input = makeSettlementEventCase();
    expect(() => evaluateEventCase({...input, observation: {...input.observation, durable_occurrence: {...input.observation.durable_occurrence, occurrence_id: "other"}}})).toThrowError("RMT_EVENT_DURABLE_HANDLE_INVALID");
    expect(() => evaluateEventCase({...input, observation: {...input.observation, unexpected: true} as never})).toThrowError("RMT_EVENT_OBSERVATION_DECODE_INVALID");
    expect(() => evaluateEventCase({...input, w3_observation: {...input.w3_observation, lifecycle_trace: ["constructed", "publish-attempted", "durable-fact"]}})).toThrowError(/ARCH_EVENT_PUBLICATION_ORDER_DRIFT/);
  });
});
