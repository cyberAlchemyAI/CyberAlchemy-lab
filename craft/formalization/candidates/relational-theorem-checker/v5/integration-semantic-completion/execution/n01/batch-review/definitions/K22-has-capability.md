# K22 — has-capability

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded declaration**.

**Meaning in plain language.** A profile or instance declares a particular capability under an owned basis. Capability declaration does not confer authority or prove successful performance.

**Question answered.** Which Agent Capability is declared for this Agent Profile or Agent Instance?

**Formal definition.**

```text
Meaning_K22(W,e,f) := ∃ w ∈ W.CapabilityDeclaration. Base_K22(W,e,f,w) ∧ (w.agent = s ∧ w.capability = t ∧ t = resolve(q.capability_version_ref) ∧ w.basis = resolve(q.declaration_basis) ∧ w.basis.agent = s ∧ w.basis.capability = t ∧ w.basis.constructor = ownedCapabilityDeclaration)
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a CapabilityDeclaration record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `agent` | Agent Profile or Agent Instance exact revision |
| `capability` | Agent Capability exact revision |
| `basis` | owned capability declaration with exact agent/capability joins |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `capability_version_ref` | `w.capability` | exact Agent Capability revision |
| `declaration_basis` | `w.basis` | owned exact profile/instance capability declaration; no implicit profile propagation |

**Operational behavior.** Record the exact declared capability without claiming permission or successful performance.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Agent Profile P declares Capability C while its instance has not successfully performed C.

**Insufficient case.** A capability declaration for another profile cannot establish this instance's declaration basis.

**Useful correction.** Use the declaration for this profile or instance and capability revision; do not substitute a successful action trace for a declaration.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| authority | An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. | `relation.has-capability:forbidden:0` |
| successful-performance | Admissible performance evidence passes the exact capability's owned criteria. | `relation.has-capability:forbidden:1` |
| product-value | An admissible valuation assessment establishes product value under its explicit metric and baseline. | `relation.has-capability:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Instance derivation from a profile needs an explicit reviewed bridge. Profile declarations do not automatically authorize or equip every instance.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/has-capability.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K22-has-capability.json)

**Exact ordered pairs (2).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-instance | agent-capability | agent-instance to agent-capability: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| agent-profile | agent-capability | agent-profile to agent-capability: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
