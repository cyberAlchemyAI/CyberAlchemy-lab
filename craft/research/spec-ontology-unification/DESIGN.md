---
node_type: design
is_session: false
status: candidate
created: 2026-07-01
authored_by: invoke (mode: design)
define: ./DEFINE.md
build_from: ./SEED.md
target_artifact: spec-ontology-unification toy
promotion_boundary: LOCAL RESEARCH ONLY (SEED.md:56-58) — the toy produces a verdict + evidence, never a spec/code mutation
---

# Design — Spec–Ontology Unification Toy

The architecture of the paper toy that tests DEFINE's four-part criterion. It is a **measurement
harness over one feature**, not a code generator: "spec subgraph in → pattern skeleton out (on paper)
→ metrics + attack".

## 1. Architecture (the toy pipeline)

```
financial-settlement spec  ──►  [T1 extract]  ──►  spec-graph (typed nodes + typed edges)
                                                        │
spec-graph + mapping tables ──►  [T2 map]     ──►  node→pattern table + edge→composition table
                                                        │
mapping applied to the graph ──► [T3 run+attack] ─► pattern skeleton (paper) + 4 metrics + break-list
                                                        │
                              ──► [T4 compare]   ──►  Lane A sketch + SURVIVED/FALSIFIED verdict + rec
```

Authority flows **one way** (spec → toy artifacts); nothing writes back to the spec (promotion boundary).
The engine stays black-box — the toy reasons about the spec-graph, never the δ-rules.

## 2. The mapping model (mostly OWNED, made explicit)

**Node→pattern is not net-new** — it already lives in `impl/spec/TAXONOMY.md` "Architecture Mapping
Appendix (Functional Style)" (Entity → type+factory+transitions; Value Object → immutable type+ctor;
Operation → use-case factory; Rule → pure predicate; Calculation → pure fn; State Machine → transition
table; Event → payload type + publisher; etc.). The toy **uses that table as the hypothesis** and tests
its 1:1-ness on a real feature.

**Edge→composition is partially implicit** — the toy makes it explicit as a table keyed by the 29
RELATIONSHIPS edges, e.g.:

| Edge | Composition rule (pattern A ∘ pattern B) |
| --- | --- |
| `enforces` (Rule→Operation) | Rule predicate is invoked inside the Operation use-case before the state change |
| `orchestrates` (Workflow→Operation[]) | Workflow fn calls the Operation factories in sequence with a compensation stack |
| `produces` (Operation→Event) | Operation returns/emits the Event payload type on success |
| `contains` (Entity→Value Object) | Entity type embeds the Value Object type as a field |
| `transitions` (Event→State Machine) | Event is an input symbol of the transition table |
| `exposes` (Interface→Operation) | Interface handler calls the Operation use-case |

(The toy fills the full 29-edge table for the corpus's edges; unmapped edges are gaps counted against
criterion 3.)

## 3. Measurement instruments (one per criterion — deterministic, reproducible)

- **M0 catalog coverage (feature-independent; added 2026-07-01).** Of the 25 TAXONOMY types, how many
  have exactly one appendix pattern? Of the 29 RELATIONSHIPS edges, how many have an authored composition
  rule? This tests the *catalog's* completeness, not the corpus's — the single-feature toy can't. (T2
  authored only **10/29** edge rules; the other 19 are the live gap, written by SWU-T2b.)
- **M1 taxonomy closure** = classified concepts / total concepts (target 100%). Instrument: cross the
  feature's concept list against the 25 types; any residue is an M1 failure.
- **M2 node→pattern 1:1** = nodes with exactly one pattern / total nodes (target ≥90%). Record every
  0-pattern and >1-pattern exception with the reason.
- **M3 edge→composition coverage** = edges with a named rule / total edges (target ≥90%). Record gaps.
- **M4 context-boundedness** = for each pattern, is every required input reachable from the node's own
  subgraph (node + direct edges)? Classify each leak as (a) none, (b) named-carrier (e.g. shared VO via
  `contains`), or (c) unbounded. Any (c) is an M4 failure.

Determinism check: re-running T3 from the same spec-graph + mapping tables must reproduce the same
metrics (if not, the mapping is under-specified — itself a finding).

**Exercise coverage (added 2026-07-01).** Record which of the 25 types / 29 edges the corpus actually
exercised (financial-settlement: **12/25, 10/29**). M1–M4 are *corpus-scoped*; M0 + exercise-coverage
keep the verdict honest about how much of the catalog was tested. A SURVIVED verdict states its coverage.

## 4. Attack lenses (Lane Z zig-zag — SEED.md:43-47)

The toy is not complete until it is attacked on:
- **1:1 break** — which node-types resolve to multiple patterns or none? (e.g. does Policy vs Rule blur?
  does Saga need >1 pattern?)
- **cross-cutting context** — what breaks when a pattern needs data the subgraph doesn't carry? (the
  SEED's central worry — shared Value Objects, cross-feature edges, auth/tenancy context.)
- **taxonomy closure under stress** — does anything in a *real* feature refuse to be one of the 25?

## 5. Lane A comparison harness

For the same feature, sketch the Lane A alternative: keep spec and code separate, **generate** a
bidirectional node→pattern mapping + a drift check (the v1 direction). Compare on: does Lane A deliver
the same "bounded agent context" (a generated map the agent queries) **without** fusing spec and code?
The verdict weighs Lane Z's 4 metrics against Lane A's cost, per the SEED's own Lane-A mandate.

## 6. Design views coverage

- **Context** — §1 pipeline. **Structure** — §2 mapping model. **Data** — the spec-graph + two mapping
  tables. **Behavior** — §3 measurement + §4 attack. **Alternatives** — §5 Lane A. **Boundary** —
  promotion boundary + engine black-box + one-way authority.

## 7. Design decisions surfaced

- **DES-D1** — is the node→pattern appendix authoritative enough to test as-is, or does it need
  completion first? Recommend: test as-is; incompleteness is itself an M2/M3 finding.
- **DES-D2** — paper toy vs a tiny script that computes M1–M4 from the extracted graph. Recommend:
  paper first (T3); promote to a script only if the tower survives (avoids overbuild before the verdict).
