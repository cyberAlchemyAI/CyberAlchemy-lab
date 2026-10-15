# Digest-checked byte captures: what changed and what remains

The earlier byte adapter could interpret the original content and preserve its
submitted digest label, while the separate digest evaluator could check content
integrity. This package connects them: an accepted prepared capture now has both
an exact record interpretation and a verified digest of those same original bytes.
It never repairs a submitted digest, substitutes an AST or replaces an envelope.

The independent DigestPreparedMeaning is the conjunction of the existing independent
PreparedBytesMeaning and VerifiedDigestMeaning. The primary theorem is:

    prepareDigestBytes P B version kind decoder Frame Envelope = some Prepared
      iff DigestPreparedMeaning P B version kind decoder Frame Envelope Prepared.

All values of the generic input types are covered, rather than a selected list of
fixtures. Full count, retained bytes, complete Frame, binding record, complete profile
RevisionRef and computed digest remain connected. Fixed resolution/role entrypoints
reuse their pinned versions, kinds and target interpreters.

Diagnostics check envelope/count first, digest profile/domain/budget/format/mismatch
second, and raw JSON/scalar/record/frame interpretation third. General exactness
results specify each refusal under that priority. An unsupported profile blocks
interpretation. A correct digest of empty bytes or malformed JSON proceeds to
interpretation and fails there. Digest equality establishes neither meaningful JSON
nor a valid binding. No result calls either refusal a successful capture.

The installed policy adapter supplies two existing requirements: independent byte
parsing and independent exact-profile digest semantics. Profile ownership, schema
and reviewed-entry predicates are unchanged. A complete CaptureMeaning can be
constructed only with those actual separate premises. The reverse bridge also
requires the configured byte budget. Missing profile ownership, schema or review
prevents complete CaptureMeaning even when preparation succeeds.

The catalog builder checks every submitted record AND root, including unused roots.
An inductive all-input relation preserves list position and full envelopes. It enforces
per-capture bytes, aggregate original bytes and total record-plus-root count, then the
existing structural/non-equivocation/root catalog meaning. A separate initial profile
check prevents vacuous acceptance of an unsupported descriptor for an empty catalog.
The accepted stage projects to the prior byte-catalog meaning, so composition retains
its structural obligations rather than bypassing them. An invalid digest at any input
cannot be skipped to produce a successful catalog.

Verification adds 49 general declarations and 12 closed kernel controls. The fresh
report records both complete compilation/replay phases and exact import resolutions.
There are 34 executable integration cases per phase. Both original resolution/role
fixture files get actually computed SHA-256 digests; runtime preparation and catalog
construction succeed, retaining their full envelopes. Same-count byte changes,
truncation and appending retain the original submitted digest and fail. Other cases
cover count/profile/old uncomputed labels, stale frames, budgets, malformed UTF-8,
unpaired JSON escapes, JSON null and an unused bad root.

The positive original fixture hash computations are runtime checks backed by the
general algorithm and composition proofs. They are not presented as separately
kernel-reduced ground hash theorems for those large files. The closed kernel controls
cover explicit refusal guards and correctly hashed empty bytes failing record syntax.
Profile and review roots in every worked fixture remain synthetic. Their labels do
not become an actual owner assignment or authenticated review by passing these tests.

Remaining work begins with formalizing the authentic expected-profile, Schema, issuer
and reviewed-entry interpretations for the exact frame and snapshots, then implementing
their providers. All nineteen complete K02 source-policy predicates and source/world,
Selection, payload and qualifier joins remain open. Digest/parse component realization
does not discharge full provenance or source policies. External-standard translation,
measured resource qualification, complete relation theory/closure and mandatory
independent proof checking are also unfinished. Resource-limit interpretation is
proved; the supplied limit values are not thereby operationally qualified.

All 263 inherited obligations remain pending. The 90 original discharges and original
R06/G4 assessment scopes are preserved. K04 is still the pending one-by-one meaning
review; D01-D08 global assessments remain pending. N01 remains in progress; N02/N03
admission and all 20 tasks retain their full completion criteria. This is candidate
preparation, not an authenticated catalog, publication or full-plan completion.
