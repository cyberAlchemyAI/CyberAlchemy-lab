import type { FactoryRunNodeRequestV1 } from "./factory-run-request-v1.js";
import type { FactoryProviderExecutionContextV1 } from
  "./factory-provider-execution-context-v1.js";
import type { ProofEvidenceV1 } from "../../kernel/contracts/proof-denominator-v1.js";

export type FactoryNodeAccountingV1 = Readonly<{
  positives_declared: number;
  positives_passed: number;
  mutants_declared: number;
  mutants_killed: number;
  proof?: ProofEvidenceV1;
}>;

export type FactoryNodeSemanticResultV1 = Readonly<{
  schema_version: "FactoryNodeSemanticResult/v1";
  result: "pass";
  provider_id: string;
  semantic_output: unknown;
  accounting: FactoryNodeAccountingV1;
  claim_ceiling: string;
  authority_effect: "none";
}>;

export type FactoryUpstreamResultV1 = Readonly<{
  node_id: string;
  provider_id: string;
  semantic_sha256: string;
  semantic_output: unknown;
}>;

export type FactoryNodeProviderV1 = Readonly<{
  provider_id: string;
  provider_version: string;
  compatible_kinds: readonly FactoryRunNodeRequestV1["kind"][];
  required_input_roles: readonly string[];
  component_paths: readonly string[];
  tool_ids: readonly string[];
  artifact_ids?: readonly string[];
  execution_timeout_ms?: number;
  execute: (input: Readonly<{
    raw_inputs: Readonly<Record<string, string>>;
    upstream: Readonly<Record<string, FactoryUpstreamResultV1>>;
    execution_context?: FactoryProviderExecutionContextV1;
  }>) => Promise<FactoryNodeSemanticResultV1>;
}>;
