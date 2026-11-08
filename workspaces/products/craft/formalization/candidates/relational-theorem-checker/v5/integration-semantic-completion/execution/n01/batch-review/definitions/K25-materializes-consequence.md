# K25 — materializes-consequence

**Proposed revision:** `v5-batch-definitions-2026-10-11-1`. Claim tier: **checked local atomic execution**.

**Meaning in plain language.** A verified local transaction already applied an authorized deterministic consequence atomically. The relation records that application and cannot add new authorization.

**Question answered.** Which declared deterministic consequence did this Admission Transaction materialize?

**Formal definition.**

```text
Meaning_K25(W,e,f) := f.profile = typedSuccessor ∧ ∃ w ∈ W.AuthorizedMaterialization. Base_K25(W,e,f,w) ∧ (w.transaction = s ∧ w.output = t ∧ w.receipt = receiptValue(q.application_receipt_ref) ∧ w.role = roleValue(q.consequence_role) ∧ hash(bytes(W,t)) = q.output_digest ∧ AppliedAuthorizedBundle(W,w,f))
```

Base requires exact selected kind/meaning revision; membership of this ordered pair in the pinned signature; independently captured endpoint revisions; exactly the declared qualifier fields with unique typed catalog interpretation; primary witness source/target joins and frame agreement; and provenance sufficient for the declared claim tier. It never invokes the relation checker. Undefined resolution cannot establish Meaning.

**Notation and independent witness.** `s` is the source revision, `t` the target revision, `q` the closed qualifier object, `f` the complete exact frame and `W` the independently supplied semantic world. `w` is a AuthorizedMaterialization record in W. None is inferred from a successful checker result.

| Witness field | Meaning |
|---|---|
| `transaction` | Admission Transaction exact revision |
| `output` | exact generated output, project state or event history revision |
| `receipt` | completed local atomic application receipt |
| `role` | selected consequence role in the approved bundle |
| `bundle` | exact previously authorized complete bundle |
| `before` | prior local state |
| `after` | actual final local state |
| `generator` | pinned deterministic generator |

`bytes`: The exact immutable resolved content bytes under the frame byte representation; source authenticity is a separately stated assumption.

`hash`: The pinned content-commitment algorithm applied to those exact bytes. Equality is checked under the named byte/hash assumptions and is not an authenticity or semantic-correctness theorem.

`receiptValue`: Profile-indexed exact application-receipt interpretation. The legacy F0 literal predicate remains separate from a successor resolved applied-receipt record.

`roleValue`: Profile-indexed exact consequence-role interpretation. The selected consequence must belong to the approved bundle, not an arbitrary role label.

`AppliedAuthorizedBundle`: A verified local execution record binds transaction, complete already-authorized bundle, prior state, pinned deterministic generator and final state. All and only declared consequences apply atomically; the named output bytes/digest occur in the final state. No authority root, external action or runtime activation outside the approved envelope is introduced. A self-reported applied flag is insufficient.

**Qualifiers.** All listed fields are required; additional fields are refused. Raw source strings require an exact owned mapping.

| Field | Independent role | Interpretation |
|---|---|---|
| `application_receipt_ref` | `w.receipt` | F0 literal or separately resolved verified applied atomic receipt |
| `consequence_role` | `w.role` | selected deterministic consequence role in the exact approved bundle |
| `output_digest` | `hash(bytes(W,w.output))` | exact final consequence bytes commitment under the selected profile |

**Operational behavior.** Record the already completed authorized materialization; preserve authorized effect boundaries, semantic correctness claims and zero runtime/external activation.

R_after = R_before ∪ {exactRecord(e,w,f)} for a new row; identical retry leaves R unchanged; same record identity with different content refuses atomically.

W_after = W_before; appending the relation log alone does not execute its witness, change authority roots or replace active artifacts.

**Worked example.** A checked local transaction materializes a generated index from its approved bundle; the index may still encode a semantically wrong definition.

**Insufficient case.** A planned transaction with a fabricated receipt label cannot count as applied.

**Useful correction.** Provide the complete applied bundle, prior/final state and output digest from a verified local execution; a planned receipt is insufficient.

**Conclusions requiring separate evidence.** The following propositions have independent definitions. The relation alone is proposed not to entail them; that does not mean they are always false.

| Conclusion | Independent definition | Original obligation |
|---|---|---|
| new-authorization | The operation adds an authorization root not present in the already approved input envelope. | `relation.materializes-consequence:forbidden:0` |
| semantic-correctness | A checked independent semantic specification establishes the output's intended correctness, beyond deterministic generation. | `relation.materializes-consequence:forbidden:1` |
| runtime-activation | An actual permitted activation starts the implementation in the named environment. | `relation.materializes-consequence:forbidden:2` |
| external-effect | An authenticated external observation establishes an effect outside the local repository state. | `relation.materializes-consequence:forbidden:3` |

**Theorems to establish.** Satisfiability of this independent meaning; soundness and completeness of the checker under independently justified input assumptions; each exact qualifier mapping; the record effect and composed preservation; a valid full-theory countermodel for each listed non-entailment; refinement for every declared ordered pair.

**Source and implementation gap.** Four consequence constructors need execution provenance and atomicity proofs. Existing F0 literal receipt/role/digest meanings must retain their own profile.

**Review status.** This meaning has no actual owner assessment yet. It is ready for the final consolidated review.

[Original source](/home/vlad_/projects/CyberAlchemy-lab/authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds/materializes-consequence.json) · [Machine-readable definition](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/execution/n01/batch-review/definitions/K25-materializes-consequence.json)

**Exact ordered pairs (4).** These branches are specified, not proved.

| Source kind | Target kind | Interpretation |
|---|---|---|
| admission-transaction | generated-output | approved deterministic generated-output consequence in a verified applied Admission Transaction; final-state commitment |
| admission-transaction | project-governance-event-history | approved deterministic project-governance-event-history consequence in a verified applied Admission Transaction; final-state commitment |
| admission-transaction | project-semantic-event-history | approved deterministic project-semantic-event-history consequence in a verified applied Admission Transaction; final-state commitment |
| admission-transaction | project-state | approved deterministic project-state consequence in a verified applied Admission Transaction; final-state commitment |

**Legacy profile boundary.** Exact original literal-token/accepted-assessment predicate. An accepted flag or nonempty literal remains supplied graph data; it is not authenticated source truth or actual application.

`LegacyQualified_k(g,e) := e.kind = k ∧ Relational.InstanceValid(g,e)`

Preserve legacy acceptance in its separately named/profile-indexed API. Do not rename LegacyQualified as the stronger Meaning, or infer typed-successor evidence, enum restrictions, execution or criteria completion from legacy acceptance.

