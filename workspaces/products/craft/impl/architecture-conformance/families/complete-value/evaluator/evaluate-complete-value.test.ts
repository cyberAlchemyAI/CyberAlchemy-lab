import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import {
  mintConstructionObservationV1,
  type LockedConstructionObserverRefV1,
} from "../../../kernel/evidence/construction-observation/index.js";
import type {
  CompleteValueDefinitionV1,
  CompleteValueDenominatorV1,
  CompleteValueMutationCatalogueV1,
  CompleteValueMutationV1,
  CompleteValueObservationV1,
} from "../contracts/complete-value-contracts.js";
import {applyCompleteValueMutant} from
  "../mutations/apply-complete-value-mutant.js";
import {
  decodeCompleteValueDefinitionV1,
  decodeCompleteValueDenominatorV1,
  decodeCompleteValueMutationCatalogueV1,
  decodeCompleteValueObservationV1,
  computeCompleteValueCatalogueSha256,
} from "../providers/decode-complete-value.js";
import {evaluateCompleteValue} from "./evaluate-complete-value.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixtureRoot = resolve(here, "../fixtures/settlement-value");
const repositoryRoot = resolve(here, "../../../../../../..");
const descriptorPath = "projects/domainspec-v2/development/remaining-meta-types/admissions/value-object/cross-language-realization-descriptor.json";
const definitionPath = "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/fixtures/settlement-value/definition.json";
const digest = (character: string): string => character.repeat(64).slice(0, 64);

const lockedObserver: LockedConstructionObserverRefV1 = Object.freeze({
  role: "independent-construction-observer",
  observer_id: "observer.complete-value-family-harness/v1",
  observer_sha256: digest("a"),
  owner_ref: "complete-value-family-proof-owner",
  provider_id: "family-fixture.settlement-value/v1",
  provider_sha256: digest("b"),
});

let definition: CompleteValueDefinitionV1;
let denominator: CompleteValueDenominatorV1;
let catalogue: CompleteValueMutationCatalogueV1;
let positive: CompleteValueObservationV1;
let definitionBytes: string;
let denominatorBytes: string;
let catalogueBytes: string;
let descriptorBytes: string;

beforeAll(async () => {
  [definitionBytes, denominatorBytes, catalogueBytes, descriptorBytes] =
    await Promise.all([
      readFile(resolve(fixtureRoot, "definition.json"), "utf8"),
      readFile(resolve(fixtureRoot, "denominator.json"), "utf8"),
      readFile(resolve(fixtureRoot, "mutants.json"), "utf8"),
      readFile(resolve(repositoryRoot, descriptorPath), "utf8"),
    ]);
  definition = decodeCompleteValueDefinitionV1(
    definitionBytes,
    descriptorPath,
    descriptorBytes,
  );
  denominator = decodeCompleteValueDenominatorV1(
    denominatorBytes,
    definitionBytes,
    definition,
    definitionPath,
  );
  catalogue = decodeCompleteValueMutationCatalogueV1(
    catalogueBytes,
    denominator,
    definition,
  );
  const attemptFor = (testCase: CompleteValueDefinitionV1["cases"][number]) => {
    const bindings = definition.components.map((component) => ({
      ...component,
      normalized_value_sha256:
        testCase.normalized_component_values[component.component_name]!,
    }));
    const failingValidatorIndex = testCase.input_class === "invalid" ? 1 : -1;
    const traceLength = failingValidatorIndex < 0
      ? definition.validators.length : failingValidatorIndex + 1;
    return {
      case_id: testCase.case_id,
      input_class: testCase.input_class,
      component_bindings: bindings,
      validator_trace: definition.validators.slice(0, traceLength)
        .map((validator, ordinal) => ({
          ...validator,
          ordinal,
          outcome: ordinal === failingValidatorIndex ? "fail" as const : "pass" as const,
        })),
      formation_ordinal: testCase.input_class === "valid"
        ? definition.validators.length : null,
      result: testCase.input_class === "valid"
        ? {status: "formed" as const, object_created: true, failure_codes: []}
        : {status: "validation-failure" as const, object_created: false,
          failure_codes: testCase.expected_failure_codes},
      normalized_tuple: testCase.input_class === "valid"
        ? bindings.map(({component_name, normalized_value_sha256}) =>
          ({component_name, normalized_value_sha256}))
        : null,
      immutability: {
        formed_value_frozen: testCase.input_class === "valid",
        recursively_owned_components_frozen: testCase.input_class === "valid",
        nested_alias_observed: false,
        nested_mutation_observed: false,
      },
    };
  };
  const hashForCase: Readonly<Record<string, string>> = Object.freeze({
    "settlement-base": digest("c"),
    "settlement-equal-copy": digest("c"),
    "settlement-currency-variant": digest("d"),
    "settlement-minor-units-variant": digest("e"),
    "settlement-account-variant": digest("f"),
  });
  positive = mintConstructionObservationV1({
    schema_version: "ConstructionObservation/v1",
    observation_id: "observation.complete-value.fixture.settlement-value/v1",
    source_kind: "independent-family-fixture",
    observer_ref: lockedObserver,
    definition_ref: denominator.owner_definition_ref,
    factory_ref: definition.factories.base,
    attempts: definition.cases.map(attemptFor),
    equality_probes: [
      {
        ...definition.equality_contract.equal_probe,
        relation: "equal-tuple",
        varied_component_name: null,
        references_distinct: true,
        observed_equal: true,
        left_hash_sha256:
          hashForCase[definition.equality_contract.equal_probe.left_case_id]!,
        right_hash_sha256:
          hashForCase[definition.equality_contract.equal_probe.right_case_id]!,
      },
      ...definition.equality_contract.component_variants.map((variant) => ({
        probe_id: variant.probe_id,
        left_case_id: variant.left_case_id,
        right_case_id: variant.right_case_id,
        relation: "component-variant" as const,
        varied_component_name: variant.component_name,
        references_distinct: true,
        observed_equal: false,
        left_hash_sha256: hashForCase[variant.left_case_id]!,
        right_hash_sha256: hashForCase[variant.right_case_id]!,
      })),
    ],
    nested_delegations: definition.components
      .filter(({nested_value_object}) => nested_value_object)
      .map((component) => ({
        component_name: component.component_name,
        protocol_id: component.protocol_id,
        protocol_sha256: component.protocol_sha256,
        equality_delegated: true,
        hash_delegated: true,
      })),
    extension: {
      base_factory_ref: definition.factories.base,
      extension_factory_ref: definition.factories.extension,
      added_validators: definition.validators.filter(({origin}) =>
        origin === "extension"),
      altered_facets: [],
      cycle_detected: false,
    },
    claim: "transport-observation-only-no-native-runtime-claim",
    collision_freedom_claim: false,
    authority_effect: "none",
  });
});

const remintCatalogueBytes = (
  mutations: readonly CompleteValueMutationV1[],
): string => {
  const parsed = JSON.parse(catalogueBytes) as CompleteValueMutationCatalogueV1;
  const {catalogue_sha256: _digest, ...body} = parsed;
  const remintedBody = {...body, mutations};
  return JSON.stringify({
    ...remintedBody,
    catalogue_sha256: computeCompleteValueCatalogueSha256(remintedBody),
  });
};

describe("complete immutable Value Object family", () => {
  it("keeps the real target lane expected-red until target/provider SWUs", async () => {
    const expectedRed = JSON.parse(await readFile(
      resolve(fixtureRoot, "expected-red.json"), "utf8",
    )) as Readonly<{
      observation: null;
      expected_verdict: "fail";
      expected_finding_codes: readonly string[];
    }>;
    const result = evaluateCompleteValue({
      definition,
      denominator,
      observation: expectedRed.observation,
      locked_observer_ref: lockedObserver,
    });
    expect(result.verdict).toBe(expectedRed.expected_verdict);
    expect(result.findings.map(({code}) => code))
      .toEqual(expectedRed.expected_finding_codes);
    expect(result.positive_decision_accounting).toEqual({
      declared: 7,
      passed: 0,
      failed: 7,
      unaccounted: 0,
    });
  });

  it("passes an independent family fixture at the transport-only ceiling", () => {
    const result = evaluateCompleteValue({
      definition,
      denominator,
      observation: positive,
      locked_observer_ref: lockedObserver,
    });
    expect(result.verdict).toBe("pass");
    expect(result.findings).toEqual([]);
    expect(result.positive_decision_accounting).toEqual({
      declared: 7, passed: 7, failed: 0, unaccounted: 0,
    });
    expect(result.hostile_class_accounting).toEqual({
      declared: 8, represented: 8, unrepresented: 0,
    });
    expect(result.native_runtime_claim).toBe(false);
    expect(result.collision_freedom_claim).toBe(false);
  });

  it("kills all 8 hostile classes, every tuple component, and nested attacks", () => {
    expect(new Set(catalogue.mutations.map(({hostile_class}) => hostile_class)).size)
      .toBe(8);
    const partialComponents = catalogue.mutations
      .filter(({mutation_kind}) => mutation_kind === "partial-tuple-equality")
      .map(({component_name}) => component_name);
    expect(partialComponents).toEqual(
      definition.components.map(({component_name}) => component_name),
    );
    expect(catalogue.mutations.filter(({mutation_kind}) =>
      mutation_kind === "nested-alias" || mutation_kind === "nested-mutation"))
      .toHaveLength(2);
    for (const mutation of catalogue.mutations) {
      const observed = applyCompleteValueMutant(positive, mutation);
      const result = evaluateCompleteValue({
        definition,
        denominator,
        observation: observed,
        locked_observer_ref: lockedObserver,
      });
      expect(result.verdict, mutation.mutation_id).toBe("fail");
      expect([...new Set(result.findings.map(({code}) => code))].sort(),
        mutation.mutation_id).toEqual([...mutation.expected_finding_codes].sort());
      expect(result.positive_decision_accounting.unaccounted).toBe(0);
    }
  });

  it("rejects provider self-authorship even if the payload is otherwise complete", () => {
    const selfIssued = mintConstructionObservationV1({
      ...(() => {
        const {observation_sha256: _digest, ...body} = positive;
        return body;
      })(),
      source_kind: "mutated-construction-observation",
      observer_ref: {...lockedObserver, owner_ref: lockedObserver.provider_id},
    });
    const result = evaluateCompleteValue({
      definition,
      denominator,
      observation: selfIssued,
      locked_observer_ref: lockedObserver,
    });
    expect(result.verdict).toBe("fail");
    expect(result.findings.map(({code}) => code))
      .toEqual(["FAMILY_VALUE_EVIDENCE_NOT_INDEPENDENT"]);
  });

  it("binds observed values and failures to owner-authored per-case expectations", () => {
    const {observation_sha256: _digest, ...body} = positive;
    const fabricatedDigest = digest("0");
    const fabricatedTuple = mintConstructionObservationV1({
      ...body,
      source_kind: "mutated-construction-observation",
      attempts: positive.attempts.map((attempt) =>
        attempt.case_id === "settlement-base"
          ? {
            ...attempt,
            component_bindings: attempt.component_bindings.map((component) =>
              component.component_name === "currency"
                ? {...component, normalized_value_sha256: fabricatedDigest}
                : component),
            normalized_tuple: attempt.normalized_tuple?.map((component) =>
              component.component_name === "currency"
                ? {...component, normalized_value_sha256: fabricatedDigest}
                : component) ?? null,
          }
          : attempt),
    });
    const fabricatedResult = evaluateCompleteValue({
      definition,
      denominator,
      observation: fabricatedTuple,
      locked_observer_ref: lockedObserver,
    });
    expect(fabricatedResult.verdict).toBe("fail");
    expect(fabricatedResult.findings.map(({code}) => code))
      .toContain("FAMILY_VALUE_CASE_LEDGER_MISMATCH");

    const wrongFailure = mintConstructionObservationV1({
      ...body,
      source_kind: "mutated-construction-observation",
      attempts: positive.attempts.map((attempt) =>
        attempt.case_id === "settlement-invalid-negative"
          ? {...attempt, result: {...attempt.result,
            failure_codes: ["UNRELATED_NONEMPTY_FAILURE"]}}
          : attempt),
    });
    const failureResult = evaluateCompleteValue({
      definition,
      denominator,
      observation: wrongFailure,
      locked_observer_ref: lockedObserver,
    });
    expect(failureResult.verdict).toBe("fail");
    expect(failureResult.findings.map(({code}) => code))
      .toContain("FAMILY_VALUE_INVALID_INPUT_FORMED");
  });

  it("rejects overcomplete, missing, and remapped mutation catalogues", () => {
    const first = catalogue.mutations[0]!;
    const overcomplete = [...catalogue.mutations, {
      ...first,
      mutation_id: "extra/reference-identity",
    }];
    expect(() => decodeCompleteValueMutationCatalogueV1(
      remintCatalogueBytes(overcomplete), denominator, definition,
    )).toThrow("FAMILY_VALUE_MUTATION_CATALOGUE_BLUEPRINT_INVALID");

    const missing = catalogue.mutations.filter(({mutation_id}) =>
      mutation_id !== "equality/partial-currency");
    expect(() => decodeCompleteValueMutationCatalogueV1(
      remintCatalogueBytes(missing), denominator, definition,
    )).toThrow("FAMILY_VALUE_MUTATION_CATALOGUE_BLUEPRINT_INVALID");

    const remapped = catalogue.mutations.map((mutation) => {
      if (mutation.mutation_id === "equality/reference-identity") {
        return {...mutation, hostile_class: "incongruent-hash" as const,
          mutation_kind: "incongruent-hash" as const};
      }
      if (mutation.mutation_id === "hash/equal-tuple-incongruent") {
        return {...mutation, hostile_class: "reference-identity" as const,
          mutation_kind: "reference-identity" as const};
      }
      return mutation;
    });
    expect(() => decodeCompleteValueMutationCatalogueV1(
      remintCatalogueBytes(remapped), denominator, definition,
    )).toThrow("FAMILY_VALUE_MUTATION_CATALOGUE_BLUEPRINT_INVALID");
  });

  it("fails closed on stale owner, denominator, catalogue, and nested shapes", () => {
    expect(() => decodeCompleteValueDefinitionV1(
      definitionBytes,
      descriptorPath,
      `${descriptorBytes}\n`,
    )).toThrow("FAMILY_VALUE_DEFINITION_DESCRIPTOR_REF_STALE");
    expect(() => decodeCompleteValueDenominatorV1(
      denominatorBytes.replace(denominator.denominator_sha256, digest("0")),
      definitionBytes,
      definition,
      definitionPath,
    )).toThrow("FAMILY_VALUE_DENOMINATOR_DIGEST_STALE");
    expect(() => decodeCompleteValueMutationCatalogueV1(
      catalogueBytes.replace(catalogue.catalogue_sha256, digest("0")),
      denominator,
      definition,
    )).toThrow("FAMILY_VALUE_MUTATION_CATALOGUE_DIGEST_STALE");
    expect(() => decodeCompleteValueObservationV1(JSON.stringify({
      ...positive,
      extension: {...positive.extension, nested_alias: true},
    }))).toThrow("CONSTRUCTION_OBSERVATION_EXTENSION_SHAPE_INVALID");
  });

  it("keeps owner expectations and target implementations outside evaluators", async () => {
    const [evaluatorSource, mutationSource] = await Promise.all([
      readFile(resolve(here, "evaluate-complete-value.ts"), "utf8"),
      readFile(resolve(here, "../mutations/apply-complete-value-mutant.ts"),
        "utf8"),
    ]);
    for (const source of [evaluatorSource, mutationSource]) {
      expect(source).not.toContain("fixtures/");
      expect(source).not.toContain("mutants.json");
      expect(source).not.toContain("expected_finding_codes");
      expect(source).not.toContain("targets/typescript");
      expect(source).not.toContain("targets/python");
      expect(source).not.toContain("targets/rust");
    }
  });
});
