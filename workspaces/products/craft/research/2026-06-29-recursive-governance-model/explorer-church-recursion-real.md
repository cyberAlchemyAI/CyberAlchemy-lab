---
node_type: explorer-memo
dispatch_id: 2026-06-29-recursive-governance-model
explorer: Church, Alonzo
angle: recursion-is-real (formal)
date: 2026-06-29
discipline: claim <= proof; build-from-owned; the bound is load-bearing
anchors: [CAV2-D30, CAV2-D17, CAV2-D29]
---

# Explorer memo — Church: the governance node is a genuine bounded recursive invariant

**Thesis.** The `law / check / trend` triad is **not** analyst-imposed pattern-matching. It is the
**carrier of an initial F-algebra** whose signature functor is fixed by the *meaning* of governance,
and the self-similarity across scales is exactly the **catamorphism** that an initial algebra forces.
The bound the SEED demands is not an extra guardrail bolted on — it is the **base case the
endofunctor's coproduct already contains**. Decidability-rooted is the real base; viability-rooted is
not a base case at all (no least fixpoint). Grounded in `CAV2-D30` and `CAV2-D17`.

## 1. The signature functor (what a governance node *is*, before any recursion)

A governance node answers three irreducible questions about a typed spec node `x`:
the **norm** it must satisfy (law / *what*), the **decision procedure** that adjudicates it
(check / *how*), and the **trend** of that adjudication over the temporal surface (drift / *when*).
This is not three flat kinds (SEED decision 3, flat side); it is one **product** of a norm with a
*recursively-governed* substructure. Define the endofunctor on the category of governable subjects:

```text
F(X) = Norm × Check(X) × Trend(X*)
```

- `Norm` — a constant functor: the *what* leaf, a predicate on the subject (no recursion in itself).
- `Check(X)` — the *how*: an adjudicator that may itself be governed (a check has its own
  norm "the check must be complete/sound", its own meta-check, its own trend). This is the
  recursive position.
- `Trend(X*)` — the *when*: a trend is a function over a (finite, well-founded) **list** `X*` of
  prior adjudications; it governs the *history* of the substructure.

A **governance structure** is then any `X` with a coalgebra/algebra over `F`. The triad is real
because `F` is forced by the *type* of the question, not chosen: drop any factor and you cannot type
"is this norm being met, and is meeting-it improving?" — the SEED's own `validation` example
(norm "specs complete" → lint → trend) is literally `Norm × Check × Trend`, i.e. one application
of `F`. The same triad re-appearing "inside each governance" is `F` applied to the `Check(X)`
position: **self-similarity is functorial self-application, which is the definition of recursion.**

## 2. The fixpoint formulation: μF and the catamorphism

Let `μF` be the **least fixpoint** (initial algebra) of `F`:

```text
μF ≅ F(μF)        in : F(μF) → μF   (the constructor: "package norm+check+trend into a node")
```

`μF` is the type of **all finite, well-founded governance trees**. The governance model is the
unique algebra map (catamorphism) `⟦φ⟧ : μF → A` for any carrier `A` with structure `φ : F(A) → A`:

```text
⟦φ⟧ ∘ in = φ ∘ F(⟦φ⟧)
```

This single equation **is** the "unfolds at each level" property the owner observed: `F(⟦φ⟧)`
recurses into the `Check` sub-node, evaluates *its* law/check/trend, and `φ` recomposes. Reading
`A = {pass, flag, block, defer}` (the AUTHORITY-MODEL gate vocabulary), `⟦φ⟧` is the **evaluator that
rolls a whole governance tree up to one gate verdict** — and it exists and is *unique* precisely
because `μF` is initial. Uniqueness is the formal content of "real, not imposed": an analyst-imposed
overlay would admit many equally-good foldings; an initial algebra admits exactly one. The structure
*chooses its own evaluator*.

**This is exactly `CAV2-D30`.** Map D30's required fields onto `in : F(μF) → μF`:
D30 source `a_n` = the sub-node `X`; target `a_(n+1)` = the wrapped node `in(...)`; altitude `h_n→h_n+1`
= the F-application depth; owner route / gate = `φ`'s carrier `A`; **residue carried forward** =
`Trend(X*)` (the history list); **recomposition path** = the catamorphism's `φ` (folds back to the
parent); **stopping condition** = §3. Every D30 admissibility field is a *component of the functor*,
so a node that type-checks as `μF` **is** a D30-admissible recursive step. The recursivity is not
described onto the model — it is the model's type.

## 3. The forced base case (the bound the math *requires*)

A least fixpoint `μF` exists **iff `F` has a base case**, i.e. iff the recursion bottoms out. `F`'s
recursive position is `Check(X)`. Write `Check` as a **coproduct** — this is forced, not optional:

```text
Check(X) = Atomic + Governed(X)
```

- `Atomic` — a **decidable leaf**: the check is a one-step decision procedure that terminates with a
  verdict and is *not itself governed by a further check*. (`impl/test-derivation-engine`'s
  `derive`/`lint`: a derived obligation either fires-and-passes or not — decidable in one engine step.)
- `Governed(X)` — the check has its own governance node (recurse).

`μF` is **well-defined only because the `Atomic` summand is non-recursive.** The base case is **not a
modelling choice — it is the left injection of the coproduct that the least-fixpoint construction
forces to exist.** Without `Atomic`, `F` has no least fixpoint (only the greatest fixpoint `νF` of
infinite trees), which is the SEED's "infinite governance regress." So:

> **Forced base case:** *every governance branch must terminate in a `decidable atomic check` —
> a leaf the engine adjudicates in one step with no further governing check.* Termination is the
> **well-founded descent** on F-application depth: each recursion strictly decreases the height of the
> remaining `Governed` subtree; structural recursion on `μF` is therefore total (every catamorphism
> on an initial algebra terminates).

**Decidability-rooted, decisively, over viability-rooted (SEED decision 2).** Viability/VSM closure is
in general **undecidable** → it furnishes no `Atomic` summand → `F` would have *no* least fixpoint, only
`νF`. A viability-rooted reading is therefore not a different base case; it is the *absence* of one —
it lands you in the greatest fixpoint (productive but non-terminating: corecursion, the regress D30
forbids). Viability belongs in the *trend* factor (a property observed over `Trend(X*)`), never as the
leaf. The bound is **decidability-rooted**, and the formalism admits no alternative.

## 4. Why D17 makes the recursion *climb* without breaking the bound

`CAV2-D17` (reflection tower) supplies the **inductive step's promotion**, complementary to D30's
node constructor. When residue `R_n` cannot close at layer `L_n`, D17 gives
`R_n -> seed(L_{n+1})`, formally `L1^(n+1) := L1^n + Carrier(μ_n)`. In F-algebra terms this is a
**new algebra over the SAME functor `F` at a higher altitude** — the tower is a sequence of
`F`-algebras `φ_0, φ_1, …` related by carrier-extending promotions `P_n`. Crucially D17's climb is
**driven by residue**, and residue (`Trend(X*)`) is finite per step; the tower grows only when an
atomic leaf *cannot* name the residue, so each climb still bottoms out in §3's decidable leaf at its
own layer. D17 = vertical (cross-layer) recursion; D30 = the node-local recursion; both fold to gate
verdicts via the same catamorphism. **`CAV2-D29` (axis orthogonality)** guarantees the three factors
of `F` stay independent across the climb, so `F` keeps its product shape and the catamorphism stays
well-typed at every floor — the recursion is real *and* stays inside the bound.

## 5. Verdicts on the four decisions (from this angle only)

1. **Real or forced? → REAL.** The triad is the signature functor `F = Norm × Check × Trend`, forced
   by the *type* of the governance question; self-similarity is the unique catamorphism of the initial
   algebra `μF`. Uniqueness (not multiplicity) of the fold is the proof it is structure, not overlay.
2. **The bound? → decidability-rooted, forced.** The base case is the `Atomic` left-injection of
   `Check(X) = Atomic + Governed(X)`; `μF` exists *iff* it does. Viability-rooted gives no `Atomic`,
   hence no least fixpoint — it is `νF` (the regress), not a base case.
3. **Schema vs flat? → one recursive schema.** Define `F` once; apply at every level. Three flat kinds
   cannot express the `Check(X)` recursion the owner observed; the schema can, and recovers the three
   "kinds" as the depth-1 unfolding `F(Norm, Atomic-check, Trend)`.
4. **Model A vs B? → A (distributed).** Each `Governed(X)` node carries its *own* `Norm` (its norm
   lives in the `F`-cell of that node). A central law-node (B) would break the functor's recursive
   position — `Check(X)` could not carry a norm, collapsing `F` and forbidding `μF`. Recursion *is*
   distributed authorship; A is the only model that types.

## 6. Residue (honest limits of this angle)

- I argue `F` is *forced* by the governance question's type; a skeptic on the **non-vacuity** gate
  may demand a witnessed governance branch that *actually* recurses ≥2 levels and *terminates* in a
  real engine leaf (validation's "specs-complete" → lint, then lint's own "lint-sound" meta-check →
  ??). If level-2's check has **no** decidable leaf in the current engine, the `Atomic` summand is
  asserted, not witnessed — the fixpoint is well-typed but possibly *uninhabited* below depth 1.
- The catamorphism's existence assumes the carrier `A` (gate verdicts) is a genuine `F`-algebra; if
  `Trend` is not adjudicable to a single gate value (it may be a *trajectory*, not a verdict), `A`
  needs to be a more structured object and the "unique fold to one gate" claim weakens.
- Initiality is a strong claim; I have shown `F` is a *polynomial* functor (constants + product +
  coproduct + list), which *does* admit an initial algebra in Set — so this residue is small, but the
  **inhabitation** of the `Atomic` leaf at depth ≥ 2 is the load-bearing empirical check I hand to the
  experiment/skeptic lane.
