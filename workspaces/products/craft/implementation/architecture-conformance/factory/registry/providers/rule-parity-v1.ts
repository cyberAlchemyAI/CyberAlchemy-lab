import { evaluateRuleParity } from "../../../acceptance/rule/parity/evaluate-rule-parity.js";
import type {
  FactoryNodeProviderV1,
  FactoryUpstreamResultV1,
} from "../../contracts/factory-node-provider-v1.js";
import { fail } from "../../shared/canonical.js";

const source = (
  upstream: Readonly<Record<string, FactoryUpstreamResultV1>>,
  providerId: string,
) => {
  const handle = Object.values(upstream).find(({ provider_id: id }) => id === providerId)
    ?? fail("FACTORY_DEPENDENCY_STALE", providerId);
  const output = handle.semantic_output as { summary?: unknown; observations?: unknown };
  if (output.summary === undefined || output.observations === undefined) {
    fail("FACTORY_DEPENDENCY_STALE", `${providerId}-semantic-output`);
  }
  return Object.freeze({
    summary: output.summary as Record<string, unknown>,
    observations: output.observations,
    semantic_sha256: handle.semantic_sha256,
  });
};

export const ruleParityV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "rule-parity-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["join-proof"] as const),
  required_input_roles: Object.freeze([]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/rule-parity-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/rule/parity/evaluate-rule-parity.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/rule/parity/evaluate-rule-parity.test.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx"]),
  execute: async ({ upstream }) => {
    const result = await evaluateRuleParity({
      typescript: source(upstream, "typescript-rule-v1"),
      python: source(upstream, "python-rule-v1"),
      rust: source(upstream, "rust-rule-v1"),
    });
    if (result.result !== "pass") fail("FACTORY_PARITY_BLOCKED", result.diagnostics.join(","));
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "rule-parity-v1",
      semantic_output: result,
      accounting: Object.freeze({
        positives_declared: result.targets.length,
        positives_passed: result.targets.length,
        mutants_declared: 0,
        mutants_killed: 0,
      }),
      claim_ceiling: result.claim_ceiling,
      authority_effect: "none",
    });
  },
});
