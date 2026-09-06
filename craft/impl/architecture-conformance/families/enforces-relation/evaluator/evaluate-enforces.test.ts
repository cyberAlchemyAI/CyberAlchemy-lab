import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type {
  EnforcesObservationV1,
  EnforcesRelationDefinitionV1,
} from "../contracts/enforces-contracts.js";
import {
  applyEnforcesMutant,
  type EnforcesMutantV1,
} from "../mutations/apply-enforces-mutant.js";
import { evaluateEnforces } from "./evaluate-enforces.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixtureRoot = resolve(here, "../fixtures/settlement-rule-operation");

describe("independent Rule enforces Operation relation kit", () => {
  it("keeps the semantic edge separate and kills bypass/order mutants", async () => {
    const definition = JSON.parse(await readFile(resolve(fixtureRoot,
      "relation-definition.json"), "utf8")) as EnforcesRelationDefinitionV1;
    const catalogue = JSON.parse(await readFile(resolve(fixtureRoot,
      "mutants.json"), "utf8")) as { mutations: EnforcesMutantV1[] };
    const positive: EnforcesObservationV1 = Object.freeze({
      schema_version: "EnforcesObservation/v1",
      semantic_edge: definition.semantic_edge,
      architecture_facts: Object.freeze({
        rule_call_count: 1,
        operation_call_count: 1,
        trace: Object.freeze([
          "rule-call", "operation-call", "payout-write", "payout-created-event",
        ] as const),
      }),
      mutation_id: null,
      authority_effect: "none",
    });
    expect(evaluateEnforces({ definition, observation: positive }).verdict).toBe("pass");
    for (const mutant of catalogue.mutations) {
      const evaluation = evaluateEnforces({
        definition,
        observation: applyEnforcesMutant(positive, mutant),
      });
      expect(evaluation.verdict).toBe("fail");
      expect(evaluation.findings.map(({ code }) => code)).toContain(
        mutant.expected_finding_code,
      );
    }
    expect(positive.semantic_edge).not.toHaveProperty("trace");
    expect(positive.architecture_facts).not.toHaveProperty("definition_id");
  });
});
