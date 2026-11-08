---
id: player-progression
feature: player-progression
title: Player Progression Operations
summary: Eligibility evaluation rules, formulas, and deterministic outputs for progression checks.
status: implemented
pillar: operations
domain: player-progression-operations
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
  - queries.md
includes: []
---

# Operations: Player Progression

> **Capabilities using this aspect:** [Check Progression](SPEC.md#check-progression)

## Domain Policy Ownership

Progression eligibility policy is owned by the domain layer, not by use-case orchestration.

- Domain service authority: [`backend/src/domain/progression/progression-policy.service.ts`](../../../backend/src/domain/progression/progression-policy.service.ts)
- Use-case orchestrator: [`backend/src/use-cases/progression/check-progression.ts`](../../../backend/src/use-cases/progression/check-progression.ts)

## CheckProgression

**Type:** Operation (read-only evaluation)
**Actor:** Operations user
**Triggers:** GET /players/:id/progression?period=BI_WEEKLY|MONTHLY

### Input

| Field      | Type    | Required | Description           |
| ---------- | ------- | -------- | --------------------- |
| playerId   | string  | yes      | Target player id      |
| periodDays | integer | no       | 15 or 30 (default 15) |

### Rules

| ID  | Rule                        | Formal                               |
| --- | --------------------------- | ------------------------------------ |
| R1  | player must exist           | `exists(Player.id == playerId)`      |
| R2  | periodDays must be 15 or 30 | `periodDays in {15, 30}`             |
| R3  | minimum average hands       | `avgHands >= 1000`                   |
| R4  | minimum winrate for 15 days | `periodDays == 15 => winrate >= 7.5` |
| R5  | minimum winrate for 30 days | `periodDays == 30 => winrate >= 5.0` |
| R6  | empty period stats          | `count(relevantStats) == 0 => winrate = 0 and avgHands = 0` |

### Calculations

| ID  | Calculation        | Formula                                    |
| --- | ------------------ | ------------------------------------------ |
| C1  | Relevant stats set | `stats where date >= now - periodDays`     |
| C2  | Average hands      | `avgHands = sum(hands) / periodDays`       |
| C3  | BB value by limit  | `bbValue = buyIn(currentLimit) / 100`      |
| C4  | Winrate bb/100     | `winrate = (totalProfit / bbValue) / (totalHands / 100)` |

### Postconditions

| ID  | Class                 | Guarantee                                                        | Formal Assertion                                                                                     | Traceability |
| --- | --------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------ |
| P1  | Integration Guarantee | Returns deterministic eligibility object.                        | `result = f(playerId, periodDays, relevantStats) and deterministic(result)`                         | [GetProgressionStatus](queries.md#getprogressionstatus), [GET /players/:id/progression](interfaces.md#get-playersidprogression) |
| P2  | Integration Guarantee | Returns reason with threshold comparison when not eligible.      | `eligibleForPromotion = false -> reason includes thresholdComparison(avgHands, winrate, periodDays)` | [PromotionEligibilityState](states.md#promotioneligibilitystate), [GetProgressionStatus](queries.md#getprogressionstatus) |
| P3  | Integration Guarantee | Emits [ProgressionChecked](events.md#progressionchecked) when evaluation completes. | `emit(ProgressionChecked where playerId = input.playerId and period in {BI_WEEKLY, MONTHLY})`      | [ProgressionChecked](events.md#progressionchecked), [produces semantics](../../../domainspec/RELATIONSHIPS.md#produces--operation--event) |

### Error States

| Condition        | Result                       |
| ---------------- | ---------------------------- |
| Player not found | 404 `PLAYER_NOT_FOUND`      |
| Invalid period   | 400 `VALIDATION_ERROR`      |
