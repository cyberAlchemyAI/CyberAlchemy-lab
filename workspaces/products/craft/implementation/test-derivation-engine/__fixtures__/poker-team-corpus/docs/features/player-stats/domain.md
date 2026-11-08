---
id: player-stats
feature: player-stats
title: Player Stats Tracking Domain
summary: Structural concepts for player stats snapshots and aggregate windows.
status: implemented
pillar: operations
domain: player-stats-domain
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
includes: []
---

# Domain: Player Stats Tracking

> **Capabilities using this aspect:** [Record Player Stats](SPEC.md#record-player-stats) · [Get Player Stats History](SPEC.md#get-player-stats-history) · [Get Player Stats Window](SPEC.md#get-player-stats-window)

## Entities

### PlayerStatsSnapshot

Authoritative daily stats snapshot for one player and one statDate.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| id | string | yes | Stable unique identifier |
| playerId | string | yes | Player reference |
| statDate | string | yes | Tracked date in `YYYY-MM-DD` |
| hands | integer | yes | Number of played hands (`>= 0`) |
| profit | number | yes | Profit value for the date |
| rakeback | number | yes | Rakeback value for the date |
| rake | number | yes | Rake paid for the date (`>= 0`) |
| closingBankroll | number | yes | End-of-day bankroll balance |
| sessionDuration | integer | yes | Total session time in minutes (`>= 0`) |
| sourceType | [StatsSourceType](#statssourcetype) | yes | Ingestion source classification |
| status | [StatsRecordStatus](#statsrecordstatus) | yes | Record lifecycle status |
| createdAt | datetime | yes | Initial creation time |
| updatedAt | datetime | yes | Last correction time |

**Uniqueness constraint:** One active snapshot per `playerId + statDate`.

## Value Objects

### PlayerStatsWindow

Aggregate projection built from all [PlayerStatsSnapshot](#playerstatssnapshot) records inside a date window.

| Field | Type | Constraint |
| ----- | ---- | ---------- |
| playerId | string | Must match query input |
| fromDate | string | `YYYY-MM-DD` |
| toDate | string | `YYYY-MM-DD`, `toDate >= fromDate` |
| totalHands | integer | Sum of `hands`, `>= 0` |
| totalProfit | number | Sum of `profit` |
| totalRakeback | number | Sum of `rakeback` |
| totalRake | number | Sum of `rake`, `>= 0` |
| totalSessionMinutes | integer | Sum of `sessionDuration`, `>= 0` |
| sessionCount | integer | Count of matched snapshots |
| avgHandsPerDay | number | `totalHands / sessionCount` (rounded) |
| winrateBbPer100 | number | `(totalProfit / bbValue) / (totalHands / 100)`, rounded to 2 decimals. Requires `currentLimit` context |

## Enums

### StatsSourceType

| Value | Description |
| ----- | ----------- |
| MANUAL | Entered manually by operations |
| IMPORT | Imported from file ingest |
| API | Received from external service integration |

### StatsRecordStatus

| Value | Description |
| ----- | ----------- |
| RECORDED | First accepted record for `playerId + statDate` |
| CORRECTED | Existing record updated with corrected values |
