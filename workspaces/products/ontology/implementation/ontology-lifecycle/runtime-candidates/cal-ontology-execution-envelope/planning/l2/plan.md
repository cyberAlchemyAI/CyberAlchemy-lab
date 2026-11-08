---
title: L2 Disposable Adapter Certification Plan
status: prepared-planning-candidate
updatedAt: 2026-09-03
owner: CyberAlchemy v2 product owner
route: CA2-ROUTE-PLAN
authorityEffect: none
---

# L2 Disposable Adapter Certification Plan

## Outcome and decision boundary

After L2, we know whether an independently authored disposable target adapter can be certified repeatably against the public execution contract without weakening any L0 or L1 guarantee.

The minimum working unit is one data-driven certification harness, one independent in-memory fixture that does not wrap or delegate to `InMemoryTarget`, one exact 18-vector set, and one deterministic certification receipt. L2 ends there. Real targets, credentials, live execution, and operator workflows belong to later decisions.

## Frozen L1 baseline

| Binding | Exact value |
| --- | --- |
| Repository commit | `5b665f4dc351853bee777f14e56cccdab6cbfb26` |
| Product candidate | `CAL-D65-EPOCH-002-RUST-EXECUTION-PROTOTYPE-002` |
| Product receipt | `receipts/tests.json` |
| Receipt SHA-256 | `802b91186fa6c41b21609bfe63428c3466fbc1519033e3692e39cf65fb00e509` |
| Adapter API SHA-256 | `066fb196f76ad7e04abb8e3b805bc5b192077fb07583aac21fd470138ded4ab7` |
| Existing adapter tests SHA-256 | `5de59e0e5d84be99e3ee1f3dff2608ced901cf60a646d9ee49fbcca56104ccec` |
| Existing result | 12/12 tests twice, dependencies current, format and Clippy PASS |

Changed baseline bytes make this plan stale and require re-planning or explicit reconciliation. The baseline proves L1 only; it does not authorize L2 implementation.

## Product-construction lane

| Wave | Product work | Exact output | Verification | Exit rule |
| --- | --- | --- | --- | --- |
| L2-W0 | Freeze the certification types and vector vocabulary. | `src/certification.rs`, schema, vector fixture | JSON schema checks and Rust type tests | Every vector has one stable ID, expected result, failure code, and state invariant. |
| L2-W1 | Build an independent disposable adapter fixture. | `tests/certification_contract.rs` | Static non-delegation check and happy-path engine run | Fixture imports the public trait but neither imports nor wraps `InMemoryTarget`. |
| L2-W2 | Execute all certification vectors and capture observations. | `CertificationReport` | Exact call order, preimage/final digest equality, failure code, and zero-effect assertions | 18/18 vectors pass and all failure vectors restore the preimage. |
| L2-W3 | Harden vector and report integrity. | Mutation tests and canonical report digest | Omission, reordering, duplication, and expected-result substitution probes | Every mutation is detected and returns `BLOCK`. |
| L2-W4 | Freeze the L2 product candidate. | `receipts/certification.json` and updated aggregate receipt | Two clean-target runs, byte-identical receipts, format and Clippy | Existing 12 L1 tests remain PASS and the L2 report is deterministic. |

## Exact certification vectors

| ID | Scenario | Required observation |
| --- | --- | --- |
| `CERT-01-BASELINE` | Exact disposable adapter | Ten ordered calls, PASS, exact rollback. |
| `CERT-02-CALL-ORDER` | Record every adapter call | Calls equal the canonical transition order exactly once. |
| `CERT-03-BINDING-IDENTITY` | Substitute adapter identity | Refused before preimage capture or mutation. |
| `CERT-04-LIVE-BINDING` | Mark adapter live | Refused before preimage capture or mutation. |
| `CERT-05-CREDENTIAL-BINDING` | Add credential kind | Refused before preimage capture or mutation. |
| `CERT-06-PREIMAGE-DRIFT` | Change source state | `TARGET_PREIMAGE_MISMATCH`; no transition call. |
| `CERT-07-STAGE-FAILURE` | Fail at stage | Exact emergency restoration. |
| `CERT-08-ACTIVATE-FAILURE` | Fail at activate | Exact emergency restoration. |
| `CERT-09-MIGRATE-FAILURE` | Fail at migrate | Exact emergency restoration. |
| `CERT-10-VERIFY-TARGET-FAILURE` | Fail target verification | Exact emergency restoration. |
| `CERT-11-CUTOVER-FAILURE` | Fail at disposable cutover | Exact emergency restoration. |
| `CERT-12-VERIFY-POSTIMAGE-FAILURE` | Fail postimage verification | Exact emergency restoration. |
| `CERT-13-ROLLBACK-FAILURE` | Fail normal rollback | Emergency restoration returns exact preimage. |
| `CERT-14-VERIFY-ROLLBACK-FAILURE` | Fail rollback verification | Emergency restoration remains exact and idempotent. |
| `CERT-15-REPORT-DETERMINISM` | Run the full set twice | Canonical report bytes and digest match. |
| `CERT-16-INDEPENDENT-FIXTURE` | Inspect fixture dependency surface | No `InMemoryTarget` import, wrapping, or delegation. |
| `CERT-17-VECTOR-OMISSION` | Remove one required vector | Vector-set digest mismatch and `BLOCK`. |
| `CERT-18-VECTOR-MUTATION` | Reorder, duplicate, or substitute an expectation | Canonical-set validation returns `BLOCK`. |

## Report contract

`CertificationReport` must contain the schema version, candidate ID, frozen L1 commit and receipt digest, adapter binding, vector-set digest, ordered per-vector outcomes, observed call order, preimage and final-state digests, pass total, external-effects flag, authority effect, and report digest.

PASS requires all of the following:

- the exact 18-vector set is present once each;
- every expected PASS or BLOCK result and failure code matches;
- every post-preimage failure returns the exact preimage;
- the independent fixture does not delegate to the concrete L1 adapter;
- two clean-target reports are byte-identical;
- all existing L1 tests remain unchanged and passing;
- `external_effects` is `false` and `authority_effect` is `none`.

## Future implementation allowlist

Only a later `CA2-ROUTE-IMPLEMENT` instruction may authorize these changes:

- `src/lib.rs`
- `src/certification.rs`
- `schemas/certification-vectors.schema.json`
- `tests/fixtures/certification-vectors.json`
- `tests/certification_contract.rs`
- `validate.py`
- `receipts/certification.json`
- `receipts/tests.json`
- `README.md`
- `implementation-layering.md`
- `l2-certification-plan.md`
- `l2-certification-contract.json`
- `Cargo.toml` and `Cargo.lock` only if an unavoidable dependency change is justified before mutation

## Non-regression guardrails

- Preserve the exact D65CUT decision, source cut, target cut, projection digest, and ten-step order.
- Live mode, credential-bearing targets, production data, and external effects fail before mutation.
- Every failure after preimage capture restores the exact preimage.
- Canonical events remain the replay source; snapshots remain noncanonical accelerators.
- L2 certification is product evidence only. It grants no adapter admission, product approval, activation, migration, cutover, publication, deployment, or external-effect authority.

## Operational lane and deferred residue

| Operational task | Owner | Affected stage | Causal blocker | Effect on L2 |
| --- | --- | --- | --- | --- |
| Select a real disposable integration target | CyberAlchemy v2 product owner | L3 | No target decision exists | Does not block L2. |
| Define target credentials and secret handling | Security and target owner | Post-product live preparation | Credentials are forbidden in L2 | Does not block L2. |
| Define maintenance, abort, and recovery windows | Operations owner | Live rehearsal/cutover | No live envelope exists | Does not block L2. |
| Author live adapter admission and cutover authority | Governance owner | External-effect stage | L2 product, approval, exact live bindings, and evidence absent | No live work may begin. |
| Repair unrelated Goals validation drift | Goals package owner | Goal registration | Package-wide source drift is outside this candidate | Prevents admission claims, not L2 prototype construction. |

## Prepared frontier

- Product frontier: L2 planning complete; implementation not authorized by this artifact.
- Runnable work after authorization: L2-W0 through L2-W4 in order.
- Exact product blocker: none identified against the frozen L1 baseline.
- Authority blocker: a future explicit `CA2-ROUTE-IMPLEMENT` instruction is required before code mutation.
- Deferred residue: every L3 target choice and every live operational concern.
