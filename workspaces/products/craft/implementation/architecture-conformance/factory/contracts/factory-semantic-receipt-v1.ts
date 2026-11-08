import type { VerifiedProofAccountingV1 } from
  "../../kernel/contracts/proof-denominator-v1.js";
import type { FactoryNodeAccountingV1 } from "./factory-node-provider-v1.js";

export type FactorySemanticNodeReceiptV1 = Readonly<{
  node_id: string;
  provider_id: string;
  depends_on: readonly string[];
  semantic_sha256: string;
  replay_sha256: string;
  accounting: FactoryNodeAccountingV1;
  claim_ceiling: string;
}>;

export type FactoryVerifiedSemanticNodeReceiptV1 = Readonly<{
  node_id: string;
  provider_id: string;
  depends_on: readonly string[];
  semantic_sha256: string;
  replay_sha256: string;
  accounting: Readonly<{
    positives_declared: number;
    positives_passed: number;
    mutants_declared: number;
    mutants_killed: number;
    proof?: VerifiedProofAccountingV1;
  }>;
  claim_ceiling: string;
}>;

export type FactorySemanticReceiptV1 = Readonly<{
  schema_version: "FactorySemanticReceipt/v1";
  result: "pass";
  request_sha256: string;
  lock_sha256: string;
  run_id: string;
  ordered_nodes: readonly FactoryVerifiedSemanticNodeReceiptV1[];
  claim_ceiling: string;
  authority_effect: "none";
}>;
