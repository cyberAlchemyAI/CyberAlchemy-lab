K27 — relation.occurs-during

Status: candidate meaning; actual owner assessment pending.

Source question: In which exact execution envelope did this Failure Occurrence happen?

Source effect: Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

Proposed claim tier: recorded temporal attribution.

Independent witness type: `OccurrenceEnvelope`.

The exact source declaration and its ordered pairs are bound by [the definition contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/definitions/K27-occurs-during.json).

**Independent meaning constraints**

- Exact kind/source definition and approved meaning revision.
- Exact source/target node kinds and revisions match one declared ordered pair.
- Every required qualifier has its independently defined typed interpretation; closed qualifier object has no extra field.
- Primary witness, subject, target, context, scope, source snapshot, epoch and time domain agree with the complete frame.
- The selected evidence and provenance policy establishes the claimed recorded/as-of/executed/observed posture; missing authenticity is not manufactured.
- occurrence = s and envelope = t = envelope_version_ref.
- The observed occurrence event belongs to the exact execution envelope under the owned temporal_scope and time domain.

**Qualifiers**

| Field | Proposed type | Exact role |
|---|---|---|
| envelope_version_ref | ExactRevisionRef | target.revision: exact declared target revision, with target kind and owner preserved |
| temporal_scope | OwnedScope | record.scope: owned exact scope of this named connection; inclusion/temporal interpretation is kind-specific |

**Effect**

Record occurrence within the exact envelope without establishing cause, blame, severity or recovery.

Append one exact immutable witnessed relation record, or idempotently retain an identical existing revision; same revision with different content is refused.

A record append does not implement its source witness's execution. Materialization requires evidence of a completed authorized atomic application; no standalone relation row proves it.

**Worked positive model**

Occurrence F is recorded inside Session S; no causal or recovery assessment has been made.

This is a candidate model blueprint. No actual approval or execution is established by the example.

**Worked refusal**

An event in a different time domain cannot be inserted by comparing raw epoch numbers.

**Exact excluded conclusions**

- `relation.occurs-during:forbidden:0` — **cause**: The owned causal model supports a counterfactual/intervention dependence, beyond observation or temporal association. Participants: the exact affected/occurred/responded-to failure subject joined by the primary witness; causal/severity/recovery policies and assessments are independently owned.
- `relation.occurs-during:forbidden:1` — **blame**: An independently justified responsibility assessment attributes fault, beyond temporal occurrence or impact. Participants: the exact affected/occurred/responded-to failure subject joined by the primary witness; causal/severity/recovery policies and assessments are independently owned.
- `relation.occurs-during:forbidden:2` — **severity**: A distinct admissible severity assessment assigns a grade under the owned severity policy. Participants: the exact affected/occurred/responded-to failure subject joined by the primary witness; causal/severity/recovery policies and assessments are independently owned.
- `relation.occurs-during:forbidden:3` — **recovery**: An admissible recovery assessment establishes restoration against every owned recovery criterion. Participants: the exact affected/occurred/responded-to failure subject joined by the primary witness; causal/severity/recovery policies and assessments are independently owned.

Each exclusion needs a checked valid countermodel. The excluded property can still hold through independent evidence; the local relation does not decide its universal falsity.

Required source refinement: Under exact owned catalog/frame well-formedness, decoding and resolution of raw source fields yields a iff the independently specified source constraints denote Meaning_K27(W,a). The decoder/checker must not define that source predicate.

Required proofs:

- Prove the independent meaning has a valid positive model.
- Prove each exact qualifier mapping and checker/meaning equivalence.
- Prove declared record effect and any required execution/closure preservation.
- Check each kind-scoped non-entailment countermodel under the complete pinned theory.
- Account for all declared ordered pairs and prove role-sensitive branches; one positive example per kind is insufficient.

Inherited pending IDs: 7; ordered endpoint branches: 5.

Policy decisions: D02, D07.
