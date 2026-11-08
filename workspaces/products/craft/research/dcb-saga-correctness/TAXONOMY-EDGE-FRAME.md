# Taxonomy And Edge Frame For DCB Saga Correctness

Status: dispatch frame
Date: 2026-06-15
Dispatch: `domainspec-v2-dcb-saga-correctness-research-20260615`

## Purpose

This frame gives the subagent lanes a common DomainSpec vocabulary for asking
whether DCB can help with saga correctness. It separates three layers:

- DomainSpec vocabulary: the concepts and typed edges a saga must expose.
- Proof surface: the model, harness, or checker that evaluates saga behavior.
- DCB boundary: the freshness or concurrency guard around accepting proof
  evidence and waivers.

## Central Split

DCB is not the behavioral proof engine by itself.

For this research route:

- The proof engine proves or falsifies saga obligations.
- DCB decides whether a proof/evidence/waiver claim can still be accepted after
  the facts it depended on may have changed.

If a lane claims "DCB proves saga correctness" without a separate proof surface,
that lane should be marked `block` or `analogy-only`.

## DomainSpec Meta-Concepts In Scope

| Meta-concept | Saga correctness role |
| --- | --- |
| `Saga` | The cross-feature orchestration being checked. |
| `Workflow` | Same-feature orchestration baseline; useful contrast to `Saga`. |
| `Operation` | Forward and compensation steps. |
| `Rule` | Guards, preconditions, and cross-context execution constraints. |
| `Policy` | Retry, timeout, dead-letter, routing, and compensation-selection behavior. |
| `Event` | Cross-context announcements that activate operations or advance state. |
| `State Machine` | Participant lifecycles and the saga lifecycle. |
| `Entity` | State owners affected by forward and compensation operations. |
| `Interface` | Callable participant boundary. |
| `Mapping` | Data shape transform across participant/API/event boundaries. |

## Relationship Edges In Scope

| Edge | Saga correctness obligation |
| --- | --- |
| `orchestrates` | The saga names the operations it coordinates. |
| `triggers-cross` | Cross-context events activate the correct participant operations. |
| `produces-for` | Operations that write/project into foreign-owned state are explicit. |
| `enforces-cross` | Cross-context execution guards are first-class, not hidden prose. |
| `produces` | Forward and compensation operations emit expected events. |
| `transitions` | Events advance participant or saga state machines as expected. |
| `applies` | Retry/dead-letter/compensation policies are connected to operations. |
| `exposes` | Participant interfaces expose the operations or queries the saga calls. |
| `maps` | Boundary inputs, outputs, events, and DTOs have documented transforms. |

## Minimum Saga Proof Obligations

1. Participant boundary completeness: every participant feature/bounded context
   is named, and each cross-context call or event has an edge.
2. Forward-step completeness: every saga step maps to a DomainSpec `Operation`
   and an owning participant.
3. Compensation completeness: every completed forward operation is paired with a
   compensation operation or an explicit terminal failure policy.
4. Guard completeness: each operation guard is a `Rule`; cross-context guards use
   `enforces-cross`.
5. Policy completeness: retry, timeout, dead-letter, and compensation-ordering
   choices are represented as `Policy` edges via `applies`.
6. Event/state completeness: events produced by operations are connected to
   participant or saga state transitions through `produces` and `transitions`.
7. Boundary data completeness: interfaces and mappings are sufficient to explain
   the data moved across each participant boundary.
8. Success safety: an accepted saga success state requires all required
   participant success states or accepted alternatives.
9. Failure safety: if a later participant fails, already-completed compensatable
   steps are compensated, explicitly terminal, or escalated by policy.
10. Claim freshness: accepted saga-correctness evidence is rejected if any read
    saga step, rule, policy, edge, model result, waiver, or external receipt has
    changed after its read marker.

## DCB Fact Vocabulary Candidate

These facts are candidates for a DCB-style read set:

- `SagaDeclared`
- `SagaStepDeclared`
- `ParticipantDeclared`
- `ForwardOperationDeclared`
- `CompensationOperationDeclared`
- `CrossContextEdgeDeclared`
- `RuleGuardObserved`
- `PolicyObserved`
- `ParticipantStateMachineObserved`
- `BoundaryMappingObserved`
- `ModelCheckRunRecorded`
- `PropertyTestRunRecorded`
- `ProofVerdictIssued`
- `HumanWaiverApplied`
- `ExternalEvidenceReceiptRecorded`
- `SagaCorrectnessClaimProposed`
- `SagaCorrectnessClaimAccepted`
- `SagaCorrectnessClaimRejected`

The alternatives lane should challenge whether each fact needs DCB or can be
handled by deterministic rerun, content hash, snapshot diff, or certificate
binding.

## Toy Saga Candidate

Use an `OrderFulfillmentSaga` unless a lane finds a better minimal example.

Participants:

- ordering
- payment
- inventory
- shipping

Forward operations:

- `CreateOrder`
- `AuthorizePayment`
- `ReserveInventory`
- `CreateShipment`

Compensation operations:

- `CancelOrder`
- `VoidPayment`
- `ReleaseInventory`
- `CancelShipment`

Candidate non-rerunnable evidence:

- a human waiver allowing shipment creation after a timeout;
- an agent/model verdict that a compensation policy is acceptable;
- an external payment-provider authorization receipt.

## Language Question

The language tournament should compare:

- TypeScript DSL plus property/bounded tests: best repository fit and easiest
  extraction path, but not a full proof by itself.
- TLA+ or PlusCal: strongest fit for temporal saga behavior, crashes, retries,
  compensation, and liveness/safety invariants.
- Alloy: strongest fit for relationship graph completeness and counterexamples
  over typed edges.
- Lean: strongest theorem-checking story, but likely too expensive for this
  first feasibility pass unless the theorem is deliberately tiny.

Recommended starting bias:

- TypeScript for the extraction and toy harness.
- TLA+ for temporal behavior if the toy targets saga execution.
- Alloy for graph completeness if the toy targets DomainSpec relationship
  coverage.

