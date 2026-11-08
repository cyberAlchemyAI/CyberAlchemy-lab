---
id: player-progression
feature: player-progression
title: Player Progression Queries
summary: Read projection contract for progression status retrieval.
status: implemented
pillar: operations
domain: player-progression-queries
audience:
  - developers
priority: p2
lang: en
owners:
  - backend-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
  - operations.md
includes: []
---

# Queries: Player Progression

> **Capabilities using this aspect:** [Check Progression](SPEC.md#check-progression)

## GetProgressionStatus

**Type:** Query (read-only)
**Actor:** Operations user, web dashboard

### Input

| Field      | Type    | Required | Description                 |
| ---------- | ------- | -------- | --------------------------- |
| playerId   | string  | yes      | Target player               |
| periodDays | integer | no       | 15 or 30 days (mapped from period query) |

### Output

| Field                | Type    | Source                  | Description                       |
| -------------------- | ------- | ----------------------- | --------------------------------- |
| eligibleForPromotion | boolean | CheckProgression result | Promotion readiness flag          |
| reason               | string  | CheckProgression result | Human-readable eligibility reason |
| avgHands             | number  | CheckProgression result | Average daily hands in period     |
| winrate              | number  | CheckProgression result | Winrate in bb/100                 |
| period               | string  | CheckProgression result | BI_WEEKLY or MONTHLY              |

### Reads From

| Entity              | Relationship | Fields Used             |
| ------------------- | ------------ | ----------------------- |
| Player              | queries      | id, currentLimit        |
| PlayerStatsSnapshot | queries      | statDate, hands, profit |
