# K21 — governed-by

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded applicable governance**.

**Meaning in plain language.** A policy, constitution, challenge contract or classification scheme applies to a subject in this frame. Applicability does not establish compliance or permission.

**Question answered.** Which Policy or Constitution governs this subject?

**Formal definition.**

```text
Meaning_K21(W,e,f) := ∃ w ∈ W.GovernanceApplicability. Base_K21(W,e,f,w) ∧ (w.subject = s ∧ w.governor = t ∧ w.role = code(q.governance_role) ∧ GovernanceApplies(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a GovernanceApplicability record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `subject` | exact governed subject revision |
| `governor` | Policy, Constitution, Challenge Contract or Classification Scheme revision |
| `role` | owned governance applicability role |
| `conditions` | owned applicability conditions |
| `origins` | complete applicable norm origins |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`GovernanceApplies`: An exact applicability record names this subject, governor and role; its owned scope/window and applicability conditions evaluate yes. All applicable norm origins are retained. Conflicting norms are represented separately and cannot produce a compliance or permission verdict.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `governance_role` | `w.role` | pair-specific policy/constitution/contract/scheme applicability role |

**Operational behavior.** Record governance applicability without establishing conformance, authorization or admission.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Policy P governs Subject S while S violates a requirement and has no authorization grant.

**Insufficient case.** A policy applicable in another scope cannot govern this scope through label equality.

**Useful correction.** Select the governance record applicable to this subject, scope and time; leave unresolved conditions unknown.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| conformance | An admissible exact conformance assessment establishes every applicable target criterion in scope. | `relation.governed-by:forbidden:0` |
| authorization | An actual exact authorization decision or grant permits the operation within its bounded envelope. | `relation.governed-by:forbidden:1` |
| admission | An already authorized atomic transaction placed an endpoint in the admitted state. | `relation.governed-by:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Twenty-nine branches require distinct governor semantics. Inherited norms and opposing obligations need the E00/E04 conflict bridge.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/governed-by.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K21-governed-by.json)

**Exact ordered pairs (29).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| admission-transaction | policy | policy applicability constructor and complete norm origins for admission-transaction |
| agent-action | policy | policy applicability constructor and complete norm origins for agent-action |
| agent-instance | policy | policy applicability constructor and complete norm origins for agent-instance |
| agent-profile | policy | policy applicability constructor and complete norm origins for agent-profile |
| agent-session | policy | policy applicability constructor and complete norm origins for agent-session |
| artifact-type | constitution | constitution applicability constructor and complete norm origins for artifact-type |
| authority-boundary | policy | policy applicability constructor and complete norm origins for authority-boundary |
| challenge-contract | policy | policy applicability constructor and complete norm origins for challenge-contract |
| challenge-event | challenge-contract | challenge-contract applicability constructor and complete norm origins for challenge-event |
| classification-assignment | classification-scheme | classification-scheme applicability constructor and complete norm origins for classification-assignment |
| classification-assignment | policy | policy applicability constructor and complete norm origins for classification-assignment |
| communication-preference | policy | policy applicability constructor and complete norm origins for communication-preference |
| context | policy | policy applicability constructor and complete norm origins for context |
| decision-bundle | policy | policy applicability constructor and complete norm origins for decision-bundle |
| decision-checkpoint | policy | policy applicability constructor and complete norm origins for decision-checkpoint |
| definition | constitution | constitution applicability constructor and complete norm origins for definition |
| failure-assessment | policy | policy applicability constructor and complete norm origins for failure-assessment |
| failure-control-binding | policy | policy applicability constructor and complete norm origins for failure-control-binding |
| failure-mode | policy | policy applicability constructor and complete norm origins for failure-mode |
| failure-occurrence | policy | policy applicability constructor and complete norm origins for failure-occurrence |
| feedback-record | policy | policy applicability constructor and complete norm origins for feedback-record |
| incident | policy | policy applicability constructor and complete norm origins for incident |
| ontology | policy | policy applicability constructor and complete norm origins for ontology |
| ontology-edge | policy | policy applicability constructor and complete norm origins for ontology-edge |
| ontology-node | policy | policy applicability constructor and complete norm origins for ontology-node |
| operational-lesson | policy | policy applicability constructor and complete norm origins for operational-lesson |
| relation-kind | constitution | constitution applicability constructor and complete norm origins for relation-kind |
| user-decision-preference | policy | policy applicability constructor and complete norm origins for user-decision-preference |
| workflow-decision-profile | policy | policy applicability constructor and complete norm origins for workflow-decision-profile |
