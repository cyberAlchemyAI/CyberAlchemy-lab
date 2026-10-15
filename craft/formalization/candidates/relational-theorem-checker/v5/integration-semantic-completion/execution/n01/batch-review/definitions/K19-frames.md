# K19 — frames

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded interpretation boundary**.

**Meaning in plain language.** A context supplies a declared interpretation boundary for a subject. Framing makes it relevant for a purpose without validating its claims.

**Question answered.** Which subject does this Context frame for relevance and interpretation?

**Formal definition.**

```text
Meaning_K19(W,e,f) := ∃ w ∈ W.ContextFraming. Base_K19(W,e,f,w) ∧ (w.context = s ∧ w.subject = t ∧ w.role = code(q.framing_role) ∧ (t,w.role) ∈ w.context.subjectBoundary ∧ RelevanceWithin(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ContextFraming record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `context` | Context exact revision |
| `subject` | framed Product, Goal, Project, Review or Bounded Context revision |
| `role` | owned framing role |
| `relevance` | exact context subject/relevance boundary |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`RelevanceWithin`: The exact context boundary includes this subject and framing role under its owned relevance interpretation; a Bounded Context target retains its separate domain identity.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `framing_role` | `w.role` | owned context-to-subject relevance role, keeping Bounded Context identity distinct |

**Operational behavior.** Record contextual framing without changing source authority, currentness or truth.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Context C frames Subject S for review, while S contains a stale and unaccepted claim.

**Insufficient case.** A subject outside the declared relevance boundary cannot reuse this framing witness.

**Useful correction.** Add or select the exact context revision whose relevance boundary includes this subject and role.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| source-authority | A separately governed authority boundary recognizes the source's authority, beyond context framing or view consumption. | `relation.frames:forbidden:0` |
| currentness | A current source observation at now still selects this source revision; historical as-of agreement is insufficient. | `relation.frames:forbidden:1` |
| truth | The independent truth valuation makes the exact interpreted claim true; evidential polarity is not that valuation. | `relation.frames:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Context framing and DDD Bounded Context identity need separate projections; relevance does not authenticate a source or make it current.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/frames.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K19-frames.json)

**Exact ordered pairs (5).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| context | bounded-context | context to bounded-context: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| context | goal | context to goal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| context | product | context to product: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| context | project | context to project: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| context | review | context to review: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
