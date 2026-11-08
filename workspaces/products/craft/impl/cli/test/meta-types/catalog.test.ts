import assert from "node:assert/strict";
import test from "node:test";

import { CatalogError, FROZEN_META_TYPE_CATALOG, metaTypeIdForLabel, selectRealization, validateFrozenCatalog } from "../../src/meta-types/catalog.ts";

test("frozen catalog closes exactly 13 types and 39 rows", () => {
  assert.equal(validateFrozenCatalog(), FROZEN_META_TYPE_CATALOG);
  assert.equal(FROZEN_META_TYPE_CATALOG.backend_meta_types.length, 13);
  assert.equal(FROZEN_META_TYPE_CATALOG.realization_rows.length, 39);
  assert.equal(new Set(FROZEN_META_TYPE_CATALOG.realization_rows.map((row) => `${row.meta_type_id}/${row.language}`)).size, 39);
  assert.equal(Object.isFrozen(FROZEN_META_TYPE_CATALOG), true);
});

test("catalog selects exact baseline-bound rows", () => {
  const row = selectRealization(metaTypeIdForLabel("Entity"), "typescript");
  assert.equal(row.meta_type_id, "DS-D1.1");
  assert.equal(row.source.sha256, "c174f82e19e72b30f9305f005809bf8a63b52d102e708a9739a3d898b704b197");
  assert.equal(row.provider.sha256, "b53128e807f734043019e75e6b892900b83c320b909d859644f6a820a9c960f1");
  assert.equal(row.binding.sha256, "4c5b4d8f9e6febb255117a7a3e207b30dc369bfe61d8dc1933d792a7bbadb6e8");
});

test("unknown type, language, duplicate and digest drift fail closed", () => {
  assert.throws(() => metaTypeIdForLabel("Saga"), (error) => error instanceof CatalogError && error.code === "MTCLI_CATALOG_TYPE");
  assert.throws(() => selectRealization("DS-D1.1", "ruby"), (error) => error instanceof CatalogError && error.code === "MTCLI_CATALOG_LANGUAGE");
  const duplicate = structuredClone(FROZEN_META_TYPE_CATALOG);
  duplicate.realization_rows[1] = duplicate.realization_rows[0]!;
  assert.throws(() => validateFrozenCatalog(duplicate), (error) => error instanceof CatalogError && error.code === "MTCLI_CATALOG_DUPLICATE");
  const drift = structuredClone(FROZEN_META_TYPE_CATALOG);
  drift.baseline_digest = "0".repeat(64);
  assert.throws(() => validateFrozenCatalog(drift), (error) => error instanceof CatalogError && error.code === "MTCLI_CATALOG_BASELINE");
});
