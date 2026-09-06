---
id: financial-settlement-ui
feature: financial-settlement
title: Financial Settlement UI Specification
summary: Frontend design contract for settlement preview, generation, and results display.
status: draft
pillar: platform
domain: financial-settlement-ui
audience:
  - developers
priority: p1
lang: en
owners:
  - web-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - interfaces.md
  - operations.md
  - queries.md
  - workflows.md
  - STORIES.md
includes: []
constitution: docs/UI-ARCHITECTURE.md
---

# UI Specification: Financial Settlement

> Governs the frontend presentation of settlement preview, execution, and results.
> Constrained by [UI-ARCHITECTURE.md](../../UI-ARCHITECTURE.md).

---

## Route Table

| Route          | Page Title  | Layout          | Auth Required | Permission                                       |
| -------------- | ----------- | --------------- | ------------- | ------------------------------------------------ |
| `/settlements` | Settlements | DashboardLayout | Yes           | `financial-settlement.read.getSettlementPreview` |

---

## Page Layouts

### /settlements

```
┌──────────────────────────────────────────────────┐
│ Header: "Settlements"                            │
├──────────────────────────────────────────────────┤
│ SettlementForm                                   │
│   Player:     [Select player ▼]                  │
│   Start Date: [2026-04-01]                       │
│   End Date:   [2026-04-15]                       │
│   [Preview]  [Generate Settlement]               │
├──────────────────────────────────────────────────┤
│ SettlementPreviewCard (shown after Preview)      │
│ ┌──────────────────────────────────────────────┐ │
│ │ Period: 2026-04-01 → 2026-04-15             │ │
│ │                                              │ │
│ │ ┌────────────────────┬───────────────────┐   │ │
│ │ │ Total Profit       │ $3,400            │   │ │
│ │ │ Total Rakeback      │ $800              │   │ │
│ │ │ Previous Makeup     │ $1,250            │   │ │
│ │ ├────────────────────┼───────────────────┤   │ │
│ │ │ Makeup Applied      │ -$1,250           │   │ │
│ │ │ Projected New Makeup│ $0                │   │ │
│ │ │ Projected Payout    │ $1,475            │   │ │
│ │ └────────────────────┴───────────────────┘   │ │
│ │                                              │ │
│ │ [Confirm & Generate]                         │ │
│ └──────────────────────────────────────────────┘ │
│                                                  │
│ SettlementResultCard (shown after Generate)      │
│ ┌──────────────────────────────────────────────┐ │
│ │ ✅ Settlement Generated                      │ │
│ │ Total Profit:    $3,400                      │ │
│ │ Total Rakeback:  $800                        │ │
│ │ Makeup Applied:  $1,250                      │ │
│ │ New Makeup:      $0                          │ │
│ │ Payout:          $1,475                      │ │
│ │ Player Share:    50%                         │ │
│ └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

---

## Component Inventory

| Component               | Type | Location                                           | Purpose                               |
| ----------------------- | ---- | -------------------------------------------------- | ------------------------------------- |
| `SettlementPage`        | Page | `components/settlements/SettlementPage.tsx`        | Orchestrates form + preview + result  |
| `SettlementForm`        | Form | `components/settlements/SettlementForm.tsx`        | Player/date selection + actions       |
| `SettlementPreviewCard` | Card | `components/settlements/SettlementPreviewCard.tsx` | Read-only preview with confirm button |
| `SettlementResultCard`  | Card | `components/settlements/SettlementResultCard.tsx`  | Final settlement summary              |

---

## Data Flow

### /settlements

| API Call                                      | Hook                      | Cache Key                         | Triggers       |
| --------------------------------------------- | ------------------------- | --------------------------------- | -------------- |
| `GET /players`                                | `usePlayers()`            | `queryKeys.players.list()`        | Page mount     |
| `GET /settlements/preview?playerId&start&end` | `useSettlementPreview()`  | `queryKeys.settlements.preview()` | Preview click  |
| `POST /settlements`                           | `useGenerateSettlement()` | Invalidate players + makeup       | Generate click |

**Side effects after Generate:**

- Invalidate `queryKeys.players.list()` (bankroll/makeup may change)
- Invalidate `queryKeys.players.makeup(playerId)` (makeup updated)
- Show SettlementResultCard

---

## Form Contracts

### SettlementForm

| Field     | Type   | HTML Input | Validation                | Error Message                  |
| --------- | ------ | ---------- | ------------------------- | ------------------------------ |
| playerId  | string | `select`   | Required                  | "Select a player"              |
| startDate | string | `date`     | Required, valid date      | "Start date is required"       |
| endDate   | string | `date`     | Required, valid, >= start | "End date must be after start" |

**Zod schema:**

```typescript
z.object({
  playerId: z.string().min(1, "Select a player"),
  startDate: z.string().min(1, "Start date is required"),
  endDate: z.string().min(1, "End date is required"),
}).refine((d) => d.endDate >= d.startDate, {
  message: "End date must be after start date",
  path: ["endDate"],
});
```

**Error Code → UI Message Mapping:**

| API Error Code     | HTTP Status | UI Message              |
| ------------------ | ----------- | ----------------------- |
| `PLAYER_NOT_FOUND` | 404         | "Player not found."     |
| (validation)       | 400         | Show field-level errors |

---

## State-to-UI Mapping

| Page State       | UI Representation                                    |
| ---------------- | ---------------------------------------------------- |
| Initial          | Form visible, preview/result hidden                  |
| Preview loading  | Preview button disabled, spinner                     |
| Preview shown    | SettlementPreviewCard visible with Confirm button    |
| Generate loading | Confirm button disabled, spinner                     |
| Generate success | SettlementResultCard replaces preview, success toast |
| Generate error   | Error alert below form, preview remains              |

---

## Accessibility Requirements

| Component             | Requirement                                                  |
| --------------------- | ------------------------------------------------------------ |
| SettlementForm        | `role="form"`, `aria-label="Settlement parameters"`          |
| SettlementPreviewCard | `aria-live="polite"` for when preview loads                  |
| SettlementResultCard  | `role="alert"` on success, focus shifts to result            |
| Confirm button        | Requires double-action (preview then confirm) as safety gate |
| Date inputs           | `aria-label` with "Start date" / "End date"                  |
