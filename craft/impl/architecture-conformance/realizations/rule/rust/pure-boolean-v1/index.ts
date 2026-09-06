import {executeRuleAdapter} from
  "../../../../families/pure-boolean-rule/providers/build-rule-adapter.js";
import {rustRuleV1Provider} from
  "../../../../factory/registry/providers/rust-rule-v1.js";

export const RUST_RULE_ADAPTER_PATHS = Object.freeze({
  definition: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/rule-definition.json",
  binding: "projects/domainspec-v2/impl/architecture-conformance/targets/rust/fixtures/rust-binding.json",
  cases: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/cases.json",
  obligations: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/obligations.json",
  mutants: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/mutants.json",
  source: "projects/domainspec-v2/impl/architecture-conformance/targets/rust/fixtures/can_settle_payout.rs",
  adapter_binding: "projects/domainspec-v2/impl/architecture-conformance/realizations/rule/rust/pure-boolean-v1/rust-binding.json",
  target_source: "projects/domainspec-v2/impl/architecture-conformance/targets/rust/src/remaining_types/rule_v1.rs",
  observer_source: "projects/domainspec-v2/impl/architecture-conformance/realizations/rule/rust/pure-boolean-v1/index.ts",
  provider_source: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rule-rust-v1.ts",
  predecessor_provider_source: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rust-rule-v1.ts",
});
export const buildRustRuleAdapterResult = (
  rawInputs: Readonly<Record<string, string>>,
) => executeRuleAdapter({
  raw_inputs: rawInputs,
  raw_paths: RUST_RULE_ADAPTER_PATHS,
  predecessor: rustRuleV1Provider,
  expected: {
    realization_id: "rule.rust.pure-boolean-v1",
    target_id: "rust",
    provider_id: "rule-rust-v1",
    predecessor_provider_id: "rust-rule-v1",
    ref_paths: {
      target_source: RUST_RULE_ADAPTER_PATHS.target_source,
      observer_source: RUST_RULE_ADAPTER_PATHS.observer_source,
      provider_source: RUST_RULE_ADAPTER_PATHS.provider_source,
      predecessor_provider_source:
        RUST_RULE_ADAPTER_PATHS.predecessor_provider_source,
    },
  },
});
