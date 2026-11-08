# TASK-FMT-004: Formal Fixture Contract

Layer: L2
Status: completed

## Objective

Define the data contract that lets the TypeScript saga witness feed Alloy and TLA+ without manual drift.

## Source Contracts

- `../../../../dcb-saga-correctness/toy-harness/saga-spec.ts`
- `../../../../dcb-saga-correctness/toy-harness/order-fulfillment.fixture.ts`
- `../../../../dcb-saga-correctness/toy-run-result.json`
- `../../../DEFINITIONS.md`

## Implementation Detail

Start with schema/design, not generator code.

Candidate tracked files:

```text
projects/domainspec-v2/research/alloy-tla-modeling/fixtures/formal-saga-fixture.schema.json
projects/domainspec-v2/research/alloy-tla-modeling/fixtures/order-fulfillment.formal-fixture.json
projects/domainspec-v2/research/alloy-tla-modeling/fixtures/README.md
```

Contract must represent:

- participants and owning contexts;
- forward operations;
- compensation operations;
- policies and terminal failure states;
- typed relationship edges;
- deterministic facts with hash/rerun mechanism;
- non-rerunnable DCB facts and external receipts;
- model result receipt fields.

## Smallest Working Units

### SWU-FMT-007

- Goal: Author the first formal fixture schema and example fixture.
- Dependencies: SWU-FMT-005 and SWU-FMT-006.
- Write scope: `fixtures/`.
- Done criteria: fixture maps to both existing examples and preserves fact classification.
- Acceptance evidence: schema, example fixture, and traceability notes.
- Validation surface: `python3 -m json.tool` for JSON files plus review against examples.
- Execution owner: subagent.
- Handoff note: Do not generate code until the schema shape is reviewable.
- Status: completed 2026-06-16.
- Evidence:
  - `../../../fixtures/formal-saga-fixture.schema.json`
  - `../../../fixtures/order-fulfillment.formal-fixture.json`
  - `../../../fixtures/README.md`
  - `../../run-results/fixtures/swu-fmt-007-fixture-validation.md`
- Validation result: pass. JSON files parse, fixture README links resolve, and the fixture preserves deterministic hash facts separately from non-rerunnable DCB facts.
