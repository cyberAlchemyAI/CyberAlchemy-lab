import {
  buildTypeScriptRuleAdapterResult,
  TYPESCRIPT_RULE_ADAPTER_PATHS,
} from "../../../realizations/rule/typescript/pure-boolean-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";

export const ruleTypeScriptV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "rule-typescript-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(
    TYPESCRIPT_RULE_ADAPTER_PATHS)),
  component_paths: Object.freeze([
    ...new Set(Object.values(TYPESCRIPT_RULE_ADAPTER_PATHS)),
    "projects/domainspec-v2/impl/architecture-conformance/families/pure-boolean-rule/providers/build-rule-adapter.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({raw_inputs: rawInputs}) =>
    buildTypeScriptRuleAdapterResult(rawInputs),
});
