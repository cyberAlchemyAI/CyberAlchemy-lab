---
id: player-progression-test-spec
feature: player-progression
title: Player Progression Test Specification
summary: Deterministic test obligations derived from Player Progression DomainSpec artifacts.
status: implemented
pillar: operations
domain: player-progression
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
  - queries.md
  - states.md
  - events.md
  - workflows.md
includes: []
---

# Player Progression — Test Specification

## Derivation Basis

- Framework constraints: `domainspec/CHANGELOG.md` (v1.8.2).
- Feature sources: `operations.md`, `queries.md`, `states.md`, `events.md`, `workflows.md`, `domain.md`.

## Test Catalogue

### Rule Validation Tests

| ID           | Type | Source                         | Obligation                     | Deterministic Assertion                    |
| ------------ | ---- | ------------------------------ | ------------------------------ | ------------------------------------------ |
| PRG-RULE-001 | Rule | operations.md#checkprogression | Player must exist              | Unknown playerId throws "Player not found" |
| PRG-RULE-002 | Rule | operations.md#checkprogression | Period defaults to BI_WEEKLY   | Omitted period uses 15-day window          |
| PRG-RULE-003 | Rule | operations.md#checkprogression | MONTHLY period maps to 30 days | `period=MONTHLY` evaluates 30-day window   |

### Calculation Tests

| ID           | Type        | Source                         | Obligation                                      | Deterministic Assertion                                     |
| ------------ | ----------- | ------------------------------ | ----------------------------------------------- | ----------------------------------------------------------- |
| PRG-CALC-001 | Calculation | operations.md#checkprogression | avgHands = totalHands / periodDays              | With 15000 hands over 15 days, avgHands = 1000              |
| PRG-CALC-002 | Calculation | operations.md#checkprogression | winrate = (totalProfit / bbValue) / (totalHands / 100) | With NL20 (bbValue=0.20), profit 24000 and hands 15000, winrate = 8 |
| PRG-CALC-003 | Calculation | operations.md#checkprogression | Eligible when avgHands >= 1000 and threshold winrate is met | 15-day flow requires winrate >= 7.5; 30-day flow requires winrate >= 5 |
| PRG-CALC-004 | Calculation | operations.md#checkprogression | Not eligible when criteria not met              | Below threshold → `eligibleForPromotion: false` with reason |
| PRG-CALC-005 | Calculation | operations.md#checkprogression | Empty stats returns zero metrics                | No entries → `avgHands: 0`, `winrate: 0`, not eligible      |

### Contract Tests

| ID          | Type     | Source     | Obligation                                  | Deterministic Assertion                                    |
| ----------- | -------- | ---------- | ------------------------------------------- | ---------------------------------------------------------- |
| PRG-API-001 | Contract | interfaces | GET /players/:id/progression 200            | Authorized request returns ProgressionResult shape         |
| PRG-API-002 | Contract | interfaces | GET /players/:id/progression 401            | Missing token returns 401 AUTH_REQUIRED                    |
| PRG-API-003 | Contract | interfaces | GET /players/:id/progression 403            | Missing permission returns 403 FORBIDDEN                   |
| PRG-API-004 | Contract | interfaces | GET /players/:id/progression 404            | Unknown player returns 404 PLAYER_NOT_FOUND                |
| PRG-API-005 | Contract | interfaces | GET /players/:id/progression?period=MONTHLY | Monthly period parameter is accepted and mapped to 30 days |
| PRG-API-006 | Contract | interfaces | GET /players/:id/progression?period=INVALID | Invalid period returns 400 VALIDATION_ERROR                |

### Query Tests

| ID            | Type  | Source                          | Obligation               | Deterministic Assertion                                                    |
| ------------- | ----- | ------------------------------- | ------------------------ | -------------------------------------------------------------------------- |
| PRG-QUERY-001 | Query | queries.md#getprogressionstatus | Response shape           | Contains `eligibleForPromotion`, `reason`, `avgHands`, `winrate`, `period` |
| PRG-QUERY-002 | Query | queries.md#getprogressionstatus | Period label in response | BI_WEEKLY for 15-day, MONTHLY for 30-day                                   |

### State/Event/Workflow Tests

| ID            | Type      | Source                                | Obligation                                    | Deterministic Assertion                                       |
| ------------- | --------- | ------------------------------------- | --------------------------------------------- | ------------------------------------------------------------- |
| PRG-STATE-001 | State     | states.md#progressionevaluationlifecycle | Evaluation lifecycle reaches EVALUATED        | Successful check returns evaluated status payload             |
| PRG-INV-001   | Invariant | states.md#progressionevaluationlifecycle | period label always matches periodDays input  | 15 -> BI_WEEKLY and 30 -> MONTHLY                            |
| PRG-EVT-001   | Event     | events.md#progressionchecked          | ProgressionChecked event is emitted           | Event contains playerId, period, eligibility, reason, metrics |
| PRG-WF-001    | Workflow  | workflows.md#progressioncheckworkflow | Invalid period is rejected before domain call | Route returns 400 and use-case handler is not invoked         |

## Test Count Summary

| Category         | Count  |
| ---------------- | ------ |
| Rule validations | 3      |
| Calculations     | 5      |
| Contract tests   | 6      |
| Query tests      | 2      |
| State/Event/WF   | 4      |
| **Total**        | **20** |

---

## Traceability Matrix

| Obligation    | Evidence File                      | Status  |
| ------------- | ---------------------------------- | ------- |
| PRG-RULE-001  | check-progression.test.ts          | covered |
| PRG-RULE-002  | check-progression.test.ts          | covered |
| PRG-RULE-003  | check-progression.test.ts          | covered |
| PRG-CALC-001  | progression-policy.service.test.ts | covered |
| PRG-CALC-002  | progression-policy.service.test.ts | covered |
| PRG-CALC-003  | check-progression.test.ts          | covered |
| PRG-CALC-004  | check-progression.test.ts          | covered |
| PRG-CALC-005  | check-progression.test.ts          | covered |
| PRG-API-001   | player.routes.contract.test.ts     | covered |
| PRG-API-002   | player.routes.auth.test.ts         | covered |
| PRG-API-003   | player.routes.auth.test.ts         | covered |
| PRG-API-004   | player.routes.contract.test.ts     | covered |
| PRG-API-005   | player.routes.test.ts              | covered |
| PRG-API-006   | player.routes.contract.test.ts     | covered |
| PRG-QUERY-001 | check-progression.test.ts          | covered |
| PRG-QUERY-002 | player.routes.test.ts              | covered |
| PRG-STATE-001 | check-progression.test.ts          | covered |
| PRG-INV-001   | check-progression.test.ts          | covered |
| PRG-EVT-001   | check-progression.test.ts          | covered |
| PRG-WF-001    | player.routes.contract.test.ts     | covered |

---

## Story To Test Mapping

| Story                                                                    | Key test IDs                                                                                                  |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| US-01 Public Journey: Check Player Progression Status                    | PRG-RULE-001, PRG-CALC-001, PRG-CALC-002, PRG-API-001, PRG-API-004, PRG-API-005, PRG-QUERY-001, PRG-QUERY-002 |
| US-02 Admin Operations Journey: Evaluate Monthly Progression             | PRG-RULE-002, PRG-CALC-003, PRG-CALC-004, PRG-CALC-005                                                        |
| US-03 Cross-Feature Integration: Progression Delegates to Stats          | PRG-QUERY-001, PRG-CALC-001                                                                                   |
| US-04 Error and Edge Case Journey: Handle Missing Player and Empty Stats | PRG-RULE-003, PRG-API-002, PRG-API-003                                                                        |

## Pilot Must-Pass Subset (Wave 1)

| Priority | Test IDs | Why it is gate-critical | Evidence file targets |
| --- | --- | --- | --- |
| P0 | PRG-RULE-001, PRG-RULE-002, PRG-RULE-003 | Protect progression eligibility evaluation entry conditions and period mapping. | `backend/src/use-cases/progression/check-progression.test.ts` |
| P0 | PRG-CALC-003, PRG-CALC-004, PRG-CALC-005 | Guarantee deterministic eligible/not-eligible decisions and empty-stats behavior. | `backend/src/domain/progression/progression-policy.service.test.ts`, `backend/src/use-cases/progression/check-progression.test.ts` |
| P0 | PRG-API-001, PRG-API-002, PRG-API-003, PRG-API-004, PRG-API-006 | Lock progression route contract for authorized and error paths, including invalid period rejection. | `backend/src/infrastructure/http/routes/player.routes.auth.test.ts`, `backend/src/infrastructure/http/routes/player.routes.contract.test.ts` |
| P0 | PRG-QUERY-001, PRG-QUERY-002 | Ensure query output shape and period label semantics consumed by operations. | `backend/src/use-cases/progression/check-progression.test.ts`, `backend/src/infrastructure/http/routes/player.routes.test.ts` |
| P0 | PRG-EVT-001, PRG-WF-001 | Guarantee lifecycle event emission and workflow boundary validation behavior. | `backend/src/use-cases/progression/check-progression.test.ts`, `backend/src/infrastructure/http/routes/player.routes.contract.test.ts` |
| P1 | PRG-CALC-001, PRG-CALC-002, PRG-API-005 | Increase confidence on detailed formula and monthly parameter mapping. | `backend/src/domain/progression/progression-policy.service.test.ts`, `backend/src/infrastructure/http/routes/player.routes.test.ts` |

## Pilot Execution Checklist

1. Freeze Wave 1 progression scope to P0 IDs.
Pass criteria: all P0 IDs are executable and linked to concrete tests.

2. Run entry-condition rule gate first.
Pass criteria: PRG-RULE-001/002/003 pass for player existence and period behavior.

3. Run eligibility calculation gate second.
Pass criteria: PRG-CALC-003/004/005 pass for threshold-based decisions and empty data paths.

4. Run route contract gate third.
Pass criteria: PRG-API-001/002/003/004 pass for success and auth/error responses.

5. Run query semantics gate fourth.
Pass criteria: PRG-QUERY-001/002 pass for output shape and period labels.

6. Execute optional P1 formula checks.
Pass criteria: PRG-CALC-001/002 and PRG-API-005 pass without affecting P0 verdict.

7. Capture blockers and evidence package.
Pass criteria: open blockers include owner, planned fix, and closure evidence.

8. Compute final Wave 1 verdict.
Pass criteria: zero failing P0 tests and no open P0 blocker.

## Pilot Go No-Go Blockers Register

| Blocker ID | Status | Blocker | Why it blocks Wave 1 | Required evidence to clear |
| --- | --- | --- | --- | --- |
| PRG-BLK-01 | closed | Operations and queries docs contain duplicated contract blocks with ambiguous authority. | Progression behavior contracts are not reliably traceable for implementation/audit. | Closed on 2026-04-24 via canonicalized `operations.md` and `queries.md` contract blocks with consistent anchors. |
| PRG-BLK-02 | closed | Formula and threshold semantics drift between stories/tests and implemented policy logic. | Eligibility outcomes can diverge between documentation and runtime behavior. | Closed on 2026-04-24 by reconciling formula/threshold semantics across `STORIES.md`, `operations.md`, and policy tests. |
| PRG-BLK-03 | closed | Alignment/layering artifacts are stale for current framework and implementation state. | MVP readiness decisions rely on outdated or incomplete verification evidence. | Closed on 2026-04-24 through refreshed alignment/layering reports on DomainSpec 1.8.2 baseline. |
| PRG-BLK-04 | closed | TEST-SPEC derivation does not fully reflect existing states/events/workflows aspect set. | Coverage model remains incomplete for progression behavior lifecycle. | Closed on 2026-04-24 by adding explicit state/event/workflow obligations and traceability evidence. |

## Pilot Evidence Package

1. Rule and eligibility evidence
- Outputs for PRG-RULE and PRG-CALC P0 IDs from use-case/domain tests.

2. Contract evidence
- Route auth/contract outputs for PRG-API-001/002/003/004.

3. Query semantics evidence
- Outputs for PRG-QUERY-001/002 with deterministic payload assertions.

4. Policy consistency evidence
- Diff-proof reconciliation artifact linking formulas in docs and policy implementation.

5. Decision artifact
- Final blocker register snapshot and computed PASS/FLAG/BLOCK decision.

## Pilot Decisions Provenance

This test gate follows policy decisions recorded in [PILOT-DECISIONS.md](PILOT-DECISIONS.md).
