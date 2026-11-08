# Saga Proof Obligations

Status: draft obligation catalog
Date: 2026-06-15
Dispatch: `domainspec-v2-dcb-saga-correctness-research-20260615`

## Obligation Classes

### Graph Completeness

The saga model must expose:

- participants or bounded contexts;
- forward operations and owning participants;
- compensation operations or terminal failure policies;
- cross-context activation edges;
- cross-context write/projection edges;
- cross-context rule constraints;
- interface and mapping boundaries.

Relevant DomainSpec edges:

- `triggers-cross`
- `produces-for`
- `enforces-cross`
- `produces`
- `transitions`
- `applies`
- `exposes`
- `maps`

Strained edge:

- `orchestrates` is currently typed as `Workflow -> Operation[]`; the pilot must
  either treat Saga as a Workflow specialization or record this as relationship
  signature residue.

### Temporal Execution

The saga model must check:

- success safety: the saga cannot accept success unless required participant
  success states hold;
- failure safety: a failed later step causes completed compensatable steps to
  compensate, reach terminal failure, or escalate under policy;
- compensation ordering: compensation runs in a declared order;
- retry/dead-letter behavior: retries and terminal failure are policy-governed;
- state transition validity: events only produce declared participant or saga
  transitions.

### DCB Claim Freshness

The DCB layer must check:

- the correctness claim records the facts it read;
- deterministic facts are rerun or content-hashed before acceptance;
- non-rerunnable facts are represented as read-set facts;
- the claim is rejected if a matching fact changed after the read marker;
- the claim is rejected or re-opened if a concurrent acceptance race changes a
  fact in the read set.

## Fact Classification

| Fact | Default mechanism |
| --- | --- |
| `SagaDeclared` | content hash / rerun |
| `SagaStepDeclared` | content hash / rerun |
| `ParticipantDeclared` | content hash / rerun |
| `ForwardOperationDeclared` | content hash / rerun |
| `CompensationOperationDeclared` | content hash / rerun |
| `CrossContextEdgeDeclared` | content hash / rerun |
| `RuleGuardObserved` | content hash / rerun |
| `PolicyObserved` | content hash / rerun |
| `ParticipantStateMachineObserved` | content hash / rerun |
| `BoundaryMappingObserved` | content hash / rerun |
| `ModelCheckRunRecorded` | version-bound receipt plus DCB if non-rerunnable |
| `PropertyTestRunRecorded` | rerun if cheap, receipt if expensive |
| `ProofVerdictIssued` | receipt plus DCB |
| `HumanWaiverApplied` | DCB |
| `ExternalEvidenceReceiptRecorded` | DCB |
| `SagaCorrectnessClaimProposed` | DCB |
| `SagaCorrectnessClaimAccepted` | DCB append condition |
| `SagaCorrectnessClaimRejected` | DCB audit event |

## First Toy Acceptance Criteria

The toy passes only if it shows:

- one graph completeness check;
- one bounded behavioral check;
- one non-rerunnable or concurrent fact in the read set;
- one stale claim rejected by freshness checking;
- clear evidence that deterministic facts were handled by rerun/hash rather
  than wrapped in DCB unnecessarily.

