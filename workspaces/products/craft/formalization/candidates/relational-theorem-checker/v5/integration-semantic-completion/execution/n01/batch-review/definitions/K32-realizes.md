# K32 — realizes

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded instantiated design/capability**.

**Meaning in plain language.** An implementation instantiates a product capability, or an experiment run executes its design. Each realization constructor needs evidence appropriate to that pair.

**Question answered.** Which declared design or capability is concretely instantiated by this subject?

**Formal definition.**

```text
Meaning_K32(W,e,f) := ∃ w ∈ W.Realization. Base_K32(W,e,f,w) ∧ (w.subject = s ∧ w.target = t ∧ t = resolve(q.exact_target_version_ref) ∧ w.role = code(q.realization_role) ∧ ((kind(s)=implementation ∧ w.constructor=implementedCapability) ∨ (kind(s)=experimentRun ∧ w.constructor=executedDesign)) ∧ RealizationObserved(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a Realization record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `subject` | Implementation or Experiment Run exact revision |
| `target` | Product Capability or Experiment Design exact revision |
| `role` | owned realization role |
| `constructor` | implementedCapability or executedDesign |
| `evidence` | exact implementation/instantiation or execution observation |

`resolve`: The unique entry for the raw token in the selected immutable typed reference catalog for this relation, pair, field and frame. Missing, ambiguous or wrong-kind entries are undefined and cannot establish Meaning.

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`kind`: The independently captured governed artifact kind of an exact reference. Camel-case constructor names in formulas denote the corresponding hyphenated source kinds listed in the signature matrix.

`RealizationObserved`: For implementedCapability, exact implementation/instantiation evidence connects subject and capability. For executedDesign, an attributable experiment execution connects run and design. The owned realization policy admits the evidence; neither branch requires conformance, benefit or hypothesis truth.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `realization_role` | `w.role` | implemented-capability or executed-design evidence constructor for the exact pair |
| `exact_target_version_ref` | `w.target` | exact realized capability/design revision |

**Operational behavior.** Record the evidenced realization constructor without inferring conformance, effectiveness, adoption or evidential support.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Implementation I concretely realizes Design D while I fails a conformance test.

**Insufficient case.** A declaration or binding alone cannot establish concrete realization.

**Useful correction.** Attach implementation evidence for the capability branch or attributable execution evidence for the design branch.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| conformance | An admissible exact conformance assessment establishes every applicable target criterion in scope. | `relation.realizes:forbidden:0` |
| effectiveness | An admissible outcome assessment establishes the owned effectiveness test. | `relation.realizes:forbidden:1` |
| adoption | An actual selected adoption decision applies to the endpoint, separately from admission and authorization. | `relation.realizes:forbidden:2` |
| support | An admissible supporting-polarity record exists; evaluation targeting, realization and test design cannot create one. | `relation.realizes:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** The two branches need different source and evidence bridges; a binds-implementation edge or experimental design declaration is insufficient.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/realizes.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K32-realizes.json)

**Exact ordered pairs (2).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| experiment-run | experiment-design | executedDesign constructor with experiment execution evidence |
| implementation | product-capability | implementedCapability constructor with implementation evidence |
