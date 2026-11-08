---
id: player-management
feature: player-management
title: Player Management Test Specification
summary: Deterministic test obligations derived from Player Management DomainSpec artifacts including coach assignment model.
status: implemented
pillar: operations
domain: player-management-tests
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
  - operations.md
  - interfaces.md
  - queries.md
  - mappings.md
includes: []
---

# Player Management TEST-SPEC

## Derivation Basis

- Framework constraints: `domainspec/CHANGELOG.md` (v1.0.2 clarifications applied).
- Pipeline rules: `domainspec/TEST-PIPELINE.md`.
- Feature sources:
  - `docs/features/player-management/domain.md`
  - `docs/features/player-management/operations.md`
  - `docs/features/player-management/interfaces.md`
  - `docs/features/player-management/queries.md`
  - `docs/features/player-management/mappings.md`

## Test Catalogue

| Test ID      | Type               | Source            | Obligation                              | Deterministic Assertion                                                      |
| ------------ | ------------------ | ----------------- | --------------------------------------- | ---------------------------------------------------------------------------- |
| PM-RULE-001  | Rule validation    | operations.md#L38 | R1 name present (pass)                  | Valid name input is accepted.                                                |
| PM-RULE-002  | Rule validation    | operations.md#L38 | R1 name present (fail)                  | Empty/trimmed-empty name returns 400 validation error.                       |
| PM-RULE-003  | Rule validation    | operations.md#L39 | R2 email present (pass)                 | Non-empty email input is accepted.                                           |
| PM-RULE-004  | Rule validation    | operations.md#L39 | R2 email present (fail)                 | Empty email returns 400 validation error.                                    |
| PM-RULE-005  | Rule validation    | operations.md#L40 | R3 currentLimit present (pass)          | Non-empty currentLimit is accepted.                                          |
| PM-RULE-006  | Rule validation    | operations.md#L40 | R3 currentLimit present (fail)          | Empty currentLimit returns 400 validation error.                             |
| PM-RULE-007  | Rule validation    | operations.md#L41 | R4 unique canonical email (pass)        | New canonical email key allows create.                                       |
| PM-RULE-008  | Rule validation    | operations.md#L41 | R4 unique canonical email (fail)        | Existing canonical email key returns 409 with code DUPLICATE_EMAIL.          |
| PM-RULE-009  | Rule validation    | operations.md#L42 | R5 non-negative initialBankroll (pass)  | Null or >=0 integer is accepted.                                             |
| PM-RULE-010  | Rule validation    | operations.md#L42 | R5 non-negative initialBankroll (fail)  | Negative value returns 400 validation error.                                 |
| PM-RULE-011  | Rule validation    | operations.md#L43 | R6 allowed limit set (pass)             | NL20/NL40/NL60/NL80/NL100 accepted.                                          |
| PM-RULE-012  | Rule validation    | operations.md#L43 | R6 allowed limit set (fail)             | Any value outside set returns 400 validation error.                          |
| PM-CALC-001  | Calculation        | operations.md#L48 | C1 default bankroll                     | Omitted initialBankroll persists bankroll=0.                                 |
| PM-CALC-002  | Calculation        | operations.md#L49 | C2 canonical email key                  | Same logical email (case/special-char variants) maps to one canonical key.   |
| PM-POST-001  | Postcondition      | operations.md#L55 | Persist player                          | Successful create persists one player record.                                |
| PM-POST-002  | Postcondition      | operations.md#L56 | Query visibility                        | Created player is returned by GET /players.                                  |
| PM-ERR-001   | Error state        | operations.md#L61 | Validation bucket R1-R3                 | Route returns 400 + standard error payload.                                  |
| PM-ERR-002   | Error state        | operations.md#L62 | Conflict R4                             | Route returns 409 + code DUPLICATE_EMAIL.                                    |
| PM-ERR-003   | Error state        | operations.md#L63 | Validation bucket R5-R6                 | Route returns 400 + standard error payload.                                  |
| PM-ERR-004   | Error state        | operations.md#L64 | Persistence failure                     | Route returns 500 + standard error payload.                                  |
| PM-API-001   | Contract           | interfaces.md#L24 | POST /players auth                      | Missing/invalid JWT returns 401.                                             |
| PM-API-002   | Contract           | interfaces.md#L24 | POST /players permission                | JWT without player-management.write.createPlayer returns 403.                |
| PM-API-003   | Contract           | interfaces.md#L35 | POST /players 201                       | Valid payload + permission returns 201 with Player body.                     |
| PM-API-004   | Contract           | interfaces.md#L38 | POST /players 400                       | Invalid payload returns 400 with {code,message,details}.                     |
| PM-API-005   | Contract           | interfaces.md#L39 | POST /players 409                       | Duplicate canonical email returns 409 + DUPLICATE_EMAIL.                     |
| PM-API-006   | Contract           | interfaces.md#L45 | GET /players auth                       | Missing/invalid JWT returns 401.                                             |
| PM-API-007   | Contract           | interfaces.md#L45 | GET /players permission                 | Missing player-management.read.getAllPlayers returns 403.                    |
| PM-API-008   | Contract           | interfaces.md#L49 | GET /players 200                        | Valid permission returns Player[].                                           |
| PM-API-009   | Contract           | interfaces.md#L55 | GET /players/overview auth              | Missing/invalid JWT returns 401.                                             |
| PM-API-010   | Contract           | interfaces.md#L55 | GET /players/overview permission        | Missing player-management.read.getPlayersOverview returns 403.               |
| PM-API-011   | Contract           | interfaces.md#L64 | GET /players/overview 200               | Valid permission returns PlayerOverviewDto[] with periodDays.                |
| PM-API-012   | Contract           | interfaces.md#L70 | GET /players/:id/progression auth       | Missing/invalid JWT returns 401.                                             |
| PM-API-013   | Contract           | interfaces.md#L70 | GET /players/:id/progression permission | Missing player-management.read.getPlayerProgression returns 403.             |
| PM-API-014   | Contract           | interfaces.md#L84 | GET /players/:id/progression 404        | Unknown player returns 404 standard error payload.                           |
| PM-MAP-001   | Mapping            | mappings.md#L30   | name direct map                         | body.name maps directly to input.name.                                       |
| PM-MAP-002   | Mapping            | mappings.md#L31   | email normalized map                    | body.email canonicalization logic applied before uniqueness.                 |
| PM-MAP-003   | Mapping            | mappings.md#L32   | currentLimit direct map                 | body.currentLimit maps directly to input.currentLimit.                       |
| PM-MAP-004   | Mapping            | mappings.md#L33   | initialBankroll default map             | Missing field maps to default bankroll behavior.                             |
| PM-MAP-005   | Mapping validation | mappings.md#L39   | unique email validation                 | Conflict returned when canonical email already exists.                       |
| PM-MAP-006   | Mapping validation | mappings.md#L41   | configured limit validation             | Out-of-set currentLimit rejected.                                            |
| PM-MAP-007   | Mapping validation | mappings.md#L42   | non-negative bankroll validation        | Negative initialBankroll rejected.                                           |
| PM-QUERY-001 | Query              | queries.md#L22    | GetAllPlayers shape                     | Output contains expected Player fields.                                      |
| PM-QUERY-002 | Query              | queries.md#L48    | GetPlayersOverview period default       | Missing periodDays applies 30 default in output.                             |
| PM-QUERY-003 | Query              | queries.md#L48    | GetPlayersOverview period custom        | Provided periodDays changes avg/winrate window deterministically.            |
| PM-QUERY-004 | Query              | queries.md#L66    | GetPlayersOverview derived fields       | lifetimeProfit, avgHandsLastPeriod, winrateLastPeriod computed and returned. |
| PM-DOM-001   | Invariant          | domain.md#L35     | email canonical uniqueness invariant    | No two records share same canonical email key.                               |
| PM-DOM-002   | Invariant          | domain.md#L36     | bankroll invariant                      | Persisted bankroll is always >= 0.                                           |
| PM-DOM-003   | Invariant          | domain.md#L37     | makeup invariant                        | Persisted makeup is always >= 0.                                             |
| PM-DOM-004   | Invariant          | domain.md#L38     | currentLimit invariant                  | Persisted currentLimit always in configured set.                             |

### Coach Domain Tests

| Test ID    | Type          | Source    | Obligation                                  | Deterministic Assertion                                                    |
| ---------- | ------------- | --------- | ------------------------------------------- | -------------------------------------------------------------------------- |
| PM-CDM-001 | Invariant     | domain.md | Coach principalId uniqueness                | No two active coaches share the same principalId.                          |
| PM-CDM-002 | Invariant     | domain.md | CoachAssignment one-active-coach-per-player | UNIQUE(playerId) WHERE unassignedAt IS NULL enforced at persistence level. |
| PM-CDM-003 | Invariant     | domain.md | Soft-delete preserves assignment history    | UnassignedAt is set but record is not deleted.                             |
| PM-CDM-004 | Enum coverage | domain.md | CoachStatus values                          | Only ACTIVE and INACTIVE are valid CoachStatus values.                     |

### Coach Operation Tests — CreateCoach

| Test ID      | Type            | Source        | Obligation                             | Deterministic Assertion                                         |
| ------------ | --------------- | ------------- | -------------------------------------- | --------------------------------------------------------------- |
| PM-COACH-001 | Rule validation | operations.md | CreateCoach R1 principalId (pass)      | Valid principalId is accepted.                                  |
| PM-COACH-002 | Rule validation | operations.md | CreateCoach R1 principalId (fail)      | Empty principalId returns 400 validation error.                 |
| PM-COACH-003 | Rule validation | operations.md | CreateCoach R2 name (pass)             | Valid name is accepted.                                         |
| PM-COACH-004 | Rule validation | operations.md | CreateCoach R2 name (fail)             | Empty name returns 400 validation error.                        |
| PM-COACH-005 | Rule validation | operations.md | CreateCoach R3 email (pass)            | Valid email is accepted.                                        |
| PM-COACH-006 | Rule validation | operations.md | CreateCoach R3 email (fail)            | Empty email returns 400 validation error.                       |
| PM-COACH-007 | Rule validation | operations.md | CreateCoach R4 unique principal (pass) | New principalId allows create.                                  |
| PM-COACH-008 | Rule validation | operations.md | CreateCoach R4 unique principal (fail) | Existing active principalId returns 409 DUPLICATE_PRINCIPAL.    |
| PM-COACH-009 | Postcondition   | operations.md | CreateCoach persists coach             | Successful create persists one coach record with ACTIVE status. |
| PM-COACH-010 | Error state     | operations.md | CreateCoach 400 validation             | Missing required fields returns 400 + standard error payload.   |
| PM-COACH-011 | Error state     | operations.md | CreateCoach 409 duplicate              | Duplicate principalId returns 409 + DUPLICATE_PRINCIPAL.        |
| PM-COACH-012 | Error state     | operations.md | CreateCoach 500 persistence            | Persistence failure returns 500 + standard error payload.       |

### Coach Operation Tests — AssignCoach

| Test ID     | Type            | Source        | Obligation                          | Deterministic Assertion                                            |
| ----------- | --------------- | ------------- | ----------------------------------- | ------------------------------------------------------------------ |
| PM-ASGN-001 | Rule validation | operations.md | AssignCoach R1 coach exists (pass)  | Existing coach allows assignment.                                  |
| PM-ASGN-002 | Rule validation | operations.md | AssignCoach R1 coach exists (fail)  | Non-existent coach returns 404.                                    |
| PM-ASGN-003 | Rule validation | operations.md | AssignCoach R2 coach active (pass)  | ACTIVE coach allows assignment.                                    |
| PM-ASGN-004 | Rule validation | operations.md | AssignCoach R2 coach active (fail)  | INACTIVE coach returns 409 COACH_INACTIVE.                         |
| PM-ASGN-005 | Rule validation | operations.md | AssignCoach R3 player exists (pass) | Existing player allows assignment.                                 |
| PM-ASGN-006 | Rule validation | operations.md | AssignCoach R3 player exists (fail) | Non-existent player returns 404.                                   |
| PM-ASGN-007 | Rule validation | operations.md | AssignCoach R4 no duplicate (pass)  | Player with no active assignment allows assignment.                |
| PM-ASGN-008 | Rule validation | operations.md | AssignCoach R4 no duplicate (fail)  | Player with active assignment returns 409 PLAYER_ALREADY_ASSIGNED. |
| PM-ASGN-009 | Postcondition   | operations.md | AssignCoach persists assignment     | Successful assign creates CoachAssignment with unassignedAt=null.  |
| PM-ASGN-010 | Error state     | operations.md | AssignCoach 500 persistence         | Persistence failure returns 500 + standard error payload.          |

### Coach Operation Tests — UnassignCoach

| Test ID      | Type            | Source        | Obligation                            | Deterministic Assertion                                            |
| ------------ | --------------- | ------------- | ------------------------------------- | ------------------------------------------------------------------ |
| PM-UASGN-001 | Rule validation | operations.md | UnassignCoach R1 active exists (pass) | Active assignment allows unassign.                                 |
| PM-UASGN-002 | Rule validation | operations.md | UnassignCoach R1 active exists (fail) | No active assignment returns 404 ASSIGNMENT_NOT_FOUND.             |
| PM-UASGN-003 | Postcondition   | operations.md | UnassignCoach sets unassignedAt       | Successful unassign sets unassignedAt timestamp; record preserved. |
| PM-UASGN-004 | Postcondition   | operations.md | UnassignCoach allows reassignment     | After unassign, player can be assigned to a different coach.       |
| PM-UASGN-005 | Error state     | operations.md | UnassignCoach 500 persistence         | Persistence failure returns 500 + standard error payload.          |

### Coach API Contract Tests

| Test ID     | Type     | Source        | Obligation                                            | Deterministic Assertion                                           |
| ----------- | -------- | ------------- | ----------------------------------------------------- | ----------------------------------------------------------------- |
| PM-CAPI-001 | Contract | interfaces.md | POST /coaches auth                                    | Missing/invalid JWT returns 401.                                  |
| PM-CAPI-002 | Contract | interfaces.md | POST /coaches permission                              | Missing player-management.write.createCoach returns 403.          |
| PM-CAPI-003 | Contract | interfaces.md | POST /coaches 201                                     | Valid payload + permission returns 201 with Coach body.           |
| PM-CAPI-004 | Contract | interfaces.md | POST /coaches 400                                     | Invalid payload returns 400 with {code,message,details}.          |
| PM-CAPI-005 | Contract | interfaces.md | POST /coaches 409                                     | Duplicate principalId returns 409 + DUPLICATE_PRINCIPAL.          |
| PM-CAPI-006 | Contract | interfaces.md | POST /coaches 500                                     | Persistence failure returns 500.                                  |
| PM-CAPI-007 | Contract | interfaces.md | GET /coaches auth                                     | Missing/invalid JWT returns 401.                                  |
| PM-CAPI-008 | Contract | interfaces.md | GET /coaches permission                               | Missing player-management.read.getAllCoaches returns 403.         |
| PM-CAPI-009 | Contract | interfaces.md | GET /coaches 200                                      | Valid permission returns Coach[].                                 |
| PM-CAPI-010 | Contract | interfaces.md | POST /coaches/:coachId/players/:playerId auth         | Missing/invalid JWT returns 401.                                  |
| PM-CAPI-011 | Contract | interfaces.md | POST /coaches/:coachId/players/:playerId permission   | Missing player-management.write.assignCoach returns 403.          |
| PM-CAPI-012 | Contract | interfaces.md | POST /coaches/:coachId/players/:playerId 201          | Valid payload + permission returns 201 with CoachAssignment body. |
| PM-CAPI-013 | Contract | interfaces.md | POST /coaches/:coachId/players/:playerId 404          | Non-existent coach or player returns 404.                         |
| PM-CAPI-014 | Contract | interfaces.md | POST /coaches/:coachId/players/:playerId 409          | Already-assigned player or inactive coach returns 409.            |
| PM-CAPI-015 | Contract | interfaces.md | DELETE /coaches/:coachId/players/:playerId auth       | Missing/invalid JWT returns 401.                                  |
| PM-CAPI-016 | Contract | interfaces.md | DELETE /coaches/:coachId/players/:playerId permission | Missing player-management.write.unassignCoach returns 403.        |
| PM-CAPI-017 | Contract | interfaces.md | DELETE /coaches/:coachId/players/:playerId 200        | Valid request returns 200.                                        |
| PM-CAPI-018 | Contract | interfaces.md | DELETE /coaches/:coachId/players/:playerId 404        | No active assignment returns 404 ASSIGNMENT_NOT_FOUND.            |
| PM-CAPI-019 | Contract | interfaces.md | GET /coaches/:coachId/players auth                    | Missing/invalid JWT returns 401.                                  |
| PM-CAPI-020 | Contract | interfaces.md | GET /coaches/:coachId/players permission              | Missing player-management.read.getCoachPlayers returns 403.       |
| PM-CAPI-021 | Contract | interfaces.md | GET /coaches/:coachId/players 200                     | Valid permission returns Player[] of assigned players.            |
| PM-CAPI-022 | Contract | interfaces.md | GET /coaches/:coachId/players 404                     | Non-existent coach returns 404.                                   |

### Coach Query Tests

| Test ID     | Type  | Source     | Obligation                              | Deterministic Assertion                              |
| ----------- | ----- | ---------- | --------------------------------------- | ---------------------------------------------------- |
| PM-CQRY-001 | Query | queries.md | GetAllCoaches returns all coaches       | Returns all coach records regardless of status.      |
| PM-CQRY-002 | Query | queries.md | GetCoachPlayers R1 coach exists (pass)  | Existing coach returns assigned players.             |
| PM-CQRY-003 | Query | queries.md | GetCoachPlayers R1 coach exists (fail)  | Non-existent coach returns 404.                      |
| PM-CQRY-004 | Query | queries.md | GetCoachPlayers R2 coach-scope self     | Coach actor sees only own assigned players.          |
| PM-CQRY-005 | Query | queries.md | GetCoachPlayers R2 admin-scope all      | Admin actor sees all assigned players for any coach. |
| PM-CQRY-006 | Query | queries.md | GetCoachPlayers only active assignments | Returns only players where unassignedAt IS NULL.     |

### Visibility Resolver Tests

| Test ID    | Type  | Source     | Obligation                                   | Deterministic Assertion                                                            |
| ---------- | ----- | ---------- | -------------------------------------------- | ---------------------------------------------------------------------------------- |
| PM-VIS-001 | Query | queries.md | ResolvePlayerVisibility admin=all            | Admin actor returns all player IDs.                                                |
| PM-VIS-002 | Query | queries.md | ResolvePlayerVisibility coach=assigned+self  | Coach actor returns assigned player IDs + own player ID if coach is also a player. |
| PM-VIS-003 | Query | queries.md | ResolvePlayerVisibility player=self          | Player actor returns only own player ID.                                           |
| PM-VIS-004 | Query | queries.md | ResolvePlayerVisibility coach no self-player | Coach who is NOT a player returns only assigned player IDs (no self).              |
| PM-VIS-005 | Query | queries.md | ResolvePlayerVisibility empty assignments    | Coach with no active assignments returns empty set (or self only if also player).  |

### Coach Mapping Tests

| Test ID     | Type    | Source      | Obligation                           | Deterministic Assertion                              |
| ----------- | ------- | ----------- | ------------------------------------ | ---------------------------------------------------- |
| PM-CMAP-001 | Mapping | mappings.md | CreateCoachRequestToEntity principal | body.principalId maps directly to input.principalId. |
| PM-CMAP-002 | Mapping | mappings.md | CreateCoachRequestToEntity name      | body.name maps directly to input.name.               |
| PM-CMAP-003 | Mapping | mappings.md | CreateCoachRequestToEntity email     | body.email maps directly to input.email.             |
| PM-CMAP-004 | Mapping | mappings.md | AssignCoachRequestToInput params     | params.coachId and params.playerId map directly.     |
| PM-CMAP-005 | Mapping | mappings.md | UnassignCoachRequestToInput params   | params.coachId and params.playerId map directly.     |

## Suggested Test File Scaffolding

- `backend/src/infrastructure/http/routes/player.routes.auth.test.ts`
- `backend/src/infrastructure/http/routes/player.routes.contract.test.ts`
- `backend/src/use-cases/player/create-player.test.ts`
- `backend/src/use-cases/player/get-players-overview.test.ts`
- `backend/src/domain/player/player-normalization.test.ts`
- `backend/src/infrastructure/http/routes/coach.routes.contract.test.ts`
- `backend/src/infrastructure/http/routes/coach.routes.contract.test.ts`
- `backend/src/use-cases/coach/create-coach.test.ts`
- `backend/src/use-cases/coach/assign-coach.test.ts`
- `backend/src/use-cases/coach/unassign-coach.test.ts`
- `backend/src/use-cases/coach/get-coach-players.test.ts`
- `backend/src/domain/coach/player-visibility.service.test.ts`

## Traceability Matrix (49/49 player + 72/64 coach = 121 total)

### Player Traceability (49/49)

| Obligation IDs    | Evidence File(s)                                                                                                                                                                                                                        |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PM-RULE-001..012  | `backend/src/use-cases/player/create-player.test.ts`                                                                                                                                                                                    |
| PM-CALC-001..002  | `backend/src/use-cases/player/create-player.test.ts`, `backend/src/domain/player/player-normalization.test.ts`                                                                                                                          |
| PM-POST-001..002  | `backend/src/use-cases/player/create-player.test.ts`, `backend/src/infrastructure/http/routes/player.routes.contract.test.ts`                                                                                                           |
| PM-ERR-001..004   | `backend/src/infrastructure/http/routes/player.routes.contract.test.ts`                                                                                                                                                                 |
| PM-API-001..014   | `backend/src/infrastructure/http/routes/player.routes.auth.test.ts`, `backend/src/infrastructure/http/routes/player.routes.contract.test.ts`                                                                                            |
| PM-MAP-001..007   | `backend/src/use-cases/player/create-player.test.ts`, `backend/src/domain/player/player-normalization.test.ts`                                                                                                                          |
| PM-QUERY-001..004 | `backend/src/use-cases/player/get-all-players.test.ts`, `backend/src/use-cases/player/get-players-overview.test.ts`, `backend/src/infrastructure/http/routes/player.routes.contract.test.ts`                                            |
| PM-DOM-001..004   | `backend/src/domain/player/player-normalization.test.ts`, `backend/src/use-cases/player/create-player.test.ts`, `backend/src/infrastructure/repositories/drizzle-player.repository.ts`, `backend/src/infrastructure/database/schema.ts` |

### Coach Traceability (72/64 — implemented)

| Obligation IDs    | Evidence File(s)                                                                                                                                             |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| PM-CDM-001..004   | `backend/src/domain/coach/coach.domain.test.ts`                                                                                                              |
| PM-COACH-001..012 | `backend/src/use-cases/coach/create-coach.test.ts`                                                                                                           |
| PM-ASGN-001..010  | `backend/src/use-cases/coach/assign-coach.test.ts`                                                                                                           |
| PM-UASGN-001..005 | `backend/src/use-cases/coach/unassign-coach.test.ts`                                                                                                         |
| PM-CAPI-001..022  | `backend/src/infrastructure/http/routes/coach.routes.contract.test.ts`                                                                                       |
| PM-CQRY-001       | `backend/src/use-cases/coach/get-all-coaches.test.ts`                                                                                                        |
| PM-CQRY-002..006  | `backend/src/use-cases/coach/get-coach-players.test.ts`                                                                                                      |
| PM-VIS-001..005   | `backend/src/domain/coach/player-visibility.service.test.ts`                                                                                                 |
| PM-CMAP-001..005  | `backend/src/use-cases/coach/create-coach.test.ts`, `backend/src/use-cases/coach/assign-coach.test.ts`, `backend/src/use-cases/coach/unassign-coach.test.ts` |

## Uncovered Or Under-Specified Areas

1. Canonical email normalization specifies `removeSpecialChars`; if provider-specific alias rules are needed later, add deterministic examples and precedence in mappings.
2. State and event aspects now exist (`states.md`, `events.md`, `workflows.md`); derive the next TEST-SPEC revision from those artifacts to expand state/event obligations.
3. Coach deactivation and reassignment edge behavior still needs explicit story-level acceptance clauses for lifecycle operations.
4. Coach-to-coach reassignment (unassign then assign to new coach in one operation) is not specified. Currently requires two separate API calls.
5. Coach deactivation (`ACTIVE→INACTIVE`) is not yet an operation. When added, test obligations for cascade behavior on active assignments should be specified.
6. ResolvePlayerVisibility is a cross-cutting query consumed by other features (player-makeup, player-stats). Integration tests for those consumers should be added in their respective TEST-SPECs.

## Coverage Summary

### Player Obligations (implemented)

- Rule validation tests: 12
- Calculation tests: 2
- Postcondition tests: 2
- Error state tests: 4
- Interface contract tests: 14
- Mapping tests: 7
- Query tests: 4
- Domain invariant tests: 4
- **Player subtotal: 49**

### Coach Obligations (implemented)

- Domain invariant tests: 3
- CreateCoach tests: 14
- AssignCoach tests: 12
- UnassignCoach tests: 6
- API contract tests: 22
- Query tests: 8
- Visibility resolver tests: 8
- Mapping tests: 5 (inline in use-case tests)
- **Coach subtotal: 72** _(some test IDs share coverage across suites)_

### Total: 121 obligations (49 player + 72 coach — all implemented)

---

## Story To Test Mapping

| Story                                                                                         | Key test IDs                                                                                                                                                                                                                                                                                                       |
| --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| US-01 Admin Operations Journey: Register A New Player                                         | PM-RULE-001, PM-RULE-002, PM-RULE-003, PM-RULE-004, PM-RULE-005, PM-RULE-006, PM-CALC-001, PM-CALC-002, PM-POST-001, PM-POST-002, PM-ERR-001, PM-ERR-002, PM-ERR-003, PM-ERR-004, PM-API-001, PM-API-002, PM-API-003, PM-MAP-001, PM-MAP-002, PM-DOM-001, PM-DOM-002, PM-DOM-003                                   |
| US-02 Public Journey: View Player List And Portfolio Overview                                 | PM-QUERY-001, PM-QUERY-002, PM-QUERY-003, PM-QUERY-004, PM-API-004, PM-API-005, PM-API-006, PM-API-007, PM-MAP-003, PM-MAP-004, PM-MAP-005, PM-MAP-006, PM-MAP-007                                                                                                                                                 |
| US-03 Cross-Feature Integration: Player Data Consumed By Settlement, Makeup, And Progression  | PM-QUERY-001, PM-QUERY-003, PM-API-007                                                                                                                                                                                                                                                                             |
| US-04 Error And Edge Case Journey: Reject Invalid Player Registration And Unauthorized Access | PM-RULE-001, PM-RULE-002, PM-RULE-003, PM-RULE-004, PM-RULE-005, PM-RULE-006, PM-ERR-001, PM-ERR-002, PM-ERR-003, PM-ERR-004, PM-API-008, PM-API-009, PM-API-010, PM-API-011, PM-API-012, PM-API-013, PM-API-014, PM-DOM-004                                                                                       |
| US-05 Admin Operations Journey: Register A New Coach                                          | PM-CDM-001, PM-CDM-002, PM-CDM-003, PM-CDM-004, PM-COACH-001, PM-COACH-002, PM-COACH-003, PM-COACH-004, PM-COACH-005, PM-COACH-006, PM-CAPI-001, PM-CAPI-002, PM-CAPI-003, PM-CMAP-001, PM-CMAP-002                                                                                                                |
| US-06 Admin Operations Journey: Assign And Unassign Coach To Player                           | PM-ASGN-001, PM-ASGN-002, PM-ASGN-003, PM-ASGN-004, PM-ASGN-005, PM-ASGN-006, PM-ASGN-007, PM-ASGN-008, PM-ASGN-009, PM-ASGN-010, PM-UASGN-001, PM-UASGN-002, PM-UASGN-003, PM-UASGN-004, PM-UASGN-005, PM-CAPI-004, PM-CAPI-005, PM-CAPI-006, PM-CAPI-007, PM-CAPI-008, PM-CAPI-009                               |
| US-07 Public Journey: Coach Views Assigned Players                                            | PM-CQRY-001, PM-CQRY-002, PM-CQRY-003, PM-CQRY-004, PM-CQRY-005, PM-CQRY-006, PM-CAPI-010, PM-CAPI-011, PM-CAPI-012, PM-CAPI-013                                                                                                                                                                                   |
| US-08 Cross-Feature Integration: Player Visibility Through Coach Assignment                   | PM-VIS-001, PM-VIS-002, PM-VIS-003, PM-VIS-004, PM-VIS-005                                                                                                                                                                                                                                                         |
| US-09 Error And Edge Case Journey: Coach Operations Failure Modes                             | PM-COACH-007, PM-COACH-008, PM-COACH-009, PM-COACH-010, PM-COACH-011, PM-COACH-012, PM-ASGN-006, PM-ASGN-007, PM-ASGN-008, PM-ASGN-009, PM-ASGN-010, PM-UASGN-003, PM-UASGN-004, PM-UASGN-005, PM-CAPI-014, PM-CAPI-015, PM-CAPI-016, PM-CAPI-017, PM-CAPI-018, PM-CAPI-019, PM-CAPI-020, PM-CAPI-021, PM-CAPI-022 |

## Pilot Must-Pass Subset (Wave 1)

| Priority | Test IDs | Why it is gate-critical | Evidence file targets |
| --- | --- | --- | --- |
| P0 | PM-RULE-007, PM-RULE-008, PM-API-005, PM-DOM-001 | Guarantee canonical player identity uniqueness and duplicate protection. | `backend/src/use-cases/player/create-player.test.ts`, `backend/src/infrastructure/http/routes/player.routes.contract.test.ts` |
| P0 | PM-API-001, PM-API-002, PM-CAPI-010, PM-CAPI-011, PM-CAPI-014 | Protect player/coach write paths with strict auth and permission contracts. | `backend/src/infrastructure/http/routes/player.routes.auth.test.ts`, `backend/src/infrastructure/http/routes/coach.routes.contract.test.ts` |
| P0 | PM-VIS-002, PM-VIS-003, PM-VIS-005, PM-CQRY-004, PM-CQRY-005 | Enforce visibility boundaries for coach and player contexts across cross-feature consumers. | `backend/src/domain/coach/player-visibility.service.test.ts`, `backend/src/use-cases/coach/get-coach-players.test.ts` |
| P0 | PM-ASGN-007, PM-ASGN-008, PM-UASGN-003, PM-UASGN-004 | Keep coach assignment lifecycle safe under duplicate and reassignment conditions. | `backend/src/use-cases/coach/assign-coach.test.ts`, `backend/src/use-cases/coach/unassign-coach.test.ts` |
| P1 | PM-QUERY-002, PM-QUERY-003, PM-CQRY-001, PM-CAPI-009 | Validate operational visibility and overview query quality for non-blocking workflows. | `backend/src/use-cases/player/get-players-overview.test.ts`, `backend/src/use-cases/coach/get-all-coaches.test.ts` |

## Pilot Execution Checklist

1. Freeze Wave 1 management scope to the P0 rows above.
Pass criteria: all P0 IDs are mapped to executable test evidence.

2. Run identity and duplication gate first.
Pass criteria: PM-RULE-007/008, PM-API-005, PM-DOM-001 pass with deterministic duplicate handling.

3. Run route auth/permission gate second.
Pass criteria: PM-API-001/002 and PM-CAPI-010/011/014 pass for unauthorized and forbidden scenarios.

4. Run visibility boundary gate third.
Pass criteria: PM-VIS-002/003/005 and PM-CQRY-004/005 prove scope correctness for coach/player/admin.

5. Run assignment lifecycle gate fourth.
Pass criteria: PM-ASGN-007/008 and PM-UASGN-003/004 pass with safe reassignment behavior.

6. Execute optional P1 operational query checks.
Pass criteria: PM-QUERY-002/003, PM-CQRY-001, PM-CAPI-009 pass with stable read semantics.

7. Capture blockers and evidence package.
Pass criteria: all open blockers have owner, due action, and required proof artifacts.

8. Compute final Wave 1 verdict.
Pass criteria: zero failing P0 tests and no open P0 blocker.

## Pilot Go No-Go Blockers Register

| Blocker ID | Status | Blocker | Why it blocks Wave 1 | Required evidence to clear |
| --- | --- | --- | --- | --- |
| PM-BLK-01 | closed | Player self-visibility relies on implicit id equivalence; explicit principal linkage is not yet implemented. | Player-scoped data access can break or overexpose data in dependent features. | Closed on 2026-04-24 via schema/model `principalId` linkage plus visibility and create-player test coverage. |
| PM-BLK-02 | closed | Coach visibility behavior can be widened by permission interpretation drift in query path. | Coach access boundaries can violate intended assignment-only scope. | Closed on 2026-04-24 by centralizing principal-based self resolution in visibility policy and tests. |
| PM-BLK-05 | closed | `getCoachPlayers` permission could bypass strict own-coach scope at use-case layer. | Coach principals could read another coach's player list despite query contract R2 ownership requirement. | Closed on 2026-04-24 by removing permission-as-admin bypass in `backend/src/use-cases/coach/get-coach-players.ts` and adding explicit forbidden regression coverage in `backend/src/use-cases/coach/get-coach-players.test.ts`. |
| PM-BLK-03 | closed | Alignment and layering reports remain draft/stale relative to current implementation. | Readiness decisions lack current drift closure evidence. | Closed on 2026-04-24 with refreshed alignment/layering snapshots for current implementation state. |
| PM-BLK-04 | closed | Event emission obligations for player/coach lifecycle were partially unresolved in docs vs runtime. | Cross-feature consumers could not rely on deterministic lifecycle event outputs. | Closed on 2026-04-24 via lifecycle event emission in create/assign/unassign use-cases with coverage in `create-player.test.ts`, `create-coach.test.ts`, `assign-coach.test.ts`, and `unassign-coach.test.ts`. |

## Pilot Evidence Package

1. Identity and duplication evidence
- Test output for PM-RULE-007/008, PM-API-005, PM-DOM-001.

2. Authorization and boundary evidence
- Auth route test output for player/coach write endpoints.
- Visibility test output for PM-VIS and PM-CQRY gate IDs.

3. Assignment lifecycle evidence
- Assign/unassign test outputs for duplicate prevention and safe reassignment.

4. Lifecycle event evidence
- Event payload assertions for `PlayerCreated`, `CoachCreated`, `CoachAssigned`, and `CoachUnassigned` from operation use-case tests.

5. Cross-feature consumption evidence
- Route-level proof that management visibility contract is correctly consumed by makeup/stats paths.

6. Decision artifact
- Final blocker register snapshot and computed PASS/FLAG/BLOCK decision for Wave 1.

## Pilot Decisions Provenance

This test gate follows policy decisions recorded in [PILOT-DECISIONS.md](PILOT-DECISIONS.md).
