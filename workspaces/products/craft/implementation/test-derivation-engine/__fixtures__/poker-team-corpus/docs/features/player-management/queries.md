---
id: player-management
feature: player-management
title: Player Management Queries
summary: Read models for player retrieval and overview metrics.
status: implemented
pillar: operations
domain: player-management-queries
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
  - domain.md
includes: []
---

# Queries: Player Management

> **Capabilities using this aspect:** [List All Players](SPEC.md#list-all-players) · [Players Overview](SPEC.md#players-overview) · [List All Coaches](SPEC.md#list-all-coaches) · [List Coach Players](SPEC.md#list-coach-players) · [Resolve Player Visibility](SPEC.md#resolve-player-visibility)

## Domain Policy Ownership

Overview projection formulas are owned by the domain layer.

- Domain projection authority: [`backend/src/domain/player/player-overview.service.ts`](../../../backend/src/domain/player/player-overview.service.ts)
- Use-case orchestrator: [`backend/src/use-cases/player/get-players-overview.ts`](../../../backend/src/use-cases/player/get-players-overview.ts)

## GetAllPlayers

**Type:** Query (read-only)  
**Actor:** Admin, operations user, internal services
**Auth Constraint:** [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) success + [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) allow for `player-management.read.getAllPlayers`

### Input

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| -     | -    | -        | No input    |

### Output

| Field     | Type     | Source    | Description      |
| --------- | -------- | --------- | ---------------- |
| players[] | Player[] | Player.\* | Flat player list |

### Reads From

| Entity | Relationship | Fields Used                                                         |
| ------ | ------------ | ------------------------------------------------------------------- |
| Player | queries      | id, principalId, name, email, currentLimit, status, bankroll, makeup |

## GetPlayersOverview

**Type:** Query (read-only)  
**Actor:** Admin, operations user, web dashboard
**Auth Constraint:** [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) success + [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) allow for `player-management.read.getPlayersOverview`

### Input

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| -     | -    | -        | No input    |

### Filters

| Field      | Type    | Default | Description                                               |
| ---------- | ------- | ------- | --------------------------------------------------------- |
| periodDays | integer | 30      | Generic rolling period used for average hands and winrate |

### Output

| Field              | Type         | Source                                                                              | Description                         |
| ------------------ | ------------ | ----------------------------------------------------------------------------------- | ----------------------------------- |
| id                 | string       | Player.id                                                                           | Player id                           |
| name               | string       | Player.name                                                                         | Player name                         |
| currentLimit       | string       | Player.currentLimit                                                                 | Current limit                       |
| status             | PlayerStatus | Player.status                                                                       | Operational status                  |
| bankroll           | integer      | Player.bankroll                                                                     | Current bankroll                    |
| makeup             | integer      | Player.makeup                                                                       | Current debt                        |
| lifetimeProfit     | integer      | [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot).profit         | Sum of all profits                  |
| avgHandsLastPeriod | integer      | [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot).hands          | Rolling average by requested period |
| winrateLastPeriod  | number       | [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot).profit, .hands | Rolling bb/100 by requested period  |
| periodDays         | integer      | Query input                                                                         | Period applied to derived metrics   |

### Reads From

| Entity                                                               | Relationship | Fields Used                                      |
| -------------------------------------------------------------------- | ------------ | ------------------------------------------------ |
| Player                                                               | queries      | id, name, currentLimit, status, bankroll, makeup |
| [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot) | queries      | statDate, hands, profit                          |

---

## GetAllCoaches

**Type:** Query (read-only)  
**Actor:** Admin, operations user  
**Auth Constraint:** [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) success + [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) allow for `player-management.read.getAllCoaches`

### Input

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| -     | -    | -        | No input    |

### Output

| Field     | Type    | Source   | Description |
| --------- | ------- | -------- | ----------- |
| coaches[] | Coach[] | Coach.\* | All coaches |

### Reads From

| Entity                   | Relationship | Fields Used                          |
| ------------------------ | ------------ | ------------------------------------ |
| [Coach](domain.md#coach) | queries      | id, principalId, name, email, status |

---

## GetCoachPlayers

**Type:** Query (read-only)  
**Actor:** Coach (own players), admin/manager (any coach's players)  
**Auth Constraint:** [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) success + [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) allow for `player-management.read.getCoachPlayers`

### Input

| Field   | Type   | Required | Description                 |
| ------- | ------ | -------- | --------------------------- |
| coachId | string | yes      | [Coach](domain.md#coach).id |

### Rules

| ID  | Rule                                                     | Formal                                                                        |
| --- | -------------------------------------------------------- | ----------------------------------------------------------------------------- |
| R1  | Coach must exist                                         | `Coach where id = coachId` exists                                             |
| R2  | Coach-scope enforcement: coach can only list own players | `actor.principalId = Coach.principalId OR actor has admin/manager permission` |

### Output

| Field     | Type     | Source    | Description                                  |
| --------- | -------- | --------- | -------------------------------------------- |
| players[] | Player[] | Player.\* | Players with active assignment to this coach |

### Reads From

| Entity                                       | Relationship | Fields Used                                             |
| -------------------------------------------- | ------------ | ------------------------------------------------------- |
| [CoachAssignment](domain.md#coachassignment) | queries      | coachId, playerId, unassignedAt (filter: IS NULL)       |
| [Player](domain.md#player)                   | queries      | id, name, email, currentLimit, status, bankroll, makeup |

---

## ResolvePlayerVisibility

**Type:** Query (cross-cutting service)  
**Actor:** Any authenticated user  
**Purpose:** Determines which player IDs a given actor may access. Consumed by [player-makeup](../player-makeup/SPEC.md), [player-stats](../player-stats/SPEC.md), and player-management routes.

### Input

| Field            | Type     | Required | Description                     |
| ---------------- | -------- | -------- | ------------------------------- |
| actorPrincipalId | string   | yes      | Auth principal of the caller    |
| actorPermissions | string[] | yes      | Effective permissions of caller |

### Resolution Rules

| Priority | Condition                                                                                                   | Visible Players                                                                                                      |
| -------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| 1        | Actor has admin/manager wildcard permission (`player-management.*.*` or `player-makeup.write.manageMakeup`) | All players                                                                                                          |
| 2        | Actor is a coach (Coach exists where `principalId = actorPrincipalId and status = ACTIVE`)                  | Players with active [CoachAssignment](domain.md#coachassignment) to that coach + actor's own player record if exists |
| 3        | Actor is a player only (no coach record, no admin/manager permission)                                       | Only the actor's own [Player](domain.md#player) record (where `principalId = actorPrincipalId`)                      |

### Output

| Field     | Type     | Description                            |
| --------- | -------- | -------------------------------------- |
| playerIds | string[] | Set of player IDs visible to the actor |

### Reads From

| Entity                                       | Relationship | Fields Used                     |
| -------------------------------------------- | ------------ | ------------------------------- |
| [Coach](domain.md#coach)                     | queries      | principalId, status             |
| [CoachAssignment](domain.md#coachassignment) | queries      | coachId, playerId, unassignedAt |
| [Player](domain.md#player)                   | queries      | id, principalId                 |
