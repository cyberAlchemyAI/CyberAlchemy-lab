---
id: financial-settlement
feature: financial-settlement
title: Financial Settlement Domain
summary: Structural concepts used by settlement generation.
status: implemented
pillar: finance
domain: financial-settlement-domain
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

# Domain: Financial Settlement

## Value Objects

### SettlementResult

| Field               | Type    | Constraint    |
| ------------------- | ------- | ------------- |
| playerId            | string  | required      |
| periodStart         | string  | valid date    |
| periodEnd           | string  | valid date    |
| totalProfit         | integer | derived sum   |
| totalRakeback       | integer | derived sum   |
| netProfit           | integer | informational |
| previousMakeup      | integer | non-negative  |
| newMakeup           | integer | non-negative  |
| playerProfitShare   | integer | non-negative  |
| playerRakebackShare | integer | non-negative  |
| totalPayout         | integer | non-negative  |

**Equality:** Two instances are equal when all fields are equal for the same player and period.

---

## Enums

### SettlementTransactionType

| Value          | Description                      |
| -------------- | -------------------------------- |
| MAKEUP_APPLIED | Debt reduction transaction entry |
| PAYOUT         | Player payout transaction entry  |
