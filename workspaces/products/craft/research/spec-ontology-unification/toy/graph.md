---
node_type: toy-artifact
swu: T1 (extract the spec-graph)
is_session: false
status: candidate
created: 2026-07-01
corpus: impl/test-derivation-engine/__fixtures__/financial-settlement/ (backend aspect files; UI-SPEC deferred)
work_pack: ../development/WORK-PACK.md
scope: EXTRACTION ONLY — no mapping (T2) or metrics (T3); anomalies are noted, not scored
---

# Spec-Graph — financial-settlement (backend)

Typed node + edge inventory extracted from the feature's aspect files, typed against
`impl/spec/TAXONOMY.md` (25 types) and `impl/spec/RELATIONSHIPS.md` (29 edges). Feeds T2 (mapping) and
T3 (M1–M4). "Owned" = defined by this feature; external/latent concepts are listed separately (they are
the cross-cutting-context surface T3's M4 measures).

## Nodes (owned — 23)

| # | Node | TAXONOMY type | Category | Source |
| --- | --- | --- | --- | --- |
| 1 | SettlementResult | Value Object | Structural | domain.md |
| 2 | SettlementTransactionType | Enum | Structural | domain.md |
| 3 | GenerateSettlement | Operation | Behavioral | operations.md |
| 4 | R1 player-must-exist | Rule | Behavioral | operations.md |
| 5 | R2 required-fields | Rule | Behavioral | operations.md |
| 6 | R3 period-range | Rule | Behavioral | operations.md |
| 7 | R4 dedupe-MAKEUP | Rule | Behavioral | operations.md |
| 8 | R5 dedupe-PAYOUT | Rule | Behavioral | operations.md |
| 9 | C1 total-profit | Calculation | Behavioral | operations.md |
| 10 | C2 total-rakeback | Calculation | Behavioral | operations.md |
| 11 | C3 deal-split | Calculation | Behavioral | operations.md |
| 12 | C4 makeup-new-debt | Calculation | Behavioral | operations.md |
| 13 | ApplyMakeupPolicyCalculation | **Calculation ∧ Policy (DUAL)** | Behavioral | operations.md |
| 14 | GetSettlementPreview | Query | Behavioral | queries.md |
| 15 | SettlementWorkflow | Workflow | Behavioral | workflows.md |
| 16 | DefaultMakeupPolicy | Policy | Behavioral | workflows.md |
| 17 | SettlementAPI | Interface | Connective | interfaces.md |
| 18 | SettlementModule | Interface | Connective | interfaces.md |
| 19 | SettlementGenerated | Event | Connective | events.md |
| 20 | PayoutCreated | Event | Connective | events.md |
| 21 | SettlementRequestToInput | Mapping | Connective | mappings.md |
| 22 | SettlementResultToResponse | Mapping | Connective | mappings.md |
| 23 | SettlementExecutionState | State Machine | Lifecycle | states.md |

**External referenced (cross-feature, not owned):** `Player` (Entity @ player-management),
`PlayerStatsSnapshot` (@ player-stats). **Latent (implied, no formal node):** `transaction`/`tx`
(only its Enum `SettlementTransactionType` is defined — the transaction Entity itself is never declared).

## Edges (25)

| # | From | Edge | To | Source | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | SettlementAPI | exposes | GenerateSettlement | interfaces.md | |
| 2 | SettlementAPI | exposes | GetSettlementPreview | interfaces.md | GET preview |
| 3 | SettlementModule | exposes | GenerateSettlement | interfaces.md | internal |
| 4 | GenerateSettlement | produces | SettlementGenerated | events.md | |
| 5 | GenerateSettlement | produces | PayoutCreated | events.md | |
| 6–10 | R1–R5 | enforces | GenerateSettlement | operations.md | 5 edges |
| 11–14 | C1–C4 | calculates | GenerateSettlement | operations.md | 4 edges |
| 15 | ApplyMakeupPolicyCalculation | calculates | GenerateSettlement | operations.md | used-by |
| 16 | SettlementWorkflow | orchestrates | GenerateSettlement | workflows.md | |
| 17 | DefaultMakeupPolicy | applies | GenerateSettlement | workflows.md | |
| 18 | SettlementGenerated | transitions | SettlementExecutionState | states.md | |
| 19 | PayoutCreated | transitions | SettlementExecutionState | states.md | |
| 20 | SettlementResultToResponse | maps | SettlementResult | mappings.md | |
| 21 | SettlementRequestToInput | maps | SettlementAPI→GenerateSettlement | mappings.md | |
| 22 | GetSettlementPreview | queries | Player | queries.md | cross-feature |
| 23 | GetSettlementPreview | queries | PlayerStatsSnapshot | queries.md | cross-feature |
| 24 | GenerateSettlement | produces-for | Player | operations.md P2 | cross-feature |
| 25 | GenerateSettlement | (reads) | PlayerStatsSnapshot | operations.md C1/C2 | **no clean edge type** |

Distinct edge types used: `exposes, produces, enforces, calculates, orchestrates, applies, transitions, maps, queries, produces-for` (10 of 29).

## Category coverage (T1 acceptance gate)

Categories exercised: **Structural, Behavioral, Connective, Lifecycle = 4** (≥3 required → **NOT INVALID**;
proceed to T2). Backend TAXONOMY types instantiated: **12 of 14** (missing: **Entity** — owns none; and
**Saga** — none).

## Extraction observations (for T2/T3 — noted, NOT scored here)

- **A1 (M2 signal — node↔type not 1:1):** node #13 `ApplyMakeupPolicyCalculation` is typed **both**
  Calculation and Policy in operations.md. A candidate node→pattern ambiguity.
- **A2 (M1 signal — taxonomy closure):** the feature owns **zero Entity** nodes; it mutates a latent
  `transaction` entity never formally declared (only its Enum). Is "transaction" an unclassified concept
  or an intentional cross-feature/ledger entity? T3/M1 must decide.
- **A3 (M3 signal — edge-law gap):** edge #25 `GenerateSettlement (reads) PlayerStatsSnapshot` has **no
  clean RELATIONSHIPS edge type** (`queries` is Query→Entity, not Operation→Entity). Also, no edge exists
  for "Operation returns Value Object" (GenerateSettlement → SettlementResult, P1). Two candidate
  edge-law gaps for T3/M3.
- **A4 (M4 signal — cross-cutting context):** the feature depends on external `Player` +
  `PlayerStatsSnapshot` via edges #22–25 — all **named-carrier** cross-feature edges so far (not
  unbounded), which is the M4-b class T3 will confirm.
- **A5 (type-overlap):** `GenerateSettlement` (Operation) is also used as a transition **event symbol**
  in the state machine (states.md transition table) — Operation-as-Event overlap for T3 to weigh.

## Counts (feed M1/M2/M3 in T3)
- owned nodes: 23 · dual-typed: 1 · external referenced: 2 · latent/undeclared: 1
- edges: 25 · distinct edge types: 10 · edges with no clean type: 1 (+1 missing "op-returns-VO")
