import {
  buildRustRuleAdapterResult,
  RUST_RULE_ADAPTER_PATHS,
} from "../../../realizations/rule/rust/pure-boolean-v1/index.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";

export const ruleRustV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "rule-rust-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(RUST_RULE_ADAPTER_PATHS)),
  component_paths: Object.freeze([
    ...new Set(Object.values(RUST_RULE_ADAPTER_PATHS)),
    "projects/domainspec-v2/impl/architecture-conformance/families/pure-boolean-rule/providers/build-rule-adapter.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "cargo", "rustc"]),
  execute: async ({raw_inputs: rawInputs}) =>
    buildRustRuleAdapterResult(rawInputs),
});
