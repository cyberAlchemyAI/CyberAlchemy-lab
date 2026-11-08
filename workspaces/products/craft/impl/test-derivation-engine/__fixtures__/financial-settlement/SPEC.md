---
id: financial-settlement
feature: financial-settlement
title: Financial Settlement DomainSpec
summary: Domain specification for period settlement, makeup application, and payout generation.
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
  - web-core
updatedAt: 2026-04-17
dependencies:
  - player-management
  - player-makeup
  - player-stats
includes:
  - domain.md
  - operations.md
  - states.md
  - interfaces.md
  - queries.md
  - events.md
  - mappings.md
  - workflows.md
  - STORIES.md
  - TEST-SPEC.md
---

# Financial Settlement

## Overview

Financial Settlement computes period outcomes for a player by combining daily profit/rakeback, deal split policy, and makeup debt policy. It persists side-effects (makeup applied and payout transactions) with idempotency checks at period end date.

## Concepts

| Concept                                                          | ID                                            | Type         | Description                                       |
| ---------------------------------------------------------------- | --------------------------------------------- | ------------ | ------------------------------------------------- |
| [SettlementResult](domain.md#settlementresult)                   | financial-settlement.SettlementResult         | Value Object | Output aggregate for one settlement period        |
| [GenerateSettlement](operations.md#generatesettlement)           | financial-settlement.GenerateSettlement       | Operation    | Executes settlement for player and date window    |
| [ApplyMakeupPolicy](operations.md#applymakeuppolicycalculation)  | financial-settlement.ApplyMakeupPolicy        | Policy       | Governs debt reduction and payout split           |
| [SettlementExecutionState](states.md#settlementexecutionstate)   | financial-settlement.SettlementExecutionState | State Machine | Execution lifecycle for settlement side-effects    |
| [SettlementAPI](interfaces.md#external-settlementapi-rest)       | financial-settlement.SettlementAPI            | Interface    | REST boundary for settlement requests             |
| [GetSettlementPreview](queries.md#getsettlementpreview)          | financial-settlement.GetSettlementPreview     | Query        | Read model of computed period figures             |
| [SettlementGenerated](events.md#settlementgenerated)             | financial-settlement.SettlementGenerated      | Event        | Final settlement produced                         |
| [PayoutCreated](events.md#payoutcreated)                         | financial-settlement.PayoutCreated            | Event        | Payout transaction persisted                      |
| [SettlementRequestToInput](mappings.md#settlementrequesttoinput) | financial-settlement.SettlementRequestToInput | Mapping      | API input to use-case input                       |
| [SettlementWorkflow](workflows.md#settlementworkflow)            | financial-settlement.SettlementWorkflow       | Workflow     | End-to-end orchestration for settlement execution |

## Feature Concept Graph

| From                                       | Edge         | To                                            | Evidence                                        | Notes                                          |
| ------------------------------------------ | ------------ | --------------------------------------------- | ----------------------------------------------- | ---------------------------------------------- |
| financial-settlement.SettlementAPI         | exposes      | financial-settlement.GenerateSettlement       | interfaces.md#external-settlementapi-rest      | API exposes settlement generation endpoint     |
| financial-settlement.SettlementAPI         | exposes      | financial-settlement.GetSettlementPreview     | interfaces.md#external-settlementapi-rest      | API exposes settlement preview query           |
| financial-settlement.SettlementWorkflow    | orchestrates | financial-settlement.GenerateSettlement       | workflows.md#settlementworkflow                | Workflow coordinates settlement execution      |
| financial-settlement.ApplyMakeupPolicy     | applies      | financial-settlement.GenerateSettlement       | operations.md#applymakeuppolicycalculation     | Policy constrains debt and payout computation  |
| financial-settlement.GenerateSettlement    | produces     | financial-settlement.SettlementGenerated      | operations.md#generatesettlement               | Operation emits settlement generated event     |
| financial-settlement.SettlementGenerated   | transitions  | financial-settlement.SettlementExecutionState | states.md#settlementexecutionstate             | Event advances settlement execution lifecycle  |
| financial-settlement.SettlementRequestToInput | maps      | financial-settlement.SettlementResult         | mappings.md#settlementrequesttoinput           | Mapping shapes incoming request semantics      |

## Aspects

- [Domain](domain.md)
- [Operations](operations.md)
- [States](states.md)
- [Interfaces](interfaces.md)
- [Queries](queries.md)
- [Events](events.md)
- [Mappings](mappings.md)
- [Workflows](workflows.md)

## Cross-Feature Dependencies

| Depends On        | Relationship | Why                                 |
| ----------------- | ------------ | ----------------------------------- |
| player-management | queries      | Resolve player and deal context     |
| player-stats      | queries      | Aggregate period profit/rakeback    |
| player-makeup     | applies      | Apply debt policy and update makeup |

## Produces For

| Consumer      | Via                   | What                                     |
| ------------- | --------------------- | ---------------------------------------- |
| accounting    | Event                 | payout and debt-application side-effects |
| player-makeup | Operation side-effect | Updated player makeup                    |

## Stories

See [STORIES.md](STORIES.md) for capability-scoped user stories with classic + BDD format, acceptance checks, and Story Coverage Matrix.

## User Stories

See [STORIES.md](STORIES.md) for classic and BDD story definitions.

## Story Coverage Matrix

See [Story Coverage Matrix](STORIES.md#story-coverage-matrix) for concept and capability coverage.

## Pilot Decisions

Pilot policy and verification decisions are recorded in [PILOT-DECISIONS.md](PILOT-DECISIONS.md).
