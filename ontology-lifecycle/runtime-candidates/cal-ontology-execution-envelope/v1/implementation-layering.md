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
- Current state: partially implemented isolated Rust prototype.
- Primary operator: the future governed ontology execution runtime.
- Primary constraint: no live target, credential, external effect, or authority expansion.
- Boundary rule: each layer ends at the smallest tested slice that unlocks the next decision.
- Value/cost rule: prefer a decision or risk reduction over integration breadth and operational coordination.

## Layer decisions

| Layer | Decision question | Minimum working unit | Included scope | Explicitly deferred | Exit evidence | Promotion decision |
| --- | --- | --- | --- | --- | --- | --- |
| L0 | After this layer, we know whether the exact D65 sequence can execute and roll back deterministically. | Concrete in-memory Rust engine. | Ten ordered steps, exact cuts, live refusal, rollback. | Adapter reuse and operational bindings. | Eight public tests run twice. | Completed: continue to L1. |
| L1 | After this layer, we know whether the engine can use a public adapter contract without weakening fail-closed behavior. | Generic engine plus external conforming wrapper. | Adapter trait, binding preflight, emergency rollback for every post-preimage failure. | Filesystem, services, credentials, live targets. | Public and adapter suites run twice; format and Clippy pass. | Continue only if all L0 guarantees remain true. |
| L2 | After this layer, we know whether independently authored disposable adapters can be certified repeatably. | Adapter certification harness and richer fault matrix. | Contract vectors, transition call-order evidence, deterministic certification receipt. | Production topology and operator workflow. | Independent adapter fixture passes all vectors. | Package or remediate the adapter contract. |
| L3 | After this layer, we know whether one reviewed non-live target adapter can rehearse against a disposable system boundary. | Exact disposable integration adapter. | Owner-selected target kind, non-secret configuration, rehearsal-only pre/postimages. | Live activation, real credentials, migration, cutover, deployment. | Isolated rehearsal and independent validation. | Hold a separate product and authority decision. |

## Capability progression

| Capability | L0 | L1 | L2 | L3 |
| --- | --- | --- | --- | --- |
| Target boundary | Concrete type | Public trait plus exact binding | Certifiable adapter vectors | Reviewed disposable integration |
| Failure handling | Mid-sequence restore | Restore after every post-preimage failure | Fault matrix | Boundary-specific abort rehearsal |
| Evidence | Engine tests | Engine plus external-adapter tests | Certification receipt | Independent rehearsal receipt |
| Effects | None | None | None | Disposable and non-live only |

## Current product frontier

- Recommended layer: L1, implemented by `PROTOTYPE-002`.
- Runnable product work: compile, run both suites twice, lint, and freeze exact input digests.
- User-visible outcome: the engine is no longer coupled to `InMemoryTarget`.
- Risk reduced: adapter substitution cannot bypass the exact prototype binding, and rollback-step failure cannot strand mutated prototype state.
- Main cost drivers: public trait stability and fault-path verification.
- Non-regression: exact event cuts, ten-step ordering, deterministic receipt, live refusal before mutation, no credentials, no external effects, and exact rollback remain mandatory.

## Operational lane and deferred residue

| Operational task | Owner | Affected future stage | Current blocker | Product-lane effect |
| --- | --- | --- | --- | --- |
| Select a real disposable target kind | CyberAlchemy v2 product owner | L3 | No owner-selected target | Does not block L1 or L2. |
| Supply credential handling | Security and target owner | Post-product authority stage | Credentials intentionally forbidden | Does not block prototype construction. |
| Define maintenance and abort window | Operations owner | Live rehearsal/cutover | No live execution envelope | Does not block prototype construction. |
| Author live migration and cutover authorization | Governance owner | External-effect stage | Product approval and exact bindings absent | No live work may begin. |

## Recommended next layer

L2 should add contract vectors and an independently authored disposable adapter fixture. The most important deferred scope is every real-system or live-effect adapter; it remains outside this product candidate.
