---
id: financial-settlement-stories
feature: financial-settlement
title: Financial Settlement User Stories
summary: Capability-scoped user stories for settlement generation, makeup application, payout creation, and preview.
status: implemented
pillar: finance
domain: financial-settlement
audience:
  - developers
  - leadership
priority: p1
lang: en
owners:
  - finance-core
  - backend-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
includes: []
---

# Financial Settlement — User Stories

> Source of storytelling truth for [financial-settlement](SPEC.md).

## US-01 Admin Operations Journey: Generate Settlement For A Player Period

**Classic format**
As an **operations or finance user**, I want **to generate a settlement for a player over a date range**, so that **period profit, rakeback, makeup debt, and payout are computed and persisted deterministically**.

**BDD scenario**
Given I submit a valid settlement request with playerId, startDate, and endDate for an existing player
When the settlement workflow executes
Then total profit, rakeback, makeup policy, payout, and updated debt are computed and persisted with transaction deduplication

**Acceptance checks**

- [ ] Settlement follows [GenerateSettlement](operations.md#generatesettlement) rules R1–R5 and calculations C1–C4.
- [ ] Player must exist (R1); all three fields required (R2).
- [ ] Period stats are filtered by inclusive date range (R3).
- [ ] Deal split uses limit-based policy: `playerShare = limit >= NL100 ? 0.5 : 0.4` (C3).
- [ ] Makeup policy application follows [ApplyMakeupPolicyCalculation](operations.md#applymakeuppolicycalculation) formula with profit-first, then rakeback debt reduction.
- [ ] Player makeup is updated when `newMakeup != previousMakeup`.
- [ ] MAKEUP_APPLIED transaction created when applied > 0 with R4 deduplication.
- [ ] PAYOUT transaction created when payout > 0 with R5 deduplication.
- [ ] [SettlementResult](domain.md#settlementresult) returned with all computed fields.
- [ ] API contract follows [POST /settlements](interfaces.md#post-settlements) with 200 success.

**Capability link**: [SPEC — Concepts: GenerateSettlement](SPEC.md#concepts)

**Concept and aspect links**

- financial-settlement.GenerateSettlement: [GenerateSettlement](operations.md#generatesettlement)
- financial-settlement.ApplyMakeupPolicy: [ApplyMakeupPolicyCalculation](operations.md#applymakeuppolicycalculation)
- financial-settlement.SettlementResult: [SettlementResult](domain.md#settlementresult)
- financial-settlement.SettlementAPI: [POST /settlements](interfaces.md#post-settlements)
- financial-settlement.SettlementWorkflow: [SettlementWorkflow](workflows.md#settlementworkflow)

---

## US-02 Public Journey: Preview Settlement Before Execution

**Classic format**
As a **finance user**, I want **to preview the projected settlement figures for a player and period before executing**, so that **I can validate expected payout and debt changes before committing side-effects**.

**BDD scenario**
Given a player has stats records for the requested period
When I request a settlement preview
Then I receive projected profit, rakeback, projected new makeup, and projected payout without persisting any side-effects

**Acceptance checks**

- [ ] Preview follows [GetSettlementPreview](queries.md#getsettlementpreview) query contract.
- [ ] Reads player stats from [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot) for the period.
- [ ] Applies [ApplyMakeupPolicyCalculation](operations.md#applymakeuppolicycalculation) to project debt and payout.
- [ ] No side-effects: player makeup is not updated, no transactions created.
- [ ] Returns totalProfit, totalRakeback, previousMakeup, projectedNewMakeup, projectedPayout.

**Capability link**: [SPEC — Concepts: GetSettlementPreview](SPEC.md#concepts)

**Concept and aspect links**

- financial-settlement.GetSettlementPreview: [GetSettlementPreview](queries.md#getsettlementpreview)
- financial-settlement.ApplyMakeupPolicy: [ApplyMakeupPolicyCalculation](operations.md#applymakeuppolicycalculation)
- financial-settlement.SettlementResult: [SettlementResult](domain.md#settlementresult)

---

## US-03 Cross-Feature Integration: Settlement Consumes Player, Stats, And Makeup Data

**Classic format**
As the **settlement workflow**, I want **to read player context from player-management, period stats from player-stats, and current debt from player-makeup**, so that **settlement calculations use authoritative upstream data**.

**BDD scenario**
Given a settlement is generated for a player
When the workflow loads dependencies
Then player identity and limit come from player-management, period profit/rakeback from player-stats, and current debt from the player's makeup balance

**Acceptance checks**

- [ ] Player context is resolved via [player-management](../player-management/SPEC.md) queries.
- [ ] Period stats aggregated from [player-stats.GetPlayerStatsWindow](../player-stats/queries.md#getplayerstatswindow) or direct snapshot queries for the date range.
- [ ] Current makeup debt read from player's stored makeup balance.
- [ ] Makeup policy application triggers [player-makeup.SettlementMakeupApplicationContract](../player-makeup/workflows.md#settlementmakeupapplicationcontract) integration.
- [ ] [SettlementGenerated](events.md#settlementgenerated) event produced for downstream consumers.
- [ ] [PayoutCreated](events.md#payoutcreated) event produced when payout > 0.
- [ ] Cross-feature dependency contracts documented in [SPEC — Cross-Feature Dependencies](SPEC.md#cross-feature-dependencies).

**Capability link**: [SPEC — Cross-Feature Dependencies](SPEC.md#cross-feature-dependencies)

**Concept and aspect links**

- financial-settlement.SettlementGenerated: [SettlementGenerated](events.md#settlementgenerated)
- financial-settlement.PayoutCreated: [PayoutCreated](events.md#payoutcreated)
- financial-settlement.SettlementWorkflow: [SettlementWorkflow](workflows.md#settlementworkflow)
- player-management.Player: [player-management SPEC](../player-management/SPEC.md)
- player-stats.PlayerStatsSnapshot: [PlayerStatsSnapshot](../player-stats/domain.md#playerstatssnapshot)
- player-makeup.SettlementMakeupApplicationContract: [SettlementMakeupApplicationContract](../player-makeup/workflows.md#settlementmakeupapplicationcontract)

---

## US-04 Error And Edge Case Journey: Reject Invalid Settlement And Prevent Duplicate Side-Effects

**Classic format**
As an **API consumer**, I want **invalid, missing, or duplicate settlement requests handled deterministically**, so that **settlement integrity is preserved and no duplicate transactions are created**.

**BDD scenario**
Given a settlement request is missing required fields, references a non-existent player, or would produce duplicate transactions
When the request is processed
Then the API returns structured errors and no duplicate MAKEUP_APPLIED or PAYOUT transactions are persisted

**Acceptance checks**

- [ ] Missing playerId, startDate, or endDate returns 400 per [GenerateSettlement](operations.md#generatesettlement) R2.
- [ ] Non-existent player returns domain error per R1.
- [ ] Duplicate MAKEUP_APPLIED for same endDate is prevented per R4 (conditional idempotency).
- [ ] Duplicate PAYOUT for same endDate is prevented per R5.
- [ ] Workflow invariants enforce `newMakeup >= 0` per [SettlementWorkflow](workflows.md#settlementworkflow) I1.
- [ ] Settlement endpoints enforce route permissions for generate and preview actions.
- [ ] All error responses follow the standard error payload from [POST /settlements responses](interfaces.md#post-settlements).

**Capability link**: [SPEC — Concepts: GenerateSettlement](SPEC.md#concepts)

**Concept and aspect links**

- financial-settlement.GenerateSettlement: [GenerateSettlement](operations.md#generatesettlement)
- financial-settlement.SettlementAPI: [POST /settlements](interfaces.md#post-settlements)
- financial-settlement.SettlementWorkflow: [SettlementWorkflow](workflows.md#settlementworkflow)

---

## Story Coverage Matrix

| Story | Mandatory Slice           | Concepts Covered                                                                                                                                                                                    | Aspect Anchors                                                                                                                                                                                                                                                                                 |
| ----- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| US-01 | Admin operations journey  | financial-settlement.GenerateSettlement, financial-settlement.ApplyMakeupPolicy, financial-settlement.SettlementResult, financial-settlement.SettlementAPI, financial-settlement.SettlementWorkflow | [GenerateSettlement](operations.md#generatesettlement), [ApplyMakeupPolicyCalculation](operations.md#applymakeuppolicycalculation), [SettlementResult](domain.md#settlementresult), [POST /settlements](interfaces.md#post-settlements), [SettlementWorkflow](workflows.md#settlementworkflow) |
| US-02 | Public journey            | financial-settlement.GetSettlementPreview, financial-settlement.ApplyMakeupPolicy, financial-settlement.SettlementResult                                                                            | [GetSettlementPreview](queries.md#getsettlementpreview), [ApplyMakeupPolicyCalculation](operations.md#applymakeuppolicycalculation), [SettlementResult](domain.md#settlementresult)                                                                                                            |
| US-03 | Cross-feature integration | financial-settlement.SettlementGenerated, financial-settlement.PayoutCreated, financial-settlement.SettlementWorkflow, financial-settlement.SettlementRequestToInput                                | [SettlementGenerated](events.md#settlementgenerated), [PayoutCreated](events.md#payoutcreated), [SettlementWorkflow](workflows.md#settlementworkflow), [SettlementRequestToInput](mappings.md#settlementrequesttoinput)                                                                        |
| US-04 | Error and edge case       | financial-settlement.GenerateSettlement, financial-settlement.SettlementAPI, financial-settlement.SettlementWorkflow                                                                                | [GenerateSettlement](operations.md#generatesettlement), [POST /settlements](interfaces.md#post-settlements), [SettlementWorkflow](workflows.md#settlementworkflow)                                                                                                                             |

**Coverage gap check**: All 9 concepts from the financial-settlement concept table are covered. SettlementRequestToInput is covered via US-03 cross-feature integration.
