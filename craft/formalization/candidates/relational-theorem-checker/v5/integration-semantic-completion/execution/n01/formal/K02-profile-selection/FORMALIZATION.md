# Expected-profile source interpretation, before implementation

This is a candidate source/selection interpretation for N01, not an actual owner
selection or approval of global D01-D08. The previous profile argument was supplied
by the caller. The new preparation must derive it from captured declaration and
selection records, with an explicit remaining evidence contract.

A declaration record retains its complete binding revision key, full Frame,
owner-review reference, original envelope and bytes. Its payload gives algorithm,
encoding, issuing principal reference, recorded review posture, recorded revocation
posture and an exclusive expiry epoch. A selection record retains the same header
and source information, and names the COMPLETE selected declaration RevisionRef,
issuing principal, recorded review/revocation postures and exclusive expiry epoch.
Both source types use separately versioned closed candidate binding records.
Recorded accepted/clear postures are claims in captured source, not authenticity.

The declaration's full profile reference is derived from its binding revision key
and verified original-byte digest. It is not asserted as its own content digest
inside the hashed payload. This avoids requiring a JSON document to contain its
own hash. The selection can name that already-computed full reference.

Capture preparation uses an explicit bootstrap digest profile and existing exact
digest/byte-record preparation. Authentic ownership of that bootstrap profile is
an additional remaining evidence obligation: selection must not bootstrap trust
from its own submitted label.

Independent selected-data meaning requires:

1. Every declaration and selection input has a digest-checked exact source meaning
   under the bootstrap profile and configured limits; every full Frame equals the
   requested Frame, preserving context, scope, snapshot, epoch and time domain.
   No source is silently skipped or normalized.
2. All captured declarations are non-equivocating by binding revision key, including
   unused declarations. Distinct content at one key is refused. Identical duplicates
   may be retained. All selection records for the exact Frame agree as full retained
   records; conflicting selections are refused regardless of list order or posture.
3. A selection record exists. Its recorded review is accepted, revocation is known
   clear, epoch is strictly before its expiry, and its exact selection token matches.
4. Its complete selected declaration reference resolves to a captured declaration.
   The declaration has the exact declaration token and the same eligible recorded
   review/revocation/expiry conditions. No fallback to a latest revision or alias is
   performed when an exact reference is missing.
5. The resulting Profile is derived from that declaration's checked entry reference
   and payload algorithm/encoding, and has the supported independent ProfileMeaning.

The source expiry is an as-of guard in one exact full Frame. It does not implement
the global D02 period/session policy or establish later live currentness.
Source shape, exact joins and recorded postures alone establish SelectedDataMeaning.
They do not establish ownedDigestProfile.

Complete OwnedSelectionMeaning additionally requires independently specified
authentic snapshot completeness, authentic bootstrap profile selection, actual
declaration and selection issuer evidence, entitlement of their exact principals
for this Frame/scope, and faithful admissible owner-review/revocation/expiry evidence
bound to the full records and original bytes. None receives a default True predicate
or a caller approval boolean. A conditional policy adapter may expose this complete
meaning; it must not reinterpret shadow preparation success as authentic ownership.

Tests must cover positive captured sources, missing/exact-stale declaration refs,
conflicting selections in both orders, unused declaration conflict, absent/rejected
recorded review, revoked/unknown revocation, expiry boundary, wrong full Frame,
invalid source bytes or digest, unsupported algorithm/encoding and configured limits.
Fixture principals, bootstrap/profile references and owner reviews remain synthetic.

This component is not the complete nineteen-policy K02 source realization, Schema
interpretation, cryptographic issuer/review verification, independent checking,
operational qualification or inherited semantic discharge. All 263 obligations,
90 retained original discharges, seven extensions and 41 relation reviews keep
their full requirements. K04 remains pending; no admission or promotion is inferred.
