# K38 — uses-method

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded method dependency/use**.

**Meaning in plain language.** A subject records a dependency on or employment of a method specification. That dependency need not mean an implementation has run successfully.

**Question answered.** Which Method does this subject depend on or employ?

**Formal definition.**

```text
Meaning_K38(W,e,f) := ∃ w ∈ W.MethodUse. Base_K38(W,e,f,w) ∧ (w.subject = s ∧ w.method = t ∧ w.role = code(q.usage_role) ∧ w.constructor ∈ {methodDependency,methodEmployment} ∧ w.record.method = t ∧ w.record.subject = s)
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a MethodUse record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `subject` | exact method-dependent activity/product/project/measurement revision |
| `method` | Method specification exact revision |
| `role` | owned dependency/employment role |
| `constructor` | methodDependency or methodEmployment |
| `record` | attributable dependency/use declaration |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `usage_role` | `w.role` | owned method dependency/employment constructor, preserving specification/implementation distinction |

**Operational behavior.** Record the method dependency/use posture without conformance, realization, validation or achievement.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Subject S depends on Method M but has not executed or validated an implementation of M.

**Insufficient case.** An implementation identifier cannot replace the exact method revision.

**Useful correction.** Resolve the method specification revision and the declared dependency/employment role; do not substitute an implementation identifier.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| conformance | An admissible exact conformance assessment establishes every applicable target criterion in scope. | `relation.uses-method:forbidden:0` |
| realization | An independent instantiation/execution witness establishes concrete realization, beyond declared contribution or method use. | `relation.uses-method:forbidden:1` |
| validation | A completed admissible validator establishes the subject's exact independent specification. | `relation.uses-method:forbidden:2` |
| achievement | Every owned success criterion of the objective has admissible exact support. | `relation.uses-method:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Seven source branches and the migrated Method carrier need exact adapters. Actual execution postures must be witnessed separately from declared dependency.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/uses-method.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K38-uses-method.json)

**Exact ordered pairs (7).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-action | method | agent-action method specification dependency/employment record; method identity is separate from implementation |
| experiment-run | method | experiment-run method specification dependency/employment record; method identity is separate from implementation |
| measurement-result | method | measurement-result method specification dependency/employment record; method identity is separate from implementation |
| observation | method | observation method specification dependency/employment record; method identity is separate from implementation |
| product | method | product method specification dependency/employment record; method identity is separate from implementation |
| project | method | project method specification dependency/employment record; method identity is separate from implementation |
| research-run | method | research-run method specification dependency/employment record; method identity is separate from implementation |
