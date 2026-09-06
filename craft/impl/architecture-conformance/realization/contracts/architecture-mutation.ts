import type { GeneratedSource } from "./generated-source.js";

export type ArchitectureMutation = Readonly<{
  schema_version: "ArchitectureMutation/v1";
  mutation_id: string;
  parent_source_sha256: string;
  child_source_sha256: string;
  delta: Readonly<{
    operation: "remove-enum-member";
    member_id: string;
    target_identifier: string;
    deleted_nodes: 1;
    inserted_nodes: 0;
    delta_sha256: string;
  }>;
  expected_compile_phase: "compile-green";
  expected_failure_code: "ARCH_ENUM_MEMBER_MISSING";
  tool: Readonly<{ name: "domainspec-enum-mutator"; version: "1.0.0"; config_sha256: string }>;
  authority_effect: "none";
}>;

export type EnumMutationResult = Readonly<{
  child: GeneratedSource;
  mutation: ArchitectureMutation;
}>;
