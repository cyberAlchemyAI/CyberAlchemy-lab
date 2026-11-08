import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { readValidatedHandle } from "../../../kernel/contracts/validated-handle.js";
import {
  decodeRuleBindingV1,
  decodeRuleCaseCatalogueV1,
  decodeRuleDefinitionV1,
  normalizeRulePackageV1,
} from "./decode-rule-contracts.js";

const here = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(here, "../../../../../../..");
const fixtureRoot = resolve(here, "../fixtures/can-settle-payout");
const readFixture = (name: string): Promise<string> =>
  readFile(resolve(fixtureRoot, name), "utf8");
const sourceResolver = (path: string) => readFile(resolve(repositoryRoot, path));

const prepare = async () => {
  const [definitionBytes, bindingBytes, casesBytes] = await Promise.all([
    readFixture("rule-definition.json"),
    readFixture("typescript-binding.json"),
    readFixture("cases.json"),
  ]);
  const definition = decodeRuleDefinitionV1(definitionBytes);
  return { definitionBytes, bindingBytes, casesBytes, definition } as const;
};

describe("Rule definition, binding, and case codecs", () => {
  it("recomputes exact refs and normalizes only validated handles", async () => {
    const value = await prepare();
    const binding = await decodeRuleBindingV1(
      value.bindingBytes,
      value.definition,
      sourceResolver,
    );
    const cases = decodeRuleCaseCatalogueV1(value.casesBytes, value.definition);
    const normalized = readValidatedHandle(normalizeRulePackageV1(
      value.definition,
      binding,
      cases,
    ));
    expect(normalized.definition.rule_id).toBe("can-settle-payout");
    expect(normalized.binding.current).toBe(true);
    expect(normalized.cases.cases.map(({ case_id: id }) => id)).toEqual([
      "duplicate-payout-denied",
      "first-payout-allowed",
      "zero-amount-denied",
    ]);
  });

  it("rejects stale definition and binding refs", async () => {
    const value = await prepare();
    const staleDefinition = JSON.parse(value.definitionBytes);
    staleDefinition.definition_sha256 = "0".repeat(64);
    expect(() => decodeRuleDefinitionV1(JSON.stringify(staleDefinition)))
      .toThrow("RULE_DEFINITION_DIGEST_STALE");

    const notCurrent = JSON.parse(value.bindingBytes);
    notCurrent.current = false;
    await expect(decodeRuleBindingV1(
      JSON.stringify(notCurrent),
      value.definition,
      sourceResolver,
    )).rejects.toThrow("RULE_BINDING_NOT_CURRENT");

    const staleSource = JSON.parse(value.bindingBytes);
    staleSource.source_ref.sha256 = "0".repeat(64);
    await expect(decodeRuleBindingV1(
      JSON.stringify(staleSource),
      value.definition,
      sourceResolver,
    )).rejects.toThrow("RULE_BINDING_SOURCE_STALE");
  });

  it.each([
    ["non-boolean outcome", (value: any) => {
      value.cases[0].expected_outcome = "yes";
    }, "RULE_CASE_OUTCOME_NON_BOOLEAN"],
    ["duplicate id", (value: any) => {
      value.cases[1].case_id = value.cases[0].case_id;
    }, "RULE_CASE_DUPLICATE"],
    ["duplicate input", (value: any) => {
      value.cases[1].input = value.cases[0].input;
    }, "RULE_CASE_DUPLICATE"],
    ["missing input", (value: any) => {
      delete value.cases[0].input.amount;
    }, "RULE_CASE_INPUT_TOTALITY_INVALID"],
    ["wrong input type", (value: any) => {
      value.cases[0].input.amount = "12500";
    }, "RULE_CASE_INPUT_TYPE_INVALID"],
  ])("rejects %s cases", async (_name, mutate, code) => {
    const value = await prepare();
    const cases = JSON.parse(value.casesBytes);
    mutate(cases);
    expect(() => decodeRuleCaseCatalogueV1(
      JSON.stringify(cases),
      value.definition,
    )).toThrow(code);
  });
});
