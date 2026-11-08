import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import {
  EFFECT_CHANNELS,
  mintEffectObservationV1,
  type LockedEffectObserverRefV1,
} from "../../../kernel/evidence/effect-observation/index.js";
import type {
  ValueComputationDefinitionV1,
  ValueComputationDenominatorV1,
  ValueComputationMutationCatalogueV1,
  ValueComputationObservationV1,
} from "../contracts/value-computation-contracts.js";
import {applyValueComputationMutant} from
  "../mutations/apply-value-computation-mutant.js";
import {
  decodeValueComputationDefinitionV1,
  decodeValueComputationDenominatorV1,
  decodeValueComputationMutationCatalogueV1,
  decodeValueComputationObservationV1,
  mintValueComputationObservationV1,
  sha256CalculationInputs,
  sha256CalculationValue,
} from "../providers/decode-value-computation.js";
import {evaluateValueComputation} from "./evaluate-value-computation.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixtureRoot = resolve(here, "../fixtures/net-settlement");
const implRoot = process.cwd().endsWith("projects/domainspec-v2/impl")
  ? process.cwd()
  : resolve(here, "../../../../..");
const repositoryRoot = resolve(implRoot, "../../..");
const descriptorPath = "projects/domainspec-v2/development/remaining-meta-types/admissions/calculation/cross-language-realization-descriptor.json";
const definitionPath = "projects/domainspec-v2/impl/architecture-conformance/families/value-computation/fixtures/net-settlement/definition.json";
const digest = (character: string): string => character.repeat(64).slice(0, 64);

const lockedObserver: LockedEffectObserverRefV1 = Object.freeze({
  role: "independent-effect-observer",
  observer_id: "observer.calculation-family-harness/v1",
  observer_sha256: digest("a"),
  owner_ref: "calculation-family-proof-owner",
  provider_id: "family-fixture.calculation-net-settlement/v1",
  provider_sha256: digest("b"),
});

let definition: ValueComputationDefinitionV1;
let denominator: ValueComputationDenominatorV1;
let mutations: ValueComputationMutationCatalogueV1;
let positive: ValueComputationObservationV1;
let definitionBytes: string;
let denominatorBytes: string;
let mutationBytes: string;
let descriptorBytes: string;

beforeAll(async () => {
  [definitionBytes, denominatorBytes, mutationBytes, descriptorBytes] =
    await Promise.all([
      readFile(resolve(fixtureRoot, "definition.json"), "utf8"),
      readFile(resolve(fixtureRoot, "denominator.json"), "utf8"),
      readFile(resolve(fixtureRoot, "mutants.json"), "utf8"),
      readFile(resolve(repositoryRoot, descriptorPath), "utf8"),
    ]);
  definition = decodeValueComputationDefinitionV1(
    definitionBytes,
    descriptorPath,
    descriptorBytes,
  );
  denominator = decodeValueComputationDenominatorV1(
    denominatorBytes,
    definitionBytes,
    definition,
    definitionPath,
  );
  mutations = decodeValueComputationMutationCatalogueV1(mutationBytes, denominator);
  const targetId = "calculation.fixture.net-settlement/v1";
  positive = mintValueComputationObservationV1({
    schema_version: "ValueComputationObservation/v1",
    observation_id: "observation.calculation.fixture.net-settlement/v1",
    source_kind: "independent-family-fixture",
    target: {
      target_id: targetId,
      language: "family-fixture",
      protocol_id: "family.value-computation-observation/v1",
    },
    definition_ref: denominator.owner_definition_ref,
    binding: {
      descriptor_id: definition.descriptor_ref.descriptor_id,
      descriptor_sha256: definition.descriptor_ref.sha256,
      provider_id: lockedObserver.provider_id,
      provider_sha256: lockedObserver.provider_sha256,
    },
    cases: definition.cases.map((testCase) => {
      const resultSha = sha256CalculationValue(testCase.expected_value);
      return {
        case_id: testCase.case_id,
        input_sha256: sha256CalculationInputs(testCase.inputs),
        result_kind: testCase.expected_value === null
          ? "null" as const
          : typeof testCase.expected_value as "number" | "string",
        result_value: testCase.expected_value,
        result_sha256: resultSha,
        fresh_process_result_sha256: resultSha,
        process_isolation: "separate-process" as const,
      };
    }),
    effect_observation: mintEffectObservationV1({
      schema_version: "EffectObservation/v1",
      observation_id: "observation.effect.calculation.fixture.net-settlement/v1",
      source_kind: "independent-owner-observation",
      target_ref: {target_id: targetId, target_sha256: digest("c")},
      observer_ref: lockedObserver,
      channels: EFFECT_CHANNELS.map((channel) => ({
        channel,
        coverage: "supported" as const,
        read_count: 0,
        write_count: 0,
        escape_count: 0,
        deferred_count: 0,
      })),
      result: {consumption: "complete", mutable_alias_observed: false},
      quiescence: {observed: true, pending_count: 0},
      authority_effect: "none",
    }),
    authority_effect: "none",
  });
});

describe("independent value-computation Calculation denominator", () => {
  it("keeps the real target lane expected-red until a later provider SWU", async () => {
    const expectedRed = JSON.parse(await readFile(
      resolve(fixtureRoot, "expected-red.json"),
      "utf8",
    )) as Readonly<{
      observation: null;
      expected_verdict: "fail";
      expected_finding_codes: readonly string[];
    }>;
    const result = evaluateValueComputation({
      definition,
      denominator,
      observation: expectedRed.observation,
      locked_observer_ref: lockedObserver,
    });
    expect(result.verdict).toBe(expectedRed.expected_verdict);
    expect(result.findings.map(({code}) => code))
      .toEqual(expectedRed.expected_finding_codes);
    expect(result.positive_decision_accounting).toEqual({
      declared: 11,
      passed: 0,
      failed: 11,
      unaccounted: 0,
    });
  });

  it("accepts an independently constructed family observation at the bounded ceiling", () => {
    const result = evaluateValueComputation({
      definition,
      denominator,
      observation: positive,
      locked_observer_ref: lockedObserver,
    });
    expect(result.verdict).toBe("pass");
    expect(result.findings).toEqual([]);
    expect(result.positive_decision_accounting).toEqual({
      declared: 11,
      passed: 11,
      failed: 0,
      unaccounted: 0,
    });
    expect(result.portable_claim)
      .toBe("owner-bound-deterministic-zero-effect-value-under-declared-perimeter");
  });

  it("keeps all declared hostile classes red with exact independent findings", () => {
    expect(mutations.mutations).toHaveLength(13);
    expect(mutations.target_code_may_read_expected_findings).toBe(false);
    for (const mutation of mutations.mutations) {
      const observed = applyValueComputationMutant(positive, mutation);
      const result = evaluateValueComputation({
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

  it("fails closed on stale owner, denominator, observation, and mutation digests", () => {
    expect(() => decodeValueComputationDefinitionV1(
      definitionBytes,
      descriptorPath,
      `${descriptorBytes}\n`,
    )).toThrow("FAMILY_CALC_DEFINITION_DESCRIPTOR_REF_STALE");
    expect(() => decodeValueComputationDenominatorV1(
      denominatorBytes.replace(denominator.denominator_sha256, digest("0")),
      definitionBytes,
      definition,
      definitionPath,
    )).toThrow("FAMILY_CALC_DENOMINATOR_DIGEST_STALE");
    expect(() => decodeValueComputationObservationV1(JSON.stringify({
      ...positive,
      observation_sha256: digest("0"),
    }))).toThrow("FAMILY_CALC_OBSERVATION_DIGEST_STALE");
    expect(() => decodeValueComputationMutationCatalogueV1(
      mutationBytes.replace(mutations.catalogue_sha256, digest("0")),
      denominator,
    )).toThrow("FAMILY_CALC_MUTATION_CATALOGUE_DIGEST_STALE");
  });

  it("keeps owner expectations outside evaluator and mutation execution", async () => {
    const [evaluatorSource, mutationSource] = await Promise.all([
      readFile(resolve(here, "evaluate-value-computation.ts"), "utf8"),
      readFile(resolve(here,
        "../mutations/apply-value-computation-mutant.ts"), "utf8"),
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
