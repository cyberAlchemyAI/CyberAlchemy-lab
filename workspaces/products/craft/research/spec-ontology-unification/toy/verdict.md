---
node_type: toy-artifact
swu: T4 (Lane A compare + verdict)
is_session: false
status: candidate
created: 2026-07-01
inputs: [../toy/run.md (M0–M4 + attack), ../toy/catalog.md, ./SEED.md (Lane Z/A), ../../2026-07-01-spec-as-ontology/findings.md (two-plane boundary)]
promotion_boundary: SEED.md:56-58 — this verdict recommends the next approved task-session; it mutates no spec/schema.
---

# Verdict — Spec–Ontology Unification Toy (financial-settlement)

## 1. Verdict: **SURVIVED — narrow + conditional**

Against the frozen criterion, on financial-settlement: **M1 100% · M2 ~96% · M3 ~96% · M4 bounded — all
four bars PASS.** The typed spec-graph **is** a viable code substrate for the tested feature. But the
survival is **narrow** (exercise coverage 12/25 types, 10/29 edges) and **conditional** (M0-coverage
INCOMPLETE — the edge catalog misses ≥2 real relations).

**Headline (the distinction the toy was built to make):** every exception traced to a **v1-spec-doc gap**,
not a hypothesis failure —
- dual-typed node (A1) → operations.md mistyped it (split into Calculation + Policy),
- untyped/missing edges (A3a/b) → RELATIONSHIPS catalog under-covers (R3-P1/P2),
- undeclared `transaction` (A2) → a spec-completeness (C10) gap.

The substrate hypothesis is **not** what failed. The **v1 spec docs are incomplete** — which is exactly
what the batch-1 reformulation exists to fix.

## 2. Lane Z vs Lane A (SEED.md:43-53) — still OPEN, and the toy explains why

The mapping that survived is a **deterministic table lookup** (node→pattern from the appendix; edge→rule
from catalog.md). That is precisely what **Lane A** (keep spec + ontology separate, *generate* a
bidirectional mapping + drift check) needs — and equally what **Lane Z** (fuse them) needs. So the toy
proves the **mapping is viable**, which **both lanes require**; it does **not** decide between them.

The Lane-Z-vs-A decider is SEED's actual claim — *"makes implementation agents cheaper / less
drift-prone"* — which this paper toy **cannot** measure (the **proxy gap**: M1–M4 are substrate metrics,
not agent-cost). So **Lane Z-vs-A stays deferred** to a later **agent-run experiment**. Until then, the
**two-plane boundary** from the 2026-07-01 spec-as-ontology research holds as the safe interim (ontology on
the authoring plane, derivation on the contract plane).

## 3. Promotion recommendation (respects SEED's boundary — no spec change here)

1. **Feed the catalog gaps into the approved task-session that MAY change the spec: batch-1 R3.** R3-P1
   (`Operation→Entity` read), R3-P2 (`Operation→ValueObject` return), R3-P3 (Event composite) — already
   wired into `development/reformulate-batch1/`. This is the SEED-sanctioned "later approved task-session"
   for the RELATIONSHIPS edge-law; **it is the only route allowed to mutate the spec.**
2. **Do NOT promote Lane Z (full unification) yet.** Two gates remain: (a) a **2nd, UI-heavy corpus** to
   exercise the 13 untested types (owner: DomainSpec v2 tower — optional T5); (b) the **agent-cost
   experiment** that measures SEED's actual claim (a separate tower). Owner decision.
3. **Interim stance = the two-plane boundary** (build-from-owned): keep the crisp derivation spec as source
   of truth; use ontology tooling only as an authoring-plane lens.

## 4. What SURVIVED buys, precisely (claim ≤ proof)

- Proven: on one real backend feature, ≥90% of nodes map 1:1 to a code pattern and ≥90% of edges to a
  composition rule, with bounded cross-cutting context. The typed graph is a **sound substrate candidate**.
- NOT proven: agent cost/drift savings (proxy gap); viability across the full 25×29 catalog (coverage
  gap — catalog-checked, not feature-exercised); that fusion (Lane Z) beats generation (Lane A).

## 5. Residue → owners
- Single corpus; SURVIVED is necessary, not sufficient → 2nd corpus (DomainSpec v2 tower).
- Proxy: agent-cost unmeasured → agent-run experiment (separate tower).
- Catalog coverage incomplete → **batch-1 R3** (owned, wired).
- Lane Z-vs-A undecided → the SEED tower + the agent-cost experiment.
