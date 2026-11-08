---
id: player-management
feature: player-management
title: Player Management Interfaces
summary: REST and internal contracts for player management.
status: implemented
pillar: platform
domain: player-management-interfaces
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

# Interfaces: Player Management

> **Capabilities using this aspect:** [Create Player](SPEC.md#create-player) · [List All Players](SPEC.md#list-all-players) · [Players Overview](SPEC.md#players-overview) · [Check Player Progression](SPEC.md#check-player-progression) · [Create Coach](SPEC.md#create-coach) · [Assign Coach](SPEC.md#assign-coach) · [Unassign Coach](SPEC.md#unassign-coach) · [List Coach Players](SPEC.md#list-coach-players) · [List All Coaches](SPEC.md#list-all-coaches)

## External: PlayerAPI (REST)

### POST /players

**Exposes:** [CreatePlayer](operations.md#createplayer)  
**Auth:** JWT validated by [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) + permission check by [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) with `player-management.write.createPlayer`

**Request:**

| Field           | Type    | Maps To                      |
| --------------- | ------- | ---------------------------- |
| name            | string  | CreatePlayer.name            |
| email           | string  | CreatePlayer.email           |
| currentLimit    | string  | CreatePlayer.currentLimit    |
| initialBankroll | integer | CreatePlayer.initialBankroll |

**Responses:**

| Status | Condition                                    | Body                                            |
| ------ | -------------------------------------------- | ----------------------------------------------- |
| 201    | Success                                      | Player entity                                   |
| 401    | Missing/invalid/expired/revoked JWT          | Standard error payload from auth-access-control |
| 403    | Missing required permission                  | Standard error payload from auth-access-control |
| 400    | Input validation failure                     | Standard error payload                          |
| 409    | Duplicate email conflict (`DUPLICATE_EMAIL`) | Standard error payload                          |
| 500    | Unexpected persistence failure               | Standard error payload                          |

### GET /players

**Exposes:** [GetAllPlayers](queries.md#getallplayers)  
**Auth:** JWT validated by [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) + permission check by [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) with `player-management.read.getAllPlayers`

**Responses:**

| Status | Condition                           | Body                                            |
| ------ | ----------------------------------- | ----------------------------------------------- |
| 200    | Success                             | Player[]                                        |
| 401    | Missing/invalid/expired/revoked JWT | Standard error payload from auth-access-control |
| 403    | Missing required permission         | Standard error payload from auth-access-control |
| 500    | Unexpected failure                  | Standard error payload                          |

### GET /players/overview

**Exposes:** [GetPlayersOverview](queries.md#getplayersoverview)  
**Auth:** JWT validated by [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) + permission check by [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) with `player-management.read.getPlayersOverview`

**Request:**

| Field            | Type    | Maps To                       |
| ---------------- | ------- | ----------------------------- |
| query.periodDays | integer | GetPlayersOverview.periodDays |

**Responses:**

| Status | Condition                           | Body                                            |
| ------ | ----------------------------------- | ----------------------------------------------- |
| 200    | Success                             | PlayerOverviewDto[]                             |
| 401    | Missing/invalid/expired/revoked JWT | Standard error payload from auth-access-control |
| 403    | Missing required permission         | Standard error payload from auth-access-control |
| 500    | Unexpected failure                  | Standard error payload                          |

### GET /players/:id/progression

**Exposes:** player-progression.CheckProgression  
**Auth:** JWT validated by [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) + permission check by [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) with `player-management.read.getPlayerProgression`

**Request:**

| Field        | Type   | Maps To                     |
| ------------ | ------ | --------------------------- |
| params.id    | string | CheckProgression.playerId   |
| query.period | string | CheckProgression.periodDays |

**Responses:**

| Status | Condition                           | Body                                            |
| ------ | ----------------------------------- | ----------------------------------------------- |
| 200    | Success                             | Progression status object                       |
| 401    | Missing/invalid/expired/revoked JWT | Standard error payload from auth-access-control |
| 403    | Missing required permission         | Standard error payload from auth-access-control |
| 404    | Player not found                    | Standard error payload                          |
| 500    | Unexpected failure                  | Standard error payload                          |

## Internal: PlayerRepository Interface

**Consumers:** player use-cases, settlement, makeup, progression

| Method            | Maps To                          | Description               |
| ----------------- | -------------------------------- | ------------------------- |
| create(input)     | CreatePlayer operation           | Persists new player       |
| findAll()         | GetAllPlayers query              | Lists players             |
| findById(id)      | GetPlayersOverview query         | Gets player context       |
| update(id, input) | makeup and settlement operations | Mutates player aggregates |

---

## External: CoachAPI (REST)

### POST /coaches

**Exposes:** [CreateCoach](operations.md#createcoach)  
**Auth:** JWT validated by [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) + permission check by [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) with `player-management.write.createCoach`

**Request:**

| Field       | Type   | Maps To                 |
| ----------- | ------ | ----------------------- |
| principalId | string | CreateCoach.principalId |
| name        | string | CreateCoach.name        |
| email       | string | CreateCoach.email       |

**Responses:**

| Status | Condition                                     | Body                                            |
| ------ | --------------------------------------------- | ----------------------------------------------- |
| 201    | Success                                       | [Coach](domain.md#coach) entity                 |
| 401    | Missing/invalid/expired/revoked JWT           | Standard error payload from auth-access-control |
| 403    | Missing required permission                   | Standard error payload from auth-access-control |
| 400    | Input validation failure                      | Standard error payload                          |
| 409    | Duplicate principalId (`DUPLICATE_PRINCIPAL`) | Standard error payload                          |
| 500    | Unexpected persistence failure                | Standard error payload                          |

### GET /coaches

**Exposes:** [GetAllCoaches](queries.md#getallcoaches)  
**Auth:** JWT validated by [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) + permission check by [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) with `player-management.read.getAllCoaches`

**Responses:**

| Status | Condition                           | Body                                            |
| ------ | ----------------------------------- | ----------------------------------------------- |
| 200    | Success                             | [Coach](domain.md#coach)[]                      |
| 401    | Missing/invalid/expired/revoked JWT | Standard error payload from auth-access-control |
| 403    | Missing required permission         | Standard error payload from auth-access-control |
| 500    | Unexpected failure                  | Standard error payload                          |

### POST /coaches/:coachId/players/:playerId

**Exposes:** [AssignCoach](operations.md#assigncoach)  
**Auth:** JWT validated by [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) + permission check by [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) with `player-management.write.assignCoach`

**Request:**

| Field           | Type   | Maps To              |
| --------------- | ------ | -------------------- |
| params.coachId  | string | AssignCoach.coachId  |
| params.playerId | string | AssignCoach.playerId |

**Responses:**

| Status | Condition                                                                               | Body                                            |
| ------ | --------------------------------------------------------------------------------------- | ----------------------------------------------- |
| 201    | Assignment created                                                                      | [CoachAssignment](domain.md#coachassignment)    |
| 401    | Missing/invalid/expired/revoked JWT                                                     | Standard error payload from auth-access-control |
| 403    | Missing required permission                                                             | Standard error payload from auth-access-control |
| 404    | Coach or player not found                                                               | Standard error payload                          |
| 409    | Player already assigned or coach inactive (`PLAYER_ALREADY_ASSIGNED`, `COACH_INACTIVE`) | Standard error payload                          |
| 500    | Unexpected persistence failure                                                          | Standard error payload                          |

### DELETE /coaches/:coachId/players/:playerId

**Exposes:** [UnassignCoach](operations.md#unassigncoach)  
**Auth:** JWT validated by [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) + permission check by [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) with `player-management.write.unassignCoach`

**Request:**

| Field           | Type   | Maps To                |
| --------------- | ------ | ---------------------- |
| params.coachId  | string | UnassignCoach.coachId  |
| params.playerId | string | UnassignCoach.playerId |

**Responses:**

| Status | Condition                                            | Body                                            |
| ------ | ---------------------------------------------------- | ----------------------------------------------- |
| 200    | Assignment soft-deleted                              | `{ unassignedAt: datetime }`                    |
| 401    | Missing/invalid/expired/revoked JWT                  | Standard error payload from auth-access-control |
| 403    | Missing required permission                          | Standard error payload from auth-access-control |
| 404    | Active assignment not found (`ASSIGNMENT_NOT_FOUND`) | Standard error payload                          |
| 500    | Unexpected persistence failure                       | Standard error payload                          |

### GET /coaches/:coachId/players

**Exposes:** [GetCoachPlayers](queries.md#getcoachplayers)  
**Auth:** JWT validated by [AuthenticateRequest](../auth-access-control/operations.md#authenticaterequest) + permission check by [AuthorizeRequest](../auth-access-control/operations.md#authorizerequest) with `player-management.read.getCoachPlayers`

**Request:**

| Field          | Type   | Maps To                 |
| -------------- | ------ | ----------------------- |
| params.coachId | string | GetCoachPlayers.coachId |

**Responses:**

| Status | Condition                                            | Body                                            |
| ------ | ---------------------------------------------------- | ----------------------------------------------- |
| 200    | Success                                              | [Player](domain.md#player)[]                    |
| 401    | Missing/invalid/expired/revoked JWT                  | Standard error payload from auth-access-control |
| 403    | Missing required permission or coach-scope violation | Standard error payload                          |
| 404    | Coach not found                                      | Standard error payload                          |
| 500    | Unexpected failure                                   | Standard error payload                          |

## Internal: CoachRepository Interface

**Consumers:** coach use-cases, visibility resolver

| Method                         | Maps To                       | Description                   |
| ------------------------------ | ----------------------------- | ----------------------------- |
| create(input)                  | CreateCoach operation         | Persists new coach            |
| findById(id)                   | AssignCoach / GetCoachPlayers | Gets coach context            |
| findByPrincipalId(principalId) | ResolvePlayerVisibility       | Finds coach by auth principal |
| findAll()                      | GetAllCoaches query           | Lists all coaches             |

## Internal: CoachAssignmentRepository Interface

**Consumers:** assign/unassign use-cases, visibility resolver

| Method                                             | Maps To                 | Description                        |
| -------------------------------------------------- | ----------------------- | ---------------------------------- |
| create(input)                                      | AssignCoach operation   | Persists new assignment            |
| findActiveByCoachId(coachId)                       | GetCoachPlayers query   | Active assignments for a coach     |
| findActiveByPlayerId(playerId)                     | AssignCoach rule check  | Checks one-active-coach constraint |
| softDelete(coachId, playerId)                      | UnassignCoach operation | Sets unassignedAt                  |
| findActivePlayerIdsByCoachPrincipalId(principalId) | ResolvePlayerVisibility | Visible player IDs for a coach     |
