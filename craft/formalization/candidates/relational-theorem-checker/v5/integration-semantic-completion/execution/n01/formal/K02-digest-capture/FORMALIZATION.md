# Digest-checked original-byte capture and ordered catalog

This formalization precedes implementation. It composes registered independent
byte-record and digest meanings, without defining meaning as checker success.
The candidate profile remains SHA-256/FIPS1804-2015 with lowercase full hex.

For expected candidate profile P, byte budget B, complete Frame F and submitted
Envelope E, DigestPreparedMeaning(E,O) requires BOTH:

- PreparedBytesMeaning: E has the correct declared byte count, its original bytes
  denote the exact complete binding record, the record's full Frame equals F,
  and O retains E without replacement.
- VerifiedDigestMeaning: E's complete profile RevisionRef equals P.ref, P has
  the supported algorithm/encoding and nonempty reference components, E's byte
  length is in the algorithm domain and within B, and the independent digest
  computation meaning derives E's submitted digest from E's exact original bytes.

The implementation must refuse the submitted envelope rather than repair it.
Its diagnostic priority is envelope/count, then digest profile/domain/budget/format/
mismatch, then raw JSON/scalar/record/frame interpretation. A valid digest can
describe malformed JSON: integrity and source interpretation remain distinct checks.
A malformed envelope must not be accepted because its content hash matches.

The capture policy adapter realizes the existing parses predicate with the
independent scalar-byte document meaning and the digest predicate with exact
candidate profile correspondence AND independent digest meaning. Resource budget
is a separate operational guard. ownedDigestProfile, schema and reviewed remain
exactly the caller's obligations. No default True predicate, owner fixture,
signature label or manufactured evidence supplies those obligations.

An ordered all-input list derivation relates EACH submitted envelope to one
prepared output at the same position. It cannot discard refused records or roots,
normalize or replace content, or skip any input because its reference is unused.
The catalog meaning additionally requires the full Frame and expected profile,
the existing structural/non-equivocation/root catalog meaning, and independently
specified limits for input count and aggregate original byte count. Per-capture
byte limits apply to every record and root. All limits are explicit caller inputs;
this proves resource-guard interpretation, not a measured operational envelope.

Theorem targets: capture success iff DigestPreparedMeaning; exact refusal meanings;
full retained-envelope and checked-entry digest/profile correspondence; unchanged
remaining policy obligations; conditional complete CaptureMeaning construction;
ordered all-input and catalog success iff their independent meanings; list/count/
byte provenance and total configured guard correspondence.

Positive controls must use computed digests of the original fixture bytes, with
profile/review reference roots clearly synthetic. Negative controls retain the
submitted digest while changing bytes (including same-count replacement), count,
profile, record interpretation or Frame. Matching repaired digest can satisfy
integrity while failing interpretation or authentication. It does not establish
the original content's issuer, ownership, review, lifecycle or relation validity.

Capture/catalog integrity composition does not prove collision freedom, authentic
profile selection, Schema interpretation, actual issuer/review, full nineteen-source
policy realization, complete relation/qualifier/theory closure, independent proof
checking, standard translation or operational qualification. All 263 inherited IDs,
all seven extensions and all 41 relations retain the existing full-plan completion
requirements. K04 and D01-D08 remain pending; original 90 discharges retain scope.
