# L2 Closure Plan

Status: pass

## Closure Goal

Move from research-tower feasibility to tool-validated evidence without mutating DomainSpec canonical definitions.

## Step 1: Alloy Validation Slice

Objective:

Validate whether `examples/OrderFulfillmentSaga.alloy` can express the graph-completeness obligations and produce a useful counterexample when compensation is missing.

Inputs:

- `examples/OrderFulfillmentSaga.alloy`
- `arcanum/definitions/TAXONOMY.md`
- `arcanum/definitions/RELATIONSHIPS.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.md`

Validation:

- Alloy Analyzer or CLI accepts the file.
- A `check` command is run with explicit scope.
- Result records either a counterexample or no counterexample in scope.
- Output records tool version and command.

## Step 2: TLA+ Validation Slice

Objective:

Validate whether `examples/OrderFulfillmentSaga.tla` can model the bounded saga trace and check safety/freshness properties with TLC.

Inputs:

- `examples/OrderFulfillmentSaga.tla`
- existing TypeScript toy witness
- proof obligations from `dcb-saga-correctness/PROOF-OBLIGATIONS.md`

Validation:

- SANY parses the module.
- TLC runs a finite model.
- Safety properties are checked.
- Freshness rejection is represented as a separate acceptance condition.
- Output records Java/TLA tools version and command.

## Step 3: Fixture Contract Slice

Objective:

Define the JSON contract that the TypeScript `SagaSpec` harness should emit for both Alloy and TLA generation.

Validation:

- One fixture file can generate or manually align to both examples.
- The fixture distinguishes deterministic facts from non-rerunnable DCB facts.
- The fixture preserves `orchestrates` residue instead of mutating `RELATIONSHIPS.md`.

## Stop Conditions

- Stop if a tool requires large installation or licensing steps not appropriate for this repo.
- Stop if the first model requires changing canonical DomainSpec definitions; reroute to definitions governance.
- Stop if a model can only pass by deleting the residue that the TypeScript witness surfaced.
