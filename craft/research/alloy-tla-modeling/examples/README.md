# Examples

Status: unvalidated sketches

These examples are intentionally small and tool-specific. They are here to make the next validation task concrete, not to claim proof.

## Files

| File | Purpose | Validation status |
| --- | --- | --- |
| `OrderFulfillmentSaga.alloy` | Sketch a bounded graph-completeness check for participants, operations, compensation links, and policy fallback. | not run |
| `OrderFulfillmentSaga.tla` | Sketch a TLA+ state-machine check for saga safety and stale-freshness rejection. | not run |

## Required Next Evidence

For Alloy:

- Alloy version.
- Exact command or Analyzer steps.
- Scope used by each `run` or `check`.
- Counterexample or no-counterexample result.

For TLA+:

- Java version and TLA+ tools version.
- SANY parse result.
- TLC command/model config.
- Checked invariants and result.
