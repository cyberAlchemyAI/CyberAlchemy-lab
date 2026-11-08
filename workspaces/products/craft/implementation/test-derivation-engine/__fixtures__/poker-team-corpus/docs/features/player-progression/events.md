---
id: player-progression
feature: player-progression
title: Player Progression Events
summary: Event contract emitted when progression criteria are evaluated.
status: implemented
pillar: operations
domain: player-progression-events
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

# Events: Player Progression

## ProgressionChecked

**Produced by:** [CheckProgression](operations.md#checkprogression)
**Triggers transition:** [ProgressionEvaluationLifecycle](states.md#progressionevaluationlifecycle)
**Implementation note:** emitted from `backend/src/use-cases/progression/check-progression.ts` and typed in `backend/src/domain/progression/progression.events.ts`.

### Payload

| Field | Type | Description |
| ----- | ---- | ----------- |
| playerId | string | Evaluated player |
| eligibleForPromotion | boolean | Promotion readiness flag |
| reason | string | Human-readable threshold result |
| avgHands | number | Average hands over selected window |
| winrate | number | Winrate in bb/100 |
| period | string | `BI_WEEKLY` or `MONTHLY` |
| occurredAt | datetime | Event timestamp |

### Consumed by

| Consumer | Action |
| -------- | ------ |
| player-management progression endpoint | Return progression status for dashboard consumption |
| operations dashboard | Display progression readiness and reason |
