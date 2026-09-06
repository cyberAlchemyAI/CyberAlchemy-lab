import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {describe, expect, it} from "vitest";

import {
  getFactoryNodeProviderV1,
  listFactoryNodeProvidersV1,
} from "../../../../factory/registry/reference-node-providers.js";
import {ruleTypeScriptV1Provider} from
  "../../../../factory/registry/providers/rule-typescript-v1.js";
import {typeScriptRuleV1Provider} from
  "../../../../factory/registry/providers/typescript-rule-v1.js";
import {TYPESCRIPT_RULE_ADAPTER_PATHS} from "./index.js";

const loadRaw = async (): Promise<Record<string, string>> =>
  Object.fromEntries(await Promise.all(Object.entries(
    TYPESCRIPT_RULE_ADAPTER_PATHS).map(async ([role, path]) =>
      [role, await readFile(resolve(process.cwd(), path), "utf8")])));

describe("TypeScript Rule WP-RMT-002 adapter provider", () => {
  it("hash-closes the adapter and delegates semantic proof", async () => {
    const result = await ruleTypeScriptV1Provider.execute({
      raw_inputs: await loadRaw(), upstream: {},
    });
    expect(result).toMatchObject({
      result: "pass",
      provider_id: "rule-typescript-v1",
      accounting: {
        positives_declared: 3,
        positives_passed: 3,
        mutants_declared: 3,
        mutants_killed: 3,
      },
      semantic_output: {
        adapter_binding: {
          target_id: "typescript",
          predecessor_provider_id: "typescript-rule-v1",
        },
        native_evidence: {
          target_id: "typescript",
          predecessor_result_provider_id: "typescript-rule-v1",
          native_hash_byte_comparison: false,
        },
      },
      authority_effect: "none",
    });
  }, 60_000);

  it("rejects drift in every target-binding-observer-provider ref", async () => {
    const raw = await loadRaw();
    for (const role of [
      "target_source", "observer_source", "provider_source",
      "predecessor_provider_source",
    ]) {
      await expect(ruleTypeScriptV1Provider.execute({
        raw_inputs: {...raw, [role]: `${raw[role]}\n`}, upstream: {},
      })).rejects.toMatchObject({
        code: "RMT_RULE_ADAPTER_REF_STALE",
        detail: role,
      });
    }
  });

  it("is unregistered while the predecessor stays registered", () => {
    const ids = listFactoryNodeProvidersV1().map(({provider_id: id}) => id);
    expect(ids).not.toContain("rule-typescript-v1");
    expect(ids).toContain("typescript-rule-v1");
    expect(() => getFactoryNodeProviderV1("rule-typescript-v1"))
      .toThrow("FACTORY_PROVIDER_UNKNOWN:rule-typescript-v1");
    expect(getFactoryNodeProviderV1("typescript-rule-v1"))
      .toBe(typeScriptRuleV1Provider);
  });
});
