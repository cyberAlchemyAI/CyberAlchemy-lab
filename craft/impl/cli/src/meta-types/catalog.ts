import { FROZEN_CATALOG_V2 } from "./frozen-catalog.generated.js";
import { SUPPORTED_LANGUAGES, type CatalogRealizationRow, type FrozenCatalogV2, type SupportedLanguage } from "./types.js";

const SHA256_PATTERN = /^[a-f0-9]{64}$/;

export class CatalogError extends Error {
  readonly exitCode = 22;

  constructor(readonly code: string, message: string) {
    super(message);
    this.name = "CatalogError";
  }
}

function deepFreeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) deepFreeze(child);
  }
  return value;
}

function fail(code: string, message: string): never {
  throw new CatalogError(code, message);
}

export function validateFrozenCatalog(value: FrozenCatalogV2 = FROZEN_CATALOG_V2): FrozenCatalogV2 {
  if (value.schema_version !== "domainspec.meta-type-catalog/v2") fail("MTCLI_CATALOG_SCHEMA", "unsupported catalog schema");
  if (value.baseline_id !== FROZEN_CATALOG_V2.baseline_id) fail("MTCLI_CATALOG_BASELINE", "baseline identity drift");
  if (value.baseline_digest !== FROZEN_CATALOG_V2.baseline_digest) fail("MTCLI_CATALOG_BASELINE", "baseline digest drift");
  if (value.manifest_sha256 !== FROZEN_CATALOG_V2.manifest_sha256) fail("MTCLI_CATALOG_BASELINE", "baseline manifest digest drift");
  if (value.backend_meta_types.length !== 13 || value.realization_rows.length !== 39) fail("MTCLI_CATALOG_COVERAGE", "catalog denominator drift");
  const typeIds = new Set<string>();
  const labels = new Set<string>();
  for (const type of value.backend_meta_types) {
    if (typeIds.has(type.id) || labels.has(type.label)) fail("MTCLI_CATALOG_DUPLICATE", "duplicate meta-type identity");
    typeIds.add(type.id);
    labels.add(type.label);
  }
  const rows = new Set<string>();
  for (const row of value.realization_rows) {
    const key = `${row.meta_type_id}/${row.language}`;
    if (rows.has(key)) fail("MTCLI_CATALOG_DUPLICATE", `duplicate realization row:${key}`);
    rows.add(key);
    if (!typeIds.has(row.meta_type_id) || !labels.has(row.meta_type_label)) fail("MTCLI_CATALOG_SCHEMA", `unknown realization type:${key}`);
    if (!SUPPORTED_LANGUAGES.includes(row.language)) fail("MTCLI_CATALOG_LANGUAGE", `unknown realization language:${key}`);
    for (const ref of [row.source, row.provider, row.binding]) {
      if (!ref.path.startsWith("projects/domainspec-v2/") || !SHA256_PATTERN.test(ref.sha256)) fail("MTCLI_CATALOG_DIGEST", `invalid realization reference:${key}`);
    }
  }
  for (const type of value.backend_meta_types) {
    for (const language of SUPPORTED_LANGUAGES) {
      if (!rows.has(`${type.id}/${language}`)) fail("MTCLI_CATALOG_COVERAGE", `missing realization:${type.id}/${language}`);
    }
  }
  return deepFreeze(value);
}

export const FROZEN_META_TYPE_CATALOG = validateFrozenCatalog();

export function normalizeLanguage(value: unknown): SupportedLanguage {
  if (typeof value !== "string" || !SUPPORTED_LANGUAGES.includes(value as SupportedLanguage)) {
    fail("MTCLI_CATALOG_LANGUAGE", `unsupported language:${String(value)}`);
  }
  return value as SupportedLanguage;
}

export function metaTypeIdForLabel(label: unknown): string {
  if (typeof label !== "string") fail("MTCLI_CATALOG_TYPE", "meta-type label must be a string");
  const match = FROZEN_META_TYPE_CATALOG.backend_meta_types.find((type) => type.label === label);
  if (!match) fail("MTCLI_CATALOG_TYPE", `unsupported meta-type:${label}`);
  return match.id;
}

export function selectRealization(metaTypeId: unknown, language: unknown): CatalogRealizationRow {
  if (typeof metaTypeId !== "string") fail("MTCLI_CATALOG_TYPE", "meta-type id must be a string");
  const normalizedLanguage = normalizeLanguage(language);
  const matches = FROZEN_META_TYPE_CATALOG.realization_rows.filter(
    (row) => row.meta_type_id === metaTypeId && row.language === normalizedLanguage,
  );
  if (matches.length !== 1) fail("MTCLI_CATALOG_SELECTION", `expected one realization:${metaTypeId}/${normalizedLanguage}`);
  return matches[0] as CatalogRealizationRow;
}
