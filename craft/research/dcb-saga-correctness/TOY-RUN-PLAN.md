# Toy Run Plan

Status: ready for task-session
Date: 2026-06-15
Dispatch: `domainspec-v2-dcb-saga-correctness-research-20260615`

## Objective

Create a small TypeScript bounded witness for `OrderFulfillmentSaga` and a DCB
freshness check for accepting the witness as current evidence.

## Proposed Files

Suggested write scope for the next task-session:

```text
projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/
projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/saga-spec.ts
projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/order-fulfillment.fixture.ts
projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/run-toy.ts
projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.md
projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.json
```

## Harness Shape

```text
SagaSpec
  -> validateGraph(spec)
  -> enumerateRuns(spec, { maxFailures: 1, maxCompensationFailures: 1 })
  -> assertBehavioralObligations(runs)
  -> buildReadSet(spec, runResult, nonRerunnableFacts)
  -> acceptSagaProofFreshnessClaim(readSet, currentFacts)
```

## Minimal Types

```ts
type SagaSpec = {
  id: string;
  participants: Participant[];
  steps: SagaStep[];
  edges: DomainSpecEdge[];
  policies: PolicyRef[];
  stateMachines: StateMachineRef[];
};

type SagaStep = {
  id: string;
  participant: string;
  forwardOperation: string;
  compensationOperation?: string;
  terminalFailurePolicy?: string;
};
```

## Checks

Graph checks:

- every step has a participant;
- every forward operation has a compensation operation or terminal failure policy;
- cross-context edges use existing relationship names;
- `orchestrates` is treated as residue unless Saga-as-Workflow specialization
  is explicitly declared.

Behavioral checks:

- success cannot be accepted after failed shipment;
- completed compensatable steps are compensated after failed shipment;
- missing compensation produces a failing witness.

Freshness checks:

- deterministic facts use per-dependency hashes;
- non-rerunnable facts use receipt ids and read markers;
- stale waiver or external receipt rejects `AcceptSagaProofFreshnessClaim`.

## Expected Output

`toy-run-result.json` should include:

```json
{
  "scenario": "OrderFulfillmentSaga",
  "behavioral_witness": "pass",
  "graph_witness": "flag",
  "graph_residue": ["orchestrates signature for Saga"],
  "freshness_claim": "rejected",
  "stale_fact": "HumanWaiverApplied:waiver:ship-after-payment-timeout-v1",
  "recommendation": "borrow-carefully"
}
```

## Stop Conditions

- Stop if the toy has no non-rerunnable evidence; downgrade to rerun/hash.
- Stop if the implementation needs taxonomy or relationship mutation.
- Stop if the output claims TypeScript proves saga correctness rather than
  producing a bounded witness.

