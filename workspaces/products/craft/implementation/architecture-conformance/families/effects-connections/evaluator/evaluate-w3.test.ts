import {describe, expect, it} from "vitest";
import {readFileSync} from "node:fs";
import type {EventDescriptor, InterfaceDescriptor, MappingDescriptor, OperationDescriptor, W3Binding} from "../contracts/w3-contracts.js";
import {evaluateW3} from "./evaluate-w3.js";
import {buildW3Hostiles} from "../hostiles/w3-hostiles.js";
import {completeSettlement, makeSettlementCreated, mapSettlementResponse, settlementPortV1Members} from "../providers/typescript/financial-settlement.js";

const digest = "a".repeat(64);
const binding: W3Binding = {
  protocol_id: "domainspec.w3-descriptor-binding/v1",
  concept_ref: {id: "DS-D1", sha256: digest},
  decision_ref: {id: "W3-A", sha256: digest},
  profile_ref: {id: "typescript-strict", sha256: digest},
  provider_ref: {id: "typescript-provider", sha256: digest},
  source_ref: {id: "fixture-source", sha256: digest},
  fixture_ref: {id: "fixture", sha256: digest},
};
const base = {schema_version: "domainspec.w3-descriptor/v1" as const, language: "typescript" as const, binding, claim_ceiling: "candidate-local-exact-fixture" as const, authority_effect: "none" as const};

const mapping: MappingDescriptor = {...base, descriptor_id: "mapping.settlement-response", kind: "Mapping", source_contract_id: "SettlementRecord/v1", target_contract_id: "SettlementResponse/v1", direction: "forward", correspondence: [{source: "id", target: "settlementId", mode: "direct"}, {source: "playerId", target: "playerId", mode: "direct"}, {source: "amount", target: "amount", mode: "direct"}], totality: "total", failure_contract_id: null, effect_policy: "none", reverse_contract_id: null};
const mappingObservation = {kind: "Mapping" as const, source_contract_id: "SettlementRecord/v1", target_contract_id: "SettlementResponse/v1", direction: "forward" as const, observed_correspondence: mapping.correspondence, totality: "total" as const, failure_contract_id: null, failure_observed: false, effect_policy: "none" as const, effects: [], reverse_contract_complete: false};

const boundary: InterfaceDescriptor = {...base, descriptor_id: "interface.settlement-port-v1", kind: "Interface", boundary_kind: "internal", contract_id: "SettlementPort", exact_version: "1", compatibility_policy_id: "exact-major/v1", exposed_bindings: [{binding_id: "completeSettlement", kind: "Operation"}, {binding_id: "findSettlement", kind: "Query"}], admission_status: "candidate"};
const boundaryObservation = {kind: "Interface" as const, boundary_kind: "internal" as const, contract_id: "SettlementPort", version: "1", compatibility_policy_id: "exact-major/v1", exposed_bindings: boundary.exposed_bindings, compatibility_checks: [{requested_version: "1", accepted: true}, {requested_version: "1.1", accepted: true}, {requested_version: "2", accepted: false}]};

const event: EventDescriptor = {...base, descriptor_id: "event.settlement-created-v1", kind: "Event", tense: "past", payload_contract_id: "SettlementCreatedPayload", payload_version: "1", occurrence_identity_contract_id: "settlement-id/v1", fact_checkpoint: "durable-outbox-append", publication_policy_id: "at-least-once/v1", consumer_contract_ids: ["ledger/v1"], distributed_exactly_once_claim: false};
const eventObservation = {kind: "Event" as const, tense: "past" as const, payload_contract_id: "SettlementCreatedPayload", payload_version: "1", occurrence_identity_contract_id: "settlement-id/v1", occurrence_id: "settlement:req-1", duplicate_occurrence_observed: false, durable_checkpoints: ["durable-outbox-append" as const], publication_policy_id: "at-least-once/v1", publication_attempt_ids: ["attempt-1", "attempt-2"], consumer_contract_ids: ["ledger/v1"], consumer_payload_checks: [{consumer_contract_id: "ledger/v1", payload_version: "1", accepted: true}], lifecycle_trace: ["constructed" as const, "durable-fact" as const, "publish-attempted" as const, "publish-attempted" as const, "acknowledged" as const], distributed_exactly_once_claim: false};

const operation: OperationDescriptor = {...base, descriptor_id: "operation.complete-settlement", kind: "Operation", input_contract_id: "SettlementRequest/v1", declared_reads: ["settlement-by-request-id"], declared_writes: ["settlement"], declared_external_effects: ["outbox"], outcome_contract_id: "settlement-completed", failure_contract_id: "settlement-rejected", atomicity: "atomic", ordered_checkpoints: ["rule:can-settle", "write:settlement", "append:outbox", "return:settlement-completed"], guard_bindings: [{rule_id: "can-settle", state_version: "settlement-state/v1", controlled_effect: "write:settlement"}], emitted_event_bindings: [{event_id: "SettlementCreated/v1", checkpoint: "durable-outbox-append", after_outcome: "write:settlement"}], continuation_boundary: "awaited-settlement"};
const operationObservation = {kind: "Operation" as const, input_contract_id: "SettlementRequest/v1", reads: ["settlement-by-request-id"], writes: [{id: "settlement", state: "committed" as const}], external_effects: ["outbox"], atomicity: "atomic" as const, trace: operation.ordered_checkpoints, guard_results: [{rule_id: "can-settle", invoked: true, decision_used: true, state_version: "settlement-state/v1", controlled_effect: "write:settlement"}], emitted_events: operation.emitted_event_bindings, outcome_id: "settlement-completed", failure_id: null, continuation_boundary: "awaited-settlement" as const, continuation_closed: true};

describe("W3 descriptor-bound effects and connections", () => {
  it("evaluates the repository-authored descriptor and observation set", () => {
    const descriptorSet = JSON.parse(readFileSync(new URL("../fixtures/financial-settlement/descriptors.json", import.meta.url), "utf8")) as {descriptors: import("../contracts/w3-contracts.js").W3Descriptor[]};
    const observationSet = JSON.parse(readFileSync(new URL("../fixtures/financial-settlement/observations.json", import.meta.url), "utf8")) as {observations: import("../contracts/w3-contracts.js").W3Observation[]};
    expect(descriptorSet.descriptors.map((descriptor, index) => evaluateW3(descriptor, observationSet.observations[index] ?? null).verdict)).toEqual(["pass", "pass", "pass", "pass"]);
  });

  it("passes exact Mapping, Interface, Event, and Operation observations", () => {
    expect(evaluateW3(mapping, mappingObservation).verdict).toBe("pass");
    expect(evaluateW3(boundary, boundaryObservation).verdict).toBe("pass");
    expect(evaluateW3(event, eventObservation).verdict).toBe("pass");
    expect(evaluateW3(operation, operationObservation).verdict).toBe("pass");
  });

  it("rejects endpoint reversal and field omission", () => {
    const reversed = {...mappingObservation, source_contract_id: mapping.target_contract_id, target_contract_id: mapping.source_contract_id, observed_correspondence: mapping.correspondence.slice(0, 2)};
    expect(evaluateW3(mapping, reversed).findings.map(({code}) => code)).toEqual(["ARCH_MAPPING_ENDPOINT_DRIFT", "ARCH_MAPPING_CORRESPONDENCE_DRIFT"]);
  });

  it("allows a multi-member Interface but rejects an undeclared exposure", () => {
    expect(settlementPortV1Members).toHaveLength(2);
    expect(evaluateW3(boundary, {...boundaryObservation, exposed_bindings: [...boundaryObservation.exposed_bindings].reverse()}).verdict).toBe("pass");
    const extra = {...boundaryObservation, exposed_bindings: [...boundaryObservation.exposed_bindings, {binding_id: "adminDelete", kind: "Operation" as const}]};
    expect(evaluateW3(boundary, extra).findings[0]?.code).toBe("ARCH_INTERFACE_EXPOSURE_DRIFT");
  });

  it("separates one durable occurrence from repeated publication attempts", () => {
    expect(evaluateW3(event, eventObservation).verdict).toBe("pass");
    const inflated = {...eventObservation, distributed_exactly_once_claim: true, durable_checkpoints: ["durable-outbox-append" as const, "domain-state-commit" as const]};
    expect(evaluateW3(event, inflated).findings.map(({code}) => code)).toEqual(["ARCH_EVENT_CHECKPOINT_INVALID", "ARCH_EVENT_EXACTLY_ONCE_INFLATION"]);
  });

  it("detects write-restore, ignored Rule, order inversion, and open lazy work", () => {
    const hostile = {...operationObservation, writes: [{id: "settlement", state: "restored" as const}], trace: [...operationObservation.trace].reverse(), guard_results: [{...operationObservation.guard_results[0]!, decision_used: false}], continuation_closed: false};
    expect(evaluateW3(operation, hostile).findings.map(({code}) => code)).toEqual(["ARCH_OPERATION_WRITE_RESTORE", "ARCH_OPERATION_ATOMICITY_DRIFT", "ARCH_OPERATION_ORDER_DRIFT", "ARCH_OPERATION_GUARD_INVALID", "ARCH_OPERATION_CONTINUATION_OPEN"]);
  });

  it("rejects missing declared effects and a partial atomic commit", () => {
    expect(evaluateW3(operation, {...operationObservation, reads: []}).findings.map(({code}) => code)).toContain("ARCH_OPERATION_EFFECT_INCOMPLETE");
    expect(evaluateW3(operation, {...operationObservation, writes: [{id: "settlement", state: "partial"}]}).findings.map(({code}) => code)).toContain("ARCH_OPERATION_ATOMICITY_DRIFT");
  });

  it("kills every independently authored W3 hostile", () => {
    for (const [descriptor, observation] of [[mapping, mappingObservation], [boundary, boundaryObservation], [event, eventObservation], [operation, operationObservation]] as const) {
      for (const hostile of buildW3Hostiles(descriptor, observation)) {
        const result = evaluateW3(descriptor, hostile.observation);
        expect(result.verdict, hostile.mutant_id).toBe("reject");
        expect(result.findings.map(({code}) => code), hostile.mutant_id).toEqual(expect.arrayContaining(hostile.expected_codes));
      }
    }
  });

  it("never turns missing observation support into a pass", () => {
    expect(evaluateW3(event, null).verdict).toBe("unsupported");
    expect(evaluateW3(event, mappingObservation).verdict).toBe("indeterminate");
  });

  it("realizes the four concepts in TypeScript", async () => {
    const record = {id: "req-1", playerId: "player-1", amount: 42};
    expect(mapSettlementResponse(record)).toEqual({settlementId: "req-1", playerId: "player-1", amount: 42});
    expect(makeSettlementCreated(record).type).toBe("SettlementCreated");
    const trace: string[] = [];
    const result = await completeSettlement({request: {requestId: "req-1", playerId: "player-1", amount: 42}, existingSettlementId: null, commitAtomically: async () => {trace.push("write", "outbox")}});
    expect(result.outcome).toBe("settlement-completed");
    expect(trace).toEqual(["write", "outbox"]);
  });

  it("crosses one atomic persistence boundary and never returns success after commit failure", async () => {
    const attempts: string[] = [];
    await expect(completeSettlement({
      request: {requestId: "req-2", playerId: "player-1", amount: 42},
      existingSettlementId: null,
      commitAtomically: async () => { attempts.push("atomic-commit"); throw new Error("COMMIT_FAILED"); },
    })).rejects.toThrow("COMMIT_FAILED");
    expect(attempts).toEqual(["atomic-commit"]);
  });
});
