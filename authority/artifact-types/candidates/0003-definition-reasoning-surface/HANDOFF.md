# Definition reasoning-surface handoff

Status: candidate-unadmitted. Authority effect: none.

## Why this belongs in Lab review

The RPOS consumer applied one repeatable question set to every definition:

- What is the subject?
- What goal does the concept serve?
- How is it used operationally?
- Which concrete use cases justify it?
- What must not be inferred from it?

Definition/v1 can preserve those answers only by placing labeled strings in
the untyped domain-context `examples` array. The result validates, but Lab
cannot require, index, compare, or query the reasoning concerns separately.
That is a reusable artifact-contract gap rather than an RPOS domain gap.

The same consumer exposed two adjacent gaps. Definition/v1 permits
`formal_expression: null` but does not record whether that means intentionally
structured invariants, an unresolved formal model, or an accidental omission.
It also has no portable selected-foundation export that carries exact
definitions, contract files, admission decisions, versions, and digests for a
consumer that must validate without a live Lab checkout.

## Recommended next decision

Prototype a separate domain-neutral Definition Reasoning Profile referenced by
Definition records. Require `subject`, `goal`, `operational_interpretation`,
`use_cases`, `boundary`, `formalization_posture`, and semantic tests. A formal
posture must distinguish `formal-expression`, `structured-invariants`, and
`open`; only the first requires notation. Test it with at least two unrelated domains. Only
then decide whether those fields belong directly in a versioned Definition/v2.

Evaluate a separate Semantic Foundation Snapshot artifact type. It should carry
only a selected transitive closure of definition bytes, required contract
files, admission evidence, versions, digests, source revision, rights posture,
and a successor-only refresh rule. Snapshotting must not re-admit or transfer
ownership of any Definition.

This avoids mutating Definition/v1 or interpreting one consumer's successful
profile as universal proof.

## Separate currentness work

Do not bundle contract evolution with validator maintenance. Definition/v1 has
one stale selected-source currentness check, while Bounded Context/v2 and
Context Map/v2 each retain a stale expected Definition-registry digest. Repair
those through successor receipts and preserve existing receipt history.

## Acceptance boundary

The chosen successor must remain domain-neutral, preserve the three-voice
normative boundary, reject missing and additional fields through hostile
fixtures, expose reasoning in deterministic projections, and leave v1 bytes
and historical receipts untouched. A snapshot successor must also validate
without the source repository present and fail on any copied-byte or manifest
digest drift.

Open questions and the three decision options are recorded in `candidate.json`.
