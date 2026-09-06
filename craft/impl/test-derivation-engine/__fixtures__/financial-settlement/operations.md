---
id: financial-settlement
feature: financial-settlement
title: Financial Settlement Operations
summary: Settlement mutation, rules, and formulas.
status: implemented
pillar: finance
domain: financial-settlement-operations
audience:
  - developers
priority: p1
lang: en
owners:
  - finance-core
  - backend-core
updatedAt: 2026-04-30
dependencies:
  - SPEC.md
  - domain.md
  - states.md
  - events.md
  - interfaces.md
  - mappings.md
includes: []
---

# Operations: Financial Settlement

## Domain Policy Ownership

Settlement policy calculations and side-effect decision rules are owned by the domain layer.

- Settlement policy authority: [`backend/src/domain/settlement/settlement.service.ts`](../../../backend/src/domain/settlement/settlement.service.ts)
- Makeup policy authority: [`backend/src/domain/makeup/makeup-policy.service.ts`](../../../backend/src/domain/makeup/makeup-policy.service.ts)
- Use-case orchestrator: [`backend/src/use-cases/financial-settlement/generate-settlement.ts`](../../../backend/src/use-cases/financial-settlement/generate-settlement.ts)

## GenerateSettlement

**Type:** Operation (mutation)  
**Actor:** Operations user or finance backoffice  
**Triggers:** POST /settlements

### Input

| Field     | Type   | Required | Description       |
| --------- | ------ | -------- | ----------------- |
| playerId  | string | yes      | Target player     |
| startDate | string | yes      | Period start date |
| endDate   | string | yes      | Period end date   |

### Rules

| ID  | Rule                                           | Formal                                                       |
| --- | ---------------------------------------------- | ------------------------------------------------------------ |
| R1  | player must exist                              | `exists(Player.id == playerId)`                              |
| R2  | required fields present                        | `playerId != null and startDate != null and endDate != null` |
| R3  | period filter by inclusive range               | `startDate <= stats.date <= endDate`                         |
| R4  | avoid duplicate MAKEUP_APPLIED on same endDate | `count(tx[type=MAKEUP_APPLIED,date=endDate]) <= 1`           |
| R5  | avoid duplicate PAYOUT on same endDate         | `count(tx[type=PAYOUT,date=endDate]) <= 1`                   |

### Calculations

| ID  | Calculation          | Formula                                                |
| --- | -------------------- | ------------------------------------------------------ |
| C1  | Total profit         | `sum(relevantRecords.profit)`                          |
| C2  | Total rakeback       | `sum(relevantRecords.rakeback)`                        |
| C3  | Deal split           | `playerShare = limit >= NL100 ? 0.5 : 0.4`             |
| C4  | Makeup new debt | `newMakeup = max(0, previousDebt - totalProfit - totalRakeback)` |

### Postconditions

| ID  | Class                 | Guarantee                                                     | Formal Assertion                                                                                                             | Traceability |
| --- | --------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------ |
| P1  | Integration Guarantee | Returns one [SettlementResult](domain.md#settlementresult).  | `result != null and type(result) = SettlementResult`                                                                        | [SettlementResult](domain.md#settlementresult), [SettlementResultToResponse](mappings.md#settlementresulttoresponse), [POST /settlements](interfaces.md#post-settlements) |
| P2  | Integration Guarantee | Updates player makeup when `newMakeup != previousMakeup`.    | `(newMakeup != previousMakeup) -> player-management.Player.makeup = newMakeup`                                             | [SettlementGenerated](events.md#settlementgenerated), [Produces For](SPEC.md#produces-for), [produces-for semantics](../../../domainspec/RELATIONSHIPS.md#produces-for--operationa--entityb) |
| P3  | Audit Guarantee       | Creates MAKEUP_APPLIED transaction when applied amount > 0 and no duplicate exists. | `(appliedMakeup > 0 and not exists tx(type=MAKEUP_APPLIED, date=endDate)) -> create tx(type=MAKEUP_APPLIED, amount=appliedMakeup, date=endDate)` | [SettlementExecutionState](states.md#settlementexecutionstate), [SettlementTransactionType](domain.md#settlementtransactiontype) |
| P4  | Integration Guarantee | Creates PAYOUT transaction when payout > 0 and no duplicate exists. | `(totalPayout > 0 and not exists tx(type=PAYOUT, date=endDate)) -> create tx(type=PAYOUT, amount=totalPayout, date=endDate) and emit(PayoutCreated)` | [PayoutCreated](events.md#payoutcreated), [SettlementExecutionState](states.md#settlementexecutionstate), [produces semantics](../../../domainspec/RELATIONSHIPS.md#produces--operation--event) |

### Error States

| Condition               | Result               |
| ----------------------- | -------------------- |
| Missing required fields | 400 validation error |
| Player not found        | 404 not found error  |
| Repository failure      | 500 internal error   |

---

## ApplyMakeupPolicyCalculation

**Type:** Calculation / Policy
**Used by:** [GenerateSettlement](#generatesettlement)

### Formula

- Normalize money-like inputs to integers.
- Add negative profit/rakeback magnitudes to debt.
- Apply profit to debt first when policy flag is true.
- Apply rakeback to remaining debt second when policy flag is true.
- Compute `playerProfitShare = remainingProfit * dealPlayerShare`.
- Compute `playerRakebackShare = remainingRakeback * policy.playerRakebackShare`.
- Compute `totalPayout = playerProfitShare + playerRakebackShare`.
