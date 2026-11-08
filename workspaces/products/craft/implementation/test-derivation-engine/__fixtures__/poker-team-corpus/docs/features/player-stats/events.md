---
id: player-stats
feature: player-stats
title: Player Stats Tracking Events
summary: Event contracts for recorded and corrected player stats snapshots.
status: implemented
pillar: operations
domain: player-stats-events
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
  - states.md
includes: []
---

# Events: Player Stats Tracking

> **Capabilities using this aspect:** [Record Player Stats](SPEC.md#record-player-stats)

## PlayerStatsRecorded

**Produced by:** [RecordPlayerStats](operations.md#recordplayerstats)
**Triggers transition:** [PlayerStatsRecordLifecycle](states.md#playerstatsrecordlifecycle)

### Payload

| Field | Type | Description |
| ----- | ---- | ----------- |
| snapshotId | string | New snapshot id |
| playerId | string | Player identity |
| statDate | string | Snapshot date |
| occurredAt | datetime | Event timestamp |

### Consumed by

| Consumer | Action |
| -------- | ------ |
| player-management overview projection | Include new stat in rolling calculations |
| financial-settlement input service | Include stat in settlement windows |

## PlayerStatsCorrected

**Produced by:** [RecordPlayerStats](operations.md#recordplayerstats)
**Triggers transition:** [PlayerStatsRecordLifecycle](states.md#playerstatsrecordlifecycle)

### Payload

| Field | Type | Description |
| ----- | ---- | ----------- |
| snapshotId | string | Corrected snapshot id |
| playerId | string | Player identity |
| statDate | string | Corrected date |
| changedFields | string[] | Field names changed in correction |
| occurredAt | datetime | Event timestamp |

### Consumed by

| Consumer | Action |
| -------- | ------ |
| player-management overview projection | Recompute affected windows |
| analytics export process | Mark correction delta for audit trail |
