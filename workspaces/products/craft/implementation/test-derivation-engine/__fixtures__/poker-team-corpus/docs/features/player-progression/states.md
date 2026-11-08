---
id: player-progression
feature: player-progression
title: Player Progression States
summary: State model for progression eligibility evaluation lifecycle.
status: implemented
pillar: operations
domain: player-progression-states
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-17
dependencies:
  - SPEC.md
  - operations.md
  - events.md
includes: []
---

# States: Player Progression

## ProgressionEvaluationLifecycle

```mermaid
stateDiagram-v2
  [*] --> REQUESTED
  REQUESTED --> EVALUATED : CheckProgression
  EVALUATED --> [*]
```

### Transition Table

| From | Event | To | Guard | Effect |
| ---- | ----- | -- | ----- | ------ |
| [new] | CheckProgressionRequested | REQUESTED | Valid player id and allowed period | Evaluation pipeline starts |
| REQUESTED | ProgressionChecked | EVALUATED | Stats window and policy evaluation completed | Deterministic progression status returned |

## PromotionEligibilityState

```mermaid
stateDiagram-v2
  [*] --> NOT_ELIGIBLE
  NOT_ELIGIBLE --> ELIGIBLE : ProgressionChecked(eligible=true)
  ELIGIBLE --> NOT_ELIGIBLE : ProgressionChecked(eligible=false)
```

### Invariants

| ID | Invariant | Formal |
| --- | --------- | ------ |
| I1 | Eligibility is derived only from evaluated period metrics | `eligibleForPromotion = f(avgHands, winrate, periodDays)` |
| I2 | Returned period label matches periodDays input | `(periodDays = 15 -> period = BI_WEEKLY) and (periodDays = 30 -> period = MONTHLY)` |
