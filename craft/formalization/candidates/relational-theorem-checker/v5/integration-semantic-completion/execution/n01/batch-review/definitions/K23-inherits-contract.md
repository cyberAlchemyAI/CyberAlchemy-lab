# K23 — inherits-contract

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **checked obligation inheritance**.

**Meaning in plain language.** An instance inherits identified contract obligations, retaining where they came from. Inheritance does not establish that the obligations are satisfied.

**Question answered.** Which exact contract obligations are inherited by this instance?

**Formal definition.**

```text
Meaning_K23(W,e,f) := ∃ w ∈ W.ContractInheritance. Base_K23(W,e,f,w) ∧ (w.instance = s ∧ w.contract = t ∧ t = resolve(q.contract_version_ref) ∧ w.binding = resolve(q.binding_ref) ∧ w.binding.instance = s ∧ w.binding.contract = t ∧ InheritedOrigins(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ContractInheritance record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `instance` | Capability Instance exact revision |
| `contract` | Contract exact revision |
| `binding` | owned instance/contract inheritance binding |
| `origins` | norm records keyed by subject, contract, norm and binding revision |
| `conditions` | owned condition expressions determining active or potential status |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`InheritedOrigins`: Every contract obligation selected by the complete owned inheritance derivation appears with its subject/contract/norm/binding origin. E00 yes activates, no makes inactive, unknown makes potential; conflicts are retained rather than resolved by dropping an origin.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `binding_ref` | `w.binding` | exact instance/contract inheritance binding with complete obligation origins |
| `contract_version_ref` | `w.contract` | exact inherited Contract revision |

**Operational behavior.** Record inherited obligation origins and potential/active status; preserve ownership and conformance as separate claims.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Instance I inherits Contract C's active obligation but does not yet conform to it.

**Insufficient case.** An unknown activation condition cannot produce an active obligation.

**Useful correction.** Use the exact inheritance binding and retain every applicable norm origin; report unknown activation as potential rather than satisfied.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| ownership-transfer | A separately authorized ownership transition changes the artifact's owner. | `relation.inherits-contract:forbidden:0` |
| conformance | An admissible exact conformance assessment establishes every applicable target criterion in scope. | `relation.inherits-contract:forbidden:1` |
| adoption | An actual selected adoption decision applies to the endpoint, separately from admission and authorization. | `relation.inherits-contract:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Complete contract norm extraction, conditional activation, overrides and conflict handling need E00/E04 adapters; an AST result is not an authority grant.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/inherits-contract.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K23-inherits-contract.json)

**Exact ordered pairs (1).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| capability-instance | contract | capability-instance to contract: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
