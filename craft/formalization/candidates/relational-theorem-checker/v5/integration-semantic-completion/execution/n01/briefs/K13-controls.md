K13 — relation.controls

Status: candidate meaning; actual owner assessment pending.

Source question: Which Failure Mode is this Failure Control Binding intended to control?

Source effect: Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.

Proposed claim tier: recorded intended control.

Independent witness type: `ControlBinding`.

The exact source declaration and its ordered pairs are bound by [the definition contract](/home/vlad_/projects/CyberAlchemy-lab/craft/formalization/candidates/relational-theorem-checker/v5/integration-semantic-completion/definitions/K13-controls.json).

**Independent meaning constraints**

- Exact kind/source definition and approved meaning revision.
- Exact source/target node kinds and revisions match one declared ordered pair.
- Every required qualifier has its independently defined typed interpretation; closed qualifier object has no extra field.
- Primary witness, subject, target, context, scope, source snapshot, epoch and time domain agree with the complete frame.
- The selected evidence and provenance policy establishes the claimed recorded/as-of/executed/observed posture; missing authenticity is not manufactured.
- binding = s; binding.failureMode = t.
- control_version_ref resolves binding.controlSubject, not the failure-mode endpoint.
- control_role agrees with the binding's one primary role: prevent, detect, contain, recover or compensate.
- installation_posture records the exact binding posture; intended control is independent of installation, execution and effectiveness.

**Qualifiers**

| Field | Proposed type | Exact role |
|---|---|---|
| control_role | OwnedRoleCode | record.control_role: exact relation-specific owned role/posture/purpose code, interpreted for this ordered endpoint pair |
| control_version_ref | ExactRevisionRef | record.controlSubject: exact control attached to source Failure Control Binding; not target Failure Mode |
| installation_posture | OwnedPostureCode | record.installation_posture: exact relation-specific owned role/posture/purpose code, interpreted for this ordered endpoint pair |

**Effect**

Record intended control of this mode by the exact bound control; preserve installation/execution/effectiveness facts.

Append one exact immutable witnessed relation record, or idempotently retain an identical existing revision; same revision with different content is refused.

A record append does not implement its source witness's execution. Materialization requires evidence of a completed authorized atomic application; no standalone relation row proves it.

**Worked positive model**

Binding B names Control C as detect for Mode M; C is still a candidate and is not installed.

This is a candidate model blueprint. No actual approval or execution is established by the example.

**Worked refusal**

Using Mode M's revision as control_version_ref fails the bound-control role.

**Exact excluded conclusions**

- `relation.controls:forbidden:0` — **installation**: An authenticated installation receipt establishes that the control is present and configured in this environment. Participants: the controlSubject revision inside source Failure Control Binding, exact target Failure Mode and bound execution environment.
- `relation.controls:forbidden:1` — **execution**: A verified execution trace shows that the exact control ran in the relevant envelope. Participants: the controlSubject revision inside source Failure Control Binding, exact target Failure Mode and bound execution environment.
- `relation.controls:forbidden:2` — **effectiveness**: An admissible outcome assessment establishes the owned effectiveness test. Participants: the controlSubject revision inside source Failure Control Binding, exact target Failure Mode and bound execution environment.
- `relation.controls:forbidden:3` — **authority**: An authenticated authority root or valid bounded delegation chain permits this holder/action/scope at the frame epoch. Participants: the explicitly joined accountable holder/source participant and this frame's exact scope; additional operation/boundary/grant witnesses range over the owner-resolved catalog.

Each exclusion needs a checked valid countermodel. The excluded property can still hold through independent evidence; the local relation does not decide its universal falsity.

Required source refinement: Under exact owned catalog/frame well-formedness, decoding and resolution of raw source fields yields a iff the independently specified source constraints denote Meaning_K13(W,a). The decoder/checker must not define that source predicate.

Required proofs:

- Prove the independent meaning has a valid positive model.
- Prove each exact qualifier mapping and checker/meaning equivalence.
- Prove declared record effect and any required execution/closure preservation.
- Check each kind-scoped non-entailment countermodel under the complete pinned theory.
- Account for all declared ordered pairs and prove role-sensitive branches; one positive example per kind is insufficient.

Inherited pending IDs: 8; ordered endpoint branches: 1.

Policy decisions: D04.
