Finite source-catalog consistency and guarded K02 payload review

This package completes the structural finite-catalog formalization component
prepared by F02. It keeps K02's accepted meaning and the five-field payload
projection unchanged. It prepares evidence inside N01; it does not accept N01,
discharge an inherited ID, freeze a public API or accept K03/global policies.

The missing case was a conflict across aliases. The previous token resolver
checks whether every value for one role/token agrees and is approved in that
role. Two different tokens can each have one approved value while their values
reuse the same owner/artifact/revision key with different digests. CatalogControls1
constructs exactly that case: both earlier token lookups succeed, but the global
invariant and guarded payload decoder refuse the capture. This is a checked
regression model, not merely a hypothetical failure description.

Artifact holds an exact revision reference, source kind, complete model body,
content bytes and owner-review reference. Its body type is generic so the invariant
applies to any full decoded artifact representation. The model does not itself
prove that a body is the complete raw JSON record or corresponds to those bytes.
The fixture bodies/bytes/reviews are explicitly synthetic; the payload values
come from the exact existing Intent Resolution source fixture.

Binding holds a reference role, opaque token and exact artifact revision. Approval
holds the role, full Artifact and capture Frame. Approval.frame is the frame in
which approval evidence was captured for verification; it is not the historical
time at which an owner originally approved an artifact. These roots are independent
verification-context inputs. A field or role label on a proposal supplies no root.
Their authentic acquisition remains a required premise to establish downstream.

The independent CaptureMeaning requires all five conditions:

- Across catalog records and every full artifact contained in approval roots,
  equal revision keys imply equal complete records. Body, bytes, digest, source
  kind and owner-review reference cannot differ for one key.
- Each reference-role/token key has one binding value. Identical repeated bindings
  are permitted in this provisional structural model; contradictory ones refuse.
- Every selectable catalog record has exact captured approval evidence.
- Every token binding is nonempty, points to an exact catalog record, and has
  approval evidence for its own reference role and complete capture frame.
- Every approval root has the complete capture frame, including profile, endpoint
  references, context, scope, snapshot, epoch and time domain.

The Bool capture checker is proved equivalent to this independent predicate.
Checking only selected fields would miss a conflicting alias elsewhere in the
capture. Checking only catalog rows would miss conflicting approval-root records.
A missing second test binding can leave the structural catalog consistent; the
payload decoder still refuses instead of omitting that required test.

The exact-record resolver fixes its lookup keys internally. Its theorem is:

    resolveRecord(capture, expectedFrame, role, token) = some artifact
        iff ResolvedMeaning(capture, expectedFrame, role, token, artifact).

ResolvedMeaning independently requires capture consistency, full expected-frame
agreement, the exact nonempty binding, catalog membership and matching role
approval. For successful aliases with one revision key, the whole returned
Artifact is equal. This is artifact-revision record equality; it grants no agent/
principal identity equivalence, ownership or authority.

GuardedIntentPayload extracts finite role/token values and approved references
from the capture, then applies the existing payload decoder only after checking
the entire capture and expected frame. The new theorem is:

    guardedDecode(capture, expectedFrame, raw) = some payload
        iff CaptureMeaning(capture)
          and capture.frame = expectedFrame
          and the independent five-field PayloadMeaning holds.

It also proves that context enrichment preserves exact bindings and decoded
payloads when old and new captures are both valid, have the same complete frame,
and retain all old records, bindings and approval roots. This structural law does
not authenticate an immutable catalog manifest or permit changing its bytes under
one catalog revision; capture/catalog identity and authenticated recapture must be
established by the later source-capture adapter. Frame changes require separate
capture evidence and are not silently treated as same-frame extensions.

Matching aliases remain valid and resolve to the same complete record. If two
selected tokens denote that same revision, the payload preserves the duplicate
references. K02's existing selectedSubjects.Nodup condition then refuses addressing.
Catalog consistency does not legitimize a duplicate selected-subject list.

CatalogFixtures holds the shared synthetic data. CatalogControls1 through
CatalogControls4 retain all 26 controls in dependent modules after the original
combined regression module exceeded the 240-second compiler timeout.

The 26 controls cover the original payload, complete record lookup, the earlier
conflicting-alias acceptance, global refusal, body/bytes/kind/review substitutions,
conflicting approval records, missing and wrong-role approvals, changed profile/
snapshot, stale capture epochs, missing tests, matching aliases, visible duplicate
selected values, legal extension, ambiguous/dangling/empty-token bindings and an
empty consistent capture that cannot seed the required payload references.

Validation uses the pinned Lean compiler, fresh compilation and a separate fresh
replay, per-theorem axiom inspection, and matching-phase import-resolution checks.
Only propext, Quot.sound and Classical.choice are allowed. Preparation failures
are retained separately; final verification.json is the proof evidence. Replay
with the same kernel is not the mandatory independent checker.

Remaining requirements:

- Authenticate and bind the finite capture/catalog identity, complete approved
  records, bytes and immutable owner/profile/source-snapshot provenance. Structural
  membership in supplied roots is not proof of an actual owner approval.
- Decode and interpret outer Intent Resolution identity, owner_ref, scope_ref,
  lifecycle, evidence and claim ceiling, including actual source-kind/role policy.
  An artifact's sourceKind string is compared for consistency here, not interpreted
  as authenticated artifact typing.
- Prove/account for JSON parsing, schema closure, body/byte correspondence, digest
  interpretation and complete metadata under the declared trust profile.
- Bind raw intent_resolution_ref/addressing_role and the owned Selection companion
  to exact resolution/subject/role/decision and the complete frame; then prove
  whole-source meaning equivalent to K02 Addresses over all six branches.
- Complete qualification/recording/storage integration, whole-rule preservation,
  all seven extension integration obligations, full-theory countermodels and
  mandatory independent checking under the unchanged full plan.
- Establish enforced resource bounds. This model uses finite pairwise checks and
  scans; no production performance/resource gate is satisfied by compiling fixtures.

Every inherited ID remains pending. The original 90 discharges and original
R06/G4 acceptance keep their original scope. K03's meaning has subsequently been accepted by the semantic owner. K04's
meaning and D01-D08's global shared-policy assessments remain separate and pending.

Current validation status: candidate component verified. Fresh pinned compilation
and a separate fresh replay both pass: 54 new declarations, 28 compiler
invocations and 276 axiom inspections including imports. All 28 matching-phase
import-resolution pairs pass. The previous timeout and partial records remain
in repair-attempts/06 as historical failed-run evidence. The successful final
verification.json and import-resolution-audit.json bind current source hashes.
This result establishes the finite-catalog/guarded-payload component only;
authenticated capture, complete source refinement, inherited discharge and
mandatory independent checking remain unproved.
