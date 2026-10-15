# R03 exact artifact reader and SQLite result

Result: **PASS for this partial candidate step**. Full R03 remains in progress. The full plan remains active at **28/46 completed tasks**. Authority effect: none. Actual owner outcome: absent.

## New usable behavior

The successor authenticated reader implements four original API handlers. `lab.status` and `catalog.get` preserve their earlier behavior; the new handlers are:

| Handler | Observed behavior |
| --- | --- |
| `artifact.inspect` | Exact identity/version/carrier/byte checks, original or explicitly encoded selected body, requested sections, independent status facets and contract/gap disclosure |
| `artifact.query` | Exact revision references, carrier/identity selectors, bounded typed traversal, canonical or verified SQLite read basis, historical cuts, freshness and generation-bound pagination |

The SQLite projector uses the original exact DDL in a disposable owned generation. Complete revision population, available original-byte cache entries, contract selectors, valid typed connections, stream watermarks, integrity and foreign keys are verified before ready selection. Later reads verify independently captured file/row/cut metadata and compare SQL selection to signed-source canonical selection. Corruption is refused; prefer-projection explicitly discloses canonical fallback. Context close removes the generation and cold reconstruction creates a new one.

## Verification and exact closure

- **104/104** final checks passed in **249.600 seconds**: 61 inherited authentication/transport guards and 43 new inspection/query/SQLite guards.
- **11/11** real child processes passed: eight authentication/transport cases plus inspection/SQL, historical-query and cold-rebuild episodes.
- **95** original frames and **27** API replies independently checked, including public Ed25519 signatures and separate wire/message/context/handler byte bindings.
- Current selected cut: **508** exact eligible revisions. Historical genesis: **485**. Full canonical/SQL reference parity and warm/cold reconstruction passed.
- **2,630** exact file bindings retain the original schema inputs, prior API/inspection/coupling proofs, failed attempts and real frame evidence.

Receipt: `product/lab/release-candidates/v1/interface/api-v2/receipts/R03-0004.json`  
SHA-256: `1dca180daad5f3a2a73e046fbf75e3368043216e30098bef6af37eee91b0cfbd`

Package: `product/lab/release-candidates/v1/interface/api-v2/`  
Reader episodes: `product/lab/release-candidates/v1/examples/operator-journeys/api/0009/`  
Transport episodes: `product/lab/release-candidates/v1/examples/operator-journeys/api/0010/`

## Gaps found rather than hidden

| Gap | Actual evidence and current behavior |
| --- | --- |
| 133 Artifact Type descriptor bodies | Their declared root schema does not accept the exact descriptor body. Metadata is queryable; this API body request returns an explicit contract error. Captured admission is unchanged. |
| Ten captured Typed Relations | Exact endpoint versions such as `...@candidate.1` are absent from this selected cut. Both signed-runtime and reader closure refuse them; their original failure stages are retained. No relation or endpoint is silently rewritten. |
| One captured identity ambiguity | Eight current carrier revision entries share `cal.artifact-type.artifact-type` in the captured subject index. Every revision is retained, and no unique head is fabricated. The source/index representation requires exact repair. |

The body audit accepts **375** other exact bodies. **45/55** captured Typed Relations close under the signed runtime, actual signature subject and original API endpoint/qualifier schema. Traversal preserves raw Project endpoint kinds separately from Project Identity carriers. Signature catalog keys remain distinct from actual Relation Kind subject identities.

Coverage: `product/lab/release-candidates/v1/interface/api-v2/receipts/coverage.json`  
Connection reasons: `product/lab/release-candidates/v1/interface/api-v2/receipts/connection-gaps.json`

The first projector's head uniqueness failure, incorrect local Work fixture selector, signature-subject identity collapse and passing suite's test-only resource warning remain inspectable. The fixture selector was corrected to the actual original signed Evidence Set; the test connections now close explicitly.

## Next work and approval boundary

**30 of the original 34 API handlers remain unfinished.** Complete descriptor-envelope coverage and exact source/index/reference closure before claiming full inspection. Broader candidate queue/Decision evidence, persistent SQLite/ontology parity and complete Agent/session operational journeys remain required, along with W07 and the rest of the DAG.

No authoring transaction, canonical admission, live service effect, private key export, Session memory export, human pilot or owner response occurred. Candidate construction remains covered by the existing authorization. The exact successor schema/authentication adapter/handler/projector package and its evidence are final S02/R08 members. A01–A04 retain their original boundaries.
