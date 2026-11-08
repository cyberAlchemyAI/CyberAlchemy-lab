---
id: player-makeup
feature: player-makeup
title: Player Makeup Operations
summary: Makeup mutation operation and policy behaviors.
status: implemented
pillar: finance
domain: player-makeup-operations
audience:
  - developers
priority: p1
lang: en
owners:
  - finance-core
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

# Operations: Player Makeup

## AdjustPlayerMakeup

**Type:** Operation (mutation)  
**Actor:** Authorized operations user  
**Triggers:** PATCH /players/:id/makeup

### Input

| Field      | Type                    | Required | Description                              |
| ---------- | ----------------------- | -------- | ---------------------------------------- |
| playerId   | string                  | yes      | Target player                            |
| operation  | increase\|decrease\|set | yes      | Adjustment mode                          |
| amount     | number                  | yes      | Adjustment amount                        |
| reasonCode | string                  | yes      | Caller-provided reason code for mutation |
| date       | string                  | no       | Optional effective date                  |

### Server-Derived Audit Metadata

The following fields are required for mutation audit traceability and are derived by the backend from authenticated request context:

- `actorId`
- `requestId`
- `sourceChannel`

### Rules

| ID  | Rule                                   | Formal                                 |
| --- | -------------------------------------- | -------------------------------------- |
| R1  | player must exist                      | `exists(Player.id == playerId)`        |
| R2  | amount must be finite and non-negative | `isFinite(amount) and amount >= 0`     |
| R3  | operation must be valid                | `operation in {increase,decrease,set}` |

### Calculations

| ID  | Calculation               | Formula                                   |
| --- | ------------------------- | ----------------------------------------- |
| C1  | amount normalization      | `normalized = floor(amount + 0.5)`        |
| C2  | resulting debt (increase) | `current = previous + normalized`         |
| C3  | resulting debt (decrease) | `current = max(0, previous - normalized)` |
| C4  | resulting debt (set)      | `current = max(0, normalized)`            |
| C5  | signed delta              | `delta = current - previous`              |

### Rounding Rule

Because `amount >= 0` is enforced by rule `R2`, normalization uses deterministic half-up rounding for non-negative values.

| Input amount | Normalized |
| ------------ | ---------- |
| 0.49         | 0          |
| 0.50         | 1          |
| 1.49         | 1          |
| 1.50         | 2          |

### State Transition

`MakeupDebtState: Settled <-> InDebt`

### Postconditions

| ID  | Class                 | Guarantee                                                   | Formal Assertion                                                                                                      | Traceability |
| --- | --------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------ |
| P1  | Persistence Guarantee | Player makeup is persisted with new non-negative value.     | `persistedMakeup = current and persistedMakeup >= 0`                                                                 | [MakeupBalance](domain.md#makeupbalance), [MakeupDebtState](states.md#makeupdebtstate) |
| P2  | Audit Guarantee       | MAKEUP_ADJUSTMENT transaction is created only when `delta != 0`. | `(delta != 0) -> create tx(type=MAKEUP_ADJUSTMENT, playerId=input.playerId, amount=abs(delta)) and (delta = 0) -> no tx(type=MAKEUP_ADJUSTMENT)` | [MakeupAdjusted](events.md#makeupadjusted), [PATCH /players/:id/makeup](interfaces.md#patch-playersidmakeup) |

### Error States

| Condition           | Result               |
| ------------------- | -------------------- |
| Player not found    | 404 domain error     |
| Invalid amount      | 400 validation error |
| Persistence failure | 500 internal error   |

---

## SetPlayerMakeupPolicy

**Type:** Operation (mutation)  
**Actor:** Authorized operations user  
**Triggers:** PATCH /players/:id/makeup/policy

### Input

| Field               | Type    | Required | Description                         |
| ------------------- | ------- | -------- | ----------------------------------- |
| playerId            | string  | yes      | Target player                       |
| applyProfitFirst    | boolean | yes      | Apply profits to debt before payout |
| applyRakebackSecond | boolean | yes      | Apply rakeback to debt after profit |
| playerRakebackShare | number  | yes      | Player's rakeback share ratio       |

### Rules

| ID  | Rule                        | Formal                                                                                                                |
| --- | --------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| R1  | player must exist           | `exists(Player.id == playerId)`                                                                                       |
| R2  | validate policy shape       | `typeof applyProfitFirst == boolean && typeof applyRakebackSecond == boolean && typeof playerRakebackShare == number` |
| R3  | clamp rakebackShare to 0..1 | `playerRakebackShare = clamp(playerRakebackShare, 0, 1)`                                                              |

### Postconditions

| ID  | Class                 | Guarantee                                                   | Formal Assertion                                                                 | Traceability |
| --- | --------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------ |
| P1  | Persistence Guarantee | Player's `makeupPolicy` is persisted with the new policy values. | `persisted.makeupPolicy.applyProfitFirst = applyProfitFirst and persisted.makeupPolicy.applyRakebackSecond = applyRakebackSecond` | [MakeupPolicy](domain.md#makeuppolicy), [SetPolicyRequestToInput](mappings.md#setpolicyrequesttoinput) |
| P2  | Persistence Guarantee | `playerRakebackShare` is clamped to `[0, 1]` before persistence. | `persisted.makeupPolicy.playerRakebackShare = clamp(input.playerRakebackShare, 0, 1)` | [MakeupPolicy](domain.md#makeuppolicy), [SetPolicyRequestToInput](mappings.md#setpolicyrequesttoinput) |

### Error States

| Condition            | Result               |
| -------------------- | -------------------- |
| Player not found     | 404 domain error     |
| Invalid policy shape | 400 validation error |
| Persistence failure  | 500 internal error   |
