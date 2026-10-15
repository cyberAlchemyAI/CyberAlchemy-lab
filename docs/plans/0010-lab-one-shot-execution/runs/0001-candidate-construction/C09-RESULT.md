# C09 — Successor integration verification

Status: candidate criteria complete. Authority effect: none. Actual owner outcome: null.

## Exact package and evidence

- Candidate manifest: `implementation/lab-integration/candidates/v1/packages/0001/manifest.json`, SHA256 `a491491d5a9b6d42760ceeb8162e611c4563c790965734ea10dd97a9000b437b`.
- Selection: `implementation/lab-integration/candidates/v1/packages/0001/selection.json`, SHA256 `456a6d2f1c86bd4f6897ae5f21bfb080e154562c51ef9a215e2ab9c3814477c7`.
- Terminal receipt: `implementation/lab-integration/candidates/v1/receipts/C09/0001/receipt.json`.
- Observed example: `implementation/lab-integration/candidates/v1/receipts/C09/0001/observed-predecision-example.json`.

The frozen source closure contains 910 files. All 213 declared cases passed in 846.658 seconds, including all 38 frozen v2 compatibility cases. Groups: profiles 23, extensions 29, replay 14, transition 20, promotion 20, bootstrap 20, context 36, joined inspection 6, publication invalidation 1, manifest 6, frozen v2 38. Every case has terminal evidence; the final manifest check detected no changed source binding. The frozen v1/v2 packages and original preparation remain preserved.

## Observed integration

An isolated D75 source inspection joined independently pinned Project State, the signed bootstrap catalog, a separately reconstructed candidate branch, and native Rust semantic/governance replay. The catalog contained 144 carrier versions, 485 inherited source subjects, six unadmitted candidate subjects, and 41 Relation Kinds. Fresh-process inspection reconstructed the same selected Project State and candidate postures. Wrong source, catalog, branch and Project HEAD pins failed.

A separate isolated promotion fixture changed the selected source closure. Consumption of the old Agent context failed and erased Session memory. The committed publication bundle survived cold verification and repair without a second fixture owner response. This provides controlled process-interruption and recovery evidence; it does not establish power-loss durability.

## Scope and limits

C09 verifies integration and supplies an exact example. Earlier C08 narrative that assigned generic API dispatch to C09 was incorrect; the original C09 contract requires successor integration verification. General trusted API authority, workflow execution, operator surfaces, ontology domain mapping and broader native profiles remain later obligations.

Replay acceleration remains a measured no-op with full verification and no cache. The C03 performance FLAG remains: one-transaction Session samples exceeded 30 seconds, five-transaction setup failed within its bound, and no Product SLA was established. No real Work satisfaction, human pilot, canonical admission, activation, external effect, commit or push is claimed.

Next: C10 prepares independent exact successor review members. Actual owner disposition remains R08, and canonical application remains A01.
