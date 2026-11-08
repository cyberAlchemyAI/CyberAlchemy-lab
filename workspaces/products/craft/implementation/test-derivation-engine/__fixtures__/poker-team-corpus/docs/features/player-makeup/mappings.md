---
id: player-makeup
feature: player-makeup
title: Player Makeup Mappings
summary: Transformations for makeup API payloads and history responses.
status: implemented
pillar: finance
domain: player-makeup-mappings
audience:
  - developers
priority: p2
lang: en
owners:
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - interfaces.md
includes: []
---

# Mappings: Player Makeup

## AdjustMakeupRequestToInput

**From:** API Request  
**To:** AdjustPlayerMakeup input  
**Direction:** Inbound

### Field Mapping

| Source Field   | Target Field | Transform | Notes                         |
| -------------- | ------------ | --------- | ----------------------------- |
| params.id      | playerId     | direct    | Required                      |
| body.operation | operation    | direct    | Must be one of allowed values |
| body.amount    | amount       | direct    | Must be number                |

### Validation

| Field     | Validation             | On Failure           |
| --------- | ---------------------- | -------------------- |
| operation | increase/decrease/set  | 400 VALIDATION_ERROR |
| amount    | finite number and >= 0 | 400 VALIDATION_ERROR |

## MakeupHistoryTransactionToDto

**From:** Transaction[]  
**To:** PlayerMakeupHistoryDto.entries[]  
**Direction:** Outbound

### Field Mapping

| Source Field          | Target Field | Transform | Notes                                       |
| --------------------- | ------------ | --------- | ------------------------------------------- |
| transaction.id        | id           | direct    |                                             |
| transaction.type      | type         | direct    | filtered for makeup-related types           |
| transaction.amount    | amount       | direct    | signed for adjustment, positive for applied |
| transaction.date      | date         | direct    |                                             |
| transaction.createdAt | createdAt    | direct    |                                             |

### Ordering Transform

`entries[] = sortBy(transaction.date desc, transaction.createdAt desc)`

---

## SetPolicyRequestToInput

**From:** API Request  
**To:** SetPlayerMakeupPolicy input  
**Direction:** Inbound

### Field Mapping

| Source Field             | Target Field        | Transform | Notes                   |
| ------------------------ | ------------------- | --------- | ----------------------- |
| params.id                | playerId            | direct    | Required                |
| body.applyProfitFirst    | applyProfitFirst    | direct    | Must be boolean         |
| body.applyRakebackSecond | applyRakebackSecond | direct    | Must be boolean         |
| body.playerRakebackShare | playerRakebackShare | direct    | Must be number, clamped |

### Validation

| Field               | Validation    | On Failure           |
| ------------------- | ------------- | -------------------- |
| applyProfitFirst    | boolean       | 400 VALIDATION_ERROR |
| applyRakebackSecond | boolean       | 400 VALIDATION_ERROR |
| playerRakebackShare | finite number | 400 VALIDATION_ERROR |
