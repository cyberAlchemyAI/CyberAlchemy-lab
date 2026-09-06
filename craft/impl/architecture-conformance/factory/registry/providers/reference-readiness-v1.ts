import type { FactoryNodeProviderV1 } from "../../contracts/factory-node-provider-v1.js";
import { fail } from "../../shared/canonical.js";

const requiredProviders = Object.freeze([
  "typescript-enum-order-status-v1",
  "typescript-enum-shipment-priority-semantic-slice-v1",
  "typescript-operation-v1",
  "typescript-rule-v1",
  "python-rule-v1",
  "rust-rule-v1",
  "typescript-enforces-v1",
  "rule-parity-v1",
]);

export const referenceReadinessV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "reference-readiness-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["projection"] as const),
  required_input_roles: Object.freeze(["ontology_projection"]),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/reference-readiness-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/factory/build-readiness-matrix.mjs",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/validate-proof-receipts.mjs",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/scaffolding/readiness-classifier.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx"]),
  execute: async ({ raw_inputs: rawInputs, upstream }) => {
    const observed = new Set(Object.values(upstream).map(({ provider_id: id }) => id));
    const missing = requiredProviders.filter((id) => !observed.has(id));
    if (missing.length > 0) fail("FACTORY_ACCOUNTING_INCOMPLETE", missing.join(","));
    const module = await import(
      "../../../acceptance/factory/build-readiness-matrix.mjs"
    ) as Readonly<{
      buildReadinessMatrix: (options: Readonly<{ sourceBytes: string }>) => Promise<{
        meta_types: readonly unknown[];
        counts: Readonly<{ bounded_proof_complete: number }>;
        claim_ceiling: string;
        [key: string]: unknown;
      }>;
    }>;
    const matrix = await module.buildReadinessMatrix({
      sourceBytes: rawInputs.ontology_projection ?? fail(
        "FACTORY_PROVIDER_INPUTS_INCOMPLETE",
        "ontology_projection",
      ),
    });
    if (matrix.meta_types.length !== 25 || matrix.counts.bounded_proof_complete !== 3) {
      fail("FACTORY_READINESS_ACCOUNTING_INVALID");
    }
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1",
      result: "pass",
      provider_id: "reference-readiness-v1",
      semantic_output: matrix,
      accounting: Object.freeze({
        positives_declared: matrix.meta_types.length,
        positives_passed: matrix.meta_types.length,
        mutants_declared: 0,
        mutants_killed: 0,
      }),
      claim_ceiling: matrix.claim_ceiling,
      authority_effect: "none",
    });
  },
});
