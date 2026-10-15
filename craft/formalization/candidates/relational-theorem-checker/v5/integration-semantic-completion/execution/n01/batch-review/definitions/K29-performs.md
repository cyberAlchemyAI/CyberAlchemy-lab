# K29 — performs

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded attributable operation**.

**Meaning in plain language.** An agent is attributable to an operation in its exact active session and recorded posture. An attempted or failed action remains an attempted or failed action.

**Question answered.** Which attributable activity is performed or attempted by this Agent Instance?

**Formal definition.**

```text
Meaning_K29(W,e,f) := ∃ w ∈ W.AttributedAction. Base_K29(W,e,f,w) ∧ (w.agent = s ∧ w.operation = t ∧ w.session = resolve(q.session_ref) ∧ w.session.agent = s ∧ w.role = code(q.participation_role) ∧ w.posture = code(q.action_posture) ∧ AttributedOperation(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a AttributedAction record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `agent` | Agent Instance exact revision |
| `operation` | Action, experiment/research run, Review or Work exact revision |
| `session` | exact attributable Agent Session revision |
| `role` | owned operation participation role |
| `posture` | proposed, attempted, completed, rejected or failed constructor |
| `operationEpoch` | recorded operation epoch in the session domain |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`AttributedOperation`: The operation and session records identify this agent, role and posture; admissible operation evidence supplies the operation epoch, and the exact session is active at that epoch in the same time domain. This predicate does not require successful effect or owner approval.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `session_ref` | `w.session` | exact session belonging to this agent and active at the recorded operation epoch |
| `participation_role` | `w.role` | owned actor/operation participation role for this pair |
| `action_posture` | `w.posture` | distinct proposed/attempted/completed/rejected/failed operation posture |

**Operational behavior.** Record actor/action participation and posture while preserving action immutability, ownership and authority.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Agent A attempts Action X in Session S, but X fails and produces no successful effect.

**Insufficient case.** An action attributed to A in another agent's session is not an exact attribution witness.

**Useful correction.** Join this operation to this agent and its session at the recorded epoch; retain the observed posture without upgrading it.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| ownership | An independently governed ownership record identifies the owner, beyond production, action or impact. | `relation.performs:forbidden:0` |
| approval | An actual owner response approves this exact operation and scope. | `relation.performs:forbidden:1` |
| admission | An already authorized atomic transaction placed an endpoint in the admitted state. | `relation.performs:forbidden:2` |
| successful-effect | Admissible outcome evidence establishes the action's owned intended effect. | `relation.performs:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Non-Agent-Action operations have different actor/session fields; all five branches need attribution projections and posture provenance.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/performs.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K29-performs.json)

**Exact ordered pairs (5).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-instance | agent-action | agent-instance attribution to agent-action through its exact active session; preserve operation-specific recorded posture |
| agent-instance | experiment-run | agent-instance attribution to experiment-run through its exact active session; preserve operation-specific recorded posture |
| agent-instance | research-run | agent-instance attribution to research-run through its exact active session; preserve operation-specific recorded posture |
| agent-instance | review | agent-instance attribution to review through its exact active session; preserve operation-specific recorded posture |
| agent-instance | work | agent-instance attribution to work through its exact active session; preserve operation-specific recorded posture |
