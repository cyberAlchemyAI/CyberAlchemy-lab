# K14 — declares-effect-on

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded declared effect**.

**Meaning in plain language.** A decision declares one governance effect on a target. Admission, adoption and authorization are distinct values, and a declaration does not execute them.

**Question answered.** Which exact governance effect does this Decision declare?

**Formal definition.**

```text
Meaning_K14(W,e,f) := f.profile = typedSuccessor ∧ ∃ w ∈ W.DecisionDeclaration. Base_K14(W,e,f,w) ∧ (w.decision = s ∧ w.target = t ∧ t = resolve(q.exact_target_version_ref) ∧ w.effect = effectValue(q.effect_kind) ∧ w.effect ∈ {admission,adoption,authorization} ∧ w.declaration = selectedDeclaration(W,s,t,w.effect,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a DecisionDeclaration record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `decision` | Decision exact revision |
| `target` | governance target exact revision |
| `effect` | one distinct governance effect constructor |
| `declaration` | exact selected decision declaration |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`effectValue`: The explicit profile-indexed interpretation of the raw effect token as admission, adoption or authorization. Legacy literal meaning is retained; no cross-effect conversion exists.

`selectedDeclaration`: The unique owned selected decision declaration for this decision/target/effect in the frame. Other declarations or later transactions remain separate records.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `effect_kind` | `w.effect` | distinct admission/adoption/authorization declaration value in the selected profile |
| `exact_target_version_ref` | `w.target` | exact selected governance target, preserving F0 literal meaning |

**Operational behavior.** Append the selected governance-effect declaration for t; execute no effect and infer no other effect value.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Decision D declares adoption of T while admission and authorization remain absent and D has not been applied.

**Insufficient case.** An adoption declaration cannot discharge an authorization challenge.

**Useful correction.** Use the selected declaration for this effect and target; provide a separately authorized application receipt to claim execution.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| effect-execution | A verified completed transaction applies this declared effect to the exact target. | `relation.declares-effect-on:forbidden:0` |
| cross-effect-inference | A distinct governance declaration exists for other != declared; an admission/adoption/authorization value cannot produce the other values by itself. | `relation.declares-effect-on:forbidden:1` |
| runtime-success | An actual runtime execution satisfies every owned success criterion. | `relation.declares-effect-on:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Retain F0 literal effect meaning while introducing any typed successor mapping. All 21 target branches need exact target/effect admissibility.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/declares-effect-on.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K14-declares-effect-on.json)

**Exact ordered pairs (21).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| decision | agent-capability | decision to agent-capability: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | agent-profile | decision to agent-profile: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | artifact-type | decision to artifact-type: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | capability-realization-binding | decision to capability-realization-binding: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | challenge-event | decision to challenge-event: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | classification-assignment | decision to classification-assignment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | communication-preference | decision to communication-preference: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | definition | decision to definition: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | delegation | decision to delegation: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | effect | decision to effect: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | failure-assessment | decision to failure-assessment: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | failure-control-binding | decision to failure-control-binding: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | failure-mode | decision to failure-mode: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | failure-occurrence | decision to failure-occurrence: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | governed-model | decision to governed-model: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | improvement-target | decision to improvement-target: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | incident | decision to incident: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | intent-resolution | decision to intent-resolution: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | operational-lesson | decision to operational-lesson: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | product-capability | decision to product-capability: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| decision | relation-kind | decision to relation-kind: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |

**Legacy profile boundary.** Exact original literal-token/accepted-assessment predicate. An accepted flag or nonempty literal remains supplied graph data; it is not authenticated source truth or actual application.

`LegacyQualified_k(g,e) := e.kind = k ∧ Relational.InstanceValid(g,e)`

Preserve legacy acceptance in its separately named/profile-indexed API. Do not rename LegacyQualified as the stronger Meaning, or infer typed-successor evidence, enum restrictions, execution or criteria completion from legacy acceptance.

