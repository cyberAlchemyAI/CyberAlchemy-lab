import {readFile} from "node:fs/promises";
import {resolve} from "node:path";

import {beforeAll, describe, expect, it} from "vitest";

import {getFactoryNodeProviderV1, listFactoryNodeProvidersV1} from
  "../../../../factory/registry/factory-node-registry-v1.js";
import {pythonRuleV1Provider} from
  "../../../../factory/registry/providers/python-rule-v1.js";
import {rustRuleV1Provider} from
  "../../../../factory/registry/providers/rust-rule-v1.js";
import {typeScriptRuleV1Provider} from
  "../../../../factory/registry/providers/typescript-rule-v1.js";
import {evaluateRuleRegistryNegative, type RuleRegistryNegativeInput} from
  "./evaluate-rule-registry-negative.js";

type JsonObject = Record<string, any>;
const root = process.cwd();
const bindingPath = "projects/domainspec-v2/impl/architecture-conformance/" +
  "acceptance/rule/wp-rmt-002/registry-negative/" +
  "rule-registry-negative-binding.json";
const newIds = ["rule-typescript-v1", "rule-python-v1", "rule-rust-v1"] as const;
let input: RuleRegistryNegativeInput;

beforeAll(async () => {
  const bindingRaw = await readFile(resolve(root, bindingPath), "utf8");
  const binding = JSON.parse(bindingRaw) as JsonObject;
  const rawInputs = Object.fromEntries(await Promise.all(binding.sources.map(
    async ({role, path}: JsonObject) => [
      role, await readFile(resolve(root, path), "utf8"),
    ])));
  const registryBefore = rawInputs.canonical_registry!;
  const newProviderErrors = Object.fromEntries(newIds.map((id) => {
    try {
      getFactoryNodeProviderV1(id);
      return [id, "unexpected-pass"];
    } catch (error) {
      return [id, (error as Error).message];
    }
  }));
  const predecessorIdentityExact = {
    "typescript-rule-v1":
      getFactoryNodeProviderV1("typescript-rule-v1") === typeScriptRuleV1Provider,
    "python-rule-v1":
      getFactoryNodeProviderV1("python-rule-v1") === pythonRuleV1Provider,
    "rust-rule-v1":
      getFactoryNodeProviderV1("rust-rule-v1") === rustRuleV1Provider,
  };
  const registryAfter = await readFile(resolve(root,
    binding.sources.find(({role}: JsonObject) =>
      role === "canonical_registry").path), "utf8");
  input = {
    binding_raw: bindingRaw,
    raw_inputs: rawInputs,
    registry_before: registryBefore,
    registry_after: registryAfter,
    runtime_provider_ids: listFactoryNodeProvidersV1().map(
      ({provider_id: providerId}) => providerId),
    predecessor_identity_exact: predecessorIdentityExact,
    new_provider_errors: newProviderErrors,
  };
});

describe("RMT-RULE-009 exact new-adapter registry nonmembership", () => {
  it("proves only the three new Rule adapter IDs absent while predecessors remain exact", () => {
    const proof = evaluateRuleRegistryNegative(input);
    expect(proof).toMatchObject({
      result: "pass",
      provider_files_exact: true,
      canonical_registry_snapshot_exact: true,
      new_provider_ids_absent: true,
      predecessor_provider_ids_present: true,
      predecessor_runtime_identity_exact: true,
      no_registration_write: true,
      authority_effect: "none",
    });
    expect(proof.checked_new_provider_ids).toEqual([...newIds]);
    expect(proof.checked_predecessor_provider_ids).toEqual([
      "typescript-rule-v1", "python-rule-v1", "rust-rule-v1",
    ]);
  });

  it("calls the canonical registry lookup and preserves exact unknown-provider errors", () => {
    for (const id of newIds) {
      expect(() => getFactoryNodeProviderV1(id)).toThrowError(
        `FACTORY_PROVIDER_UNKNOWN:${id}`);
    }
  });

  it("rejects simulated runtime registration of any new adapter ID", () => {
    for (const id of newIds) {
      expect(() => evaluateRuleRegistryNegative({
        ...input,
        runtime_provider_ids: [...input.runtime_provider_ids, id],
      })).toThrowError("RMT_RULE_NEW_PROVIDER_REGISTERED_OR_DRIFTED");
    }
  });
});
