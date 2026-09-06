import {
  canonicalConstructionObservationJson,
  sha256ConstructionObservationBytes,
} from "./construction-observation.js";
import type {
  ConstructionFactoryRefV1,
  ConstructionValidatorRefV1,
  LockedConstructionObserverRefV1,
} from "./contracts.js";
import {
  ENTITY_CONSTRUCTION_ROUTES,
  type DeclaredEntityLifecycleConstructionContractV1,
  type EntityConstructionRouteTraceV1,
  type EntityConstructionRouteV1,
  type EntityFactoryExtensionEvidenceV1,
  type EntityIdentityComponentV1,
  type EntityIdentityEqualityProbeV1,
  type EntityLifecycleConstructionDiagnostic,
  type EntityLifecycleConstructionEvaluationV1,
  type EntityLifecycleConstructionObservationV1,
  type EntityLifecycleSnapshotV1,
  type EntityValidationFailureProbeV1,
} from "./entity-lifecycle-contracts.js";

type JsonObject = Record<string, unknown>;
type ObservationBody = Omit<EntityLifecycleConstructionObservationV1,
"observation_sha256">;

const SHA256 = /^[a-f0-9]{64}$/u;
const IDENTIFIER = /^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$/u;
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isRecord = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: string): never => {
  const error = Object.assign(new Error(code), {code});
  error.name = "EntityLifecycleConstructionObservationDecodeError";
  throw error;
};
const exactKeys = (
  source: JsonObject,
  keys: readonly string[],
  code: string,
): void => {
  const actual = Object.keys(source).sort(compareUtf8);
  const expected = [...keys].sort(compareUtf8);
  if (JSON.stringify(actual) !== JSON.stringify(expected)) fail(code);
};
const object = (value: unknown, code: string): JsonObject =>
  isRecord(value) ? value : fail(code);
const array = (value: unknown, code: string): readonly unknown[] =>
  Array.isArray(value) ? value : fail(code);
const string = (value: unknown, code: string): string =>
  typeof value === "string" && IDENTIFIER.test(value) ? value : fail(code);
const sha = (value: unknown, code: string): string =>
  typeof value === "string" && SHA256.test(value) ? value : fail(code);
const boolean = (value: unknown, code: string): boolean =>
  typeof value === "boolean" ? value : fail(code);
const ordinal = (value: unknown, code: string): number =>
  Number.isSafeInteger(value) && Number(value) >= 0 ? Number(value) : fail(code);
const nullableOrdinal = (value: unknown, code: string): number | null =>
  value === null ? null : ordinal(value, code);
const unique = (values: readonly string[]): boolean =>
  new Set(values).size === values.length;
const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left)
    === canonicalConstructionObservationJson(right);
const deepFreeze = <Value>(value: Value): Readonly<Value> => {
  if (value === null || typeof value !== "object" || Object.isFrozen(value)) {
    return value;
  }
  Object.freeze(value);
  for (const child of Object.values(value)) deepFreeze(child);
  return value;
};

const decodeObserver = (value: unknown): LockedConstructionObserverRefV1 => {
  const source = object(value, "ENTITY_OBSERVATION_OBSERVER_INVALID");
  exactKeys(source, ["role", "observer_id", "observer_sha256", "owner_ref",
    "provider_id", "provider_sha256"], "ENTITY_OBSERVATION_OBSERVER_SHAPE_INVALID");
  if (source.role !== "independent-construction-observer") {
    return fail("ENTITY_OBSERVATION_OBSERVER_INVALID");
  }
  return Object.freeze({
    role: "independent-construction-observer" as const,
    observer_id: string(source.observer_id, "ENTITY_OBSERVATION_OBSERVER_INVALID"),
    observer_sha256: sha(source.observer_sha256,
      "ENTITY_OBSERVATION_OBSERVER_INVALID"),
    owner_ref: string(source.owner_ref, "ENTITY_OBSERVATION_OBSERVER_INVALID"),
    provider_id: string(source.provider_id, "ENTITY_OBSERVATION_OBSERVER_INVALID"),
    provider_sha256: sha(source.provider_sha256,
      "ENTITY_OBSERVATION_OBSERVER_INVALID"),
  });
};

const decodeFactory = (value: unknown): ConstructionFactoryRefV1 => {
  const source = object(value, "ENTITY_OBSERVATION_FACTORY_INVALID");
  exactKeys(source, ["factory_id", "factory_sha256", "concept_id"],
    "ENTITY_OBSERVATION_FACTORY_SHAPE_INVALID");
  return Object.freeze({
    factory_id: string(source.factory_id, "ENTITY_OBSERVATION_FACTORY_INVALID"),
    factory_sha256: sha(source.factory_sha256,
      "ENTITY_OBSERVATION_FACTORY_INVALID"),
    concept_id: string(source.concept_id, "ENTITY_OBSERVATION_FACTORY_INVALID"),
  });
};

const decodeValidator = (
  value: unknown,
  trace: boolean,
): ConstructionValidatorRefV1 | Readonly<ConstructionValidatorRefV1 & {
  ordinal: number;
  outcome: "pass" | "fail";
}> => {
  const source = object(value, "ENTITY_OBSERVATION_VALIDATOR_INVALID");
  exactKeys(source, trace
    ? ["validator_id", "validator_sha256", "origin", "ordinal", "outcome"]
    : ["validator_id", "validator_sha256", "origin"],
  "ENTITY_OBSERVATION_VALIDATOR_SHAPE_INVALID");
  if (source.origin !== "base" && source.origin !== "extension") {
    return fail("ENTITY_OBSERVATION_VALIDATOR_INVALID");
  }
  const core: ConstructionValidatorRefV1 = Object.freeze({
    validator_id: string(source.validator_id,
      "ENTITY_OBSERVATION_VALIDATOR_INVALID"),
    validator_sha256: sha(source.validator_sha256,
      "ENTITY_OBSERVATION_VALIDATOR_INVALID"),
    origin: source.origin,
  });
  if (!trace) return core;
  if (source.outcome !== "pass" && source.outcome !== "fail") {
    return fail("ENTITY_OBSERVATION_VALIDATOR_INVALID");
  }
  return Object.freeze({...core,
    ordinal: ordinal(source.ordinal, "ENTITY_OBSERVATION_VALIDATOR_INVALID"),
    outcome: source.outcome});
};

const decodeIdentity = (value: unknown): EntityIdentityComponentV1 => {
  const source = object(value, "ENTITY_OBSERVATION_IDENTITY_INVALID");
  exactKeys(source, ["component_name", "type_id", "type_sha256",
    "normalized_value_sha256"], "ENTITY_OBSERVATION_IDENTITY_SHAPE_INVALID");
  return Object.freeze({
    component_name: string(source.component_name,
      "ENTITY_OBSERVATION_IDENTITY_INVALID"),
    type_id: string(source.type_id, "ENTITY_OBSERVATION_IDENTITY_INVALID"),
    type_sha256: sha(source.type_sha256, "ENTITY_OBSERVATION_IDENTITY_INVALID"),
    normalized_value_sha256: sha(source.normalized_value_sha256,
      "ENTITY_OBSERVATION_IDENTITY_INVALID"),
  });
};

const route = (value: unknown): EntityConstructionRouteV1 =>
  typeof value === "string"
    && (ENTITY_CONSTRUCTION_ROUTES as readonly string[]).includes(value)
    ? value as EntityConstructionRouteV1
    : fail("ENTITY_OBSERVATION_ROUTE_INVALID");

const decodeRouteTrace = (value: unknown): EntityConstructionRouteTraceV1 => {
  const source = object(value, "ENTITY_OBSERVATION_ROUTE_INVALID");
  exactKeys(source, ["route_id", "input_class", "normalization_ordinal",
    "validator_trace", "identity_resolution_ordinal", "construction_ordinal",
    "immutability_ordinal", "direct_constructor_policy", "result"],
  "ENTITY_OBSERVATION_ROUTE_SHAPE_INVALID");
  if (source.input_class !== "valid") fail("ENTITY_OBSERVATION_ROUTE_INVALID");
  if (source.direct_constructor_policy !== "not-applicable"
      && source.direct_constructor_policy !== "private-inaccessible"
      && source.direct_constructor_policy !== "delegating-facade") {
    fail("ENTITY_OBSERVATION_ROUTE_INVALID");
  }
  const directConstructorPolicy = source.direct_constructor_policy as
    EntityConstructionRouteTraceV1["direct_constructor_policy"];
  const result = object(source.result, "ENTITY_OBSERVATION_ROUTE_RESULT_INVALID");
  exactKeys(result, ["status", "snapshot_created", "snapshot_id"],
    "ENTITY_OBSERVATION_ROUTE_RESULT_SHAPE_INVALID");
  if (result.status !== "formed" && result.status !== "constructor-inaccessible") {
    fail("ENTITY_OBSERVATION_ROUTE_RESULT_INVALID");
  }
  const status = result.status as EntityConstructionRouteTraceV1["result"]["status"];
  return Object.freeze({
    route_id: route(source.route_id),
    input_class: "valid" as const,
    normalization_ordinal: nullableOrdinal(source.normalization_ordinal,
      "ENTITY_OBSERVATION_ROUTE_INVALID"),
    validator_trace: Object.freeze(array(source.validator_trace,
      "ENTITY_OBSERVATION_ROUTE_INVALID").map((item) =>
      decodeValidator(item, true) as EntityConstructionRouteTraceV1["validator_trace"][number])),
    identity_resolution_ordinal: nullableOrdinal(source.identity_resolution_ordinal,
      "ENTITY_OBSERVATION_ROUTE_INVALID"),
    construction_ordinal: nullableOrdinal(source.construction_ordinal,
      "ENTITY_OBSERVATION_ROUTE_INVALID"),
    immutability_ordinal: nullableOrdinal(source.immutability_ordinal,
      "ENTITY_OBSERVATION_ROUTE_INVALID"),
    direct_constructor_policy: directConstructorPolicy,
    result: Object.freeze({
      status,
      snapshot_created: boolean(result.snapshot_created,
        "ENTITY_OBSERVATION_ROUTE_RESULT_INVALID"),
      snapshot_id: result.snapshot_id === null ? null
        : string(result.snapshot_id, "ENTITY_OBSERVATION_ROUTE_RESULT_INVALID"),
    }),
  });
};

const decodeFailure = (value: unknown): EntityValidationFailureProbeV1 => {
  const source = object(value, "ENTITY_OBSERVATION_FAILURE_INVALID");
  exactKeys(source, ["probe_id", "route_id", "validator_trace",
    "identity_resolution_ordinal", "construction_ordinal", "result"],
  "ENTITY_OBSERVATION_FAILURE_SHAPE_INVALID");
  if (source.route_id !== "factory") {
    fail("ENTITY_OBSERVATION_FAILURE_INVALID");
  }
  const result = object(source.result, "ENTITY_OBSERVATION_FAILURE_INVALID");
  exactKeys(result, ["status", "snapshot_created", "failure_codes"],
    "ENTITY_OBSERVATION_FAILURE_RESULT_SHAPE_INVALID");
  if (result.status !== "validation-failure") {
    fail("ENTITY_OBSERVATION_FAILURE_INVALID");
  }
  return Object.freeze({
    probe_id: string(source.probe_id, "ENTITY_OBSERVATION_FAILURE_INVALID"),
    route_id: "factory" as const,
    validator_trace: Object.freeze(array(source.validator_trace,
      "ENTITY_OBSERVATION_FAILURE_INVALID").map((item) =>
      decodeValidator(item, true) as EntityValidationFailureProbeV1["validator_trace"][number])),
    identity_resolution_ordinal: nullableOrdinal(source.identity_resolution_ordinal,
      "ENTITY_OBSERVATION_FAILURE_INVALID"),
    construction_ordinal: nullableOrdinal(source.construction_ordinal,
      "ENTITY_OBSERVATION_FAILURE_INVALID"),
    result: Object.freeze({
      status: "validation-failure" as const,
      snapshot_created: boolean(result.snapshot_created,
        "ENTITY_OBSERVATION_FAILURE_INVALID"),
      failure_codes: Object.freeze(array(result.failure_codes,
        "ENTITY_OBSERVATION_FAILURE_INVALID").map((item) =>
        string(item, "ENTITY_OBSERVATION_FAILURE_INVALID"))),
    }),
  });
};

const decodeSnapshot = (value: unknown): EntityLifecycleSnapshotV1 => {
  const source = object(value, "ENTITY_OBSERVATION_SNAPSHOT_INVALID");
  exactKeys(source, ["snapshot_id", "entity_case_id", "sequence", "route_id",
    "predecessor_snapshot_id", "identity", "state_sha256", "frozen",
    "mutation_observed"], "ENTITY_OBSERVATION_SNAPSHOT_SHAPE_INVALID");
  return Object.freeze({
    snapshot_id: string(source.snapshot_id, "ENTITY_OBSERVATION_SNAPSHOT_INVALID"),
    entity_case_id: string(source.entity_case_id,
      "ENTITY_OBSERVATION_SNAPSHOT_INVALID"),
    sequence: ordinal(source.sequence, "ENTITY_OBSERVATION_SNAPSHOT_INVALID"),
    route_id: route(source.route_id),
    predecessor_snapshot_id: source.predecessor_snapshot_id === null ? null
      : string(source.predecessor_snapshot_id,
        "ENTITY_OBSERVATION_SNAPSHOT_INVALID"),
    identity: Object.freeze(array(source.identity,
      "ENTITY_OBSERVATION_SNAPSHOT_INVALID").map(decodeIdentity)),
    state_sha256: sha(source.state_sha256,
      "ENTITY_OBSERVATION_SNAPSHOT_INVALID"),
    frozen: boolean(source.frozen, "ENTITY_OBSERVATION_SNAPSHOT_INVALID"),
    mutation_observed: boolean(source.mutation_observed,
      "ENTITY_OBSERVATION_SNAPSHOT_INVALID"),
  });
};

const decodeEqualityProbe = (value: unknown): EntityIdentityEqualityProbeV1 => {
  const source = object(value, "ENTITY_OBSERVATION_EQUALITY_INVALID");
  exactKeys(source, ["probe_id", "left_snapshot_id", "right_snapshot_id",
    "relation", "comparison_basis", "observed_equal", "left_hash_sha256",
    "right_hash_sha256"], "ENTITY_OBSERVATION_EQUALITY_SHAPE_INVALID");
  if (source.relation !== "same-identity-different-state"
      && source.relation !== "distinct-identity") {
    fail("ENTITY_OBSERVATION_EQUALITY_INVALID");
  }
  const relation = source.relation as EntityIdentityEqualityProbeV1["relation"];
  if (source.comparison_basis !== "canonical-identity-only") {
    fail("ENTITY_OBSERVATION_EQUALITY_INVALID");
  }
  return Object.freeze({
    probe_id: string(source.probe_id, "ENTITY_OBSERVATION_EQUALITY_INVALID"),
    left_snapshot_id: string(source.left_snapshot_id,
      "ENTITY_OBSERVATION_EQUALITY_INVALID"),
    right_snapshot_id: string(source.right_snapshot_id,
      "ENTITY_OBSERVATION_EQUALITY_INVALID"),
    relation,
    comparison_basis: "canonical-identity-only" as const,
    observed_equal: boolean(source.observed_equal,
      "ENTITY_OBSERVATION_EQUALITY_INVALID"),
    left_hash_sha256: sha(source.left_hash_sha256,
      "ENTITY_OBSERVATION_EQUALITY_INVALID"),
    right_hash_sha256: sha(source.right_hash_sha256,
      "ENTITY_OBSERVATION_EQUALITY_INVALID"),
  });
};

const decodeExtension = (value: unknown): EntityFactoryExtensionEvidenceV1 => {
  const source = object(value, "ENTITY_OBSERVATION_EXTENSION_INVALID");
  exactKeys(source, ["base_factory_ref", "extension_factory_ref",
    "base_validators_preserved", "added_validators",
    "identity_resolver_preserved", "altered_facets", "cycle_detected"],
  "ENTITY_OBSERVATION_EXTENSION_SHAPE_INVALID");
  return Object.freeze({
    base_factory_ref: decodeFactory(source.base_factory_ref),
    extension_factory_ref: decodeFactory(source.extension_factory_ref),
    base_validators_preserved: boolean(source.base_validators_preserved,
      "ENTITY_OBSERVATION_EXTENSION_INVALID"),
    added_validators: Object.freeze(array(source.added_validators,
      "ENTITY_OBSERVATION_EXTENSION_INVALID").map((item) =>
      decodeValidator(item, false) as ConstructionValidatorRefV1)),
    identity_resolver_preserved: boolean(source.identity_resolver_preserved,
      "ENTITY_OBSERVATION_EXTENSION_INVALID"),
    altered_facets: Object.freeze(array(source.altered_facets,
      "ENTITY_OBSERVATION_EXTENSION_INVALID").map((item) =>
      string(item, "ENTITY_OBSERVATION_EXTENSION_INVALID"))),
    cycle_detected: boolean(source.cycle_detected,
      "ENTITY_OBSERVATION_EXTENSION_INVALID"),
  });
};

const decodeBody = (value: unknown): ObservationBody => {
  const source = object(value, "ENTITY_OBSERVATION_INVALID");
  exactKeys(source, ["schema_version", "observation_id", "source_kind",
    "observer_ref", "definition_ref", "factory_ref", "route_traces",
    "validation_failure_probe", "snapshots", "equality_probes", "extension",
    "per_call_validator_supplied", "claim", "collision_freedom_claim",
    "authority_effect"], "ENTITY_OBSERVATION_SHAPE_INVALID");
  if (source.schema_version !== "EntityLifecycleConstructionObservation/v1"
      || (source.source_kind !== "independent-family-fixture"
        && source.source_kind !== "target-observation"
        && source.source_kind !== "mutated-entity-lifecycle-observation")
      || source.claim !== "transport-observation-only-no-native-runtime-claim"
      || source.collision_freedom_claim !== false
      || source.authority_effect !== "none") fail("ENTITY_OBSERVATION_POLICY_INVALID");
  const sourceKind = source.source_kind as ObservationBody["source_kind"];
  const definition = object(source.definition_ref,
    "ENTITY_OBSERVATION_DEFINITION_INVALID");
  exactKeys(definition, ["definition_id", "path", "sha256"],
    "ENTITY_OBSERVATION_DEFINITION_SHAPE_INVALID");
  return {
    schema_version: "EntityLifecycleConstructionObservation/v1",
    observation_id: string(source.observation_id, "ENTITY_OBSERVATION_ID_INVALID"),
    source_kind: sourceKind,
    observer_ref: decodeObserver(source.observer_ref),
    definition_ref: Object.freeze({
      definition_id: string(definition.definition_id,
        "ENTITY_OBSERVATION_DEFINITION_INVALID"),
      path: string(definition.path, "ENTITY_OBSERVATION_DEFINITION_INVALID"),
      sha256: sha(definition.sha256, "ENTITY_OBSERVATION_DEFINITION_INVALID"),
    }),
    factory_ref: decodeFactory(source.factory_ref),
    route_traces: Object.freeze(array(source.route_traces,
      "ENTITY_OBSERVATION_ROUTES_INVALID").map(decodeRouteTrace)),
    validation_failure_probe: decodeFailure(source.validation_failure_probe),
    snapshots: Object.freeze(array(source.snapshots,
      "ENTITY_OBSERVATION_SNAPSHOTS_INVALID").map(decodeSnapshot)),
    equality_probes: Object.freeze(array(source.equality_probes,
      "ENTITY_OBSERVATION_EQUALITY_INVALID").map(decodeEqualityProbe)),
    extension: decodeExtension(source.extension),
    per_call_validator_supplied: boolean(source.per_call_validator_supplied,
      "ENTITY_OBSERVATION_POLICY_INVALID"),
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false,
    authority_effect: "none",
  };
};

export const mintEntityLifecycleConstructionObservationV1 = (
  body: ObservationBody,
): EntityLifecycleConstructionObservationV1 => {
  const decoded = decodeBody(body);
  const observationSha256 = sha256ConstructionObservationBytes(
    canonicalConstructionObservationJson(decoded),
  );
  return deepFreeze({...decoded, observation_sha256: observationSha256});
};

export const decodeEntityLifecycleConstructionObservationV1 = (
  bytes: string,
): EntityLifecycleConstructionObservationV1 => {
  let parsed: unknown;
  try {
    parsed = JSON.parse(bytes);
  } catch {
    return fail("ENTITY_OBSERVATION_JSON_INVALID");
  }
  const source = object(parsed, "ENTITY_OBSERVATION_INVALID");
  exactKeys(source, ["schema_version", "observation_id", "source_kind",
    "observer_ref", "definition_ref", "factory_ref", "route_traces",
    "validation_failure_probe", "snapshots", "equality_probes", "extension",
    "per_call_validator_supplied", "claim", "collision_freedom_claim",
    "authority_effect", "observation_sha256"], "ENTITY_OBSERVATION_SHAPE_INVALID");
  const {observation_sha256: digest, ...body} = source;
  const decoded = decodeBody(body);
  const observed = sha(digest, "ENTITY_OBSERVATION_DIGEST_INVALID");
  const expected = sha256ConstructionObservationBytes(
    canonicalConstructionObservationJson(decoded),
  );
  if (observed !== expected) fail("ENTITY_OBSERVATION_DIGEST_STALE");
  return deepFreeze({...decoded, observation_sha256: observed});
};

const validatorCore = (value: ConstructionValidatorRefV1): unknown => ({
  validator_id: value.validator_id,
  validator_sha256: value.validator_sha256,
  origin: value.origin,
});

export const evaluateEntityLifecycleConstructionObservationV1 = (input: {
  readonly locked_observer_ref: LockedConstructionObserverRefV1;
  readonly locked_definition_ref: EntityLifecycleConstructionObservationV1["definition_ref"];
  readonly declared_contract: DeclaredEntityLifecycleConstructionContractV1;
  readonly observation: EntityLifecycleConstructionObservationV1;
}): EntityLifecycleConstructionEvaluationV1 => {
  const {observation, declared_contract: contract} = input;
  const diagnostics = new Set<EntityLifecycleConstructionDiagnostic>();
  const {observation_sha256: observedDigest, ...observationBody} = observation;
  const expectedDigest = sha256ConstructionObservationBytes(
    canonicalConstructionObservationJson(observationBody),
  );
  if (observedDigest !== expectedDigest) {
    diagnostics.add("ENTITY_OBSERVATION_DIGEST_MISMATCH");
  }
  if (!same(observation.observer_ref, input.locked_observer_ref)) {
    diagnostics.add("ENTITY_OBSERVER_BINDING_MISMATCH");
  }
  if (observation.observer_ref.owner_ref === observation.observer_ref.provider_id) {
    diagnostics.add("ENTITY_OBSERVER_SELF_ISSUED");
  }
  if (!same(observation.definition_ref, input.locked_definition_ref)) {
    diagnostics.add("ENTITY_DEFINITION_BINDING_MISMATCH");
  }
  if (!same(observation.factory_ref, contract.factory_ref)) {
    diagnostics.add("ENTITY_FACTORY_BINDING_MISMATCH");
  }

  const routes = observation.route_traces.map(({route_id}) => route_id);
  if (!unique(routes) || !same([...routes].sort(compareUtf8),
    [...contract.construction_routes].sort(compareUtf8))) {
    diagnostics.add("ENTITY_ROUTE_LEDGER_MISMATCH");
  }
  const snapshotById = new Map(observation.snapshots.map((item) =>
    [item.snapshot_id, item]));
  for (const trace of observation.route_traces) {
    const inaccessible = trace.route_id === "language-visible-direct-constructor"
      && trace.direct_constructor_policy === "private-inaccessible";
    if (trace.route_id === "language-visible-direct-constructor") {
      const validDirect = inaccessible
        ? trace.result.status === "constructor-inaccessible"
          && !trace.result.snapshot_created && trace.result.snapshot_id === null
          && trace.normalization_ordinal === null
          && trace.validator_trace.length === 0
          && trace.identity_resolution_ordinal === null
          && trace.construction_ordinal === null
          && trace.immutability_ordinal === null
        : trace.direct_constructor_policy === "delegating-facade";
      if (!validDirect) diagnostics.add("ENTITY_DIRECT_CONSTRUCTOR_BYPASS");
    } else if (trace.direct_constructor_policy !== "not-applicable") {
      diagnostics.add("ENTITY_DIRECT_CONSTRUCTOR_BYPASS");
    }
    if (inaccessible) continue;
    const traceValidators = trace.validator_trace.map(validatorCore);
    const expectedValidators = contract.validators.map(validatorCore);
    if (!same(traceValidators, expectedValidators)) {
      diagnostics.add("ENTITY_VALIDATOR_BINDING_MISMATCH");
    }
    if (trace.normalization_ordinal !== 0
        || trace.validator_trace.some((validator, index) =>
          validator.ordinal !== index + 1 || validator.outcome !== "pass")
        || contract.validators.some((validator, index) =>
          validator.origin === "base"
          && contract.validators.slice(0, index).some(({origin}) =>
            origin === "extension"))) {
      diagnostics.add("ENTITY_VALIDATOR_ORDER_MISMATCH");
    }
    const identityOrdinal = contract.validators.length + 1;
    if (trace.identity_resolution_ordinal !== identityOrdinal) {
      diagnostics.add("ENTITY_IDENTITY_RESOLUTION_ORDER_MISMATCH");
    }
    if (trace.construction_ordinal !== identityOrdinal + 1
        || trace.immutability_ordinal !== identityOrdinal + 2) {
      diagnostics.add("ENTITY_CONSTRUCTION_ORDER_MISMATCH");
    }
    if (trace.result.status !== "formed" || !trace.result.snapshot_created
        || trace.result.snapshot_id === null
        || !snapshotById.has(trace.result.snapshot_id)) {
      diagnostics.add("ENTITY_VALID_INPUT_NOT_ONE_SNAPSHOT");
    }
  }

  const failure = observation.validation_failure_probe;
  const failureTrace = failure.validator_trace.map(validatorCore);
  const expectedPrefix = contract.validators.slice(0, failureTrace.length)
    .map(validatorCore);
  if (!same(failureTrace, expectedPrefix)
      || failure.validator_trace.length === 0
      || failure.validator_trace.at(-1)?.outcome !== "fail"
      || failure.validator_trace.slice(0, -1).some(({outcome}) => outcome !== "pass")
      || failure.validator_trace.some((validator, index) =>
        validator.ordinal !== index + 1)) {
    diagnostics.add("ENTITY_VALIDATOR_ORDER_MISMATCH");
  }
  if (failure.result.snapshot_created || failure.identity_resolution_ordinal !== null
      || failure.construction_ordinal !== null) {
    diagnostics.add("ENTITY_INVALID_INPUT_FORMED_SNAPSHOT");
  }
  if (failure.probe_id !== contract.validation_failure.probe_id
      || !same(failure.result.failure_codes,
        contract.validation_failure.expected_failure_codes)) {
    diagnostics.add("ENTITY_FAILURE_CODE_MISMATCH");
  }

  const expectedSnapshotById = new Map(contract.snapshots.map((item) =>
    [item.snapshot_id, item]));
  if (!unique(observation.snapshots.map(({snapshot_id}) => snapshot_id))
      || observation.snapshots.length !== contract.snapshots.length) {
    diagnostics.add("ENTITY_SNAPSHOT_LEDGER_MISMATCH");
  }
  const identityShape = contract.identity_components.map((component) => ({
    component_name: component.component_name,
    type_id: component.type_id,
    type_sha256: component.type_sha256,
  }));
  for (const snapshot of observation.snapshots) {
    const expected = expectedSnapshotById.get(snapshot.snapshot_id);
    if (!expected || expected.entity_case_id !== snapshot.entity_case_id
        || expected.sequence !== snapshot.sequence
        || expected.route_id !== snapshot.route_id
        || expected.predecessor_snapshot_id !== snapshot.predecessor_snapshot_id
        || expected.state_sha256 !== snapshot.state_sha256) {
      diagnostics.add("ENTITY_SNAPSHOT_LEDGER_MISMATCH");
      continue;
    }
    if (!same(snapshot.identity.map(({normalized_value_sha256: _value, ...shape}) =>
      shape), identityShape)
        || !same(Object.fromEntries(snapshot.identity.map((component) =>
          [component.component_name, component.normalized_value_sha256])),
        expected.identity_values)) {
      diagnostics.add("ENTITY_IDENTITY_COMPONENT_MISMATCH");
    }
    if (!snapshot.frozen || snapshot.mutation_observed) {
      diagnostics.add("ENTITY_SNAPSHOT_MUTABLE");
    }
    if (snapshot.predecessor_snapshot_id !== null) {
      const predecessor = snapshotById.get(snapshot.predecessor_snapshot_id);
      if (!predecessor || predecessor.entity_case_id !== snapshot.entity_case_id
          || !same(predecessor.identity, snapshot.identity)) {
        diagnostics.add("ENTITY_IDENTITY_CHANGED_ACROSS_LIFECYCLE");
      }
    }
  }

  const probeById = new Map(observation.equality_probes.map((item) =>
    [item.probe_id, item]));
  if (!unique(observation.equality_probes.map(({probe_id}) => probe_id))
      || probeById.size !== contract.equality_probes.length) {
    diagnostics.add("ENTITY_IDENTITY_EQUALITY_MISMATCH");
  }
  for (const expected of contract.equality_probes) {
    const probe = probeById.get(expected.probe_id);
    const left = probe ? snapshotById.get(probe.left_snapshot_id) : undefined;
    const right = probe ? snapshotById.get(probe.right_snapshot_id) : undefined;
    if (!probe || !left || !right || probe.left_snapshot_id !== expected.left_snapshot_id
        || probe.right_snapshot_id !== expected.right_snapshot_id
        || probe.relation !== expected.relation
        || probe.comparison_basis !== "canonical-identity-only") {
      diagnostics.add("ENTITY_IDENTITY_EQUALITY_MISMATCH");
      continue;
    }
    if (probe.observed_equal !== expected.expected_equal) {
      diagnostics.add(expected.relation === "same-identity-different-state"
        ? "ENTITY_COMPLETE_FIELD_EQUALITY"
        : "ENTITY_IDENTITY_EQUALITY_MISMATCH");
      continue;
    }
    const identitiesEqual = same(left.identity, right.identity);
    if (expected.relation === "same-identity-different-state") {
      if (!identitiesEqual || left.state_sha256 === right.state_sha256
          || !probe.observed_equal) diagnostics.add("ENTITY_COMPLETE_FIELD_EQUALITY");
      if (probe.left_hash_sha256 !== probe.right_hash_sha256) {
        diagnostics.add("ENTITY_IDENTITY_HASH_INCONGRUENT");
      }
    } else if (identitiesEqual || probe.observed_equal) {
      diagnostics.add("ENTITY_IDENTITY_EQUALITY_MISMATCH");
    }
  }

  const extensions = contract.validators.filter(({origin}) => origin === "extension")
    .map(validatorCore);
  if (!same(observation.extension.base_factory_ref, contract.factory_ref)
      || !same(observation.extension.extension_factory_ref,
        contract.extension_factory_ref)) {
    diagnostics.add("ENTITY_EXTENSION_BINDING_MISMATCH");
  }
  if (!observation.extension.base_validators_preserved) {
    diagnostics.add("ENTITY_BASE_VALIDATOR_REMOVED");
  }
  if (!same(observation.extension.added_validators.map(validatorCore), extensions)) {
    diagnostics.add("ENTITY_VALIDATOR_BINDING_MISMATCH");
  }
  if (!observation.extension.identity_resolver_preserved) {
    diagnostics.add("ENTITY_IDENTITY_RESOLVER_REPLACED");
  }
  if (observation.extension.altered_facets.length > 0) {
    diagnostics.add("ENTITY_EXTENSION_NOT_ADDITIVE");
  }
  if (observation.extension.cycle_detected) diagnostics.add("ENTITY_EXTENSION_CYCLE");
  if (observation.per_call_validator_supplied) {
    diagnostics.add("ENTITY_PER_CALL_VALIDATOR_BYPASS");
  }

  const normalized = [...diagnostics].sort(compareUtf8);
  const observationRef = Object.freeze({
    observation_id: observation.observation_id,
    observation_sha256: observation.observation_sha256,
  });
  const evaluationId = sha256ConstructionObservationBytes(
    canonicalConstructionObservationJson({observationRef, diagnostics: normalized}),
  );
  return Object.freeze({
    schema_version: "EntityLifecycleConstructionEvaluation/v1" as const,
    evaluation_id: `evaluation.entity-lifecycle.${evaluationId}`,
    observation_ref: observationRef,
    result: normalized.length === 0 ? "pass" as const : "fail" as const,
    diagnostics: Object.freeze(normalized),
    accounting: Object.freeze({
      typed_identity_components: contract.identity_components.length,
      declared_validators: contract.validators.length,
      construction_routes: contract.construction_routes.length,
      lifecycle_snapshots: contract.snapshots.length,
      equality_probes: contract.equality_probes.length,
    }),
    claim:
      "entity-lifecycle-transport-evaluation-no-native-runtime-interception" as const,
    collision_freedom_claim: false as const,
    authority_effect: "none" as const,
  });
};
