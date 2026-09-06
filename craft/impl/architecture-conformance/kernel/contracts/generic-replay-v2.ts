import type { RawIndexEntryV2, RawIndexV2 } from "./raw-index-v2.js";

export type ReplayFilePinV2 = Readonly<{
  path: string;
  sha256: string;
}>;

export type ReplayToolPinV2 = Readonly<{
  path: string;
  version: string;
  sha256: string;
}>;

export type GenericReplayManifestV2 = Readonly<{
  schema_version: "GenericReplayManifest/v2";
  child_entry: ReplayFilePinV2;
  components: Readonly<Record<string, ReplayFilePinV2>>;
  configs: Readonly<Record<string, ReplayFilePinV2>>;
  toolchain: Readonly<{
    node: ReplayToolPinV2;
    tsx_loader: ReplayToolPinV2;
  }>;
  expected_output_sha256: string;
  authority_effect: "none";
}>;

export type GenericReplayChildRequestV2 = Readonly<{
  schema_version: "GenericReplayChildRequest/v2";
  parent_pid: number;
  raw_root: string;
  raw_inputs: readonly RawIndexEntryV2[];
  expected_output_sha256: string;
  authority_effect: "none";
}>;

export type GenericReplayChildResultV2 = Readonly<{
  schema_version: "GenericReplayChildResult/v2";
  status: "pass" | "fail";
  child_pid: number;
  semantic_recomposition: "pass" | "fail";
  output_sha256: string;
  observed_raw_count: number;
  diagnostics: readonly string[];
  result_sha256: string;
  authority_effect: "none";
}>;

export type GenericReplayResultV2 = Readonly<{
  schema_version: "GenericReplayResult/v2";
  status: "pass";
  child_pid: number;
  raw_index_sha256: string;
  result_sha256: string;
  claims: Readonly<{
    semantic_recomposition: "pass";
    process_isolation: "pass";
    byte_identity: "not-claimed";
  }>;
  authority_effect: "none";
}>;

export type GenericReplayInputV2 = Readonly<{
  repositoryRoot: string;
  runPath: string;
  rawIndex: RawIndexV2;
  rawIndexSha256: string;
  manifest: GenericReplayManifestV2;
}>;
