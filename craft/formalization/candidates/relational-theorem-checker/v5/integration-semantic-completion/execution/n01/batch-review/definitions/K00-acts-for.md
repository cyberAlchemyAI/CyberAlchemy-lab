# K00 — acts-for

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **checked bounded representation**.

**Meaning in plain language.** Bounded representation permits a particular agent to represent a principal for this use. It does not make them the same identity.

**Question answered.** Which Principal is this Agent Instance acting for under one exact Delegation?

**Formal definition.**

```text
Meaning_K00(W,e,f) := ∃ w ∈ W.DelegationUse. Base_K00(W,e,f,w) ∧ (w.agent = s ∧ w.principal = t ∧ w.delegation = resolve(q.delegation_ref) ∧ w.scope = resolve(q.scope_ref) ∧ w.window = resolve(q.effective_period) ∧ w.revocation = resolve(q.revocation_state) ∧ PermitUse(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a DelegationUse record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `agent` | Agent Instance exact revision |
| `principal` | Principal exact revision |
| `delegation` | Delegation exact revision |
| `scope` | owned scope revision |
| `window` | epoch interval or exact session window |
| `revocation` | as-of revocation observation |
| `use` | exact action, subject and scope being represented |
| `ancestors` | complete applicable delegation chain |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`PermitUse`: The exact delegation names agent and principal; the proposed use lies in every independently established ancestor action/subject/scope envelope; all owned gates evaluate yes; the use epoch lies in the D02 window in its domain; admissible as-of observations show every relevant delegation unrevoked. The ancestry input must be complete under its owned derivation policy.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `delegation_ref` | `w.delegation` | exact Agent-to-Principal delegation; every ancestor restriction remains applicable |
| `scope_ref` | `w.scope` | owned scope containing the proposed use and contained in every ancestor envelope |
| `effective_period` | `w.window` | half-open epoch interval or exact observed session window, with one time domain |
| `revocation_state` | `w.revocation` | admissible as-of observations covering this use and every relevant ancestor |

**Operational behavior.** Record the agent's bounded representation of the principal through d; preserve identities, ownership and the authority-root set.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Agent A represents Principal P for read in scope X at epoch 5 through a delegation valid on [0,10); no write grant exists.

**Insufficient case.** A delegation for Agent B cannot justify A's acts-for edge.

**Useful correction.** Select the delegation for this agent and principal; narrow the use to the intersection of all ancestor envelopes and supply matching window/gate/revocation evidence.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| identity-equivalence | The independent governed identity model equates these endpoints, beyond representation or container membership. | `relation.acts-for:forbidden:0` |
| ownership-transfer | A separately authorized ownership transition changes the artifact's owner. | `relation.acts-for:forbidden:1` |
| unrestricted-authority | The actor is permitted every action/subject/scope in the independently owned universe, beyond the delegated subset. | `relation.acts-for:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Original and redelegated grant authenticity, complete ancestry, scope inclusion, owned gates and observed revocation require adapters and refinement.

**Review status.** An earlier scoped meaning receipt exists. It remains bound to its original definition; this expansion is presented for batch review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/acts-for.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K00-acts-for.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-instance | principal | agent-instance to principal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
