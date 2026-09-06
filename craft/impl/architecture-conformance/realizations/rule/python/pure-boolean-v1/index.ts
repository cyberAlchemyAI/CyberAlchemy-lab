import {executeRuleAdapter} from
  "../../../../families/pure-boolean-rule/providers/build-rule-adapter.js";
import {pythonRuleV1Provider} from
  "../../../../factory/registry/providers/python-rule-v1.js";

export const PYTHON_RULE_ADAPTER_PATHS = Object.freeze({
  definition: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/rule-definition.json",
  binding: "projects/domainspec-v2/impl/architecture-conformance/targets/python/fixtures/python-binding.json",
  cases: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/cases.json",
  obligations: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/obligations.json",
  mutants: "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/fixtures/can-settle-payout/mutants.json",
  source: "projects/domainspec-v2/impl/architecture-conformance/targets/python/fixtures/can_settle_payout.py",
  adapter_binding: "projects/domainspec-v2/impl/architecture-conformance/realizations/rule/python/pure-boolean-v1/python-binding.json",
  target_source: "projects/domainspec-v2/impl/architecture-conformance/targets/python/remaining_types/rule_v1.py",
  observer_source: "projects/domainspec-v2/impl/architecture-conformance/realizations/rule/python/pure-boolean-v1/index.ts",
  provider_source: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rule-python-v1.ts",
  predecessor_provider_source: "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/python-rule-v1.ts",
});
export const buildPythonRuleAdapterResult = (
  rawInputs: Readonly<Record<string, string>>,
) => executeRuleAdapter({
  raw_inputs: rawInputs,
  raw_paths: PYTHON_RULE_ADAPTER_PATHS,
  predecessor: pythonRuleV1Provider,
  expected: {
    realization_id: "rule.python.pure-boolean-v1",
    target_id: "python",
    provider_id: "rule-python-v1",
    predecessor_provider_id: "python-rule-v1",
    ref_paths: {
      target_source: PYTHON_RULE_ADAPTER_PATHS.target_source,
      observer_source: PYTHON_RULE_ADAPTER_PATHS.observer_source,
      provider_source: PYTHON_RULE_ADAPTER_PATHS.provider_source,
      predecessor_provider_source:
        PYTHON_RULE_ADAPTER_PATHS.predecessor_provider_source,
    },
  },
});
