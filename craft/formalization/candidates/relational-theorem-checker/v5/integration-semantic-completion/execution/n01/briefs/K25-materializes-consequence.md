K25 — relation.materializes-consequence

Status: candidate meaning; actual owner assessment pending.

Source question: Which declared deterministic consequence did this Admission Transaction materialize?

Source effect: Records a deterministic output created while atomically applying an already authorized Decision Bundle; it grants no additional authority and proves no semantic correctness.

Proposed claim tier: checked local atomic execution.

Independent witness type: `AuthorizedMaterialization`.

The exact source declaration and its ordered pairs are bound by [the definition contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/definitions/K25-materializes-consequence.json).

**Independent meaning constraints**

- Exact kind/source definition and approved meaning revision.
- Exact source/target node kinds and revisions match one declared ordered pair.
- Every required qualifier has its independently defined typed interpretation; closed qualifier object has no extra field.
- Primary witness, subject, target, context, scope, source snapshot, epoch and time domain agree with the complete frame.
- The selected evidence and provenance policy establishes the claimed recorded/as-of/executed/observed posture; missing authenticity is not manufactured.
- transaction = s; its applied receipt identifies deterministic consequence t and final output_digest.
- The independently verified transaction consumed the exact already-authorized bundle, prior input state and declared deterministic generator.
- The whole bundle applied atomically; no undeclared target, effect, authority root or external action was added.
- Receipt consistency alone is insufficient: the local execution/state-transition provenance must establish actual application.

**Qualifiers**

| Field | Proposed type | Exact role |
|---|---|---|
| application_receipt_ref | LegacyF0LiteralMeaning | record.receipt: source transaction, prior authorized bundle, target final output and atomic application |
| consequence_role | LegacyF0LiteralMeaning | record.consequence_role: exact relation-specific owned role/posture/purpose code, interpreted for this ordered endpoint pair |
| output_digest | LegacyF0LiteralMeaning | record.outputContent: final target consequence bytes, preserving legacy F0 meaning in its original profile |

**Effect**

Record the already completed authorized materialization; preserve authorized effect boundaries, semantic correctness claims and zero runtime/external activation.

Append one exact immutable witnessed relation record, or idempotently retain an identical existing revision; same revision with different content is refused.

A record append does not implement its source witness's execution. Materialization requires evidence of a completed authorized atomic application; no standalone relation row proves it.

**Worked positive model**

A checked local transaction materializes a generated index from its approved bundle; the index may still encode a semantically wrong definition.

This is a candidate model blueprint. No actual approval or execution is established by the example.

**Worked refusal**

A planned transaction with a fabricated receipt label cannot count as applied.

**Exact excluded conclusions**

- `relation.materializes-consequence:forbidden:0` — **new-authorization**: The operation adds an authorization root not present in the already approved input envelope. Participants: source transaction's before/after states and exact already-approved bundle envelope; a root outside that envelope.
- `relation.materializes-consequence:forbidden:1` — **semantic-correctness**: A checked independent semantic specification establishes the output's intended correctness, beyond deterministic generation. Participants: the exact endpoint or output/action explicitly joined by this relation's primary witness; specification, decision, environment and execution are separate exact owned references.
- `relation.materializes-consequence:forbidden:2` — **runtime-activation**: An actual permitted activation starts the implementation in the named environment. Participants: the exact endpoint or output/action explicitly joined by this relation's primary witness; specification, decision, environment and execution are separate exact owned references.
- `relation.materializes-consequence:forbidden:3` — **external-effect**: An authenticated external observation establishes an effect outside the local repository state. Participants: the exact endpoint or output/action explicitly joined by this relation's primary witness; specification, decision, environment and execution are separate exact owned references.

Each exclusion needs a checked valid countermodel. The excluded property can still hold through independent evidence; the local relation does not decide its universal falsity.

Required source refinement: Under exact owned catalog/frame well-formedness, decoding and resolution of raw source fields yields a iff the independently specified source constraints denote Meaning_K25(W,a). The decoder/checker must not define that source predicate.

Required proofs:

- Prove the independent meaning has a valid positive model.
- Prove each exact qualifier mapping and checker/meaning equivalence.
- Prove declared record effect and any required execution/closure preservation.
- Check each kind-scoped non-entailment countermodel under the complete pinned theory.
- Account for all declared ordered pairs and prove role-sensitive branches; one positive example per kind is insufficient.

Inherited pending IDs: 5; ordered endpoint branches: 4.

Policy decisions: D07, D08.
