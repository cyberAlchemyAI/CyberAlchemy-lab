---
id: player-stats
feature: player-stats
title: Player Stats Tracking Interfaces
summary: REST contracts for writing and reading player stats tracking data.
status: implemented
pillar: platform
domain: player-stats-interfaces
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - operations.md
  - queries.md
includes: []
---

# Interfaces: Player Stats Tracking

> **Capabilities using this aspect:** [Record Player Stats](SPEC.md#record-player-stats) · [Get Player Stats History](SPEC.md#get-player-stats-history) · [Get Player Stats Window](SPEC.md#get-player-stats-window)

## External: PlayerStatsAPI (REST)

### POST /player-stats

**Exposes:** [RecordPlayerStats](operations.md#recordplayerstats)
**Auth:** requirePermission(`player-stats.write.recordPlayerStats`)

**Request:**

| Field | Type | Maps To |
| ----- | ---- | ------- |
| playerId | string | [RecordPlayerStats](operations.md#recordplayerstats).playerId |
| statDate | string | [RecordPlayerStats](operations.md#recordplayerstats).statDate |
| hands | integer | [RecordPlayerStats](operations.md#recordplayerstats).hands |
| profit | number | [RecordPlayerStats](operations.md#recordplayerstats).profit |
| rakeback | number | [RecordPlayerStats](operations.md#recordplayerstats).rakeback |
| rake | number | [RecordPlayerStats](operations.md#recordplayerstats).rake |
| closingBankroll | number | [RecordPlayerStats](operations.md#recordplayerstats).closingBankroll |
| sessionDuration | integer | [RecordPlayerStats](operations.md#recordplayerstats).sessionDuration |
| sourceType | string | [RecordPlayerStats](operations.md#recordplayerstats).sourceType |

**Responses:**

| Status | Condition | Body |
| ------ | --------- | ---- |
| 200 | Recorded or corrected | Snapshot summary |
| 400 | Validation error | Structured error |
| 401 | Missing/invalid auth | Structured error |
| 403 | Missing permission | Structured error |
| 404 | Player not found | Structured error |
| 500 | Unexpected error | Structured error |

### GET /player-stats/:playerId/history

**Exposes:** [GetPlayerStatsHistory](queries.md#getplayerstatshistory)
**Auth:** requirePermission(`player-stats.read.getPlayerStatsHistory`)

**Responses:**

| Status | Condition | Body |
| ------ | --------- | ---- |
| 200 | Success | History page |
| 400 | Invalid filters | Structured error |
| 401 | Missing/invalid auth | Structured error |
| 403 | Missing permission | Structured error |
| 500 | Unexpected error | Structured error |

### GET /player-stats/:playerId/window

**Exposes:** [GetPlayerStatsWindow](queries.md#getplayerstatswindow)
**Auth:** requirePermission(`player-stats.read.getPlayerStatsWindow`)

**Responses:**

| Status | Condition | Body |
| ------ | --------- | ---- |
| 200 | Success | Aggregate window projection |
| 400 | Invalid date window | Structured error |
| 401 | Missing/invalid auth | Structured error |
| 403 | Missing permission | Structured error |
| 500 | Unexpected error | Structured error |
