---
id: player-progression
feature: player-progression
title: Player Progression Domain
summary: Core domain concepts for progression evaluation.
status: implemented
pillar: operations
domain: player-progression-domain
audience:
  - developers
priority: p2
lang: en
owners:
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
includes: []
---

# Domain: Player Progression

## ProgressionResult

**Type:** Value Object

Represents the outcome of a progression eligibility check for a single player.

| Field        | Type                  | Description                                     |
| ------------ | --------------------- | ----------------------------------------------- |
| playerId     | string                | Player being evaluated                          |
| eligible     | boolean               | Whether the player meets all promotion criteria |
| currentLimit | string                | Player's current limit level                    |
| nextLimit    | string \| null        | Target limit if eligible, null otherwise        |
| criteria     | CriteriaCheckResult[] | Per-rule pass/fail breakdown                    |
| evaluatedAt  | datetime              | Timestamp of evaluation                         |

## ProgressionCriteria

**Type:** Value Object

Configurable thresholds that define promotion readiness for a given limit level.

| Field           | Type    | Description                                  |
| --------------- | ------- | -------------------------------------------- |
| fromLimit       | string  | Current limit level this criteria applies to |
| toLimit         | string  | Target limit on promotion                    |
| minHands        | integer | Minimum total hands in observation window    |
| minWinrateBb100 | number  | Minimum winrate in BB/100                    |
| minDays         | integer | Minimum days with recorded sessions          |
| observationDays | integer | Rolling window for evaluation (e.g., 30)     |
