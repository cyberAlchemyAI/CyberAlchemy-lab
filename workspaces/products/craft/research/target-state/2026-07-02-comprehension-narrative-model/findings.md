---
node_type: research
is_session: false
status: candidate
created: 2026-07-02
authored_by: domainspec-subagents-strategy (synthesis of 3 lenses + 2 skeptics, P8-verified)
dispatch: 2026-07-02-spec-comprehension-model
final_approver: parent
promotion_boundary: local research only — NOT promoted to domainspec-v2 until owner confirms; no engine δ-rules touched.
inputs:
  - ./lens-narrative.md       # Alexander (narrative / OCM)
  - ./lens-example.md         # Polanyi (example / tacit)
  - ./lens-distillation.md    # Wittgenstein (DDD distillation / Evans)
  - ./candidate-model.md      # merged pre-skeptic candidate
  - ./skeptic-feyerabend.md   # cut-further
  - ./skeptic-gigerenzer.md   # completeness / novice-witness
---

# Findings — Spec Comprehension Model

## The question
The owner: *"a bad thing about DomainSpec is it's hard to understand what abstractions a new spec
proposes — a narrative model (like OPTIMIZATION-CHAIN-METHOD) might help; DomainSpec should reach
simplicity of vocabulary WITH completeness (Evans)."* Instinct: **add a narrative layer.**

## The headline (radical candor — this corrects the instinct)
**Adding a narrative layer would make comprehension worse, and every lens + both skeptics agree.**
OCM mandates 7 sentence-forms per idea (`OPTIMIZATION-CHAIN-METHOD.md` OCM-009); that is *7 dialects for
one concept* — the **inverse** of Evans' ubiquitous language (one sharp shared word). The owner's *goal*
(simplicity + completeness) is real and reachable, but by **subtraction + surfacing what already exists**,
not addition.

## What is already true on disk (all P8-verified this session)
| Fact | Evidence |
|---|---|
| All **14 backend meta-types have a `.schema.yml`** carrying a machine `distinguisher.vs` + `distinguisher.rule` | `impl/spec/meta-types/**/**.schema.yml` — 14/14 confirmed |
| A meta-type's `.md` card is a **near-total projection** of its schema (criterion/required_structure/edge_participation/distinguisher/fixtures all map) | `entity.md` headers ↔ `entity.schema.yml` keys |
| A **true crossed pair** already exists (same concept, two verdicts) | `__fixtures__/mt/entity-bad.md` rejects `Money` *as Entity*; `value-object-ok.md` accepts the same `Money` *as VO* |
| **No UI `.schema.yml` exists** (11 UI types unformalized) | `meta-types/` has only structural/behavioral/connective/lifecycle |
| The 5 "shadow" UI types are **first-class edge endpoints**, not Rule/VO duplicates | `RELATIONSHIPS.md:39,51` — Guard sources `protects`→Page and `mirrors`→Rule; Rule sources `enforces`→Operation |
| `distinguisher.vs` is **single-valued** — one sibling per type | e.g. `operation.schema.yml` `vs: Query`, though Operation's real confusion set is Query+Workflow+Event |

## The verdict: a 4-region partition (the tension did not cancel — it carved the type space)
The two skeptics reached **opposite terminal verdicts** (Feyerabend: *cut further, author nothing*;
Gigerenzer: *the cut loses completeness*) and **both are right, in different regions**:

### Region 1 — the 9 "crossed" backend types → **author ZERO** (Feyerabend)
Structural (Entity/VO) + all 7 Behavioral types have a negative that flips to a *named sibling with a
matching positive fixture*. Here the comprehension asset already exists:
- **Relocate** the existing crossed fixture pair beside the schema (out of `__fixtures__/` plumbing into
  the author's entry point).
- **Caption** it with the schema's existing `distinguisher.rule` (one line — no authoring).
- **Delete** the redundant `Common Confusion` rows and thin prose definitions (ceremony over the pair).
- Even the two "authored human forms" from the candidate → cut to **zero** (`entity.md` proves the card
  projects from the schema).

### Region 2 — the 5 "uncrossed" backend types → **needs MORE scaffolding** (Gigerenzer)
`Enum, Interface, Mapping` have **malformed-only** negatives (missing a column/attribute); `Event, State
Machine` have **intent-flips whose flip-target has no matching positive** (event-bad renames the concept).
None is a true minimal pair. **Load-bearing risk: Event + State Machine are 2 of the candidate's own
CORE-6** — so the "example-first" entry point is *absent exactly where "internalize first" points.* Fix
(build-from-owned): upgrade each `-bad.md` into a genuine class-flipping pair (same concept, two models,
landing on the sibling's `-ok`), OR explicitly mark these as *attribute-distinguished, not
example-distinguished* (read the axis from the schema). This is the **one place to add, not cut.**
> Note: this **refutes the candidate's own R2 guess** (it predicted behavioral/lifecycle would be weakest;
> behavioral is 7/7 strongest — the real cliff is connective 0/3 + lifecycle 0/1 + Enum).

### Region 3 — the 11 UI types → **cannot be dictionaried away** (Gigerenzer)
No schema exists for any UI type, and the 5 "shadows" carry **their own edges** (`protects`, `mirrors`,
`reflects`) absent from their backend counterparts. Collapsing them to a one-line dictionary (candidate M1)
**loses edge completeness.** They must stay first-class in the graph; formalizing them is a separate,
deferred piece (matches the existing UI-11-deferred boundary).

### Region 4 — narrative → **reserved for the target-state doc only** (survived both skeptics)
The narrative/OCM instinct lands in exactly one place: a **target-state** doc (the owner's
`research/target-state/` line, SEED Lane-A) — a buildable "done looks like…" paragraph + a **checkable
oracle-by-example** (DONE vs a discriminating NOT-DONE near-miss). It is *document-level*, NOT a
per-meta-type authoring layer.

## Where the skeptics converged (the honest core)
Both agreed: **for a type that has a genuine crossed pair, `pair + one-line axis` IS the whole lesson** —
the thin definition and any projected/authored forms are redundant. They diverged only on the *5 failing
types*, and that divergence is the real finding: **the model's quality is not uniform across the 25 —
it is excellent for 9, thin for 5, and absent for 11.**

## Recommendation to the owner (build-from-owned, minimal, honest)
1. **Do NOT add a narrative/multi-form layer to per-spec authoring.** (unanimous)
2. **Distill the author-facing learning order** to ~6 core types met **example-first via the crossed
   fixtures you already have** — a learning order, *not a new artifact* (`lens-distillation.md:188`).
   Keep shadows **first-class in the graph** (dictionary the *learning*, not the edges).
3. **Relocate** the 9 crossed fixture pairs beside their schemas; **delete** the redundant confusion rows.
   (author nothing)
4. **Upgrade** the 5 weak `-bad.md` fixtures into genuine discriminating pairs — the single add.
5. **Reserve narrative for a target-state doc** with an oracle-by-example.
6. **Before adopting**, run the novice-witness test Gigerenzer named: have someone author a real spec that
   uses a SUPPORTING/GENERIC type and observe where they stall. (claim ≤ proof — comprehension gain is a
   *hypothesis*, not a measured result; DDD/NDD primary sources 403'd, quotes are secondary.)

## Claim ≤ proof ledger
- **Verified on disk:** the 6-row fact table above; the 5 weak-fixture classification (inspected all 5);
  the Guard/Rule edge distinctness.
- **Judgment call (labelled):** the exact "9 of 14" cut depends on where "genuine pair" is thresholded;
  the structural finding (quality degrades outside Structural+Behavioral; 2 CORE-6 are weak) is robust.
- **Unproven hypothesis:** that distillation + example-first *empirically* improves author comprehension.
  Needs the novice-witness test. Not claimed as fact.
