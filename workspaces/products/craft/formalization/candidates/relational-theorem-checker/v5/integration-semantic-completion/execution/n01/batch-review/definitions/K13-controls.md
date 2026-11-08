# K13 — controls

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded intended control**.

**Meaning in plain language.** A binding names a control intended for a failure mode and states its role. The binding can exist before installation or execution.

**Question answered.** Which Failure Mode is this Failure Control Binding intended to control?

**Formal definition.**

```text
Meaning_K13(W,e,f) := ∃ w ∈ W.ControlBinding. Base_K13(W,e,f,w) ∧ (w.binding = s ∧ w.failureMode = t ∧ w.control = resolve(q.control_version_ref) ∧ w.binding.controlSubject = w.control ∧ w.binding.failureMode = t ∧ w.role = code(q.control_role) ∧ w.role ∈ {prevent,detect,contain,recover,compensate} ∧ w.installationPosture = code(q.installation_posture))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ControlBinding record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `binding` | Failure Control Binding exact revision |
| `failureMode` | Failure Mode exact revision |
| `control` | the separate controlSubject revision |
| `role` | one primary intended control role |
| `installationPosture` | recorded binding installation posture |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `control_role` | `w.role` | one primary prevent/detect/contain/recover/compensate role |
| `control_version_ref` | `w.control` | exact binding.controlSubject revision; never the failure-mode endpoint |
| `installation_posture` | `w.installationPosture` | owner-recorded intended/installed or other declared binding posture; no installation inference |

**Operational behavior.** Record intended control of this mode by the exact bound control; preserve installation/execution/effectiveness facts.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Binding B names Control C as detect for Mode M; C is still a candidate and is not installed.

**Insufficient case.** Using Mode M's revision as control_version_ref fails the bound-control role.

**Useful correction.** Reference the controlSubject revision, retain its actual installation posture, and select one owned primary control role.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| installation | An authenticated installation receipt establishes that the control is present and configured in this environment. | `relation.controls:forbidden:0` |
| execution | A verified execution trace shows that the exact control ran in the relevant envelope. | `relation.controls:forbidden:1` |
| effectiveness | An admissible outcome assessment establishes the owned effectiveness test. | `relation.controls:forbidden:2` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.controls:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** A typed control subject and installation-posture catalog must be mapped. The failure-mode target is not the control-version reference.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/controls.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K13-controls.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| failure-control-binding | failure-mode | failure-control-binding to failure-mode: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
