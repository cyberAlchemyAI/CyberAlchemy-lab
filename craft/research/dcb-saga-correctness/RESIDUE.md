# DCB Saga Correctness Residue

Status: open residue
Date: 2026-06-15
Dispatch: `domainspec-v2-dcb-saga-correctness-research-20260615`

## R1: Saga `orchestrates` Signature

Current state:

- `orchestrates` is typed as `Workflow -> Operation[]`.
- Saga needs to name coordinated operations.

Options:

- Treat Saga as a Workflow specialization for the toy.
- Propose a later relationship signature extension.
- Avoid `orchestrates` in the toy and use a saga step table.

Owner: DomainSpec definitions owner.

## R2: Compensation Semantics

Current state:

- Saga requires explicit compensation and rollback semantics.
- The edge vocabulary lacks a compensation relation.

Options:

- Represent compensation as a role on `Operation` inside the saga step table.
- Add a later relationship extension such as `compensates-for`.
- Keep compensation entirely in the toy proof model until promoted.

Owner: DomainSpec v2 research.

## R3: Participant Representation

Current state:

- Participants/bounded contexts are required for saga proof obligations.
- Participant is not a canonical meta-concept.

Options:

- Use feature namespace as participant id.
- Use `Interface` boundary as participant id.
- Use entity ownership as participant id.

Owner: DomainSpec v2 research.

## R4: DCB Evidence Vocabulary

Current state:

- Proof verdicts, waivers, external receipts, read markers, and claim acceptance
  are not DomainSpec taxonomy concepts.

Decision:

- Keep them in a DCB evidence vocabulary for now.

Owner: DCB correctness research.

## R5: Read Marker Granularity

Current state:

- Content rollup hash is accepted as the broad marker direction.
- Coarse rollup versus per-dependency hashes remains open.

Recommendation:

- Use per-dependency hashes in the toy to preserve DCB explainability.

Owner: next task-session.

