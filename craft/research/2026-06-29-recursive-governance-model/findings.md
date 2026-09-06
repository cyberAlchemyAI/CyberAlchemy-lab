---
node_type: synthesis-findings
subject: recursive governance model (bounded) for domainspec-v2 — verdict matrix
dispatch_id: 2026-06-29-recursive-governance-model
synthesizer: Jacobs, Bart
date: 2026-06-30
status: REVISED (post-skeptic; zig-zag pass loop_cap 1 — precedent / non-vacuity / definitional gates incorporated)
discipline: claim <= proof; build-from-owned; the bound is load-bearing; one verdict per decision
anchors: [CAV2-D30, CAV2-D17, CAV2-D29]
external_owners: [Hagino 1987, Jacobs 2016, Turi-Rutten 1998, Meijer-Fokkinga-Paterson 1991, Beer 1972/1979]
skeptics_incorporated: [Russell (precedent), Gödel (non-vacuity), Rittel (definitional)]
---

# Findings — Recursive Governance Model (Bounded)

## 1. One-line answer (close to dispatch goal)

The `law/check` spine is a **build-from-owned** bounded recursion — the standard initial-algebra/
final-coalgebra duality (Hagino 1987; Jacobs 2016) **applied** to the `law/check/trend` governance
triad — with recursion REAL and engine-witnessed on the μF spine **at depth 1**, `trend`/drift typed as
its νF coalgebraic dual (bound = guardedness/productivity, **a design commitment, not yet a present-tense
fact**), and Model A demoted to a corollary of D30's authority-boundary clause.

## 2. Build-from-owned vs net-new (precedent gate — Russell)

The architecture is **build-from-owned**, not a discovery. The μF/νF instrument and every bound are
owned by prior art and CAV2; only the *application* to the governance triad and two engineering findings
are net-new — and each at a strictly bounded altitude.

**OWNED (cite, do not claim as a finding):**

| Material | Owner |
|----------|-------|
| μF/νF initial-algebra / final-coalgebra duality | Hagino 1987; Jacobs 2016; Turi-Rutten 1998 |
| Catamorphism = unique fold from μF (anamorphism = unfold from νF) | Meijer-Fokkinga-Paterson 1991; Hagino 1987 |
| Guardedness/productivity as the νF bound | Turi-Rutten 1998; Jacobs 2016 Ch.5 |
| Coinductive `Stream` as νF | Jacobs 2016 Ch.5 |
| VSM recursive viability; viability is not statically checkable | Beer 1972/1979 |
| Bounded recursive self-application = process-on-own-artifact discipline | CAV2-D30 (process discipline only — NOT the schema) |
| Reflection-tower climb (residue at L_n seeds L_{n+1}) | CAV2-D17 |
| Axis orthogonality (product shape of F across floors) | CAV2-D29 |

**NET-NEW (exactly three, at the altitude Russell allowed):**

| Claim | Altitude | Status |
|-------|----------|--------|
| (a) Applying μF/νF to the `law/check/trend` triad — `F(X)=Norm × (Atomic+Governed(X)) × Stream<CheckResult>` | **Application claim** (not theory) | Held — the standard duality, applied, predicts the schema split |
| (b) Decidable-leaf base case engine-witnessed via `classifyFormal`/`δ` | **Witnessed at depth 1 only** | Depth-1 inhabited; depth-2 **asserted** — residue R-leaf-inhabitation open (Gödel) |
| (c) `trend` has no typed representation in the engine today — a typed engineering residue | **Codebase finding** (not theory) | Held — narrows Yanofsky from "recursion forced" to "νF factor untyped today" |

## 3. Verdict matrix (one verdict per decision; no split differences)

| # | Decision | Verdict | Rationale (cited; owned vs net-new marked) | Use-mode |
|---|----------|---------|-------------------|----------|
| 1 | Recursion REAL or FORCED | **REAL** on the law/check spine — **witnessed at depth 1** (depth-2 open) | The recursive position is `Check(X)`, the signature functor `F`, forced by the type of the governance question — `F(X)=Norm×(Atomic+Governed(X))×Stream<CheckResult>`; the SEED's `validation` example is one application of `F` (Church §1). Witnessed in the engine **at depth 1**: `δ` total over finite `G`, `Check` bottoms out in `classifyFormal` — a one-step decidable verdict, `sub=[]` (Gödel §a: depth-1 inhabited ✓). The functor `F` is net-new **as a governance schema** (Russell §2a application claim); the recursion math is owned. Yanofsky over-generalizes from drift to the whole triad. | Encode the recursion on `Norm×Check`; functorial self-application of `F` at `Check(X)`, not a doc mnemonic. |
| 2 | The BOUND + base case | **DECIDABILITY-ROOTED**. Base case: a node is a leaf iff its `law` resolves to ≥1 `δ_i` decidable atomic checks — a `classifyFormal`-style call returning a finite verdict (incl. terminal `needs-formal`) in one engine step, with `sub=[]`. | `μF` exists *iff* `Check(X)=Atomic+Governed(X)` has the non-recursive `Atomic` summand; viability gives no `Atomic` (Church §3). The coproduct base-case form is **owned** type theory (Russell §1b); pinning the `Atomic` summand to a *mechanically decidable engine predicate* is the **net-new** (b) claim — and is **witnessed at depth 1 only**; depth-2 `δ_i` is asserted, not exhibited in the engine (Gödel §a; residue R-leaf-inhabitation). VSM autonomy-floor demoted to a declared `atomic` tag is a **design choice** justified by the VSM/decidability tension, not a theoretical result (Russell §1c). | The engine's `atomic` tag / `δ_i` leaf is the inspectable base case; structural induction on nesting depth guarantees descent — sound at depth 1. |
| 3 | ONE recursive schema vs flat kinds | **ONE recursive schema** | Three flat kinds cannot express the `Check(X)` recursion; the schema recovers the three "kinds" as the depth-1 unfolding `F(Norm, Atomic-check, Trend)` (Church §5.3). The owned, engine-shaped schema `GovernanceNode{norm,check,trend}`; δ already enacts the spine (Wisnesky §4). | Define `GovernanceNode` once; `check = Atomic+Governed` is the μF spine; `trend` is the νF factor (§4). |
| 4 | Model A (distributed) vs B (central law) | **A (distributed)** — **as a corollary of D30**, not a top-level discovery | The normative verdict (distributed ownership) is **already entailed** by D30's authority-boundary clause: a single owner route must not be collapsed across governed nodes without a recorded coupling (Rittel — COLLAPSES to D30 proviso). The functor argument (B breaks `Check(X)`'s recursive position; B needs a cross-governance read that breaks δ's totality) is a useful **restatement**, not the source of the verdict. | Each `Governed(X)` node carries its own `Norm`; no central authority node — because D30 forbids the collapse, restated functorially. |

## 4. The μF / νF call — build-from-owned application; νF bound demoted (Russell + Gödel)

**The standard algebra/coalgebra duality (Hagino 1987; Jacobs 2016) applies here; applying it resolves
the four decisions as follows.** This is the *correct application of owned math*, not a discovery
(Russell §3.1).

All four explorers independently located the same fault at `trend`/drift:
- **Church** (residue): if `Trend` is "a *trajectory*, not a verdict," the carrier `A` is not a plain
  `F`-algebra and the "unique fold to one gate" weakens (Church §6).
- **Yanofsky** (sharpest counterexample): drift's inner "check" is "a scalar, not a pass/fail verdict";
  "divergence accumulates continuously" — no decidable leaf.
- **Wisnesky** (engine level): `trend` "has no typed representation in `ir/types.ts`" / `Obligation`
  (Wisnesky §6).
- **Turi-Rutten 1998** supply the dual's bound: `νF`/coinduction is bounded by **guardedness/
  productivity** (cited as the external owner; the explorer internally named "Ashby" §1–2).

**Verdict:** Yanofsky is **partly right and partly wrong**. Right: `trend` is *not* a `μF` leaf — it has
no decidable atomic check, so forcing it into a flat inductive spine is the error he names. Wrong: this
is not broken recursion — `trend` belongs in the **standard coalgebraic dual** (νF, Jacobs 2016 §1),
which Yanofsky does not consider. (The coalgebraic dual is *owned*; what is net-new is recognizing that
`trend` belongs there — Russell §3.2.)

Split the schema:
- **`check` = `μF`** (initial algebra, inductive): finite well-founded governance trees, bounded by the
  decidable `Atomic` leaf (Decision 2). Folds to a gate verdict by the unique catamorphism
  (Meijer-Fokkinga-Paterson 1991; Hagino 1987; engine δ as the algebra action, Wisnesky §4).
  **Witnessed at depth 1.**
- **`trend` = `νF`** (final coalgebra, coinductive): a productive observation stream over the history,
  bounded by **guardedness/productivity (Turi-Rutten 1998)** — **a design commitment, NOT a present-tense
  fact**. Per Gödel §b, the bound is currently **vacuous in the engine**: there is no `Stream<CheckResult>`
  type, no `unfold`/`corec` combinator, hence no term on which to run the guardedness check. Retract
  "statically checkable today"; the bound is a design target pending the type + the productivity spec.

This keeps Decision 1 = REAL **without overclaiming**: recursion is real and decidably bounded on the
spine at depth 1; the μF/νF split is the correct *architecture*; the νF present-tense bound is retracted.
The single schema survives; `trend` is typed as a coinductive `Stream`/`CheckLog`, **not** as a
`sub:GovernanceNode` recursion.

## 5. Recommended model

`GovernanceNode` (one recursive schema, Model A *as a D30 corollary*, defined once, applied at every level):

```
GovernanceNode {
  id     : GovernanceId
  norm   : Norm                       -- the *what*; constant, lives in THIS node (Model A = D30 corollary)
  check  : Atomic + Governed          -- the *how*; μF recursive position (owned: Hagino/Jacobs)
                                      --   Atomic   = decidable δ_i leaf (classifyFormal-style) BASE CASE
                                      --              [witnessed at depth 1; depth-2 asserted — R-leaf-inhabitation]
                                      --   Governed = sub : GovernanceNode  (recursive step)
  trend  : Stream<CheckResult>        -- the *when*; νF coinductive factor, NOT a sub-recursion
                                      --   bound = guardedness/productivity (Turi-Rutten 1998)
                                      --           = DESIGN COMMITMENT, not yet typed in the engine [R-trend-type]
}
```

- **Base case (μF):** `check = Atomic` (`sub=[]`); `classifyFormal` returns a finite verdict in one step
  (Wisnesky §2; Church §3). Witnessed at depth 1 (Gödel §a). Owned base-case form (Russell §1b); net-new
  engine-witnessing claim (Russell §2b, depth-1 only).
- **Recursive step (μF):** `check = Governed(sub)`; descent on nesting depth / strictly-smaller sub-graph
  of `G` (Wisnesky §4). Sound at depth 1; depth-2 leaf unwitnessed.
- **Coinductive factor (νF):** `trend` read as a guarded productive stream of `check` results; never in
  the termination argument. Its well-formedness *would be* the productivity check — but **no such check
  is checkable today** (no `Stream` type, no `unfold`): a design commitment, not a witnessed bound
  (Gödel §b).
- **Climb (D17):** residue no atomic leaf can name promotes to a higher layer as a new algebra over the
  same `F` (Church §4; D17); `CAV2-D29` keeps the three factors orthogonal so `F` keeps its product shape.
  (Distinct from the νF factor, which runs *parallel* to the μF spine, not above it — Rittel: not a D17 re-skin.)

## 6. Residue (with owner)

- **R-leaf-inhabitation (μF, depth-2; owner: domainspec-v2 validation/drift governance + engine /
  experiment lane).** The `Atomic` leaf at depth ≥ 2 is asserted, not witnessed. Depth-1 is a genuine
  witness (`classifyFormal`, finite verdict, `sub=[]` — Gödel §a ✓). A depth-2 `δ_i` (e.g. a meta-lint
  reading the lint rule file → `{structurally-valid|malformed}`) is **constructible in principle but not
  named in the engine**. **Survivable, not closed** (Gödel): the architecture is sound; the claim is
  scoped to depth 1 until a depth-2 `δ_i` is exhibited or committed. Not fatal.
- **R-trend-type (νF; load-bearing; owner: engine / Wisnesky lane → the `Stream<CheckResult>` +
  guardedness work).** `trend` has **no typed representation** in `ir/types.ts` / `Obligation` (Wisnesky
  §6). The νF bound is **vacuous today** — no `Stream<CheckResult>`/`CheckLog` type, no `unfold`/`corec`,
  no productivity spec (Gödel §b: FATAL to the *phrasing* "statically checkable today", not to the
  architecture). Closes only when (1) `Stream<CheckResult>` is typed in `ir/types.ts`, and (2) a
  guardedness/productivity check is specified ("each engine step produces one `CheckResult` before the
  next call"). This is Yanofsky's surviving objection, narrowed to its true scope.
- **R-needs-formal (owner: engine lane).** `needs-formal` is today the only undecidable-ish leaf; bounded
  (counts as 1, terminal). A future lint reducing it to a smaller decidable class is not yet owned
  (Wisnesky §6).
- **R-atomic-tag-meta (owner: definitional lane).** Likely resolved by well-foundedness of the depth
  measure (Ashby R1); needs explicit confirmation. Note: the `atomic` tag's normative status is a
  *design choice* (Russell §1c), not a theoretical result.
- **R-VSM-audit-path (owner: model author, optional).** Beer's S3–S3* audit channel maps to a drift
  audit path distinct from the law/check chain — candidate structure for the νF factor (Ashby R3).
