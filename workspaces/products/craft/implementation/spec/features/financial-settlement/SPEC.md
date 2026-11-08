# Financial Settlement — feature pack (L0 POC)

> First **real** v2 feature pack. Promoted build-from-owned from the engine fixture
> `test-derivation-engine/__fixtures__/financial-settlement/` (backend aspect files; graph typed by
> the spec-ontology toy, 23 nodes) into the v2 feature-pack shape and typed to the backend meta-type
> schemas under `spec/meta-types/`. Its purpose is to make the node-plane validators **non-vacuous**
> (APE package, `DEC-DSV2-APE-L0-DOMAIN` → reuse financial-settlement).
>
> **Node + edge plane.** R3 now supplies root relationship signatures under `definitions/relationships/`.
> This pack exercises `validate-content` over node criteria and `validate:rels` over a small valid graph.

## What This Feature Owns

Settlement generation for a player over a period: compute the settlement result, apply makeup debt,
and create the resulting ledger transactions (MAKEUP_APPLIED / PAYOUT).

## Concept Registry

| Concept | Type |
| --- | --- |
| SettlementTransaction | Entity |
| SettlementResult | Value Object |
| SettlementTransactionType | Enum |
| GenerateSettlement | Operation |
| GetSettlementPreview | Query |
| DealSplitCalculation | Calculation |
| PayoutEligibilityRule | Rule |
| NoDuplicateMakeupRule | Rule |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| PayoutEligibilityRule | enforces | GenerateSettlement |
| NoDuplicateMakeupRule | enforces | GenerateSettlement |
| DealSplitCalculation | calculates | GenerateSettlement |
| GenerateSettlement | creates | SettlementTransaction |
| GenerateSettlement | reads | SettlementTransaction |
| GetSettlementPreview | reads | SettlementTransaction |

## SettlementTransaction

An identity-bearing settlement ledger entry — a persisted transaction row created by settlement
generation.

| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| transactionId | UUID | yes | yes | unique transaction identity |
| type | SettlementTransactionType | yes |  | MAKEUP_APPLIED or PAYOUT |
| amount | integer | yes |  | transaction amount (non-negative) |
| date | string | yes |  | settlement end date |

## SettlementResult

A value defined entirely by its fields; no identity.

| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| playerId | string | yes |  | player the result is for |
| periodStart | string | yes |  | inclusive period start |
| periodEnd | string | yes |  | inclusive period end |
| totalProfit | integer | yes |  | derived profit sum |
| totalPayout | integer | yes |  | non-negative payout total |

**Equality:** two SettlementResult are equal iff all fields are equal for the same player and period.

## SettlementTransactionType

| Value | Description |
| --- | --- |
| MAKEUP_APPLIED | debt-reduction transaction entry |
| PAYOUT | player payout transaction entry |

## GenerateSettlement

Compute a settlement for a player over a period and write the resulting transactions.

| Attribute | Value |
| --- | --- |
| state_change | yes |

## GetSettlementPreview

Read-only preview of a settlement result without writing transactions.

| Attribute | Value |
| --- | --- |
| state_change | no |

## DealSplitCalculation

Pure derivation of the player's profit-share split from the stake limit.

| Attribute | Value |
| --- | --- |
| formal_return_type | value |
| state_change | no |

## PayoutEligibilityRule

Candidate-local one-way guard: when `totalPayout > 0` and there is no same-date `PAYOUT`,
`GenerateSettlement` must produce exactly one `PAYOUT` write followed by one matching
`PayoutCreated` event. No converse is admitted.

| Attribute | Value |
| --- | --- |
| formal_return_type | boolean |
| semantic_ref | evf.semantic.financial-settlement.p4.v1 |

## NoDuplicateMakeupRule

Boolean guard: block a second MAKEUP_APPLIED transaction for the same end date.

| Attribute | Value |
| --- | --- |
| formal_return_type | boolean |
| semantic_ref | evf.semantic.financial-settlement.r4.v1 |
