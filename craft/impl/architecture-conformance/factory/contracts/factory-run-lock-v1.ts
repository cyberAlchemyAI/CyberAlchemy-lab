import type { FactoryPurpose } from "./factory-run-request-v1.js";
import type { LockedFactoryArtifactV1 } from "./factory-locked-artifact-v1.js";

export type LockedFactoryRefV1 = Readonly<{
  role: string;
  path: string;
  sha256: string;
  byte_length: number;
}>;

export type LockedFactoryToolV1 = Readonly<{
  tool_id: string;
  version: string;
  executable_sha256: string;
}>;

export type LockedFactoryNodeV1 = Readonly<{
  node_id: string;
  kind: "direct-proof" | "join-proof" | "projection";
  provider_id: string;
  provider_version: string;
  depends_on: readonly string[];
  inputs: readonly LockedFactoryRefV1[];
  components: readonly LockedFactoryRefV1[];
  tools: readonly LockedFactoryToolV1[];
  artifacts?: readonly LockedFactoryArtifactV1[];
  execution_timeout_ms?: number;
  claim_ceiling: string;
}>;

export type FactoryRunLockV1 = Readonly<{
  schema_version: "FactoryRunLock/v1";
  request_id: string;
  suite_id: string;
  purpose: FactoryPurpose;
  request_sha256: string;
  ordered_node_ids: readonly string[];
  nodes: readonly LockedFactoryNodeV1[];
  replay_policy: Readonly<{
    timeout_ms: number;
    output_limit_bytes: number;
    termination_grace_ms: number;
    environment_keys: readonly string[];
  }>;
  claim_ceiling: string;
  authority_effect: "none";
  lock_sha256: string;
}>;
