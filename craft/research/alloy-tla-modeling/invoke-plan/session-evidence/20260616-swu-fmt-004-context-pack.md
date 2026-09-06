# SWU-FMT-004 Context Pack

## Scope

- Task session target: `SWU-FMT-004`
- Parent task: `TASK-FMT-002`
- Objective: document cache, binary, wrapper, and receipt policy for the formal-tooling surface.
- Execution mode: local documentation.

## Controlling Sources

- `../WORK-PACK.md`
- `../work-pack/tasks/TASK-FMT-002-wrapper-surface.md`
- `../run-results/toolchain/toolchain-receipt.md`
- `../run-results/toolchain/swu-fmt-003-wrapper-validation.md`

## Write Scope

- Allowed:
  - `projects/domainspec-v2/research/alloy-tla-modeling/tooling/README.md`
  - `invoke-plan/run-results/`
  - `invoke-plan/session-evidence/`
  - work-pack status sync files
- Not allowed:
  - tool downloads or `.formal-tools/` mutation
  - example model repair
  - canonical DomainSpec definitions

## Gates

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Dependency `SWU-FMT-003` | pass | wrapper validation receipt |
| Write scope | pass | documentation and receipt-only update |
| Binary safety | pass | README must state `.formal-tools/` is ignored and never tracked |
| Validation | pass path | single-file markdown link check |

## Decisions

- Keep the policy in the tooling directory so future users find it next to the scripts.
- Reference receipts with relative links and keep generated outputs under `invoke-plan/run-results/`.
- Avoid tracked `.gitignore` churn because `.git/info/exclude` already protects the local cache for this checkout.

## Completion Criteria

- README says what is tracked, ignored, downloaded, and recorded.
- Markdown link check passes for `tooling/README.md`.
