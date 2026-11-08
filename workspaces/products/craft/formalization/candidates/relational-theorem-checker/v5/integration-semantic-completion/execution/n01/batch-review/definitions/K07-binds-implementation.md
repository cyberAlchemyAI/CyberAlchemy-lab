# K07 — binds-implementation

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded model binding**.

**Meaning in plain language.** An implementation declares a binding to an ontology or schema. Binding identifies what it implements, while conformance and performance are assessed separately.

**Question answered.** Which Ontology or Schema does this implementation bind?

**Formal definition.**

```text
Meaning_K07(W,e,f) := ∃ w ∈ W.ImplementationBinding. Base_K07(W,e,f,w) ∧ (w.implementation = s ∧ w.model = t ∧ w.role = code(q.binding_role) ∧ ((kind(t)=schema ∧ w.constructor=schemaBinding) ∨ (kind(t)=ontology ∧ w.constructor=ontologyBinding)))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ImplementationBinding record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `implementation` | Implementation exact revision |
| `model` | Schema or Ontology exact revision |
| `role` | owned binding role |
| `constructor` | schemaBinding or ontologyBinding with exact model reference |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`kind`: The independently captured governed artifact kind of an exact reference. Camel-case constructor names in formulas denote the corresponding hyphenated source kinds listed in the signature matrix.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `binding_role` | `w.role` | schema-binding or ontology-binding role as determined by target kind |

**Operational behavior.** Record implementation-to-model binding without executing the implementation or admitting either endpoint.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Implementation I binds Schema S while one conformance case still fails.

**Insufficient case.** An ontology binding cannot silently substitute for a schema binding with different endpoints.

**Useful correction.** Use a schema-binding witness for a schema target and an ontology-binding witness for an ontology target.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| conformance | An admissible exact conformance assessment establishes every applicable target criterion in scope. | `relation.binds-implementation:forbidden:0` |
| runtime-effectiveness | An admissible runtime outcome assessment passes the owned effectiveness criteria. | `relation.binds-implementation:forbidden:1` |
| admission | An already authorized atomic transaction placed an endpoint in the admitted state. | `relation.binds-implementation:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Source-to-model binding fields and owned role catalogs require refinement; a binding must not reuse conformance evidence as its definition.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/binds-implementation.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K07-binds-implementation.json)

**Exact ordered pairs (2).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| implementation | ontology | ontology-binding constructor; implementation.model must resolve this ontology revision |
| implementation | schema | schema-binding constructor; implementation.model must resolve this schema revision |
