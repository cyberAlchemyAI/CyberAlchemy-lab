---
id: player-makeup
feature: player-makeup
title: Player Makeup States
summary: Debt state machine for makeup lifecycle.
status: implemented
pillar: finance
domain: player-makeup-states
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

# State Machines: Player Makeup

## MakeupDebtState

```mermaid
stateDiagram-v2
    [*] --> Settled
    Settled --> InDebt : MakeupAdjusted(increase|set>0)
    InDebt --> InDebt : MakeupAdjusted(increase)
    InDebt --> InDebt : MakeupAdjusted(decrease with remaining debt)
    InDebt --> Settled : MakeupAdjusted(decrease to zero)
    InDebt --> Settled : MakeupApplied(settlement consumes all debt)
```

### Transition Table

| From    | Event          | To      | Guard                           | Effect         |
| ------- | -------------- | ------- | ------------------------------- | -------------- |
| Settled | MakeupAdjusted | InDebt  | operation creates amount > 0    | debt increases |
| InDebt  | MakeupAdjusted | InDebt  | result > 0                      | debt updated   |
| InDebt  | MakeupAdjusted | Settled | result == 0                     | debt cleared   |
| InDebt  | MakeupApplied  | Settled | applied amount >= previous debt | debt cleared   |

### Invalid Transition Table

| From    | Event          | Guard Not Satisfied                | Expected Result                  |
| ------- | -------------- | ---------------------------------- | -------------------------------- |
| Settled | MakeupApplied  | n/a                                | reject transition, remain Settled |
| Settled | MakeupAdjusted | result == 0                        | reject transition, remain Settled |
| InDebt  | MakeupApplied  | applied amount < previous debt     | reject transition, remain InDebt  |

### Invariants

| ID  | Invariant                              | Formal                                     |
| --- | -------------------------------------- | ------------------------------------------ |
| I1  | Debt is never negative                 | `makeup >= 0`                              |
| I2  | No adjustment event when delta is zero | `delta == 0 => !create(MAKEUP_ADJUSTMENT)` |
