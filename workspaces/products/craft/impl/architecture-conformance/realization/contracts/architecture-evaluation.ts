import type { ArchitectureObligationCatalogueV2 } from "./architecture-obligation-catalogue-v2.js";
import type { CompileExpectation, CompileResult } from "./compile-result.js";
import type { GeneratedSourceManifest } from "./generated-source.js";
import type { TypeScriptTargetBinding } from "./typescript-target-binding.js";
import type { EnumDefinitionSnapshot } from "./enum-definition-snapshot.js";

export type EnumObservationFact = Readonly<{
  fact_type: "enum-member";
  semantic_member_id: null;
  target_identifier: string;
  runtime_value: string;
  source_span: Readonly<{ start: number; length: number }>;
  confidence: "exact";
}>;

export type EnumObservation = Readonly<{
  schema_version: "ObservationProjection/v1";
  observation_id: string;
  source_manifest_ref: Readonly<{ module_path: string; source_sha256: string }>;
  protocol_ref: Readonly<{
    protocol_id: "typescript.owned-const-object-enum/v1";
    provider_sha256: string;
  }>;
  facts: readonly EnumObservationFact[];
  unsupported: readonly Readonly<{ code: string; reason: string }>[];
  diagnostics: readonly Readonly<{ code: string; message: string }>[];
  observation_sha256: string;
  authority_effect: "none";
}>;

export type ArchitectureFinding = Readonly<{
  code:
    | "ARCH_ENUM_MEMBER_MISSING"
    | "ARCH_ENUM_MEMBER_UNEXPECTED"
    | "ARCH_ENUM_VALUE_MISMATCH"
    | "ARCH_ENUM_MEMBER_DUPLICATE"
    | "ARCH_ENUM_BINDING_AMBIGUOUS"
    | "ARCH_ENUM_OBSERVATION_UNSUPPORTED"
    | "ARCH_ENUM_CATALOGUE_DIGEST_STALE"
    | "ARCH_ENUM_CATALOGUE_DEFINITION_MISMATCH"
    | "ARCH_ENUM_CATALOGUE_BINDING_MISMATCH"
    | "ARCH_ENUM_COMPILE_EXECUTION_INVALID"
    | "ARCH_ENUM_COMPILE_TOOL_INVALID"
    | "ARCH_ENUM_COMPILE_TYPE_WITNESS_INVALID"
    | "ARCH_ENUM_COMPILE_RUNTIME_VALUES_INVALID"
    | "ARCH_ENUM_COMPILE_RUNTIME_FREEZE_INVALID"
    | "ARCH_REALIZATION_HANDLE_STALE";
  member_id: string | null;
  target_identifier: string | null;
  expected_value: string | null;
  observed_value: string | null;
}>;

export type ArchitectureEvaluation = Readonly<{
  schema_version: "ArchitectureEvaluation/v1";
  evaluation_id: string;
  obligation_key: "enum.member-bijection@1";
  input_refs: Readonly<{
    catalogue_sha256: string;
    binding_sha256: string;
    source_sha256: string;
    compile_config_sha256: string;
    observation_sha256: string;
  }>;
  verdict: "pass" | "fail";
  findings: readonly ArchitectureFinding[];
  obligation_accounting: Readonly<{
    declared: 1;
    passed: 0 | 1;
    failed: 0 | 1;
    unaccounted: 0;
  }>;
  authority_effect: "none";
}>;

export type EvaluateEnumBijectionInput = Readonly<{
  definition: EnumDefinitionSnapshot;
  catalogue: ArchitectureObligationCatalogueV2;
  binding: TypeScriptTargetBinding;
  sourceManifest: GeneratedSourceManifest;
  compileExpectation: CompileExpectation;
  compileResult: CompileResult;
  observation: EnumObservation;
}>;
