K33 — relation.requests-resolution-of

Status: candidate meaning; actual owner assessment pending.

Source question: Which exact Context version does this Context Request ask to resolve?

Source effect: Records a resolution request without performing resolution or mutating Context.

Proposed claim tier: recorded request.

Independent witness type: `ContextResolutionRequest`.

The exact source declaration and its ordered pairs are bound by [the definition contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/definitions/K33-requests-resolution-of.json).

**Independent meaning constraints**

- Exact kind/source definition and approved meaning revision.
- Exact source/target node kinds and revisions match one declared ordered pair.
- Every required qualifier has its independently defined typed interpretation; closed qualifier object has no extra field.
- Primary witness, subject, target, context, scope, source snapshot, epoch and time domain agree with the complete frame.
- The selected evidence and provenance policy establishes the claimed recorded/as-of/executed/observed posture; missing authenticity is not manufactured.
- request = s; request.context = t = context_version_ref; the owned request identifies consumers, selectors and bounded output constraints.

**Qualifiers**

| Field | Proposed type | Exact role |
|---|---|---|
| context_version_ref | ExactRevisionRef | target.revision: exact declared target revision, with target kind and owner preserved |

**Effect**

Record the resolution request without creating a resolved view or mutating Context.

Append one exact immutable witnessed relation record, or idempotently retain an identical existing revision; same revision with different content is refused.

A record append does not implement its source witness's execution. Materialization requires evidence of a completed authorized atomic application; no standalone relation row proves it.

**Worked positive model**

Request R names Context C@1 but no resolver has run and no view exists.

This is a candidate model blueprint. No actual approval or execution is established by the example.

**Worked refusal**

A request for C@2 cannot resolve or mutate C@1 by label matching.

**Exact excluded conclusions**

- `relation.requests-resolution-of:forbidden:0` — **resolution**: A completed owned resolution establishes all relevant target criteria, beyond inquiry intent or a context request. Participants: the exact Context revision named by the Context Request, its request and its independently verified before/after state.
- `relation.requests-resolution-of:forbidden:1` — **context-mutation**: A verified qualified state transition changes the durable Context revision, beyond a request/view record. Participants: the exact Context revision named by the Context Request, its request and its independently verified before/after state.
- `relation.requests-resolution-of:forbidden:2` — **source-authority**: A separately governed authority boundary recognizes the source's authority, beyond context framing or view consumption. Participants: the explicitly joined accountable holder/source participant and this frame's exact scope; additional operation/boundary/grant witnesses range over the owner-resolved catalog.

Each exclusion needs a checked valid countermodel. The excluded property can still hold through independent evidence; the local relation does not decide its universal falsity.

Required source refinement: Under exact owned catalog/frame well-formedness, decoding and resolution of raw source fields yields a iff the independently specified source constraints denote Meaning_K33(W,a). The decoder/checker must not define that source predicate.

Required proofs:

- Prove the independent meaning has a valid positive model.
- Prove each exact qualifier mapping and checker/meaning equivalence.
- Prove declared record effect and any required execution/closure preservation.
- Check each kind-scoped non-entailment countermodel under the complete pinned theory.
- Account for all declared ordered pairs and prove role-sensitive branches; one positive example per kind is insufficient.

Inherited pending IDs: 5; ordered endpoint branches: 1.

Policy decisions: D01/D04/D07 common catalog and provenance rules.
