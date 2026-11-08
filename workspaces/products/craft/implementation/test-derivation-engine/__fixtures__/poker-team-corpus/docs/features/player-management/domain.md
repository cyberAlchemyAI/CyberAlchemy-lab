---
id: player-management
feature: player-management
title: Player Management Domain
summary: Structural concepts for player identity and status.
status: implemented
pillar: operations
domain: player-management
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
includes: []
---

# Domain: Player Management

> **Capabilities using this aspect:** [Create Player](SPEC.md#create-player) · [List All Players](SPEC.md#list-all-players) · [Players Overview](SPEC.md#players-overview) · [Create Coach](SPEC.md#create-coach) · [Assign Coach](SPEC.md#assign-coach) · [Unassign Coach](SPEC.md#unassign-coach) · [List Coach Players](SPEC.md#list-coach-players) · [List All Coaches](SPEC.md#list-all-coaches) · [Resolve Player Visibility](SPEC.md#resolve-player-visibility)

## Entities

### Player

| Field        | Type         | Required | Description                                           |
| ------------ | ------------ | -------- | ----------------------------------------------------- |
| id           | string       | yes      | Unique player identifier                              |
| principalId  | string       | no       | Auth principal linkage for player self-visibility     |
| name         | string       | yes      | Display name                                          |
| email        | string       | yes      | Contact and unique login reference                    |
| currentLimit | string       | yes      | Current limit selected from configured allowed limits |
| status       | PlayerStatus | yes      | Operational status                                    |
| bankroll     | integer      | yes      | Current bankroll in integer monetary units            |
| makeup       | integer      | yes      | Current debt balance                                  |
| createdAt    | datetime     | yes      | Creation timestamp                                    |
| updatedAt    | datetime     | yes      | Last update timestamp                                 |

**Operations:** [CreatePlayer](operations.md#createplayer)

**Invariants:**

- `email` uniqueness uses canonical key `lowercase(removeSpecialChars(trim(email)))`.
- `principalId` must be unique when present.
- `bankroll >= 0`.
- `makeup >= 0`.
- `currentLimit` must be one of: `NL20`, `NL40`, `NL60`, `NL80`, `NL100`.

---

## Enums

### PlayerStatus

| Value       | Description                                |
| ----------- | ------------------------------------------ |
| ACTIVE      | Player can operate and receive new records |
| INACTIVE    | Player is not active for operations        |
| OBSERVATION | Player requires monitoring                 |

---

## Entities (Coach Model)

### Coach

| Field       | Type        | Required | Description                                        |
| ----------- | ----------- | -------- | -------------------------------------------------- |
| id          | string      | yes      | Unique coach identifier (UUID)                     |
| principalId | string      | yes      | Auth principal identifier for login and visibility |
| name        | string      | yes      | Display name                                       |
| email       | string      | yes      | Contact email                                      |
| status      | CoachStatus | yes      | Operational status                                 |
| createdAt   | datetime    | yes      | Creation timestamp                                 |
| updatedAt   | datetime    | yes      | Last update timestamp                              |

**Operations:** [CreateCoach](operations.md#createcoach)

**Invariants:**

- `principalId` must be unique across active coaches.
- `email` must be a non-empty string (no canonical uniqueness enforcement — coach identity is `principalId`).

### CoachAssignment

| Field        | Type     | Required | Description                                   |
| ------------ | -------- | -------- | --------------------------------------------- |
| id           | string   | yes      | Unique assignment identifier (UUID)           |
| coachId      | string   | yes      | FK → [Coach](#coach).id                       |
| playerId     | string   | yes      | FK → [Player](#player).id                     |
| assignedAt   | datetime | yes      | When the assignment was created               |
| unassignedAt | datetime | no       | When the assignment was revoked (soft delete) |

**Operations:** [AssignCoach](operations.md#assigncoach) · [UnassignCoach](operations.md#unassigncoach)

**Invariants:**

- A player has at most one **active** coach: `UNIQUE(playerId) WHERE unassignedAt IS NULL`.
- `coachId` must reference an existing Coach with `status = ACTIVE`.
- `playerId` must reference an existing [Player](#player).

---

## Enums (Coach Model)

### CoachStatus

| Value    | Description                          |
| -------- | ------------------------------------ |
| ACTIVE   | Coach can receive player assignments |
| INACTIVE | Coach cannot receive new assignments |
