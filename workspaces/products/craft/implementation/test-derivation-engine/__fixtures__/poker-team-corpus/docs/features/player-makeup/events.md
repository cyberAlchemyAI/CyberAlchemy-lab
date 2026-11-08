---
id: player-makeup
feature: player-makeup
title: Player Makeup Events
summary: Domain events produced by makeup adjustments and debt application.
status: implemented
pillar: finance
domain: player-makeup-events
audience:
  - developers
priority: p2
lang: en
owners:
  - finance-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - operations.md
includes: []
---

# Events: Player Makeup

## MakeupAdjusted

**Produced by:** [AdjustPlayerMakeup](operations.md#adjustplayermakeup)
**Triggers transition:** [MakeupDebtState](states.md#makeupdebtstate)

### Payload

| Field          | Type    | Description           |
| -------------- | ------- | --------------------- |
| playerId       | string  | Player id             |
| previousMakeup | integer | Debt before operation |
| currentMakeup  | integer | Debt after operation  |
| operation      | string  | increase/decrease/set |
| amount         | integer | Normalized amount     |
| delta          | integer | Signed difference     |

### Consumed by

| Consumer      | Action                          |
| ------------- | ------------------------------- |
| finance audit | Track manual debt interventions |

## MakeupApplied

**Produced by:** financial-settlement.GenerateSettlement
**Triggers transition:** [MakeupDebtState](states.md#makeupdebtstate)
**Emission constraint:** idempotent per `(playerId, date)` settlement period.

### Payload

| Field    | Type    | Description              |
| -------- | ------- | ------------------------ |
| playerId | string  | Player id                |
| amount   | integer | Amount applied from debt |
| date     | string  | Settlement period end    |

### Consumed by

| Consumer             | Action                         |
| -------------------- | ------------------------------ |
| makeup history query | Include debt consumption event |

### Idempotency Rule

- For repeated settlement execution with same player and period end date, `MAKEUP_APPLIED` MUST NOT be duplicated.

### Deduplication Identity

- Deduplication key for `MAKEUP_APPLIED`: `(type=MAKEUP_APPLIED, playerId, date)`.
- Storage or event-bus publishing MUST enforce uniqueness on this key.
- If duplicate production is attempted with same key, existing event MUST be reused (or no-op) without changing business outcome.
