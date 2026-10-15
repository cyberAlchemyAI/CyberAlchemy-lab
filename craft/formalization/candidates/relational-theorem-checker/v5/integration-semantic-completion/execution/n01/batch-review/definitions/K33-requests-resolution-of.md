# K33 — requests-resolution-of

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded request**.

**Meaning in plain language.** A context request asks for resolution of a particular context revision and constraints. The request can exist before any view is created.

**Question answered.** Which exact Context version does this Context Request ask to resolve?

**Formal definition.**

```text
Meaning_K33(W,e,f) := ∃ w ∈ W.ContextResolutionRequest. Base_K33(W,e,f,w) ∧ (w.request = s ∧ w.context = t ∧ t = resolve(q.context_version_ref) ∧ w.request.contextRevision = t ∧ RequestWellFormed(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ContextResolutionRequest record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `request` | Context Request exact revision |
| `context` | Context exact revision |
| `consumers` | exact intended consumers |
| `selectors` | owned request selectors |
| `constraints` | exclusions, freshness, budget and output constraints |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`RequestWellFormed`: The exact context request resolves its consumers, context reference/revision, selectors, exclusions and bounded freshness/budget/output constraints under the owned request schema/profile. Resolution has not necessarily been executed.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `context_version_ref` | `w.context` | exact requested Context revision, consistent with the source context reference |

**Operational behavior.** Record the resolution request without creating a resolved view or mutating Context.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Request R names Context C@1 but no resolver has run and no view exists.

**Insufficient case.** A request for C@2 cannot resolve or mutate C@1 by label matching.

**Useful correction.** Bind the request to the intended exact context revision and its complete constraints; produce and assess a view separately.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| resolution | A completed owned resolution establishes all relevant target criteria, beyond inquiry intent or a context request. | `relation.requests-resolution-of:forbidden:0` |
| context-mutation | A verified qualified state transition changes the durable Context revision, beyond a request/view record. | `relation.requests-resolution-of:forbidden:1` |
| source-authority | A separately governed authority boundary recognizes the source's authority, beyond context framing or view consumption. | `relation.requests-resolution-of:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** The source has context_ref and context_version_ref fields; their exact revision join and all request constraints need refinement.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/requests-resolution-of.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K33-requests-resolution-of.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| context-request | context | context-request to context: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
