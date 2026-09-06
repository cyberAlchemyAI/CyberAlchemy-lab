# Task Session Context Pack: SWU-FMT-001

Status: pass
Date: 2026-06-16
Task session target: `SWU-FMT-001`
Parent task: `TASK-FMT-001`

## User Request

The user asked to run all tasks from the Alloy/TLA modeling plan through `task-session`.

The `task-session` sigil requires one bounded task or SWU at a time. The work-pack selects `SWU-FMT-001` as the first mutation-capable execution boundary, so this session executes that SWU first and records follow-up ordering for the remaining SWUs.

## Controlling Sources

| Source | Role |
| --- | --- |
| `../WORK-PACK.md` | Selects `SWU-FMT-001`, work scope, done criteria, and validation surface. |
| `../work-pack/tasks/TASK-FMT-001-toolchain.md` | Toolchain install commands and acceptance evidence. |
| `../IMPLEMENTATION-LAYERING.md` | L0 boundary: install and smoke only, no model repair. |
| `../PLAN-TRANSPORT.md` | Environment probe and pinned tool defaults. |
| `../../examples/README.md` | Evidence requirements for later model validation, deferred here. |

## Selected SWU

`SWU-FMT-001`: Make Java, TLA+ tools, and Alloy available from ignored local storage.

## Write Scope

Allowed:

- `.formal-tools/`
- `.git/info/exclude`
- `projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/toolchain/`
- `projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/session-evidence/`
- task/work-pack status synchronization if completion evidence passes
- repository-local observability JSONL

Not allowed:

- `arcanum/definitions/TAXONOMY.md`
- `arcanum/definitions/RELATIONSHIPS.md`
- model repairs to `examples/`
- wrapper scripts
- fixture contract files
- committing downloaded binaries or jars

## Gate Checks

| Gate | Result | Notes |
| --- | --- | --- |
| Exactly one SWU selected | pass | `SWU-FMT-001` selected. |
| Dependencies clear | pass | none. |
| Write scope defined | pass | local ignored tool cache plus receipts. |
| Validation surface defined | pass | Java, TLA+, and Alloy smoke commands. |
| System install path available | flag | `sudo -n true` failed; use local portable Java instead. |
| Tool binaries tracked | pass | `.formal-tools/` will be excluded through `.git/info/exclude`. |

## Decisions

| Decision | Selection | Rationale |
| --- | --- | --- |
| Java install method | Local portable Temurin JRE 17 | `sudo` requires a password; local JRE satisfies Java 11+ without system mutation. |
| Git ignore policy | `.git/info/exclude` | Keeps third-party tools local without editing project `.gitignore` in this SWU. |
| Tool versions | TLA+ `v1.7.4`; Alloy `v6.2.0`; Temurin JRE `17.0.19+10` | Pinned enough for reproducible first smoke. |

## Completion Criteria

- Java runs from `.formal-tools/jre/bin/java`.
- TLA+ tools jar is downloaded and its upstream SHA1 passes.
- Alloy jar is downloaded and a local SHA256 is recorded.
- TLA+ SANY help or equivalent command responds.
- TLA+ jar help or TLC help responds.
- Alloy jar help responds or exact CLI limitation is recorded.
- No `.formal-tools/` content appears in tracked git status.
