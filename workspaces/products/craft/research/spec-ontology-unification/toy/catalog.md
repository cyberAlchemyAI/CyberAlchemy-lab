---
node_type: toy-artifact
swu: T2b (catalog coverage — all 25 types + 29 edges + M0)
is_session: false
status: candidate
created: 2026-07-01
inputs: [impl/spec/TAXONOMY.md (Architecture Mapping Appendix — 25 patterns), impl/spec/RELATIONSHIPS.md (29 edge signatures), ../toy/mapping.md (T2's 10 rules), ../toy/graph.md (T1 missing-edge finding)]
work_pack: ../development/WORK-PACK.md
scope: FEATURE-INDEPENDENT catalog check. Authors composition rules; records M0. NO edit to impl/spec/RELATIONSHIPS.md — catalog gaps are proposed to batch-1 R3.
---

# Catalog Coverage — all 25 types × 29 edges (M0)

Tests the **catalog's** completeness, independent of any feature (which the single-corpus toy cannot):
does every TAXONOMY type have exactly one code pattern, and every RELATIONSHIPS edge a composition rule?
Composition rules are authored here (grounded in each endpoint's node-pattern); rules that need invented
structure are recorded as **catalog gaps** → R3, never forced.

## A. Node → pattern (all 25 types)

Every type has exactly **one** appendix pattern. 24 atomic; 1 composite (Event = 2 layers).

Backend (14): Entity→type+factory+transition-fns · Value Object→immutable type+ctor · Enum→enum/union ·
Operation→use-case factory · Query→query factory · Calculation→pure fn · Rule→pure predicate ·
Policy→strategy-selection fn · Workflow→intra-feature orchestrator+compensation · Saga→cross-feature
orchestrator+compensation · Interface→boundary handler · **Event→payload type (domain)+publisher (infra)
[composite]** · Mapping→pure shape-transform · State Machine→transition table+guards+transition fn.

UI (11): Page→.astro (layout+island) · Layout→layout+`<slot/>` · Component→typed-props fn component ·
View Model→TS type · Hook→`use{Name}()` (TanStack) · Form→Zod schema+`useForm` · Action→event handler ·
Guard→auth check→redirect/null · Binding→`useQuery`/`useMutation` config · Adapter→pure API→VM fn ·
State Indicator→badge/icon `Record<state,visual>`.

**M0-node = 25/25 have a pattern** (24 atomic 1:1, 1 composite).

## B. Edge → composition rule (all 29; T2 = 10, T2b authors 19)

**Backend (15):**

| Edge (from→to) | Composition rule | src |
| --- | --- | --- |
| performs (Entity→Operation) | Operation factory takes the Entity/actor as its acting subject | **T2b** |
| produces (Operation→Event) | Operation returns/emits the Event payload on success | T2 |
| produces-for (Operation@A→Entity@B) | A's Operation writes/projects into B's Entity via B's contract | T2 |
| triggers-cross (Event@A→Operation@B) | A's Event payload is consumed by B's subscriber adapter, which invokes B's Operation | **T2b** ⚠ needs cross-feature carrier |
| enforces-cross (Rule@A→Operation@B) | A's Rule predicate is invoked inside B's Operation via B's contract | **T2b** ⚠ needs cross-feature carrier |
| enforces (Rule→Operation) | Rule predicate invoked inside the Operation before the state change | T2 |
| calculates (Calculation→Operation) | Calculation pure fn called by the Operation to derive a value | T2 |
| transitions (Event→State Machine) | Event is an input symbol of the transition table | T2 |
| exposes (Interface→Operation/Query) | Interface handler calls the Operation/Query use-case | T2 |
| orchestrates (Workflow→Operation[]) | Workflow fn calls the Operation factories in sequence + compensation | T2 |
| applies (Policy→Operation) | Policy strategy-selection fn chosen/invoked by the Operation | T2 |
| maps (Mapping→Entity/Interface) | Mapping pure fn converts between the boundary shapes | T2 |
| contains (Entity→Value Object) | Entity type embeds the Value Object type as a field | **T2b** |
| queries (Query→Entity) | Query factory reads the Entity read-model | T2 |
| emits (Entity→Event) | Entity transition fn returns the Event payload; publisher dispatches | **T2b** |

**Intra-UI (8) — all T2b:**

| Edge | Composition rule |
| --- | --- |
| renders (Page→Component[]) | Page `.astro` imports + mounts the Components as React islands |
| wraps (Layout→Page[]) | Layout wraps the Page via `<slot/>` |
| composes (Component→Component[]) | parent Component includes child Component(s) in JSX |
| consumes (Component→Hook) | Component calls the `use{Name}()` hook for data/state |
| submits (Form→Action) | Form `onSubmit` (post Zod-validate) calls the Action handler |
| shapes (Adapter→View Model) | Adapter pure fn returns the View Model type from API data |
| protects (Guard→Page) | Guard auth-check gates the Page render (redirect/null) |
| displays (Component→View Model) | Component renders fields from the View Model type |

**Cross-Layer (6) — all T2b:**

| Edge | Composition rule |
| --- | --- |
| fetches (Binding→Query) | Binding `useQuery` config calls the backend Query use-case over HTTP |
| mutates (Binding→Operation) | Binding `useMutation` config invokes the backend Operation over HTTP |
| reflects (State Indicator→State Machine) | Indicator maps the machine's current state → visual (`Record<state,visual>`) |
| derives (View Model→Entity) | View Model type is projected (pure) from the Entity's fields |
| contracts (Form→Interface) | Form's Zod schema aligns with the Interface endpoint request contract |
| mirrors (Guard→Rule) | client Guard predicate duplicates the backend Rule predicate |

**M0-edge = 29/29 have an authored rule** (10 T2 + 19 T2b; 0 forced-invention among the 29).

## C. The real finding — catalog is entry-complete but COVERAGE-incomplete

Every one of the 29 edges maps — **but the 29-edge catalog does not cover the relations a real feature
needs.** T1 already found **2 relations with no edge type in the catalog at all**:

| Missing edge type | Seen at (T1) | Why the catalog misses it |
| --- | --- | --- |
| **Operation → reads → Entity** | GenerateSettlement reads PlayerStatsSnapshot | `queries` is Query→Entity only; no Operation→Entity read edge exists |
| **Operation → returns → Value Object** | GenerateSettlement → SettlementResult (P1) | no edge for an Operation's output/return type |

So M0 splits into two honest numbers:
- **M0-entry (do catalog entries map): 25/25 types, 29/29 edges — COMPLETE.**
- **M0-coverage (does the catalog span real relations): INCOMPLETE — ≥2 needed edge types are absent.**

Plus two near-1:1 caveats (not gaps, for T3/M2): **Event** node = composite (payload+publisher);
**triggers-cross / enforces-cross** compositions require a cross-feature carrier (interface/event-bus).

## D. Proposals to batch-1 R3 (RELATIONSHIPS reformulation) — NOT applied here
- **R3-P1:** add an `Operation → Entity` read edge (or generalize `queries` to `Behavioral→Entity`).
- **R3-P2:** add an `Operation → Value Object` (returns/produces-result) edge for operation output types.
- **R3-P3:** decide whether Event's composite pattern (payload+publisher) is one node or should split
  (payload = Structural, publisher = Connective) — affects node→pattern 1:1.

## E. M0 result (feeds T3)
- M0-node: **25/25** typed patterns (24 atomic, 1 composite).
- M0-edge-entry: **29/29** authored rules (0 forced).
- M0-coverage: **INCOMPLETE** — catalog misses ≥2 real edge types (R3-P1/P2).
- exercise coverage of the corpus (from T1): 12/25 types, 10/29 edges — the other 13 types / 19 edges are
  catalog-checked here but **not exercised on a real feature** (only a 2nd corpus would).
