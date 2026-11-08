---
id: player-stats
feature: player-stats
title: Player Stats Tracking Mappings
summary: Data transformations for player stats tracking request and response shapes.
status: implemented
pillar: platform
domain: player-stats-mappings
audience:
  - developers
priority: p2
lang: en
owners:
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - interfaces.md
  - domain.md
includes: []
---

# Mappings: Player Stats Tracking

> **Capabilities using this aspect:** [Record Player Stats](SPEC.md#record-player-stats) · [Get Player Stats History](SPEC.md#get-player-stats-history) · [Get Player Stats Window](SPEC.md#get-player-stats-window)

## RecordStatsRequestToInput

**From:** PlayerStatsAPI request payload
**To:** [RecordPlayerStats](operations.md#recordplayerstats) input

| Source | Target | Transform | Notes |
| ------ | ------ | --------- | ----- |
| body.playerId | playerId | direct | UUID/string identity |
| body.statDate | statDate | normalize-date | `YYYY-MM-DD` required |
| body.hands | hands | to-integer | Reject NaN and negative |
| body.profit | profit | money-normalize | Keep deterministic precision |
| body.rakeback | rakeback | money-normalize | Keep deterministic precision |
| body.rake | rake | money-normalize | Non-negative |
| body.closingBankroll | closingBankroll | money-normalize | End-of-day balance |
| body.sessionDuration | sessionDuration | to-integer | Non-negative minutes |
| body.sourceType | sourceType | enum-validate | Must match [StatsSourceType](domain.md#statssourcetype) |

## PlayerStatsEntityToHistoryItem

**From:** [PlayerStatsSnapshot](domain.md#playerstatssnapshot)
**To:** History response `entries[]`

| Source | Target | Transform | Notes |
| ------ | ------ | --------- | ----- |
| snapshot.id | id | direct | Stable identifier |
| snapshot.statDate | statDate | direct | Date string |
| snapshot.hands | hands | direct | Non-negative integer |
| snapshot.profit | profit | direct | Numeric value |
| snapshot.rakeback | rakeback | direct | Numeric value |
| snapshot.rake | rake | direct | Numeric value |
| snapshot.closingBankroll | closingBankroll | direct | Numeric value |
| snapshot.sessionDuration | sessionDuration | direct | Integer minutes |
| snapshot.sourceType | sourceType | direct | Enum value |
| snapshot.status | status | direct | Record status |
| snapshot.updatedAt | updatedAt | iso-datetime | ISO output |

## PlayerStatsWindowToProjection

**From:** [PlayerStatsWindow](domain.md#playerstatswindow)
**To:** Aggregate window response

| Source | Target | Transform | Notes |
| ------ | ------ | --------- | ----- |
| window.playerId | playerId | direct | Query identity |
| window.fromDate | fromDate | direct | Window start |
| window.toDate | toDate | direct | Window end |
| window.totalHands | totalHands | direct | Summed hands |
| window.totalProfit | totalProfit | direct | Summed profit |
| window.totalRakeback | totalRakeback | direct | Summed rakeback |
| window.totalRake | totalRake | direct | Summed rake |
| window.totalSessionMinutes | totalSessionMinutes | direct | Summed session time |
| window.sessionCount | sessionCount | direct | Matched record count |
| window.avgHandsPerDay | avgHandsPerDay | direct | Computed average |
| window.winrateBbPer100 | winrateBbPer100 | direct \| null | null when unavailable |
