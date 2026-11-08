import type {EventDescriptor, EventObservation} from "../../families/effects-connections/contracts/w3-contracts.js";
import {evaluateW3} from "../../families/effects-connections/evaluator/evaluate-w3.js";
import type {EventFindingCode, PastTenseEventDescriptor, PastTenseEventObservation} from "../../families/past-tense-event/contracts/event-contracts.js";
import {decodePastTenseEventObservation} from "../../families/past-tense-event/decoder/decode-event-observation.js";
import {evaluatePastTenseEvent} from "../../families/past-tense-event/evaluator/evaluate-event.js";
import {settlementEventDescriptor, settlementEventObservation} from "../../families/past-tense-event/fixtures/settlement-event.js";
import {applyEventObservationHostile, type EventHostileMutation} from "../../families/past-tense-event/mutations/apply-event-hostile.js";

export type EventPortableResult = Readonly<{
  schema_version: "domainspec.event-portable-result/v1";
  result: "pass";
  meta_type: "Event";
  event_name: string;
  tense: "past";
  payload_contract_id: string;
  payload_version: string;
  payload_immutable: true;
  occurrence_identity_contract_id: string;
  occurrence_id: string;
  retry_occurrence_id: string;
  persistence_checkpoint: string;
  publication_is_separate_from_commit: true;
  publication_policy_id: string;
  consumer_contract_ids: readonly string[];
  durable_occurrence: PastTenseEventObservation["durable_occurrence"];
  distributed_exactly_once_claim: false;
  semantic_plan_epoch_id: string;
  semantic_contract_digest: string;
  authority_effect: "none";
}>;

export type EventS1PortableResult = Readonly<{
  schema_version: "domainspec.event-s1-portable-result/v1";
  result: "reject";
  meta_type: "Event";
  diagnostic_code: EventFindingCode;
  scenario: NonNullable<PastTenseEventObservation["s1_observation"]>["scenario"];
  occurrence_id: string;
  durable_occurrence: PastTenseEventObservation["durable_occurrence"];
  required_residue: NonNullable<PastTenseEventObservation["s1_observation"]>;
  distributed_exactly_once_claim: false;
  semantic_plan_epoch_id: string;
  semantic_contract_digest: string;
  authority_effect: "none";
}>;

export type EventCase = Readonly<{
  w3_descriptor: EventDescriptor;
  w3_observation: EventObservation;
  descriptor: PastTenseEventDescriptor;
  observation: PastTenseEventObservation;
}>;

type NativeResult = Readonly<{
  portable: EventPortableResult | EventS1PortableResult;
  native_evidence: Readonly<{language: "typescript"; mechanism: "readonly-event-and-frozen-durable-handle"}>;
}>;

const ref = (id: string) => ({id, sha256: "a".repeat(64)});
const exactKeys = (value: unknown, expected: readonly string[]): boolean => value !== null && typeof value === "object" && !Array.isArray(value) && JSON.stringify(Object.keys(value).sort()) === JSON.stringify([...expected].sort());
const caseKeys = ["w3_descriptor", "w3_observation", "descriptor", "observation"] as const;
const descriptorKeys = ["schema_version", "descriptor_id", "semantic_plan_epoch_id", "semantic_contract_digest", "event_name", "tense", "payload_contract_id", "payload_version", "payload_immutable", "occurrence_identity_contract_id", "persistence_checkpoint", "publication_policy_id", "consumer_contract_ids", "distributed_exactly_once_claim", "durable_handle", "admission_status", "authority_effect"] as const;

export const makeSettlementEventCase = (publicationAttemptId = "publish:req-1:1"): EventCase => {
  const observation = settlementEventObservation();
  return {
    w3_descriptor: {
      schema_version: "domainspec.w3-descriptor/v1", descriptor_id: "event.settlement-created-v1", language: "typescript",
      binding: {protocol_id: "domainspec.w3-descriptor-binding/v1", concept_ref: ref("DS-D1.12"), decision_ref: ref("WP-RMT-002/S1/2026-08-16"), profile_ref: ref("typescript"), provider_ref: ref("typescript-w3-effects-connections-v1"), source_ref: ref("financial-settlement.ts"), fixture_ref: ref("event-case")},
      claim_ceiling: "candidate-local-exact-fixture", authority_effect: "none", kind: "Event", tense: "past",
      payload_contract_id: "SettlementCreatedPayload/v1", payload_version: "1", occurrence_identity_contract_id: "SettlementOccurrenceId/v1",
      fact_checkpoint: "durable-outbox-append", publication_policy_id: "at-least-once-idempotent/v1", consumer_contract_ids: ["SettlementProjectionConsumer/v1"], distributed_exactly_once_claim: false,
    },
    w3_observation: {
      kind: "Event", tense: "past", payload_contract_id: "SettlementCreatedPayload/v1", payload_version: "1", occurrence_identity_contract_id: "SettlementOccurrenceId/v1", occurrence_id: "settlement:req-1", duplicate_occurrence_observed: false,
      durable_checkpoints: ["durable-outbox-append"], publication_policy_id: "at-least-once-idempotent/v1", publication_attempt_ids: [publicationAttemptId], consumer_contract_ids: ["SettlementProjectionConsumer/v1"], consumer_payload_checks: [{consumer_contract_id: "SettlementProjectionConsumer/v1", payload_version: "1", accepted: true}], lifecycle_trace: ["constructed", "durable-fact", "outbox-appended", "publish-attempted"], distributed_exactly_once_claim: false,
    },
    descriptor: settlementEventDescriptor,
    observation: {...observation, durable_occurrence: {...observation.durable_occurrence, publication_attempt_id: publicationAttemptId}},
  };
};

export const makeSettlementEventS1Case = (hostile: EventHostileMutation): EventCase => {
  if (hostile.hostile_class !== "s1-cross-boundary") throw new Error("RMT_EVENT_S1_HOSTILE_REQUIRED");
  const baseline = makeSettlementEventCase();
  return {...baseline, observation: applyEventObservationHostile(baseline.observation, hostile)};
};

export const evaluateEventCase = (input: EventCase): NativeResult => {
  if (!exactKeys(input, caseKeys) || !exactKeys(input.descriptor, descriptorKeys)) throw new Error("RMT_EVENT_CASE_DECODE_INVALID");
  if (input.descriptor.semantic_plan_epoch_id !== "WP-RMT-002/S1/2026-08-16" || input.descriptor.semantic_contract_digest !== "75fd21cd605735b9ca76ed42e46d126850b6c94ea976f55347aa35fd61d530b7") throw new Error("RMT_EVENT_TYPESCRIPT_BINDING_STALE");
  const observation = decodePastTenseEventObservation(input.observation);
  const w3 = evaluateW3(input.w3_descriptor, input.w3_observation);
  if (w3.verdict !== "pass") throw new Error(`RMT_EVENT_TYPESCRIPT_REJECTED:${JSON.stringify({w3: w3.findings})}`);
  const extension = evaluatePastTenseEvent(input.descriptor, observation);
  const native_evidence = Object.freeze({language: "typescript" as const, mechanism: "readonly-event-and-frozen-durable-handle" as const});
  if (observation.s1_observation !== null) {
    if (extension.verdict !== "reject" || extension.findings.length !== 1) throw new Error("RMT_EVENT_TYPESCRIPT_S1_CLASSIFICATION_INVALID");
    return Object.freeze({
      portable: Object.freeze({
        schema_version: "domainspec.event-s1-portable-result/v1", result: "reject", meta_type: "Event",
        diagnostic_code: extension.findings[0]!.code, scenario: observation.s1_observation.scenario, occurrence_id: observation.occurrence_id,
        durable_occurrence: Object.freeze({...observation.durable_occurrence}), required_residue: Object.freeze({...observation.s1_observation}),
        distributed_exactly_once_claim: false, semantic_plan_epoch_id: input.descriptor.semantic_plan_epoch_id,
        semantic_contract_digest: input.descriptor.semantic_contract_digest, authority_effect: "none",
      }), native_evidence,
    });
  }
  if (extension.verdict !== "pass") throw new Error(`RMT_EVENT_TYPESCRIPT_REJECTED:${JSON.stringify({extension: extension.findings})}`);
  return Object.freeze({
    portable: Object.freeze({
      schema_version: "domainspec.event-portable-result/v1", result: "pass", meta_type: "Event", event_name: input.descriptor.event_name, tense: "past",
      payload_contract_id: input.descriptor.payload_contract_id, payload_version: input.descriptor.payload_version, payload_immutable: true,
      occurrence_identity_contract_id: input.descriptor.occurrence_identity_contract_id, occurrence_id: observation.occurrence_id, retry_occurrence_id: observation.occurrence_id,
      persistence_checkpoint: input.descriptor.persistence_checkpoint, publication_is_separate_from_commit: true, publication_policy_id: input.descriptor.publication_policy_id,
      consumer_contract_ids: Object.freeze([...input.descriptor.consumer_contract_ids].sort()), durable_occurrence: Object.freeze({...observation.durable_occurrence}),
      distributed_exactly_once_claim: false, semantic_plan_epoch_id: input.descriptor.semantic_plan_epoch_id, semantic_contract_digest: input.descriptor.semantic_contract_digest, authority_effect: "none",
    }), native_evidence,
  });
};
