---
id: player-makeup
feature: player-makeup
title: Player Makeup Domain
summary: Structural makeup concepts and policy shape.
status: implemented
pillar: finance
domain: player-makeup-domain
audience:
  - developers
priority: p1
lang: en
owners:
  - finance-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
includes: []
---

# Domain: Player Makeup

## Value Objects

### MakeupBalance

| Field  | Type    | Constraint    |
| ------ | ------- | ------------- |
| amount | integer | `amount >= 0` |

**Equality:** same amount means equal debt value.

### MakeupPolicy

| Field               | Type    | Constraint        |
| ------------------- | ------- | ----------------- |
| applyProfitFirst    | boolean | required          |
| applyRakebackSecond | boolean | required          |
| playerRakebackShare | number  | `0 <= value <= 1` |

**Default policy values:**

| Field               | Default |
| ------------------- | ------- |
| applyProfitFirst    | true    |
| applyRakebackSecond | true    |
| playerRakebackShare | 0.5     |

**Scope:**

- Effective policy can be resolved per player.
- When no player-specific override is available, default values above are authoritative.

---

## Enums

### MakeupOperationType

| Value    | Description                          |
| -------- | ------------------------------------ |
| increase | Adds debt by amount                  |
| decrease | Removes debt down to zero floor      |
| set      | Replaces debt by non-negative amount |
