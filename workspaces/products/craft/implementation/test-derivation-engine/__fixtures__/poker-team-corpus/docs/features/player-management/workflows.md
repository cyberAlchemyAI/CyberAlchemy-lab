---
id: player-management
feature: player-management
title: Player Management Workflows
summary: End-to-end orchestration for player creation and coach assignment lifecycle.
status: implemented
pillar: operations
domain: player-management-workflows
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
  - queries.md
includes: []
---

# Workflows: Player Management

## PlayerRegistrationWorkflow

**Type:** Workflow
**Triggers:** `POST /players`
**Orchestrates:** [CreatePlayer](operations.md#createplayer), [GetAllPlayers](queries.md#getallplayers)
**Compensation Strategy:** none
**Idempotency:** no (duplicate canonical email is rejected)

### Steps

```mermaid
graph TD
  A[Authenticate + authorize caller] --> B[Validate player payload]
  B --> C[Normalize canonical email and bankroll]
  C --> D[Persist player]
  D --> E[Return player projection]
```

## CoachAssignmentWorkflow

**Type:** Workflow
**Triggers:** `POST /coaches/:coachId/players/:playerId`, `DELETE /coaches/:coachId/players/:playerId`
**Orchestrates:** [AssignCoach](operations.md#assigncoach), [UnassignCoach](operations.md#unassigncoach), [ResolvePlayerVisibility](queries.md#resolveplayervisibility)
**Compensation Strategy:** none
**Idempotency:** partial (unassign on non-existent active assignment returns `ASSIGNMENT_NOT_FOUND`)

### Steps

```mermaid
graph TD
  A[Authenticate + authorize caller] --> B{Assign or unassign action}
  B -->|Assign| C[Validate coach and player]
  C --> D[Enforce one active coach per player]
  D --> E[Persist active assignment]
  B -->|Unassign| F[Soft-delete active assignment]
  E --> G[Refresh visibility projection]
  F --> G
```

### Invariants

| ID | Invariant | Formal |
| --- | --------- | ------ |
| I1 | Assignment flow preserves one active coach per player | `count(active assignments by playerId) <= 1` |
| I2 | Visibility query must reflect latest assignment state | `ResolvePlayerVisibility(playerId) uses active assignment set` |
