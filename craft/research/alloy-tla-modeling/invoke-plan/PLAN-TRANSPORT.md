# Invoke Plan Transport

Status: executed-with-residue
Timestamp: 2026-06-16T21:50:00Z

## Intent

User requested: `/invoke a plan so we can install the languages and have a more workable surface`.

## Mode Selection

- Mode: plan
- Spell: invoke
- Canonical ID: invoke
- Reason: The tower already exists and needs an execution-ready work-pack for installing Alloy/TLA+ tooling and validating examples.

## Context Builder Coverage

| Source | Coverage |
| --- | --- |
| `../BRIDGE-DECISIONS.md` | pass |
| `../levels/L2-closure-plan.md` | pass |
| `../examples/` | pass |
| official Alloy release source | pass |
| official TLA+ release source | pass |
| local environment probe | pass |

## Template Selection

| Template | Selected | Eligibility Evidence |
| --- | --- | --- |
| `implementation-layering.md` | yes | Required by invoke plan mode. |
| `work-pack.md` | yes | Required by invoke plan mode. |
| split task/wave files | yes | Medium complexity: system dependency, wrappers, validation, fixture contract. |
| execution pack | yes | Medium complexity wave choreography. |

## Environment Probe

| Check | Result |
| --- | --- |
| OS | WSL/Linux x86_64 |
| `apt` / `apt-get` | available |
| `curl` / `wget` | available |
| `sha1sum` | available |
| `java` | missing |
| `alloy` | missing |
| `tlc` | missing |
| local Alloy/TLA jars | missing |

Post-execution note: system commands are still not installed on `PATH`, but the tower now has a portable Java/TLA+/Alloy surface under ignored `.formal-tools/` with wrappers in `../tooling/`.

## Pinned Tool Defaults

| Tool | Pinned default | Source |
| --- | --- | --- |
| Java | Java 11+ required; plan recommends OpenJDK 17 on WSL/apt. | TLA+ tools README |
| TLA+ tools | v1.7.4 `tla2tools.jar`; sha1 `bee4a54f3ee3d4afc347c3240ec2d9e93b075104`. | TLA+ GitHub release |
| Alloy | v6.2.0 `org.alloytools.alloy.dist.jar` or Linux tarball. | Alloy homepage and GitHub release |

## Decisions

- Use pinned stable releases for the first toolchain surface.
- Keep third-party binaries in ignored local storage.
- Track only scripts, receipts, docs, examples, configs, and fixture contracts.
- Select `SWU-FMT-001` as the next execution boundary.
- Defer liveness/fairness until TLA+ safety checks parse and run.

## Outputs

- `IMPLEMENTATION-LAYERING.md`
- `WORK-PACK.md`
- `EXECUTION-PACK.md`
- `PLAN-TRANSPORT.md`
- `work-pack/tasks/`
- `work-pack/waves/`
- `work-pack/shared/`

## Unresolved Gaps

| Gap | Owner | Next Action |
| --- | --- | --- |
| Java missing locally. | task-session executor | Install OpenJDK or point wrappers at an existing Java 11+ runtime. |
| Alloy release asset checksum unavailable from upstream release metadata. | task-session executor | Record local checksum after download and source URL. |
| Alloy/TLA examples unvalidated. | task-session executor | Execute SWU-FMT-005 and SWU-FMT-006 after toolchain is available. |

## Execution Results

| SWU | Result | Evidence |
| --- | --- | --- |
| SWU-FMT-001 | pass | `run-results/toolchain/swu-fmt-001-smoke-clean.md` |
| SWU-FMT-002 | pass | `run-results/toolchain/toolchain-receipt.md` |
| SWU-FMT-003 | pass | `run-results/toolchain/swu-fmt-003-wrapper-validation.md` |
| SWU-FMT-004 | pass | `run-results/toolchain/swu-fmt-004-policy-validation.md` |
| SWU-FMT-005 | completed-with-counterexample | `run-results/tla/order-fulfillment-summary.md` |
| SWU-FMT-006 | pass-bounded | `run-results/alloy/order-fulfillment-summary.md` |
| SWU-FMT-007 | pass | `run-results/fixtures/swu-fmt-007-fixture-validation.md` |

## Next Route

Repair or reframe the TLA+ freshness semantics before promoting any saga-correctness claim. The local tooling surface is ready for repeated research runs.
