import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { beforeAll, describe, expect, it } from "vitest";

import {
  createValidatedHandle,
  readValidatedHandle,
  type ValidatedHandle,
} from "../../../kernel/contracts/validated-handle.js";
import type {
  RuleObservationV1,
  RuleObligationCatalogueV1,
} from "../contracts/rule-contracts.js";
import { applyRuleSemanticMutant } from "../mutations/apply-semantic-mutant.js";
import {
  canonicalRuleJson,
  decodeRuleBindingV1,
  decodeRuleCaseCatalogueV1,
  decodeRuleDefinitionV1,
  normalizeRulePackageV1,
  type NormalizedRulePackageV1,
} from "../providers/decode-rule-contracts.js";
import {
  decodeRuleMutationCatalogueV1,
  decodeRuleObligationCatalogueV1,
} from "../providers/decode-rule-obligations.js";
import { evaluateRule } from "./evaluate-rule.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = process.cwd();
const fixtureRoot = resolve(here, "../fixtures/can-settle-payout");
const sha256 = (value: string): string => createHash("sha256")
  .update(value, "utf8").digest("hex");

let rule: ValidatedHandle<NormalizedRulePackageV1>;
let obligations: ValidatedHandle<RuleObligationCatalogueV1>;
let positive: RuleObservationV1;
let mutationBytes: string;

const mintObservation = (value: RuleObservationV1) => createValidatedHandle({
  value,
  source_sha256: value.observation_sha256,
  validated_refs: [],
});
const observation = (
  overrides: Partial<RuleObservationV1> = {},
): RuleObservationV1 => {
  const body: Omit<RuleObservationV1, "observation_sha256"> = {
    schema_version: "RuleObservation/v1",
    binding_id: "can-settle-payout.typescript/v1",
    source_sha256: "2a68541d798f2e964b4d9afd5ff2c0a5d301191e004b893206127ade627ea4b2",
    symbol_name: "canSettlePayout",
    case_observations: [
      { case_id: "first-payout-allowed", outcome: true, observed_effect_count: 0 },
      { case_id: "duplicate-payout-denied", outcome: false, observed_effect_count: 0 },
      { case_id: "zero-amount-denied", outcome: false, observed_effect_count: 0 },
    ],
    unsupported: [],
    authority_effect: "none",
    ...overrides,
  };
  return Object.freeze({
    ...body,
    observation_sha256: sha256(canonicalRuleJson(body)),
  });
};

beforeAll(async () => {
  const [definitionBytes, bindingBytes, caseBytes, obligationBytes, mutants] =
    await Promise.all([
      readFile(resolve(fixtureRoot, "rule-definition.json"), "utf8"),
      readFile(resolve(fixtureRoot, "typescript-binding.json"), "utf8"),
      readFile(resolve(fixtureRoot, "cases.json"), "utf8"),
      readFile(resolve(fixtureRoot, "obligations.json"), "utf8"),
      readFile(resolve(fixtureRoot, "mutants.json"), "utf8"),
    ]);
  const definition = decodeRuleDefinitionV1(definitionBytes);
  const binding = await decodeRuleBindingV1(
    bindingBytes,
    definition,
    (path) => readFile(resolve(repositoryRoot, path)),
  );
  const cases = decodeRuleCaseCatalogueV1(caseBytes, definition);
  rule = normalizeRulePackageV1(definition, binding, cases);
  obligations = decodeRuleObligationCatalogueV1(obligationBytes, rule);
  mutationBytes = mutants;
  positive = observation();
});

describe("independent Rule evaluator", () => {
  it("accepts the exact binding, outcomes, and effect-free observations", () => {
    const result = evaluateRule({ rule, obligations, observation: mintObservation(positive) });
    expect(result.verdict).toBe("pass");
    expect(result.findings).toEqual([]);
    expect(result.evaluation_id).toMatch(/^evaluation\.rule\.[a-f0-9]{64}$/u);
  });

  it("kills all three required semantic mutant classes with exact IDs", () => {
    const catalogue = readValidatedHandle(
      decodeRuleMutationCatalogueV1(mutationBytes, rule),
    );
    expect(catalogue.mutations.map(({ mutation_id: id }) => id)).toEqual([
      "wrong-result/first-payout",
      "bypass-check/duplicate-payout",
      "observable-effect/first-payout",
    ]);
    for (const mutant of catalogue.mutations) {
      const mutated = applyRuleSemanticMutant(positive, mutant);
      expect(mutated.observation_sha256).toMatch(/^[a-f0-9]{64}$/u);
      const result = evaluateRule({
        rule,
        obligations,
        observation: mintObservation(mutated),
      });
      expect(result.verdict).toBe("fail");
      expect(result.findings).toEqual([{
        code: mutant.expected_finding_code,
        case_id: mutant.case_id,
        expected: mutant.defect === "observable-effect" ? null :
          mutant.defect === "bypass-check" ? false : true,
        observed: mutant.defect === "observable-effect" ? 1 :
          mutant.defect === "bypass-check" ? true : false,
      }]);
    }
  });

  it.each([
    ["missing binding", { binding_id: null, source_sha256: null, symbol_name: null }, "RULE_BINDING_MISSING"],
    ["stale binding", { binding_id: "stale" }, "RULE_BINDING_STALE"],
    ["unsupported observation", { unsupported: ["dynamic-import"] }, "RULE_OBSERVATION_UNSUPPORTED"],
  ] as const)("fails closed for %s", (_name, overrides, code) => {
    const result = evaluateRule({
      rule,
      obligations,
      observation: mintObservation(observation(overrides)),
    });
    expect(result.findings.map(({ code: findingCode }) => findingCode)).toContain(code);
  });

  it("distinguishes missing, duplicate, unexpected, and non-boolean outcomes", () => {
    const malformed = observation({
      case_observations: [
        { case_id: "first-payout-allowed", outcome: "yes", observed_effect_count: 0 },
        { case_id: "duplicate-payout-denied", outcome: false, observed_effect_count: 0 },
        { case_id: "duplicate-payout-denied", outcome: false, observed_effect_count: 0 },
        { case_id: "foreign", outcome: true, observed_effect_count: 0 },
      ],
    });
    const result = evaluateRule({ rule, obligations, observation: mintObservation(malformed) });
    expect(result.findings.map(({ code }) => code)).toEqual([
      "RULE_OUTCOME_DUPLICATE",
      "RULE_OUTCOME_MISSING",
      "RULE_OUTCOME_NON_BOOLEAN",
      "RULE_OUTCOME_UNEXPECTED",
    ]);
  });
});
