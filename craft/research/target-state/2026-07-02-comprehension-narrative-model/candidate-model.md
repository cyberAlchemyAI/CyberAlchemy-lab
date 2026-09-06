---
node_type: research
is_session: false
status: candidate
created: 2026-07-02
authored_by: domainspec-subagents-strategy (merge of 3 explorer lenses)
dispatch: 2026-07-02-spec-comprehension-model
promotion_boundary: local research only — not promoted to domainspec-v2 until skeptics + owner confirm.
inputs:
  - ./lens-narrative.md      # Alexander — narrative / OCM
  - ./lens-example.md        # Polanyi — example / tacit knowledge
  - ./lens-distillation.md   # Wittgenstein — DDD distillation / Evans
---

# Candidate Model — Spec Comprehension (merged, pre-skeptic)

**The owner's framing:** "hard to understand what abstractions/system a new spec proposes" →
instinct: *add a narrative layer* (like OPTIMIZATION-CHAIN-METHOD's multi-form sentences).

**What three independent lenses converged on instead** (this is a radical-candor correction of the
instinct, not a rubber-stamp): the comprehension win is **distillation + surfacing what already
exists**, NOT adding a narrative/multi-form layer. Adding forms *raises* the vocabulary an author must
hold; the goal ("simplicity of vocabulary with completeness" — Evans) is bought by *reducing* it.

---

## The convergence (where all three agree)

1. **Don't add a narrative layer to per-spec authoring.** (Alexander conceded the 7-form mandate is
   ceremony; Wittgenstein showed the narrative layer is structurally the OCM move = **7 dialects for one
   idea = the inverse of ubiquitous language**.) The owner's instinct, followed literally, makes
   comprehension *worse*.
2. **The comprehension asset largely already exists on disk** — it's mis-filed as validator plumbing,
   not surfaced as an author's entry point:
   - The **crossed discriminating pair** (VERIFIED): `impl/spec/__fixtures__/mt/entity-bad.md` rejects
     `Money` *as Entity* and `value-object-ok.md` accepts the same `Money` *as VO* — differing by the one
     axis (identity vs equality). One glance teaches the classification.
   - The **machine distinguisher** already lives in each `<type>.schema.yml` (`distinguisher:` /
     `criterion:`), so a "machine view" can be **projected, not authored**.
3. **Completeness is not lost by distilling** — it lives in the *type system* (engine/validator still
   ranges over all 25). Comprehensibility lives in *learning order*. These are separable (Wittgenstein).

---

## The merged candidate (4 moves)

### M1 — Distilled learning order (from Wittgenstein)
Tier the 25 by how the *author* meets them, not by category:
- **CORE (~6, internalize):** Entity, Value Object, Operation, Rule, State Machine (+ Event).
- **SUPPORTING (~6, learn on demand as "an X is a Y that…"):** Enum, Query, Calculation, Workflow,
  Policy, Interface, Form.
- **GENERIC (~13, recognize + template, never "learn"):** Saga (a scaling modifier), Mapping, and the 11
  UI types — of which **5 are literally declared backend shadows** in TAXONOMY's own "Backend Counterpart"
  column (VERIFIED: View Model→Value Object, Guard→Rule, Binding→Interface, Adapter→Mapping, State
  Indicator→State Machine/Enum). Shadows become a one-line dictionary, not vocabulary to acquire.
- The CORE/GENERIC split is a **per-domain author-declarable lens**, not hard-coded (Evans/Vernon: the
  same subdomain is core or generic depending on what the org does).

### M2 — Example-first comprehension unit (from Polanyi)
Per CORE meta-type, the author's entry point is (read in this order):
1. a **worked positive** (the concept done right),
2. a **discriminating negative** = nearest-neighbour minimal pair (differs by the ONE feature that flips
   the class),
3. the **named contrast axis** (e.g. *identity vs equality*),
4. then a **thin definition**.
Surface the **existing crossed fixtures** as this entry point — don't author new prose. The fixture CI
already runs on the same pair, so the comprehension asset **fails when it rots** (living documentation).

### M3 — Projected, not authored, machine forms (from Alexander)
The `.schema.yml` `distinguisher`/`criterion` is the single source. Any "machine view" or table is
*generated* from it. **At most two authored human forms**, opt-in, and only for **discriminable** types
(a type with no clean minimal pair doesn't get forced into one).

### M4 — Narrative survives ONLY for target-state (from all three; strongest in Alexander/Polanyi)
The narrative / optimization-chain instinct is *right* in exactly one place: the **target-state doc**
(SEED Lane-A) — a buildable "done looks like…" paragraph paired with a **checkable oracle** (Polanyi's
*oracle-by-example*: DONE vs a discriminating NOT-DONE near-miss). It is a *document-level* aid, NOT a
per-meta-type authoring layer. This is where the owner's `research/target-state/` line actually lands.

---

## What this costs / open residues (for the skeptics)
- **R1 (completeness / novice cliff):** does tiering to ~6 CORE help a novice, or does hiding 19 types
  create a cliff the first time they hit a SUPPORTING/GENERIC one? Who declares the per-domain lens, and
  is that itself a new authoring burden?
- **R2 (minimal-pair coverage):** the crossed pair is clean for **structural** types (Entity/VO). Polanyi
  flagged that **behavioral/lifecycle** types (Workflow, Saga, State Machine) may lack a clean minimal
  pair — M2 may not generalize.
- **R3 (is any of this still ceremony?):** M2 asks for positive + negative + axis + definition per CORE
  type. Is that itself ceremony we should cut further (e.g. just the crossed pair + a one-line axis)?
- **R4 (claim ≤ proof):** that distillation *empirically* improves author comprehension is a
  well-grounded hypothesis, **not a measured result**. DDD source PDF 403'd; NDD primary URLs are dead —
  quotes are search-surfaced/secondary (Fowler, herbertograca 2016, Wikipedia), not verbatim primary.

---

## The one-line answer to the owner
> DomainSpec is hard to read not because it lacks a narrative layer, but because it carries **too much
> vocabulary** and **hides the examples that already discriminate the types**. Fix it by *distilling* the
> author-facing surface to ~6 core types met **example-first through the crossed fixtures you already
> have**, projecting machine views from the schema, and reserving narrative for the **target-state** doc —
> not for every spec.
