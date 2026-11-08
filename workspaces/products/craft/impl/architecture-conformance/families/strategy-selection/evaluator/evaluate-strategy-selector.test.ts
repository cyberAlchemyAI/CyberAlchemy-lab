import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import type {
  StrategySelectionEvaluationInputV1,
  StrategySelectionObservationV1,
} from "../contracts/strategy-selection-contracts.js";
import {applyStrategySelectorMutant} from
  "../mutations/apply-strategy-selector-mutant.js";
import {
  decodeStrategySelectionDenominatorV1,
  decodeStrategySelectionMutationCatalogueV1,
  decodeStrategySelectionObservationV1,
} from "../providers/decode-strategy-selector.js";
import {evaluateStrategySelector} from "./evaluate-strategy-selector.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const fixtureRoot = resolve(here, "../fixtures/settlement-routing");
const descriptorPath =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/policy/cross-language-realization-descriptor.json";
const cataloguePath =
  "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/catalogue.json";
const definitionPath =
  "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/selector-definition.json";

let input: StrategySelectionEvaluationInputV1;
let observation: StrategySelectionObservationV1;
let mutations: ReturnType<typeof decodeStrategySelectionMutationCatalogueV1>;

beforeAll(async () => {
  const [
    catalogueBytes,
    definitionBytes,
    denominatorBytes,
    observationBytes,
    mutationBytes,
    descriptorBytes,
  ] = await Promise.all([
    readFile(resolve(fixtureRoot, "catalogue.json"), "utf8"),
    readFile(resolve(fixtureRoot, "selector-definition.json"), "utf8"),
    readFile(resolve(fixtureRoot, "selector-denominator.json"), "utf8"),
    readFile(resolve(fixtureRoot, "positive-selector-observation.json"), "utf8"),
    readFile(resolve(fixtureRoot, "selector-mutants.json"), "utf8"),
    readFile(resolve(repositoryRoot, descriptorPath), "utf8"),
  ]);
  const decoded = decodeStrategySelectionDenominatorV1(
    denominatorBytes,
    definitionBytes,
    definitionPath,
    catalogueBytes,
    cataloguePath,
    descriptorPath,
    descriptorBytes,
  );
  observation = decodeStrategySelectionObservationV1(observationBytes);
  mutations = decodeStrategySelectionMutationCatalogueV1(mutationBytes);
  input = Object.freeze({
    catalogue: decoded.catalogue,
    definition: decoded.definition,
    denominator: decoded.denominator,
    observation,
    locked_effect_observer_ref: observation.effect_observation.observer_ref,
    locked_execution_observer_ref:
      observation.strategy_execution_observation.observer_ref,
    locked_selector_target_ref: Object.freeze({
      target_id: observation.target.target_id,
      target_sha256: observation.target.target_sha256,
    }),
  });
});

describe("owner-fixture Policy selector evidence", () => {
  it("proves fourteen distinct selector decisions without executing a strategy", () => {
    const evaluation = evaluateStrategySelector(input);
    expect(evaluation).toMatchObject({
      schema_version: "StrategySelectionEvaluation/v1",
      verdict: "pass",
      positive_decision_accounting: {
        declared: 14,
        passed: 14,
        failed: 0,
        unaccounted: 0,
      },
      portable_claim:
        "owner-bound-input-sensitive-zero-effect-strategy-identity-selection-without-strategy-execution",
      authority_effect: "none",
    });
    expect(evaluation.findings).toEqual([]);
    expect(observation.strategy_execution_observation).toMatchObject({
      coverage: "all-owner-declared-strategies",
      attempt_count: 0,
      attempted_strategy_ids: [],
      completion_count: 0,
    });
  });

  it("uses four single-input controlled pairs with different selected identities", () => {
    const definitionByCase = new Map(
      input.definition.cases.map((item) => [item.case_id, item]),
    );
    const observationByCase = new Map(
      observation.cases.map((item) => [item.case_id, item]),
    );
    expect(input.definition.sensitivity_pairs).toHaveLength(4);
    expect(new Set(input.definition.sensitivity_pairs
      .map(({changed_input_fact: fact}) => fact))).toEqual(new Set([
      "amount_minor",
      "expedite_limit_minor",
      "expedite_requested",
      "manual_review_required",
    ]));
    for (const pair of input.definition.sensitivity_pairs) {
      const leftDefinition = definitionByCase.get(pair.left_case_id);
      const rightDefinition = definitionByCase.get(pair.right_case_id);
      const leftObservation = observationByCase.get(pair.left_case_id);
      const rightObservation = observationByCase.get(pair.right_case_id);
      expect(leftDefinition).toBeDefined();
      expect(rightDefinition).toBeDefined();
      expect(leftObservation).toBeDefined();
      expect(rightObservation).toBeDefined();
      const changed = Object.keys(leftDefinition?.inputs ?? {}).filter((name) =>
        JSON.stringify(leftDefinition?.inputs[name]) !==
        JSON.stringify(rightDefinition?.inputs[name]));
      expect(changed).toEqual([pair.changed_input_fact]);
      expect(leftObservation?.selected_strategy_id)
        .not.toBe(rightObservation?.selected_strategy_id);
    }
  });

  it("binds all evidence to one target and a complete twelve-channel perimeter", () => {
    expect(observation.effect_observation.target_ref).toEqual({
      target_id: observation.target.target_id,
      target_sha256: observation.target.target_sha256,
    });
    expect(observation.strategy_execution_observation.target_ref)
      .toEqual(observation.effect_observation.target_ref);
    expect(observation.effect_observation.channels).toHaveLength(12);
    expect(observation.effect_observation.channels.every((channel) =>
      channel.coverage === "supported" && channel.read_count === 0 &&
      channel.write_count === 0 && channel.escape_count === 0 &&
      channel.deferred_count === 0)).toBe(true);
    expect(observation.effect_observation.quiescence).toEqual({
      observed: true,
      pending_count: 0,
    });
  });

  it("kills all sixteen independent selector, effect, and execution mutants", () => {
    expect(mutations.mutations).toHaveLength(16);
    for (const mutation of mutations.mutations) {
      const evaluation = evaluateStrategySelector({
        ...input,
        observation: applyStrategySelectorMutant(observation, mutation),
      });
      expect(evaluation.verdict, mutation.mutation_id).toBe("fail");
      const observedCodes = new Set(evaluation.findings.map(({code}) => code));
      for (const expected of mutation.expected_finding_codes) {
        expect(observedCodes.has(expected),
          `${mutation.mutation_id}:${expected}`).toBe(true);
      }
    }
  });

  it("fails closed on stale content-addressed selector bytes", async () => {
    const bytes = await readFile(
      resolve(fixtureRoot, "positive-selector-observation.json"),
      "utf8",
    );
    expect(() => decodeStrategySelectionObservationV1(
      bytes.replace("branch.expedited", "branch.standard"),
    )).toThrow("FAMILY_POLICY_SELECTOR_OBSERVATION_DIGEST_STALE");
  });
});
