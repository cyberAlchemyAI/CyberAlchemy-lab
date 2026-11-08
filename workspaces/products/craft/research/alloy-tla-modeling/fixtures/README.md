# Formal Fixture Contract

Status: first reviewable contract, no generator yet.

## Files

- `formal-saga-fixture.schema.json`: JSON Schema for a saga fixture that can feed Alloy and TLA+ generation later.
- `order-fulfillment.formal-fixture.json`: fixture instance derived from the TypeScript bounded witness and the current Alloy/TLA examples.

## Mapping

The fixture keeps the TypeScript `SagaSpec` shape recognizable:

- `participants` maps to bounded contexts and Alloy participant atoms.
- `operations` splits forward and compensation operations so Alloy can check graph completeness and TLA+ can construct next-state actions.
- `policies` carries terminal failure and compensation-order policy references.
- `edges` preserves DomainSpec relationship names and the `orchestrates` residue.
- `facts` preserves the read-set distinction between deterministic hash facts and non-rerunnable DCB facts.
- `trace` carries the bounded witness events that a later generator can translate into TLA+ scenario constraints.
- `modelExpectations` records bounded expectations and known residue from the current tool runs.

## Fact Classification

Deterministic facts use `mechanism: "hash"` and can be checked by stable content markers. DCB facts use `mechanism: "dcb"` and are classified as `non-rerunnable`; they participate in freshness acceptance but do not prove saga behavior.

## Current Residue

- TLA+ `FreshnessSafety` currently has a counterexample after acceptance followed by a waiver change.
- `orchestrates` remains relationship residue because the taxonomy relationship currently types it as `Workflow -> Operation[]`, while this fixture keeps the saga-level edge visible.

## Validation

```bash
python3 -m json.tool projects/domainspec-v2/research/alloy-tla-modeling/fixtures/formal-saga-fixture.schema.json
python3 -m json.tool projects/domainspec-v2/research/alloy-tla-modeling/fixtures/order-fulfillment.formal-fixture.json
```
