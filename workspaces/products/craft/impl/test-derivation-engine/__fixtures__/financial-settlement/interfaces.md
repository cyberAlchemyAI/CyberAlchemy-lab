---
id: financial-settlement
feature: financial-settlement
title: Financial Settlement Interfaces
summary: API and internal contracts for settlement generation.
status: implemented
pillar: platform
domain: financial-settlement-interfaces
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
  - operations.md
includes: []
---

# Interfaces: Financial Settlement

## External: SettlementAPI (REST)

### POST /settlements

**Exposes:** [GenerateSettlement](operations.md#generatesettlement)  
**Auth:** bearer token + permission `financial-settlement.write.generateSettlement`

**Request:**

| Field     | Type   | Maps To                      |
| --------- | ------ | ---------------------------- |
| playerId  | string | GenerateSettlement.playerId  |
| startDate | string | GenerateSettlement.startDate |
| endDate   | string | GenerateSettlement.endDate   |

**Responses:**

| Status | Condition               | Body             |
| ------ | ----------------------- | ---------------- |
| 200    | Success                 | SettlementResult |
| 400    | Missing required fields | Error payload    |
| 404    | Player not found        | Error payload    |
| 500    | Unexpected error        | Error payload    |

### GET /settlements/preview

**Exposes:** Settlement projection preview (read-only)
**Auth:** bearer token + permission `financial-settlement.read.getSettlementPreview`

**Request query:**

| Field     | Type   | Required | Description             |
| --------- | ------ | -------- | ----------------------- |
| playerId  | string | yes      | Target player ID        |
| startDate | string | yes      | Period start (ISO date) |
| endDate   | string | yes      | Period end (ISO date)   |

**Responses:**

| Status | Condition               | Body                  |
| ------ | ----------------------- | --------------------- |
| 200    | Success                 | Settlement projection |
| 400    | Missing required params | Error payload         |
| 401    | Missing/invalid token   | Error payload         |
| 403    | Missing permission      | Error payload         |
| 404    | Player not found        | Error payload         |
| 500    | Unexpected error        | Error payload         |

## Internal: SettlementModule Interface

| Method                                           | Maps To                      | Description                                   |
| ------------------------------------------------ | ---------------------------- | --------------------------------------------- |
| generateSettlement(playerId, startDate, endDate) | GenerateSettlement operation | Computes and persists settlement side-effects |
