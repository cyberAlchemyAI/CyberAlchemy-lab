---
id: financial-settlement-test-spec
feature: financial-settlement
title: Financial Settlement Test Specification
summary: Deterministic test catalogue derived from DomainSpec aspect documents.
status: implemented
pillar: finance
domain: financial-settlement
audience:
  - developers
priority: p1
lang: en
owners:
  - finance-core
  - backend-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
  - operations.md
  - interfaces.md
  - queries.md
  - events.md
  - workflows.md
includes: []
---

# Financial Settlement — Test Specification

> Derived from [SPEC.md](SPEC.md), [operations.md](operations.md), [interfaces.md](interfaces.md), [queries.md](queries.md), [events.md](events.md), [workflows.md](workflows.md).

## Rule Validation Tests

### GenerateSettlement Rules

Source: [GenerateSettlement](operations.md#generatesettlement)

| ID   | Rule                        | Test Description                                        | Expected          |
| ---- | --------------------------- | ------------------------------------------------------- | ----------------- |
| RV-1 | R1: player must exist       | Generate with non-existent playerId                     | domain error      |
| RV-2 | R2: required fields present | Generate with missing playerId                          | 400               |
| RV-3 | R2: required fields present | Generate with missing startDate                         | 400               |
| RV-4 | R2: required fields present | Generate with missing endDate                           | 400               |
| RV-5 | R3: inclusive date range    | Stats exactly on startDate are included                 | included in total |
| RV-6 | R3: inclusive date range    | Stats exactly on endDate are included                   | included in total |
| RV-7 | R3: inclusive date range    | Stats outside range are excluded                        | excluded          |
| RV-8 | R4: MAKEUP_APPLIED dedup    | Second settlement same endDate skips MAKEUP_APPLIED txn | no duplicate      |
| RV-9 | R5: PAYOUT dedup            | Second settlement same endDate skips PAYOUT txn         | no duplicate      |

---

## Calculation Tests

Source: [GenerateSettlement](operations.md#generatesettlement), [ApplyMakeupPolicyCalculation](operations.md#applymakeuppolicycalculation)

| ID    | Calculation                     | Test Description                                          | Expected Formula              |
| ----- | ------------------------------- | --------------------------------------------------------- | ----------------------------- |
| CT-1  | C1: total profit                | Sum of profit across relevant records                     | `sum(records.profit)`         |
| CT-2  | C2: total rakeback              | Sum of rakeback across relevant records                   | `sum(records.rakeback)`       |
| CT-3  | C3: deal split NL100+           | Player on NL100 → 50% share                               | `playerShare = 0.5`           |
| CT-4  | C3: deal split below NL100      | Player on NL20/40/60/80 → 40% share                       | `playerShare = 0.4`           |
| CT-5  | Makeup: profit applied to debt  | Negative profit adds to debt; positive reduces debt first | per ApplyMakeupPolicy formula |
| CT-6  | Makeup: rakeback applied second | Remaining debt reduced by rakeback after profit           | per ApplyMakeupPolicy formula |
| CT-7  | Makeup: playerProfitShare       | `remainingProfit * dealPlayerShare`                       | deterministic calculation     |
| CT-8  | Makeup: playerRakebackShare     | `remainingRakeback * playerRakebackShare`                 | `remainingRakeback * 0.5`     |
| CT-9  | Makeup: totalPayout             | `playerProfitShare + playerRakebackShare`                 | sum of both shares            |
| CT-10 | Makeup: non-negative debt       | Applied amount cannot result in negative makeup           | `newMakeup >= 0`              |

---

## Postcondition Tests

Source: [GenerateSettlement](operations.md#generatesettlement)

| ID   | Postcondition                         | Test Description                                           |
| ---- | ------------------------------------- | ---------------------------------------------------------- |
| PC-1 | Returns SettlementResult              | Response contains all expected fields                      |
| PC-2 | Updates player makeup when changed    | Player makeup updated when `newMakeup != previousMakeup`   |
| PC-3 | Does not update makeup when unchanged | Player makeup untouched when `newMakeup == previousMakeup` |
| PC-4 | MAKEUP_APPLIED transaction created    | Created when applied > 0 and no duplicate for endDate      |
| PC-5 | PAYOUT transaction created            | Created when payout > 0 and no duplicate for endDate       |
| PC-6 | No PAYOUT when payout = 0             | No transaction created when computed payout is 0           |
| PC-7 | No MAKEUP_APPLIED when applied = 0    | No transaction when no debt was consumed                   |

---

## Workflow Tests

Source: [SettlementWorkflow](workflows.md#settlementworkflow)

| ID   | Step                         | Test Description                                         |
| ---- | ---------------------------- | -------------------------------------------------------- |
| WF-1 | Step 1: Validate request     | Invalid payload returns 400 before loading dependencies  |
| WF-2 | Step 2: Load dependencies    | Player not found returns domain error before computation |
| WF-3 | Step 3: Compute policy       | Policy computation produces deterministic result         |
| WF-4 | Step 4: Persist side-effects | Transactions are persisted atomically with deduplication |
| WF-5 | Step 5: Return response      | SettlementResult returned matching computed values       |

### Workflow Invariant Tests

| ID   | Invariant                       | Test Description                                                 |
| ---- | ------------------------------- | ---------------------------------------------------------------- |
| WI-1 | I1: makeup debt non-negative    | After settlement, `newMakeup >= 0` always                        |
| WI-2 | I2: duplicate PAYOUT prevention | Re-running settlement same endDate does not create second PAYOUT |

---

## Contract Tests

Source: [interfaces.md](interfaces.md)

| ID   | Endpoint          | Scenario                | Expected Status | Expected Body Shape |
| ---- | ----------------- | ----------------------- | --------------- | ------------------- |
| CO-1 | POST /settlements | Valid settlement        | 200             | SettlementResult    |
| CO-2 | POST /settlements | Missing required fields | 400             | Error payload       |
| CO-3 | POST /settlements | Player not found        | 500 or domain   | Error payload       |
| CO-4 | POST /settlements | Internal error          | 500             | Error payload       |

---

## Event Tests

Source: [events.md](events.md)

| ID   | Event               | Test Description                                            |
| ---- | ------------------- | ----------------------------------------------------------- |
| EV-1 | SettlementGenerated | Event contains all required payload fields after settlement |
| EV-2 | PayoutCreated       | Event emitted when payout > 0 with correct payload          |
| EV-3 | PayoutCreated       | Event not emitted when payout = 0                           |

---

## Query Tests

Source: [queries.md](queries.md)

| ID   | Query                | Test Description                                      |
| ---- | -------------------- | ----------------------------------------------------- |
| QT-1 | GetSettlementPreview | Returns projected figures without side-effects        |
| QT-2 | GetSettlementPreview | Uses player stats for requested date range            |
| QT-3 | GetSettlementPreview | Applies makeup policy to project newMakeup and payout |
| QT-4 | GetSettlementPreview | Missing player returns error                          |

---

## Mapping Tests

Source: [mappings.md](mappings.md)

| ID   | Mapping                  | Test Description                               |
| ---- | ------------------------ | ---------------------------------------------- |
| MT-1 | SettlementRequestToInput | All API fields map correctly to use-case input |
| MT-2 | SettlementRequestToInput | Missing optional fields handled gracefully     |

---

## Test Count Summary

| Category            | Count  |
| ------------------- | ------ |
| Rule validations    | 9      |
| Calculations        | 10     |
| Postconditions      | 7      |
| Workflow tests      | 5      |
| Workflow invariants | 2      |
| Contract tests      | 4      |
| Event tests         | 3      |
| Query tests         | 4      |
| Mapping tests       | 2      |
| **Total**           | **46** |

---

## Story To Test Mapping

| Story                                                                                           | Key test IDs                                                                                                                                                                                                            |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| US-01 Admin Operations Journey: Generate Settlement For A Player Period                         | RV-1, RV-2, RV-3, RV-4, RV-8, RV-9, CT-1, CT-2, CT-3, CT-4, CT-5, CT-6, CT-7, CT-8, CT-9, CT-10, PC-1, PC-2, PC-3, PC-4, PC-5, PC-6, PC-7, WF-1, WF-2, WF-3, WF-4, WF-5, WI-1, WI-2, CO-1, EV-1, EV-2, EV-3, MT-1, MT-2 |
| US-02 Public Journey: Preview Settlement Before Execution                                       | QT-1, QT-2, QT-3, QT-4                                                                                                                                                                                                  |
| US-03 Cross-Feature Integration: Settlement Consumes Player, Stats, And Makeup Data             | CT-5, CT-6, CT-7, CT-8, WF-2, WF-3                                                                                                                                                                                      |
| US-04 Error And Edge Case Journey: Reject Invalid Settlement And Prevent Duplicate Side-Effects | RV-2, RV-3, RV-4, RV-8, RV-9, WI-2, CO-2, CO-3, CO-4                                                                                                                                                                    |

## Pilot Must-Pass Subset (Wave 1)

| Priority | Test IDs | Why it is gate-critical | Evidence file targets |
| --- | --- | --- | --- |
| P0 | RV-8, RV-9, WI-2 | Enforce settlement idempotency and dedupe guarantees for MAKEUP_APPLIED and PAYOUT side effects. | `backend/src/use-cases/settlement/generate-settlement.makeup-idempotency.test.ts`, `backend/src/use-cases/financial-settlement/generate-settlement.test.ts` |
| P0 | CT-5, CT-6, CT-10, WI-1 | Protect non-negative makeup debt and deterministic makeup application order. | `backend/src/use-cases/financial-settlement/generate-settlement.test.ts` |
| P0 | CO-1, CO-2, CO-4 | Lock external settlement API behavior for success, validation, and internal failures. | `backend/src/infrastructure/http/routes/settlement.routes.preview.test.ts` |
| P0 | WF-2, WF-3, WF-4, PC-4, PC-5 | Guarantee dependency load, policy calculation, and side-effect persistence behavior. | `backend/src/use-cases/financial-settlement/generate-settlement.test.ts` |
| P0 | EV-2, EV-3 | Validate payout event behavior for positive and zero payout branches. | `backend/src/use-cases/financial-settlement/generate-settlement.test.ts` |
| P1 | QT-1, QT-2, QT-3, QT-4, CO-3 | Expand confidence on preview workflow and not-found/error semantics. | `backend/src/use-cases/financial-settlement/get-settlement-preview.test.ts`, `backend/src/infrastructure/http/routes/settlement.routes.preview.test.ts` |

## Pilot Execution Checklist

1. Freeze Wave 1 settlement scope to P0 IDs.
Pass criteria: all P0 IDs are mapped to executable tests and run artifacts.

2. Run idempotency and dedupe gate first.
Pass criteria: RV-8, RV-9, WI-2 pass and show no duplicate settlement side effects.

3. Run makeup safety gate second.
Pass criteria: CT-5, CT-6, CT-10, WI-1 pass with non-negative debt guarantee.

4. Run API contract gate third.
Pass criteria: CO-1, CO-2, CO-4 pass with deterministic status and payload shape.

5. Run workflow and persistence gate fourth.
Pass criteria: WF-2/3/4 and PC-4/5 pass for deterministic compute and write behavior.

6. Run payout event gate fifth.
Pass criteria: EV-2 and EV-3 pass for payout emitted/not-emitted branches.

7. Execute optional P1 preview checks.
Pass criteria: QT-1/2/3/4 and CO-3 pass without affecting P0 verdict.

8. Compute final Wave 1 verdict.
Pass criteria: zero failing P0 tests and no open P0 blocker.

## Pilot Go No-Go Blockers Register

| Blocker ID | Status | Blocker | Why it blocks Wave 1 | Required evidence to clear |
| --- | --- | --- | --- | --- |
| FST-BLK-01 | closed | Settlement event contract semantics are inconsistent across docs, tests, and implementation. | Event-driven side effects cannot be validated deterministically. | Closed on 2026-04-24 via explicit settlement event contract (`backend/src/domain/settlement/settlement.events.ts`) and deterministic EV coverage in `backend/src/use-cases/financial-settlement/generate-settlement.test.ts`. |
| FST-BLK-02 | closed | Preview response contract names drift between queries/stories and runtime output mapping. | Consumers can mis-handle settlement preview payloads in production. | Closed on 2026-04-24 via preview alias normalization and route contract coverage updates. |
| FST-BLK-03 | closed | Player-not-found behavior for settlement endpoints is not deterministic across artifacts. | Operational error handling remains ambiguous for missing players. | Closed on 2026-04-24 with deterministic `PLAYER_NOT_FOUND` mapping and updated contract tests. |
| FST-BLK-04 | closed | Settlement namespace ownership remains split and layering findings are still open. | Readiness decisions cannot confirm deterministic ownership boundaries for long-term maintenance. | Closed on 2026-04-24 by converging canonical settlement orchestrators and tests into `backend/src/use-cases/financial-settlement/` and updating route wiring. |
| FST-BLK-05 | closed | Observability coverage was below pilot threshold for settlement workflows. | Without O6/O9/O15/O16 telemetry, finance integrity checks could not be enforced at pilot gate. | Closed on 2026-04-24 by instrumenting settlement calculation drift (C1-C4), idempotency violation/dedup and exposure, reconciliation mismatch, workflow metrics, and settlement cycle metrics in `backend/src/use-cases/financial-settlement/generate-settlement.ts`; validated by `generate-settlement.test.ts`, `generate-settlement.makeup-idempotency.test.ts`, and refreshed [OBSERVABILITY-REPORT.md](OBSERVABILITY-REPORT.md) verdict (FLAG, no open P0 gaps). |

## Pilot Evidence Package

1. Idempotency evidence
- Replay and duplicate prevention test outputs for RV-8, RV-9, WI-2.

2. Financial integrity evidence
- CT-5/6/10 and WI-1 outputs proving debt safety and deterministic application order.

3. API and workflow evidence
- Contract test outputs for CO-1/2/4 and workflow/postcondition outputs for WF/PC gates.

4. Event evidence
- EV-2 and EV-3 assertions with payout emitted/not-emitted branches.

5. Decision artifact
- Final blocker register snapshot and computed PASS/FLAG/BLOCK decision.

## Pilot Decisions Provenance

This test gate follows policy decisions recorded in [PILOT-DECISIONS.md](PILOT-DECISIONS.md).
