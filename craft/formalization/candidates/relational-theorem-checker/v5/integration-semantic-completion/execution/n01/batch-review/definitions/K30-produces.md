# K30 — produces

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded attributable production**.

**Meaning in plain language.** An action produced an exact recorded output. Producing a candidate does not accept it, prove its correctness or admit it.

**Question answered.** Which governed output was produced by this Agent Action?

**Formal definition.**

```text
Meaning_K30(W,e,f) := ∃ w ∈ W.ActionOutput. Base_K30(W,e,f,w) ∧ (w.action = s ∧ w.output = t ∧ w.receipt = resolve(q.action_receipt_ref) ∧ w.role = code(q.production_role) ∧ w.posture = code(q.output_posture) ∧ t ∈ w.action.actualOutputs ∧ OutputProduced(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ActionOutput record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `action` | Agent Action exact revision |
| `output` | exact produced artifact revision |
| `receipt` | attributable action/output/frame production receipt |
| `role` | owned production role |
| `posture` | recorded output posture, separate from output acceptance |
| `actualOutputs` | outputs established by the production observation |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`OutputProduced`: An admissible production observation and receipt join this action, output bytes/revision, role, posture and frame. The output belongs to the observed actual output set, not merely a planned set. It may remain a candidate or later be rejected.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `action_receipt_ref` | `w.receipt` | exact attributable action/output/frame production receipt |
| `production_role` | `w.role` | owned action-output production role |
| `output_posture` | `w.posture` | actual recorded output posture; planned output does not qualify as produced |

**Operational behavior.** Record exact produced output and posture; preserve acceptance, correctness, admission and authority effect as separate facts.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Action A produces candidate Output O, which is later rejected by its owner.

**Insufficient case.** A receipt for a planned or different output cannot justify this production claim.

**Useful correction.** Supply a receipt for this actual output and action; keep a planned output in the plan until production is observed.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| acceptance | An actual exact owner acceptance event exists for the governed output under the selected policy. | `relation.produces:forbidden:0` |
| correctness | The output satisfies its independently owned correctness specification, beyond production or acceptance. | `relation.produces:forbidden:1` |
| admission | An already authorized atomic transaction placed an endpoint in the admitted state. | `relation.produces:forbidden:2` |
| authority-effect | A verified applied transaction executed the exact already-authorized effect on the target. | `relation.produces:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Nineteen output-kind branches need exact receipt roles and body capture. Planned references and candidate acceptance labels are insufficient.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/produces.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K30-produces.json)

**Exact ordered pairs (19).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-action | agent-reflection | actual agent-reflection output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | challenge-event | actual challenge-event output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | classification-assignment | actual classification-assignment output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | definition | actual definition output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | drift-assessment | actual drift-assessment output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | evidence-set | actual evidence-set output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | failure-assessment | actual failure-assessment output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | failure-occurrence | actual failure-occurrence output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | feedback-record | actual feedback-record output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | finding | actual finding output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | generated-output | actual generated-output output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | improvement-signal | actual improvement-signal output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | lesson-application | actual lesson-application output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | measurement-result | actual measurement-result output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | observation | actual observation output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | operational-lesson | actual operational-lesson output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | operational-observation | actual operational-observation output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | typed-relation | actual typed-relation output bytes/revision joined to Agent Action and exact attributable production receipt |
| agent-action | work-outcome-assessment | actual work-outcome-assessment output bytes/revision joined to Agent Action and exact attributable production receipt |
