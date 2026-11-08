type ComponentProtocol = Readonly<{
  protocol_id: string;
  protocol_sha256: string;
}>;

type SettlementValueInput = Readonly<{
  currency: Readonly<ComponentProtocol & {normalized_value_sha256: string}>;
  minor_units: Readonly<ComponentProtocol & {normalized_value_sha256: string}>;
  settlement_account: Readonly<ComponentProtocol & {
    normalized_value_sha256: string;
    owned_value: Readonly<{account_ref: string; active: boolean}>;
  }>;
}>;

type SettlementValue = Readonly<{
  tuple: readonly [string, string, string];
  component_bindings: readonly Readonly<ComponentProtocol & {
    component_name: "currency" | "minor_units" | "settlement_account";
    normalized_value_sha256: string;
    nested_value_object: boolean;
  }>[];
  settlement_account: SettlementAccountValue;
  equals: (other: SettlementValue) => boolean;
  hash: () => string;
}>;

type SettlementAccountValue = Readonly<ComponentProtocol & {
  account_ref: string;
  normalized_value_sha256: string;
  equals: (other: SettlementAccountValue) => boolean;
  hash: () => string;
}>;

type ValidationFailure = Readonly<{
  ok: false;
  value: null;
  failure_codes: readonly string[];
  validator_trace: readonly string[];
}>;

type FormationSuccess = Readonly<{
  ok: true;
  value: SettlementValue;
  failure_codes: readonly [];
  validator_trace: readonly string[];
}>;

type BoundValidator = Readonly<{
  validator_id: string;
  validator_sha256: string;
  origin: "base" | "extension";
  validate: (input: SettlementValueInput) => string | null;
}>;

type SettlementValueFactory = Readonly<{
  factory_ref: Readonly<{
    factory_id: string;
    factory_sha256: string;
    concept_id: string;
  }>;
  validators: readonly BoundValidator[];
  create: (
    input: SettlementValueInput,
  ) => FormationSuccess | ValidationFailure;
  extendWithAccountActive: (() => SettlementValueFactory) | null;
}>;

const expectedProtocols: Readonly<{
  currency: ComponentProtocol;
  minor_units: ComponentProtocol;
  settlement_account: ComponentProtocol;
}> = Object.freeze({
  currency: Object.freeze({
    protocol_id: "typescript.owned-value-component.currency-code/v1",
    protocol_sha256: "1111111111111111111111111111111111111111111111111111111111111111",
  }),
  minor_units: Object.freeze({
    protocol_id: "typescript.owned-value-component.minor-units/v1",
    protocol_sha256: "2222222222222222222222222222222222222222222222222222222222222222",
  }),
  settlement_account: Object.freeze({
    protocol_id: "typescript.owned-value-component.settlement-account/v1",
    protocol_sha256: "3333333333333333333333333333333333333333333333333333333333333333",
  }),
});

const protocolMatches = (
  observed: ComponentProtocol,
  expected: ComponentProtocol,
): boolean => observed.protocol_id === expected.protocol_id
  && observed.protocol_sha256 === expected.protocol_sha256;

const baseValidators: readonly BoundValidator[] = Object.freeze([
  Object.freeze({
    validator_id: "rule.settlement-value.currency-supported/v1",
    validator_sha256: "4444444444444444444444444444444444444444444444444444444444444444",
    origin: "base",
    validate: (input: SettlementValueInput): string | null =>
      protocolMatches(input.currency, expectedProtocols.currency)
        ? null : "COMPONENT_PROTOCOL_MISMATCH",
  }),
  Object.freeze({
    validator_id: "rule.settlement-value.nonnegative-minor-units/v1",
    validator_sha256: "5555555555555555555555555555555555555555555555555555555555555555",
    origin: "base",
    validate: (input: SettlementValueInput): string | null =>
      !protocolMatches(input.minor_units, expectedProtocols.minor_units)
        ? "COMPONENT_PROTOCOL_MISMATCH"
        : input.minor_units.normalized_value_sha256
          === "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
          ? "NEGATIVE_MINOR_UNITS" : null,
  }),
]);

const accountValidator: BoundValidator = Object.freeze({
  validator_id: "rule.settlement-value.account-active/v1",
  validator_sha256: "6666666666666666666666666666666666666666666666666666666666666666",
  origin: "extension",
  validate: (input: SettlementValueInput): string | null =>
    input.settlement_account.owned_value.active
      ? null : "INACTIVE_SETTLEMENT_ACCOUNT",
});

const tupleHash = (tuple: readonly string[]): string => tuple.join(":");

const createSettlementAccountValue = (
  input: SettlementValueInput["settlement_account"],
): SettlementAccountValue => {
  const protocolId = input.protocol_id;
  const protocolSha256 = input.protocol_sha256;
  const normalizedValueSha256 = input.normalized_value_sha256;
  return Object.freeze({
    protocol_id: protocolId,
    protocol_sha256: protocolSha256,
    account_ref: input.owned_value.account_ref,
    normalized_value_sha256: normalizedValueSha256,
    equals: (other: SettlementAccountValue): boolean =>
      protocolId === other.protocol_id
      && protocolSha256 === other.protocol_sha256
      && normalizedValueSha256 === other.normalized_value_sha256,
    hash: (): string => tupleHash([
      protocolId,
      protocolSha256,
      normalizedValueSha256,
    ]),
  });
};

export const createSettlementValueFactory = (
  mode: "base" | "with-account-active" = "base",
): SettlementValueFactory => {
  const validators = mode === "base" ? baseValidators
    : Object.freeze([...baseValidators, accountValidator]);
  const factoryRef = mode === "base" ? Object.freeze({
    factory_id: "factory.settlement-value.base/v1",
    factory_sha256: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    concept_id: "settlement.SettlementValue",
  }) : Object.freeze({
    factory_id: "factory.settlement-value.extended-validation/v1",
    factory_sha256: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    concept_id: "settlement.SettlementValue",
  });
  return Object.freeze({
    factory_ref: factoryRef,
    validators,
    create: (input: SettlementValueInput): FormationSuccess | ValidationFailure => {
      const trace: string[] = [];
      if (!protocolMatches(input.currency, expectedProtocols.currency)
          || !protocolMatches(input.minor_units, expectedProtocols.minor_units)
          || !protocolMatches(input.settlement_account,
            expectedProtocols.settlement_account)) {
        return Object.freeze({
          ok: false as const,
          value: null,
          failure_codes: Object.freeze(["COMPONENT_PROTOCOL_MISMATCH"]),
          validator_trace: Object.freeze(trace),
        });
      }
      for (const validator of validators) {
        trace.push(`${validator.validator_id}@${validator.validator_sha256}`);
        const failure = validator.validate(input);
        if (failure !== null) {
          return Object.freeze({
            ok: false as const,
            value: null,
            failure_codes: Object.freeze([failure]),
            validator_trace: Object.freeze(trace),
          });
        }
      }
      const settlementAccount = createSettlementAccountValue(
        input.settlement_account,
      );
      const tuple = Object.freeze([
        input.currency.normalized_value_sha256,
        input.minor_units.normalized_value_sha256,
        settlementAccount.normalized_value_sha256,
      ] as const);
      const componentBindings = Object.freeze([
        Object.freeze({component_name: "currency" as const,
          protocol_id: input.currency.protocol_id,
          protocol_sha256: input.currency.protocol_sha256,
          normalized_value_sha256: input.currency.normalized_value_sha256,
          nested_value_object: false}),
        Object.freeze({component_name: "minor_units" as const,
          protocol_id: input.minor_units.protocol_id,
          protocol_sha256: input.minor_units.protocol_sha256,
          normalized_value_sha256: input.minor_units.normalized_value_sha256,
          nested_value_object: false}),
        Object.freeze({component_name: "settlement_account" as const,
          protocol_id: settlementAccount.protocol_id,
          protocol_sha256: settlementAccount.protocol_sha256,
          normalized_value_sha256: settlementAccount.normalized_value_sha256,
          nested_value_object: true}),
      ]);
      const value = Object.freeze({
        tuple,
        component_bindings: componentBindings,
        settlement_account: settlementAccount,
        equals: (other: SettlementValue): boolean =>
          tuple[0] === other.tuple[0]
          && tuple[1] === other.tuple[1]
          && settlementAccount.equals(other.settlement_account),
        hash: (): string => tupleHash([
          tuple[0],
          tuple[1],
          settlementAccount.hash(),
        ]),
      });
      return Object.freeze({
        ok: true as const,
        value,
        failure_codes: Object.freeze([]) as readonly [],
        validator_trace: Object.freeze(trace),
      });
    },
    extendWithAccountActive: mode === "base"
      ? () => createSettlementValueFactory("with-account-active")
      : null,
  });
};

export const settlementValueProtocol = Object.freeze({
  protocol_id: "typescript.owned-value-object-factory/v1",
  concept_id: "settlement.SettlementValue",
  component_protocols: expectedProtocols,
  base_validator_count: 2,
  extension_policy: "additive-validation-only" as const,
  equality_mode: "complete-normalized-tuple" as const,
  hash_mode: "same-normalized-complete-tuple" as const,
  immutability_mode: "formed-and-recursive-owned-components" as const,
});
