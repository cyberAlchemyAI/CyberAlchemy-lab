export type RelationshipFeatureScope = "same-feature" | "cross-feature" | "ui" | "ui-backend";

export type RelationshipMultiplicity =
  | "one_to_one"
  | "one_to_many"
  | "one_to_many_ordered"
  | "many_to_one"
  | "many_to_many";

export interface FrozenRelationshipSignature {
  readonly id: string;
  readonly source_types: readonly string[];
  readonly target_types: readonly string[];
  readonly multiplicity: RelationshipMultiplicity;
  readonly feature_scope: readonly RelationshipFeatureScope[];
  readonly inverse: Readonly<{ readonly kind: "none" | "generated_view"; readonly id?: string }>;
  readonly validation_obligations: readonly string[];
  readonly generated_source_projection?: Readonly<{
    readonly attribute: string;
    readonly value_shape: "concept-reference-set";
    readonly derivation: "outgoing-targets";
    readonly authorship: "forbidden";
  }>;
}

export interface FrozenRelationshipAuthorityV1 {
  readonly schema_version: "domainspec.relationship-authority/v1";
  readonly source_path: "projects/domainspec-v2/definitions/relationships/relationships.yml";
  readonly source_sha256: string;
  readonly signature_count: 31;
  readonly signatures: readonly FrozenRelationshipSignature[];
  readonly generated_views: readonly Readonly<{
    readonly id: string;
    readonly from_signature: string;
    readonly source_type: string;
    readonly target_type: string;
  }>[];
  readonly deprecated: readonly Readonly<{
    readonly id: string;
    readonly replacement: string;
    readonly reason: string;
  }>[];
}
