---
id: financial-settlement
feature: financial-settlement
title: Financial Settlement Queries
summary: Read model for settlement period preview and review.
status: implemented
pillar: finance
domain: financial-settlement-queries
audience:
  - developers
  - finance
priority: p2
lang: en
owners:
  - finance-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
includes: []
---

# Queries: Financial Settlement

## GetSettlementPreview

**Type:** Query (read-only)  
**Actor:** Finance user

### Input

| Field     | Type   | Required | Description   |
| --------- | ------ | -------- | ------------- |
| playerId  | string | yes      | Target player |
| startDate | string | yes      | Period start  |
| endDate   | string | yes      | Period end    |

### Output

| Field              | Type    | Source              | Description            |
| ------------------ | ------- | ------------------- | ---------------------- |
| totalProfit        | integer | [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot).profit   | Sum in period          |
| totalRakeback      | integer | [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot).rakeback | Sum in period          |
| previousMakeup     | integer | Player.makeup       | Debt before settlement |
| newMakeup          | integer | ApplyMakeupPolicy   | Debt after policy      |
| totalPayout        | integer | ApplyMakeupPolicy   | Expected payout        |
| projectedNewMakeup | integer | API compatibility alias for `newMakeup` | Debt after policy      |
| projectedPayout    | integer | API compatibility alias for `totalPayout` | Expected payout        |

### Reads From

| Entity     | Relationship | Fields Used              |
| ---------- | ------------ | ------------------------ |
| Player     | queries      | id, makeup, currentLimit |
| [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot) | queries | statDate, profit, rakeback |
