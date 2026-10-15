Shared qualified recording candidate review

This package prepares the common record effect required by all 41 relation kinds.
The coverage map binds each exact operational-effect ID and its immutable source
contract. The map does not discharge those IDs or freeze the successor API. K03's
actual meaning assessment remains pending, and globally shared policies still
need their own assessments.

QualifiedRecording.lean defines the store independently: every revision key
appears at most once. Its recursive Bool check is proved equivalent to that
invariant. A revision key is owner/artifact/revision; the opaque digest is not a
license to assign different content to the same revision key.

The proposal envelope has separate revision reference, complete typed payload
and content bytes. Submission first requires qualification, then a well-formed
store. A new key appends one envelope. An identical envelope retains the entire
state. Same key with a changed payload, digest or bytes refuses without changing
the state. A malformed store also refuses without repair. An existing record
cannot bypass new qualification when its evidence or context stops qualifying.

The central implication is:

    appended or retained ⇒ issued exact record ∧ independent kind meaning

For K02, that meaning includes the exact owned Intent Resolution selecting the
subject for its Intent in the matching role, without exclusion. For K03, it includes
the admissible observed-impact witness and its owned scope/evidence policy. Issuance
by itself cannot replace either meaning. Qualification failure preserves all state,
even if an identical record already exists. An identical retry is retained only
while its independently captured qualification context still passes.

General theorems prove protection of arbitrary protected state, preservation of
unique store keys, successful submission's qualification/independent meaning,
exact append and retention/refusal behavior, and immediate fresh-append retry
idempotence under the same qualification context. These are pure state laws,
not durability, concurrency or crash-recovery claims.

The generic theorem is parameterized by a checker and requires an actual
checker/meaning equivalence. The eventual public API must not let a caller choose
this checker or supply eligibility booleans. RecordingBindings.lean fixes the
already checked K02 and K03 checkers. It requires an independently issued relation revision in a separate
identity field bound to the exact kind, full frame, primary witness and content
bytes, together with the relation's independent meaning. A witness revision alone does not establish relation issuance. The two
identity fields are separate; inequality between their values is not required or
proved by this candidate. If the owner policy requires unequal values, that must
be an explicit additional constraint.

The issued catalog is independently captured input, not a caller-owned approval
flag. Its authenticity, non-equivocation, complete ownership policy and byte/body
source interpretation are explicit future refinements. Equality to expected bytes
is not a proof of serialization, hashing, signature authenticity or physical truth.
The pure recorder holds the verification context fixed for each call; the full
application must establish snapshot/epoch freshness and race-safe qualification.

RecordingExamples.lean checks append, duplicate retention, immediate retry,
conflicting payload/digest/bytes, a distinct next revision, unqualified submission,
non-seeding from an existing row, and malformed stores containing conflicting or
identical duplicate keys. These are synthetic primitive controls. Concrete raw
relation transactions still need their source-bound models and public tests.

BindingExamples.lean uses the resolved K02 and K03 witness models to check
qualified append and retry, wrong-kind issuance, an unissued witness substituted
for the relation reference, mismatched issued bytes, invalid addressing role,
predicted impact, and missing selection/provenance even when a row exists. The
identity-substitution control is about its exact fixture catalog; it is not a
universal proof that relation and witness references must be unequal.

Verification uses fresh pinned compilation and a separate fresh replay, with
per-theorem axiom inspection. Only propext, Quot.sound and Classical.choice are
allowed. Exact source/output hashes, declarations and compiler logs are in
verification.json. The current run passes 50 new candidate declarations, 26
compiler invocations and 366 axiom inspections including imported dependencies.
The separate import audit confirms exact fresh outputs for all 26 source/phase
pairs. This remains same-kernel replay, not independent checking.

Remaining work for the 41 exact effect obligations:

- Bind each complete relation record body and issued identity to its independently
  reviewed kind meaning; only resolved K02/K03 bindings are prepared here.
- Prove raw decoding/serialization, byte/body correspondence, digest/revision
  binding and authenticity/non-equivocation of the issued catalog.
- Decide and bind issuance/ownership policy and complete frame/provenance context;
  a trusted issued catalog is not proof of its capture or an authority grant.
- Implement one composed store for all kinds using a complete payload sum/profile;
  separate typed examples do not constitute the whole extension integration.
- Implement atomic public persistence, concurrent writers, crash recovery, stale
  qualification refusal and resource/status/diagnostic behavior under actual limits.
- Check whole-rule closure so later consumers cannot manufacture authority,
  ownership, identity or execution effects from a recorded row.
- Independently check every selected mandatory closure proof and complete all
  remaining successor plan gates. No original acceptance is widened here.

All inherited obligations remain pending. The full plan remains active.
