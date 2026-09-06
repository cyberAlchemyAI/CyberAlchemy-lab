export type CompileResult = Readonly<{
  schema_version: "CompileResult/v1";
  source_sha256: string;
  provider_sha256: string;
  compiler: Readonly<{
    name: "typescript";
    version: string;
    tool_sha256: string;
    config_sha256: string;
  }>;
  workspace: Readonly<{
    workspace_id: string;
    isolated: true;
    symlinks: false;
    cleaned: true;
  }>;
  exit_status: 0 | 1;
  diagnostics: readonly Readonly<{ code: string; message: string }>[];
  type_witness: Readonly<{
    mode: "definition-exact" | "compile-only";
    expected_union: readonly string[];
    source_sha256: string | null;
    passed: boolean;
  }>;
  runtime_values: readonly string[];
  runtime_frozen: boolean;
  authority_effect: "none";
}>;

export type CompileExpectation = Readonly<{
  compiler: Readonly<{
    name: "typescript";
    version: string;
    tool_sha256: string;
    config_sha256: string;
  }>;
}>;
