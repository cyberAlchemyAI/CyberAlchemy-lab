import type { AuthorityEffect, EvidenceLane, OperationalObservation } from "./operational-evidence.js";

export const LEGACY_V1_SHAPE_IDS = Object.freeze([
  "legacy-v1.failure-mapping-row/v1",
  "legacy-v1.otel-metric-declaration/v1",
  "legacy-v1.async-observer-signal/v1",
  "legacy-v1.telemetry-bundle/v1",
  "legacy-v1.slo-row/v1",
  "legacy-v1.prometheus-scrape-config/v1",
  "legacy-v1.prometheus-alert-rule/v1",
  "legacy-v1.infrastructure-plan/v1",
  "legacy-v1.deployment-plan/v1",
  "legacy-v1.load-result/v1",
  "legacy-v1.canary-result/v1",
] as const);

export type LegacyV1ShapeId = (typeof LEGACY_V1_SHAPE_IDS)[number];
export type LegacyV1ShapeKind =
  | "declaration-row"
  | "declaration-object"
  | "workflow-telemetry"
  | "policy-declaration"
  | "infrastructure-configuration"
  | "procedure-proposal"
  | "absent-family";
export type LegacyV1AdapterDisposition =
  | "normalize-as-candidate-local-simulation"
  | "reject-workflow-plane"
  | "reject-not-observed-evidence"
  | "reject-proposal-only"
  | "reject-family-absent";

export type LegacyV1SourceBinding = Readonly<{
  path: string;
  sha256: string;
  selector: string;
}>;

export type LegacyV1SourceShape = LegacyV1SourceBinding & Readonly<{
  shape_id: LegacyV1ShapeId;
  shape_kind: LegacyV1ShapeKind;
  adapter_disposition: LegacyV1AdapterDisposition;
  exact_fields: readonly string[];
}>;

export type LegacyV1SourceInventory = Readonly<{
  schema_version: "domainspec.orodi.legacy-v1-source-inventory/v1";
  inventory_id: string;
  captured_at: string;
  sources: readonly LegacyV1SourceShape[];
  claim_ceiling: string;
  authority_effect: AuthorityEffect;
}>;

export type LegacyV1AdapterInput = Readonly<{
  schema_version: "domainspec.orodi.legacy-v1-adapter-input/v1";
  input_id: string;
  source_shape_id: string;
  source: LegacyV1SourceBinding;
  payload: unknown;
}>;

export type LegacyV1NormalizationFinding = Readonly<{
  code: string;
  path: string;
  detail: string;
}>;

export type LegacyV1NormalizationResult = Readonly<{
  schema_version: "domainspec.orodi.legacy-v1-normalization-result/v1";
  adapter_id: "domainspec.orodi.legacy-v1-adapter";
  adapter_version: "1.0.0-candidate-local";
  evidence_lane: EvidenceLane;
  input_id: string;
  source_shape_id: string;
  source: LegacyV1SourceBinding | null;
  replayed_at: string;
  verdict: "normalized" | "rejected";
  normalized_observations: readonly OperationalObservation[];
  findings: readonly LegacyV1NormalizationFinding[];
  authority_effect: AuthorityEffect;
}>;
