# K26 — member-of

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded membership/composition**.

**Meaning in plain language.** A member-to-container record establishes an owned membership or composition link. It does not imply assignments, contributions or inherited permissions.

**Question answered.** Which governed container or scope is this member part of?

**Formal definition.**

```text
Meaning_K26(W,e,f) := ∃ w ∈ W.ScopedMembership. Base_K26(W,e,f,w) ∧ (w.member = s ∧ w.container = t ∧ w.role = code(q.membership_role) ∧ (s,w.role) ∈ w.container.members ∧ w.constructor = membershipFor(kind(s),kind(t)))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ScopedMembership record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `member` | exact member revision |
| `container` | exact container revision |
| `role` | owned membership/composition role |
| `constructor` | team membership, role composition, bundle membership, ontology membership or other exact pair constructor |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`kind`: The independently captured governed artifact kind of an exact reference. Camel-case constructor names in formulas denote the corresponding hyphenated source kinds listed in the signature matrix.

`membershipFor`: The owner-maintained membership/composition constructor for the exact ordered pair. It reads the corresponding container record; inverse or transitive membership is not supplied by this function.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `membership_role` | `w.role` | owned directional membership/composition constructor for this member/container pair |

**Operational behavior.** Record scoped membership or composition; preserve assignments, contributions, authority and identity classes.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Subject S is a member of Container C but has no assignment, contribution record or grant.

**Insufficient case.** The inverse container-to-member pair cannot reuse this directional witness.

**Useful correction.** Use the owner-maintained member-to-container record in the declared direction; do not invert it or add transitive membership without a rule.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| contribution | A distinct contribution declaration records intended advancement of the objective. | `relation.member-of:forbidden:0` |
| assignment | An active exact assignment record identifies this assignee and responsibility. | `relation.member-of:forbidden:1` |
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.member-of:forbidden:2` |
| identity-equivalence | The independent governed identity model equates these endpoints, beyond representation or container membership. | `relation.member-of:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Twenty-four branches have distinct composition/membership meanings. Live membership requires lifecycle evidence separate from historical inclusion.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/member-of.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K26-member-of.json)

**Exact ordered pairs (24).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-action | agent-session | membershipFor(agent-action,agent-session); owner-maintained agent-session container includes agent-action in its exact role |
| agent-assignment | project | membershipFor(agent-assignment,project); owner-maintained project container includes agent-assignment in its exact role |
| agent-instance | agent-session | membershipFor(agent-instance,agent-session); owner-maintained agent-session container includes agent-instance in its exact role |
| capability-realization-binding | project | membershipFor(capability-realization-binding,project); owner-maintained project container includes capability-realization-binding in its exact role |
| classification-value | classification-scheme | membershipFor(classification-value,classification-scheme); owner-maintained classification-scheme container includes classification-value in its exact role |
| context | product | membershipFor(context,product); owner-maintained product container includes context in its exact role |
| context | project | membershipFor(context,project); owner-maintained project container includes context in its exact role |
| decision | decision-bundle | membershipFor(decision,decision-bundle); owner-maintained decision-bundle container includes decision in its exact role |
| evidence-set | project | membershipFor(evidence-set,project); owner-maintained project container includes evidence-set in its exact role |
| experiment-design | project | membershipFor(experiment-design,project); owner-maintained project container includes experiment-design in its exact role |
| experiment-run | project | membershipFor(experiment-run,project); owner-maintained project container includes experiment-run in its exact role |
| failure-occurrence | incident | membershipFor(failure-occurrence,incident); owner-maintained incident container includes failure-occurrence in its exact role |
| goal | project | membershipFor(goal,project); owner-maintained project container includes goal in its exact role |
| ontology-node | ontology | membershipFor(ontology-node,ontology); owner-maintained ontology container includes ontology-node in its exact role |
| person-reference | team | membershipFor(person-reference,team); owner-maintained team container includes person-reference in its exact role |
| product | product | membershipFor(product,product); owner-maintained product container includes product in its exact role |
| product-capability | product | membershipFor(product-capability,product); owner-maintained product container includes product-capability in its exact role |
| product-thesis | product | membershipFor(product-thesis,product); owner-maintained product container includes product-thesis in its exact role |
| project-state | project | membershipFor(project-state,project); owner-maintained project container includes project-state in its exact role |
| research-inquiry | project | membershipFor(research-inquiry,project); owner-maintained project container includes research-inquiry in its exact role |
| research-run | project | membershipFor(research-run,project); owner-maintained project container includes research-run in its exact role |
| responsibility | role | membershipFor(responsibility,role); owner-maintained role container includes responsibility in its exact role |
| typed-relation | ontology | membershipFor(typed-relation,ontology); owner-maintained ontology container includes typed-relation in its exact role |
| work | project | membershipFor(work,project); owner-maintained project container includes work in its exact role |
