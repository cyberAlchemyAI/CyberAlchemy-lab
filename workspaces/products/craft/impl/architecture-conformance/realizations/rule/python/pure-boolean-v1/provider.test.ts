import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {describe, expect, it} from "vitest";

import {
  getFactoryNodeProviderV1,
  listFactoryNodeProvidersV1,
} from "../../../../factory/registry/reference-node-providers.js";
import {pythonRuleV1Provider} from
  "../../../../factory/registry/providers/python-rule-v1.js";
import {rulePythonV1Provider} from
  "../../../../factory/registry/providers/rule-python-v1.js";
import {PYTHON_RULE_ADAPTER_PATHS} from "./index.js";

const loadRaw = async (): Promise<Record<string, string>> =>
  Object.fromEntries(await Promise.all(Object.entries(
    PYTHON_RULE_ADAPTER_PATHS).map(async ([role, path]) =>
      [role, await readFile(resolve(process.cwd(), path), "utf8")])));

describe("Python Rule WP-RMT-002 adapter provider", () => {
  it("hash-closes the adapter and delegates native semantic proof", async () => {
    const result = await rulePythonV1Provider.execute({
      raw_inputs: await loadRaw(), upstream: {},
    });
    expect(result).toMatchObject({
      result: "pass",
      provider_id: "rule-python-v1",
      accounting: {
        positives_declared: 3,
        positives_passed: 3,
        mutants_declared: 3,
        mutants_killed: 3,
      },
      semantic_output: {
        adapter_binding: {
          target_id: "python",
          predecessor_provider_id: "python-rule-v1",
        },
        native_evidence: {
          target_id: "python",
          predecessor_result_provider_id: "python-rule-v1",
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
      await expect(rulePythonV1Provider.execute({
        raw_inputs: {...raw, [role]: `${raw[role]}\n`}, upstream: {},
      })).rejects.toMatchObject({
        code: "RMT_RULE_ADAPTER_REF_STALE",
        detail: role,
      });
    }
  });

  it("is unregistered while the predecessor stays registered", () => {
    const ids = listFactoryNodeProvidersV1().map(({provider_id: id}) => id);
    expect(ids).not.toContain("rule-python-v1");
    expect(ids).toContain("python-rule-v1");
    expect(() => getFactoryNodeProviderV1("rule-python-v1"))
      .toThrow("FACTORY_PROVIDER_UNKNOWN:rule-python-v1");
    expect(getFactoryNodeProviderV1("python-rule-v1"))
      .toBe(pythonRuleV1Provider);
  });
});
