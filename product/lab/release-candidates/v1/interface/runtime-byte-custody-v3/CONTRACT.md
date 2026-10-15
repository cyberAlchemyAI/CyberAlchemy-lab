# Original JSON byte custody — candidate

Status: candidate implementation; actual admission and public API integration pending. Owner outcome: none.

## Selected representation

`lab-runtime-original-json-proposal/v1-candidate` extends the existing closed proposal with a required `content` entry on each target and an exact `schema_contents` map. Admission and revision carry base64 original UTF8 JSON bytes; withdrawal carries null and preserves the original revision. Every supplied schema also retains its original bytes. Content entries use the existing proposed `lab-artifact-content-entry/v1-candidate` schema, with application/json and null semantic binding under this selected profile.

The corresponding `lab-runtime-original-json-transaction/v1-candidate` embeds the complete signed proposal. One existing atomic HEAD publication makes records and original content visible together. No extra content authority or independent publication point is introduced.

The original-byte SHA256, structural record digest, structural target/proposal digest, approval byte hash and semantic/governance event digests remain distinct. `common.digest` is the frozen structural JSON algorithm, not a semantic equivalence claim. Parsed JSON must match it exactly; booleans and numbers are not collapsed. Descriptor schema SHA256 retains its inherited schema encoding contract; the schema's original-byte SHA256 is separately held in its content entry.

## Signature and compatibility

Each stable Decision core binds its full target including the original entry. The provisioned fixture approval binds the complete proposal and all cores, scope, policy, challenge route, source snapshot and expected HEAD. A whitespace or escaping change requires a new review and signature. Existing proposal/v1, transaction/v1 and approval/v1 encoding/signature rules are preserved. Cold reading of existing v2 histories is supported; successor source profiles remain read-only on old stores and need explicit fresh branch provisioning for writes.

This package's default store is `.local/lab-runtime/byte-custody-v3/store`. Validation uses only newly created isolated stores. No existing store is initialized, migrated or rebased.

## Retrieval and disposable SQLite

`original_bytes` independently replays the canonical chain, checks the requested exact cut and exact immutable revision, verifies its source selector, original hash and parsed structural record, then returns the original bytes. Legacy embedded records retain their explicitly declared inherited encoding. Baseline repository files remain independently hash-bound original files and must still be present; this candidate does not retroactively pack them or reconstruct missing originals.

`build_content_cache` projects committed authored targets and schema inputs into exact SQLite BLOBs. It verifies parity and records the canonical cut. Deleting or corrupting this cache cannot change replay or the original content. It is a bounded storage primitive, not the complete governed files.materialize/package.export or artifact.query API.

## Bounds and remaining integration

One original is limited to 1 MiB, one proposal to 16 MiB original content, 64 targets and 64 schemas. Strict parsing rejects duplicate keys, nonfinite numbers, unpaired surrogates, non-object JSON and excess nesting. No broad storage performance claim is made.

This selects JSON custody for the existing JSON writer. Binary evidence/package materials, full transaction/source/schema/reference/privacy closure, public transport permission and paths, managed file publication, export/import/install, ontology joins, final review members and actual R08 remain obligations. Candidate conformance does not supply admission, runtime activation or actual owner authorization.

Successor reason: the predecessor export table selected the legacy proposal schema while its generated file selected both explicit versions. v2 corrects only that export entry and candidate-local source/default-store locators. The failed predecessor is immutable and retained.

Protocol identifier audit: existing corrections-v1/engine-next already declares lab-runtime-proposal/v2-candidate with correction-specific fields. This successor uses distinct original-json proposal/transaction identities, preserving the corrected semantic and scoped authority contracts as independent integration inputs. It does not select the bare writer as a replacement for the correction engine.
