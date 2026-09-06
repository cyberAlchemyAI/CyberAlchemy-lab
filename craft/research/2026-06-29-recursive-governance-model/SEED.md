---
node_type: research
subject: recursive governance model (bounded) for domainspec-v2
dispatch_id: 2026-06-29-recursive-governance-model
dispatch_type: research
date: 2026-06-29
discipline: claim <= proof; build-from-owned (a found owner is build-from-owned, never a kill)
---

# SEED — Recursive governance model (bounded) for domainspec-v2

Shared context for all agents. Read first; your `initial_prompt` adds your angle.

## The finding under examination

domainspec-v2's minted authority model has three domain-originated governances —
**layering / validation / drift** — that appear to form a **`what / how / when`** (law / check /
trend) chain. We then noticed the SAME triad **inside each governance** (e.g. validation has its own
norm "specs must be complete" → a check (lint) → a trend over time). So the structure looks
**self-similar across ≥2 scales** = recursive. The owner flagged this as **`CAV2-D30` bounded
recursive self-application** (the inventory states "recursivity" is only an alias for the *bounded*
meaning). The decision to model this is heavy → this research.

## The four decisions to resolve

1. **Real or forced?** Is the law/check/trend self-similarity a *genuine* recursive invariant, or
   analyst-imposed pattern-matching (the levels differ in kind, so "self-similar" is a mnemonic)?
2. **The bound (base case).** D30 demands a bound. Where does the recursion terminate? Candidate
   axes: **decidability-rooted** (an atomic decidable leaf the engine checks in one step) vs
   **viability-rooted** (VSM operational closure — *not* in general decidable). A structure may
   satisfy one and fail the other — this is the load-bearing axis.
3. **Encode as one recursive schema vs flat kinds.** Define the law/check/trend node once and apply
   at every level (recursive schema), or keep three flat governance kinds?
4. **Model A vs B.** A = each governance owns its own norms (distributed; recursion-friendly).
   B = one central "law" node owns all norms; validation/drift are pure act-ors.

## Owned anchors (build-from-owned — cite, don't reinvent)

- `CAV2-D30` bounded recursive self-application · `CAV2-D17` reflection-tower-method (residue → higher
  layer with its own schema/check/recomposition) · `CAV2-D29` axis orthogonality invariant.
- The minted authority model: `projects/domainspec-v2/authority/AUTHORITY-MODEL.md` (the 3 governances).
- `impl/spec/DRIFT-CONVERGENCE.md` (the drift surfaces) · the engine `impl/test-derivation-engine/`
  (decidable `derive`/`lint` leaves).

## External precedent to weigh

Recursion schemes / fixpoints / well-founded recursion / F-algebras + initial algebras (type theory);
**Beer's VSM** (recursive viable systems — each viable system contains viable systems); holonic /
fractal governance.

## Guardrails

claim ≤ proof · build-from-owned (a found owner is a WIN, relabel build-from-owned, never a kill) ·
**the bound is load-bearing** (unbounded = infinite governance regress) · keep the
**decidability-rooted vs viability-rooted** distinction explicit.

## Output contract

Each explorer writes `<this folder>/explorer-<name>-<angle>.md` and returns a short summary. The
synthesizer (Jacobs) writes `findings.md` — a **verdict matrix** over the four decisions (real? ·
bound? · schema-vs-flat? · Model A/B?) with a recommendation + residue. Skeptics attack the
synthesizer's draft on their gate (precedent / non-vacuity / definitional) and write skeptic memos.
