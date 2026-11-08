# Handoff: DCB Saga Correctness Toy

Status: ready for next task-session
Date: 2026-06-15
Dispatch: `domainspec-v2-dcb-saga-correctness-research-20260615`

## Objective

Implement a small TypeScript bounded witness for saga behavior and a DCB-style
freshness check for accepting that witness as current evidence.

## Starting Context

Read:

- `projects/domainspec-v2/research/dcb-saga-correctness/TAXONOMY-EDGE-FRAME.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/LANE-RECEIPTS.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/MODEL-CHOICE.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/PROOF-OBLIGATIONS.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/TOY-SAGA-SCENARIO.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/TOY-RUN-PLAN.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/SYNTHESIS.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/RESIDUE.md`

## Decision State

Decision: `borrow-carefully`.

Use TypeScript first, but call the result a bounded witness, not a proof.

Use DCB only at the acceptance boundary:

```text
AcceptSagaProofFreshnessClaim
```

Do not use:

```text
AcceptSagaCorrectnessClaim
```

## Recommended Next Command

```text
Run a task-session to build the toy TypeScript bounded witness under projects/domainspec-v2/research/dcb-saga-correctness/toy-harness. Model OrderFulfillmentSaga with participants, forward operations, compensation operations, policies, state transitions, DomainSpec edge triples, and one non-rerunnable human waiver or external receipt. Produce toy-run-result.md and toy-run-result.json showing one bounded behavioral witness and one rejected stale AcceptSagaProofFreshnessClaim. Do not mutate DomainSpec taxonomy, relationships, templates, validators, or generated registries.
```

## Acceptance Criteria

- The toy includes `OrderFulfillmentSaga`.
- The harness checks graph completeness and at least one bounded behavioral
  obligation.
- The toy includes one non-rerunnable fact or concurrent acceptance race.
- Deterministic facts use hash/rerun semantics.
- `AcceptSagaProofFreshnessClaim` rejects one stale claim.
- The result does not claim DCB proves saga behavior directly.

## Stop Conditions

- If all facts are deterministic, downgrade to content hash and rerun-before-use.
- If the toy needs taxonomy or relationship mutation, stop and write a decision
  gate instead.
- If TypeScript cannot express the behavior cleanly, promote to TLA+/PlusCal or
  Alloy depending on the failure mode.

