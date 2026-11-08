import {describe, expect, it} from "vitest";

import {createSettlementEntityFactory, settlementEntityProtocol} from
  "./entity-v1.js";

const digest = (character: string): string => character.repeat(64);
const input = (settlement = "7", state = "8") => ({
  entity_case_id: `settlement-${settlement}`,
  snapshot_id: `snapshot.settlement-${settlement}.created`,
  sequence: 0,
  predecessor_snapshot_id: null,
  organization_id: {...settlementEntityProtocol.identity_components[0],
    normalized_value_sha256: digest("6")},
  settlement_id: {...settlementEntityProtocol.identity_components[1],
    normalized_value_sha256: digest(settlement)},
  owner_id: digest("6"),
  amount_minor_units: 100,
  duplicate: false,
  state_sha256: digest(state),
});

describe("TypeScript Settlement Entity", () => {
  it("runs exact base then extension validators before typed identity", () => {
    const base = createSettlementEntityFactory();
    const factory = base.extendWithDuplicateBlocked?.();
    if (!factory) throw new Error("TEST_EXTENSION_MISSING");
    expect(factory.validators.slice(0, base.validators.length))
      .toEqual(base.validators);
    expect(factory.identity_resolver_ref).toBe(base.identity_resolver_ref);
    expect(factory.extendWithDuplicateBlocked).toBeNull();
    const result = factory.create(input());
    expect(result.ok).toBe(true);
    if (!result.ok) throw new Error("TEST_ENTITY_FORMATION_FAILED");
    expect(result.trace.validator_trace.map(({origin}) => origin))
      .toEqual(["base", "base", "extension"]);
    expect(result.trace).toMatchObject({identity_resolution_ordinal: 4,
      construction_ordinal: 5, immutability_ordinal: 6});
    expect(result.value.identity).toHaveLength(2);
  });

  it("creates immutable snapshots and uses identity-only equality and hash", () => {
    const factory = createSettlementEntityFactory("with-duplicate-blocked");
    const left = factory.create(input());
    const sameIdentity = factory.reconstruct({...input(),
      snapshot_id: "snapshot.settlement-7.reconstructed"});
    const distinct = factory.create(input("c"));
    if (!left.ok || !sameIdentity.ok || !distinct.ok) {
      throw new Error("TEST_ENTITY_FORMATION_FAILED");
    }
    expect(left.value).not.toBe(sameIdentity.value);
    expect(left.value.equals(sameIdentity.value)).toBe(true);
    expect(left.value.hash()).toBe(sameIdentity.value.hash());
    expect(left.value.equals(distinct.value)).toBe(false);
    expect(Object.isFrozen(left.value)).toBe(true);
    expect(Object.isFrozen(left.value.identity)).toBe(true);
    expect(Object.isFrozen(left.value.identity[0])).toBe(true);
  });

  it("transitions through the same pipeline while preserving identity", () => {
    const factory = createSettlementEntityFactory("with-duplicate-blocked");
    const created = factory.create(input());
    if (!created.ok) throw new Error("TEST_ENTITY_FORMATION_FAILED");
    const completed = factory.transition(created.value, {
      snapshot_id: "snapshot.settlement-7.completed",
      state_sha256: digest("9"),
      amount_minor_units: 100,
      duplicate: false,
    });
    if (!completed.ok) throw new Error("TEST_TRANSITION_FAILED");
    expect(completed.trace.route_id).toBe("lifecycle-transition");
    expect(completed.value.identity).toEqual(created.value.identity);
    expect(completed.value.equals(created.value)).toBe(true);
    expect(completed.value.state_sha256).not.toBe(created.value.state_sha256);
    expect(completed.value.predecessor_snapshot_id).toBe(created.value.snapshot_id);
  });

  it("has no callable direct constructor and creates no invalid snapshot", () => {
    const factory = createSettlementEntityFactory("with-duplicate-blocked");
    expect(factory.directConstructor).toBeNull();
    const invalid = factory.create({...input(), amount_minor_units: 0});
    expect(invalid).toMatchObject({ok: false, value: null,
      failure_codes: ["AMOUNT_INVALID"]});
    expect(invalid.trace.identity_resolution_ordinal).toBeNull();
    const duplicate = factory.create({...input(), duplicate: true});
    expect(duplicate).toMatchObject({ok: false, value: null,
      failure_codes: ["DUPLICATE_SETTLEMENT"]});
  });
});
