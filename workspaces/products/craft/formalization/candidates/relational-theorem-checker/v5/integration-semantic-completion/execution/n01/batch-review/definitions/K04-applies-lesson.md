# K04 — applies-lesson

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded attributable application**.

**Meaning in plain language.** A recorded application says a lesson was used or deliberately not used, with a reason in this session. Merely selecting or displaying it is insufficient.

**Question answered.** Which exact Operational Lesson revision was used or deliberately not used by this Lesson Application?

**Formal definition.**

```text
Meaning_K04(W,e,f) := ∃ w ∈ W.LessonUse. Base_K04(W,e,f,w) ∧ (w.application = s ∧ w.lesson = t ∧ t = resolve(q.lesson_revision_ref) ∧ w.posture = code(q.application_posture) ∧ w.posture ∈ {used, deliberatelyNotUsed} ∧ w.assessment = resolve(q.applicability_assessment_ref) ∧ w.precedence = resolve(q.instruction_precedence) ∧ QualifiedLessonUse(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a LessonUse record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `application` | Lesson Application exact revision |
| `lesson` | Operational Lesson exact revision |
| `posture` | used or deliberatelyNotUsed constructor |
| `assessment` | exact lesson/application/frame applicability assessment |
| `precedence` | owned instruction precedence policy |
| `sessionOrAction` | exact attributable use envelope |
| `conflicts` | all relevant instruction conflict origins |
| `overrides` | exact justified override records |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`QualifiedLessonUse`: The application, lesson, session/action, disposition evidence and applicability assessment join exactly; assessment covers applicable/excluded/expiry conditions at this use. All relevant conflicts and override origins are retained. The owned precedence relation is irreflexive and transitive on the applicable instruction set, and each required resolution has a justified winner. Used and deliberate non-use have distinct attributable records.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `lesson_revision_ref` | `w.lesson` | exact Operational Lesson revision |
| `application_posture` | `w.posture` | used or deliberately-not-used; selected and presented remain insufficient |
| `applicability_assessment_ref` | `w.assessment` | assessment for this lesson/application/envelope, including exclusions and expiry |
| `instruction_precedence` | `w.precedence` | owned strict partial order and justified conflict/override resolution; no implicit numeric tie-break |

**Operational behavior.** Record the exact lesson use/non-use posture and its basis; no compliance, benefit or method execution is inferred.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Lesson L is deliberately not used in Session S under a recorded higher-priority instruction; no compliance or benefit follows.

**Insufficient case.** Presenting a lesson to a session without an application record is insufficient.

**Useful correction.** Record actual use or the deliberate non-use decision and its assessment; resolve applicable conflicts with an owned precedence basis.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| compliance | The application meets every applicable instruction obligation under the owned precedence policy. | `relation.applies-lesson:forbidden:0` |
| benefit | An admissible comparison records a positive benefit under the owned metric and baseline policy. | `relation.applies-lesson:forbidden:1` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.applies-lesson:forbidden:2` |
| method-use | An exact method-employment record exists; lesson selection/application alone cannot create it. | `relation.applies-lesson:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Synthetic draft uses inclusive intervals, unlike proposed D02 half-open intervals. Lesson identifiers in original fixtures disagree and need an owned mapping. Applicability, expiry, retention and influence fields are not fully refined.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/applies-lesson.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K04-applies-lesson.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| lesson-application | operational-lesson | lesson-application to operational-lesson: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
