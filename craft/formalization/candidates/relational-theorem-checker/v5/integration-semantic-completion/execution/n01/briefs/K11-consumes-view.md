K11 — relation.consumes-view

Status: candidate meaning; actual owner assessment pending.

Source question: Which immutable Context View or Ontology View did this Agent Session actually consume?

Source effect: Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

Proposed claim tier: recorded attributable consumption.

Independent witness type: `ViewConsumption`.

The exact source declaration and its ordered pairs are bound by [the definition contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/definitions/K11-consumes-view.json).

**Independent meaning constraints**

- Exact kind/source definition and approved meaning revision.
- Exact source/target node kinds and revisions match one declared ordered pair.
- Every required qualifier has its independently defined typed interpretation; closed qualifier object has no extra field.
- Primary witness, subject, target, context, scope, source snapshot, epoch and time domain agree with the complete frame.
- The selected evidence and provenance policy establishes the claimed recorded/as-of/executed/observed posture; missing authenticity is not manufactured.
- w.session = s and w.view = t; w.viewDigest matches the immutable view content.
- cursor denotes an exact position/extent in this view revision; consumption_purpose is an owned purpose code.
- An attributable consumption record establishes consumption; mere availability or request does not.

**Qualifiers**

| Field | Proposed type | Exact role |
|---|---|---|
| view_digest | ViewContentCommitment | record.viewContent: digest of exact target immutable View bytes |
| cursor | ViewCursor | record.cursor: position/extent inside exact target view; not an epoch |
| consumption_purpose | OwnedPostureCode | record.consumption_purpose: exact relation-specific owned role/posture/purpose code, interpreted for this ordered endpoint pair |

**Effect**

Record session consumption of the exact immutable view and extent; preserve source currentness, ownership and request status.

Append one exact immutable witnessed relation record, or idempotently retain an identical existing revision; same revision with different content is refused.

A record append does not implement its source witness's execution. Materialization requires evidence of a completed authorized atomic application; no standalone relation row proves it.

**Worked positive model**

Session S consumes an immutable View V; a source changes afterward and V no longer satisfies a fresh request.

This is a candidate model blueprint. No actual approval or execution is established by the example.

**Worked refusal**

A cursor from a different view digest cannot prove this consumption.

**Exact excluded conclusions**

- `relation.consumes-view:forbidden:0` — **currentness**: A current source observation at now still selects this source revision; historical as-of agreement is insufficient. Participants: each exact included source of the consumed/fulfilling view (or target framed source), at a separately observed now in the same time domain.
- `relation.consumes-view:forbidden:1` — **source-authority**: A separately governed authority boundary recognizes the source's authority, beyond context framing or view consumption. Participants: the explicitly joined accountable holder/source participant and this frame's exact scope; additional operation/boundary/grant witnesses range over the owner-resolved catalog.
- `relation.consumes-view:forbidden:2` — **memory-ownership**: A distinct ownership record assigns the memory artifact to the holder; consuming a view is not ownership. Participants: source/target or exact produced/consumed artifact from the primary witness; owner/attribute/provenance comes from the independent catalog, not a relation label.
- `relation.consumes-view:forbidden:3` — **request-fulfillment**: The exact immutable view satisfies every owned request criterion in the request/resolution frame. Participants: exact source/target participants and primary-witness roles in this kind's definition; extra criterion/policy/record witnesses range over the independent owned catalog in this frame.

Each exclusion needs a checked valid countermodel. The excluded property can still hold through independent evidence; the local relation does not decide its universal falsity.

Required source refinement: Under exact owned catalog/frame well-formedness, decoding and resolution of raw source fields yields a iff the independently specified source constraints denote Meaning_K11(W,a). The decoder/checker must not define that source predicate.

Required proofs:

- Prove the independent meaning has a valid positive model.
- Prove each exact qualifier mapping and checker/meaning equivalence.
- Prove declared record effect and any required execution/closure preservation.
- Check each kind-scoped non-entailment countermodel under the complete pinned theory.
- Account for all declared ordered pairs and prove role-sensitive branches; one positive example per kind is insufficient.

Inherited pending IDs: 8; ordered endpoint branches: 2.

Policy decisions: D07.
