# Exact schema bytes in the composed API writer

Status: required integration analysis; authority effect none.

The first composed candidate preserves the inherited descriptor `schema_sha256` encoding rule and separately retains original schema bytes. This proves custody while deliberately leaving the full public schema/header/export binding open. The complete Lab must bind the descriptor and Schema content to the actual original bytes rather than export a different encoding under an unchanged hash claim.

Select a distinct successor protocol family for this changed schema custody contract. Preserve old proposal/transaction families and their historical deterministic replay. In the new family:

1. Every new schema has an exact original content entry and a parsed value used by validators. A descriptor or contract that points to that schema uses its original byte SHA256.
2. Existing baseline schema paths retain their independently captured original file SHA256. Existing runtime schema paths retain their established content identity. Reusing an immutable path with different bytes is rejected, even when parsed values match.
3. The canonical replay projection keeps explicit schema-content bindings, including original byte hash, encoding and proposal/transaction selector. Legacy schemas without an original-byte envelope retain the inherited canonical schema encoding; no missing original is fabricated.
4. All schema references/selectors/dependencies validate against the same frozen closure. Syntax caching never caches instance, authority, source or dependency verdicts.
5. Artifact Type header/body/source metadata, query cache, package export/import and managed schema file output use that same declared exact content identity. Raw and structural hashes remain separately labeled.
6. Review cores and signatures bind the descriptor, contract and every schema content entry. The actual full original candidate and intended member/effect closure is reviewed at S02/R08.

This is not a new Relationship Kind or endpoint pair. It is a versioned storage/protocol representation change requiring an exact final review member. Binary materials, complete API reference/privacy/authority closure and original remaining task requirements still apply.
