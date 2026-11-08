# EXECUTION-PACK: Alloy/TLA Modeling Toolchain

Status: draft
Observed capability: invoke
Invoke mode: plan

## Purpose

Choreograph the medium-complexity work-pack into layer-mapped waves. This file schedules work; task files own the executable SWU contracts.

## Wave Overview

| Wave | Layer | Tasks | Parallelism | Promotion Evidence |
| --- | --- | --- | --- | --- |
| [W0](work-pack/waves/W0-toolchain.md) | L0 | TASK-FMT-001 | sequential | Java, TLA+, and Alloy can be invoked without tracked binaries. |
| [W1](work-pack/waves/W1-wrapper-surface.md) | L0/L1 | TASK-FMT-002 | sequential after W0 | Scripts and local cache policy make commands repeatable. |
| [W2](work-pack/waves/W2-example-validation.md) | L1 | TASK-FMT-003 | Alloy and TLA checks can run independently after W1 | Example receipts exist for both lanes. |
| [W3](work-pack/waves/W3-fixture-contract.md) | L2 | TASK-FMT-004 | sequential after W2 | Fixture contract bridges TypeScript witness to formal tools. |
| [W4](work-pack/waves/W4-readiness.md) | L3 | TASK-FMT-VERIFY | sequential closeout | Tower gates and learning pack reflect actual validation. |

## Execution Policy

- Execute one SWU at a time.
- `SWU-FMT-001` is selected first.
- Do not run Alloy/TLA model repair in the same SWU as toolchain install.
- If a tool cannot be installed in the local environment, close the SWU as `block` with exact command/output and reroute to manual environment setup.

## Expected Result Shape

```yaml
swu_id: SWU-FMT-001
result: pass | flag | block | interrupted
capability_ref: task-session
receipt_kind: native-stage | local-fallback | blocked
receipt_artifact: projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/<receipt>.md
files_touched:
  - <paths>
validation:
  - <command and result>
blockers:
  - <blocker or none>
residue:
  - <residue or none>
reroute: <next owner or none>
handoff_note: <what to run next>
```
