---
id: player-stats
feature: player-stats
title: Player Stats Tracking Queries
summary: Read contracts for player stats timeline and aggregate windows.
status: implemented
pillar: operations
domain: player-stats-queries
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
includes: []
---

# Queries: Player Stats Tracking

> **Capabilities using this aspect:** [Get Player Stats History](SPEC.md#get-player-stats-history) · [Get Player Stats Window](SPEC.md#get-player-stats-window)

## Domain Policy Ownership

Derived stats-window metrics are domain-owned and use-case orchestration delegates to that policy.

- Domain policy authority: [`backend/src/domain/player-stats/player-stats-window-policy.service.ts`](../../../backend/src/domain/player-stats/player-stats-window-policy.service.ts)
- Use-case orchestrator: [`backend/src/use-cases/player-stats/get-player-stats-window.ts`](../../../backend/src/use-cases/player-stats/get-player-stats-window.ts)

## GetPlayerStatsHistory

**Type:** Query (read-only)
**Actor:** Authorized operations user

### Input

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| playerId | string | yes | Target player |
| fromDate | string | no | Lower bound (`YYYY-MM-DD`) |
| toDate | string | no | Upper bound (`YYYY-MM-DD`) |
| limit | integer | no | Page size (default 50, max 200) |
| cursor | string | no | Opaque pagination cursor |

### Output

| Field | Type | Source | Description |
| ----- | ---- | ------ | ----------- |
| playerId | string | [PlayerStatsSnapshot](domain.md#playerstatssnapshot).playerId | Target player |
| entries[] | array | [PlayerStatsSnapshot](domain.md#playerstatssnapshot) | Newest-first snapshots |
| nextCursor | string \| null | Query page state | Cursor for next page |

### Reads From

| Entity | Relationship | Fields Used |
| ------ | ------------ | ----------- |
| [PlayerStatsSnapshot](domain.md#playerstatssnapshot) | queries | playerId, statDate, hands, profit, rakeback, rake, closingBankroll, sessionDuration, sourceType, status, updatedAt |

## GetPlayerStatsWindow

**Type:** Query (read-only)
**Actor:** Authorized feature consumer

### Input

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| playerId | string | yes | Target player |
| fromDate | string | yes | Window start (`YYYY-MM-DD`) |
| toDate | string | yes | Window end (`YYYY-MM-DD`) |
| currentLimit | string | no | Player limit for BB derivation (enables winrate) |

### Rules

| ID | Rule | Formal |
| -- | ---- | ------ |
| R1 | fromDate must be valid | `isValidDate(fromDate) = true` |
| R2 | toDate must be valid | `isValidDate(toDate) = true` |
| R3 | Window ordering must be valid | `toDate >= fromDate` |

### Output

| Field | Type | Source | Description |
| ----- | ---- | ------ | ----------- |
| playerId | string | [PlayerStatsWindow](domain.md#playerstatswindow).playerId | Target player |
| fromDate | string | [PlayerStatsWindow](domain.md#playerstatswindow).fromDate | Window start |
| toDate | string | [PlayerStatsWindow](domain.md#playerstatswindow).toDate | Window end |
| totalHands | integer | [PlayerStatsWindow](domain.md#playerstatswindow).totalHands | Sum of hands |
| totalProfit | number | [PlayerStatsWindow](domain.md#playerstatswindow).totalProfit | Sum of profit |
| totalRakeback | number | [PlayerStatsWindow](domain.md#playerstatswindow).totalRakeback | Sum of rakeback |
| totalRake | number | [PlayerStatsWindow](domain.md#playerstatswindow).totalRake | Sum of rake |
| totalSessionMinutes | integer | [PlayerStatsWindow](domain.md#playerstatswindow).totalSessionMinutes | Sum of session time |
| sessionCount | integer | [PlayerStatsWindow](domain.md#playerstatswindow).sessionCount | Matched record count |
| avgHandsPerDay | number | [PlayerStatsWindow](domain.md#playerstatswindow).avgHandsPerDay | totalHands / sessionCount |
| winrateBbPer100 | number \| null | [PlayerStatsWindow](domain.md#playerstatswindow).winrateBbPer100 | BB/100 winrate; null when currentLimit not provided or totalHands = 0 |

### Reads From

| Entity | Relationship | Fields Used |
| ------ | ------------ | ----------- |
| [PlayerStatsSnapshot](domain.md#playerstatssnapshot) | queries | playerId, statDate, hands, profit, rakeback, rake, sessionDuration |
| [player-management.Player](../player-management/domain.md#player) | queries (optional) | currentLimit |
