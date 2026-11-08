# SWU-FMT-006 Context Pack

## Scope

- Task session target: `SWU-FMT-006`
- Parent task: `TASK-FMT-003`
- Objective: run Alloy validation for the graph-completeness example, or capture exact CLI/model error residue.
- Execution mode: local fallback through tracked wrappers.

## Controlling Sources

- `../WORK-PACK.md`
- `../work-pack/tasks/TASK-FMT-003-example-validation.md`
- `../../examples/OrderFulfillmentSaga.alloy`
- `../../examples/README.md`
- `../../CLAIM-LEDGER.md`
- `../../tooling/README.md`
- `../run-results/toolchain/toolchain-receipt.md`

## Write Scope

- Allowed:
  - `examples/OrderFulfillmentSaga.alloy` only for necessary syntax repair
  - `invoke-plan/run-results/alloy/`
  - `invoke-plan/session-evidence/`
  - work-pack status sync files
- Not allowed:
  - changing canonical relationships
  - hiding `orchestrates` residue
  - widening the model beyond the existing bounded sketch

## Gates

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Dependency `SWU-FMT-003` | pass | wrapper validation receipt |
| Alloy CLI available | pass | Alloy version/help from wrapper validation |
| Syntax repair scope | pass | one-word field rename from reserved `steps` to `forwardSteps` |
| Generated output location | pass | Alloy `--output` directed under `invoke-plan/run-results/alloy/` |

## Decisions

- Repair only the Alloy 6 reserved-word collision (`steps`) needed for parsing.
- Run all declared commands with `exec -c '*'` and JSON output under run-results.
- Preserve graph-completeness semantics and relationship residue; do not mutate DomainSpec definitions.

## Completion Criteria

- Alloy command listing passes or exact syntax error is captured.
- Alloy execution produces result or exact CLI/model error receipt.
- Receipt records command, version/scope, and result.
