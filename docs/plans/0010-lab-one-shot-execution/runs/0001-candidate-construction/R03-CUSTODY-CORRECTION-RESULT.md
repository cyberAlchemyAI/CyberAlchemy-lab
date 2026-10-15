# Artifact and schema originals integrated with correction rules

Candidate proof **R03-0018**. R03 remains in progress. The full plan remains **35/46 criteria closed**, with **12/34 actual API operations** and **22 remaining**. One actual final owner checkpoint remains **R08 after full S02**.

## Work completed

The composed runtime now retains exact original JSON bytes for artifacts and schemas. Its new explicit protocol families bind the Artifact Type descriptor, schema contract and immutable source selector to the original schema SHA256. A changed encoding at an established schema path is rejected, even when the parsed JSON is equal.

The correction profile, original member witnesses, carrier/endpoint rules, independent domain grants and configuration-bound signatures retain their checks. Ten historical corrections were actually applied in an owned fixture; exact retry, captured original reads, SQLite BLOB parity, cache deletion and a cold process were verified. The owned signer/store were removed.

A historical reader is bound to the exact original v2 code and profile. It verifies old signed transactions under their original interpretation. Those stores remain stale for successor writes. The failed predecessors remain preserved.

## Verification

| Suite | Passing methods |
| --- | ---: |
| Original runtime | 38 |
| Original byte custody | 28 |
| Correction guards | 67 |
| Schema syntax cache | 9 |
| Relationship coupling | 35 |
| New exact schema custody | 12 |
| **Total** | **189** |

The correction journey passed **49 named checks including cleanup**. Its immutable numeric counter was recorded before cleanup as 48; the independent audit explicitly reconciles that observation. No frozen result was rewritten.

The independent audit passed **17,922 checks**, including an independently reconstructed and verified Ed25519 signature. The new receipt binds **9,022 files**, retaining all **8,773 parent files**. The global currentness check passed against all 36 active receipts, 77 original preparation files and 887 source bindings.

## Concrete example

The [original Work schema](examples/R03-0018/original-work-schema.json) is copied byte for byte from the actual owned fixture evidence. Its SHA256 is `447765bef7bd8550e76d8df0e86d7f30b38c094a7de629f07b8cc8c30dc68907`. The [rendered carrier descriptor](examples/R03-0018/rendered-carrier-descriptor.json) selects that same schema digest. The [provenance](examples/R03-0018/provenance.json) keeps its inherited encoder digest and rendered explanation separate. These files provide an owned candidate example and have no canonical admission effect.

## Next

Wire this foundation into the public API: provision a new independently bound source, connect the captured original reader, update artifact headers/body reads and the complete privacy-aware SQLite projection, then rebuild exact preparation cores. Preserve all old reader branches and permissions. The [integration order](R03-CUSTODY-API-INTEGRATION-0002.md) lists the implementation boundaries.

Complete the 22 remaining original APIs and all remaining R03-R07/S02 conditions before the final R08 review. Binary materials, complete exports, actual Tool/model dispatch, human pilot and admitted/live operation remain open. This proof supplies no owner outcome, canonical admission, activation, publication or complete-Lab claim.

## Exact evidence

- Runtime source: `product/lab/release-candidates/v1/interface/custody-correction-v4/source-manifest.json`, SHA256 `4aec6a68b6398d43d10afb7399897ac004d2a2ad869cbd5fe1aee8d2e08f024e`.
- Partial proof: `product/lab/release-candidates/v1/interface/custody-correction-close-v1/receipts/R03-0018.json`, SHA256 `61fa64a9cc7b7d1147979b681b8f75f00877cb92b94ba64969737e4e43352072`.
- Currentness: `docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/currentness-receipts/0077.json`, SHA256 `2e19342183ac50910f820ce7b82f67ba28431114ce3dafe95acceacd663e7fda`.
