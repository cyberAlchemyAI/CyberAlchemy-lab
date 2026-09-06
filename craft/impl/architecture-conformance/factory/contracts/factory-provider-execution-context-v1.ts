export type FactoryVerifiedExecutableHandleV1 = Readonly<{
  kind: "executable";
  tool_id: string;
  version: string;
  sha256: string;
  path: string;
}>;

export type FactoryVerifiedArtifactHandleV1 = Readonly<{
  kind: "artifact";
  artifact_id: string;
  version: string;
  sha256: string;
  path: string;
}>;

export type FactoryProviderExecutionContextV1 = Readonly<{
  schema_version: "FactoryProviderExecutionContext/v1";
  node_id: string;
  scratch_path: string;
  executables: readonly FactoryVerifiedExecutableHandleV1[];
  artifacts: readonly FactoryVerifiedArtifactHandleV1[];
  process_bounds: Readonly<{
    timeout_ms: number;
    output_limit_bytes: number;
    termination_grace_ms: number;
  }>;
  authority_effect: "none";
}>;
