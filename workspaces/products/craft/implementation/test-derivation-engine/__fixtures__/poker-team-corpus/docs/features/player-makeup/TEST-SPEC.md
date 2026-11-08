---
id: player-makeup
feature: player-makeup
title: Player Makeup Test Specification
summary: Deterministic test obligations derived from Player Makeup DomainSpec artifacts.
status: implemented
pillar: finance
domain: player-makeup-tests
audience:
  - developers
priority: p1
lang: en
owners:
  - finance-core
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - domain.md
  - states.md
  - operations.md
  - interfaces.md
  - events.md
  - queries.md
  - workflows.md
  - mappings.md
includes: []
---

# Player Makeup TEST-SPEC

## Derivation Basis

- Framework constraints: `domainspec/CHANGELOG.md` (v1.1.0 delegation clarifications applied; DomainSpec remains semantic authority).
- Pipeline rules: `domainspec/TEST-PIPELINE.md`.
- Feature sources:
  - `docs/features/player-makeup/states.md`
  - `docs/features/player-makeup/operations.md`
  - `docs/features/player-makeup/interfaces.md`
  - `docs/features/player-makeup/events.md`
  - `docs/features/player-makeup/queries.md`
  - `docs/features/player-makeup/workflows.md`
  - `docs/features/player-makeup/mappings.md`
  - `docs/features/player-makeup/domain.md`

## Test Catalogue

| Test ID | Type | Source | Obligation | Deterministic Assertion |
| --- | --- | --- | --- | --- |
| PMK-STATE-001 | Transition | states.md#makeupdebtstate | Settled + MakeupAdjusted -> InDebt | With operation that results in `amount > 0`, state transitions from Settled to InDebt. |
| PMK-STATE-002 | Transition | states.md#makeupdebtstate | InDebt + MakeupAdjusted -> InDebt | With resulting debt `> 0`, state remains InDebt and debt updates. |
| PMK-STATE-003 | Transition | states.md#makeupdebtstate | InDebt + MakeupAdjusted -> Settled | With resulting debt `== 0`, state transitions to Settled. |
| PMK-STATE-004 | Transition | states.md#makeupdebtstate | InDebt + MakeupApplied -> Settled | With `applied amount >= previous debt`, debt is cleared and state becomes Settled. |
| PMK-NEG-001 | Negative transition | states.md#invalid-transition-table | Settled rejects MakeupApplied | Applying makeup while already Settled is rejected and state remains Settled. |
| PMK-NEG-002 | Negative transition | states.md#invalid-transition-table | Settled guard not satisfied | `MakeupAdjusted` with resulting amount `== 0` does not transition to InDebt. |
| PMK-NEG-003 | Negative transition | states.md#invalid-transition-table | InDebt guard not satisfied on MakeupApplied | If `applied amount < previous debt`, transition to Settled is rejected and state remains InDebt. |
| PMK-INV-001 | Invariant | states.md#invariants | I1 non-negative debt | For all reachable states, `makeup >= 0` holds. |
| PMK-INV-002 | Invariant | states.md#invariants | I2 no zero-delta adjustment event | If `delta == 0`, no MAKEUP_ADJUSTMENT transaction/event is created. |
| PMK-RULE-001 | Rule validation | operations.md#rules | R1 player exists (pass) | Existing playerId is accepted. |
| PMK-RULE-002 | Rule validation | operations.md#rules | R1 player exists (fail) | Unknown playerId returns 404 domain error. |
| PMK-RULE-003 | Rule validation | operations.md#rules | R2 finite non-negative amount (pass) | Finite amount `>= 0` is accepted. |
| PMK-RULE-004 | Rule validation | operations.md#rules | R2 finite non-negative amount (fail) | NaN, Infinity, or negative amount returns 400 validation error. |
| PMK-RULE-005 | Rule validation | operations.md#rules | R3 valid operation (pass) | `increase`, `decrease`, `set` are accepted. |
| PMK-RULE-006 | Rule validation | operations.md#rules | R3 valid operation (fail) | Any operation outside allowed set returns 400 validation error. |
| PMK-CALC-001 | Calculation | operations.md#calculations | C1 normalization integer input | Integer amount remains unchanged after `floor(amount + 0.5)`. |
| PMK-CALC-002 | Calculation | operations.md#rounding-rule | C1 normalization tie-break cases | `0.50 -> 1` and `1.50 -> 2` with half-up rounding for non-negative values. |
| PMK-CALC-003 | Calculation | operations.md#calculations | C2 increase formula | `current = previous + normalized` for operation increase. |
| PMK-CALC-004 | Calculation | operations.md#calculations | C3 decrease floor formula | `current = max(0, previous - normalized)` for decrease; never negative. |
| PMK-CALC-005 | Calculation | operations.md#calculations | C4 set floor formula | `current = max(0, normalized)` for set. |
| PMK-CALC-006 | Calculation | operations.md#calculations | C5 signed delta formula | `delta = current - previous` for all operation modes. |
| PMK-POST-001 | Postcondition | operations.md#postconditions | Persist updated makeup | Successful mutation persists new non-negative makeup value. |
| PMK-POST-002 | Postcondition | operations.md#postconditions | Conditional audit transaction | MAKEUP_ADJUSTMENT transaction is created only when `delta != 0`. |
| PMK-ERR-001 | Error state | operations.md#error-states | Player not found | Returns 404 structured domain error. |
| PMK-ERR-002 | Error state | operations.md#error-states | Invalid amount | Returns 400 structured validation error. |
| PMK-ERR-003 | Error state | operations.md#error-states | Persistence failure | Returns 500 structured internal error. |
| PMK-API-001 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup 200 | Authorized request returns makeup snapshot shape. |
| PMK-API-002 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup 401 | Missing/invalid token returns structured 401. |
| PMK-API-003 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup 403 | Missing permission returns structured 403. |
| PMK-API-004 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup 404 | Unknown player returns structured 404. |
| PMK-API-005 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup 500 | Unexpected failure returns structured 500. |
| PMK-API-006 | Contract | interfaces.md#external-makeupapi-rest | PATCH /players/:id/makeup 200 | Valid request returns adjustment result shape. |
| PMK-API-007 | Contract | interfaces.md#external-makeupapi-rest | PATCH /players/:id/makeup 401 | Missing/invalid token returns structured 401. |
| PMK-API-008 | Contract | interfaces.md#external-makeupapi-rest | PATCH /players/:id/makeup 403 | Missing permission returns structured 403. |
| PMK-API-009 | Contract | interfaces.md#external-makeupapi-rest | PATCH /players/:id/makeup 400 | Invalid operation/amount returns structured 400. |
| PMK-API-010 | Contract | interfaces.md#external-makeupapi-rest | PATCH /players/:id/makeup 404 | Unknown player returns structured 404. |
| PMK-API-011 | Contract | interfaces.md#external-makeupapi-rest | PATCH /players/:id/makeup 500 | Unexpected failure returns structured 500. |
| PMK-API-012 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup/history 200 | Authorized request returns history shape with entries list. |
| PMK-API-013 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup/history 401 | Missing/invalid token returns structured 401. |
| PMK-API-014 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup/history 403 | Missing permission returns structured 403. |
| PMK-API-015 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup/history 404 | Unknown player returns structured 404. |
| PMK-API-016 | Contract | interfaces.md#external-makeupapi-rest | GET /players/:id/makeup/history 500 | Unexpected failure returns structured 500. |
| PMK-API-017 | Contract | interfaces.md#external-makeupapi-rest | GET /players/makeup/policy 200 | Authorized request returns policy snapshot shape. |
| PMK-API-018 | Contract | interfaces.md#external-makeupapi-rest | GET /players/makeup/policy 401 | Missing/invalid token returns structured 401. |
| PMK-API-019 | Contract | interfaces.md#external-makeupapi-rest | GET /players/makeup/policy 403 | Missing permission returns structured 403. |
| PMK-API-020 | Contract | interfaces.md#external-makeupapi-rest | GET /players/makeup/policy 500 | Unexpected failure returns structured 500. |
| PMK-API-021 | Contract | interfaces.md#external-playerdirectoryapi-rest | GET /players 200 | Authorized request returns player list containing `id,name,currentLimit,status,makeup`. |
| PMK-API-022 | Contract | interfaces.md#external-playerdirectoryapi-rest | GET /players 401 | Missing/invalid token returns structured 401. |
| PMK-API-023 | Contract | interfaces.md#external-playerdirectoryapi-rest | GET /players 403 | Missing permission returns structured 403. |
| PMK-API-029 | Contract | interfaces.md#external-playerdirectoryapi-rest | GET /players 500 | Unexpected failure returns structured 500. |
| PMK-API-024 | Field mapping | interfaces.md#external-makeupapi-rest | params.id -> playerId | `params.id` is passed as `AdjustPlayerMakeup.playerId`. |
| PMK-API-025 | Field mapping | interfaces.md#external-makeupapi-rest | body.operation -> operation | `body.operation` is passed without semantic drift. |
| PMK-API-026 | Field mapping | interfaces.md#external-makeupapi-rest | body.amount -> amount | `body.amount` is passed to operation input amount. |
| PMK-API-030 | Field mapping | interfaces.md#external-makeupapi-rest | body.reasonCode -> reasonCode | `body.reasonCode` is required and is passed to adjustment input without semantic drift. |
| PMK-API-027 | Contract | interfaces.md#error-contract | Standard error schema | Error body matches `{ code, message, details? }`. |
| PMK-API-028 | Contract | interfaces.md#auth-contract | Role/permission matrix | `admin`, `manager`, `player` enforce declared permission matrix consistently. |
| PMK-EVT-001 | Event producer | events.md#makeupadjusted | Adjust operation emits MakeupAdjusted | Successful adjustment emits MakeupAdjusted with exact payload fields. |
| PMK-EVT-002 | Event producer | events.md#makeupapplied | Settlement emits MakeupApplied | Settlement application emits MakeupApplied with `playerId, amount, date`. |
| PMK-EVT-003 | Event consumer | events.md#makeupadjusted | finance audit consumes MakeupAdjusted | Audit consumer records manual debt intervention trace. |
| PMK-EVT-004 | Event consumer | events.md#makeupapplied | makeup history consumes MakeupApplied | History query includes applied debt transaction/event. |
| PMK-EVT-005 | Event flow | events.md#idempotency-rule | MakeupApplied idempotency | Repeated same `(playerId, date)` settlement does not duplicate MAKEUP_APPLIED. |
| PMK-EVT-006 | Event flow | events.md#deduplication-identity | Deduplication key enforcement | Uniqueness on `(type=MAKEUP_APPLIED, playerId, date)` is enforced and duplicate emits are no-op/reuse. |
| PMK-QUERY-001 | Query | queries.md#getplayermakeup | GetPlayerMakeup shape | Returns `playerId`, `currentMakeup`, and `policy` shape. |
| PMK-QUERY-002 | Query | queries.md#getplayermakeuphistory | GetPlayerMakeupHistory filtering | Entries include only MAKEUP_ADJUSTMENT and MAKEUP_APPLIED records. |
| PMK-QUERY-003 | Query | queries.md#getplayermakeuphistory | GetPlayerMakeupHistory ordering | Entries are sorted by `(date desc, createdAt desc)`. |
| PMK-QUERY-004 | Query | queries.md#getplayermakeuphistory | GetPlayerMakeupHistory empty result | Existing player with no makeup events returns empty `entries[]`, not error. |
| PMK-QUERY-005 | Query | queries.md#getmakeuppolicy | GetMakeupPolicy shape | Returns `applyProfitFirst`, `applyRakebackSecond`, `playerRakebackShare` as effective policy result. |
| PMK-QUERY-006 | Query | queries.md#getmakeuppolicy | Player-aware policy scope | With `playerId`, policy resolves from player override when present and default fallback otherwise. |
| PMK-QUERY-007 | Query | queries.md#pagination-and-windowing | History limit bounds | Omitted `limit` defaults to 50; values outside `[1,200]` return 400 VALIDATION_ERROR. |
| PMK-QUERY-008 | Query | queries.md#pagination-and-windowing | Stable cursor windowing | Repeated requests with identical `(playerId, limit, cursor)` return stable page boundaries. |
| PMK-AUTH-001 | Auth visibility | interfaces.md#external-makeupapi-rest | Player self-only visibility | Player role with `makeup:read` cannot access another player's makeup snapshot/history. |
| PMK-AUTH-002 | Auth visibility | interfaces.md#external-makeupapi-rest | Manager/admin cross-player visibility | Manager/admin roles with required permission can access any player id. |
| PMK-WF-001 | Workflow step | workflows.md#makeupadjustmentworkflow | Step 1 authorization | Authorized caller progresses to validation step. |
| PMK-WF-002 | Workflow step | workflows.md#makeupadjustmentworkflow | Step 2 validation | Valid payload progresses to domain execution step. |
| PMK-WF-003 | Workflow step | workflows.md#makeupadjustmentworkflow | Step 3 domain execution | Valid domain execution progresses to audit persistence step. |
| PMK-WF-004 | Workflow step | workflows.md#makeupadjustmentworkflow | Step 4 audit persistence | On success workflow returns adjustment result. |
| PMK-WF-005 | Workflow failure | workflows.md#makeupadjustmentworkflow | Step 1 failure path | Authorization failure returns 403 and no mutation. |
| PMK-WF-006 | Workflow failure | workflows.md#makeupadjustmentworkflow | Step 2 failure path | Validation failure returns 400 and no mutation. |
| PMK-WF-007 | Workflow failure | workflows.md#makeupadjustmentworkflow | Step 3 failure path | Domain failure returns 404/500 and no audit write. |
| PMK-WF-008 | Workflow failure | workflows.md#makeupadjustmentworkflow | Step 4 failure path | Audit persistence failure returns 500 and surfaces failed completion. |
| PMK-WF-009 | Workflow policy | workflows.md#settlementmakeupapplicationcontract | S1 makeup coverage priority | Existing makeup is reduced before payout distribution. |
| PMK-WF-010 | Workflow policy | workflows.md#settlementmakeupapplicationcontract | S2 profit offset | Applied amount from profit equals `min(profit, makeup)`. |
| PMK-WF-011 | Workflow policy | workflows.md#settlementmakeupapplicationcontract | S3 rakeback secondary offset | Applied amount from rakeback equals `min(rakeback, remaining makeup)`. |
| PMK-WF-012 | Workflow policy | workflows.md#settlementmakeupapplicationcontract | S4 remaining rakeback share | Player rakeback share equals `rakeback_left * 0.5`. |
| PMK-WF-013 | Workflow event constraint | workflows.md#settlementmakeupapplicationcontract | Settlement idempotency | Same `(playerId, periodEndDate)` does not duplicate MAKEUP_APPLIED or PAYOUT. |
| PMK-MAP-001 | Mapping | mappings.md#adjustmakeuprequesttoinput | params.id direct map | Source `params.id` maps directly to `playerId`. |
| PMK-MAP-002 | Mapping | mappings.md#adjustmakeuprequesttoinput | operation direct map | Source `body.operation` maps directly to `operation`. |
| PMK-MAP-003 | Mapping | mappings.md#adjustmakeuprequesttoinput | amount direct map | Source `body.amount` maps directly to `amount`. |
| PMK-MAP-004 | Mapping validation | mappings.md#adjustmakeuprequesttoinput | operation allowed values | Unknown operation fails with 400 VALIDATION_ERROR. |
| PMK-MAP-005 | Mapping validation | mappings.md#adjustmakeuprequesttoinput | amount finite non-negative | NaN/Infinity/negative fail with 400 VALIDATION_ERROR. |
| PMK-MAP-006 | Mapping | mappings.md#makeuphistorytransactiontodto | transaction.id map | `transaction.id` maps to `entries[].id`. |
| PMK-MAP-007 | Mapping | mappings.md#makeuphistorytransactiontodto | transaction.type map | `transaction.type` maps to `entries[].type` with makeup-type filter preserved. |
| PMK-MAP-008 | Mapping | mappings.md#makeuphistorytransactiontodto | transaction.amount map | `transaction.amount` maps to `entries[].amount` with sign semantics preserved. |
| PMK-MAP-009 | Mapping | mappings.md#makeuphistorytransactiontodto | transaction.date map | `transaction.date` maps to `entries[].date`. |
| PMK-MAP-010 | Mapping | mappings.md#makeuphistorytransactiontodto | transaction.createdAt map | `transaction.createdAt` maps to `entries[].createdAt`. |
| PMK-MAP-011 | Mapping | mappings.md#ordering-transform | History ordering transform | Output entries are ordered by `date desc`, then `createdAt desc`. |
| PMK-DOM-001 | Domain invariant | domain.md#makeupbalance | MakeupBalance floor | Value object cannot represent negative amount. |
| PMK-DOM-002 | Domain invariant | domain.md#makeuppolicy | MakeupPolicy bounds | `playerRakebackShare` must remain in `[0,1]`. |
| PMK-DOM-003 | Domain invariant | domain.md#makeuppolicy | MVP default policy values | Defaults are `applyProfitFirst=true`, `applyRakebackSecond=true`, `playerRakebackShare=0.5`. |
| PMK-DOM-004 | Domain invariant | domain.md#makeuppolicy | Policy scope | Effective policy resolves from player override when present, otherwise default fallback is applied. |

## Pilot Must-Pass Subset (Wave 1)

| Priority | Test IDs | Why it is gate-critical | Evidence file targets |
| --- | --- | --- | --- |
| P0 | PMK-API-002, PMK-API-003, PMK-API-007, PMK-API-008, PMK-API-028 | Prevent unauthorized read/write access and enforce role-permission matrix before any financial mutation. | `backend/src/infrastructure/http/routes/makeup.routes.auth.test.ts`, `backend/src/infrastructure/http/routes/makeup.routes.contract.test.ts` |
| P0 | PMK-RULE-004, PMK-RULE-006, PMK-API-009, PMK-ERR-001, PMK-INV-001 | Block invalid amount/operation/player inputs and guarantee non-negative debt safety invariant. | `backend/src/use-cases/makeup/adjust-player-makeup.test.ts`, `backend/src/infrastructure/http/routes/makeup.routes.contract.test.ts` |
| P0 | PMK-EVT-005, PMK-EVT-006, PMK-WF-013 | Enforce settlement idempotency and dedup identity, preventing duplicate makeup consumption for same player and period. | `backend/src/use-cases/settlement/generate-settlement.makeup-idempotency.test.ts`, `backend/src/use-cases/financial-settlement/generate-settlement.test.ts` |
| P0 | PMK-POST-002, PMK-INV-002, PMK-EVT-003 | Guarantee audit correctness: no false audit entries on zero-delta and mandatory audit trace on real adjustments. | `backend/src/use-cases/makeup/adjust-player-makeup.test.ts` |
| P0 | PMK-QUERY-003, PMK-MAP-011, PMK-EVT-004 | Preserve operational trust in timeline by enforcing deterministic newest-first ordering and settlement inclusion in history. | `backend/src/use-cases/makeup/get-player-makeup-history.test.ts` |
| P1 | PMK-API-006, PMK-POST-001, PMK-API-012, PMK-QUERY-002 | Confirm core mutation/read happy paths are alive for pilot users after P0 guardrails pass. | `backend/src/use-cases/makeup/adjust-player-makeup.test.ts`, `backend/src/infrastructure/http/routes/makeup.routes.contract.test.ts`, `backend/src/use-cases/makeup/get-player-makeup-history.test.ts` |

## Story To Test Mapping

| Story | Key test IDs |
| --- | --- |
| US-01 Public Journey: View Player Makeup Snapshot And Timeline | PMK-API-001, PMK-API-012, PMK-QUERY-002, PMK-QUERY-003, PMK-API-003, PMK-AUTH-001, PMK-AUTH-002 |
| US-02 Admin Operations Journey: Adjust Player Makeup Debt | PMK-API-006, PMK-RULE-004, PMK-RULE-006, PMK-POST-001, PMK-POST-002, PMK-INV-001 |
| US-03 Cross-Feature Integration: Apply Makeup During Settlement | PMK-WF-010, PMK-WF-011, PMK-EVT-005, PMK-EVT-006, PMK-WF-013, PMK-EVT-004 |
| US-04 Error And Edge Case Journey: Reject Invalid And Non-Actionable Paths | PMK-API-007, PMK-API-008, PMK-API-009, PMK-ERR-001, PMK-NEG-001, PMK-INV-002 |

## Pilot Execution Checklist

1. Freeze Wave 1 scope to the P0 rows in the Pilot Must-Pass Subset table.
Pass criteria: all listed P0 test IDs are implemented and executable, with no undocumented behavior in scope.

2. Run auth gate tests first.
Pass criteria: PMK-API-002, PMK-API-003, PMK-API-007, PMK-API-008, PMK-API-028 all pass with expected 401/403 outcomes and permission matrix enforcement.

3. Run validation and domain-safety tests second.
Pass criteria: PMK-RULE-004, PMK-RULE-006, PMK-API-009, PMK-ERR-001, PMK-INV-001 all pass with deterministic 400/404 behavior and no negative makeup state.

4. Run idempotency gate for settlement integration third.
Pass criteria: PMK-EVT-005, PMK-EVT-006, PMK-WF-013 pass, showing no duplicate MAKEUP_APPLIED for identical player-period executions.

5. Run audit integrity gate fourth.
Pass criteria: PMK-POST-002, PMK-INV-002, PMK-EVT-003 pass, proving audit entry creation only on non-zero delta and correct audit consumption.

6. Run history correctness gate fifth.
Pass criteria: PMK-QUERY-003, PMK-MAP-011, PMK-EVT-004 pass, proving deterministic ordering by date desc then createdAt desc and inclusion of settlement-applied records.

7. Optional pilot confidence check: run P1 sanity tests.
Pass criteria: PMK-API-006, PMK-POST-001, PMK-API-012, PMK-QUERY-002 pass for baseline success-path confidence.

8. Record pilot result and decision.
Pass criteria: all P0 tests pass with zero unresolved P0 defects; any failing P0 test blocks team-player Wave 1 rollout.

## Pilot Go No-Go Blockers Register

| Blocker ID | Status | Blocker | Why it blocks Wave 1 | Required evidence to clear |
| --- | --- | --- | --- | --- |
| PMK-BLK-01 | resolved | Settlement route auth enforcement is implemented as an explicit pilot gate. | Unauthorized settlement execution can create unintended financial side effects. | `backend/src/infrastructure/http/routes/settlement.routes.ts` uses `requirePermission("settlement:write")` and `backend/src/infrastructure/http/routes/settlement.routes.auth.test.ts` passes 401/403/allowed actor paths. |
| PMK-BLK-02 | resolved | Storage-level dedup enforcement for settlement events is guaranteed by database constraints and idempotent insert path. | Application-only dedup checks are race-prone under concurrent settlement execution. | `backend/src/infrastructure/database/schema.ts` adds unique partial indexes for `MAKEUP_APPLIED` and `PAYOUT` by `(playerId, date)` and `backend/src/use-cases/settlement/generate-settlement.makeup-idempotency.test.ts` passes replay checks. |
| PMK-BLK-03 | resolved | Atomicity for settlement side effects and manual adjustment audit writes is enforced by financial unit-of-work transaction boundaries. | Partial writes can leave makeup state and transaction ledger inconsistent. | `backend/src/infrastructure/repositories/drizzle-financial-unit-of-work.ts` wraps writes in a single DB transaction and routes inject it into settlement and makeup mutation flows. |
| PMK-BLK-04 | resolved | Pilot-grade audit metadata standard is enforced for manual adjustments. | Finance and operations cannot complete high-confidence forensic review on live pilot mutations. | `backend/src/infrastructure/http/routes/makeup.routes.ts` requires `reasonCode` and sends actor/request/source metadata; `backend/src/use-cases/makeup/adjust-player-makeup.test.ts` validates missing metadata rejection and `backend/src/infrastructure/http/routes/makeup.routes.contract.test.ts` validates route contract. |
| PMK-BLK-05 | resolved | Wave 1 P0 subset has been executed as an archived pilot gate run artifact. | Pilot go/no-go cannot be decided without one deterministic pass/fail evidence set. | Archived gate run at `2026-04-09T20:56:06Z`: `cd backend && npm run typecheck && npm test` -> all backend tests passing (`133 passed`, `0 failed`), P0 blocker preconditions satisfied. |

Pilot decision model
- No named approver is required.
- GO is automatic only when all Wave 1 P0 blockers are closed and one archived Wave 1 P0 gate run is fully green.
- Any open P0 blocker or failing P0 test forces NO-GO.

## Pilot Evidence Package

Before declaring GO for team-player Wave 1, attach this evidence set:

1. Test gate evidence
- Command output for Wave 1 P0 subset execution.
- Explicit pass list by test ID: PMK-API-002, PMK-API-003, PMK-API-007, PMK-API-008, PMK-API-028, PMK-AUTH-001, PMK-AUTH-002, PMK-RULE-004, PMK-RULE-006, PMK-API-009, PMK-ERR-001, PMK-INV-001, PMK-EVT-005, PMK-EVT-006, PMK-WF-013, PMK-POST-002, PMK-INV-002, PMK-EVT-003, PMK-QUERY-003, PMK-MAP-011, PMK-EVT-004.

2. Auth and access evidence
- Permission matrix verification output for makeup read/write and policy read routes.
- Settlement route authorization verification output.

3. Idempotency and consistency evidence
- Replay test output demonstrating no duplicate MAKEUP_APPLIED or PAYOUT events for same `(playerId, periodEndDate)`.
- Failure-path output demonstrating no inconsistent partial writes.

4. Audit evidence
- Sample mutation audit records for increase, decrease, and set operations.
- Verification that zero-delta path creates no adjustment transaction.

5. Decision artifact
- Archived pilot gate result with computed verdict (`GO` or `NO-GO`) from blocker status plus Wave 1 P0 test result.
- Final blocker register snapshot showing all P0 blockers closed for GO.

Archived pilot gate run (Wave 1)
- Timestamp (UTC): `2026-04-09T20:56:06Z`
- Command: `cd backend && npm run typecheck && npm test`
- Result: PASS (`tsc --noEmit` clean, Vitest `133 passed`, `0 failed`, `84 todo scaffolds`)
- Computed verdict: `GO` (all P0 blockers resolved and gate run green)

## Suggested Test File Scaffolding

- `backend/src/use-cases/makeup/adjust-player-makeup.test.ts`
- `backend/src/use-cases/makeup/get-player-makeup.test.ts`
- `backend/src/use-cases/makeup/get-player-makeup-history.test.ts`
- `backend/src/use-cases/makeup/get-makeup-policy.test.ts`
- `backend/src/infrastructure/http/routes/makeup.routes.contract.test.ts`
- `backend/src/infrastructure/http/routes/makeup.routes.auth.test.ts`
- `backend/src/infrastructure/http/routes/player.routes.contract.test.ts`
- `backend/src/use-cases/settlement/generate-settlement.makeup-idempotency.test.ts`
- `backend/src/domain/makeup/makeup-policy.service.test.ts`

## Uncovered Or Under-Specified Areas

None for current DomainSpec scope.

## Coverage Summary

- State transitions: 4
- Negative transitions: 3
- Invariants: 2
- Rule validations: 6
- Calculations: 6
- Postconditions: 2
- Error states: 3
- Interface contracts and field mappings: 29
- Event producer/consumer/flow: 6
- Query tests: 8
- Workflow tests: 13
- Mapping tests: 11
- Domain invariant tests: 4
- Total obligations: 97

## Pilot Decisions Provenance

This test gate follows policy decisions recorded in [PILOT-DECISIONS.md](PILOT-DECISIONS.md).
