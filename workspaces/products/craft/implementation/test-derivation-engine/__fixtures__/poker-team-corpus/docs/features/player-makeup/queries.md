---
id: player-makeup
feature: player-makeup
title: Player Makeup Queries
summary: Read models for current makeup state, history, and policy.
status: implemented
pillar: finance
domain: player-makeup-queries
audience:
  - developers
  - operations
priority: p1
lang: en
owners:
  - finance-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
includes: []
---

# Queries: Player Makeup

## GetPlayerMakeup

**Type:** Query (read-only)  
**Actor:** Authorized operations user

### Input

| Field    | Type   | Required | Description   |
| -------- | ------ | -------- | ------------- |
| playerId | string | yes      | Target player |

### Output

| Field         | Type         | Source          | Description              |
| ------------- | ------------ | --------------- | ------------------------ |
| playerId      | string       | Player.id       | Player id                |
| currentMakeup | integer      | Player.makeup   | Current debt             |
| policy        | MakeupPolicy | resolved policy | Policy currently applied |

### Reads From

| Entity | Relationship | Fields Used |
| ------ | ------------ | ----------- |
| Player | queries      | id, makeup  |

## GetPlayerMakeupHistory

**Type:** Query (read-only)
**Actor:** Authorized operations user

### Input

| Field    | Type   | Required | Description                           |
| -------- | ------ | -------- | ------------------------------------- |
| playerId | string | yes      | Target player                         |
| limit    | number | no       | Page size, default 50, min 1, max 200 |
| cursor   | string | no       | Opaque cursor for next page window    |

### Output

| Field     | Type          | Source      | Description                                  |
| --------- | ------------- | ----------- | -------------------------------------------- |
| entries[] | transaction[] | Transaction | MAKEUP_ADJUSTMENT and MAKEUP_APPLIED records |

**Ordering:** `entries[]` MUST be returned newest-first by `(date desc, createdAt desc)`.

### Pagination And Windowing

- Default `limit` is `50` when omitted.
- `limit` outside `[1, 200]` returns `400 VALIDATION_ERROR`.
- `cursor` identifies an exclusive start point in the same newest-first ordering.
- Page boundaries MUST be stable for repeated requests with identical `(playerId, limit, cursor)` inputs.

### Reads From

| Entity      | Relationship | Fields Used                       |
| ----------- | ------------ | --------------------------------- |
| Transaction | queries      | id, type, amount, date, createdAt |

## GetMakeupPolicy

**Type:** Query (read-only)
**Actor:** Authorized operations user

### Input

| Field    | Type   | Required | Description                                   |
| -------- | ------ | -------- | --------------------------------------------- |
| playerId | string | no       | Target player for effective policy resolution |

### Output

| Field               | Type    | Source                     | Description             |
| ------------------- | ------- | -------------------------- | ----------------------- |
| applyProfitFirst    | boolean | player override or default | Profit priority flag    |
| applyRakebackSecond | boolean | player override or default | Rakeback secondary flag |
| playerRakebackShare | number  | player override or default | Player rakeback split   |

**Scope Rule:**

- Policy resolution is player-aware when `playerId` is provided.
- Default policy remains authoritative fallback when player override is missing.
