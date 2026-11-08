---
id: player-stats
feature: player-stats
title: Player Stats Tracking Test Specification
summary: Deterministic test obligations derived from daily stats tracking contracts.
status: implemented
pillar: operations
domain: player-stats-tests
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
  - domain.md
  - operations.md
  - queries.md
  - interfaces.md
  - states.md
  - events.md
  - workflows.md
  - mappings.md
includes: []
---

# Player Stats Tracking TEST-SPEC

## Test Catalogue

| Test ID       | Type            | Source        | Obligation                              | Deterministic Assertion                                                                   |
| ------------- | --------------- | ------------- | --------------------------------------- | ----------------------------------------------------------------------------------------- |
| DST-RULE-001  | Rule validation | operations.md | R1 player exists                        | Unknown player returns `PLAYER_NOT_FOUND`                                                 |
| DST-RULE-002  | Rule validation | operations.md | R2 valid statDate                       | Invalid date format returns `VALIDATION_ERROR`                                            |
| DST-RULE-003  | Rule validation | operations.md | R3 hands non-negative integer           | Negative/non-integer hands return `VALIDATION_ERROR`                                      |
| DST-RULE-004  | Rule validation | operations.md | R4 sourceType supported                 | Unknown sourceType returns `VALIDATION_ERROR`                                             |
| DST-RULE-005  | Rule validation | operations.md | R6 correction must change values        | Unchanged correction returns `NO_CHANGES_DETECTED`                                        |
| DST-RULE-006  | Rule validation | operations.md | R7 rake non-negative                    | Negative rake returns `VALIDATION_ERROR`                                                  |
| DST-RULE-007  | Rule validation | operations.md | R8 sessionDuration non-negative integer | Negative/non-integer duration returns `VALIDATION_ERROR`                                  |
| DST-CALC-001  | Calculation     | operations.md | C2 record status                        | New snapshot => `RECORDED`; correction => `CORRECTED`                                     |
| DST-STATE-001 | Transition      | states.md     | [new] -> RECORDED                       | First write transitions to RECORDED                                                       |
| DST-STATE-002 | Transition      | states.md     | RECORDED -> CORRECTED                   | Correction transitions status                                                             |
| DST-INV-001   | Invariant       | states.md     | I1 unique identity                      | Only one snapshot exists per player/date                                                  |
| DST-INV-002   | Invariant       | states.md     | I2 non-negative hands                   | Persisted hands never negative                                                            |
| DST-API-001   | Contract        | interfaces.md | POST /player-stats                      | Response codes and shape match contract                                                   |
| DST-API-002   | Contract        | interfaces.md | GET history                             | Newest-first page and cursor semantics                                                    |
| DST-API-003   | Contract        | interfaces.md | GET window                              | Aggregate projection shape and auth codes                                                 |
| DST-QUERY-001 | Query           | queries.md    | GetPlayerStatsHistory                   | Filters/date window/pagination deterministic                                              |
| DST-QUERY-002 | Query           | queries.md    | GetPlayerStatsWindow                    | Aggregates equal sum of matching snapshots                                                |
| DST-QUERY-003 | Query           | queries.md    | GetPlayerStatsWindow derived metrics    | avgHandsPerDay = totalHands / sessionCount; winrate = (totalProfit/bb) / (totalHands/100) |
| DST-QUERY-004 | Query           | queries.md    | GetPlayerStatsWindow winrate null       | winrateBbPer100 is null when currentLimit not provided or totalHands = 0                  |
| DST-EVT-001   | Event           | events.md     | PlayerStatsRecorded produced            | Producer emits event on first write                                                       |
| DST-EVT-002   | Event           | events.md     | PlayerStatsCorrected produced           | Producer emits event on correction                                                        |
| DST-WF-001    | Workflow        | workflows.md  | RecordStatsWorkflow                     | Workflow path matches authorization -> validation -> persist -> event                     |

## Coverage Summary

- Rule validation: 7
- Calculations: 1
- State transitions/invariants: 4
- API contracts: 3
- Queries: 4
- Events: 2
- Workflow: 1
- Total obligations: 22

---

## Traceability Matrix

| Obligation    | Evidence File                        | Status  |
| ------------- | ------------------------------------ | ------- |
| DST-RULE-001  | record-player-stats.test.ts          | covered |
| DST-RULE-002  | record-player-stats.test.ts          | covered |
| DST-RULE-003  | record-player-stats.test.ts          | covered |
| DST-RULE-004  | record-player-stats.test.ts          | covered |
| DST-RULE-005  | record-player-stats.test.ts          | covered |
| DST-RULE-006  | record-player-stats.test.ts          | covered |
| DST-RULE-007  | record-player-stats.test.ts          | covered |
| DST-CALC-001  | record-player-stats.test.ts          | covered |
| DST-STATE-001 | record-player-stats.test.ts          | covered |
| DST-STATE-002 | record-player-stats.test.ts          | covered |
| DST-INV-001   | record-player-stats.test.ts          | covered |
| DST-INV-002   | record-player-stats.test.ts          | covered |
| DST-API-001   | player-stats.routes.contract.test.ts | covered |
| DST-API-002   | player-stats.routes.contract.test.ts | covered |
| DST-API-003   | player-stats.routes.contract.test.ts | covered |
| DST-QUERY-001 | get-player-stats-history.test.ts     | covered |
| DST-QUERY-002 | get-player-stats-window.test.ts      | covered |
| DST-QUERY-003 | get-player-stats-window.test.ts, player-stats-window-policy.service.test.ts | covered |
| DST-QUERY-004 | get-player-stats-window.test.ts      | covered |
| DST-EVT-001   | record-player-stats.test.ts          | covered |
| DST-EVT-002   | record-player-stats.test.ts          | covered |
| DST-WF-001    | record-player-stats.test.ts          | covered |

---

## Story To Test Mapping

| Story                                                                      | Key test IDs                                                                                                                                                                                                |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| US-01 Operations records daily stats for a player                          | DST-RULE-001, DST-RULE-002, DST-RULE-003, DST-RULE-004, DST-RULE-006, DST-RULE-007, DST-CALC-001, DST-STATE-001, DST-STATE-002, DST-INV-001, DST-INV-002, DST-API-001, DST-EVT-001, DST-EVT-002, DST-WF-001 |
| US-02 Operations reviews player stats history timeline                     | DST-QUERY-001, DST-API-002                                                                                                                                                                                  |
| US-03 Player overview and settlement consume aggregated stats window       | DST-QUERY-002, DST-QUERY-003, DST-QUERY-004, DST-API-003                                                                                                                                                    |
| US-04 Invalid and duplicate tracking inputs are rejected deterministically | DST-RULE-001, DST-RULE-002, DST-RULE-003, DST-RULE-004, DST-RULE-005, DST-RULE-006, DST-RULE-007, DST-INV-001                                                                                               |

## Pilot Must-Pass Subset (Wave 1)

| Priority | Test IDs | Why it is gate-critical | Evidence file targets |
| --- | --- | --- | --- |
| P0 | DST-RULE-001, DST-RULE-006, DST-RULE-007, DST-INV-001 | Protect stats data integrity and player identity validity for downstream finance and progression consumers. | `backend/src/use-cases/player-stats/record-player-stats.test.ts` |
| P0 | DST-API-001, DST-API-002, DST-API-003 | Lock API contracts for write/history/window endpoints consumed by operations and integrations. | `backend/src/infrastructure/http/routes/player-stats.routes.contract.test.ts` |
| P0 | DST-QUERY-002, DST-QUERY-003, DST-QUERY-004 | Guarantee deterministic aggregate/window metrics used by settlement and progression logic. | `backend/src/use-cases/player-stats/get-player-stats-window.test.ts`, `backend/src/domain/player-stats/player-stats-window-policy.service.test.ts` |
| P0 | DST-EVT-001, DST-EVT-002, DST-WF-001 | Ensure event and workflow integrity for recorded/corrected snapshot lifecycle. | `backend/src/use-cases/player-stats/record-player-stats.test.ts` |
| P1 | DST-RULE-002, DST-RULE-003, DST-RULE-004, DST-RULE-005, DST-QUERY-001 | Expand confidence on validation and history slicing behavior. | `backend/src/use-cases/player-stats/record-player-stats.test.ts`, `backend/src/use-cases/player-stats/get-player-stats-history.test.ts` |

## Pilot Execution Checklist

1. Freeze Wave 1 stats scope to P0 IDs.
Pass criteria: all P0 IDs are executable and mapped to evidence files.

2. Run stats integrity gate first.
Pass criteria: DST-RULE-001/006/007 and DST-INV-001 pass with deterministic rejection and uniqueness behavior.

3. Run API contract gate second.
Pass criteria: DST-API-001/002/003 pass with expected status and payload contracts.

4. Run aggregate/window gate third.
Pass criteria: DST-QUERY-002/003/004 pass and produce stable derived metrics.

5. Run event/workflow gate fourth.
Pass criteria: DST-EVT-001/002 and DST-WF-001 pass for record/correction lifecycle.

6. Execute optional P1 validation/history checks.
Pass criteria: P1 IDs pass without affecting P0 verdict.

7. Capture blockers and evidence package.
Pass criteria: open blockers include owner, action, and closure evidence target.

8. Compute final Wave 1 verdict.
Pass criteria: zero failing P0 tests and no open P0 blocker.

## Pilot Go No-Go Blockers Register

| Blocker ID | Status | Blocker | Why it blocks Wave 1 | Required evidence to clear |
| --- | --- | --- | --- | --- |
| PST-BLK-01 | closed | UI/alignment artifacts are stale and inconsistent with current implementation evidence. | Pilot governance decisions can be based on outdated readiness signals. | Closed on 2026-04-24 via refreshed [UI-REVIEW.md](UI-REVIEW.md) and [ALIGNMENT-REPORT.md](ALIGNMENT-REPORT.md) with current evidence. |
| PST-BLK-02 | closed | Layering drift remains unresolved for stats window derivation authority. | Metric derivation behavior can drift across consumers over time. | Closed on 2026-04-24 by extracting derivation authority to `backend/src/domain/player-stats/player-stats-window-policy.service.ts` and refreshing [LAYERING-ALIGNMENT-REPORT.md](LAYERING-ALIGNMENT-REPORT.md). |
| PST-BLK-03 | closed | Observability coverage was below pilot threshold for stats lifecycle workflows. | Without P0 lifecycle telemetry, MVP GO would remain blocked by missing transition/invariant evidence. | Closed on 2026-04-24 by instrumenting `state.transition`, `state.invalid_transition`, `invariant.violation`, plus operation/workflow/event metrics in `backend/src/use-cases/player-stats/record-player-stats.ts`; validated by `record-player-stats.test.ts` and refreshed [OBSERVABILITY-REPORT.md](OBSERVABILITY-REPORT.md) verdict (FLAG, no open P0 gaps). |

## Pilot Evidence Package

1. Data integrity evidence
- Test outputs for DST-RULE-001/006/007 and DST-INV-001.

2. Contract evidence
- Route contract test output for POST/GET history/GET window endpoints.

3. Aggregate correctness evidence
- Query test outputs for DST-QUERY-002/003/004 with deterministic numeric assertions.

4. Event/workflow evidence
- Recorded/corrected event and workflow execution assertions.

5. Decision artifact
- Final blocker register snapshot and computed PASS/FLAG/BLOCK decision.

## Pilot Decisions Provenance

This test gate follows policy decisions recorded in [PILOT-DECISIONS.md](PILOT-DECISIONS.md).
