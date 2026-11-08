---
id: financial-settlement
feature: financial-settlement
title: Financial Settlement States
summary: State machine for settlement execution and idempotent side-effects.
status: implemented
pillar: finance
domain: financial-settlement-states
audience:
  - developers
  - finance
priority: p1
lang: en
owners:
  - finance-core
  - backend-core
updatedAt: 2026-04-17
dependencies:
  - SPEC.md
  - operations.md
  - events.md
includes: []
---

# States: Financial Settlement

## SettlementExecutionState

```mermaid
stateDiagram-v2
  [*] --> VALIDATED
  VALIDATED --> COMPUTED : GenerateSettlement
  COMPUTED --> SIDE_EFFECTS_PERSISTED : SettlementGenerated
  SIDE_EFFECTS_PERSISTED --> COMPLETED : PayoutCreated|no-payout
  COMPLETED --> [*]
```

### Transition Table

| From | Event | To | Guard | Effect |
| ---- | ----- | -- | ----- | ------ |
| [new] | GenerateSettlement | VALIDATED | Required input fields present and player exists | Request accepted for execution |
| VALIDATED | GenerateSettlement | COMPUTED | Stats and policy dependencies loaded | Totals and policy result computed |
| COMPUTED | SettlementGenerated | SIDE_EFFECTS_PERSISTED | Computed result is deterministic | Player makeup and transaction side-effects persisted |
| SIDE_EFFECTS_PERSISTED | PayoutCreated or no-payout | COMPLETED | PAYOUT dedupe rule is satisfied | Response finalized for API caller |

### Invariants

| ID | Invariant | Formal |
| --- | --------- | ------ |
| I1 | Makeup debt cannot become negative | `newMakeup >= 0` |
| I2 | Settlement side-effects are idempotent by period end | `count(tx[type in {MAKEUP_APPLIED, PAYOUT} where playerId = input.playerId and date = endDate]) <= 1 per type` |
