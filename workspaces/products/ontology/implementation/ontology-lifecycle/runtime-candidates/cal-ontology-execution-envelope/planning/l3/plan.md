---
title: L3 Disposable Filesystem Rehearsal Plan
status: implementation-candidate
updatedAt: 2026-09-03
owner: CyberAlchemy v2 product owner
route: CA2-ROUTE-IMPLEMENT
authorityEffect: none
---

# L3 Disposable Filesystem Rehearsal Plan

## Outcome and decision boundary

After L3, we know whether the certified execution-target contract can cross a
real operating-system boundary while remaining disposable, non-live,
credential-free, path-confined, rollback-exact, and deterministic.

The selected target kind is a newly created directory below the process
temporary directory. The adapter accepts no caller-supplied path, network
address, credential, production data, or live binding. Filesystem writes are
local disposable rehearsal effects; they are removed before the rehearsal
returns and do not constitute an external-system effect.

## Frozen baseline

| Binding | Exact value |
| --- | --- |
| L1 receipt | `v1/receipts/tests.json` |
| L1 receipt SHA-256 | `802b91186fa6c41b21609bfe63428c3466fbc1519033e3692e39cf65fb00e509` |
| L2 candidate | `CAL-D65-EPOCH-002-ADAPTER-CERTIFICATION-PROTOTYPE-003` |
| L2 receipt | `v1/receipts/certification.json` |
| L2 receipt SHA-256 | `4046bc8954c232e40e37b0e3b9d8d9f54f0a59b378cabc8f4d9d2d8277ad5080` |
| L2 result | 20/20 Rust tests per run; 18/18 vectors; deterministic report |

The L1 and L2 receipts remain immutable historical evidence. L3 emits a new
receipt and never rewrites either predecessor.

## Product-construction lane

| Wave | Product work | Exact output | Verification | Exit rule |
| --- | --- | --- | --- | --- |
| L3-W0 | Freeze the exact filesystem binding and rehearsal invariants. | This plan, `contract.json`, schema, fixture. | Digest and shape checks. | One target kind and six invariants are exact. |
| L3-W1 | Implement the path-confined disposable adapter. | `src/filesystem_target.rs`, exact envelope binding. | Public tests. | No caller path, credentials, network, live mode, or production data. |
| L3-W2 | Exercise the full D65 sequence through filesystem bytes. | Rehearsal API and integration tests. | Exact trace, preimage, rollback, and cleanup assertions. | Happy path crosses the filesystem boundary and restores exact bytes. |
| L3-W3 | Exercise boundary-specific failure and tamper cases. | Failure tests. | Cutover fault, preimage tamper, substituted binding, cleanup checks. | Every failure is fail-closed and leaves no rehearsal directory. |
| L3-W4 | Freeze deterministic L3 product evidence. | `receipts/filesystem-rehearsal.json`. | Two clean-target runs, report-byte equality, format and Clippy. | Prior tests pass and the L3 receipt is deterministic. |

## Exact rehearsal invariants

1. `FSR-01-PATH-CONFINEMENT`: the adapter creates its own directory below the
   process temporary directory and accepts no path from the caller.
2. `FSR-02-EXACT-BINDING`: only
   `cal.prototype.rust-disposable-filesystem-target/epoch-002` is accepted.
3. `FSR-03-BYTE-PREIMAGE`: rollback restores the exact preimage bytes, not
   merely a semantically equivalent object.
4. `FSR-04-FAILURE-RESTORATION`: a post-preimage failure triggers exact
   emergency restoration.
5. `FSR-05-CLEANUP`: the complete rehearsal directory is absent when the
   rehearsal returns.
6. `FSR-06-DETERMINISTIC-REPORT`: two clean rehearsals emit identical canonical
   report bytes; temporary paths are never evidence fields.

## Mutation allowlist

- `planning/l3/plan.md`
- `planning/l3/contract.json`
- `v1/src/lib.rs`
- `v1/src/filesystem_target.rs`
- `v1/tests/filesystem_rehearsal.rs`
- `v1/tests/fixtures/filesystem-rehearsal.json`
- `v1/schemas/filesystem-rehearsal.schema.json`
- `v1/validate-l3.py`
- `v1/receipts/filesystem-rehearsal.json`
- `v1/Cargo.toml`
- `v1/Cargo.lock`
- `v1/README.md`
- `v1/implementation-layering.md`

## Operational lane and deferred residue

| Operational task | Owner | Affected stage | Causal blocker | Effect on L3 |
| --- | --- | --- | --- | --- |
| Select a service or production target | Product and target owner | Post-L3 | No approved real target | Does not block disposable filesystem construction. |
| Supply credentials and secret handling | Security and target owner | Live preparation | Credentials forbidden in L3 | Does not block L3. |
| Define maintenance and abort windows | Operations owner | Live rehearsal/cutover | No live envelope | Does not block L3. |
| Admit an adapter or authorize effects | Governance owner | Authority stage | Tested product approval and exact bindings absent | No live work may begin. |

## Claim ceiling

An L3 PASS proves only the isolated disposable-filesystem rehearsal candidate.
It does not approve or admit an adapter, make a live target available, use
credentials, migrate production data, perform an operational cutover, publish,
deploy, or authorize external effects.
