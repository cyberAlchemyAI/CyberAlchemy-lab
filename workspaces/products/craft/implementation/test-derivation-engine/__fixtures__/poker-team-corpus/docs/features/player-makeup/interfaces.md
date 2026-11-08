---
id: player-makeup
feature: player-makeup
title: Player Makeup Interfaces
summary: REST and internal contracts for makeup management.
status: implemented
pillar: finance
domain: player-makeup-interfaces
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - operations.md
  - queries.md
includes: []
---

# Interfaces: Player Makeup

API contract authority for this feature is defined in this file.

## External: MakeupAPI (REST)

### GET /players/:id/makeup

**Exposes:** [GetPlayerMakeup](queries.md#getplayermakeup)  
**Auth:** requirePermission(`player-makeup.read.viewMakeup`)

**Visibility rule:**

- Player role: can read only own player id.
- Coach role: can read assigned players and self.
- Manager/admin roles: can read any player id allowed by permission.

**Responses:**

| Status | Condition                    | Body             |
| ------ | ---------------------------- | ---------------- |
| 200    | Success                      | makeup snapshot  |
| 401    | Missing/invalid bearer token | structured error |
| 403    | Missing permission           | structured error |
| 404    | Player not found             | structured error |
| 500    | Unexpected failure           | structured error |

### PATCH /players/:id/makeup

**Exposes:** [AdjustPlayerMakeup](operations.md#adjustplayermakeup)  
**Auth:** requirePermission(`player-makeup.write.manageMakeup`)

**Request:**

| Field           | Type   | Maps To                       |
| --------------- | ------ | ----------------------------- |
| params.id       | string | AdjustPlayerMakeup.playerId   |
| body.operation  | string | AdjustPlayerMakeup.operation  |
| body.amount     | number | AdjustPlayerMakeup.amount     |
| body.reasonCode | string | AdjustPlayerMakeup.reasonCode |

Server-derived metadata fields (`actorId`, `requestId`, `sourceChannel`) are not client inputs and are resolved from authenticated request context.

**Responses:**

| Status | Condition                | Body              |
| ------ | ------------------------ | ----------------- |
| 200    | Success                  | adjustment result |
| 401    | Missing/invalid token    | structured error  |
| 403    | Missing permission       | structured error  |
| 400    | Invalid operation/amount | structured error  |
| 404    | Player not found         | structured error  |
| 500    | Unexpected failure       | structured error  |

### GET /players/:id/makeup/history

**Exposes:** [GetPlayerMakeupHistory](queries.md#getplayermakeuphistory)  
**Auth:** requirePermission(`player-makeup.read.viewMakeup`)

**Visibility rule:**

- Player role: can read only own player id.
- Coach role: can read assigned players and self.
- Manager/admin roles: can read any player id allowed by permission.

**Responses:**

| Status | Condition                    | Body                   |
| ------ | ---------------------------- | ---------------------- |
| 200    | Success                      | sorted history entries |
| 401    | Missing/invalid bearer token | structured error       |
| 403    | Missing permission           | structured error       |
| 404    | Player not found             | structured error       |
| 500    | Unexpected failure           | structured error       |

**Contract Note:** `entries[]` MUST be sorted newest-first.

### GET /players/makeup/policy

**Exposes:** [GetMakeupPolicy](queries.md#getmakeuppolicy)  
**Auth:** requirePermission(`player-makeup.policy.readPolicy`)

**Request query:**

| Field    | Type   | Required | Description                                   |
| -------- | ------ | -------- | --------------------------------------------- |
| playerId | string | no       | Target player for effective policy resolution |

**Responses:**

| Status | Condition                    | Body             |
| ------ | ---------------------------- | ---------------- |
| 200    | Success                      | policy snapshot  |
| 401    | Missing/invalid bearer token | structured error |
| 403    | Missing permission           | structured error |
| 500    | Unexpected failure           | structured error |

### PATCH /players/:id/makeup/policy

**Exposes:** [SetPlayerMakeupPolicy](operations.md#setplayermakeuppolicy)  
**Auth:** requirePermission(`player-makeup.policy.writePolicy`)

**Request:**

| Field                    | Type    | Maps To                                   |
| ------------------------ | ------- | ----------------------------------------- |
| params.id                | string  | SetPlayerMakeupPolicy.playerId            |
| body.applyProfitFirst    | boolean | SetPlayerMakeupPolicy.applyProfitFirst    |
| body.applyRakebackSecond | boolean | SetPlayerMakeupPolicy.applyRakebackSecond |
| body.playerRakebackShare | number  | SetPlayerMakeupPolicy.playerRakebackShare |

**Responses:**

| Status | Condition                    | Body             |
| ------ | ---------------------------- | ---------------- |
| 200    | Success                      | updated policy   |
| 400    | Invalid policy shape         | structured error |
| 401    | Missing/invalid bearer token | structured error |
| 403    | Missing permission           | structured error |
| 404    | Player not found             | structured error |
| 500    | Unexpected failure           | structured error |

## External: PlayerDirectoryAPI (REST)

### GET /players

**Purpose:** Provide player selector input for makeup operational flows.

**Auth:** delegated to player-management permission model

**Response Body:** list of player items with `id`, `name`, `currentLimit`, `status`, `makeup`.

Permission authority is delegated to player-management feature ownership for this shared endpoint contract.

**Responses:**

| Status | Condition                    | Body             |
| ------ | ---------------------------- | ---------------- |
| 200    | Success                      | player list      |
| 401    | Missing/invalid bearer token | structured error |
| 403    | Missing permission           | structured error |
| 500    | Unexpected failure           | structured error |

## Error Contract

All protected endpoints in this file return structured errors:

| Field   | Type   | Required | Description                      |
| ------- | ------ | -------- | -------------------------------- |
| code    | string | yes      | Stable machine-readable code     |
| message | string | yes      | Human-readable summary           |
| details | object | no       | Optional context for remediation |

## Auth Contract

- Transport: bearer JWT.
- Supported MVP roles: `admin`, `manager`, `coach`, `player`.
- Role mapping:

| Role    | Permissions                                                                                                                                |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| admin   | `player-makeup.*.*`                                                                                                                        |
| manager | `player-makeup.read.viewMakeup`, `player-makeup.policy.readPolicy`, `player-makeup.policy.writePolicy`, `player-makeup.write.manageMakeup` |
| coach   | `player-makeup.read.viewMakeup`, `player-makeup.policy.readPolicy`                                                                         |
| player  | `player-makeup.read.viewMakeup`, `player-makeup.policy.readPolicy`                                                                         |

- Route permission matrix:

| Route                            | Permission                         |
| -------------------------------- | ---------------------------------- |
| GET /players/:id/makeup          | `player-makeup.read.viewMakeup`    |
| GET /players/:id/makeup/history  | `player-makeup.read.viewMakeup`    |
| GET /players/makeup/policy       | `player-makeup.policy.readPolicy`  |
| PATCH /players/:id/makeup        | `player-makeup.write.manageMakeup` |
| PATCH /players/:id/makeup/policy | `player-makeup.policy.writePolicy` |
| GET /players                     | delegated to player-management     |
