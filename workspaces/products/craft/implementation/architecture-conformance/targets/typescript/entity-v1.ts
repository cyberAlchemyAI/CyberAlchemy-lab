type IdentityComponent = Readonly<{
  component_name: "organization_id" | "settlement_id";
  type_id: string;
  type_sha256: string;
  normalized_value_sha256: string;
}>;

type SettlementEntityInput = Readonly<{
  entity_case_id: string;
  snapshot_id: string;
  sequence: number;
  predecessor_snapshot_id: string | null;
  organization_id: Readonly<Omit<IdentityComponent, "component_name">>;
  settlement_id: Readonly<Omit<IdentityComponent, "component_name">>;
  owner_id: string;
  amount_minor_units: number;
  duplicate: boolean;
  state_sha256: string;
}>;

type ValidatorRef = Readonly<{
  validator_id: string;
  validator_sha256: string;
  origin: "base" | "extension";
}>;

type Validator = ValidatorRef & Readonly<{
  validate: (input: SettlementEntityInput) => string | null;
}>;

type ValidatorTrace = Readonly<ValidatorRef & {
  ordinal: number;
  outcome: "pass" | "fail";
}>;

type SettlementIdentity = readonly [IdentityComponent, IdentityComponent] &
  Readonly<{__brand: "SettlementIdentity"}>;

type SettlementEntity = Readonly<{
  entity_case_id: string;
  snapshot_id: string;
  sequence: number;
  predecessor_snapshot_id: string | null;
  identity: SettlementIdentity;
  owner_id: string;
  amount_minor_units: number;
  duplicate: boolean;
  state_sha256: string;
  equals: (other: SettlementEntity) => boolean;
  hash: () => string;
}>;

type RouteId = "factory" | "deserialization-reconstruction" |
  "lifecycle-transition";

type ConstructionTrace = Readonly<{
  route_id: RouteId;
  normalization_ordinal: 0;
  validator_trace: readonly ValidatorTrace[];
  identity_resolution_ordinal: number | null;
  construction_ordinal: number | null;
  immutability_ordinal: number | null;
}>;

type EntitySuccess = Readonly<{
  ok: true;
  value: SettlementEntity;
  failure_codes: readonly [];
  trace: ConstructionTrace;
}>;

type EntityFailure = Readonly<{
  ok: false;
  value: null;
  failure_codes: readonly string[];
  trace: ConstructionTrace;
}>;

type EntityResult = EntitySuccess | EntityFailure;

type SettlementEntityFactory = Readonly<{
  factory_ref: Readonly<{
    factory_id: string;
    factory_sha256: string;
    concept_id: "settlement.Settlement";
  }>;
  validators: readonly ValidatorRef[];
  identity_resolver_ref: Readonly<{
    resolver_id: "resolver.settlement.typed-composite-identity/v1";
    resolver_sha256: string;
  }>;
  create: (input: SettlementEntityInput) => EntityResult;
  reconstruct: (input: SettlementEntityInput) => EntityResult;
  transition: (
    previous: SettlementEntity,
    next: Readonly<{
      snapshot_id: string;
      state_sha256: string;
      amount_minor_units: number;
      duplicate: boolean;
    }>,
  ) => EntityResult;
  directConstructor: null;
  extendWithDuplicateBlocked: (() => SettlementEntityFactory) | null;
}>;

const organizationIdentityProtocol = Object.freeze({
  type_id: "identity.organization-id/v1",
  type_sha256: "1".repeat(64),
});

const settlementIdentityProtocol = Object.freeze({
  type_id: "identity.settlement-id/v1",
  type_sha256: "2".repeat(64),
});

const ownerMatchesValidator: Validator = Object.freeze({
  validator_id: "rule.settlement.owner-matches/v1",
  validator_sha256: "3".repeat(64),
  origin: "base",
  validate: (input: SettlementEntityInput): string | null =>
    input.owner_id === input.organization_id.normalized_value_sha256
      ? null : "OWNER_MISMATCH",
});

const amountValidValidator: Validator = Object.freeze({
  validator_id: "rule.settlement.amount-valid/v1",
  validator_sha256: "4".repeat(64),
  origin: "base",
  validate: (input: SettlementEntityInput): string | null =>
    Number.isSafeInteger(input.amount_minor_units)
      && input.amount_minor_units > 0 ? null : "AMOUNT_INVALID",
});

const duplicateBlockedValidator: Validator = Object.freeze({
  validator_id: "rule.settlement.duplicate-blocked/v1",
  validator_sha256: "5".repeat(64),
  origin: "extension",
  validate: (input: SettlementEntityInput): string | null =>
    input.duplicate ? "DUPLICATE_SETTLEMENT" : null,
});

const baseValidators: readonly Validator[] = Object.freeze([
  ownerMatchesValidator,
  amountValidValidator,
]);

const identityResolverRef = Object.freeze({
  resolver_id: "resolver.settlement.typed-composite-identity/v1" as const,
  resolver_sha256: "d".repeat(64),
});

const identityMatchesProtocol = (input: SettlementEntityInput): boolean =>
  input.organization_id.type_id === organizationIdentityProtocol.type_id
  && input.organization_id.type_sha256 === organizationIdentityProtocol.type_sha256
  && input.settlement_id.type_id === settlementIdentityProtocol.type_id
  && input.settlement_id.type_sha256 === settlementIdentityProtocol.type_sha256;

const resolveIdentity = (input: SettlementEntityInput): SettlementIdentity =>
  Object.freeze([
    Object.freeze({component_name: "organization_id" as const,
      ...input.organization_id}),
    Object.freeze({component_name: "settlement_id" as const,
      ...input.settlement_id}),
  ]) as unknown as SettlementIdentity;

const identityKey = (identity: SettlementIdentity): string => identity.map(
  ({component_name: name, type_id: typeId, type_sha256: typeSha256,
    normalized_value_sha256: value}) => `${name}:${typeId}:${typeSha256}:${value}`,
).join("|");

const formSnapshot = (
  input: SettlementEntityInput,
  identity: SettlementIdentity,
): SettlementEntity => {
  const key = identityKey(identity);
  return Object.freeze({
    entity_case_id: input.entity_case_id,
    snapshot_id: input.snapshot_id,
    sequence: input.sequence,
    predecessor_snapshot_id: input.predecessor_snapshot_id,
    identity,
    owner_id: input.owner_id,
    amount_minor_units: input.amount_minor_units,
    duplicate: input.duplicate,
    state_sha256: input.state_sha256,
    equals: (other: SettlementEntity): boolean => key === identityKey(other.identity),
    hash: (): string => key,
  });
};

const executeRoute = (
  routeId: RouteId,
  validators: readonly Validator[],
  input: SettlementEntityInput,
): EntityResult => {
  const validatorTrace: ValidatorTrace[] = [];
  if (!identityMatchesProtocol(input)) {
    return Object.freeze({ok: false as const, value: null,
      failure_codes: Object.freeze(["IDENTITY_PROTOCOL_MISMATCH"]),
      trace: Object.freeze({route_id: routeId, normalization_ordinal: 0 as const,
        validator_trace: Object.freeze(validatorTrace),
        identity_resolution_ordinal: null, construction_ordinal: null,
        immutability_ordinal: null})});
  }
  for (const validator of validators) {
    const failure = validator.validate(input);
    validatorTrace.push(Object.freeze({
      validator_id: validator.validator_id,
      validator_sha256: validator.validator_sha256,
      origin: validator.origin,
      ordinal: validatorTrace.length + 1,
      outcome: failure === null ? "pass" as const : "fail" as const,
    }));
    if (failure !== null) {
      return Object.freeze({ok: false as const, value: null,
        failure_codes: Object.freeze([failure]),
        trace: Object.freeze({route_id: routeId, normalization_ordinal: 0 as const,
          validator_trace: Object.freeze(validatorTrace),
          identity_resolution_ordinal: null, construction_ordinal: null,
          immutability_ordinal: null})});
    }
  }
  const identityResolutionOrdinal = validators.length + 1;
  const identity = resolveIdentity(input);
  const value = formSnapshot(input, identity);
  return Object.freeze({ok: true as const, value,
    failure_codes: Object.freeze([]) as readonly [],
    trace: Object.freeze({route_id: routeId, normalization_ordinal: 0 as const,
      validator_trace: Object.freeze(validatorTrace),
      identity_resolution_ordinal: identityResolutionOrdinal,
      construction_ordinal: identityResolutionOrdinal + 1,
      immutability_ordinal: identityResolutionOrdinal + 2})});
};

export const createSettlementEntityFactory = (
  mode: "base" | "with-duplicate-blocked" = "base",
): SettlementEntityFactory => {
  const validators = mode === "base" ? baseValidators
    : Object.freeze([...baseValidators, duplicateBlockedValidator]);
  const factoryRef = mode === "base" ? Object.freeze({
    factory_id: "factory.settlement-entity.base/v1",
    factory_sha256: "a".repeat(64),
    concept_id: "settlement.Settlement" as const,
  }) : Object.freeze({
    factory_id: "factory.settlement-entity.extended/v1",
    factory_sha256: "b".repeat(64),
    concept_id: "settlement.Settlement" as const,
  });
  const validatorRefs = Object.freeze(validators.map(({validate: _validate, ...ref}) =>
    Object.freeze(ref)));
  return Object.freeze({
    factory_ref: factoryRef,
    validators: validatorRefs,
    identity_resolver_ref: identityResolverRef,
    create: (input: SettlementEntityInput): EntityResult =>
      executeRoute("factory", validators, input),
    reconstruct: (input: SettlementEntityInput): EntityResult =>
      executeRoute("deserialization-reconstruction", validators, input),
    transition: (previous: SettlementEntity, next: Readonly<{
      snapshot_id: string;
      state_sha256: string;
      amount_minor_units: number;
      duplicate: boolean;
    }>): EntityResult => executeRoute("lifecycle-transition", validators, {
      entity_case_id: previous.entity_case_id,
      snapshot_id: next.snapshot_id,
      sequence: previous.sequence + 1,
      predecessor_snapshot_id: previous.snapshot_id,
      organization_id: previous.identity[0],
      settlement_id: previous.identity[1],
      owner_id: previous.owner_id,
      amount_minor_units: next.amount_minor_units,
      duplicate: next.duplicate,
      state_sha256: next.state_sha256,
    }),
    directConstructor: null,
    extendWithDuplicateBlocked: mode === "base"
      ? () => createSettlementEntityFactory("with-duplicate-blocked") : null,
  });
};

export const settlementEntityProtocol = Object.freeze({
  protocol_id: "typescript.validated-extensible-entity-factory/v1",
  concept_id: "settlement.Settlement",
  identity_components: Object.freeze([
    Object.freeze({component_name: "organization_id" as const,
      ...organizationIdentityProtocol}),
    Object.freeze({component_name: "settlement_id" as const,
      ...settlementIdentityProtocol}),
  ]),
  identity_stability: "stable-across-every-lifecycle-snapshot" as const,
  equality_mode: "canonical-identity-only" as const,
  hash_mode: "canonical-identity-only" as const,
  lifecycle_observation_mode: "immutable-snapshot-sequence" as const,
  extension_policy: "additive-only" as const,
  construction_routes: Object.freeze(["factory",
    "deserialization-reconstruction", "lifecycle-transition",
    "language-visible-direct-constructor"] as const),
  direct_constructor_policy: "private-inaccessible" as const,
});
