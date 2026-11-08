---
id: player-progression
feature: player-progression
title: Player Progression Workflows
summary: Workflow for progression checks delegated from player-management.
status: implemented
pillar: operations
domain: player-progression-workflows
audience:
  - developers
  - operations
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-17
dependencies:
  - SPEC.md
  - operations.md
  - mappings.md
  - queries.md
includes: []
---

# Workflows: Player Progression

## ProgressionCheckWorkflow

**Type:** Workflow
**Triggers:** `GET /players/:id/progression`
**Orchestrates:** [CheckProgression](operations.md#checkprogression), [GetProgressionStatus](queries.md#getprogressionstatus)
**Compensation Strategy:** none
**Idempotency:** yes (same inputs produce same output for unchanged stats)

### Steps

```mermaid
graph TD
  A[Authenticate + authorize caller] --> B[Map period query to periodDays]
  B --> C[Load player and stats window]
  C --> D[Evaluate progression policy]
  D --> E[Project response payload]
  E --> F[Return status]
```

### Step Table

| # | Step | Actor | Operation | On Success | On Failure | Compensation |
| --- | ---- | ----- | --------- | ---------- | ---------- | ------------ |
| 1 | Auth guard | API | CheckProgression | Step 2 | 401/403 | - |
| 2 | Period mapping | API | [ProgressionPeriodQueryToDays](mappings.md#progressionperiodquerytodays) | Step 3 | 400 | - |
| 3 | Domain inputs load | Use-case | CheckProgression | Step 4 | 404/500 | - |
| 4 | Policy evaluation | Domain | CheckProgression | Step 5 | 500 | - |
| 5 | Response projection | API | [ProgressionResultToStatusProjection](mappings.md#progressionresulttostatusprojection) | done | 500 | - |

### Invariants

| ID | Invariant | Formal |
| --- | --------- | ------ |
| I1 | Invalid period never reaches domain policy | `period not in {BI_WEEKLY, MONTHLY} -> request rejected` |
| I2 | No persistence side-effects occur in progression checks | `checkProgression => writes = 0` |
