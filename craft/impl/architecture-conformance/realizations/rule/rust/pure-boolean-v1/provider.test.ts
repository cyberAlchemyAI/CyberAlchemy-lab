import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {describe, expect, it} from "vitest";

import {
  getFactoryNodeProviderV1,
  listFactoryNodeProvidersV1,
} from "../../../../factory/registry/reference-node-providers.js";
import {ruleRustV1Provider} from
  "../../../../factory/registry/providers/rule-rust-v1.js";
import {rustRuleV1Provider} from
  "../../../../factory/registry/providers/rust-rule-v1.js";
import {RUST_RULE_ADAPTER_PATHS} from "./index.js";

const loadRaw = async (): Promise<Record<string, string>> =>
  Object.fromEntries(await Promise.all(Object.entries(
    RUST_RULE_ADAPTER_PATHS).map(async ([role, path]) =>
      [role, await readFile(resolve(process.cwd(), path), "utf8")])));

describe("Rust Rule WP-RMT-002 adapter provider", () => {
  it("hash-closes the adapter and delegates native semantic proof", async () => {
    const result = await ruleRustV1Provider.execute({
      raw_inputs: await loadRaw(), upstream: {},
    });
    expect(result).toMatchObject({
      result: "pass",
      provider_id: "rule-rust-v1",
      accounting: {
        positives_declared: 3,
        positives_passed: 3,
        mutants_declared: 3,
        mutants_killed: 3,
      },
      semantic_output: {
        adapter_binding: {
          target_id: "rust",
          predecessor_provider_id: "rust-rule-v1",
        },
        native_evidence: {
          target_id: "rust",
          predecessor_result_provider_id: "rust-rule-v1",
          native_hash_byte_comparison: false,
        },
      },
      authority_effect: "none",
    });
  }, 120_000);

  it("rejects drift in every target-binding-observer-provider ref", async () => {
    const raw = await loadRaw();
    for (const role of [
      "target_source", "observer_source", "provider_source",
      "predecessor_provider_source",
    ]) {
      await expect(ruleRustV1Provider.execute({
        raw_inputs: {...raw, [role]: `${raw[role]}\n`}, upstream: {},
      })).rejects.toMatchObject({
        code: "RMT_RULE_ADAPTER_REF_STALE",
        detail: role,
      });
    }
  });

  it("is unregistered while the predecessor stays registered", () => {
    const ids = listFactoryNodeProvidersV1().map(({provider_id: id}) => id);
    expect(ids).not.toContain("rule-rust-v1");
    expect(ids).toContain("rust-rule-v1");
    expect(() => getFactoryNodeProviderV1("rule-rust-v1"))
      .toThrow("FACTORY_PROVIDER_UNKNOWN:rule-rust-v1");
    expect(getFactoryNodeProviderV1("rust-rule-v1"))
      .toBe(rustRuleV1Provider);
  });
});
