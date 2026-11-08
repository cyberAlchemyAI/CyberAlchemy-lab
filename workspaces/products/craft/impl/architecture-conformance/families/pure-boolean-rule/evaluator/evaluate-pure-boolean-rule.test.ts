import {readFile, readdir} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

import {describe, expect, it} from "vitest";

import type {RuleHostileFixtureV1} from
  "../contracts/pure-boolean-rule-contracts.js";
import {applyRuleHostile} from "../mutations/apply-rule-hostile.js";
import {
  evaluatePureBooleanRuleProfile,
  PURE_BOOLEAN_RULE_BASELINE,
} from "./evaluate-pure-boolean-rule.js";

const here = dirname(fileURLToPath(import.meta.url));
const hostileRoot = resolve(here, "../hostiles");
const hostileContract = Object.freeze({
  "non-boolean-return.json": Object.freeze({
    hostile_id: "rule/non-boolean-return",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_NON_BOOLEAN_RETURN",
  }),
  "hidden-mutation.json": Object.freeze({
    hostile_id: "rule/hidden-mutation",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_HIDDEN_MUTATION",
  }),
  "external-effect.json": Object.freeze({
    hostile_id: "rule/external-effect",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_EXTERNAL_EFFECT",
  }),
  "missing-enforces-edge.json": Object.freeze({
    hostile_id: "rule/missing-enforces-edge",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_MISSING_ENFORCES_EDGE",
  }),
  "inverse-enforces-edge.json": Object.freeze({
    hostile_id: "rule/inverse-enforces-edge",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_INVERSE_ENFORCES_EDGE",
  }),
  "undeclared-dependency.json": Object.freeze({
    hostile_id: "rule/undeclared-dependency",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_UNDECLARED_DEPENDENCY",
  }),
  "rule-calls-operation.json": Object.freeze({
    hostile_id: "rule/rule-calls-operation",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_RULE_CALLS_OPERATION",
  }),
  "evaluation-order-dependence.json": Object.freeze({
    hostile_id: "rule/evaluation-order-dependence",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_EVALUATION_ORDER_DEPENDENCE",
  }),
  "unstable-input-binding.json": Object.freeze({
    hostile_id: "rule/unstable-input-binding",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_UNSTABLE_INPUT_BINDING",
  }),
  "exception-as-false.json": Object.freeze({
    hostile_id: "rule/exception-as-false",
    hostile_class: "type-semantic",
    expected_code: "RMT_RULE_EXCEPTION_AS_FALSE",
  }),
  "relation-owner-evidence-stale.json": Object.freeze({
    hostile_id: "rule/relation-owner-evidence-stale",
    hostile_class: "rel-a-evidence",
    expected_code: "RMT_RELATION_OWNER_EVIDENCE_STALE",
  }),
  "relation-source-endpoint-mismatch.json": Object.freeze({
    hostile_id: "rule/relation-source-endpoint-mismatch",
    hostile_class: "rel-a-evidence",
    expected_code: "RMT_RELATION_SOURCE_ENDPOINT_MISMATCH",
  }),
  "relation-target-endpoint-mismatch.json": Object.freeze({
    hostile_id: "rule/relation-target-endpoint-mismatch",
    hostile_class: "rel-a-evidence",
    expected_code: "RMT_RELATION_TARGET_ENDPOINT_MISMATCH",
  }),
  "materialized-without-exact-assertion.json": Object.freeze({
    hostile_id: "rule/materialized-without-exact-assertion",
    hostile_class: "rel-a-evidence",
    expected_code: "RMT_RELATION_ASSERTION_REQUIRED",
  }),
} as const);
const hostileFiles = Object.freeze(Object.keys(hostileContract));

const loadFixture = async (name: string): Promise<RuleHostileFixtureV1> =>
  JSON.parse(await readFile(resolve(hostileRoot, name), "utf8")) as
    RuleHostileFixtureV1;

describe("WP-RMT-002 pure boolean Rule hostile family", () => {
  it("accepts the strict deterministic effect-free baseline", () => {
    expect(evaluatePureBooleanRuleProfile(PURE_BOOLEAN_RULE_BASELINE)).toEqual({
      schema_version: "PureBooleanRuleEvaluation/v1",
      verdict: "pass",
      findings: [],
      authority_effect: "none",
    });
  });

  it("kills exactly 10 semantic and 4 REL-A non-noop hostiles", async () => {
    expect((await readdir(hostileRoot)).sort()).toEqual(
      [...hostileFiles].sort(),
    );
    const fixtures = await Promise.all(hostileFiles.map(loadFixture));
    expect(fixtures).toHaveLength(14);
    expect(fixtures.filter(({hostile_class: kind}) =>
      kind === "type-semantic")).toHaveLength(10);
    expect(fixtures.filter(({hostile_class: kind}) =>
      kind === "rel-a-evidence")).toHaveLength(4);
    expect(new Set(fixtures.map(({hostile_id: id}) => id)).size).toBe(14);
    for (const [index, fixture] of fixtures.entries()) {
      const name = hostileFiles[index]!;
      expect(fixture).toMatchObject(hostileContract[name]!);
      const mutated = applyRuleHostile(PURE_BOOLEAN_RULE_BASELINE, fixture);
      expect(mutated).not.toEqual(PURE_BOOLEAN_RULE_BASELINE);
      expect(evaluatePureBooleanRuleProfile(mutated)).toEqual({
        schema_version: "PureBooleanRuleEvaluation/v1",
        verdict: "fail",
        findings: [{code: hostileContract[name]!.expected_code}],
        authority_effect: "none",
      });
    }
  });
});
