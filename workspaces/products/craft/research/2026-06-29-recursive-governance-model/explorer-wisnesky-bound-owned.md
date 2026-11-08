---
node_type: research-memo
subject: bound-from-owned angle — decidable leaf base case for recursive governance model
dispatch_id: 2026-06-29-recursive-governance-model
author: Wisnesky, Ryan (explorer)
angle: bound-from-owned (computational/engine)
date: 2026-06-30
discipline: claim <= proof; build-from-owned
---

# Explorer Memo — Bound-from-Owned: Decidable Leaf Base Case

## 1. The Owned Anchor: What the Engine Actually Does

The `test-derivation-engine` (`implementation/domainspec/tools/test-derivation-engine/src/rules/index.ts`) is a
pure, total function `δ: ConceptGraph → Obligation[]`. Each δ sub-function (`deriveValidTransitions`,
`deriveInvariants`, `classifyFormal`, etc.) reads exactly one `NodeType` from the typed graph `G` and emits a
finite, deterministically-counted set of `Obligation` records, each identified by
`obligation_key = sha1(source_anchor | rule_type | canonical_params)`.

The `classifyFormal` function is the sharpest example of a **decidable leaf**: given a `Formal` string, it
returns one of `{EXISTENCE, PRESENCE, RANGE, COUNT_CAP, UNCLASSIFIED}` — a finite yes/no verdict per
syntactic pattern, no further decomposition, no recursion, no network, no clock. Output is byte-stable.
`UNCLASSIFIED` is not "unknown" — it is the bounded escape hatch: it yields exactly one `needs-formal`
obligation (counts as 1, not 0, not ∞). The engine never defers the decision.

## 2. What a Leaf IS (Precise Definition)

A **decidable leaf** in this model is:

> A `δ_i : NodeType → Obligation[]` call that (a) reads exactly one `NodeType` in `G`, (b) returns a
> statically-bounded finite set (cardinality provable from the node's fields alone, without inspecting
> any other node or recursing into governance), and (c) has no `needs-formal` escape that spawns
> further governance — `needs-formal` is a terminal label, not a recursive call.

Concretely: `Transition`, `Invariant`, `Rule`, `Calculation`, `Postcondition`, `Response`, `Event`,
`Consumer`, `WorkflowStep`, `Query`, `Mapping`, `ErrorState`, `DomainField`, `Enum`, `PolicyDecision`
are all leaf `NodeType`s in this sense. Each maps to one δ sub-function; that sub-function terminates
on any finite graph.

## 3. CAV2-D30 Bound: Where Recursion Terminates

CAV2-D30 demands a bound. The bound is **structural**: the concept graph `G` is finite (it is parsed from
a finite set of Markdown feature docs). Each governance level (layering / validation / drift) ultimately
resolves to a set of `Node`s in `G`; the recursive "a governance has its own law/check/trend" bottoms
out when the sub-governance's **law** is itself expressible as one or more `NodeType` leaves whose `δ_i`
produces obligations without spawning a new governance sub-problem. The recursion terminates when:

1. The sub-governance's norm ("spec must be complete") can be expressed as a `Rule` or `Invariant` node
   in `G` — i.e., as a `formal` string that `classifyFormal` can classify (or `needs-formal`-label) in
   one step.
2. There is no obligation type in `RuleType` that requires reading another governance level to resolve —
   every `RuleType` is a terminal label: `valid-transition`, `invariant`, `rule-validation`, …,
   `needs-formal`.

This is the **decidability-rooted** base case (SEED decision axis 2). The engine proves termination by
construction: `δ` is total over any finite `G`, and `G` is finite because the Markdown doc set is finite.
The **viability-rooted** axis (Beer's VSM operational closure) does not guarantee decidability — VSM
recursion only promises that each level is *viable*, not that membership is checkable in finite steps.
The engine does not inherit that guarantee; it provides a strictly stronger one.

## 4. Proposed Encoding: One Recursive Schema, Applied at Every Level

Rather than three flat governance kinds (layering/validation/drift), encode **one recursive governance
node** schema:

```
GovernanceNode {
  id:     GovernanceId          -- uniquely names this governance at this level
  law:    Obligation[]          -- derived by δ from NodeType leaves (the base case)
  check:  lint(law) -> Pass|Fail  -- a lint function: law obligations -> boolean verdict
  trend:  sequence(check) -> Δ  -- a time-indexed log of check results
  sub:    GovernanceNode[]      -- zero or more child governances (recursive step)
}
```

The **base case** fires when `sub = []`: the node has no children; its `law` is fully resolved by δ over
leaf nodes in `G`; `check` calls `classifyFormal`-style lint; `trend` is the time-indexed accumulation of
`check` results. No further recursion is triggered.

The **recursive step** fires when `sub ≠ []`: each child is itself a `GovernanceNode` that must reach its
own base case before the parent's `check` can aggregate. Termination is guaranteed because (a) the child
sub-graph of `G` is strictly smaller than the parent's (structural induction on `G`), and (b) every child
eventually reaches a `GovernanceNode` whose `law` is a set of `δ`-emitted leaf obligations — a finite set.

This is isomorphic to a **well-founded recursion** on the partial order of `G`'s node subsets, which is
the standard F-algebra / initial algebra pattern from type theory. The engine's existing δ functions are
the F-algebra's "action" — they are already written in this shape; the schema just makes the recursion
explicit and single.

## 5. Model A vs B Verdict (from the owned anchor)

The engine's structure already enacts **Model A** (each governance owns its own norms): each δ sub-function
is independent and does not call into another governance's δ. There is no central "law" dispatcher. Model B
(one central law node) would require a shared `NodeType` that aggregates all governance norms — the engine
has no such type, and adding one would break the pure-total-function property (it would need to read across
governance levels, losing locality). **Model A is build-from-owned; Model B is net-new and breaks the
existing decidability guarantee.**

## 6. Residue / Open Items

- The `needs-formal` escape is the only undecidable leaf today. A future lint pass that reduces
  `needs-formal` to a smaller decidable class is possible but not yet owned.
- The `trend` dimension (time-indexed check log) is not yet represented in the engine's `Obligation` type
  — drift surfaces in `DRIFT-CONVERGENCE.md` reference it conceptually but it has no typed representation
  in `ir/types.ts`. Adding a `CheckLog` type to `G` would close this gap without breaking δ's totality.
- The schema sketch above is a **proposal** — it should be validated against `AUTHORITY-MODEL.md` before
  any code change.
