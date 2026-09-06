---
id: financial-settlement
feature: financial-settlement
title: Financial Settlement Events
summary: Domain events produced by settlement generation.
status: implemented
pillar: finance
domain: financial-settlement-events
audience:
  - developers
priority: p2
lang: en
owners:
  - finance-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
  - operations.md
includes: []
---

# Events: Financial Settlement

## SettlementGenerated

**Produced by:** [GenerateSettlement](operations.md#generatesettlement)
**Implementation note:** emitted through `SettlementEventHandler` from `backend/src/use-cases/financial-settlement/generate-settlement.ts` and typed in `backend/src/domain/settlement/settlement.events.ts`.

### Payload

| Field          | Type    | Description            |
| -------------- | ------- | ---------------------- |
| playerId       | string  | Player id              |
| periodStart    | string  | Start date             |
| periodEnd      | string  | End date               |
| totalProfit    | integer | Total profit           |
| totalRakeback  | integer | Total rakeback         |
| previousMakeup | integer | Debt before settlement |
| newMakeup      | integer | Debt after settlement  |
| totalPayout    | integer | Payout amount          |

### Consumed by

| Consumer          | Action                   |
| ----------------- | ------------------------ |
| finance reporting | Save settlement snapshot |

## PayoutCreated

**Produced by:** [GenerateSettlement](operations.md#generatesettlement)
**Implementation note:** emitted when a `PAYOUT` ledger transaction is created (idempotent per player/date), from `backend/src/use-cases/financial-settlement/generate-settlement.ts`.

### Payload

| Field    | Type    | Description           |
| -------- | ------- | --------------------- |
| playerId | string  | Player id             |
| date     | string  | Settlement period end |
| amount   | integer | Payout amount         |

### Consumed by

| Consumer          | Action                  |
| ----------------- | ----------------------- |
| payout operations | Reconcile payout ledger |
