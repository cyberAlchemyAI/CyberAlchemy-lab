export const SUPPORTED_LANGUAGES = ["typescript", "python", "rust"] as const;

export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

export interface CatalogDigestRef {
  readonly path: string;
  readonly sha256: string;
}

export interface CatalogMetaType {
  readonly id: string;
  readonly label: string;
}

export interface CatalogRealizationRow {
  readonly meta_type_id: string;
  readonly meta_type_label: string;
  readonly language: SupportedLanguage;
  readonly source: CatalogDigestRef;
  readonly provider: CatalogDigestRef;
  readonly binding: CatalogDigestRef;
}

export interface FrozenCatalogV2 {
  readonly schema_version: "domainspec.meta-type-catalog/v2";
  readonly baseline_id: `domainspec-meta-types-current-implemented@${number}`;
  readonly baseline_digest: string;
  readonly manifest_sha256: string;
  readonly backend_meta_types: readonly CatalogMetaType[];
  readonly realization_rows: readonly CatalogRealizationRow[];
}
