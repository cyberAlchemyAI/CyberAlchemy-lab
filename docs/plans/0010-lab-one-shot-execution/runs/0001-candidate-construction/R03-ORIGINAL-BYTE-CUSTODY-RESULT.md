# Reviewed artifact bytes: candidate implementation result

The candidate writer now keeps the original UTF8 JSON bytes for artifact revisions and schema inputs. Review cores and the signed proposal bind those exact bytes. Recreating JSON with different whitespace or escaping produces a different review and requires a new signature.

## Actual example

The owned fixture reviewed `work:lab-runtime:original-byte-work@candidate.1`, named **Review the café experiment 🔬**. Its original encoding uses CRLF, indentation and Unicode escapes. It is available in [the exact original JSON](examples/R03-0017/original-work.json).

- Original byte SHA256: `7c79b591022aff95acf66d60550da7ae2fada895486009bc3a3bea76e5f18457`.
- Recreated inherited JSON encoding SHA256: `917d83c96bed053354cdbc9692c08ad39f4ecf6297e8f538aa1c1a8a609eeaf7`.
- The parsed values match; the original encodings remain distinct.
- The old signature rejected a whitespace change. Applying the exact reviewed proposal, retrying it, reading it after a cold restart and deleting its SQLite cache preserved the original bytes.

The signature is from a newly created isolated test fixture. It is independently verified, and its private key and store were removed. It is not an actual owner decision.

## Validation

- **66 storage runtime methods passed:** all 38 inherited assertions and 28 new original-byte tests, each in its own process.
- Real crashes after pending creation, before HEAD publication and after publication passed verified recovery. Revision and withdrawal retained old originals.
- Cold reading of a committed frozen-v2 store preserved its transaction bytes and signatures, with successor writes correctly blocked.
- **17,525 independent checks passed**, including the retained public fixture signature, original bytes, exact source/core/transaction/retry bindings and all **8,533** prior proof files.
- All selected test and journey roots were removed. No private key or short memory was exported.

The selected aggregate reports PASS with all 66 case processes observed exiting 0. Its launcher handle later reported 143; that observation is retained explicitly and is not rewritten as exit 0. A failed preflight export check and missing-manifest authoring attempt are also retained.

## Protocol and integration findings

The existing reference correction engine already uses proposal/v2 for different closed fields. The selected storage candidate therefore declares distinct **original-json proposal and transaction** identifiers. Integration must retain all existing correction/reference bindings, endpoint mapping, scoped configuration and approval contracts.

The lower-level storage mechanism is implemented and proved. The current public API still has **12 of 34 handlers**, and the full plan remains at **35 of 46 closed criteria**. R03 remains in progress. JSON storage does not close binary package custody, complete reference/privacy/schema closure, governed query/export/files, ontology projection or the full review/admission journey.

## Next work

Compose this custody mechanism with the selected corrected engine and public prepare/review/admit/read/query/export paths. Then continue classification, failure and operational learning handlers, retaining all other original API and plan obligations. Include the exact protocol/codec/publisher/source-reader contracts and validation in S02. **R08 remains the one actual final owner checkpoint.**

Evidence: [R03-0017](/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/runtime-byte-custody-close-v1/receipts/R03-0017.json). Detailed next integration: [R03-CUSTODY-API-INTEGRATION-0001.md](R03-CUSTODY-API-INTEGRATION-0001.md).
