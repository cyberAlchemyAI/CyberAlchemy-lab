# K35 — scopes-authority-over

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded authority boundary**.

**Meaning in plain language.** An authority claim or boundary declares its scope over a decision scope or role assignment. Recording a boundary does not authenticate a claim or issue a grant.

**Question answered.** What governed scope is bounded by this explicit Authority Claim or Authority Boundary?

**Formal definition.**

```text
Meaning_K35(W,e,f) := ∃ w ∈ W.AuthorityScopeDeclaration. Base_K35(W,e,f,w) ∧ (w.declarer = s ∧ w.subject = t ∧ w.role = code(q.authority_role) ∧ w.scope = resolve(q.scope_ref) ∧ ScopeDeclared(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a AuthorityScopeDeclaration record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `declarer` | Authority Claim or Authority Boundary exact revision |
| `subject` | Decision Scope or Role Assignment exact revision |
| `role` | owned declared boundary role |
| `scope` | explicit owned declared authority scope |
| `declaration` | boundary declaration; not an authenticated grant |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`ScopeDeclared`: The exact boundary declaration joins declarer and subject; its owned scope includes the named subject in the declared role. Authentication, effective permission and execution are independent catalogs, never synthesized from this declaration.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `authority_role` | `w.role` | declared claim/boundary role over this decision scope or role assignment |
| `scope_ref` | `w.scope` | explicit owned declared authority scope; inclusion is not permission |

**Operational behavior.** Record the bounded authority declaration without granting permission, authenticating the claim or executing an effect.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Unverified Claim C declares scope over S; no authenticated grant or execution exists.

**Insufficient case.** A claimed wider scope cannot replace the exact owner-recorded scope definition.

**Useful correction.** Resolve the declared boundary for this subject and scope; establish authentication and permission through separate records.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| permission-grant | A distinct authorized grant creates this permission, beyond an authority-scope declaration. | `relation.scopes-authority-over:forbidden:0` |
| claim-authentication | The provenance/authentication boundary verifies the claim's exact issuer and content. | `relation.scopes-authority-over:forbidden:1` |
| effect-execution | A verified completed transaction applies this declared effect to the exact target. | `relation.scopes-authority-over:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Three branches need scope interpretation. Scope declaration must not reuse effective authority as its antecedent and become a grant-producing definition.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/scopes-authority-over.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K35-scopes-authority-over.json)

**Exact ordered pairs (3).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| authority-boundary | decision-scope | authority-boundary declared authority boundary over decision-scope; explicit scope inclusion is separate from a grant |
| authority-claim | decision-scope | authority-claim declared authority boundary over decision-scope; explicit scope inclusion is separate from a grant |
| authority-claim | role-assignment | authority-claim declared authority boundary over role-assignment; explicit scope inclusion is separate from a grant |
