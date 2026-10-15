# K02 — addresses-intent

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded owner selection**.

**Meaning in plain language.** An owner has selected this subject to address an intent. Selection supplies a reason for work, while satisfaction and completion need their own evidence.

**Question answered.** Which exact Intent is this governed subject intended to address?

**Formal definition.**

```text
Meaning_K02(W,e,f) := ∃ w ∈ W.IntentSelection. Base_K02(W,e,f,w) ∧ (w.subject = s ∧ w.intent = t ∧ w.resolution = resolve(q.intent_resolution_ref) ∧ w.resolution.intent = t ∧ s ∈ w.resolution.selected ∧ s ∉ w.resolution.excluded ∧ w.role = code(q.addressing_role) ∧ w.role = roleFor(w.resolution,s) ∧ SelectedByOwner(W,w.resolution,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a IntentSelection record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `subject` | selected Assignment, Goal, Product, Capability, Project or Inquiry revision |
| `intent` | Intent exact revision |
| `resolution` | owned Intent Resolution with selected/excluded subjects, decision, roles and satisfaction tests |
| `role` | selection addressing role |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`SelectedByOwner`: An actual decision in the independently supplied owner decision catalog selects this resolution revision, selected/excluded participants, role map and exact satisfaction-test definitions within the frame. The tests need not have passed.

`roleFor`: The uniquely selected addressing role for this subject in the exact owned Intent Resolution role map. Missing or ambiguous entries cannot establish the selection meaning.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `intent_resolution_ref` | `w.resolution` | owned selected resolution including this subject and excluding no selected subject |
| `addressing_role` | `w.role` | role chosen for this subject by that exact resolution |

**Operational behavior.** Record the selected subject's intended addressing of the intent; preserve satisfaction, delivery and authority as separate facts.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** An owner selects Project P to address Intent I under Test Q; Q has not passed and P is incomplete.

**Insufficient case.** A subject appearing only in the resolution's excluded list cannot be accepted.

**Useful correction.** Supply the exact owner-selected resolution that includes this subject and agrees with its addressing role; revise the resolution if it excludes the subject.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| satisfaction | Every satisfaction test selected by the exact intent resolution has admissible support. | `relation.addresses-intent:forbidden:0` |
| completion | The owned complete requirement set for this work is fulfilled with admissible exact support. | `relation.addresses-intent:forbidden:1` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.addresses-intent:forbidden:2` |
| membership | An independently owned member-to-container record establishes membership/composition. | `relation.addresses-intent:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Existing parser/body fragments do not realize all selection-policy premises; satisfaction-test ownership, selection/exclusion and catalog authenticity remain.

**Review status.** An earlier scoped meaning receipt exists. It remains bound to its original definition; this expansion is presented for batch review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/addresses-intent.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K02-addresses-intent.json)

**Exact ordered pairs (6).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-assignment | intent | agent-assignment to intent: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| goal | intent | goal to intent: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| product | intent | product to intent: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| product-capability | intent | product-capability to intent: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| project | intent | project to intent: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| research-inquiry | intent | research-inquiry to intent: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
