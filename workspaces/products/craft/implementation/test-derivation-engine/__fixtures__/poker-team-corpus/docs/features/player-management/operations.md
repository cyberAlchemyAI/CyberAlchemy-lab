---
id: player-management
feature: player-management
title: Player Management Operations
summary: Mutation behavior for player lifecycle writes.
status: implemented
pillar: operations
domain: player-management-operations
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-30
dependencies:
  - SPEC.md
  - domain.md
  - states.md
  - events.md
  - queries.md
  - interfaces.md
  - mappings.md
includes: []
---

# Operations: Player Management

> **Capabilities using this aspect:** [Create Player](SPEC.md#create-player) · [Create Coach](SPEC.md#create-coach) · [Assign Coach](SPEC.md#assign-coach) · [Unassign Coach](SPEC.md#unassign-coach)

## CreatePlayer

**Type:** Operation (mutation)  
**Actor:** Admin or operations user  
**Triggers:** POST /players

### Input

| Field           | Type    | Required | Description               |
| --------------- | ------- | -------- | ------------------------- |
| name            | string  | yes      | Player display name       |
| email           | string  | yes      | Player email              |
| currentLimit    | string  | yes      | Initial limit             |
| principalId     | string  | no       | Optional auth principal linkage |
| initialBankroll | integer | no       | Optional initial bankroll |

### Rules

| ID  | Rule                                                   | Formal                                                                                                                  |
| --- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| R0  | caller must be authenticated and authorized for create | `AuthenticateRequest = success and AuthorizeRequest(requiredPermission='player-management.write.createPlayer') = ALLOW` |
| R1  | name must be present                                   | `len(trim(name)) > 0`                                                                                                   |
| R2  | email must be present                                  | `len(trim(email)) > 0`                                                                                                  |
| R3  | currentLimit must be present                           | `len(trim(currentLimit)) > 0`                                                                                           |
| R4  | email uniqueness must use canonical key                | `count(Player where emailKey = lowercase(removeSpecialChars(trim(input.email)))) = 0`                                   |
| R5  | initialBankroll must be non-negative when provided     | `initialBankroll is null or initialBankroll >= 0`                                                                       |
| R6  | currentLimit must be configured allowed limit          | `currentLimit in {NL20, NL40, NL60, NL80, NL100}`                                                                       |
| R7  | principalId must be non-empty and unique when provided | `principalId is null OR (len(trim(principalId)) > 0 AND count(Player where principalId = input.principalId) = 0)`       |

### Calculations

| ID  | Calculation                    | Formula                                                 |
| --- | ------------------------------ | ------------------------------------------------------- |
| C1  | Default bankroll normalization | `bankroll = initialBankroll ?? 0`                       |
| C2  | Canonical email key            | `emailKey = lowercase(removeSpecialChars(trim(email)))` |

### State Transition

`Player: [new] -> OBSERVATION`

### Postconditions

| ID  | Class                 | Guarantee                                                      | Formal Assertion                                        | Traceability |
| --- | --------------------- | -------------------------------------------------------------- | ------------------------------------------------------- | ------------ |
| P1  | Persistence Guarantee | Player record is persisted.                                    | `exists(Player.id = createdPlayerId)`                   | [Player](domain.md#player), [CreatePlayerRequestToEntity](mappings.md#createplayerrequesttoentity) |
| P2  | State Guarantee       | Player starts in `OBSERVATION` lifecycle state.               | `createdPlayer.status = OBSERVATION`                    | [PlayerLifecycle](states.md#playerlifecycle) |
| P3  | Integration Guarantee | Player can be returned by [GetAllPlayers](queries.md#getallplayers). | `GetAllPlayers().items contains createdPlayerId`        | [GetAllPlayers](queries.md#getallplayers), [GET /players](interfaces.md#get-players) |

### Error States

| Condition                | Result                                                      |
| ------------------------ | ----------------------------------------------------------- |
| R0 violated              | Authentication/authorization error from auth-access-control |
| R1-R3 violated           | Validation error                                            |
| R4 violated              | Conflict error (`DUPLICATE_EMAIL`)                          |
| R5-R6 violated           | Validation error                                            |
| R7 violated              | Validation or conflict error (`DUPLICATE_PRINCIPAL_ID`)     |
| Repository rejects write | Internal persistence error                                  |

---

## CreateCoach

**Type:** Operation (mutation)  
**Actor:** Admin or operations user  
**Triggers:** POST /coaches

### Input

| Field       | Type   | Required | Description                             |
| ----------- | ------ | -------- | --------------------------------------- |
| principalId | string | yes      | Auth principal identifier for the coach |
| name        | string | yes      | Coach display name                      |
| email       | string | yes      | Coach contact email                     |

### Rules

| ID  | Rule                                                   | Formal                                                                                                                 |
| --- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| R0  | Caller must be authenticated and authorized for create | `AuthenticateRequest = success and AuthorizeRequest(requiredPermission='player-management.write.createCoach') = ALLOW` |
| R1  | principalId must be present                            | `len(trim(principalId)) > 0`                                                                                           |
| R2  | name must be present                                   | `len(trim(name)) > 0`                                                                                                  |
| R3  | email must be present                                  | `len(trim(email)) > 0`                                                                                                 |
| R4  | principalId must be unique among active coaches        | `count(Coach where principalId = input.principalId and status = ACTIVE) = 0`                                           |

### State Transition

`Coach: [new] -> ACTIVE`

### Postconditions

| ID  | Class                 | Guarantee                                                         | Formal Assertion                                        | Traceability |
| --- | --------------------- | ----------------------------------------------------------------- | ------------------------------------------------------- | ------------ |
| P1  | State Guarantee       | Coach record is persisted with `status = ACTIVE`.                | `exists(Coach.id = createdCoachId) and createdCoach.status = ACTIVE` | [Coach](domain.md#coach), [CoachLifecycle](states.md#coachlifecycle) |
| P2  | Integration Guarantee | Coach can be listed by [GetAllCoaches](queries.md#getallcoaches). | `GetAllCoaches().items contains createdCoachId`         | [GetAllCoaches](queries.md#getallcoaches), [GET /coaches](interfaces.md#get-coaches) |
| P3  | Integration Guarantee | Coach can receive player assignments via [AssignCoach](#assigncoach). | `canAssign(createdCoachId) = true`                      | [AssignCoach](#assigncoach), [POST /coaches/:coachId/players/:playerId](interfaces.md#post-coachescoachidplayersplayerid) |

### Error States

| Condition                | Result                                                      |
| ------------------------ | ----------------------------------------------------------- |
| R0 violated              | Authentication/authorization error from auth-access-control |
| R1-R3 violated           | Validation error (400)                                      |
| R4 violated              | Conflict error (`DUPLICATE_PRINCIPAL`, 409)                 |
| Repository rejects write | Internal persistence error (500)                            |

---

## AssignCoach

**Type:** Operation (mutation)  
**Actor:** Admin or operations user  
**Triggers:** POST /coaches/:coachId/players/:playerId

### Input

| Field    | Type   | Required | Description                   |
| -------- | ------ | -------- | ----------------------------- |
| coachId  | string | yes      | [Coach](domain.md#coach).id   |
| playerId | string | yes      | [Player](domain.md#player).id |

### Rules

| ID  | Rule                                                   | Formal                                                                                                                 |
| --- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| R0  | Caller must be authenticated and authorized for assign | `AuthenticateRequest = success and AuthorizeRequest(requiredPermission='player-management.write.assignCoach') = ALLOW` |
| R1  | Coach must exist                                       | `Coach where id = coachId` exists                                                                                      |
| R2  | Coach must be ACTIVE                                   | `Coach.status = ACTIVE`                                                                                                |
| R3  | Player must exist                                      | `Player where id = playerId` exists                                                                                    |
| R4  | Player must not already have an active coach           | `count(CoachAssignment where playerId = input.playerId and unassignedAt IS NULL) = 0`                                  |

### State Transition

`CoachAssignment: [new] -> ACTIVE (assignedAt = now, unassignedAt = null)`

### Postconditions

| ID  | Class                 | Guarantee                                                                 | Formal Assertion                                                                                  | Traceability |
| --- | --------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------ |
| P1  | Persistence Guarantee | [CoachAssignment](domain.md#coachassignment) record is persisted.         | `exists(CoachAssignment where coachId = input.coachId and playerId = input.playerId and unassignedAt is null)` | [CoachAssignment](domain.md#coachassignment), [CoachAssignmentLifecycle](states.md#coachassignmentlifecycle) |
| P2  | Integration Guarantee | Coach can see the player via [GetCoachPlayers](queries.md#getcoachplayers). | `GetCoachPlayers(coachId).items contains playerId`                                                | [GetCoachPlayers](queries.md#getcoachplayers), [GET /coaches/:coachId/players](interfaces.md#get-coachescoachidplayers) |
| P3  | Integration Guarantee | [ResolvePlayerVisibility](queries.md#resolveplayervisibility) includes the player in the coach's visible set. | `ResolvePlayerVisibility(principalId=coachPrincipalId).visiblePlayerIds contains playerId`      | [ResolvePlayerVisibility](queries.md#resolveplayervisibility), [CoachAssigned](events.md#coachassigned) |

### Error States

| Condition                | Result                                                      |
| ------------------------ | ----------------------------------------------------------- |
| R0 violated              | Authentication/authorization error from auth-access-control |
| R1 violated              | Coach not found (404)                                       |
| R2 violated              | Coach inactive (409 `COACH_INACTIVE`)                       |
| R3 violated              | Player not found (404)                                      |
| R4 violated              | Conflict (`PLAYER_ALREADY_ASSIGNED`, 409)                   |
| Repository rejects write | Internal persistence error (500)                            |

---

## UnassignCoach

**Type:** Operation (mutation)  
**Actor:** Admin or operations user  
**Triggers:** DELETE /coaches/:coachId/players/:playerId

### Input

| Field    | Type   | Required | Description                   |
| -------- | ------ | -------- | ----------------------------- |
| coachId  | string | yes      | [Coach](domain.md#coach).id   |
| playerId | string | yes      | [Player](domain.md#player).id |

### Rules

| ID  | Rule                                                     | Formal                                                                                                                   |
| --- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| R0  | Caller must be authenticated and authorized for unassign | `AuthenticateRequest = success and AuthorizeRequest(requiredPermission='player-management.write.unassignCoach') = ALLOW` |
| R1  | Active assignment must exist for the coach-player pair   | `CoachAssignment where coachId = input.coachId and playerId = input.playerId and unassignedAt IS NULL` exists            |

### State Transition

`CoachAssignment: ACTIVE -> UNASSIGNED (unassignedAt = now)`

### Postconditions

| ID  | Class                 | Guarantee                                                                 | Formal Assertion                                                                                  | Traceability |
| --- | --------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------ |
| P1  | Persistence Guarantee | [CoachAssignment](domain.md#coachassignment).unassignedAt is set to current timestamp. | `assignment.unassignedAt != null`                                                                 | [CoachAssignment](domain.md#coachassignment), [CoachAssignmentLifecycle](states.md#coachassignmentlifecycle) |
| P2  | Integration Guarantee | Player is no longer visible to the coach via [ResolvePlayerVisibility](queries.md#resolveplayervisibility). | `ResolvePlayerVisibility(principalId=coachPrincipalId).visiblePlayerIds does not contain playerId` | [ResolvePlayerVisibility](queries.md#resolveplayervisibility), [CoachUnassigned](events.md#coachunassigned) |
| P3  | Audit Guarantee       | Historical assignment is preserved for audit.                              | `exists(CoachAssignment where coachId = input.coachId and playerId = input.playerId and unassignedAt != null)` | [CoachAssignment](domain.md#coachassignment), [CoachUnassigned](events.md#coachunassigned) |

### Error States

| Condition                | Result                                                      |
| ------------------------ | ----------------------------------------------------------- |
| R0 violated              | Authentication/authorization error from auth-access-control |
| R1 violated              | Assignment not found (404 `ASSIGNMENT_NOT_FOUND`)           |
| Repository rejects write | Internal persistence error (500)                            |
