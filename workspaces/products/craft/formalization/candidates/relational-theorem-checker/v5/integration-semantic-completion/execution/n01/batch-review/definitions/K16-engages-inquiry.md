# K16 — engages-inquiry

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded role-specific engagement**.

**Meaning in plain language.** An activity addresses an inquiry, or a finding proposes an answer. These are distinct engagement constructors; neither accepts the answer or completes the inquiry.

**Question answered.** How does this research carrier engage a Research Inquiry?

**Formal definition.**

```text
Meaning_K16(W,e,f) := ∃ w ∈ W.InquiryEngagement. Base_K16(W,e,f,w) ∧ (w.carrier = s ∧ w.inquiry = t ∧ w.role = code(q.inquiry_role) ∧ ((kind(s)=finding ∧ w.constructor=proposedAnswer) ∨ (kind(s)∈{experimentDesign,experimentRun,researchRun} ∧ w.constructor=activityAddressing)))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a InquiryEngagement record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `carrier` | Finding or research activity exact revision |
| `inquiry` | Research Inquiry exact revision |
| `role` | owned answer/activity engagement role |
| `constructor` | proposedAnswer or activityAddressing |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`kind`: The independently captured governed artifact kind of an exact reference. Camel-case constructor names in formulas denote the corresponding hyphenated source kinds listed in the signature matrix.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `inquiry_role` | `w.role` | finding proposed-answer role or activity-addressing role; constructor follows source kind |

**Operational behavior.** Record the appropriate engagement constructor without accepting a finding, adding evidence or completing the inquiry.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** A Finding F proposes an answer to Inquiry I but F has not been accepted and I remains open.

**Insufficient case.** An activity-addressing witness cannot establish a finding-answer witness.

**Useful correction.** Select the finding-answer constructor for a finding and the activity-addressing constructor for a research activity.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| finding-acceptance | An actual owner decision accepts the exact finding, beyond its proposed answer to an inquiry. | `relation.engages-inquiry:forbidden:0` |
| evidence-support | An admissible evidence-polarity record supports the claim, beyond an inquiry answer or evaluation target. | `relation.engages-inquiry:forbidden:1` |
| inquiry-completion | All owned inquiry completion criteria have admissible exact support. | `relation.engages-inquiry:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Raw carrier bodies and role codes must refine the two constructors; answer content and experimental execution remain separate evidence.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/engages-inquiry.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K16-engages-inquiry.json)

**Exact ordered pairs (4).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| experiment-design | research-inquiry | activityAddressing constructor for experiment-design |
| experiment-run | research-inquiry | activityAddressing constructor for experiment-run |
| finding | research-inquiry | proposedAnswer constructor |
| research-run | research-inquiry | activityAddressing constructor for research-run |
