import {createHash} from "node:crypto";

import type {
  ConstructionAttemptV1,
  ConstructionComponentBindingV1,
  ConstructionEqualityProbeV1,
  ConstructionExtensionEvidenceV1,
  ConstructionFactoryRefV1,
  ConstructionNestedDelegationV1,
  ConstructionObservationDiagnostic,
  ConstructionObservationEvaluationV1,
  ConstructionObservationV1,
  ConstructionValidatorRefV1,
  DeclaredConstructionContractV1,
  LockedConstructionObserverRefV1,
} from "./contracts.js";

type JsonObject = Record<string, unknown>;
type ConstructionObservationBodyV1 = Omit<ConstructionObservationV1,
"observation_sha256">;

const SHA256 = /^[a-f0-9]{64}$/u;
const IDENTIFIER = /^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$/u;
const compareUtf8 = (left: string, right: string): number =>
  Buffer.from(left).compare(Buffer.from(right));
const isRecord = (value: unknown): value is JsonObject =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const fail = (code: string): never => {
  const error = Object.assign(new Error(code), {code});
  error.name = "ConstructionObservationDecodeError";
  throw error;
};
const exactKeys = (
  source: JsonObject,
  expectedKeys: readonly string[],
  code: string,
): void => {
  const observed = Object.keys(source).sort(compareUtf8);
  const expected = [...expectedKeys].sort(compareUtf8);
  if (JSON.stringify(observed) !== JSON.stringify(expected)) fail(code);
};
const expectObject = (value: unknown, code: string): JsonObject =>
  isRecord(value) ? value : fail(code);
const expectString = (value: unknown, code: string): string =>
  typeof value === "string" && IDENTIFIER.test(value) ? value : fail(code);
const expectSha256 = (value: unknown, code: string): string =>
  typeof value === "string" && SHA256.test(value) ? value : fail(code);
const expectBoolean = (value: unknown, code: string): boolean =>
  typeof value === "boolean" ? value : fail(code);
const expectArray = (value: unknown, code: string): readonly unknown[] =>
  Array.isArray(value) ? value : fail(code);
const expectOrdinal = (value: unknown, code: string): number =>
  Number.isSafeInteger(value) && Number(value) >= 0 ? Number(value) : fail(code);
const canonicalValue = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (!isRecord(value)) return value;
  return Object.fromEntries(Object.entries(value)
    .sort(([left], [right]) => compareUtf8(left, right))
    .map(([key, child]) => [key, canonicalValue(child)]));
};
const deepFreeze = <Value>(value: Value): Readonly<Value> => {
  if (value === null || typeof value !== "object" || Object.isFrozen(value)) {
    return value;
  }
  Object.freeze(value);
  for (const child of Object.values(value)) deepFreeze(child);
  return value;
};

export const canonicalConstructionObservationJson = (value: unknown): string =>
  JSON.stringify(canonicalValue(value));
export const sha256ConstructionObservationBytes = (
  value: string | Uint8Array,
): string => createHash("sha256").update(value).digest("hex");

const decodeObserverRef = (value: unknown): LockedConstructionObserverRefV1 => {
  const source = expectObject(value, "CONSTRUCTION_OBSERVATION_OBSERVER_INVALID");
  exactKeys(source, ["role", "observer_id", "observer_sha256", "owner_ref",
    "provider_id", "provider_sha256"],
  "CONSTRUCTION_OBSERVATION_OBSERVER_SHAPE_INVALID");
  if (source.role !== "independent-construction-observer") {
    return fail("CONSTRUCTION_OBSERVATION_OBSERVER_INVALID");
  }
  return Object.freeze({
    role: "independent-construction-observer" as const,
    observer_id: expectString(source.observer_id,
      "CONSTRUCTION_OBSERVATION_OBSERVER_INVALID"),
    observer_sha256: expectSha256(source.observer_sha256,
      "CONSTRUCTION_OBSERVATION_OBSERVER_INVALID"),
    owner_ref: expectString(source.owner_ref,
      "CONSTRUCTION_OBSERVATION_OBSERVER_INVALID"),
    provider_id: expectString(source.provider_id,
      "CONSTRUCTION_OBSERVATION_OBSERVER_INVALID"),
    provider_sha256: expectSha256(source.provider_sha256,
      "CONSTRUCTION_OBSERVATION_OBSERVER_INVALID"),
  });
};

const decodeFactoryRef = (value: unknown): ConstructionFactoryRefV1 => {
  const source = expectObject(value, "CONSTRUCTION_OBSERVATION_FACTORY_INVALID");
  exactKeys(source, ["factory_id", "factory_sha256", "concept_id"],
    "CONSTRUCTION_OBSERVATION_FACTORY_SHAPE_INVALID");
  return Object.freeze({
    factory_id: expectString(source.factory_id,
      "CONSTRUCTION_OBSERVATION_FACTORY_INVALID"),
    factory_sha256: expectSha256(source.factory_sha256,
      "CONSTRUCTION_OBSERVATION_FACTORY_INVALID"),
    concept_id: expectString(source.concept_id,
      "CONSTRUCTION_OBSERVATION_FACTORY_INVALID"),
  });
};

const decodeComponent = (value: unknown): ConstructionComponentBindingV1 => {
  const source = expectObject(value, "CONSTRUCTION_OBSERVATION_COMPONENT_INVALID");
  exactKeys(source, ["component_name", "protocol_id", "protocol_sha256",
    "normalized_value_sha256", "nested_value_object"],
  "CONSTRUCTION_OBSERVATION_COMPONENT_SHAPE_INVALID");
  return Object.freeze({
    component_name: expectString(source.component_name,
      "CONSTRUCTION_OBSERVATION_COMPONENT_INVALID"),
    protocol_id: expectString(source.protocol_id,
      "CONSTRUCTION_OBSERVATION_COMPONENT_INVALID"),
    protocol_sha256: expectSha256(source.protocol_sha256,
      "CONSTRUCTION_OBSERVATION_COMPONENT_INVALID"),
    normalized_value_sha256: expectSha256(source.normalized_value_sha256,
      "CONSTRUCTION_OBSERVATION_COMPONENT_INVALID"),
    nested_value_object: expectBoolean(source.nested_value_object,
      "CONSTRUCTION_OBSERVATION_COMPONENT_INVALID"),
  });
};

const decodeValidator = (
  value: unknown,
  includeTrace: boolean,
): ConstructionValidatorRefV1 | ConstructionAttemptV1["validator_trace"][number] => {
  const source = expectObject(value, "CONSTRUCTION_OBSERVATION_VALIDATOR_INVALID");
  exactKeys(source, includeTrace
    ? ["validator_id", "validator_sha256", "origin", "ordinal", "outcome"]
    : ["validator_id", "validator_sha256", "origin"],
  "CONSTRUCTION_OBSERVATION_VALIDATOR_SHAPE_INVALID");
  if (source.origin !== "base" && source.origin !== "extension") {
    return fail("CONSTRUCTION_OBSERVATION_VALIDATOR_INVALID");
  }
  const core: ConstructionValidatorRefV1 = {
    validator_id: expectString(source.validator_id,
      "CONSTRUCTION_OBSERVATION_VALIDATOR_INVALID"),
    validator_sha256: expectSha256(source.validator_sha256,
      "CONSTRUCTION_OBSERVATION_VALIDATOR_INVALID"),
    origin: source.origin as "base" | "extension",
  };
  if (!includeTrace) return Object.freeze(core);
  if (source.outcome !== "pass" && source.outcome !== "fail") {
    return fail("CONSTRUCTION_OBSERVATION_VALIDATOR_INVALID");
  }
  return Object.freeze({
    ...core,
    ordinal: expectOrdinal(source.ordinal,
      "CONSTRUCTION_OBSERVATION_VALIDATOR_INVALID"),
    outcome: source.outcome,
  });
};

const decodeAttempt = (value: unknown): ConstructionAttemptV1 => {
  const source = expectObject(value, "CONSTRUCTION_OBSERVATION_ATTEMPT_INVALID");
  exactKeys(source, ["case_id", "input_class", "component_bindings",
    "validator_trace", "formation_ordinal", "result", "normalized_tuple",
    "immutability"], "CONSTRUCTION_OBSERVATION_ATTEMPT_SHAPE_INVALID");
  if (source.input_class !== "valid" && source.input_class !== "invalid") {
    return fail("CONSTRUCTION_OBSERVATION_ATTEMPT_INVALID");
  }
  const result = expectObject(source.result,
    "CONSTRUCTION_OBSERVATION_RESULT_INVALID");
  exactKeys(result, ["status", "object_created", "failure_codes"],
    "CONSTRUCTION_OBSERVATION_RESULT_SHAPE_INVALID");
  if (result.status !== "formed" && result.status !== "validation-failure") {
    return fail("CONSTRUCTION_OBSERVATION_RESULT_INVALID");
  }
  const failureCodes = expectArray(result.failure_codes,
    "CONSTRUCTION_OBSERVATION_RESULT_INVALID")
    .map((item) => expectString(item, "CONSTRUCTION_OBSERVATION_RESULT_INVALID"));
  const tuple = source.normalized_tuple === null ? null
    : expectArray(source.normalized_tuple,
      "CONSTRUCTION_OBSERVATION_TUPLE_INVALID").map((item) => {
      const entry = expectObject(item, "CONSTRUCTION_OBSERVATION_TUPLE_INVALID");
      exactKeys(entry, ["component_name", "normalized_value_sha256"],
        "CONSTRUCTION_OBSERVATION_TUPLE_SHAPE_INVALID");
      return Object.freeze({
        component_name: expectString(entry.component_name,
          "CONSTRUCTION_OBSERVATION_TUPLE_INVALID"),
        normalized_value_sha256: expectSha256(entry.normalized_value_sha256,
          "CONSTRUCTION_OBSERVATION_TUPLE_INVALID"),
      });
    });
  const immutability = expectObject(source.immutability,
    "CONSTRUCTION_OBSERVATION_IMMUTABILITY_INVALID");
  exactKeys(immutability, ["formed_value_frozen",
    "recursively_owned_components_frozen", "nested_alias_observed",
    "nested_mutation_observed"],
  "CONSTRUCTION_OBSERVATION_IMMUTABILITY_SHAPE_INVALID");
  return Object.freeze({
    case_id: expectString(source.case_id,
      "CONSTRUCTION_OBSERVATION_ATTEMPT_INVALID"),
    input_class: source.input_class,
    component_bindings: Object.freeze(expectArray(source.component_bindings,
      "CONSTRUCTION_OBSERVATION_COMPONENTS_INVALID").map(decodeComponent)),
    validator_trace: Object.freeze(expectArray(source.validator_trace,
      "CONSTRUCTION_OBSERVATION_VALIDATORS_INVALID").map((item) =>
      decodeValidator(item, true) as ConstructionAttemptV1["validator_trace"][number])),
    formation_ordinal: source.formation_ordinal === null ? null
      : expectOrdinal(source.formation_ordinal,
        "CONSTRUCTION_OBSERVATION_FORMATION_INVALID"),
    result: Object.freeze({
      status: result.status,
      object_created: expectBoolean(result.object_created,
        "CONSTRUCTION_OBSERVATION_RESULT_INVALID"),
      failure_codes: Object.freeze(failureCodes),
    }),
    normalized_tuple: tuple === null ? null : Object.freeze(tuple),
    immutability: Object.freeze({
      formed_value_frozen: expectBoolean(immutability.formed_value_frozen,
        "CONSTRUCTION_OBSERVATION_IMMUTABILITY_INVALID"),
      recursively_owned_components_frozen: expectBoolean(
        immutability.recursively_owned_components_frozen,
        "CONSTRUCTION_OBSERVATION_IMMUTABILITY_INVALID"),
      nested_alias_observed: expectBoolean(immutability.nested_alias_observed,
        "CONSTRUCTION_OBSERVATION_IMMUTABILITY_INVALID"),
      nested_mutation_observed: expectBoolean(immutability.nested_mutation_observed,
        "CONSTRUCTION_OBSERVATION_IMMUTABILITY_INVALID"),
    }),
  });
};

const decodeProbe = (value: unknown): ConstructionEqualityProbeV1 => {
  const source = expectObject(value, "CONSTRUCTION_OBSERVATION_PROBE_INVALID");
  exactKeys(source, ["probe_id", "left_case_id", "right_case_id", "relation",
    "varied_component_name", "references_distinct", "observed_equal",
    "left_hash_sha256", "right_hash_sha256"],
  "CONSTRUCTION_OBSERVATION_PROBE_SHAPE_INVALID");
  if (source.relation !== "equal-tuple" && source.relation !== "component-variant") {
    return fail("CONSTRUCTION_OBSERVATION_PROBE_INVALID");
  }
  return Object.freeze({
    probe_id: expectString(source.probe_id,
      "CONSTRUCTION_OBSERVATION_PROBE_INVALID"),
    left_case_id: expectString(source.left_case_id,
      "CONSTRUCTION_OBSERVATION_PROBE_INVALID"),
    right_case_id: expectString(source.right_case_id,
      "CONSTRUCTION_OBSERVATION_PROBE_INVALID"),
    relation: source.relation,
    varied_component_name: source.varied_component_name === null ? null
      : expectString(source.varied_component_name,
        "CONSTRUCTION_OBSERVATION_PROBE_INVALID"),
    references_distinct: expectBoolean(source.references_distinct,
      "CONSTRUCTION_OBSERVATION_PROBE_INVALID"),
    observed_equal: expectBoolean(source.observed_equal,
      "CONSTRUCTION_OBSERVATION_PROBE_INVALID"),
    left_hash_sha256: expectSha256(source.left_hash_sha256,
      "CONSTRUCTION_OBSERVATION_PROBE_INVALID"),
    right_hash_sha256: expectSha256(source.right_hash_sha256,
      "CONSTRUCTION_OBSERVATION_PROBE_INVALID"),
  });
};

const decodeDelegation = (value: unknown): ConstructionNestedDelegationV1 => {
  const source = expectObject(value,
    "CONSTRUCTION_OBSERVATION_DELEGATION_INVALID");
  exactKeys(source, ["component_name", "protocol_id", "protocol_sha256",
    "equality_delegated", "hash_delegated"],
  "CONSTRUCTION_OBSERVATION_DELEGATION_SHAPE_INVALID");
  return Object.freeze({
    component_name: expectString(source.component_name,
      "CONSTRUCTION_OBSERVATION_DELEGATION_INVALID"),
    protocol_id: expectString(source.protocol_id,
      "CONSTRUCTION_OBSERVATION_DELEGATION_INVALID"),
    protocol_sha256: expectSha256(source.protocol_sha256,
      "CONSTRUCTION_OBSERVATION_DELEGATION_INVALID"),
    equality_delegated: expectBoolean(source.equality_delegated,
      "CONSTRUCTION_OBSERVATION_DELEGATION_INVALID"),
    hash_delegated: expectBoolean(source.hash_delegated,
      "CONSTRUCTION_OBSERVATION_DELEGATION_INVALID"),
  });
};

const decodeExtension = (value: unknown): ConstructionExtensionEvidenceV1 => {
  const source = expectObject(value, "CONSTRUCTION_OBSERVATION_EXTENSION_INVALID");
  exactKeys(source, ["base_factory_ref", "extension_factory_ref",
    "added_validators", "altered_facets", "cycle_detected"],
  "CONSTRUCTION_OBSERVATION_EXTENSION_SHAPE_INVALID");
  return Object.freeze({
    base_factory_ref: decodeFactoryRef(source.base_factory_ref),
    extension_factory_ref: decodeFactoryRef(source.extension_factory_ref),
    added_validators: Object.freeze(expectArray(source.added_validators,
      "CONSTRUCTION_OBSERVATION_EXTENSION_INVALID").map((item) =>
      decodeValidator(item, false) as ConstructionValidatorRefV1)),
    altered_facets: Object.freeze(expectArray(source.altered_facets,
      "CONSTRUCTION_OBSERVATION_EXTENSION_INVALID").map((item) =>
      expectString(item, "CONSTRUCTION_OBSERVATION_EXTENSION_INVALID"))),
    cycle_detected: expectBoolean(source.cycle_detected,
      "CONSTRUCTION_OBSERVATION_EXTENSION_INVALID"),
  });
};

const decodeBody = (value: unknown): ConstructionObservationBodyV1 => {
  const source = expectObject(value, "CONSTRUCTION_OBSERVATION_INVALID");
  exactKeys(source, ["schema_version", "observation_id", "source_kind",
    "observer_ref", "definition_ref", "factory_ref", "attempts",
    "equality_probes", "nested_delegations", "extension", "claim",
    "collision_freedom_claim", "authority_effect"],
  "CONSTRUCTION_OBSERVATION_SHAPE_INVALID");
  if (source.schema_version !== "ConstructionObservation/v1"
      || (source.source_kind !== "independent-family-fixture"
        && source.source_kind !== "target-observation"
        && source.source_kind !== "mutated-construction-observation")
      || source.claim !== "transport-observation-only-no-native-runtime-claim"
      || source.collision_freedom_claim !== false
      || source.authority_effect !== "none") {
    return fail("CONSTRUCTION_OBSERVATION_POLICY_INVALID");
  }
  const definition = expectObject(source.definition_ref,
    "CONSTRUCTION_OBSERVATION_DEFINITION_REF_INVALID");
  exactKeys(definition, ["definition_id", "path", "sha256"],
    "CONSTRUCTION_OBSERVATION_DEFINITION_REF_SHAPE_INVALID");
  return Object.freeze({
    schema_version: "ConstructionObservation/v1" as const,
    observation_id: expectString(source.observation_id,
      "CONSTRUCTION_OBSERVATION_ID_INVALID"),
    source_kind: source.source_kind,
    observer_ref: decodeObserverRef(source.observer_ref),
    definition_ref: Object.freeze({
      definition_id: expectString(definition.definition_id,
        "CONSTRUCTION_OBSERVATION_DEFINITION_REF_INVALID"),
      path: expectString(definition.path,
        "CONSTRUCTION_OBSERVATION_DEFINITION_REF_INVALID"),
      sha256: expectSha256(definition.sha256,
        "CONSTRUCTION_OBSERVATION_DEFINITION_REF_INVALID"),
    }),
    factory_ref: decodeFactoryRef(source.factory_ref),
    attempts: Object.freeze(expectArray(source.attempts,
      "CONSTRUCTION_OBSERVATION_ATTEMPTS_INVALID").map(decodeAttempt)),
    equality_probes: Object.freeze(expectArray(source.equality_probes,
      "CONSTRUCTION_OBSERVATION_PROBES_INVALID").map(decodeProbe)),
    nested_delegations: Object.freeze(expectArray(source.nested_delegations,
      "CONSTRUCTION_OBSERVATION_DELEGATIONS_INVALID").map(decodeDelegation)),
    extension: decodeExtension(source.extension),
    claim: "transport-observation-only-no-native-runtime-claim" as const,
    collision_freedom_claim: false as const,
    authority_effect: "none" as const,
  });
};

const observationBody = (
  observation: ConstructionObservationV1,
): ConstructionObservationBodyV1 => {
  const {observation_sha256: _digest, ...body} = observation;
  return body;
};

export const mintConstructionObservationV1 = (
  input: ConstructionObservationBodyV1,
): ConstructionObservationV1 => {
  const body = decodeBody(input);
  return deepFreeze({
    ...body,
    observation_sha256: sha256ConstructionObservationBytes(
      canonicalConstructionObservationJson(body),
    ),
  }) as ConstructionObservationV1;
};

export const decodeConstructionObservationV1 = (
  bytes: string,
): ConstructionObservationV1 => {
  let decoded: unknown;
  try {
    decoded = JSON.parse(bytes);
  } catch {
    return fail("CONSTRUCTION_OBSERVATION_JSON_INVALID");
  }
  const source = expectObject(decoded, "CONSTRUCTION_OBSERVATION_INVALID");
  exactKeys(source, ["schema_version", "observation_id", "source_kind",
    "observer_ref", "definition_ref", "factory_ref", "attempts",
    "equality_probes", "nested_delegations", "extension", "claim",
    "collision_freedom_claim", "authority_effect", "observation_sha256"],
  "CONSTRUCTION_OBSERVATION_SHAPE_INVALID");
  const {observation_sha256, ...body} = source;
  const digest = expectSha256(observation_sha256,
    "CONSTRUCTION_OBSERVATION_DIGEST_INVALID");
  const minted = mintConstructionObservationV1(
    body as ConstructionObservationBodyV1,
  );
  if (minted.observation_sha256 !== digest) {
    return fail("CONSTRUCTION_OBSERVATION_DIGEST_STALE");
  }
  return minted;
};

const same = (left: unknown, right: unknown): boolean =>
  canonicalConstructionObservationJson(left) ===
    canonicalConstructionObservationJson(right);
const uniqueExact = (observed: readonly string[], expected: readonly string[]): boolean =>
  new Set(observed).size === observed.length
    && same([...observed].sort(compareUtf8), [...expected].sort(compareUtf8));
const push = (
  diagnostics: ConstructionObservationDiagnostic[],
  code: ConstructionObservationDiagnostic,
): void => {
  if (!diagnostics.includes(code)) diagnostics.push(code);
};

export const evaluateConstructionObservationV1 = (input: Readonly<{
  locked_observer_ref: LockedConstructionObserverRefV1;
  locked_definition_ref: ConstructionObservationV1["definition_ref"];
  declared_contract: DeclaredConstructionContractV1;
  observation: ConstructionObservationV1;
}>): ConstructionObservationEvaluationV1 => {
  const {locked_observer_ref: lockedObserver, locked_definition_ref: lockedDefinition,
    declared_contract: contract, observation} = input;
  if (sha256ConstructionObservationBytes(canonicalConstructionObservationJson(
    observationBody(observation),
  )) !== observation.observation_sha256) {
    return fail("CONSTRUCTION_OBSERVATION_DIGEST_STALE");
  }
  const diagnostics: ConstructionObservationDiagnostic[] = [];
  if (!same(lockedObserver, observation.observer_ref)) {
    push(diagnostics, "CONSTRUCTION_OBSERVER_BINDING_MISMATCH");
  }
  if (lockedObserver.owner_ref === lockedObserver.provider_id
      || observation.observer_ref.owner_ref === observation.observer_ref.provider_id) {
    push(diagnostics, "CONSTRUCTION_OBSERVER_SELF_ISSUED");
  }
  if (!same(lockedDefinition, observation.definition_ref)) {
    push(diagnostics, "CONSTRUCTION_DEFINITION_BINDING_MISMATCH");
  }
  if (!same(contract.factory_ref, observation.factory_ref)) {
    push(diagnostics, "CONSTRUCTION_FACTORY_BINDING_MISMATCH");
  }

  const expectedCases = contract.cases.map(({case_id}) => case_id);
  if (!uniqueExact(observation.attempts.map(({case_id}) => case_id), expectedCases)) {
    push(diagnostics, "CONSTRUCTION_CASE_LEDGER_MISMATCH");
  }
  const expectedCaseById = new Map(contract.cases.map((testCase) =>
    [testCase.case_id, testCase]));
  const attemptById = new Map(observation.attempts.map((attempt) =>
    [attempt.case_id, attempt]));
  const expectedComponentCore = contract.components.map((component) => ({...component}));
  const expectedValidatorCore = contract.validators.map((validator) => ({...validator}));
  for (const attempt of observation.attempts) {
    const expectedCase = expectedCaseById.get(attempt.case_id);
    if (expectedCase && attempt.input_class !== expectedCase.input_class) {
      push(diagnostics, "CONSTRUCTION_CASE_CLASS_MISMATCH");
    }
    const actualComponents = attempt.component_bindings.map((component) => ({
      component_name: component.component_name,
      protocol_id: component.protocol_id,
      protocol_sha256: component.protocol_sha256,
      nested_value_object: component.nested_value_object,
    }));
    if (!same(actualComponents, expectedComponentCore)
        || new Set(actualComponents.map(({component_name}) => component_name)).size
          !== expectedComponentCore.length) {
      push(diagnostics, "CONSTRUCTION_COMPONENT_PROTOCOL_MISMATCH");
    }
    const actualComponentValues = attempt.component_bindings.map((component) => ({
      component_name: component.component_name,
      normalized_value_sha256: component.normalized_value_sha256,
    }));
    if (expectedCase && !same(actualComponentValues,
      expectedCase.expected_components)) {
      push(diagnostics, "CONSTRUCTION_COMPONENT_VALUE_MISMATCH");
    }
    const traceCore = attempt.validator_trace.map((validator) => ({
      validator_id: validator.validator_id,
      validator_sha256: validator.validator_sha256,
      origin: validator.origin,
    }));
    const ordinalsValid = attempt.validator_trace.every((validator, index) =>
      validator.ordinal === index);
    const expectedInputClass = expectedCase?.input_class ?? attempt.input_class;
    const expectedTrace = expectedInputClass === "valid"
      ? expectedValidatorCore
      : expectedValidatorCore.slice(0, traceCore.length);
    const invalidTraceStopsAtFailure = expectedInputClass === "invalid"
      && attempt.validator_trace.length > 0
      && attempt.validator_trace.at(-1)?.outcome === "fail"
      && attempt.validator_trace.slice(0, -1).every(({outcome}) => outcome === "pass");
    if (!ordinalsValid || !same(traceCore, expectedTrace)
        || (expectedInputClass === "valid"
          && attempt.validator_trace.some(({outcome}) => outcome !== "pass"))
        || (expectedInputClass === "invalid" && !invalidTraceStopsAtFailure)) {
      push(diagnostics, "CONSTRUCTION_VALIDATOR_ORDER_MISMATCH");
    }
    if (expectedInputClass === "valid") {
      if (attempt.formation_ordinal !== attempt.validator_trace.length) {
        push(diagnostics, "CONSTRUCTION_FORMATION_ORDER_MISMATCH");
      }
      if (attempt.result.status !== "formed" || !attempt.result.object_created
          || attempt.result.failure_codes.length !== 0) {
        push(diagnostics, "CONSTRUCTION_VALID_INPUT_NOT_FORMED");
      }
      const expectedTuple = expectedCase?.expected_components
        ?? actualComponentValues;
      if (attempt.normalized_tuple === null
          || attempt.normalized_tuple.length !== contract.components.length) {
        push(diagnostics, "CONSTRUCTION_TUPLE_INCOMPLETE");
      }
      if (attempt.normalized_tuple !== null
          && !same(attempt.normalized_tuple, expectedTuple)) {
        push(diagnostics, "CONSTRUCTION_TUPLE_EXPECTATION_MISMATCH");
      }
      if (!attempt.immutability.formed_value_frozen
          || !attempt.immutability.recursively_owned_components_frozen
          || attempt.immutability.nested_alias_observed
          || attempt.immutability.nested_mutation_observed) {
        push(diagnostics, "CONSTRUCTION_RECURSIVE_IMMUTABILITY_VIOLATION");
      }
    } else {
      if (attempt.formation_ordinal !== null
          || attempt.result.status !== "validation-failure"
          || attempt.result.object_created
          || attempt.result.failure_codes.length === 0
          || attempt.normalized_tuple !== null) {
        push(diagnostics, "CONSTRUCTION_INVALID_INPUT_FORMED");
      }
      if (expectedCase && !same(attempt.result.failure_codes,
        expectedCase.expected_failure_codes)) {
        push(diagnostics, "CONSTRUCTION_FAILURE_CODE_MISMATCH");
      }
    }
  }

  const expectedProbeIds = [...contract.equal_probe_ids,
    ...Object.values(contract.component_variant_probe_ids)];
  if (!uniqueExact(observation.equality_probes.map(({probe_id}) => probe_id),
    expectedProbeIds)) {
    push(diagnostics, "CONSTRUCTION_CASE_LEDGER_MISMATCH");
  }
  for (const probe of observation.equality_probes) {
    const left = attemptById.get(probe.left_case_id);
    const right = attemptById.get(probe.right_case_id);
    if (!left || !right || left.normalized_tuple === null
        || right.normalized_tuple === null) {
      push(diagnostics, "CONSTRUCTION_TUPLE_INCOMPLETE");
      continue;
    }
    if (contract.equal_probe_ids.includes(probe.probe_id)) {
      if (probe.relation !== "equal-tuple" || probe.varied_component_name !== null
          || !same(left.normalized_tuple, right.normalized_tuple)) {
        push(diagnostics, "CONSTRUCTION_EQUAL_TUPLE_UNEQUAL");
      }
      if (!probe.references_distinct) {
        push(diagnostics, "CONSTRUCTION_REFERENCE_IDENTITY_OBSERVED");
      }
      if (!probe.observed_equal) {
        push(diagnostics, "CONSTRUCTION_EQUAL_TUPLE_UNEQUAL");
      }
      if (probe.left_hash_sha256 !== probe.right_hash_sha256) {
        push(diagnostics, "CONSTRUCTION_EQUAL_HASH_INCONGRUENT");
      }
      continue;
    }
    const componentEntry = Object.entries(contract.component_variant_probe_ids)
      .find(([, probeId]) => probeId === probe.probe_id);
    const componentName = componentEntry?.[0];
    const leftByName = new Map(left.normalized_tuple.map((entry) =>
      [entry.component_name, entry.normalized_value_sha256]));
    const rightByName = new Map(right.normalized_tuple.map((entry) =>
      [entry.component_name, entry.normalized_value_sha256]));
    const changed = contract.components.filter(({component_name}) =>
      leftByName.get(component_name) !== rightByName.get(component_name))
      .map(({component_name}) => component_name);
    if (!componentName || probe.relation !== "component-variant"
        || probe.varied_component_name !== componentName
        || !same(changed, [componentName]) || probe.observed_equal) {
      push(diagnostics, "CONSTRUCTION_COMPONENT_VARIANT_EQUAL");
    }
  }

  const expectedNested = contract.components.filter(({nested_value_object}) =>
    nested_value_object);
  if (!uniqueExact(observation.nested_delegations.map(({component_name}) =>
    component_name), contract.nested_component_names)) {
    push(diagnostics, "CONSTRUCTION_NESTED_DELEGATION_MISMATCH");
  }
  for (const nested of expectedNested) {
    const observed = observation.nested_delegations.find(({component_name}) =>
      component_name === nested.component_name);
    if (!observed || observed.protocol_id !== nested.protocol_id
        || observed.protocol_sha256 !== nested.protocol_sha256
        || !observed.equality_delegated || !observed.hash_delegated) {
      push(diagnostics, "CONSTRUCTION_NESTED_DELEGATION_MISMATCH");
    }
  }

  const expectedAdded = contract.validators.filter(({origin}) => origin === "extension");
  if (!same(observation.extension.base_factory_ref, contract.factory_ref)
      || !same(observation.extension.extension_factory_ref,
        contract.extension_factory_ref)) {
    push(diagnostics, "CONSTRUCTION_EXTENSION_BINDING_MISMATCH");
  }
  if (!same(observation.extension.added_validators, expectedAdded)
      || observation.extension.altered_facets.length !== 0) {
    push(diagnostics, "CONSTRUCTION_EXTENSION_NOT_ADDITIVE");
  }
  if (observation.extension.cycle_detected) {
    push(diagnostics, "CONSTRUCTION_EXTENSION_CYCLE");
  }

  const normalized = Object.freeze([...diagnostics].sort(compareUtf8));
  const evaluationCore = {
    schema_version: "ConstructionObservationEvaluation/v1" as const,
    observation_ref: {
      observation_id: observation.observation_id,
      observation_sha256: observation.observation_sha256,
    },
    result: normalized.length === 0 ? "pass" as const : "fail" as const,
    diagnostics: normalized,
    accounting: {
      declared_components: contract.components.length,
      observed_components_per_valid_case: observation.attempts.find(
        ({input_class}) => input_class === "valid",
      )?.component_bindings.length ?? 0,
      declared_validators: contract.validators.length,
      observed_attempts: observation.attempts.length,
      equality_probes: observation.equality_probes.length,
    },
    claim: "construction-transport-evaluation-no-native-runtime-interception" as const,
    collision_freedom_claim: false as const,
    authority_effect: "none" as const,
  };
  return deepFreeze({
    ...evaluationCore,
    evaluation_id: `evaluation.construction.${sha256ConstructionObservationBytes(
      canonicalConstructionObservationJson(evaluationCore),
    )}`,
  }) as ConstructionObservationEvaluationV1;
};
