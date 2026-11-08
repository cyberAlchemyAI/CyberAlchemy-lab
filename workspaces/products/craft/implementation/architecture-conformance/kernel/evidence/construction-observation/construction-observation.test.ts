import {describe, expect, it} from "vitest";

import type {
  ConstructionObservationV1,
  DeclaredConstructionContractV1,
  LockedConstructionObserverRefV1,
} from "./contracts.js";
import {
  decodeConstructionObservationV1,
  evaluateConstructionObservationV1,
  mintConstructionObservationV1,
} from "./construction-observation.js";

const digest = (character: string): string => character.repeat(64).slice(0, 64);
const definitionRef = Object.freeze({
  definition_id: "complete-value.kernel-fixture/v1",
  path: "fixture/complete-value-definition.json",
  sha256: digest("a"),
});
const observer: LockedConstructionObserverRefV1 = Object.freeze({
  role: "independent-construction-observer",
  observer_id: "observer.complete-value-kernel/v1",
  observer_sha256: digest("b"),
  owner_ref: "complete-value-kernel-owner",
  provider_id: "family-fixture.complete-value/v1",
  provider_sha256: digest("c"),
});
const baseFactory = Object.freeze({
  factory_id: "factory.complete-value.base/v1",
  factory_sha256: digest("d"),
  concept_id: "settlement.CompleteValue",
});
const extensionFactory = Object.freeze({
  factory_id: "factory.complete-value.extended/v1",
  factory_sha256: digest("e"),
  concept_id: "settlement.CompleteValue",
});
const components = Object.freeze([
  Object.freeze({
    component_name: "currency",
    protocol_id: "owned.string/v1",
    protocol_sha256: digest("1"),
    nested_value_object: false,
  }),
  Object.freeze({
    component_name: "account",
    protocol_id: "owned.account-value/v1",
    protocol_sha256: digest("2"),
    nested_value_object: true,
  }),
]);
const validators = Object.freeze([
  Object.freeze({
    validator_id: "rule.currency-supported/v1",
    validator_sha256: digest("3"),
    origin: "base" as const,
  }),
  Object.freeze({
    validator_id: "rule.account-open/v1",
    validator_sha256: digest("4"),
    origin: "extension" as const,
  }),
]);
const values: Readonly<Record<string, readonly [string, string]>> = Object.freeze({
  base: [digest("5"), digest("6")],
  copy: [digest("5"), digest("6")],
  "currency-variant": [digest("7"), digest("6")],
  "account-variant": [digest("5"), digest("8")],
  invalid: [digest("5"), digest("6")],
});
const validCaseIds = Object.freeze(["base", "copy", "currency-variant",
  "account-variant"]);
const contract: DeclaredConstructionContractV1 = Object.freeze({
  factory_ref: baseFactory,
  components,
  validators,
  cases: Object.freeze([
    ...validCaseIds.map((caseId) => Object.freeze({
      case_id: caseId,
      input_class: "valid" as const,
      expected_components: Object.freeze(components.map((component, index) =>
        Object.freeze({
          component_name: component.component_name,
          normalized_value_sha256: values[caseId]![index]!,
        }))),
      expected_failure_codes: Object.freeze([]),
    })),
    Object.freeze({
      case_id: "invalid",
      input_class: "invalid" as const,
      expected_components: Object.freeze(components.map((component, index) =>
        Object.freeze({
          component_name: component.component_name,
          normalized_value_sha256: values.invalid![index]!,
        }))),
      expected_failure_codes: Object.freeze(["CURRENCY_UNSUPPORTED"]),
    }),
  ]),
  equal_probe_ids: Object.freeze(["equal-copy"]),
  component_variant_probe_ids: Object.freeze({
    currency: "variant-currency",
    account: "variant-account",
  }),
  nested_component_names: Object.freeze(["account"]),
  extension_factory_ref: extensionFactory,
});

const formedAttempt = (caseId: string) => {
  const tupleValues = values[caseId];
  if (!tupleValues) throw new Error("TEST_CASE_UNKNOWN");
  const bindings = components.map((component, index) => ({
    ...component,
    normalized_value_sha256: tupleValues[index]!,
  }));
  return {
    case_id: caseId,
    input_class: "valid" as const,
    component_bindings: bindings,
    validator_trace: validators.map((validator, ordinal) => ({
      ...validator,
      ordinal,
      outcome: "pass" as const,
    })),
    formation_ordinal: validators.length,
    result: {status: "formed" as const, object_created: true, failure_codes: []},
    normalized_tuple: bindings.map(({component_name, normalized_value_sha256}) =>
      ({component_name, normalized_value_sha256})),
    immutability: {
      formed_value_frozen: true,
      recursively_owned_components_frozen: true,
      nested_alias_observed: false,
      nested_mutation_observed: false,
    },
  };
};

const makePositive = (): ConstructionObservationV1 =>
  mintConstructionObservationV1({
    schema_version: "ConstructionObservation/v1",
    observation_id: "observation.complete-value.kernel/v1",
    source_kind: "independent-family-fixture",
    observer_ref: observer,
    definition_ref: definitionRef,
    factory_ref: baseFactory,
    attempts: [
      ...validCaseIds.map(formedAttempt),
      {
        case_id: "invalid",
        input_class: "invalid",
        component_bindings: formedAttempt("base").component_bindings,
        validator_trace: [{...validators[0]!, ordinal: 0, outcome: "fail"}],
        formation_ordinal: null,
        result: {
          status: "validation-failure",
          object_created: false,
          failure_codes: ["CURRENCY_UNSUPPORTED"],
        },
        normalized_tuple: null,
        immutability: {
          formed_value_frozen: false,
          recursively_owned_components_frozen: false,
          nested_alias_observed: false,
          nested_mutation_observed: false,
        },
      },
    ],
    equality_probes: [
      {
        probe_id: "equal-copy",
        left_case_id: "base",
        right_case_id: "copy",
        relation: "equal-tuple",
        varied_component_name: null,
        references_distinct: true,
        observed_equal: true,
        left_hash_sha256: digest("9"),
        right_hash_sha256: digest("9"),
      },
      ...components.map(({component_name}, index) => ({
        probe_id: `variant-${component_name}`,
        left_case_id: "base",
        right_case_id: `${component_name}-variant`,
        relation: "component-variant" as const,
        varied_component_name: component_name,
        references_distinct: true,
        observed_equal: false,
        left_hash_sha256: digest("9"),
        right_hash_sha256: digest(index === 0 ? "0" : "f"),
      })),
    ],
    nested_delegations: [{
      component_name: "account",
      protocol_id: components[1]!.protocol_id,
      protocol_sha256: components[1]!.protocol_sha256,
      equality_delegated: true,
      hash_delegated: true,
    }],
    extension: {
      base_factory_ref: baseFactory,
      extension_factory_ref: extensionFactory,
      added_validators: [validators[1]!],
      altered_facets: [],
      cycle_detected: false,
    },
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false,
    authority_effect: "none",
  });

const bodyOf = (
  observation: ConstructionObservationV1,
): Omit<ConstructionObservationV1, "observation_sha256"> => {
  const {observation_sha256: _digest, ...body} = observation;
  return body;
};

describe("construction observation transport", () => {
  it("accepts a complete independently issued observation", () => {
    const positive = makePositive();
    const decoded = decodeConstructionObservationV1(JSON.stringify(positive));
    const result = evaluateConstructionObservationV1({
      locked_observer_ref: observer,
      locked_definition_ref: definitionRef,
      declared_contract: contract,
      observation: decoded,
    });
    expect(result.result).toBe("pass");
    expect(result.diagnostics).toEqual([]);
    expect(result.collision_freedom_claim).toBe(false);
    expect(result.claim)
      .toBe("construction-transport-evaluation-no-native-runtime-interception");
  });

  it("fails closed on digest drift and nested aliases", () => {
    const positive = makePositive();
    expect(() => decodeConstructionObservationV1(JSON.stringify({
      ...positive,
      observation_sha256: digest("0"),
    }))).toThrow("CONSTRUCTION_OBSERVATION_DIGEST_STALE");
    expect(() => decodeConstructionObservationV1(JSON.stringify({
      ...positive,
      attempts: positive.attempts.map((attempt, attemptIndex) => ({
        ...attempt,
        component_bindings: attempt.component_bindings.map((component, index) =>
          attemptIndex === 0 && index === 0 ? {...component, alias: true} : component),
      })),
    }))).toThrow("CONSTRUCTION_OBSERVATION_COMPONENT_SHAPE_INVALID");
  });

  it("detects semantic attacks even when the transport digest is current", () => {
    const positive = makePositive();
    const attacked = mintConstructionObservationV1({
      ...bodyOf(positive),
      source_kind: "mutated-construction-observation",
      observer_ref: {...observer, owner_ref: observer.provider_id},
      attempts: positive.attempts.map((attempt) => attempt.case_id === "invalid"
        ? {
          ...attempt,
          formation_ordinal: attempt.validator_trace.length,
          result: {status: "formed", object_created: true, failure_codes: []},
          normalized_tuple: formedAttempt("base").normalized_tuple,
        }
        : attempt.case_id === "base"
          ? {
            ...attempt,
            immutability: {...attempt.immutability, nested_alias_observed: true},
          }
          : attempt),
      equality_probes: positive.equality_probes.map((probe) =>
        probe.probe_id === "equal-copy"
          ? {...probe, references_distinct: false, observed_equal: false,
            right_hash_sha256: digest("a")}
          : probe),
      nested_delegations: positive.nested_delegations.map((delegation) =>
        ({...delegation, equality_delegated: false})),
      extension: {...positive.extension, altered_facets: ["declared-tuple"],
        cycle_detected: true},
    });
    const result = evaluateConstructionObservationV1({
      locked_observer_ref: observer,
      locked_definition_ref: definitionRef,
      declared_contract: contract,
      observation: attacked,
    });
    expect(result.result).toBe("fail");
    expect(result.diagnostics).toEqual(expect.arrayContaining([
      "CONSTRUCTION_OBSERVER_BINDING_MISMATCH",
      "CONSTRUCTION_OBSERVER_SELF_ISSUED",
      "CONSTRUCTION_INVALID_INPUT_FORMED",
      "CONSTRUCTION_REFERENCE_IDENTITY_OBSERVED",
      "CONSTRUCTION_EQUAL_TUPLE_UNEQUAL",
      "CONSTRUCTION_EQUAL_HASH_INCONGRUENT",
      "CONSTRUCTION_RECURSIVE_IMMUTABILITY_VIOLATION",
      "CONSTRUCTION_NESTED_DELEGATION_MISMATCH",
      "CONSTRUCTION_EXTENSION_NOT_ADDITIVE",
      "CONSTRUCTION_EXTENSION_CYCLE",
    ]));
  });

  it("binds self-consistent tuples and failure codes to exact owner cases", () => {
    const positive = makePositive();
    const fabricatedDigest = digest("0");
    const fabricatedTuple = mintConstructionObservationV1({
      ...bodyOf(positive),
      source_kind: "mutated-construction-observation",
      attempts: positive.attempts.map((attempt) => attempt.case_id === "base"
        ? {
          ...attempt,
          component_bindings: attempt.component_bindings.map((component, index) =>
            index === 0
              ? {...component, normalized_value_sha256: fabricatedDigest}
              : component),
          normalized_tuple: attempt.normalized_tuple?.map((component, index) =>
            index === 0
              ? {...component, normalized_value_sha256: fabricatedDigest}
              : component) ?? null,
        }
        : attempt),
    });
    const fabricatedResult = evaluateConstructionObservationV1({
      locked_observer_ref: observer,
      locked_definition_ref: definitionRef,
      declared_contract: contract,
      observation: fabricatedTuple,
    });
    expect(fabricatedResult.result).toBe("fail");
    expect(fabricatedResult.diagnostics).toEqual(expect.arrayContaining([
      "CONSTRUCTION_COMPONENT_VALUE_MISMATCH",
      "CONSTRUCTION_TUPLE_EXPECTATION_MISMATCH",
    ]));

    const wrongFailure = mintConstructionObservationV1({
      ...bodyOf(positive),
      source_kind: "mutated-construction-observation",
      attempts: positive.attempts.map((attempt) => attempt.case_id === "invalid"
        ? {...attempt, result: {...attempt.result,
          failure_codes: ["UNRELATED_NONEMPTY_FAILURE"]}}
        : attempt),
    });
    const failureResult = evaluateConstructionObservationV1({
      locked_observer_ref: observer,
      locked_definition_ref: definitionRef,
      declared_contract: contract,
      observation: wrongFailure,
    });
    expect(failureResult.result).toBe("fail");
    expect(failureResult.diagnostics)
      .toContain("CONSTRUCTION_FAILURE_CODE_MISMATCH");
  });
});
