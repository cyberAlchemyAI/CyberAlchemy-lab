# K20 — fulfills-request

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **checked owned requirement completion**.

**Meaning in plain language.** A view fulfills a particular request when every mandatory owned request constraint is met at resolution time. Later source changes require rechecking.

**Question answered.** Which request is this immutable output intended to fulfill?

**Formal definition.**

```text
Meaning_K20(W,e,f) := ∃ w ∈ W.RequestFulfillment. Base_K20(W,e,f,w) ∧ (w.view = s ∧ w.request = t ∧ w.view.request = t ∧ w.view.contextRevision = w.request.contextRevision ∧ w.role = code(q.fulfillment_role) ∧ w.criteria = deriveCriteria(W,t,f) ∧ RequestSatisfied(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a RequestFulfillment record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `view` | Context View exact revision |
| `request` | Context Request exact revision |
| `role` | owned request/view fulfillment role |
| `criteria` | complete independently derived selector, exclusion, freshness, budget and output criterion set |
| `resolutionEpoch` | view generation/source-resolution epoch in one domain |
| `evidence` | exact admissible criterion support |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`deriveCriteria`: The deterministic owned derivation from the exact request body, selector catalogs, exclusions, freshness requirement, budget and output constraints in the frame. The complete output is bound by revision/digest; callers cannot provide a smaller substitute.

`RequestSatisfied`: The view/request/context revision joins are exact; source epoch and generation epoch use the same domain; deriveCriteria produces the complete mandatory set; D05 supplies yes for every mandatory criterion; no unresolved potential or conflict is ignored. Included/excluded material, freshness at resolution, budget and output format satisfy the request. An empty set is allowed only when the owned request derivation itself yields it.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `fulfillment_role` | `w.role` | owned complete request/view fulfillment constructor, distinct from generic conformance |

**Operational behavior.** Record demonstrated request fulfillment in f; do not assert that included sources remain current afterward or mutate Context.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** View V satisfies all of Request R's constraints at resolution epoch 5; a source changes at epoch 6.

**Insufficient case.** A view omitting one requested selector cannot qualify by supplying a reduced criterion list.

**Useful correction.** Derive the full criterion set from the owned request, restore omitted selectors, and supply exact support at the resolution epoch.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| currentness | A current source observation at now still selects this source revision; historical as-of agreement is insufficient. | `relation.fulfills-request:forbidden:0` |
| source-authority | A separately governed authority boundary recognizes the source's authority, beyond context framing or view consumption. | `relation.fulfills-request:forbidden:1` |
| context-mutation | A verified qualified state transition changes the durable Context revision, beyond a request/view record. | `relation.fulfills-request:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Owned selector derivation, exclusions, source freshness, budgets and output constraints require a full E03 bridge; a caller-supplied reduced set is insufficient.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/fulfills-request.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K20-fulfills-request.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| context-view | context-request | context-view to context-request: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
