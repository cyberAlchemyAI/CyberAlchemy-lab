import {canonicalJson, sha256} from '../input/source-manifest.js';
import type {TypedQueryContract} from '../typed-backend/contracts.js';

/** Additive candidate contract. Does not rewrite the pinned list-query profiles. */
export const QUERY_CARDINALITY_EXTENSION = Object.freeze({
  schema_version: 'domainspec.query-cardinality-extension/v1-candidate',
  typed_contract: 'domainspec.typed-query/v2',
  base_scope: 'input-validation-filtering-field-projection-and-read-only-dependencies',
  result_override: 'explicit-list-or-optional-projection',
  list: 'all-selected-projections-in-source-or-explicit-sort-order',
  optional_zero: 'native-absence',
  optional_one: 'one-projection-not-a-list-or-constructed-entity',
  optional_many: 'QUERY_CARDINALITY',
  optional_limit: 'forbidden',
  evaluation: 'validate-source-then-filter-then-check-cardinality-then-project',
  authority_effect: 'none',
});

export function queryCardinalityExtension(contract: TypedQueryContract, language: 'typescript' | 'python' | 'rust') {
  return contract.schema_version === 'domainspec.typed-query/v2' ? {
    protocol_id: `${language}.bound-query/v2-candidate`,
    result_cardinality: contract.result_cardinality,
    cardinality_extension: {schema_version: QUERY_CARDINALITY_EXTENSION.schema_version,
      contract: QUERY_CARDINALITY_EXTENSION, sha256: sha256(canonicalJson(QUERY_CARDINALITY_EXTENSION)), authority_effect: 'none'},
  } : {};
}
