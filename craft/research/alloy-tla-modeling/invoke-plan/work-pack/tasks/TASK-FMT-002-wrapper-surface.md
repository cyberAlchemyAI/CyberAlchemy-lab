# TASK-FMT-002: Wrapper Surface

Layer: L0/L1
Status: completed

## Objective

Create a small tracked command surface so future agents can run Alloy/TLA checks without re-learning tool paths.

## Source Contracts

- `TASK-FMT-001-toolchain.md`
- `../../WORK-PACK.md`
- `../../../examples/README.md`

## Implementation Detail

Proposed tracked files:

```text
projects/domainspec-v2/research/alloy-tla-modeling/tooling/README.md
projects/domainspec-v2/research/alloy-tla-modeling/tooling/formal-tools.env.example
projects/domainspec-v2/research/alloy-tla-modeling/tooling/install-formal-tools.sh
projects/domainspec-v2/research/alloy-tla-modeling/tooling/run-tla-check.sh
projects/domainspec-v2/research/alloy-tla-modeling/tooling/run-alloy-check.sh
projects/domainspec-v2/research/alloy-tla-modeling/tooling/validate-examples.sh
```

Wrapper behavior:

- default `FORMAL_TOOLS_HOME=.formal-tools`;
- fail with clear instructions when Java or jars are missing;
- write receipts under `invoke-plan/run-results/`;
- never download into tracked paths;
- allow env overrides for `JAVA_BIN`, `TLA_TOOLS_JAR`, and `ALLOY_JAR`.

## Smallest Working Units

### SWU-FMT-003

- Goal: Add wrapper scripts and env example.
- Dependencies: SWU-FMT-001.
- Write scope: `tooling/`, optional `.gitignore`.
- Done criteria: scripts exist, are executable or documented, and parse with `bash -n`.
- Acceptance evidence: `bash -n tooling/*.sh` output.
- Validation surface: `bash -n`.
- Execution owner: subagent.
- Handoff note: Keep scripts boring; shell portability beats cleverness here.
- Status: completed 2026-06-16.
- Evidence:
  - `../../../tooling/formal-tools.env.example`
  - `../../../tooling/install-formal-tools.sh`
  - `../../../tooling/run-tla-check.sh`
  - `../../../tooling/run-alloy-check.sh`
  - `../../../tooling/validate-examples.sh`
  - `../../../tooling/lib/formal-tools-common.sh`
  - `../../run-results/toolchain/swu-fmt-003-wrapper-validation.md`
- Validation result: pass. `bash -n` passed and wrappers resolved the local TLA+/Alloy tools.

### SWU-FMT-004

- Goal: Document cache, binary, and receipt policy.
- Dependencies: SWU-FMT-003.
- Write scope: `tooling/README.md`, `invoke-plan/run-results/`.
- Done criteria: docs say what is tracked, ignored, downloaded, and recorded.
- Acceptance evidence: README plus link check.
- Validation surface: `bash tools/check_markdown_links.sh projects/domainspec-v2/research/alloy-tla-modeling/tooling/README.md`.
- Execution owner: subagent.
- Handoff note: The policy should protect the repo from accidental binary commits.
- Status: completed 2026-06-16.
- Evidence:
  - `../../../tooling/README.md`
  - `../../run-results/toolchain/swu-fmt-004-policy-validation.md`
- Validation result: pass. `tools/check_markdown_links.sh` passed for the tooling README.
