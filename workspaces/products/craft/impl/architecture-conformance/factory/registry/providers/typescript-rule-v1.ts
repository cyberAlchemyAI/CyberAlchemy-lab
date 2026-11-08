import { buildTypeScriptRuleProof } from "../../../acceptance/rule/typescript/run-rule-proof.js";
import type { FactoryNodeProviderV1 } from "../../contracts/factory-node-provider-v1.js";

export const typeScriptRuleV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "typescript-rule-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["direct-proof"] as const),
  required_input_roles: Object.freeze([
    "definition",
    "binding",
    "cases",
    "obligations",
    "mutants",
    "source",
  ]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-rule-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/rule/typescript/run-rule-proof.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/evaluator/evaluate-rule.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/providers/decode-rule-contracts.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/outcome-function/providers/decode-rule-obligations.ts",
    "projects/domainspec-v2/impl/architecture-conformance/typescript/compiler/rule/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter/rule/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/typescript/runtime/rule/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/typescript/mutations/rule/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({ raw_inputs: rawInputs }) => {
    const proof = await buildTypeScriptRuleProof(rawInputs as Parameters<
      typeof buildTypeScriptRuleProof
    >[0]);
    const accounting = proof.summary.accounting;
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "typescript-rule-v1",
      semantic_output: Object.freeze({
        summary: proof.summary,
        observations: proof.positiveExecution.observation?.case_observations ?? [],
      }),
      accounting: Object.freeze({
        positives_declared: accounting.positive.declared,
        positives_passed: accounting.positive.passed,
        mutants_declared: accounting.mutations.declared,
        mutants_killed: accounting.mutations.killed,
      }),
      claim_ceiling: proof.summary.claim_ceiling,
      authority_effect: "none",
    });
  },
});
