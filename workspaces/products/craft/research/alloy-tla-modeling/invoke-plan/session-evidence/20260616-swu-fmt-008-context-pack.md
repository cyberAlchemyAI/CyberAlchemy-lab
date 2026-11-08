# SWU-FMT-008 Context Pack

## Scope

- Task session target: `SWU-FMT-008`
- Parent task: `TASK-FMT-VERIFY`
- Objective: verify execution artifacts and sync tower status.
- Execution mode: local closeout.

## Controlling Sources

- `../WORK-PACK.md`
- `../work-pack/tasks/TASK-FMT-VERIFY-readiness.md`
- `../../gates/closure-gates.md`
- `../../LEARNING-PACK.md`
- `../PLAN-TRANSPORT.md`
- `../../README.md`
- all SWU receipts under `../run-results/`

## Write Scope

- Allowed:
  - `../../gates/closure-gates.md`
  - `../../LEARNING-PACK.md`
  - `../PLAN-TRANSPORT.md`
  - `../../README.md`
  - `invoke-plan/run-results/`
  - work-pack status sync files
- Not allowed:
  - promoting to canonical validator readiness
  - changing taxonomy or relationships
  - repairing TLA freshness semantics
  - changing generated tool binaries

## Gates

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Dependencies `SWU-FMT-001..007` | pass | work-pack rows and receipts |
| Tool binary tracking | pass path | scoped git status must show no `.formal-tools/` |
| Markdown links | pass path | tower README plus generated tower markdown checks |
| Promotion honesty | pass | status must preserve TLA counterexample residue |

## Decisions

- Mark executable surface ready for research use, not canonical proof/validator readiness.
- Promote Alloy example from unvalidated to bounded-pass-with-syntax-repair.
- Promote TLA example from unvalidated to counterexample-captured.
- Keep next work as repair/generator integration, not proof claim.

## Completion Criteria

- Tower gates accurately reflect actual tool/model validation results.
- Markdown links pass for the tower.
- Scoped git status shows no tracked binaries.
- Receipt inventory exists.
