---
id: player-progression
feature: player-progression
title: Player Progression Mappings
summary: Input and output mappings for progression period and result projection.
status: implemented
pillar: operations
domain: player-progression-mappings
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-17
dependencies:
  - SPEC.md
  - interfaces.md
  - operations.md
  - queries.md
includes: []
---

# Mappings: Player Progression

## ProgressionPeriodQueryToDays

**Direction:** External API -> Use-case input
**Used by:** [CheckProgression](operations.md#checkprogression)

| Source | Target | Rule |
| ------ | ------ | ---- |
| `period = MONTHLY` | `periodDays = 30` | Explicit monthly window |
| `period = BI_WEEKLY` | `periodDays = 15` | Explicit bi-weekly window |
| `period` omitted | `periodDays = 15` | Default behavior |

## ProgressionResultToStatusProjection

**Direction:** Use-case output -> External API
**Used by:** [GetProgressionStatus](queries.md#getprogressionstatus)

| Source | Target | Rule |
| ------ | ------ | ---- |
| `eligibleForPromotion` | `eligibleForPromotion` | Direct mapping |
| `reason` | `reason` | Direct mapping |
| `avgHands` | `avgHands` | Direct mapping |
| `winrate` | `winrate` | Direct mapping |
| `period` | `period` | Direct mapping (`BI_WEEKLY` or `MONTHLY`) |
