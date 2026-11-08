# SWU-FMT-005 Context Pack

## Scope

- Task session target: `SWU-FMT-005`
- Parent task: `TASK-FMT-003`
- Objective: parse and model-check the TLA+ example with safety properties, or capture exact parse/check errors.
- Execution mode: local fallback through tracked wrappers.

## Controlling Sources

- `../WORK-PACK.md`
- `../work-pack/tasks/TASK-FMT-003-example-validation.md`
- `../../examples/OrderFulfillmentSaga.tla`
- `../../examples/README.md`
- `../../NOTATION-BRIDGE.md`
- `../../CLAIM-LEDGER.md`
- `../../tooling/README.md`

## Write Scope

- Allowed:
  - `examples/OrderFulfillmentSaga.cfg`
  - `invoke-plan/run-results/tla/`
  - `invoke-plan/session-evidence/`
  - work-pack status sync files
- Not allowed:
  - repairing `examples/OrderFulfillmentSaga.tla`
  - changing DomainSpec canonical definitions
  - hiding parse/check failures

## Gates

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Dependency `SWU-FMT-003` | pass | wrapper validation receipt |
| TLA parse path | pass | SANY wrapper available |
| TLA safety config | pass | added `OrderFulfillmentSaga.cfg` for declared invariants |
| Failure policy | pass | exact TLC violation is acceptable evidence for this SWU |

## Decisions

- Add a minimal TLC `.cfg` next to the example because the task requested safety checks for `Spec`, `SuccessSafety`, `FailureSafety`, and `FreshnessSafety`.
- Do not repair the TLA model in this SWU.
- Treat the TLC counterexample as validation evidence and model-repair residue.

## Completion Criteria

- SANY passes or exact parse error is captured.
- TLC passes or exact check error/counterexample is captured.
- Receipt records command, version, config, and result.
