# K34 — responds-to

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded intended response**.

**Meaning in plain language.** An action is intended as a response to an occurrence or incident. Its intended outcome remains separate from successful containment, recovery or closure.

**Question answered.** Which Failure Occurrence or Incident is this Agent Action intended to address?

**Formal definition.**

```text
Meaning_K34(W,e,f) := ∃ w ∈ W.IntendedFailureResponse. Base_K34(W,e,f,w) ∧ (w.action = s ∧ w.incidentOrOccurrence = t ∧ w.role = code(q.response_role) ∧ w.objective = resolve(q.intended_outcome) ∧ w.declaration.action = s ∧ w.declaration.responseTarget = t ∧ w.declaration.role = w.role ∧ w.declaration.intendedOutcome = w.objective)
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a IntendedFailureResponse record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `action` | Agent Action exact revision |
| `incidentOrOccurrence` | Incident or Failure Occurrence exact revision |
| `role` | owned intended response role |
| `objective` | declared versioned response outcome |
| `declaration` | owned intended response declaration |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `response_role` | `w.role` | owned intended response-to-occurrence/incident role |
| `intended_outcome` | `w.objective` | versioned declared response objective; no observed recovery result |

**Operational behavior.** Record intended response without asserting recovery, closure, causal attribution or authority.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Action A intends to contain Incident I but the incident remains open and containment has not succeeded.

**Insufficient case.** An intended recovery label cannot satisfy a recovery-success conclusion.

**Useful correction.** Supply the declaration naming this incident/occurrence and intended outcome; assess actual recovery or closure separately.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| recovery-success | The action satisfies the incident's owned recovery criteria with admissible outcome evidence. | `relation.responds-to:forbidden:0` |
| cause | The owned causal model supports a counterfactual/intervention dependence, beyond observation or temporal association. | `relation.responds-to:forbidden:1` |
| closure | An owned closure event establishes all mandatory incident closure criteria. | `relation.responds-to:forbidden:2` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.responds-to:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Both response constructors and intended-outcome ownership need mapping; response labels cannot discharge recovery criteria.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/responds-to.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K34-responds-to.json)

**Exact ordered pairs (2).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-action | failure-occurrence | agent-action to failure-occurrence: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-action | incident | agent-action to incident: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
