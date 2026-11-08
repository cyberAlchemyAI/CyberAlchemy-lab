K22 — relation.has-capability

Status: candidate meaning; actual owner assessment pending.

Source question: Which Agent Capability is declared for this Agent Profile or Agent Instance?

Source effect: Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

Proposed claim tier: recorded declaration.

Independent witness type: `CapabilityDeclaration`.

The exact source declaration and its ordered pairs are bound by [the definition contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/definitions/K22-has-capability.json).

**Independent meaning constraints**

- Exact kind/source definition and approved meaning revision.
- Exact source/target node kinds and revisions match one declared ordered pair.
- Every required qualifier has its independently defined typed interpretation; closed qualifier object has no extra field.
- Primary witness, subject, target, context, scope, source snapshot, epoch and time domain agree with the complete frame.
- The selected evidence and provenance policy establishes the claimed recorded/as-of/executed/observed posture; missing authenticity is not manufactured.
- w.agentProfileOrInstance = s and w.capability = t = capability_version_ref.
- declaration_basis resolves an owned source declaration for s/t; it is separate from performance and authority evidence.

**Qualifiers**

| Field | Proposed type | Exact role |
|---|---|---|
| capability_version_ref | ExactRevisionRef | target.revision: exact declared target revision, with target kind and owner preserved |
| declaration_basis | DeclarationBasis | record.basis: exact source profile/instance and target capability declaration |

**Effect**

Record the exact declared capability without claiming permission or successful performance.

Append one exact immutable witnessed relation record, or idempotently retain an identical existing revision; same revision with different content is refused.

A record append does not implement its source witness's execution. Materialization requires evidence of a completed authorized atomic application; no standalone relation row proves it.

**Worked positive model**

Agent Profile P declares Capability C while its instance has not successfully performed C.

This is a candidate model blueprint. No actual approval or execution is established by the example.

**Worked refusal**

A capability declaration for another profile cannot establish this instance's declaration basis.

**Exact excluded conclusions**

- `relation.has-capability:forbidden:0` — **authority**: An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. Participants: the explicitly joined accountable holder/source participant and this frame's exact scope; additional operation/boundary/grant witnesses range over the owner-resolved catalog.
- `relation.has-capability:forbidden:1` — **successful-performance**: Admissible performance evidence passes the exact capability's owned criteria. Participants: the exact endpoint or output/action explicitly joined by this relation's primary witness; specification, decision, environment and execution are separate exact owned references.
- `relation.has-capability:forbidden:2` — **product-value**: An admissible valuation assessment establishes product value under its explicit metric and baseline. Participants: exact source/target participants and primary-witness roles in this kind's definition; extra criterion/policy/record witnesses range over the independent owned catalog in this frame.

Each exclusion needs a checked valid countermodel. The excluded property can still hold through independent evidence; the local relation does not decide its universal falsity.

Required source refinement: Under exact owned catalog/frame well-formedness, decoding and resolution of raw source fields yields a iff the independently specified source constraints denote Meaning_K22(W,a). The decoder/checker must not define that source predicate.

Required proofs:

- Prove the independent meaning has a valid positive model.
- Prove each exact qualifier mapping and checker/meaning equivalence.
- Prove declared record effect and any required execution/closure preservation.
- Check each kind-scoped non-entailment countermodel under the complete pinned theory.
- Account for all declared ordered pairs and prove role-sensitive branches; one positive example per kind is insufficient.

Inherited pending IDs: 6; ordered endpoint branches: 2.

Policy decisions: D01/D04/D07 common catalog and provenance rules.
