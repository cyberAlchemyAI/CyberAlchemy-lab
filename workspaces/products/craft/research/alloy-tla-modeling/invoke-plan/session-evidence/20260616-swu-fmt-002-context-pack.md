# SWU-FMT-002 Context Pack

## Scope

- Task session target: `SWU-FMT-002`
- Parent task: `TASK-FMT-001`
- Objective: record provenance and checksum policy for the locally downloaded formal tools.
- Execution mode: local fallback.

## Controlling Sources

- `../WORK-PACK.md`
- `../work-pack/tasks/TASK-FMT-001-toolchain.md`
- `../run-results/toolchain/swu-fmt-001-smoke-clean.md`
- TLA+ release page: `https://github.com/tlaplus/tlaplus/releases/tag/v1.7.4`
- Alloy release page: `https://github.com/AlloyTools/org.alloytools.alloy/releases/tag/v6.2.0`
- Temurin JRE release asset from Adoptium API.

## Write Scope

- Allowed:
  - `invoke-plan/run-results/toolchain/`
  - `invoke-plan/session-evidence/`
  - `WORK-PACK.md`
  - `work-pack/tasks/TASK-FMT-001-toolchain.md`
- Not allowed:
  - tracked third-party binaries
  - canonical DomainSpec definitions
  - model repairs or wrapper scripts

## Gates

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Dependency `SWU-FMT-001` | pass | `swu-fmt-001-smoke-clean.md` |
| Write scope | pass | receipt-only update under run-results and task status sync |
| Tool binary tracking | pass | `.formal-tools/` ignored by `.git/info/exclude`; scoped git status has no `.formal-tools` entries |
| Checksum policy | pass | TLA upstream SHA-1 recorded; Alloy local checksum recorded honestly |

## Decisions

- Preserve TLA+ upstream SHA-1 as the authoritative release checksum.
- Record Alloy checksum as local-only because no upstream checksum digest was available from the release metadata checked for this work-pack.
- Record Temurin JRE provenance because SWU-FMT-001 used a portable JRE rather than system Java.

## Completion Criteria

- Receipt records URLs, release tags, date checked, TLA+ upstream SHA-1, and local Alloy checksum.
- Validation confirms `.formal-tools/` remains untracked.
