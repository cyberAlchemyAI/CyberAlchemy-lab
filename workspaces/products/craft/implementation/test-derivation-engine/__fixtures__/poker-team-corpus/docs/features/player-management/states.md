---
id: player-management
feature: player-management
title: Player Management States
summary: State machines for player, coach, and coach assignment lifecycle.
status: implemented
pillar: operations
domain: player-management-states
audience:
  - developers
  - operations
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-17
dependencies:
  - SPEC.md
  - operations.md
  - domain.md
includes: []
---

# States: Player Management

## PlayerLifecycle

```mermaid
stateDiagram-v2
  [*] --> OBSERVATION : CreatePlayer
  OBSERVATION --> ACTIVE : activation decision
  ACTIVE --> INACTIVE : operational disable
  INACTIVE --> ACTIVE : operational re-enable
```

### Transition Table

| From | Event | To | Guard | Effect |
| ---- | ----- | -- | ----- | ------ |
| [new] | CreatePlayer | OBSERVATION | Create rules R0-R6 pass | Player record persisted |
| OBSERVATION | ActivatePlayer | ACTIVE | Player satisfies operational requirements | Player can fully operate |
| ACTIVE | DeactivatePlayer | INACTIVE | Admin/ops action | New operational writes can be blocked by policy |
| INACTIVE | ReactivatePlayer | ACTIVE | Admin/ops action | Player returns to active operation |

## CoachLifecycle

```mermaid
stateDiagram-v2
  [*] --> ACTIVE : CreateCoach
  ACTIVE --> INACTIVE : operational disable
  INACTIVE --> ACTIVE : operational re-enable
```

## CoachAssignmentLifecycle

```mermaid
stateDiagram-v2
  [*] --> ACTIVE : AssignCoach
  ACTIVE --> UNASSIGNED : UnassignCoach
  UNASSIGNED --> [*]
```

### Invariants

| ID | Invariant | Formal |
| --- | --------- | ------ |
| I1 | One active coach assignment per player | `count(CoachAssignment where playerId = X and unassignedAt is null) <= 1` |
| I2 | Inactive coach cannot receive new assignments | `Coach.status = INACTIVE -> AssignCoach rejected` |
