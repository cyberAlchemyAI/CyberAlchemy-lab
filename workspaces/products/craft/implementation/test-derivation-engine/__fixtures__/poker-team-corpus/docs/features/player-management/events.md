---
id: player-management
feature: player-management
title: Player Management Events
summary: Domain events produced by player and coach lifecycle operations.
status: implemented
pillar: operations
domain: player-management-events
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
  - states.md
includes: []
---

# Events: Player Management

## PlayerCreated

**Produced by:** [CreatePlayer](operations.md#createplayer)
**Triggers transition:** [PlayerLifecycle](states.md#playerlifecycle)

### Payload

| Field | Type | Description |
| ----- | ---- | ----------- |
| playerId | string | Persisted player identity |
| emailKey | string | Canonical email key |
| currentLimit | string | Initial limit |
| occurredAt | datetime | Event timestamp |

## CoachCreated

**Produced by:** [CreateCoach](operations.md#createcoach)
**Triggers transition:** [CoachLifecycle](states.md#coachlifecycle)

### Payload

| Field | Type | Description |
| ----- | ---- | ----------- |
| coachId | string | Persisted coach identity |
| principalId | string | Auth principal linked to coach |
| status | string | Initial coach status (`ACTIVE`) |
| occurredAt | datetime | Event timestamp |

## CoachAssigned

**Produced by:** [AssignCoach](operations.md#assigncoach)
**Triggers transition:** [CoachAssignmentLifecycle](states.md#coachassignmentlifecycle)

### Payload

| Field | Type | Description |
| ----- | ---- | ----------- |
| assignmentId | string | Assignment identity |
| coachId | string | Assigned coach |
| playerId | string | Assigned player |
| assignedAt | datetime | Assignment timestamp |

## CoachUnassigned

**Produced by:** [UnassignCoach](operations.md#unassigncoach)
**Triggers transition:** [CoachAssignmentLifecycle](states.md#coachassignmentlifecycle)

### Payload

| Field | Type | Description |
| ----- | ---- | ----------- |
| assignmentId | string | Assignment identity |
| coachId | string | Unassigned coach |
| playerId | string | Unassigned player |
| unassignedAt | datetime | Unassignment timestamp |
