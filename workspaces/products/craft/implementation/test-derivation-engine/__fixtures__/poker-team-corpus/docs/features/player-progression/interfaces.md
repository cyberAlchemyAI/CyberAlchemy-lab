---
id: player-progression
feature: player-progression
title: Player Progression Interfaces
summary: REST contracts for progression status retrieval, proxied via player-management.
status: implemented
pillar: operations
domain: player-progression-interfaces
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
  - queries.md
includes: []
---

# Interfaces: Player Progression

API contract authority for this feature is defined in this file. The progression endpoint is registered under the player-management route prefix as a delegated capability.

## External: PlayerProgressionAPI (REST)

### GET /players/:id/progression

**Exposes:** [CheckProgression](operations.md#checkprogression) via [GetProgressionStatus](queries.md#getprogressionstatus)  
**Auth:** requirePermission(player-management.read.getPlayerProgression)

**Request:**

| Field  | Source | Type   | Required | Description                    |
| ------ | ------ | ------ | -------- | ------------------------------ |
| id     | params | string | yes      | Target player id               |
| period | query  | string | no       | BI_WEEKLY (default) or MONTHLY |

**Period mapping:**

| Value     | Window            |
| --------- | ----------------- |
| BI_WEEKLY | 15 days           |
| MONTHLY   | 30 days           |
| (omitted) | 15 days (default) |

**Response body (200):**

| Field                | Type    | Description                       |
| -------------------- | ------- | --------------------------------- |
| eligibleForPromotion | boolean | Promotion readiness flag          |
| reason               | string  | Human-readable eligibility reason |
| avgHands             | number  | Average daily hands in period     |
| winrate              | number  | Winrate in bb/100                 |
| period               | string  | BI_WEEKLY or MONTHLY              |

**Responses:**

| Status | Condition                    | Body              |
| ------ | ---------------------------- | ----------------- |
| 200    | Success                      | ProgressionResult |
| 400    | Invalid period query value   | structured error  |
| 401    | Missing/invalid bearer token | structured error  |
| 403    | Missing permission           | structured error  |
| 404    | Player not found             | structured error  |
| 500    | Unexpected failure           | structured error  |

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
- Route permission matrix:

| Route                        | Permission                                  |
| ---------------------------- | ------------------------------------------- |
| GET /players/:id/progression | player-management.read.getPlayerProgression |
