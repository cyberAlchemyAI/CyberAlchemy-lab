import {describe, expect, it} from "vitest";

import type {
  DeclaredEntityLifecycleConstructionContractV1,
  EntityLifecycleConstructionObservationV1,
  LockedConstructionObserverRefV1,
} from "./index.js";
import {
  decodeEntityLifecycleConstructionObservationV1,
  evaluateEntityLifecycleConstructionObservationV1,
  mintEntityLifecycleConstructionObservationV1,
} from "./index.js";

const digest = (character: string): string => character.repeat(64).slice(0, 64);
const observer: LockedConstructionObserverRefV1 = Object.freeze({
  role: "independent-construction-observer",
  observer_id: "observer.entity-kernel/v1",
  observer_sha256: digest("a"),
  owner_ref: "owner.entity-kernel/v1",
  provider_id: "provider.entity-kernel/v1",
  provider_sha256: digest("b"),
});
const definitionRef = Object.freeze({
  definition_id: "identity-lifecycle.kernel-fixture/v1",
  path: "fixture/entity-definition.json",
  sha256: digest("c"),
});
const baseFactory = Object.freeze({
  factory_id: "factory.entity.base/v1",
  factory_sha256: digest("d"),
  concept_id: "settlement.Settlement",
});
const extensionFactory = Object.freeze({
  factory_id: "factory.entity.extended/v1",
  factory_sha256: digest("e"),
  concept_id: "settlement.Settlement",
});
const identityComponents = Object.freeze([
  Object.freeze({component_name: "organization_id", type_id: "id.organization/v1",
    type_sha256: digest("1")}),
  Object.freeze({component_name: "settlement_id", type_id: "id.settlement/v1",
    type_sha256: digest("2")}),
]);
const identityA = Object.freeze({organization_id: digest("3"),
  settlement_id: digest("4")});
const identityB = Object.freeze({organization_id: digest("3"),
  settlement_id: digest("5")});
const validators = Object.freeze([
  Object.freeze({validator_id: "rule.entity.owner/v1",
    validator_sha256: digest("6"), origin: "base" as const}),
  Object.freeze({validator_id: "rule.entity.amount/v1",
    validator_sha256: digest("7"), origin: "base" as const}),
  Object.freeze({validator_id: "rule.entity.extension/v1",
    validator_sha256: digest("8"), origin: "extension" as const}),
]);
const snapshots = Object.freeze([
  Object.freeze({snapshot_id: "snapshot.created", entity_case_id: "settlement-a",
    sequence: 0, route_id: "factory" as const, predecessor_snapshot_id: null,
    identity_values: identityA, state_sha256: digest("9")}),
  Object.freeze({snapshot_id: "snapshot.reconstructed",
    entity_case_id: "settlement-a", sequence: 0,
    route_id: "deserialization-reconstruction" as const,
    predecessor_snapshot_id: null, identity_values: identityA,
    state_sha256: digest("9")}),
  Object.freeze({snapshot_id: "snapshot.completed", entity_case_id: "settlement-a",
    sequence: 1, route_id: "lifecycle-transition" as const,
    predecessor_snapshot_id: "snapshot.created", identity_values: identityA,
    state_sha256: digest("f")}),
  Object.freeze({snapshot_id: "snapshot.other", entity_case_id: "settlement-b",
    sequence: 0, route_id: "factory" as const, predecessor_snapshot_id: null,
    identity_values: identityB, state_sha256: digest("0")}),
]);
const contract: DeclaredEntityLifecycleConstructionContractV1 = Object.freeze({
  factory_ref: baseFactory,
  extension_factory_ref: extensionFactory,
  identity_components: identityComponents,
  validators,
  construction_routes: Object.freeze(["factory", "deserialization-reconstruction",
    "lifecycle-transition", "language-visible-direct-constructor"] as const),
  direct_constructor_policy: "private-inaccessible-or-delegating-facade",
  snapshots,
  equality_probes: Object.freeze([
    Object.freeze({probe_id: "same-identity", left_snapshot_id: "snapshot.created",
      right_snapshot_id: "snapshot.completed",
      relation: "same-identity-different-state" as const, expected_equal: true}),
    Object.freeze({probe_id: "distinct-identity",
      left_snapshot_id: "snapshot.created", right_snapshot_id: "snapshot.other",
      relation: "distinct-identity" as const, expected_equal: false}),
  ]),
  validation_failure: Object.freeze({probe_id: "invalid-amount",
    expected_failure_codes: Object.freeze(["AMOUNT_INVALID"])}),
});

const identity = (values: Readonly<Record<string, string>>) =>
  identityComponents.map((component) => Object.freeze({...component,
    normalized_value_sha256: values[component.component_name]!}));
const trace = (routeId: "factory" | "deserialization-reconstruction"
| "lifecycle-transition", snapshotId: string) => Object.freeze({
  route_id: routeId,
  input_class: "valid" as const,
  normalization_ordinal: 0,
  validator_trace: validators.map((validator, index) => Object.freeze({...validator,
    ordinal: index + 1, outcome: "pass" as const})),
  identity_resolution_ordinal: 4,
  construction_ordinal: 5,
  immutability_ordinal: 6,
  direct_constructor_policy: "not-applicable" as const,
  result: Object.freeze({status: "formed" as const, snapshot_created: true,
    snapshot_id: snapshotId}),
});
const makePositive = (): EntityLifecycleConstructionObservationV1 =>
  mintEntityLifecycleConstructionObservationV1({
    schema_version: "EntityLifecycleConstructionObservation/v1",
    observation_id: "observation.entity-kernel/v1",
    source_kind: "independent-family-fixture",
    observer_ref: observer,
    definition_ref: definitionRef,
    factory_ref: baseFactory,
    route_traces: Object.freeze([
      trace("factory", "snapshot.created"),
      trace("deserialization-reconstruction", "snapshot.reconstructed"),
      trace("lifecycle-transition", "snapshot.completed"),
      Object.freeze({
        route_id: "language-visible-direct-constructor",
        input_class: "valid" as const,
        normalization_ordinal: null,
        validator_trace: Object.freeze([]),
        identity_resolution_ordinal: null,
        construction_ordinal: null,
        immutability_ordinal: null,
        direct_constructor_policy: "private-inaccessible" as const,
        result: Object.freeze({status: "constructor-inaccessible" as const,
          snapshot_created: false, snapshot_id: null}),
      }),
    ]),
    validation_failure_probe: Object.freeze({
      probe_id: "invalid-amount",
      route_id: "factory",
      validator_trace: Object.freeze([
        Object.freeze({...validators[0]!, ordinal: 1, outcome: "pass" as const}),
        Object.freeze({...validators[1]!, ordinal: 2, outcome: "fail" as const}),
      ]),
      identity_resolution_ordinal: null,
      construction_ordinal: null,
      result: Object.freeze({status: "validation-failure", snapshot_created: false,
        failure_codes: Object.freeze(["AMOUNT_INVALID"])}),
    }),
    snapshots: snapshots.map((snapshot) => Object.freeze({
      snapshot_id: snapshot.snapshot_id,
      entity_case_id: snapshot.entity_case_id,
      sequence: snapshot.sequence,
      route_id: snapshot.route_id,
      predecessor_snapshot_id: snapshot.predecessor_snapshot_id,
      identity: identity(snapshot.identity_values),
      state_sha256: snapshot.state_sha256,
      frozen: true,
      mutation_observed: false,
    })),
    equality_probes: Object.freeze([
      Object.freeze({probe_id: "same-identity", left_snapshot_id: "snapshot.created",
        right_snapshot_id: "snapshot.completed",
        relation: "same-identity-different-state", comparison_basis:
          "canonical-identity-only", observed_equal: true,
        left_hash_sha256: digest("a"), right_hash_sha256: digest("a")}),
      Object.freeze({probe_id: "distinct-identity",
        left_snapshot_id: "snapshot.created", right_snapshot_id: "snapshot.other",
        relation: "distinct-identity", comparison_basis: "canonical-identity-only",
        observed_equal: false, left_hash_sha256: digest("a"),
        right_hash_sha256: digest("b")}),
    ]),
    extension: Object.freeze({base_factory_ref: baseFactory,
      extension_factory_ref: extensionFactory, base_validators_preserved: true,
      added_validators: Object.freeze([validators[2]!]),
      identity_resolver_preserved: true, altered_facets: Object.freeze([]),
      cycle_detected: false}),
    per_call_validator_supplied: false,
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false,
    authority_effect: "none",
  });
const bodyOf = (value: EntityLifecycleConstructionObservationV1) => {
  const {observation_sha256: _digest, ...body} = value;
  return body;
};
const evaluate = (observation: EntityLifecycleConstructionObservationV1) =>
  evaluateEntityLifecycleConstructionObservationV1({
    locked_observer_ref: observer,
    locked_definition_ref: definitionRef,
    declared_contract: contract,
    observation,
  });

describe("Entity lifecycle construction observation transport", () => {
  it("accepts stable identity snapshots and all four policy-specific routes", () => {
    const positive = decodeEntityLifecycleConstructionObservationV1(
      JSON.stringify(makePositive()),
    );
    const result = evaluate(positive);
    expect(result.result).toBe("pass");
    expect(result.diagnostics).toEqual([]);
    expect(result.accounting).toEqual({typed_identity_components: 2,
      declared_validators: 3, construction_routes: 4, lifecycle_snapshots: 4,
      equality_probes: 2});
  });

  it("rejects stale serialized and forged in-memory digests", () => {
    const positive = makePositive();
    expect(() => decodeEntityLifecycleConstructionObservationV1(JSON.stringify({
      ...positive, observation_sha256: digest("0"),
    }))).toThrow("ENTITY_OBSERVATION_DIGEST_STALE");
    const forged = {...positive, observation_sha256: digest("0")};
    expect(evaluate(forged).diagnostics)
      .toContain("ENTITY_OBSERVATION_DIGEST_MISMATCH");
  });

  it("detects bypass, changed identity, mutation, and invalid formation", () => {
    const positive = makePositive();
    const attacked = mintEntityLifecycleConstructionObservationV1({
      ...bodyOf(positive),
      source_kind: "mutated-entity-lifecycle-observation",
      per_call_validator_supplied: true,
      validation_failure_probe: {...positive.validation_failure_probe,
        identity_resolution_ordinal: 3, construction_ordinal: 4,
        result: {...positive.validation_failure_probe.result,
          snapshot_created: true}},
      snapshots: positive.snapshots.map((snapshot) =>
        snapshot.snapshot_id === "snapshot.completed"
          ? {...snapshot, identity: identity(identityB), frozen: false,
            mutation_observed: true}
          : snapshot),
      extension: {...positive.extension, base_validators_preserved: false,
        identity_resolver_preserved: false, cycle_detected: true},
    });
    expect(evaluate(attacked).diagnostics).toEqual(expect.arrayContaining([
      "ENTITY_PER_CALL_VALIDATOR_BYPASS",
      "ENTITY_INVALID_INPUT_FORMED_SNAPSHOT",
      "ENTITY_IDENTITY_CHANGED_ACROSS_LIFECYCLE",
      "ENTITY_SNAPSHOT_MUTABLE",
      "ENTITY_BASE_VALIDATOR_REMOVED",
      "ENTITY_IDENTITY_RESOLVER_REPLACED",
      "ENTITY_EXTENSION_CYCLE",
    ]));
  });
});
