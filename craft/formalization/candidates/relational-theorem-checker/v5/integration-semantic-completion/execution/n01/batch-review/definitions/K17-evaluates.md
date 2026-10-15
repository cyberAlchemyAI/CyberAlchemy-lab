# K17 — evaluates

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded assessment scope**.

**Meaning in plain language.** An evaluation or experiment names its subject and purpose. Naming the target leaves the eventual result and evidential polarity open.

**Question answered.** Which subject or proposition is being assessed?

**Formal definition.**

```text
Meaning_K17(W,e,f) := ∃ w ∈ W.EvaluationTarget. Base_K17(W,e,f,w) ∧ (w.assessor = s ∧ w.subject = t ∧ w.role = code(q.evaluation_role) ∧ w.purpose = code(q.evaluation_purpose) ∧ w.assessmentScope.subject = t ∧ w.assessmentScope.role = w.role ∧ w.assessmentScope.purpose = w.purpose)
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a EvaluationTarget record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `assessor` | Evaluation, experiment or specialized assessment exact revision |
| `subject` | exact evaluated subject revision |
| `role` | owned assessment role |
| `purpose` | owned evaluation purpose |
| `assessmentScope` | recorded target and scope; no result field is required to define targeting |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `evaluation_role` | `w.role` | pair-specific target assessment role, including specialized failure/lesson/preference/work assessment |
| `evaluation_purpose` | `w.purpose` | owned reason/scope for assessment; no evidence polarity or result |

**Operational behavior.** Record what is evaluated and for what purpose; preserve polarity, adoption, realization and value.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Evaluation E assesses Claim C, but its outcome is unknown and no support or contradiction has been established.

**Insufficient case.** Evaluation purpose alone cannot supply an evidence polarity.

**Useful correction.** Use the assessment scope naming this subject and purpose; attach a result assessment separately when claiming support or contradiction.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| support | An admissible supporting-polarity record exists; evaluation targeting, realization and test design cannot create one. | `relation.evaluates:forbidden:0` |
| contradiction | An admissible evidence-polarity record specifically contradicts this claim. | `relation.evaluates:forbidden:1` |
| adoption | An actual selected adoption decision applies to the endpoint, separately from admission and authorization. | `relation.evaluates:forbidden:2` |
| realization | An independent instantiation/execution witness establishes concrete realization, beyond declared contribution or method use. | `relation.evaluates:forbidden:3` |
| product-value | An admissible valuation assessment establishes product value under its explicit metric and baseline. | `relation.evaluates:forbidden:4` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Sixteen branches include specialized failure, lesson, preference and work assessments; their target fields need separate source projections.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/evaluates.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K17-evaluates.json)

**Exact ordered pairs (16).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| evaluation | capability-realization-binding | evaluation assessment target projection for capability-realization-binding; explicit subject, scope, role and purpose without outcome |
| evaluation | product-capability | evaluation assessment target projection for product-capability; explicit subject, scope, role and purpose without outcome |
| evaluation | product-thesis | evaluation assessment target projection for product-thesis; explicit subject, scope, role and purpose without outcome |
| experiment-design | capability-realization-binding | experiment-design assessment target projection for capability-realization-binding; explicit subject, scope, role and purpose without outcome |
| experiment-design | product | experiment-design assessment target projection for product; explicit subject, scope, role and purpose without outcome |
| experiment-design | product-capability | experiment-design assessment target projection for product-capability; explicit subject, scope, role and purpose without outcome |
| experiment-design | product-thesis | experiment-design assessment target projection for product-thesis; explicit subject, scope, role and purpose without outcome |
| experiment-run | capability-realization-binding | experiment-run assessment target projection for capability-realization-binding; explicit subject, scope, role and purpose without outcome |
| experiment-run | product | experiment-run assessment target projection for product; explicit subject, scope, role and purpose without outcome |
| experiment-run | product-capability | experiment-run assessment target projection for product-capability; explicit subject, scope, role and purpose without outcome |
| experiment-run | product-thesis | experiment-run assessment target projection for product-thesis; explicit subject, scope, role and purpose without outcome |
| failure-assessment | failure-occurrence | failure-assessment assessment target projection for failure-occurrence; explicit subject, scope, role and purpose without outcome |
| lesson-outcome-assessment | lesson-application | lesson-outcome-assessment assessment target projection for lesson-application; explicit subject, scope, role and purpose without outcome |
| preference-application-assessment | communication-preference | preference-application-assessment assessment target projection for communication-preference; explicit subject, scope, role and purpose without outcome |
| work-outcome-assessment | agent-action | work-outcome-assessment assessment target projection for agent-action; explicit subject, scope, role and purpose without outcome |
| work-outcome-assessment | work | work-outcome-assessment assessment target projection for work; explicit subject, scope, role and purpose without outcome |
