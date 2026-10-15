# K06 — assigned-to

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded lifecycle assignment**.

**Meaning in plain language.** An exact assignment connects an assignee with a role or responsibility and its recorded lifecycle. This connection alone does not add team membership or permissions.

**Question answered.** Which Role or Responsibility is explicitly assigned to this assignee?

**Formal definition.**

```text
Meaning_K06(W,e,f) := ∃ w ∈ W.Assignment. Base_K06(W,e,f,w) ∧ (w.assignment = resolve(q.relation_record_ref) ∧ w.assignee = s ∧ w.assignedRoleOrResponsibility = t ∧ w.assignmentKind = code(q.assignment_kind) ∧ AssignmentRecorded(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a Assignment record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `assignment` | exact lifecycle assignment record |
| `assignee` | Agent Instance, Person Reference or Team revision |
| `assignedRoleOrResponsibility` | Role or Responsibility revision |
| `assignmentKind` | owned role/responsibility assignment constructor |
| `period` | assignment interval or session window |
| `lifecycle` | recorded assignment state at the frame |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`AssignmentRecorded`: The owner-maintained assignment joins assignee, role/responsibility, assignment kind, scope, period and lifecycle. Historical mode records the witnessed state at its recorded epoch; live mode additionally requires active lifecycle and a containing D02 window at the frame epoch. The selected mode is explicit.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `assignment_kind` | `w.assignmentKind` | owned role-assignment or responsibility-assignment constructor for this pair |
| `relation_record_ref` | `w.assignment` | exact assignee/role-or-responsibility assignment and lifecycle record |

**Operational behavior.** Append the exact assignment connection and recorded lifecycle; preserve membership and grants.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Assignee A receives responsibility R without joining Team T or receiving a permission grant.

**Insufficient case.** An assignment to another assignee cannot justify this connection.

**Useful correction.** Use the assignment naming this assignee and role/responsibility; show an active-at-frame record for a live assignment claim.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| team-membership | An owned active team-membership record exists independently of role/responsibility assignment. | `relation.assigned-to:forbidden:0` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.assigned-to:forbidden:1` |
| permission | The complete owned permission policy and an authenticated grant permit this operation. | `relation.assigned-to:forbidden:2` |
| identity | The independent governed identity model equates these endpoints; assignment is not identity. | `relation.assigned-to:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Role-assignment and responsibility records have different fields. Historical assignment and live assignment require explicit temporal/lifecycle profiles.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/assigned-to.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K06-assigned-to.json)

**Exact ordered pairs (6).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-instance | responsibility | agent-instance to responsibility: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-instance | role | agent-instance to role: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| person-reference | responsibility | person-reference to responsibility: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| person-reference | role | person-reference to role: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| team | responsibility | team to responsibility: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| team | role | team to role: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
