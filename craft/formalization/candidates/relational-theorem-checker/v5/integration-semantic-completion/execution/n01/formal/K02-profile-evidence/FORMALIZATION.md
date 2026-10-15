# Profile authority evidence interpretation, before implementation

The preceding profile preparation interprets source data but leaves eight open
evidence requirements. Implement a concrete interpretation of those requirements
using one separately captured, versioned authority snapshot. A supplied label,
hash or list member must not become authentic authority by itself.

The snapshot is a closed binding record with the complete existing Frame. Its
payload retains: an independently selected trust-root reference; bootstrap
profile reference/algorithm/encoding; complete ordered declaration and selection
reference manifests; source issuance facts; principal entitlement facts; and
review/lifecycle facts. It has a computed reference of its own, separately from
Frame.snapshot, which identifies the underlying source snapshot. The payload
does not contain its own content hash.

Issuance facts retain source reference, source kind, issuer principal, owner-review
reference and the complete original source bytes. Entitlements retain an exact
grant reference, principal, permitted actions (declare and/or select) and scope. Review facts
retain exact review and reviewed-source references, recorded decision/revocation
postures and exclusive expiry epoch. All facts are scoped to the full snapshot
Frame, including context, underlying source snapshot, epoch and time domain.

Independent data meaning requires all of the following:

1. Authority capture has an exact byte/digest/closed-record meaning under the
   explicit bootstrap profile and configured capture limit. Its computed complete
   reference matches the independently requested authority reference, and its
   payload trust root matches the independently requested trust-root reference.
   The exact frame and authority token must match. Its bootstrap data equals the
   supplied bootstrap profile; self-selection is not authentic bootstrap trust.
2. Issuance facts are globally non-equivocating by source revision key. Grants
   are non-equivocating by grant revision key. Review revision keys resolve to one
   complete reference; assertions for the same review/source revision-key pair
   are non-equivocating. One review may cover multiple sources, and one grant may
   permit both actions. Identical duplicates are permitted. Conflicts among unused
   facts also refuse. Do not impose a one-subject review restriction absent from
   the existing source contract.
3. Both ordered reference manifests exactly equal the prepared source lists.
   No unused source is filtered and no reference alias/latest fallback is used.
4. Every declaration and selection row has exact issuance evidence, an entitlement
   for its issuer/action/scope, and review/lifecycle evidence matching its complete
   source and owner-review references and recorded posture/expiry fields. Exact
   issuance retains the original bytes as well as the reference. Snapshot-scoped
   facts cannot be transplanted into a different complete Frame.
5. The prepared profile stage satisfies the preceding SelectedDataMeaning with
   every original envelope retained. The authority evidence checker cannot turn
   a malformed or ineligible source into an admissible profile.

Data interpretation is executable and must be proved equivalent to this independent
meaning. It produces preparation evidence, not a proof of authentic authority.

The remaining external boundary is `AuthoritativeSnapshot(trustRoot, frame,
authorityCapture)`: a real owner-selected provider must establish that this exact
captured snapshot is authentic, complete and admissible for issuance, entitlement,
review/lifecycle and bootstrap statements under the pinned trust policy. This is
not an approval Boolean or a default True predicate. Cryptographic authenticity,
owner/admission evidence, or a trusted store may supply it only when their actual
contract is implemented and checked. No such real provider is invented here.

Instantiate the eight previous requirements with this boundary plus the concrete
exact source predicates. Prove that prepared evidence and an actual boundary proof
construct OwnedSelectionMeaning, preserve the other capture policies, and compose
with the existing complete-capture bridge. Prove explicitly that absence of the
boundary blocks ownership even if every structural evidence check passes.

Controls must cover positive declaration/selection evidence, each missing fact,
wrong complete authority/root/subject/principal/review/scope reference, changed
same-count source bytes, review/revocation/expiry mismatch, wrong full Frame,
bootstrap mismatch, reordered/omitted manifests and unused equivocation. Captured
snapshot source decoding must be exercised, not only constructed typed rows.

This is one exact evidence interpreter within full K02 source completion. It does
not complete all nineteen source policies, Schema semantics, relation-theory
countermodels, independent checking or any inherited discharge. The complete
41-kind/550-pair/263-obligation/seven-extension/twenty-task scope remains intact.
K04 and globally shared D01-D08 remain pending. All examples remain synthetic.
