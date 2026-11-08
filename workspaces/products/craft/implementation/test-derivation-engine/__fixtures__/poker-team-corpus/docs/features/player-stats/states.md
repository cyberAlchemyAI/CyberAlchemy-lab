---
id: player-stats
feature: player-stats
title: Player Stats Tracking States
summary: State machine for player stats snapshot lifecycle.
status: implemented
pillar: operations
domain: player-stats-states
audience:
  - developers
priority: p2
lang: en
owners:
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - operations.md
includes: []
---

# States: Player Stats Tracking

> **Capabilities using this aspect:** [Record Player Stats](SPEC.md#record-player-stats)

## PlayerStatsRecordLifecycle

```mermaid
stateDiagram-v2
  [*] --> RECORDED
  RECORDED --> CORRECTED : PlayerStatsCorrected
  CORRECTED --> CORRECTED : PlayerStatsCorrected
```

### Transition Table

| From | Event | To | Guard | Effect |
| ---- | ----- | -- | ----- | ------ |
| [new] | PlayerStatsRecorded | RECORDED | Valid payload and player exists | Snapshot persisted |
| RECORDED | PlayerStatsCorrected | CORRECTED | At least one value changed | Snapshot updated |
| CORRECTED | PlayerStatsCorrected | CORRECTED | At least one value changed | Snapshot updated |

### Invariants

| ID | Invariant | Formal |
|----|-----------|--------|
| I1 | One snapshot per day identity | `unique(playerId, statDate)` |
| I2 | Hands are always non-negative | `hands >= 0` |
