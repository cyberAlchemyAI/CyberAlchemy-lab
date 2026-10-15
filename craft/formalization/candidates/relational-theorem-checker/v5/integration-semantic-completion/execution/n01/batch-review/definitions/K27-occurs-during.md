# K27 — occurs-during

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded temporal attribution**.

**Meaning in plain language.** An occurrence was observed within a particular execution envelope and time domain. Temporal inclusion does not establish cause or recovery.

**Question answered.** In which exact execution envelope did this Failure Occurrence happen?

**Formal definition.**

```text
Meaning_K27(W,e,f) := ∃ w ∈ W.OccurrenceEnvelope. Base_K27(W,e,f,w) ∧ (w.occurrence = s ∧ w.envelope = t ∧ t = resolve(q.envelope_version_ref) ∧ w.scope = resolve(q.temporal_scope) ∧ OccurrenceWithin(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a OccurrenceEnvelope record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `occurrence` | Failure Occurrence exact revision |
| `envelope` | Action, Session, experiment, research or Work execution envelope |
| `scope` | owned temporal attribution scope |
| `event` | observed occurrence time or interval in the envelope time domain |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`OccurrenceWithin`: An admissible observation supplies the occurrence event time/interval; the exact envelope independently supplies its execution window in the same time domain. The owned temporal-scope policy establishes inclusion under D02. Planned windows do not show observed occurrence.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `envelope_version_ref` | `w.envelope` | exact observed execution envelope revision |
| `temporal_scope` | `w.scope` | owned temporal attribution scope and time-domain inclusion policy |

**Operational behavior.** Record occurrence within the exact envelope without establishing cause, blame, severity or recovery.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Occurrence F is recorded inside Session S; no causal or recovery assessment has been made.

**Insufficient case.** An event in a different time domain cannot be inserted by comparing raw epoch numbers.

**Useful correction.** Resolve the exact envelope and compare the observed event under its owned time-domain/window policy.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| cause | The owned causal model supports a counterfactual/intervention dependence, beyond observation or temporal association. | `relation.occurs-during:forbidden:0` |
| blame | An independently justified responsibility assessment attributes fault, beyond temporal occurrence or impact. | `relation.occurs-during:forbidden:1` |
| severity | A distinct admissible severity assessment assigns a grade under the owned severity policy. | `relation.occurs-during:forbidden:2` |
| recovery | An admissible recovery assessment establishes restoration against every owned recovery criterion. | `relation.occurs-during:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** All five envelope kinds need observed execution windows; equal numeric epochs in different domains cannot establish inclusion.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/occurs-during.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K27-occurs-during.json)

**Exact ordered pairs (5).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| failure-occurrence | agent-action | observed Failure Occurrence inside the exact agent-action execution window and time domain |
| failure-occurrence | agent-session | observed Failure Occurrence inside the exact agent-session execution window and time domain |
| failure-occurrence | experiment-run | observed Failure Occurrence inside the exact experiment-run execution window and time domain |
| failure-occurrence | research-run | observed Failure Occurrence inside the exact research-run execution window and time domain |
| failure-occurrence | work | observed Failure Occurrence inside the exact work execution window and time domain |
