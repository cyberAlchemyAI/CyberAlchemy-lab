# K24 — instance-of

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded exact classification**.

**Meaning in plain language.** An exact binding classifies a subject under a model, product, capability, failure mode or classification value. Classification does not show realization or conformance.

**Question answered.** Under which exact parent model is this subject classified?

**Formal definition.**

```text
Meaning_K24(W,e,f) := ∃ w ∈ W.Classification. Base_K24(W,e,f,w) ∧ (w.subject = s ∧ w.parent = t ∧ t = resolve(q.parent_version_ref) ∧ w.binding = resolve(q.binding_ref) ∧ w.binding.subject = s ∧ w.binding.parent = t ∧ w.binding.constructor = classificationFor(kind(s),kind(t)))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a Classification record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `subject` | classified exact revision |
| `parent` | exact classification/model/product/failure parent revision |
| `binding` | owned classification assignment or model-instance binding |
| `constructor` | pair-specific classification constructor |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`kind`: The independently captured governed artifact kind of an exact reference. Camel-case constructor names in formulas denote the corresponding hyphenated source kinds listed in the signature matrix.

`classificationFor`: The owned constructor indexed by this exact allowed pair: model instance, product/capability classification, failure classification or classification-value assignment. Each constructor joins the proper parent revision without making a conformance or failure confirmation claim.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `parent_version_ref` | `w.parent` | exact classification/model/product/failure parent revision |
| `binding_ref` | `w.binding` | pair-specific classification or model-instance record |

**Operational behavior.** Record exact parent classification without transferring ownership or establishing conformance.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Candidate Instance I is classified under Model M while a conformance requirement fails.

**Insufficient case.** An assignment under another parent revision cannot justify this classification.

**Useful correction.** Choose the binding whose subject, parent revision and classification constructor match this pair.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| conformance | An admissible exact conformance assessment establishes every applicable target criterion in scope. | `relation.instance-of:forbidden:0` |
| realization | An independent instantiation/execution witness establishes concrete realization, beyond declared contribution or method use. | `relation.instance-of:forbidden:1` |
| ownership-transfer | A separately authorized ownership transition changes the artifact's owner. | `relation.instance-of:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Twelve branches require classification-specific bodies; classification under a failure mode is not the separate confirmation assessment.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/instance-of.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K24-instance-of.json)

**Exact ordered pairs (12).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-action | classification-value | classificationFor(agent-action,classification-value); bind this exact subject to this exact parent using the pair-specific assignment |
| agent-instance | classification-value | classificationFor(agent-instance,classification-value); bind this exact subject to this exact parent using the pair-specific assignment |
| capability-instance | governed-model | classificationFor(capability-instance,governed-model); bind this exact subject to this exact parent using the pair-specific assignment |
| capability-instance | product-capability | classificationFor(capability-instance,product-capability); bind this exact subject to this exact parent using the pair-specific assignment |
| failure-mode | classification-value | classificationFor(failure-mode,classification-value); bind this exact subject to this exact parent using the pair-specific assignment |
| failure-occurrence | classification-value | classificationFor(failure-occurrence,classification-value); bind this exact subject to this exact parent using the pair-specific assignment |
| failure-occurrence | failure-mode | classificationFor(failure-occurrence,failure-mode); bind this exact subject to this exact parent using the pair-specific assignment |
| implementation | governed-model | classificationFor(implementation,governed-model); bind this exact subject to this exact parent using the pair-specific assignment |
| implementation | product-capability | classificationFor(implementation,product-capability); bind this exact subject to this exact parent using the pair-specific assignment |
| improvement-target | classification-value | classificationFor(improvement-target,classification-value); bind this exact subject to this exact parent using the pair-specific assignment |
| operational-lesson | classification-value | classificationFor(operational-lesson,classification-value); bind this exact subject to this exact parent using the pair-specific assignment |
| product-capability | product | classificationFor(product-capability,product); bind this exact subject to this exact parent using the pair-specific assignment |
