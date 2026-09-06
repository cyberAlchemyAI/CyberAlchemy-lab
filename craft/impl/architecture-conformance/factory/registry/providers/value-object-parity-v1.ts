import {
  proveValueObjectParity,
  VALUE_OBJECT_PARITY_RAW_PATHS,
} from "../../../acceptance/value-object/evaluate-value-object-joins.js";
import type {FactoryNodeProviderV1} from
  "../../contracts/factory-node-provider-v1.js";
import {typeScriptValueObjectV1Provider} from
  "./typescript-value-object-v1.js";
import {TYPESCRIPT_VALUE_OBJECT_RAW_PATHS} from
  "../../../realizations/value-object/typescript/complete-value-v1/index.js";

export const registeredTypeScriptValueObjectV1Provider:
FactoryNodeProviderV1 = Object.freeze({
  ...typeScriptValueObjectV1Provider,
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/value-object-parity-v1.ts",
    ...Object.values(TYPESCRIPT_VALUE_OBJECT_RAW_PATHS).filter((path) =>
      path !== TYPESCRIPT_VALUE_OBJECT_RAW_PATHS.typescript_compiler),
  ]),
});

export const valueObjectParityV1Provider: FactoryNodeProviderV1 = Object.freeze({
  provider_id: "value-object-parity-v1",
  provider_version: "1.0.0",
  compatible_kinds: Object.freeze(["join-proof"] as const),
  required_input_roles: Object.freeze(Object.keys(VALUE_OBJECT_PARITY_RAW_PATHS)),
  component_paths: Object.freeze([
    "projects/domainspec-v2/impl/architecture-conformance/factory/registry/providers/value-object-parity-v1.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/value-object/evaluate-value-object-joins.ts",
    "projects/domainspec-v2/impl/architecture-conformance/acceptance/value-object/evaluate-value-object-joins.test.ts",
    "projects/domainspec-v2/impl/architecture-conformance/families/complete-value/index.ts",
    "projects/domainspec-v2/impl/architecture-conformance/kernel/evidence/construction-observation/index.ts",
  ]),
  tool_ids: Object.freeze(["node", "tsx"]),
  execute: async ({raw_inputs: rawInputs, upstream}) => {
    const proof = proveValueObjectParity(upstream, rawInputs);
    return Object.freeze({
      schema_version: "FactoryNodeSemanticResult/v1" as const,
      result: "pass" as const,
      provider_id: "value-object-parity-v1",
      semantic_output: Object.freeze({proof}),
      accounting: Object.freeze({
        positives_declared: proof.obligations.length,
        positives_passed: proof.obligations.length,
        mutants_declared: proof.hostile_mutations.length,
        mutants_killed: proof.hostile_mutations.length,
      }),
      claim_ceiling: proof.claim_ceiling,
      authority_effect: "none" as const,
    });
  },
});
