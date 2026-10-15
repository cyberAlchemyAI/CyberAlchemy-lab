# K31 — profiled-by

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded configuration**.

**Meaning in plain language.** An instance is configured by an exact profile through a specific binding. Configuration alone does not create capability, conformance or identity continuity.

**Question answered.** Which exact Agent Profile revision configures this Agent Instance?

**Formal definition.**

```text
Meaning_K31(W,e,f) := ∃ w ∈ W.ProfileBinding. Base_K31(W,e,f,w) ∧ (w.instance = s ∧ w.profile = t ∧ t = resolve(q.profile_version_ref) ∧ w.binding = resolve(q.binding_ref) ∧ w.binding.instance = s ∧ w.binding.profile = t ∧ w.binding.constructor = profileConfiguration)
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ProfileBinding record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `instance` | Agent Instance exact revision |
| `profile` | Agent Profile exact revision |
| `binding` | owned profile configuration record |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `profile_version_ref` | `w.profile` | exact configuring Agent Profile revision |
| `binding_ref` | `w.binding` | owned profile configuration record; separate from generic classification |

**Operational behavior.** Record profile configuration without deriving capability, authority, conformance or identity continuity.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Instance I is configured by Profile P but has no declared capability or successful conformance assessment.

**Insufficient case.** A generic instance-of binding cannot substitute for the profile-configuration role.

**Useful correction.** Supply the exact profile-configuration binding; a generic classification assignment cannot substitute for it.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| conformance | An admissible exact conformance assessment establishes every applicable target criterion in scope. | `relation.profiled-by:forbidden:0` |
| capability | An exact capability declaration identifies the agent and versioned capability under its owned basis. | `relation.profiled-by:forbidden:1` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.profiled-by:forbidden:2` |
| identity-continuity | A distinct continuity record establishes the instance's identity continuation, beyond profile configuration. | `relation.profiled-by:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Profile binding source fields and ownership need refinement; capability inheritance and identity continuity require separate explicit contracts.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/profiled-by.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K31-profiled-by.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-instance | agent-profile | agent-instance to agent-profile: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
