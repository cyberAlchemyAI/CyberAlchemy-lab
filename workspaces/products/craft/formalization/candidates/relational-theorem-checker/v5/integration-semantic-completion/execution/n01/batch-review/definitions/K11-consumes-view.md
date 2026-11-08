# K11 — consumes-view

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **recorded attributable consumption**.

**Meaning in plain language.** A session consumed an immutable view to an exact position or extent. Consumption is historical and does not establish that its sources are still current.

**Question answered.** Which immutable Context View or Ontology View did this Agent Session actually consume?

**Formal definition.**

```text
Meaning_K11(W,e,f) := ∃ w ∈ W.ViewConsumption. Base_K11(W,e,f,w) ∧ (w.session = s ∧ w.view = t ∧ hash(bytes(W,t)) = q.view_digest ∧ w.cursor = cursorValue(q.cursor,t,q.view_digest) ∧ w.purpose = code(q.consumption_purpose) ∧ ConsumptionObserved(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a ViewConsumption record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `session` | Agent Session exact revision |
| `view` | Context View or Ontology View exact revision |
| `cursor` | view-specific bounded position or extent |
| `purpose` | owned consumption-purpose code |
| `receipt` | attributable observation of consumption |

`code`: The unique entry in the owner-reviewed code catalog indexed by relation kind, exact ordered pair, field and catalog revision. Its semantic constructor and record role must agree; identical spellings in another catalog are distinct.

`bytes`: The exact immutable resolved content bytes under the frame byte representation; source authenticity is a separately stated assumption.

`hash`: The pinned content-commitment algorithm applied to those exact bytes. Equality is checked under the named byte/hash assumptions and is not an authenticity or semantic-correctness theorem.

`cursorValue`: The unique owner-resolved cursor interpretation in this exact view revision and digest. Its positions or extent lie within the view-specific bounds; it is neither a source epoch nor a cursor from another view.

`ConsumptionObserved`: An admissible attributable consumption record joins this session, view bytes, extent and purpose at the recorded epoch. Availability, a request, or a generated view alone do not establish consumption.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `view_digest` | `hash(bytes(W,w.view))` | exact consumed view content commitment |
| `cursor` | `w.cursor` | bounded position/extent within that exact view revision and digest |
| `consumption_purpose` | `w.purpose` | owned session consumption purpose, separate from request fulfillment |

**Operational behavior.** Record session consumption of the exact immutable view and extent; preserve source currentness, ownership and request status.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** Session S consumes an immutable View V; a source changes afterward and V no longer satisfies a fresh request.

**Insufficient case.** A cursor from a different view digest cannot prove this consumption.

**Useful correction.** Use a cursor from the same view revision and digest, and attach an attributable consumption receipt.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| currentness | A current source observation at now still selects this source revision; historical as-of agreement is insufficient. | `relation.consumes-view:forbidden:0` |
| source-authority | A separately governed authority boundary recognizes the source's authority, beyond context framing or view consumption. | `relation.consumes-view:forbidden:1` |
| memory-ownership | A distinct ownership record assigns the memory artifact to the holder; consuming a view is not ownership. | `relation.consumes-view:forbidden:2` |
| request-fulfillment | The exact immutable view satisfies every owned request criterion in the request/resolution frame. | `relation.consumes-view:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Context and ontology views use different extent models; digest framing, cursor bounds, provenance and session attribution require adapters.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/consumes-view.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K11-consumes-view.json)

**Exact ordered pairs (2).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| agent-session | context-view | context-view content commitment and its own cursor/extent interpretation; session consumption receipt |
| agent-session | ontology-view | ontology-view content commitment and its own cursor/extent interpretation; session consumption receipt |
