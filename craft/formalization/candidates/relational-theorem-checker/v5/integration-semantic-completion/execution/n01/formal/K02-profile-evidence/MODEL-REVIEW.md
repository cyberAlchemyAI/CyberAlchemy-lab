# What the authority evidence interpreter adds

The previous profile component could check declaration/selection bytes and their
recorded approval, revocation and expiry values. Its eight evidence requirements
were still open predicates. This interpreter gives those requirements concrete
source joins against one retained authority snapshot.

For every declaration and selection, it checks three things: issuance identifies
the same complete reference, kind, issuer, owner review and original bytes;
entitlement permits the exact issuer/action/scope; and the review identifies the
same complete source and owner-review references and the same decision,
revocation and expiry. The snapshot has the complete frame and exact ordered
source manifests. It also binds the independently requested trust root, authority
capture reference and bootstrap profile.

The main theorem states that successful `prepareProfileEvidence` is equivalent
to the independently defined `PreparedEvidenceMeaning`. This includes the full
preceding profile preparation, captured authority source meaning, global fact
coherence, exact manifests and every required evidence join. Source envelopes
are retained, and issuance matches complete original bytes rather than only a
hash or a revision label. Failure means no stage satisfies that data meaning.

## A restriction removed during review

A first draft would have rejected two reviewed sources sharing one owner-review
reference. The existing source contract does not require a review to concern only
one artifact. The implemented model permits a batch review: its full reference
must remain consistent, and decisions for the same review/source revision-key
pair must agree. It also permits one grant to contain both declaration and
selection actions. The captured positive fixture exercises both cases. Conflicting
unused issuance, grant, review-reference and review/source facts still refuse.

## What remains outside structural checking

The data checker does not establish that the snapshot is authentic or its claims
are admissible. A real owner-selected provider must establish
`RootPolicy.authoritativeSnapshot(root, frame, originalCapture)` for this exact
capture. That boundary covers authenticity, completeness and admissible bootstrap,
issuance, entitlement and review/lifecycle statements under the pinned policy.
There is no default True provider or caller approval Boolean.

The eight interpreted requirements each retain that boundary. A general theorem
constructs `OwnedSelectionMeaning` from prepared evidence **and an actual boundary
proof**. Another theorem shows that absent boundary evidence prevents owned profile
meaning even when the structural checks pass. The existing complete capture bridge
then composes conditionally with actual Schema and reviewed-entry requirements.
No real authoritative-snapshot provider, actual keys or deployment root is supplied.

This distinction matters for the examples: their roots, principals and review
references remain synthetic. A valid synthetic snapshot demonstrates the exact
join behavior; it does not grant ownership or admission to a real source.

## Verification and limits

The package contains 26 general declarations and 35 closed controls. One of the
36 declarations in the controls module is a general missing-root result. Typed
controls exercise every missing/wrong join, changed bytes, full-frame/root/ref
and bootstrap mismatches, manifest differences, duplicate retention, unused
equivocation and unsupported byte/action domains. Ten captured-source runtime
cases check the actual authority decoder and composed profile/evidence path.

The candidate snapshot schema and three-function local API describe the current
implementation. Nine decoded-value schema checks also show that missing review,
changed issued bytes and unused conflict may pass shape validation but fail the
semantic checker. Schema validation cannot enforce duplicate-key preservation or
exact rational-to-Nat evaluation from byte/epoch lexemes. Decimal and exponent
spellings with an exact natural value are supported. A floating-point JSON decoder
may round a non-integral token to an integer; the formal decoder refuses that token.
No schema/byte-interpreter equivalence is claimed. The numeric explanation in the
preceding profile packet is corrected by `NUMERIC-REPRESENTATION-CORRECTION.md`.

Fresh isolated compilation/replay and import resolution are recorded separately.
Same-kernel replay is not mandatory independent checking. The current limits bound
the authority capture separately and the declaration/selection catalog by the
preceding guards; a combined total/count guard and measured operational profile
remain pending. The Option API does not yet expose public refusal diagnostics.

All nineteen full K02 source policies, whole-theory countermodels, independent
checking and final use assessment retain their complete requirements. The 263
inherited IDs remain pending with zero new discharges; 90 original discharges keep
their scope. K04 and global D01-D08 remain pending. This is a verified interpreter
component, not N01/N02/N03 or full-plan completion.
