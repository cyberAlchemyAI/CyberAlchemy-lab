import { executeTypeScriptRule } from "../../../../typescript/compiler/rule/index.js";
import { inspectTypeScriptRuleSource } from "../../../../typescript/adapter/rule/index.js";
import { mutateTypeScriptRuleSource } from "../../../../typescript/mutations/rule/index.js";

export const boundArrowFunctionRuleRealizationV1 = Object.freeze({
  schema_version: "RuleRealizationProvider/v1" as const,
  realization_id: "rule.typescript.bound-arrow-function-v1",
  target_id: "typescript" as const,
  admitted_form: "exported synchronous const arrow with one input and pure boolean expression body",
  inspect: inspectTypeScriptRuleSource,
  execute: executeTypeScriptRule,
  mutate: mutateTypeScriptRuleSource,
  authority_effect: "none" as const,
});
