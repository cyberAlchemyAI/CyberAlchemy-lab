import { buildCompositionProof } from "../../../acceptance/relation/typescript/run-composition-proof.js";
import type { FactoryNodeProviderV1 } from "../../contracts/factory-node-provider-v1.js";
import { fail } from "../../shared/canonical.js";

export const typeScriptEnforcesV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "typescript-enforces-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["join-proof"] as const),
  required_input_roles: Object.freeze([
    "relationDefinition",
    "relationBinding",
    "relationMutants",
    "useCaseSource",
    "ruleSource",
    "operationSource",
  ]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/typescript-enforces-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/relation/typescript/run-composition-proof.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/relation/typescript/composition-proof.test.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/enforces-relation/evaluator/evaluate-enforces.ts",
    "projects/domainspec-v2/impl/architecture-conformance/typescript/adapter/relation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx", "typescript"]),
  execute: async ({ raw_inputs: rawInputs, upstream }) => {
    const rule = Object.values(upstream).find(({ provider_id: id }) => id === "typescript-rule-v1")
      ?? fail("FACTORY_DEPENDENCY_STALE", "typescript-rule-v1");
    const operation = Object.values(upstream).find(({ provider_id: id }) =>
      id === "typescript-operation-v1") ?? fail("FACTORY_DEPENDENCY_STALE", "typescript-operation-v1");
    const ruleOutput = rule.semantic_output as { summary?: unknown };
    const proof = await buildCompositionProof({
      ...rawInputs,
      ruleDirectProof: JSON.stringify(ruleOutput.summary ?? fail(
        "FACTORY_DEPENDENCY_STALE",
        "typescript-rule-summary",
      )),
      operationDirectProof: JSON.stringify(operation.semantic_output),
    } as Parameters<typeof buildCompositionProof>[0]);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "typescript-enforces-v1",
      semantic_output: proof.summary,
      accounting: Object.freeze({
        positives_declared: 2,
        positives_passed: proof.summary.positive.verdict === "pass" &&
          proof.summary.denied_guard.outcome === false ? 2 : 0,
        mutants_declared: proof.summary.mutations.length,
        mutants_killed: proof.summary.mutations.filter(({ status }) => status === "killed").length,
      }),
      claim_ceiling: proof.summary.claim_ceiling,
      authority_effect: "none",
    });
  },
});
