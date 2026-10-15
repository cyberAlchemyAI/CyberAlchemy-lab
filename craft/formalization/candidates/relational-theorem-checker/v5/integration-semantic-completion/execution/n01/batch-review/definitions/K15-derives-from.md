# K15 — derives-from

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded lineage**.

**Meaning in plain language.** A recorded transformation, compilation or projection produced one revision from another. Lineage does not transfer source authority or equate identities.

**Question answered.** From which material or governed source was this artifact derived?

**Formal definition.**

```text
Meaning_K15(W,e,f) := ∃ w ∈ W.Derivation. Base_K15(W,e,f,w) ∧ (w.derived = s ∧ w.input = t ∧ w.role = code(q.derivation_role) ∧ w.transform.role = w.role ∧ w.transform.output = s ∧ t ∈ w.transform.inputs ∧ w.transform.kind ∈ {transformation,compilation,projection})
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a Derivation record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `derived` | derived exact revision |
| `input` | source exact revision |
| `role` | owned derivation role |
| `transform` | exact transformation record with inputs and output |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `derivation_role` | `w.role` | transformation/compilation/projection role joining actual input and output revisions |

**Operational behavior.** Record derivation lineage without merging identities or transferring source authority.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Generated Projection P derives from Source S while P is independently identified and unadmitted.

**Insufficient case.** An origin assertion with no derivation record cannot stand in for a transformation.

**Useful correction.** Provide the actual transformation record joining this input to this output; keep an origin assertion separate.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| identity-equality | The independent governed identity model equates these endpoints, beyond lineage or succession. | `relation.derives-from:forbidden:0` |
| source-authority-transfer | A separately authorized authority transfer recognizes the derived artifact as an authority holder. | `relation.derives-from:forbidden:1` |
| admission | An already authorized atomic transaction placed an endpoint in the admitted state. | `relation.derives-from:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Forty heterogeneous branches need input/output projections and transformation provenance. Repeated graph edges do not prove transformation correctness.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/derives-from.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K15-derives-from.json)

**Exact ordered pairs (40).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-reflection | agent-action | agent-reflection to agent-action: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-reflection | agent-session | agent-reflection to agent-session: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-reflection | evidence-set | agent-reflection to evidence-set: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-reflection | failure-assessment | agent-reflection to failure-assessment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-reflection | feedback-record | agent-reflection to feedback-record: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-reflection | finding | agent-reflection to finding: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-reflection | observation | agent-reflection to observation: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-reflection | operational-observation | agent-reflection to operational-observation: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-reflection | work-outcome-assessment | agent-reflection to work-outcome-assessment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| classification-assignment | evidence-set | classification-assignment to evidence-set: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| classification-assignment | feedback-record | classification-assignment to feedback-record: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| classification-assignment | finding | classification-assignment to finding: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| classification-assignment | measurement-result | classification-assignment to measurement-result: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| classification-assignment | observation | classification-assignment to observation: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| classification-assignment | operational-observation | classification-assignment to operational-observation: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| classification-assignment | source | classification-assignment to source: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| context-view | context | context-view to context: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| evidence-set | experiment-run | evidence-set to experiment-run: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| evidence-set | research-run | evidence-set to research-run: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| finding | evidence-set | finding to evidence-set: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| finding | research-run | finding to research-run: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| generated-output | source | generated-output to source: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| improvement-signal | drift-assessment | improvement-signal to drift-assessment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| improvement-signal | failure-assessment | improvement-signal to failure-assessment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| improvement-signal | operational-observation | improvement-signal to operational-observation: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| improvement-signal | work-outcome-assessment | improvement-signal to work-outcome-assessment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| improvement-target | improvement-signal | improvement-target to improvement-signal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| improvement-target | lesson-outcome-assessment | improvement-target to lesson-outcome-assessment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| improvement-target | operational-lesson | improvement-target to operational-lesson: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| measurement-result | experiment-run | measurement-result to experiment-run: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| measurement-result | research-run | measurement-result to research-run: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| observation | experiment-run | observation to experiment-run: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| observation | research-run | observation to research-run: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| operational-lesson | agent-reflection | operational-lesson to agent-reflection: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| operational-lesson | evidence-set | operational-lesson to evidence-set: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| operational-lesson | failure-assessment | operational-lesson to failure-assessment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| operational-lesson | feedback-record | operational-lesson to feedback-record: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| operational-lesson | finding | operational-lesson to finding: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| operational-lesson | lesson-outcome-assessment | operational-lesson to lesson-outcome-assessment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| product-capability | product-thesis | product-capability to product-thesis: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
