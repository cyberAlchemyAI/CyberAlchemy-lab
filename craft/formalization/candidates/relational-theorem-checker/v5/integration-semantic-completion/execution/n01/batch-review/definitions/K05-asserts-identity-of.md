# K05 — asserts-identity-of

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded bounded assertion**.

**Meaning in plain language.** An identity assertion records a correspondence claim in a specified scope. Recording the claim neither merges identities nor reveals private attributes.

**Question answered.** What bounded identity correspondence is being asserted between these endpoints?

**Formal definition.**

```text
Meaning_K05(W,e,f) := ∃ w ∈ W.IdentityAssertion. Base_K05(W,e,f,w) ∧ (w.assertor = s ∧ w.correspondent = t ∧ w.assertionKind = code(q.assertion_kind) ∧ w.scope = resolve(q.claim_scope) ∧ w.claim.correspondence = (s,t,w.assertionKind,w.scope))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a IdentityAssertion record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `assertor` | Identity Claim, Person Reference or Principal Reference revision |
| `correspondent` | Person, Person Reference or Principal revision |
| `assertionKind` | owned correspondence claim constructor |
| `scope` | bounded correspondence claim scope |
| `claim` | recorded assertion with exact participants and provenance |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `assertion_kind` | `w.assertionKind` | bounded correspondence claim constructor for this exact pair |
| `claim_scope` | `w.scope` | bounded domain of this asserted correspondence, with privacy restrictions |

**Operational behavior.** Record the bounded correspondence claim; leave identity classes, authority grants and private attributes unchanged.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Record A claims an external identifier correspondence with B while their governed identity classes remain distinct.

**Insufficient case.** A changed assertion scope is a different claim and cannot reuse the old assertion witness.

**Useful correction.** Supply the assertion for these participants and scope; request a separate identity operation if merging is actually intended.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| identity-merge | A separately authorized identity operation merges two previously distinct identity classes. | `relation.asserts-identity-of:forbidden:0` |
| authority-transfer | A separately authorized transfer changes the authority holder for this envelope. | `relation.asserts-identity-of:forbidden:1` |
| private-attribute-inference | Independent admissible provenance establishes a private attribute value; identity assertion alone does not. | `relation.asserts-identity-of:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Each of the four permitted pairs needs its own assertion constructor and privacy boundary; no asserted identifier is an authenticated equivalence.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/asserts-identity-of.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K05-asserts-identity-of.json)

**Exact ordered pairs (4).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| identity-claim | person-reference | identity-claim to person-reference: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| person-reference | person | person-reference to person: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| person-reference | person-reference | person-reference to person-reference: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| principal-reference | principal | principal-reference to principal: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
