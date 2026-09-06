# SWU-FMT-007 Context Pack

## Scope

- Task session target: `SWU-FMT-007`
- Parent task: `TASK-FMT-004`
- Objective: author the first formal fixture schema and example fixture.
- Execution mode: local schema/design.

## Controlling Sources

- `../WORK-PACK.md`
- `../work-pack/tasks/TASK-FMT-004-fixture-contract.md`
- `../../../../dcb-saga-correctness/toy-harness/saga-spec.ts`
- `../../../../dcb-saga-correctness/toy-harness/order-fulfillment.fixture.ts`
- `../../../../dcb-saga-correctness/toy-run-result.json`
- `../../DEFINITIONS.md`
- `../run-results/tla/order-fulfillment-summary.md`
- `../run-results/alloy/order-fulfillment-summary.md`

## Write Scope

- Allowed:
  - `fixtures/`
  - `invoke-plan/session-evidence/`
  - work-pack status sync files
- Not allowed:
  - generator implementation
  - toy harness mutation
  - model repair
  - canonical DomainSpec definitions

## Gates

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Dependency `SWU-FMT-005` | pass-with-residue | TLA summary captures freshness counterexample |
| Dependency `SWU-FMT-006` | pass | Alloy summary captures bounded run/check output |
| Write scope | pass | fixture files only |
| Validation | pass path | `python3 -m json.tool` for JSON files |

## Decisions

- Use JSON Schema as the first contract so TypeScript can emit fixtures later without generator code in this SWU.
- Preserve fact mechanisms as `hash`, `rerun`, and `dcb`.
- Represent DCB facts as non-rerunnable freshness inputs, not behavioral proof.
- Include model expectations and known residues so formal outputs stay bounded and honest.

## Completion Criteria

- Schema, example fixture, and traceability notes exist.
- JSON files parse.
- Fixture maps to both existing examples and preserves fact classification.
