---
title: Ontology Execution Target Adapter Implementation Layering
status: prototype
updatedAt: 2026-09-03
owner: CyberAlchemy v2 product owner
scope: capability
---

# Ontology Execution Target Adapter Implementation Layering

## Context and method

- Target: reusable, fail-closed target adapter boundary for the D65 execution envelope.
- Current state: L4 state-bearing local sandbox product candidate implemented; its evidence remains separate from the frozen L1-L3 receipts.
- Primary operator: the future governed ontology execution runtime.
- Primary constraint: no live target, credential, external effect, or authority expansion.
- Boundary rule: each layer ends at the smallest tested slice that unlocks the next decision.
- Value/cost rule: prefer a decision or risk reduction over integration breadth and operational coordination.

## Layer decisions

| Layer | Decision question | Minimum working unit | Included scope | Explicitly deferred | Exit evidence | Promotion decision |
| --- | --- | --- | --- | --- | --- | --- |
| L0 | After this layer, we know whether the exact D65 sequence can execute and roll back deterministically. | Concrete in-memory Rust engine. | Ten ordered steps, exact cuts, live refusal, rollback. | Adapter reuse and operational bindings. | Eight public tests run twice. | Completed: continue to L1. |
| L1 | After this layer, we know whether the engine can use a public adapter contract without weakening fail-closed behavior. | Generic engine plus external conforming wrapper. | Adapter trait, binding preflight, emergency rollback for every post-preimage failure. | Filesystem, services, credentials, live targets. | Public and adapter suites run twice; format and Clippy pass. | Continue only if all L0 guarantees remain true. |
| L2 | After this layer, we know whether independently authored disposable adapters can be certified repeatably. | Adapter certification harness and richer fault matrix. | Contract vectors, transition call-order evidence, deterministic certification receipt. | Production topology and operator workflow. | Independent adapter fixture passes all vectors. | Implemented as `CERTIFICATION-PROTOTYPE-003`; freeze exact test evidence. |
| L3 | After this layer, we know whether one reviewed non-live target adapter can rehearse against a disposable system boundary. | Exact disposable filesystem adapter. | Adapter-created temporary root, canonical state bytes, exact binding, rehearsal-only pre/postimages, cleanup. | Caller paths, services, live activation, real credentials, production migration, operational cutover, deployment. | 27 Rust tests per run, six exact invariants, deterministic rehearsal receipt, byte-exact rollback, and complete cleanup. | Implemented as `FILESYSTEM-REHEARSAL-PROTOTYPE-004`; product approval and every authority decision remain separate. |
| L4 | After this layer, we know whether bounded activation state can survive long enough to inspect without becoming a live or operational target. | Distinct state-bearing local sandbox plus activation harness. | Exact L4 selection, new identity, adapter-owned temporary root, stage and sandbox activation, persistent observation window, explicit teardown. | Caller paths, services, network, credentials, production data, governed runtime activation, migration, operational cutover, deployment. | 35 Rust tests per run, seven exact invariants, deterministic L4 receipt, state survival, exact restore, and cleanup. | Implemented as `STATE-BEARING-SANDBOX-PROTOTYPE-005`; product approval and adapter admission remain separate. |

## Capability progression

| Capability | L0 | L1 | L2 | L3 | L4 |
| --- | --- | --- | --- | --- | --- |
| Target boundary | Concrete type | Public trait plus exact binding | Certifiable adapter vectors | Exact path-confined filesystem integration | Distinct state-bearing sandbox binding refused by the L3 engine |
| Failure handling | Mid-sequence restore | Restore after every post-preimage failure | Fault matrix | Byte-exact boundary restoration and cleanup | Emergency restore plus explicit exact teardown |
| Evidence | Engine tests | Engine plus external-adapter tests | Certification receipt | Deterministic filesystem rehearsal receipt | Deterministic activation-observation and teardown receipt |
| Effects | None | None | None | Local disposable filesystem writes only; no external-system effects | Local temporary state survives only until explicit teardown; no external-system effects |

## Current product frontier

- Current layer: L4, implemented by `CAL-D65-EPOCH-003-STATE-BEARING-SANDBOX-PROTOTYPE-005` under candidate identity `cal.prototype.rust-state-bearing-sandbox-target/epoch-003`.
- Runnable product work: run all 35 Rust tests twice, emit the L4 report twice, verify seven exact sandbox invariants and the selected L3/L4 dependencies, lint, and freeze `receipts/stateful-sandbox.json`.
- User-visible outcome: bounded sandbox activation state survives the activation call for inspection, then explicit teardown restores exact preimage bytes and removes the complete root.
- Risk reduced: vacuous activation, implicit cleanup, binding substitution, live-mode drift, migration/cutover leakage, failure residue, and path-dependent evidence are detected.
- Main cost drivers: state-lifetime ownership, explicit teardown, boundary-specific restoration, and proof that the existing engine cannot accept the new binding accidentally.
- Non-regression: all L0-L3 tests, exact event cuts, ten-step L3 ordering, live refusal before mutation, no credentials or network, no production data, no external-system effects, exact restoration, and deterministic receipts remain mandatory.

## Operational lane and deferred residue

| Operational task | Owner | Affected future stage | Current blocker | Product-lane effect |
| --- | --- | --- | --- | --- |
| Select a service or production target kind | CyberAlchemy v2 product owner | Post-L3 | No approved real target | Does not block the disposable filesystem product. |
| Supply credential handling | Security and target owner | Post-product authority stage | Credentials intentionally forbidden | Does not block prototype construction. |
| Define maintenance and abort window | Operations owner | Live rehearsal/cutover | No live execution envelope | Does not block prototype construction. |
| Author live migration and cutover authorization | Governance owner | External-effect stage | Product approval and exact bindings absent | No live work may begin. |

## Next decision frontier

After L4 evidence is frozen, the candidate can be reviewed for product
approval. That review cannot itself admit the adapter or authorize a live
target. Adapter admission remains a later distinct decision, and any service
adapter, credential binding, live rehearsal, governed runtime activation,
migration, operational cutover, publication, or deployment requires its own
exact construction and authority route.
