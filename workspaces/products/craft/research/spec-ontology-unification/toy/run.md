---
node_type: toy-artifact
swu: T3 (run the toy + attack — the falsification)
is_session: false
status: candidate
created: 2026-07-01
inputs: [../toy/graph.md (T1), ../toy/mapping.md (T2), ../toy/catalog.md (T2b/M0)]
corpus: financial-settlement (backend)
scope: metrics + attack. Verdict is T4. Recomputable from graph.md + mapping.md + catalog.md.
---

# Toy Run — financial-settlement

## 0. FROZEN CRITERION (pre-registered in DEFINE.md before T1; frozen 2026-07-01, unchanged)

SURVIVED iff ALL: **M1** taxonomy closure = 100% (0 unclassifiable) · **M2** node→pattern ≥90% 1:1
(exceptions ≤10%) · **M3** edge→composition ≥90% coverage (gaps ≤10%) · **M4** cross-cutting context
bounded (0 unbounded leaks). INVALID if <3 categories (T1 cleared: 4). Thresholds NOT changed after seeing
data (DEF-D2 auto-adopted as proposed — no post-hoc tuning).

## 1. Metrics

- **M0 (catalog, from T2b):** entry-complete — 25/25 node patterns, 29/29 edge rules. **Coverage
  INCOMPLETE** — catalog misses ≥2 real edge types (op-reads-Entity, op-returns-VO). *[catalog-level]*
- **M1 taxonomy closure = 100% → PASS.** All 23 owned concepts classify to exactly one type; the latent
  `transaction` classifies as **Entity** (it *would* be one) → it is **classifiable but undeclared**, a
  **spec-completeness** gap (C10), not a closure failure. 0 concepts refuse a type.
- **M2 node→pattern = 22/23 ≈ 95.7% 1:1 → PASS (≥90%).** One hard exception: `ApplyMakeupPolicyCalculation`
  (dual Calculation∧Policy → 2 patterns, 4.3%). One composite (Event = payload+publisher; still one
  coherent pattern). Even counting Event as an exception: 21/23 = 91.3% ≥ 90%.
- **M3 edge→composition = 24/25 = 96% → PASS (≥90%).** 24 of the 25 graph edges map to a rule; **1 untyped**
  (op-reads-Entity, no edge type). Counting the never-formed op-returns-VO relation too: 24/26 = 92.3% ≥ 90%.
- **M4 context-boundedness → PASS (bounded).** Cross-feature deps (Player, PlayerStatsSnapshot) are all
  reached via **named-carrier** edges (`queries`, `produces-for`) = M4-b. **0 unbounded (M4-c) leaks.**
  Caveat: the 1 untyped read (op→PlayerStatsSnapshot) is **named but untyped** — bounded, but lacks a typed
  carrier (→ R3-P1).

**Determinism:** recomputing M1–M4 from graph.md + mapping.md yields the same numbers (the mapping is a
table lookup + edge-rule table). ✓

## 2. Attack (3 lenses)

- **1:1-break:** the only node→pattern break is the dual-typed `ApplyMakeupPolicyCalculation`. Root cause is
  **operations.md typing it as both** — a *spec-authoring* defect (should be split into a Calculation +
  a Policy), NOT a taxonomy defect (Calculation and Policy each have clean, distinct patterns). Verdict input:
  indicts the **doc**, not the hypothesis.
- **cross-cutting context:** the feared failure ("a pattern needs the whole graph") **did not occur** — every
  external dependency (Player, PlayerStatsSnapshot) is carried by a *named* cross-feature edge. The one soft
  spot is the **untyped** op-reads-Entity (A3a): bounded to a named entity, but the edge-law can't express it
  → **R3-P1**, a catalog gap, not an unbounded leak.
- **taxonomy-closure-under-stress:** the feature **creates a `transaction` entity it never declares** (P3/P4
  "create tx"). Nothing refuses a type (it's an Entity), but the spec is **incomplete** — it acts on an
  unmodeled node. A *spec-completeness* (C10) finding, not a closure/hypothesis failure.

## 3. Result (feeds T4 — not the verdict itself)

- Per-corpus bars **M1–M4 all PASS** on financial-settlement.
- **But** two catalog/coverage qualifiers stand: **M0-coverage INCOMPLETE** (≥2 missing edge types) and
  **exercise coverage only 12/25 types, 10/29 edges** (the rest catalog-checked but not feature-exercised).
- **Every failure/exception traced to a v1-SPEC-DOC gap** (dual-typing, undeclared entity, missing edge
  types) — fixable by the batch-1 reformulation (R3/completeness), **not** a hypothesis failure. T4 must
  make this distinction the headline.
