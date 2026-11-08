import type { RuleSemanticMutantV1 } from "../../../families/outcome-function/contracts/rule-contracts.js";
import { inspectTypeScriptRuleSource } from "../../adapter/rule/index.js";

const fail = (code: string): never => {
  throw Object.assign(new Error(code), { code });
};

export const mutateTypeScriptRuleSource = (input: Readonly<{
  modulePath: string;
  source: string;
  symbolName: string;
  mutant: RuleSemanticMutantV1;
}>): string => {
  const inspection = inspectTypeScriptRuleSource(input);
  if (!inspection.supported || inspection.expression_span === null) {
    return fail("TS_RULE_MUTATION_BASE_UNSUPPORTED");
  }
  const { start, length } = inspection.expression_span;
  const expression = input.source.slice(start, start + length);
  let replacement: string;
  if (input.mutant.defect === "wrong-result") {
    const separator = expression.indexOf("&&");
    if (separator < 0) return fail("TS_RULE_MUTATION_WRONG_RESULT_NOT_APPLICABLE");
    replacement = `false && ${expression.slice(separator + 2).trimStart()}`;
  } else if (input.mutant.defect === "bypass-check") {
    const separator = expression.lastIndexOf("&&");
    if (separator < 0) return fail("TS_RULE_MUTATION_BYPASS_NOT_APPLICABLE");
    replacement = expression.slice(0, separator).trimEnd();
  } else {
    const effect = "(globalThis as unknown as { __domainspecRuleEffectCount?: number }).__domainspecRuleEffectCount";
    replacement = `((${expression}) ? ((${effect} = (${effect} ?? 0) + 1), true) : false)`;
  }
  return `${input.source.slice(0, start)}${replacement}${input.source.slice(start + length)}`;
};
