import {executeRuleAdapter} from
  "../../../../families/pure-boolean-rule/providers/build-rule-adapter.js";
import {typeScriptRuleV1Provider} from
  "../../../../factory/registry/providers/typescript-rule-v1.js";

export const TYPESCRIPT_RULE_ADAPTER_PATHS = Object.freeze({
  definition: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/rule-definition.json",
  binding: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/typescript-binding.json",
  cases: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/cases.json",
  obligations: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/obligations.json",
  mutants: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/mutants.json",
  source: "projects/domainspec-v2/impl/architecture-conformance/realizations/rule/typescript/bound-arrow-function-v1/fixtures/can-settle-payout.ts",
  adapter_binding: "projects/domainspec-v2/impl/architecture-conformance/realizations/rule/typescript/pure-boolean-v1/typescript-binding.json",
  target_source: "projects/domainspec-v2/impl/architecture-conformance/targets/typescript/rule-v1.ts",
  observer_source: "projects/domainspec-v2/impl/architecture-conformance/realizations/rule/typescript/pure-boolean-v1/index.ts",
  provider_source: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rule-typescript-v1.ts",
  predecessor_provider_source: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-rule-v1.ts",
});
export const buildTypeScriptRuleAdapterResult = (
  rawInputs: Readonly<Record<string, string>>,
) => executeRuleAdapter({
  raw_inputs: rawInputs,
  raw_paths: TYPESCRIPT_RULE_ADAPTER_PATHS,
  predecessor: typeScriptRuleV1Provider,
  expected: {
    realization_id: "rule.typescript.pure-boolean-v1",
    target_id: "typescript",
    provider_id: "rule-typescript-v1",
    predecessor_provider_id: "typescript-rule-v1",
    ref_paths: {
      target_source: TYPESCRIPT_RULE_ADAPTER_PATHS.target_source,
      observer_source: TYPESCRIPT_RULE_ADAPTER_PATHS.observer_source,
      provider_source: TYPESCRIPT_RULE_ADAPTER_PATHS.provider_source,
      predecessor_provider_source:
        TYPESCRIPT_RULE_ADAPTER_PATHS.predecessor_provider_source,
    },
  },
});
