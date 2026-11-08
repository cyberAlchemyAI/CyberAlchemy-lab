---
node_type: toy-artifact
swu: T2 (author the mapping tables)
is_session: false
status: candidate
created: 2026-07-01
inputs: [../toy/graph.md, ../../../impl/spec/TAXONOMY.md (Architecture Mapping Appendix), ../DESIGN.md §2]
work_pack: ../development/WORK-PACK.md
scope: MAPPING ONLY — per-type 1:1 judgement recorded; the M1/M2/M3 aggregate SCORES are T3 (after criterion freeze). No pattern invented to force 1:1.
---

# Mapping Tables — financial-settlement

Maps the T1 spec-graph (23 nodes / 25 edges) to code patterns (nodes) and composition rules (edges).
Node patterns are **copied** from `impl/spec/TAXONOMY.md` "Architecture Mapping Appendix (Functional
Style)"; edge rules extend DESIGN §2. Exceptions/gaps are recorded honestly for T3, not scored here.

## A. Node → code-pattern (by type; all 23 nodes covered)

| TAXONOMY type | #nodes | Code pattern (TAXONOMY appendix) | 1:1 at type? | note |
| --- | --- | --- | --- | --- |
| Value Object | 1 | immutable `type` + ctor/factory + pure helpers | ✅ | SettlementResult |
| Enum / Type | 1 | enum or union type | ✅ | SettlementTransactionType |
| Operation | 1 | use-case factory `makeX(deps)->(input)=>Promise<out>` | ✅ | GenerateSettlement |
| Rule | 5 | pure predicate function (`boolean`) | ✅ | R1–R5 |
| Calculation | 4 | pure deterministic function | ✅ | C1–C4 |
| Query | 1 | query factory `makeX(deps)->(input)=>Promise<view>` | ✅ | GetSettlementPreview |
| Workflow | 1 | intra-feature orchestrator fn + compensation stack | ✅ | SettlementWorkflow |
| Policy | 1 | strategy-selection function | ✅ | DefaultMakeupPolicy |
| Interface | 2 | boundary handlers (HTTP/RPC/module) calling use-cases | ✅ | SettlementAPI (REST) + SettlementModule (module) — same pattern, two carriers |
| Event | 2 | **payload type (domain) + publisher adapter (infra)** | ⚠️ composite | 1 pattern spanning 2 layers — not a clean single artifact |
| Mapping | 2 | pure shape-transformation functions | ✅ | SettlementRequestToInput, SettlementResultToResponse |
| State Machine | 1 | transition table/map + guard checks + pure transition fn | ✅ | SettlementExecutionState |
| **Calculation ∧ Policy (DUAL)** | 1 | pure fn **AND** strategy-selection fn — **2 candidate patterns** | ❌ **>1** | **ApplyMakeupPolicyCalculation** (A1 exception) |

**Node coverage:** 23/23 accounted for. Clean 1:1 types: 11 of 12. Exceptions: **1 node** (dual-typed →
2 patterns, A1). Composite (not an exception, but non-atomic): **Event** (payload+publisher).

## B. Edge → composition rule (by type; all 25 edges covered)

| Edge type | #edges | Composition rule (pattern A ∘ pattern B) | mapped? |
| --- | --- | --- | --- |
| exposes | 3 | Interface boundary handler **calls** the Operation/Query use-case | ✅ |
| produces | 2 | Operation **returns/emits** the Event payload on success; publisher adapter dispatches | ✅ |
| enforces | 5 | Rule predicate **invoked inside** the Operation use-case before the state change; false ⇒ reject | ✅ |
| calculates | 5 | Calculation pure fn **called by** the Operation to derive a value | ✅ |
| orchestrates | 1 | Workflow fn **calls** the Operation factories in sequence with a compensation stack | ✅ |
| applies | 1 | Policy strategy-selection fn **chosen/invoked by** the Operation to pick behavior | ✅ |
| transitions | 2 | Event is an **input symbol** of the transition table; triggers a guarded transition | ✅ |
| maps | 2 | Mapping pure shape-transform fn **converts between** the boundary shapes | ✅ |
| queries | 2 | Query factory **reads** the (cross-feature) Entity read-model | ✅ (cross-feature) |
| produces-for | 1 | Operation@A **writes/projects into** a cross-feature Entity@B via B's contract | ✅ (cross-feature) |
| **(reads) Operation→Entity** | 1 | — **no edge type ⇒ no composition rule** | ❌ **GAP (A3)** |

**Edge coverage:** 25/25 accounted for. Mapped edge-types: 10 of 10 present. Gaps: **1 edge** with no
type/rule (GenerateSettlement reads PlayerStatsSnapshot). Also latent: **Operation → returns → Value
Object** (GenerateSettlement → SettlementResult, P1) has **no edge type at all** in the T1 graph — a
missing-edge gap for T3/M3.

## C. Exceptions & gaps (raw material for T3 — NOT scored here)

- **A1 (node >1 pattern):** ApplyMakeupPolicyCalculation → {pure fn, strategy-selection fn}. Root cause:
  dual-typing in operations.md. T3/M2 decides whether this indicts the *node* (should be split into a
  Calculation + a Policy) or the *taxonomy* (Calculation/Policy overlap).
- **A3a (edge, no type):** Operation-reads-Entity. RELATIONSHIPS has `queries` (Query→Entity) but nothing
  for an Operation reading an entity for its calculations.
- **A3b (edge, missing):** Operation-returns-ValueObject — the operation's *output type* has no edge to
  hang on; the graph loses the Operation→SettlementResult relation entirely.
- **Composite note (Event):** node→pattern is 1→(payload+publisher) — near-1:1 but not atomic; T3/M2
  decides whether "1 pattern, 2 layers" counts as 1:1.
- **Cross-feature carriers (feeds M4):** `queries`/`produces-for` edges (#22–24) DO name their external
  Entity (Player, PlayerStatsSnapshot) — bounded/named carriers; but the A3a *untyped* read is an
  **unnamed** dependency ⇒ a candidate M4 leak T3 must classify.

## D. Counts (feed T3)
- node types mapped 1:1: **11/12**; node exceptions: **1** (A1); composite: **1** (Event).
- edge types with a rule: **10/10**; edge gaps: **1 untyped (A3a)** + **1 missing (A3b)**.
- every T1 node (23) and edge (25) has a row or an explicit exception/gap — **no silent drops**.
