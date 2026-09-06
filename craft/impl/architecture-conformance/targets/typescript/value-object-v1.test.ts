import {describe, expect, it} from "vitest";

import {createSettlementValueFactory, settlementValueProtocol} from
  "./value-object-v1.js";

const digest = (character: string): string => character.repeat(64);
const input = () => ({
  currency: {...settlementValueProtocol.component_protocols.currency,
    normalized_value_sha256: digest("7")},
  minor_units: {...settlementValueProtocol.component_protocols.minor_units,
    normalized_value_sha256: digest("8")},
  settlement_account: {
    ...settlementValueProtocol.component_protocols.settlement_account,
    normalized_value_sha256: digest("9"),
    owned_value: {account_ref: "account-001", active: true},
  },
});

describe("TypeScript owned Settlement Value Object", () => {
  it("forms equal immutable values from the complete tuple", () => {
    const source = input();
    const factory = createSettlementValueFactory().extendWithAccountActive?.();
    if (!factory) throw new Error("TEST_EXTENSION_MISSING");
    const left = factory.create(source);
    const right = factory.create(input());
    expect(left.ok && right.ok).toBe(true);
    if (!left.ok || !right.ok) throw new Error("TEST_FORMATION_FAILED");
    expect(left.value).not.toBe(right.value);
    expect(left.value.equals(right.value)).toBe(true);
    expect(left.value.hash()).toBe(right.value.hash());
    expect(Object.isFrozen(left.value)).toBe(true);
    expect(Object.isFrozen(left.value.settlement_account)).toBe(true);
    source.settlement_account.owned_value.account_ref = "changed";
    expect(left.value.settlement_account.account_ref).toBe("account-001");
  });

  it("uses every component and fails without forming an invalid value", () => {
    const factory = createSettlementValueFactory().extendWithAccountActive?.();
    if (!factory) throw new Error("TEST_EXTENSION_MISSING");
    const base = factory.create(input());
    if (!base.ok) throw new Error("TEST_FORMATION_FAILED");
    for (const component of ["currency", "minor_units", "settlement_account"] as const) {
      const changed = input();
      changed[component].normalized_value_sha256 = digest(component[0]!);
      const observed = factory.create(changed);
      if (!observed.ok) throw new Error("TEST_FORMATION_FAILED");
      expect(base.value.equals(observed.value), component).toBe(false);
    }
    const invalid = input();
    invalid.minor_units.normalized_value_sha256 = digest("f");
    expect(factory.create(invalid)).toMatchObject({
      ok: false,
      value: null,
      failure_codes: ["NEGATIVE_MINOR_UNITS"],
    });
    const staleProtocol = input();
    staleProtocol.settlement_account.protocol_sha256 = digest("0");
    expect(createSettlementValueFactory("base").create(staleProtocol)).toMatchObject({
      ok: false,
      value: null,
      failure_codes: ["COMPONENT_PROTOCOL_MISMATCH"],
      validator_trace: [],
    });
  });

  it("preserves bound validators while adding extension validation", () => {
    const base = createSettlementValueFactory("base");
    const extended = base.extendWithAccountActive?.();
    if (!extended) throw new Error("TEST_EXTENSION_MISSING");
    expect(extended.validators.slice(0, base.validators.length))
      .toEqual(base.validators);
    expect(extended.validators).toHaveLength(base.validators.length + 1);
    expect(extended.extendWithAccountActive).toBeNull();
    const invalid = input();
    invalid.settlement_account.owned_value.active = false;
    expect(extended.create(invalid)).toMatchObject({
      ok: false,
      value: null,
      failure_codes: ["INACTIVE_SETTLEMENT_ACCOUNT"],
    });
    expect(base.create(invalid).ok).toBe(true);
  });
});
