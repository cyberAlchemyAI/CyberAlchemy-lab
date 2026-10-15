# K28 — originates-from

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded origin**.

**Meaning in plain language.** An origin declaration identifies where an identity or content came from. It does not establish a transformation or replacement.

**Question answered.** From which source did this identity or content originate?

**Formal definition.**

```text
Meaning_K28(W,e,f) := ∃ w ∈ W.OriginLineage. Base_K28(W,e,f,w) ∧ (w.derived = s ∧ w.origin = t ∧ w.role = code(q.origin_role) ∧ w.assertion.derived = s ∧ w.assertion.source = t ∧ w.assertion.role = w.role ∧ w.assertion.constructor = originDeclaration)
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a OriginLineage record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `derived` | exact identity/content artifact revision |
| `origin` | Source exact revision |
| `role` | owned origin role |
| `assertion` | exact origin declaration |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `origin_role` | `w.role` | owned identity/content origin declaration; separate from transformation or succession |

**Operational behavior.** Record origin lineage without implying derivation, succession or authority transfer.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Identity A originated from source O, with no transformation or predecessor replacement recorded.

**Insufficient case.** An origin statement cannot be substituted for an exact derivation witness.

**Useful correction.** Use an origin declaration joining these revisions; use a separate transformation or succession record for those stronger claims.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| derivation | A distinct exact transformation/compilation/projection record establishes derivation. | `relation.originates-from:forbidden:0` |
| successor | A distinct owned succession record establishes continuation/replacement; origin alone does not. | `relation.originates-from:forbidden:1` |
| authority-transfer | A separately authorized transfer changes the authority holder for this envelope. | `relation.originates-from:forbidden:2` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Seven source-origin projections require owned provenance interpretation. Origin and derivation records are not interchangeable.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/originates-from.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K28-originates-from.json)

**Exact ordered pairs (7).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| artifact-type | source | artifact-type to source: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| definition | source | definition to source: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| drift-assessment | source | drift-assessment to source: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| feedback-record | source | feedback-record to source: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| finding | source | finding to source: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| operational-observation | source | operational-observation to source: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
| relation-kind | source | relation-kind to source: the exact witness constructor and participant joins in this definition, with a pair-indexed owned qualifier catalog |
