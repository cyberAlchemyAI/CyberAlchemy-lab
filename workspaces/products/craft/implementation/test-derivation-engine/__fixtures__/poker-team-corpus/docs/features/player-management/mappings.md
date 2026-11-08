---
id: player-management
feature: player-management
title: Player Management Mappings
summary: Mapping contracts for player API payloads and overview projection outputs.
status: implemented
pillar: platform
domain: player-management-mappings
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - interfaces.md
  - queries.md
includes: []
---

# Mappings: Player Management

> **Capabilities using this aspect:** [Create Player](SPEC.md#create-player) · [Players Overview](SPEC.md#players-overview) · [Create Coach](SPEC.md#create-coach) · [Assign Coach](SPEC.md#assign-coach) · [Unassign Coach](SPEC.md#unassign-coach)

## CreatePlayerRequestToEntity

**From:** API Request  
**To:** CreatePlayer input  
**Direction:** Inbound

### Field Mapping

| Source Field         | Target Field    | Transform  | Notes                                                         |
| -------------------- | --------------- | ---------- | ------------------------------------------------------------- |
| body.name            | name            | direct     | Required                                                      |
| body.email           | email           | normalized | lowercase and remove special chars for canonical identity key |
| body.currentLimit    | currentLimit    | direct     | Required                                                      |
| body.initialBankroll | initialBankroll | default    | Optional                                                      |

### Validation

| Field           | Validation                                     | On Failure      |
| --------------- | ---------------------------------------------- | --------------- |
| name            | non-empty string                               | reject request  |
| email           | non-empty string                               | reject request  |
| email           | unique player email                            | return conflict |
| currentLimit    | non-empty string                               | reject request  |
| currentLimit    | one of `NL20`, `NL40`, `NL60`, `NL80`, `NL100` | reject request  |
| initialBankroll | null or non-negative number                    | reject request  |

## PlayerToOverviewDto

**From:** Player + [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot)[]  
**To:** PlayerOverviewDto  
**Direction:** Outbound

### Field Mapping

| Source Field                      | Target Field       | Transform                       | Notes                         |
| --------------------------------- | ------------------ | ------------------------------- | ----------------------------- |
| player.id                         | id                 | direct                          |                               |
| player.name                       | name               | direct                          |                               |
| player.currentLimit               | currentLimit       | direct                          |                               |
| player.status                     | status             | direct                          |                               |
| player.bankroll                   | bankroll           | direct                          |                               |
| player.makeup                     | makeup             | direct                          |                               |
| stats[].profit                    | lifetimeProfit     | computed(sum)                   | All-time sum                  |
| stats[date>=now-periodDays].hands | avgHandsLastPeriod | computed(sum/periodDays, round) | Period defaults to 30         |
| stats[date>=now-periodDays]       | winrateLastPeriod  | computed(bb/100, round2)        | Uses requested period window  |
| query.periodDays                  | periodDays         | default(30)                     | Echo applied period in output |

---

## CreateCoachRequestToEntity

**From:** API Request  
**To:** [CreateCoach](operations.md#createcoach) input  
**Direction:** Inbound

### Field Mapping

| Source Field     | Target Field | Transform | Notes    |
| ---------------- | ------------ | --------- | -------- |
| body.principalId | principalId  | direct    | Required |
| body.name        | name         | direct    | Required |
| body.email       | email        | direct    | Required |

### Validation

| Field       | Validation       | On Failure     |
| ----------- | ---------------- | -------------- |
| principalId | non-empty string | reject request |
| name        | non-empty string | reject request |
| email       | non-empty string | reject request |

## AssignCoachRequestToInput

**From:** API Request  
**To:** [AssignCoach](operations.md#assigncoach) input  
**Direction:** Inbound

### Field Mapping

| Source Field    | Target Field | Transform | Notes         |
| --------------- | ------------ | --------- | ------------- |
| params.coachId  | coachId      | direct    | URL parameter |
| params.playerId | playerId     | direct    | URL parameter |

## UnassignCoachRequestToInput

**From:** API Request  
**To:** [UnassignCoach](operations.md#unassigncoach) input  
**Direction:** Inbound

### Field Mapping

| Source Field    | Target Field | Transform | Notes         |
| --------------- | ------------ | --------- | ------------- |
| params.coachId  | coachId      | direct    | URL parameter |
| params.playerId | playerId     | direct    | URL parameter |
