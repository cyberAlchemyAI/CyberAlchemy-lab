# TASK-FMT-003: Example Validation

Layer: L1
Status: completed-with-residue

## Objective

Validate the existing Alloy and TLA+ sketches or capture exact repair residue.

## Source Contracts

- `../../../examples/OrderFulfillmentSaga.tla`
- `../../../examples/OrderFulfillmentSaga.alloy`
- `../../../NOTATION-BRIDGE.md`
- `../../../CLAIM-LEDGER.md`

## Implementation Detail

TLA+ validation should start with parsing and safety checks:

```bash
java -cp .formal-tools/tla/tla2tools-1.7.4.jar tla2sany.SANY \
  projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.tla
```

If TLC requires a `.cfg`, add one next to the example. The first config should check `Spec`, `SuccessSafety`, `FailureSafety`, and `FreshnessSafety`. Defer liveness/fairness until safety is stable.

Alloy validation should use the Alloy CLI if available from the jar. If the CLI cannot run the sketch directly, capture the exact limitation and route to model/CLI repair.

## Smallest Working Units

### SWU-FMT-005

- Goal: Parse and model-check the TLA+ example with safety properties.
- Dependencies: SWU-FMT-003.
- Write scope: `examples/OrderFulfillmentSaga.cfg` if needed; `invoke-plan/run-results/tla/`.
- Done criteria: SANY/TLC pass or exact parse/check errors are captured.
- Acceptance evidence: TLA receipt with command, version, config, result.
- Validation surface: SANY and TLC commands.
- Execution owner: local-fallback.
- Handoff note: A failure receipt is acceptable; do not silently edit the model until the failure is captured.
- Status: completed-with-counterexample 2026-06-16.
- Evidence:
  - `../../../examples/OrderFulfillmentSaga.cfg`
  - `../../run-results/tla/order-fulfillment-sany.md`
  - `../../run-results/tla/order-fulfillment-tlc-safety.md`
  - `../../run-results/tla/order-fulfillment-summary.md`
- Validation result: pass for task acceptance, counterexample for model claim. SANY parsed successfully; TLC found a `FreshnessSafety` violation after acceptance followed by `WaiverChangesAfterRead`.

### SWU-FMT-006

- Goal: Run Alloy validation for the graph-completeness example.
- Dependencies: SWU-FMT-003.
- Write scope: `examples/OrderFulfillmentSaga.alloy` only if syntax repair is necessary; `invoke-plan/run-results/alloy/`.
- Done criteria: Alloy check produces result or exact CLI/model error receipt.
- Acceptance evidence: Alloy receipt with command, version, scope, result.
- Validation surface: Alloy CLI command with explicit scope.
- Execution owner: local-fallback.
- Handoff note: Preserve the `orchestrates` residue; do not "fix" it by changing canonical relationships.
- Status: completed 2026-06-16.
- Evidence:
  - `../../../examples/OrderFulfillmentSaga.alloy`
  - `../../run-results/alloy/order-fulfillment-commands.md`
  - `../../run-results/alloy/order-fulfillment-exec.md`
  - `../../run-results/alloy/order-fulfillment-output/receipt.json`
  - `../../run-results/alloy/order-fulfillment-summary.md`
- Validation result: pass after syntax repair. Alloy CLI listed commands and executed all declared commands within scope 8. `showCompleteSaga` was SAT; `findMissingCompensation` and the completeness check found no witness/counterexample for the current complete graph.
