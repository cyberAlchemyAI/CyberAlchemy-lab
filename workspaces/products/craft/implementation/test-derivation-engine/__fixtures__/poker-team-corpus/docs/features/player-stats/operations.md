---
id: player-stats
feature: player-stats
title: Player Stats Tracking Operations
summary: Mutation contracts for recording and correcting tracked player stats.
status: implemented
pillar: operations
domain: player-stats-operations
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-30
dependencies:
  - SPEC.md
  - domain.md
  - states.md
  - events.md
  - interfaces.md
  - mappings.md
includes: []
---

# Operations: Player Stats Tracking

> **Capabilities using this aspect:** [Record Player Stats](SPEC.md#record-player-stats)

## RecordPlayerStats

**Type:** Operation (mutation)
**Actor:** Operations user or ingestion service
**Triggers:** `POST /player-stats`

### Input

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| playerId | string | yes | Target player id |
| statDate | string | yes | Snapshot date (`YYYY-MM-DD`) |
| hands | integer | yes | Hands played |
| profit | number | yes | Profit amount |
| rakeback | number | yes | Rakeback amount |
| rake | number | yes | Rake paid |
| closingBankroll | number | yes | End-of-day bankroll balance |
| sessionDuration | integer | yes | Session time in minutes |
| sourceType | [StatsSourceType](domain.md#statssourcetype) | yes | Data source category |

### Rules

| ID | Rule | Formal |
| -- | ---- | ------ |
| R1 | Player must exist | `exists(player-management.Player.id == playerId)` |
| R2 | statDate must be valid date | `isValidDate(statDate) = true` |
| R3 | Hands must be non-negative integer | `isInteger(hands) and hands >= 0` |
| R4 | sourceType must be supported | `sourceType in {MANUAL, IMPORT, API}` |
| R5 | One snapshot identity per player/date | `unique(playerId, statDate)` |
| R6 | Correction requires effective change | `existing != null => atLeastOneFieldChanged = true` |
| R7 | Rake must be non-negative | `rake >= 0` |
| R8 | Session duration must be non-negative integer | `isInteger(sessionDuration) and sessionDuration >= 0` |

### Calculations

| ID | Calculation | Formula |
| -- | ----------- | ------- |
| C1 | Snapshot key | `snapshotKey = playerId + ':' + statDate` |
| C2 | Record status | `status = RECORDED if existing == null else CORRECTED` |

### State Transition

`[PlayerStatsSnapshot](domain.md#playerstatssnapshot): RECORDED -> CORRECTED`

### Postconditions

| ID  | Class                 | Guarantee                                                     | Formal Assertion                                                                 | Traceability |
| --- | --------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------ |
| P1  | Persistence Guarantee | A snapshot exists for `playerId + statDate` with current values. | `exists(PlayerStatsSnapshot where playerId = input.playerId and statDate = input.statDate)` | [PlayerStatsSnapshot](domain.md#playerstatssnapshot), [RecordStatsRequestToInput](mappings.md#recordstatsrequesttoinput) |
| P2  | Integration Guarantee | New records produce [PlayerStatsRecorded](events.md#playerstatsrecorded). | `(existing == null) -> emit(PlayerStatsRecorded)`                                | [PlayerStatsRecorded](events.md#playerstatsrecorded), [produces semantics](../../../domainspec/RELATIONSHIPS.md#produces--operation--event) |
| P3  | Integration Guarantee | Corrections produce [PlayerStatsCorrected](events.md#playerstatscorrected). | `(existing != null and atLeastOneFieldChanged = true) -> emit(PlayerStatsCorrected)` | [PlayerStatsCorrected](events.md#playerstatscorrected), [produces semantics](../../../domainspec/RELATIONSHIPS.md#produces--operation--event) |

### Error States

| Condition | Result |
| --------- | ------ |
| R1 violated | `PLAYER_NOT_FOUND` |
| R2, R3, R4 violated | `VALIDATION_ERROR` |
| R6 violated | `NO_CHANGES_DETECTED` |
| Persistence failure | `INTERNAL_ERROR` |
