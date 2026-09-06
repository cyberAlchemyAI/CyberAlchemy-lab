---
module: alloy-tla-modeling-toolchain
version: current
status: draft
updatedAt: 2026-06-16T20:51:08Z
docType: work-pack
observedCapability: invoke
invokeMode: plan
---

# WORK-PACK: Alloy/TLA Modeling Toolchain

## Control Fields

| Field | Value | Notes |
| --- | --- | --- |
| workPackGateStatus | completed-with-residue | Local executable surface is ready; TLA freshness repair remains. |
| complexity | medium | More than two artifacts, system tool dependency, wrapper scripts, model validation, fixture contract. |
| outputMode | split | Uses task and wave files. |
| executionPackRef | `EXECUTION-PACK.md` | Wave choreography lives there. |
| layeringArtifactRef | `IMPLEMENTATION-LAYERING.md` | L0-L3 boundaries. |
| activeLayerWindow | complete | All planned SWUs executed; residue is tracked. |
| lastUpdatedAt | 2026-06-16T21:53:00Z | UTC. |
| readinessProfile | pilot | Research harness, not canonical validator. |

## Objective Summary

- Objective: Install and expose a repo-local, repeatable Alloy/TLA+ formal-modeling surface for the DomainSpec v2 `alloy-tla-modeling` tower.
- Primary inputs:
  - `../BRIDGE-DECISIONS.md`
  - `../levels/L2-closure-plan.md`
  - `../examples/OrderFulfillmentSaga.alloy`
  - `../examples/OrderFulfillmentSaga.tla`
  - `../../dcb-saga-correctness/toy-run-result.md`
- Success condition: A later `task-session` can install or locate Java, fetch pinned Alloy/TLA tools into ignored local storage, run smoke commands, validate both example models, and record formal-run receipts without mutating canonical DomainSpec definitions.

## Delivery Slices

| Slice ID | Outcome | Layer | Wave | Dependencies | Validation |
| --- | --- | --- | --- | --- | --- |
| S-001 | Local toolchain install and smoke surface. | L0 | [W0](work-pack/waves/W0-toolchain.md) | none | Java, TLA+, Alloy help commands pass. |
| S-002 | Wrapper scripts and cache policy. | L0/L1 | [W1](work-pack/waves/W1-wrapper-surface.md) | S-001 | Scripts produce deterministic command output and avoid tracked binaries. |
| S-003 | Alloy and TLA example validation. | L1 | [W2](work-pack/waves/W2-example-validation.md) | S-001, S-002 | Alloy/TLA receipts captured with commands, versions, and results. |
| S-004 | Fixture contract for TypeScript-to-formal bridge. | L2 | [W3](work-pack/waves/W3-fixture-contract.md) | S-003 | Fixture aligns to examples and preserves fact classification. |
| S-005 | Readiness verification and tower sync. | L3 | [W4](work-pack/waves/W4-readiness.md) | S-001..S-004 | Markdown links pass, receipts present, tower gates updated. |

## Task Status Board

| Task ID | Goal | Layer | Complexity | Waves | Source | Gate Status | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [TASK-FMT-001](work-pack/tasks/TASK-FMT-001-toolchain.md) | Install or locate Java, TLA+, and Alloy without committing binaries. | L0 | medium | [W0](work-pack/waves/W0-toolchain.md) | `IMPLEMENTATION-LAYERING.md`, official releases | completed | completed |
| [TASK-FMT-002](work-pack/tasks/TASK-FMT-002-wrapper-surface.md) | Add wrapper/install scripts and local cache policy. | L0/L1 | medium | [W1](work-pack/waves/W1-wrapper-surface.md) | TASK-FMT-001 | completed | completed |
| [TASK-FMT-003](work-pack/tasks/TASK-FMT-003-example-validation.md) | Validate Alloy and TLA example models and capture receipts. | L1 | medium | [W2](work-pack/waves/W2-example-validation.md) | examples, TASK-FMT-002 | completed-with-residue | completed |
| [TASK-FMT-004](work-pack/tasks/TASK-FMT-004-fixture-contract.md) | Define TypeScript `SagaSpec` formal fixture contract. | L2 | medium | [W3](work-pack/waves/W3-fixture-contract.md) | toy harness, TASK-FMT-003 | completed | completed |
| [TASK-FMT-VERIFY](work-pack/tasks/TASK-FMT-VERIFY-readiness.md) | Verify plan execution artifacts and sync tower gates. | L3 | low | [W4](work-pack/waves/W4-readiness.md) | all prior tasks | completed-with-residue | completed |

## SWU Execution Handoff

| SWU ID | Parent Task | Source Anchors | Related Context | Dependencies | Write Scope | Done Criteria | Acceptance Evidence | Validation Surface | Execution Owner | Handoff Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SWU-FMT-001 | [TASK-FMT-001](work-pack/tasks/TASK-FMT-001-toolchain.md) | official release URLs, `../examples/README.md` | `../SOURCE-RECORD.md` | none | ignored cache path only; optional `.gitignore`/`.git/info/exclude` | Java and jars/binaries available without tracked artifacts. | [clean smoke receipt](run-results/toolchain/swu-fmt-001-smoke-clean.md) | local Java version; SANY parse; TLC finite smoke; Alloy help/version. | local-fallback | completed |
| SWU-FMT-002 | [TASK-FMT-001](work-pack/tasks/TASK-FMT-001-toolchain.md) | official checksums and asset URLs | source release pages | SWU-FMT-001 | `invoke-plan/run-results/toolchain/` | Checksum or provenance receipt recorded. | [toolchain provenance receipt](run-results/toolchain/toolchain-receipt.md) | checksum review; scoped git status. | local-fallback | completed |
| SWU-FMT-003 | [TASK-FMT-002](work-pack/tasks/TASK-FMT-002-wrapper-surface.md) | command examples in task file | toolchain smoke output | SWU-FMT-001 | `tooling/`, `.gitignore` if needed | Wrapper scripts provide stable commands for install, TLA check, Alloy check. | [wrapper validation](run-results/toolchain/swu-fmt-003-wrapper-validation.md) | `bash -n`; wrapper Alloy/TLA smoke. | local-fallback | completed |
| SWU-FMT-004 | [TASK-FMT-002](work-pack/tasks/TASK-FMT-002-wrapper-surface.md) | `../gates/closure-gates.md` | run-results policy | SWU-FMT-003 | `run-results/`, `tooling/README.md` | Results and generated artifacts policy is explicit. | [policy validation](run-results/toolchain/swu-fmt-004-policy-validation.md) | markdown link check. | local-fallback | completed |
| SWU-FMT-005 | [TASK-FMT-003](work-pack/tasks/TASK-FMT-003-example-validation.md) | `../examples/OrderFulfillmentSaga.tla` | `../NOTATION-BRIDGE.md` | SWU-FMT-003 | examples `.cfg`, run-results TLA receipts | SANY/TLC validates or flags TLA model with exact error. | [TLA summary](run-results/tla/order-fulfillment-summary.md) | SANY pass; TLC `FreshnessSafety` counterexample captured. | local-fallback | completed-with-counterexample |
| SWU-FMT-006 | [TASK-FMT-003](work-pack/tasks/TASK-FMT-003-example-validation.md) | `../examples/OrderFulfillmentSaga.alloy` | `../CLAIM-LEDGER.md` | SWU-FMT-003 | Alloy example and run-results receipts | Alloy validates or flags model with exact error/counterexample result. | [Alloy summary](run-results/alloy/order-fulfillment-summary.md) | Alloy commands and exec pass after reserved-word syntax repair. | local-fallback | completed |
| SWU-FMT-007 | [TASK-FMT-004](work-pack/tasks/TASK-FMT-004-fixture-contract.md) | `../../dcb-saga-correctness/toy-harness/`, `../../dcb-saga-correctness/toy-run-result.json` | `../DEFINITIONS.md` | SWU-FMT-005, SWU-FMT-006 | `fixtures/`, optional generator design doc | Formal fixture contract maps SagaSpec to Alloy/TLA inputs. | [fixture validation](run-results/fixtures/swu-fmt-007-fixture-validation.md) | JSON validation plus fixture README link check. | local-fallback | completed |
| SWU-FMT-008 | [TASK-FMT-VERIFY](work-pack/tasks/TASK-FMT-VERIFY-readiness.md) | all prior receipts | tower gates | SWU-FMT-001..SWU-FMT-007 | `../gates/closure-gates.md`, `../LEARNING-PACK.md`, `invoke-plan/PLAN-TRANSPORT.md` | Tower gates accurately reflect tool validation state. | [readiness closeout](run-results/swu-fmt-008-readiness-closeout.md) | markdown links; scoped git status; receipt inventory. | local-fallback | completed-with-residue |

## Blockers

| Blocker ID | Scope | Description | Owner | Next Action | Target Date |
| --- | --- | --- | --- | --- | --- |
| B-FMT-001 | SWU-FMT-001 | `java` is not currently on PATH. | executor | Resolved for L0 by portable Temurin JRE in `.formal-tools/jre/current`; system install remains optional. | completed 2026-06-16 |
| B-FMT-002 | SWU-FMT-006 | Alloy release assets do not publish checksums in the GitHub API. | executor | Policy recorded in `run-results/toolchain/toolchain-receipt.md`; future Alloy receipts must keep the checksum local-only. | next Alloy validation |
| B-FMT-003 | SWU-FMT-005 | TLA+ liveness checking has a release-note caveat in v1.7.4; first model should start with safety checks. | executor | Safety run completed and found `FreshnessSafety` counterexample; defer liveness/fairness until freshness semantics are repaired or reframed. | after TLA repair |

## Required Links

- [Implementation layering](IMPLEMENTATION-LAYERING.md)
- [Execution pack](EXECUTION-PACK.md)
- [Plan transport](PLAN-TRANSPORT.md)
- [Shared context](work-pack/shared/context.md)
- [Traceability](work-pack/shared/traceability.md)
- [Cross-task gaps](work-pack/shared/cross-task-gaps.md)
- [Cross-task decisions](work-pack/shared/cross-task-decisions.md)

## Gate Checks

1. All SWUs were executed in order from toolchain to readiness closeout.
2. Tool downloads went into ignored local storage at `.formal-tools/`.
3. Wrapper scripts are tracked; downloaded binaries are not tracked.
4. Alloy and TLA results are receipts, not prose-only claims.
5. Failed checks are captured honestly and rerouted to model repair.
6. No task mutated DomainSpec canonical definitions.

## Recommended Next Route

All planned SWUs have been executed. Next route is TLA freshness repair/reframing before any proof-strength claim.

## Change Log

| Date | Change | Author |
| --- | --- | --- |
| 2026-06-16 | SWU-FMT-001 completed with portable Java, TLA+, and Alloy smoke evidence. | Codex |
| 2026-06-16 | SWU-FMT-002 completed with tool provenance and checksum policy. | Codex |
| 2026-06-16 | SWU-FMT-003 completed with tracked wrapper scripts and syntax/smoke evidence. | Codex |
| 2026-06-16 | SWU-FMT-004 completed with tooling policy docs and link validation. | Codex |
| 2026-06-16 | SWU-FMT-005 completed with TLA parse pass and TLC freshness counterexample receipt. | Codex |
| 2026-06-16 | SWU-FMT-006 completed with Alloy bounded run/check receipts. | Codex |
| 2026-06-16 | SWU-FMT-007 completed with formal fixture schema and example fixture. | Codex |
| 2026-06-16 | SWU-FMT-008 completed with tower readiness closeout and residue sync. | Codex |
| 2026-06-16 | Initial invoke plan authored. | Codex |
