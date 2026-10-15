# K12 — contributes-to

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded intent**.

**Meaning in plain language.** A contribution declaration says how an activity intends to advance a product or goal. It does not establish delivered value or membership.

**Question answered.** Which Product or Goal is this activity intended to advance?

**Formal definition.**

```text
Meaning_K12(W,e,f) := ∃ w ∈ W.IntendedContribution. Base_K12(W,e,f,w) ∧ (w.activity = s ∧ w.objective = t ∧ w.role = code(q.contribution_role) ∧ w.scope = resolve(q.contribution_scope) ∧ w.declaration.activity = s ∧ w.declaration.objective = t ∧ w.declaration.role = w.role ∧ w.declaration.scope = w.scope ∧ w.declaration.intent = intendedContribution)
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a IntendedContribution record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `activity` | exact activity/project/inquiry revision |
| `objective` | Product or Goal exact revision |
| `role` | owned intended contribution role |
| `scope` | bounded contribution scope |
| `declaration` | record of intended advancement |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `contribution_role` | `w.role` | intended activity-to-product/goal contribution constructor |
| `contribution_scope` | `w.scope` | bounded scope of intended contribution, not a product-value assessment |

**Operational behavior.** Record intended contribution; preserve membership, realized outcomes, assessments and product value.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Activity A intends to advance Goal G but has produced no realized improvement.

**Insufficient case.** A contribution in scope X cannot be accepted as a contribution in wider scope Y.

**Useful correction.** Match the declaration scope and role to this activity and objective; use separate outcome evidence for realized contribution.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| membership | An independently owned member-to-container record establishes membership/composition. | `relation.contributes-to:forbidden:0` |
| realization | An independent instantiation/execution witness establishes concrete realization, beyond declared contribution or method use. | `relation.contributes-to:forbidden:1` |
| evaluation-result | An admissible evaluation result is established, beyond identifying its subject or intended contribution. | `relation.contributes-to:forbidden:2` |
| product-value | An admissible valuation assessment establishes product value under its explicit metric and baseline. | `relation.contributes-to:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Each of eight permitted pairs needs an intended-contribution adapter; product value and goal achievement cannot be collapsed into this declaration.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/contributes-to.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K12-contributes-to.json)

**Exact ordered pairs (8).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-action | goal | agent-action to goal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-action | product | agent-action to product: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| experiment-design | goal | experiment-design to goal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| experiment-run | goal | experiment-run to goal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| project | goal | project to goal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| project | product | project to product: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| research-inquiry | goal | research-inquiry to goal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| research-run | goal | research-run to goal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
