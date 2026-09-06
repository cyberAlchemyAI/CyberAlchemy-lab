import { FROZEN_RELATIONSHIP_AUTHORITY_V1 } from "./frozen-authority.generated.js";
import type { FrozenRelationshipAuthorityV1, FrozenRelationshipSignature } from "./types.js";

export const RELATIONSHIP_AUTHORITY_SHA256 = "82c55ea1ad031d3135c5b8a85162e44b4e85f296b54057fda0dc38131ab376a1" as const;

export class RelationshipAuthorityError extends Error {
  readonly exitCode = 22;

  constructor(readonly code: string, message: string) {
    super(message);
    this.name = "RelationshipAuthorityError";
  }
}

function fail(code: string, message: string): never {
  throw new RelationshipAuthorityError(code, message);
}

function deepFreeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) deepFreeze(child);
  }
  return value;
}

const SPECIAL_RELATIONSHIP_OBLIGATIONS = new Set([
  "admit_same_and_cross_feature_scope",
  "derive_creation_targets_from_edge",
  "reject_authored_generated_projection",
  "reject_cross_feature_scope",
  "reject_deprecated_queries_alias",
  "reject_enforces_cross_label",
  "reject_inverse_collapse_with_owns",
  "reject_multiple_sources_per_target",
  "reject_multiple_targets_per_source",
  "require_admitted_workflow_scope",
]);

function isEndpointObligation(obligation: string): boolean {
  return /^reject_non_.+_(?:source|target)$/.test(obligation);
}

export function validateRelationshipAuthority(
  value: FrozenRelationshipAuthorityV1 = FROZEN_RELATIONSHIP_AUTHORITY_V1,
): FrozenRelationshipAuthorityV1 {
  if (value.schema_version !== "domainspec.relationship-authority/v1") fail("MTCLI_RELATIONSHIP_AUTHORITY_SCHEMA", "unsupported relationship authority schema");
  if (value.source_path !== "projects/domainspec-v2/definitions/relationships/relationships.yml") fail("MTCLI_RELATIONSHIP_AUTHORITY_SOURCE", "relationship authority source path drift");
  if (value.source_sha256 !== RELATIONSHIP_AUTHORITY_SHA256) fail("MTCLI_RELATIONSHIP_AUTHORITY_DIGEST", "relationship authority source digest drift");
  if (value.signature_count !== 31 || value.signatures.length !== 31) fail("MTCLI_RELATIONSHIP_AUTHORITY_COVERAGE", "relationship signature denominator drift");
  const active = new Set<string>();
  const obligations = new Set<string>();
  for (const signature of value.signatures) {
    if (!signature.id || active.has(signature.id)) fail("MTCLI_RELATIONSHIP_AUTHORITY_DUPLICATE", `duplicate relationship signature:${signature.id}`);
    if (signature.source_types.length === 0 || signature.target_types.length === 0 || signature.feature_scope.length === 0) fail("MTCLI_RELATIONSHIP_AUTHORITY_SCHEMA", `incomplete relationship signature:${signature.id}`);
    if (signature.validation_obligations.length === 0) fail("MTCLI_RELATIONSHIP_AUTHORITY_OBLIGATION", `relationship signature has no validation obligations:${signature.id}`);
    for (const obligation of signature.validation_obligations) {
      if (!isEndpointObligation(obligation) && !SPECIAL_RELATIONSHIP_OBLIGATIONS.has(obligation)) {
        fail("MTCLI_RELATIONSHIP_AUTHORITY_OBLIGATION", `unhandled relationship obligation:${signature.id}:${obligation}`);
      }
      obligations.add(obligation);
    }
    active.add(signature.id);
  }
  if (obligations.size !== 45) fail("MTCLI_RELATIONSHIP_AUTHORITY_OBLIGATION", `relationship obligation denominator drift:${obligations.size}`);
  const generated = new Set<string>();
  for (const view of value.generated_views) {
    if (!view.id || generated.has(view.id) || active.has(view.id) || !active.has(view.from_signature)) fail("MTCLI_RELATIONSHIP_AUTHORITY_GENERATED_VIEW", `invalid generated relationship view:${view.id}`);
    generated.add(view.id);
  }
  const deprecated = new Set<string>();
  for (const alias of value.deprecated) {
    if (!alias.id || deprecated.has(alias.id) || active.has(alias.id) || generated.has(alias.id) || !active.has(alias.replacement)) fail("MTCLI_RELATIONSHIP_AUTHORITY_DEPRECATED", `invalid deprecated relationship alias:${alias.id}`);
    deprecated.add(alias.id);
  }
  return deepFreeze(value);
}

export const FROZEN_RELATIONSHIP_AUTHORITY = validateRelationshipAuthority();
export const RELATIONSHIP_SIGNATURES: readonly FrozenRelationshipSignature[] = FROZEN_RELATIONSHIP_AUTHORITY.signatures;

export function relationshipSignature(id: string): FrozenRelationshipSignature | undefined {
  return RELATIONSHIP_SIGNATURES.find((signature) => signature.id === id);
}

export function deprecatedRelationship(id: string): Readonly<{ readonly id: string; readonly replacement: string; readonly reason: string }> | undefined {
  return FROZEN_RELATIONSHIP_AUTHORITY.deprecated.find((alias) => alias.id === id);
}

export function generatedRelationshipView(id: string): Readonly<{ readonly id: string; readonly from_signature: string; readonly source_type: string; readonly target_type: string }> | undefined {
  return FROZEN_RELATIONSHIP_AUTHORITY.generated_views.find((view) => view.id === id);
}
