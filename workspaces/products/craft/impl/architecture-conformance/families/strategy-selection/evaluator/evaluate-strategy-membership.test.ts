import {readFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {beforeAll, describe, expect, it} from "vitest";

import type {
  StrategyMembershipEvaluationInputV1,
} from "../contracts/strategy-selection-contracts.js";
import {applyStrategyMembershipMutant} from
  "../mutations/apply-strategy-membership-mutant.js";
import {
  decodeStrategyMembershipDenominatorV1,
  decodeStrategyMembershipMutationCatalogueV1,
  decodeStrategyMembershipObservationV1,
} from "../providers/decode-strategy-selection.js";
import {evaluateStrategyMembership} from "./evaluate-strategy-membership.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const familyRoot = resolve(here, "../fixtures/settlement-routing");
const descriptorPath =
  "projects/domainspec-v2/development/remaining-meta-types/admissions/policy/cross-language-realization-descriptor.json";
const cataloguePath =
  "projects/domainspec-v2/impl/architecture-conformance/families/strategy-selection/fixtures/settlement-routing/catalogue.json";

let input: StrategyMembershipEvaluationInputV1;
let mutationCatalogue: ReturnType<typeof decodeStrategyMembershipMutationCatalogueV1>;

beforeAll(async () => {
  const [catalogueBytes, denominatorBytes, observationBytes, mutationBytes, descriptorBytes] =
    await Promise.all([
      readFile(resolve(familyRoot, "catalogue.json"), "utf8"),
      readFile(resolve(familyRoot, "denominator.json"), "utf8"),
      readFile(resolve(familyRoot, "positive-membership.json"), "utf8"),
      readFile(resolve(familyRoot, "mutants.json"), "utf8"),
      readFile(resolve(repositoryRoot, descriptorPath), "utf8"),
    ]);
  const decoded = decodeStrategyMembershipDenominatorV1(
    denominatorBytes,
    catalogueBytes,
    cataloguePath,
    descriptorPath,
    descriptorBytes,
  );
  input = Object.freeze({
    catalogue: decoded.catalogue,
    denominator: decoded.denominator,
    observation: decodeStrategyMembershipObservationV1(observationBytes),
  });
  mutationCatalogue = decodeStrategyMembershipMutationCatalogueV1(mutationBytes);
});

describe("owner-bound strategy catalogue membership", () => {
  it("proves all eight membership decisions without selecting or executing a strategy", () => {
    const result = evaluateStrategyMembership(input);
    expect(result).toMatchObject({
      schema_version: "StrategyMembershipEvaluation/v1",
      verdict: "pass",
      positive_decision_accounting: {
        declared: 8,
        passed: 8,
        failed: 0,
        unaccounted: 0,
      },
      portable_claim: "owner-bound-current-data-only-strategy-membership",
      authority_effect: "none",
    });
    expect(result.findings).toEqual([]);
    expect(input.observation.selection_claim).toBe("none");
    expect(input.observation.execution_claim).toBe("none");
  });

  it("kills all ten independent catalogue and membership mutants", () => {
    expect(mutationCatalogue.mutations).toHaveLength(10);
    for (const mutation of mutationCatalogue.mutations) {
      const evaluation = evaluateStrategyMembership(
        applyStrategyMembershipMutant(input, mutation),
      );
      expect(evaluation.verdict, mutation.mutation_id).toBe("fail");
      const observed = new Set(evaluation.findings.map(({code}) => code));
      for (const expected of mutation.expected_finding_codes) {
        expect(observed.has(expected), `${mutation.mutation_id}:${expected}`).toBe(true);
      }
    }
  });

  it("keeps the owner catalogue non-empty, unique, data-only, and current", () => {
    expect(input.catalogue.members.map(({strategy_id: strategyId}) => strategyId)).toEqual([
      "settlement.route.standard",
      "settlement.route.expedited",
      "settlement.route.manual-review",
    ]);
    expect(new Set(input.catalogue.members.map(({strategy_id: strategyId}) => strategyId)).size)
      .toBe(3);
    expect(input.catalogue.members.every(({executable}) => executable === false)).toBe(true);
    expect(input.catalogue.membership_contract).toMatchObject({
      selection: "not-proven-by-membership",
      execution: "not-proven-by-membership",
    });
  });

  it("rejects stale content-addressed fixture bytes before evaluation", async () => {
    const observation = await readFile(resolve(familyRoot, "positive-membership.json"), "utf8");
    expect(() => decodeStrategyMembershipObservationV1(
      observation.replace("settlement.route.standard", "settlement.route.expedited"),
    )).toThrowError("FAMILY_POLICY_OBSERVATION_DIGEST_STALE");
  });
});
