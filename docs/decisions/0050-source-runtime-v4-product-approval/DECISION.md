# v4 migration Product approved

Your approval -> accept the exact tested v4 prototype -> prepare for operational evaluation

**Product approval** means this version's declared behavior, coverage and limitations are accepted.
**Cutover** means switching actual consumers to it; that remains a separate decision.

The accepted scope is 21 packages, 815 nodes, 1,210 relations and 422 supporting documents, with import/export and event-based updates. Coverage is limited to the exact manifest. Domain-specific semantic compilation and transitive reference closure are outside this scope; production durability and scale are unproven.

Tests provide evidence that the prototype meets its checks -> your decision accepts whether that scope meets the intended need.

Approval was explicitly given as `approved` on 2026-09-07T00:34:51.898963Z.

- Candidate SHA-256: `496a699de7ac0182b4456d8c89f19e8d250e055b5fbcaf2ab016352cacbfe2fa`
- Product-test receipt SHA-256: `4b190b290ab8ce39e9ae5553c5c67714e3de2e89eca722bd2cbf5c1d4a74dba0`

The historical receipt records PASS and 23 focused tests. Current checks verified 21 candidate/preserved files and the candidate and receipt digest links. Rust tests were not rerun. Local runtime stores are absent and cargo is unavailable on PATH. All 418 manifest references matched at the relocated source root.

Restore local execution -> rerun acceptance -> demonstrate imported data and updates -> define consumer cutover

This decision grants Product approval only. It records no binding admission, runtime adoption, source admission, consumer cutover, publication, release, deployment or source retirement.

The frozen candidate and DAG retain their preapproval wording. [decision.json](decision.json) records the successor approval state without rewriting that evidence.
