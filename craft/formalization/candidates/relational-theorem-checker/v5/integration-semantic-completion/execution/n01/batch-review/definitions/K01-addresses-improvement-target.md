# K01 — addresses-improvement-target

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded intent**.

**Meaning in plain language.** An inquiry may aim at an improvement target while the target stays open. The link is optional: inquiries need not have an improvement target.

**Question answered.** Which Improvement Target is this Research Inquiry intended to address?

**Formal definition.**

```text
Meaning_K01(W,e,f) := ∃ w ∈ W.ImprovementAddressing. Base_K01(W,e,f,w) ∧ (w.inquiry = s ∧ w.target = t ∧ t = resolve(q.target_version_ref) ∧ w.role = code(q.addressing_role))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ImprovementAddressing record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `inquiry` | Research Inquiry exact revision |
| `target` | Improvement Target exact revision |
| `role` | owned intended-addressing role for this inquiry/target pair |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `target_version_ref` | `w.target` | exact Improvement Target revision; optional inquiry linkage |
| `addressing_role` | `w.role` | intended investigation/addressing role; no resolution or measured improvement |

**Operational behavior.** Append the inquiry's intended addressing of this target revision; do not mark the target resolved or improved.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Inquiry I is assigned to investigate Target T while the target remains open and no improvement has been measured.

**Insufficient case.** A work record for T@2 cannot justify an edge to T@1.

**Useful correction.** Use the target revision actually named by the addressing declaration, or create a new declaration for the other revision.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| resolution | A completed owned resolution establishes all relevant target criteria, beyond inquiry intent or a context request. | `relation.addresses-improvement-target:forbidden:0` |
| improvement | An admissible comparison establishes improvement under the owned target metric. | `relation.addresses-improvement-target:forbidden:1` |
| priority | An actual owned prioritization decision assigns the target a position in the exact queue. | `relation.addresses-improvement-target:forbidden:2` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.addresses-improvement-target:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** An owner-maintained optional addressing declaration and exact target/role resolution must be mapped; do not add a required target to every inquiry.

**Review status.** An earlier scoped meaning receipt exists. It remains bound to its original definition; this expansion is presented for batch review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/addresses-improvement-target.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K01-addresses-improvement-target.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| research-inquiry | improvement-target | research-inquiry to improvement-target: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
