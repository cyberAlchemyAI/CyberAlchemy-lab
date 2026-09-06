export type ReplayRawInputName =
  | "ontology"
  | "base_profile"
  | "typescript_profile"
  | "definition"
  | "realization_spec"
  | "catalogue"
  | "binding"
  | "provider";

export type ReplayComponentName =
  | "generator"
  | "adapter"
  | "evaluator"
  | "compiler"
  | "mutator"
  | "registry"
  | "family"
  | "target"
  | "realization"
  | "registration"
  | "replay_parent"
  | "replay_child";

type ReplayFileRef = Readonly<{ path: string; sha256: string }>;

export type ReplayEnvironment = Readonly<{
  components: Readonly<Record<ReplayComponentName, ReplayFileRef>>;
  toolchain: Readonly<{
    node: Readonly<{ path: string; version: string; sha256: string }>;
    tsx_loader: Readonly<{ path: string; version: string; sha256: string }>;
    typescript: Readonly<{ path: string; version: string; sha256: string }>;
  }>;
  config: Readonly<{
    compiler_sha256: string;
    mutator_sha256: string;
    replay_protocol_sha256: string;
  }>;
}>;

export type ReplayRawIndex = Readonly<{
  schema_version: "ReplayRawIndex/v2";
  inputs: Readonly<Record<ReplayRawInputName, ReplayFileRef>>;
  environment: ReplayEnvironment;
  expected: Readonly<{
    positive_evaluation_sha256: string;
    mutation_sha256: string;
    mutation_evaluation_sha256: string;
  }>;
  authority_effect: "none";
}>;

export type ReplayResult = Readonly<{
  schema_version: "ReplayResult/v2";
  status: "pass" | "fail";
  child_pid: number;
  workspace_id: string;
  recomputed: Readonly<{
    realization_spec_sha256: string;
    source_sha256: string;
    positive_evaluation_sha256: string;
    mutation_sha256: string;
    mutation_evaluation_sha256: string;
  }>;
  diagnostics: readonly string[];
  claims: Readonly<{
    semantic_recomposition: "pass" | "fail";
    process_isolation: "pass" | "fail";
    byte_identity: "not-claimed";
  }>;
  result_sha256: string;
  authority_effect: "none";
}>;
