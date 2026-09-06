# SWU-FMT-003 Context Pack

## Scope

- Task session target: `SWU-FMT-003`
- Parent task: `TASK-FMT-002`
- Objective: add tracked wrapper scripts and an environment example for repeatable local formal-tool invocation.
- Execution mode: local implementation.

## Controlling Sources

- `../WORK-PACK.md`
- `../work-pack/tasks/TASK-FMT-002-wrapper-surface.md`
- `../work-pack/waves/W1-wrapper-surface.md`
- `../../examples/README.md`
- `../run-results/toolchain/swu-fmt-001-smoke-clean.md`
- `../run-results/toolchain/toolchain-receipt.md`

## Write Scope

- Allowed:
  - `projects/domainspec-v2/research/alloy-tla-modeling/tooling/`
  - `invoke-plan/session-evidence/`
  - `WORK-PACK.md`
  - `work-pack/tasks/TASK-FMT-002-wrapper-surface.md`
- Not allowed:
  - `.formal-tools/` content changes beyond optional local runtime use
  - canonical DomainSpec definitions
  - example model repairs

## Gates

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Dependency `SWU-FMT-001` | pass | `swu-fmt-001-smoke-clean.md` |
| Dependency `SWU-FMT-002` | pass | `toolchain-receipt.md` |
| Write scope | pass | wrapper files only under `tooling/` plus status sync |
| Validation | pass path | `bash -n` on shell scripts |

## Decisions

- Add `lib/formal-tools-common.sh` to keep path resolution and receipt writing consistent across wrappers.
- Keep scripts boring Bash with repo-root-relative defaults.
- Provide an installer wrapper, but keep third-party downloads under `.formal-tools/` only.

## Completion Criteria

- Wrapper scripts and env example exist.
- Scripts are executable or documented.
- `bash -n` passes for all shell scripts.
