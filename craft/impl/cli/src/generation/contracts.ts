import type { DecodedBody, DecodedRelationship } from "../input/project-model.js";
import type { CatalogRealizationRow, SupportedLanguage } from "../meta-types/types.js";
import type { SourceManifestV1 } from "../input/source-manifest.js";
import type { SystemIntegrationSelectionV1 } from "../system-integration/types.js";
import type { TypedSemanticClosureV1 } from "../typed-operation/closure.js";

export interface PlannedArtifact {
  readonly relative_path: string;
  readonly content: string;
  readonly size_bytes: number;
  readonly sha256: string;
}

export interface InstantiationPlanV1 {
  readonly schema_version: "domainspec.instantiation-plan/v1";
  readonly baseline: {
    readonly id: `domainspec-meta-types-current-implemented@${number}`;
    readonly digest: string;
    readonly manifest_sha256: string;
  };
  readonly input: {
    readonly project_id: string;
    readonly feature_id: string;
    readonly node_id: string;
    readonly kind: string;
    readonly meta_type_id: string;
    readonly body: DecodedBody;
    readonly relationships: readonly DecodedRelationship[];
    readonly source_manifest: SourceManifestV1;
    readonly typed_closure: TypedSemanticClosureV1 | null;
  };
  readonly language: SupportedLanguage;
  readonly selected_realization: CatalogRealizationRow;
  readonly generator_id: string;
  readonly system_integration: SystemIntegrationSelectionV1 | null;
  readonly artifacts: readonly PlannedArtifact[];
  readonly plan_sha256: string;
  readonly authority_effect: "none";
}

export interface GeneratorInput {
  readonly project_id: string;
  readonly feature_id: string;
  readonly node_id: string;
  readonly kind: string;
  readonly meta_type_id: string;
  readonly body: DecodedBody;
  readonly relationships: readonly DecodedRelationship[];
  readonly realization: CatalogRealizationRow;
  readonly typed_closure: TypedSemanticClosureV1 | null;
}

export interface GeneratorRegistration {
  readonly generator_id: string;
  readonly meta_type_id: string;
  readonly language: SupportedLanguage;
  readonly extension: "ts" | "py" | "rs";
}
