---
id: financial-settlement
feature: financial-settlement
title: Financial Settlement Mappings
summary: Data transformations between API, use-case, and output DTOs.
status: implemented
pillar: platform
domain: financial-settlement-mappings
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

# Mappings: Financial Settlement

## SettlementRequestToInput

**From:** API Request  
**To:** GenerateSettlement input  
**Direction:** Inbound

### Field Mapping

| Source Field   | Target Field | Transform | Notes    |
| -------------- | ------------ | --------- | -------- |
| body.playerId  | playerId     | direct    | Required |
| body.startDate | startDate    | direct    | Required |
| body.endDate   | endDate      | direct    | Required |

### Validation

| Field     | Validation       | On Failure   |
| --------- | ---------------- | ------------ |
| playerId  | non-empty string | 400 response |
| startDate | non-empty string | 400 response |
| endDate   | non-empty string | 400 response |

## SettlementResultToResponse

**From:** SettlementResult  
**To:** API Response  
**Direction:** Outbound

### Field Mapping

| Source Field        | Target Field | Transform | Notes                       |
| ------------------- | ------------ | --------- | --------------------------- |
| SettlementResult.\* | response.\*  | direct    | DTO mirrors use-case result |
